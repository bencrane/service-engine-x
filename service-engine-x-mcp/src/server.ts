import express, { type Request, type Response } from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { env } from "./env.js";
import type { SerxToolError } from "./errors.js";
import { compoundToolDescriptions, compoundToolSchemas } from "./compound-tools.js";
import {
  ToolOutputSchema,
  annotationFromKind,
  coreToolDefinitions,
  executeCoreTool,
  getToolInputSchema,
} from "./tool-catalog.js";
import { buildToolDriftReport } from "./tool-spec.overrides.js";

type CoreResult = Awaited<ReturnType<typeof executeCoreTool>>;

class WorkflowStepFailed extends Error {
  constructor(
    public readonly stepName: string,
    public readonly result: CoreResult,
  ) {
    super(`Workflow step '${stepName}' failed.`);
  }
}

function toStructuredContent(value: unknown): Record<string, unknown> {
  if (value && typeof value === "object") {
    return value as Record<string, unknown>;
  }
  return { value };
}

function toMcpResponse(result: CoreResult) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
    structuredContent: toStructuredContent(result),
  };
}

function buildWorkflowFailureResponse(
  workflow: string,
  steps: Record<string, unknown>,
  failedStep: string,
  result: CoreResult,
) {
  const category = result.error?.category ?? "upstream_error";
  const message =
    result.error?.message ??
    `Workflow ${workflow} failed at step ${failedStep}. Inspect prior step output and retry with corrected inputs.`;

  const failure: CoreResult = {
    ok: false,
    status: result.status,
    data: {
      workflow,
      failed_step: failedStep,
      steps,
    },
    error: {
      category,
      message,
      retryable: result.error?.retryable,
      suggestedTools: result.error?.suggestedTools,
      status: result.status,
    },
  };

  return toMcpResponse(failure);
}

function assertStepOk(stepName: string, result: CoreResult, steps: Record<string, unknown>) {
  steps[stepName] = result;
  if (!result.ok) {
    throw new WorkflowStepFailed(stepName, result);
  }
}

function extractBearerToken(headerValue: string | undefined): string | null {
  if (!headerValue) return null;
  if (!headerValue.startsWith("Bearer ")) return null;
  return headerValue.slice(7);
}

function ensureIngressAuth(req: Request, res: Response): boolean {
  const token = extractBearerToken(req.header("authorization") ?? undefined);
  if (token === env.SERX_MCP_SHARED_SECRET) {
    return true;
  }

  res.status(401).json({
    error: "Unauthorized MCP request. Configure Managed Agent connector header Authorization: Bearer <vault secret>.",
  });
  return false;
}

function buildServer(): McpServer {
  const server = new McpServer({
    name: "service-engine-x-mcp-server",
    version: "1.0.0",
  });

  for (const def of coreToolDefinitions) {
    const inputSchema = getToolInputSchema(def);

    server.registerTool(
      def.name,
      {
        title: def.name,
        description: def.description,
        inputSchema: inputSchema.shape,
        outputSchema: ToolOutputSchema,
        annotations: annotationFromKind(def.kind),
      },
      async (input) => {
        const result = await executeCoreTool(def, input as Record<string, unknown>);
        return toMcpResponse(result);
      },
    );
  }

  registerCompoundTools(server);

  if (env.enableResources) {
    server.registerResource(
      "serx_deal_context_resource",
      "serx://org/{org_id}/deal/{deal_id}/context",
      {
        title: "Deal Context Snapshot",
        description: "Forward-compatible placeholder resource for deal context snapshots.",
      },
      async () => ({
        contents: [
          {
            uri: "serx://resource-disabled",
            text: "Resource placeholders enabled. Implement resolver wiring when connector resource support is available.",
          },
        ],
      }),
    );
  }

  if (env.enablePrompts) {
    server.registerPrompt(
      "serx_prompt_sales_briefing_from_deal_context",
      {
        title: "Sales Briefing From Deal Context",
        description: "Forward-compatible prompt placeholder for summarized deal briefing.",
        argsSchema: {
          deal_id: z.string().min(1),
          org_id: z.string().min(1),
        },
      },
      async (args) => ({
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Generate a sales briefing for org ${args.org_id ?? "<org_id>"} and deal ${args.deal_id ?? "<deal_id>"}.`,
            },
          },
        ],
      }),
    );
  }

  return server;
}

function registerCompoundTools(server: McpServer) {
  server.registerTool(
    "serx_process_new_booking",
    {
      title: "serx_process_new_booking",
      description: compoundToolDescriptions.serx_process_new_booking,
      inputSchema: compoundToolSchemas.serx_process_new_booking.shape,
      outputSchema: ToolOutputSchema,
      annotations: annotationFromKind("MUT"),
    },
    async (input) => {
      const steps: Record<string, unknown> = {};
      try {
        const parsed = compoundToolSchemas.serx_process_new_booking.parse(input);

        const resolvedOrg = await executeNamed("serx_resolve_org_from_event_type", {
          event_type_id: parsed.event_type_id,
          query: { event_type_id: parsed.event_type_id },
        });
        assertStepOk("resolve_org", resolvedOrg, steps);
        const orgId = pickOrgId(resolvedOrg);

        const createdRaw = await executeNamed("serx_create_cal_raw_event", {
          body: {
            ...parsed.raw_event,
            org_id: parsed.raw_event.org_id ?? orgId,
          },
        });
        assertStepOk("create_raw", createdRaw, steps);
        const rawEventId = pickId(createdRaw);

        assertStepOk(
          "create_booking_event",
          await executeNamed("serx_create_booking_event", {
            body: {
              ...parsed.booking_event,
              raw_event_id: rawEventId,
              org_id: orgId,
            },
          }),
          steps,
        );

        assertStepOk(
          "bulk_upsert_attendees",
          await executeNamed("serx_bulk_upsert_booking_attendees", {
            body: parsed.attendees
              ? {
                  attendees: parsed.attendees,
                  org_id: orgId,
                }
              : {
                  raw_payload: parsed.raw_event.payload,
                  org_id: orgId,
                },
          }),
          steps,
        );

        const createdMeeting = await executeNamed("serx_create_meeting_from_cal_event", {
          org_id: orgId,
          body: parsed.meeting,
        });
        assertStepOk("create_meeting", createdMeeting, steps);

        if (parsed.create_deal) {
          const meetingId = pickMeetingId(createdMeeting);
          assertStepOk(
            "create_deal",
            await executeNamed("serx_create_deal_from_meeting", {
              org_id: orgId,
              body: {
                ...parsed.deal,
                meeting_id: meetingId,
              },
            }),
            steps,
          );
        }

        if (rawEventId) {
          assertStepOk(
            "mark_processed",
            await executeNamed("serx_mark_cal_raw_event_processed", {
              event_id: rawEventId,
              body: {},
            }),
            steps,
          );
        }

        return toMcpResponse({ ok: true, status: 200, data: { workflow: "serx_process_new_booking", steps } });
      } catch (error) {
        if (error instanceof WorkflowStepFailed) {
          return buildWorkflowFailureResponse("serx_process_new_booking", steps, error.stepName, error.result);
        }
        throw error;
      }
    },
  );

  server.registerTool(
    "serx_process_booking_reschedule",
    {
      title: "serx_process_booking_reschedule",
      description: compoundToolDescriptions.serx_process_booking_reschedule,
      inputSchema: compoundToolSchemas.serx_process_booking_reschedule.shape,
      outputSchema: ToolOutputSchema,
      annotations: annotationFromKind("MUT"),
    },
    async (input) => {
      const steps: Record<string, unknown> = {};
      try {
        const parsed = compoundToolSchemas.serx_process_booking_reschedule.parse(input);
        const resolvedOrg = await executeNamed("serx_resolve_org_from_event_type", {
          event_type_id: parsed.event_type_id,
          query: { event_type_id: parsed.event_type_id },
        });
        assertStepOk("resolve_org", resolvedOrg, steps);
        const orgId = pickOrgId(resolvedOrg);

        const createdRaw = await executeNamed("serx_create_cal_raw_event", {
          body: {
            ...parsed.raw_event,
            org_id: parsed.raw_event.org_id ?? orgId,
          },
        });
        assertStepOk("create_raw", createdRaw, steps);
        const rawEventId = pickId(createdRaw);

        assertStepOk(
          "create_booking_event",
          await executeNamed("serx_create_booking_event", {
            body: {
              ...parsed.booking_event,
              raw_event_id: rawEventId,
              org_id: orgId,
            },
          }),
          steps,
        );

        assertStepOk(
          "bulk_upsert_attendees",
          await executeNamed("serx_bulk_upsert_booking_attendees", {
            body: parsed.attendees
              ? { attendees: parsed.attendees, org_id: orgId }
              : { raw_payload: parsed.raw_event.payload, org_id: orgId },
          }),
          steps,
        );

        assertStepOk(
          "create_meeting",
          await executeNamed("serx_create_meeting_from_cal_event", {
            org_id: orgId,
            body: parsed.meeting,
          }),
          steps,
        );

        if (rawEventId) {
          assertStepOk(
            "mark_processed",
            await executeNamed("serx_mark_cal_raw_event_processed", {
              event_id: rawEventId,
              body: {},
            }),
            steps,
          );
        }

        return toMcpResponse({ ok: true, status: 200, data: { workflow: "serx_process_booking_reschedule", steps } });
      } catch (error) {
        if (error instanceof WorkflowStepFailed) {
          return buildWorkflowFailureResponse("serx_process_booking_reschedule", steps, error.stepName, error.result);
        }
        throw error;
      }
    },
  );

  server.registerTool(
    "serx_process_booking_cancelled",
    {
      title: "serx_process_booking_cancelled",
      description: compoundToolDescriptions.serx_process_booking_cancelled,
      inputSchema: compoundToolSchemas.serx_process_booking_cancelled.shape,
      outputSchema: ToolOutputSchema,
      annotations: annotationFromKind("MUT"),
    },
    async (input) => {
      const steps: Record<string, unknown> = {};
      try {
        const parsed = compoundToolSchemas.serx_process_booking_cancelled.parse(input);
        const resolvedOrg = await executeNamed("serx_resolve_org_from_event_type", {
          event_type_id: parsed.event_type_id,
          query: { event_type_id: parsed.event_type_id },
        });
        assertStepOk("resolve_org", resolvedOrg, steps);
        const orgId = pickOrgId(resolvedOrg);

        const createdRaw = await executeNamed("serx_create_cal_raw_event", {
          body: {
            ...parsed.raw_event,
            org_id: parsed.raw_event.org_id ?? orgId,
          },
        });
        assertStepOk("create_raw", createdRaw, steps);
        const rawEventId = pickId(createdRaw);

        assertStepOk(
          "create_booking_event",
          await executeNamed("serx_create_booking_event", {
            body: {
              ...parsed.booking_event,
              raw_event_id: rawEventId,
              org_id: orgId,
            },
          }),
          steps,
        );

        const bookingUid = extractBookingUid(parsed.raw_event.payload);
        const meetingLookup = await executeNamed("serx_get_meeting_by_cal_uid", {
          org_id: orgId,
          cal_event_uid: bookingUid,
        });
        assertStepOk("get_meeting", meetingLookup, steps);
        const meetingId = pickMeetingId(meetingLookup);

        if (meetingId) {
          assertStepOk(
            "cancel_meeting",
            await executeNamed("serx_update_meeting", {
              org_id: orgId,
              meeting_id: meetingId,
              body: { status: "cancelled" },
            }),
            steps,
          );
        }

        if (parsed.update_deal_to_lost) {
          const dealId = pickDealId(meetingLookup);
          if (dealId) {
            assertStepOk(
              "update_deal",
              await executeNamed("serx_update_deal", {
                org_id: orgId,
                deal_id: dealId,
                body: { status: "lost", lost_reason: parsed.lost_reason ?? "booking_cancelled" },
              }),
              steps,
            );
          }
        }

        if (rawEventId) {
          assertStepOk(
            "mark_processed",
            await executeNamed("serx_mark_cal_raw_event_processed", {
              event_id: rawEventId,
              body: {},
            }),
            steps,
          );
        }

        return toMcpResponse({ ok: true, status: 200, data: { workflow: "serx_process_booking_cancelled", steps } });
      } catch (error) {
        if (error instanceof WorkflowStepFailed) {
          return buildWorkflowFailureResponse("serx_process_booking_cancelled", steps, error.stepName, error.result);
        }
        throw error;
      }
    },
  );

  server.registerTool(
    "serx_process_meeting_ended",
    {
      title: "serx_process_meeting_ended",
      description: compoundToolDescriptions.serx_process_meeting_ended,
      inputSchema: compoundToolSchemas.serx_process_meeting_ended.shape,
      outputSchema: ToolOutputSchema,
      annotations: annotationFromKind("MUT"),
    },
    async (input) => {
      const steps: Record<string, unknown> = {};
      try {
        const parsed = compoundToolSchemas.serx_process_meeting_ended.parse(input);
        const resolvedOrg = await executeNamed("serx_resolve_org_from_event_type", {
          event_type_id: parsed.event_type_id,
          query: { event_type_id: parsed.event_type_id },
        });
        assertStepOk("resolve_org", resolvedOrg, steps);
        const orgId = pickOrgId(resolvedOrg);

        const createdRaw = await executeNamed("serx_create_cal_raw_event", {
          body: {
            ...parsed.raw_event,
            org_id: parsed.raw_event.org_id ?? orgId,
          },
        });
        assertStepOk("create_raw", createdRaw, steps);
        const rawEventId = pickId(createdRaw);

        assertStepOk(
          "create_booking_event",
          await executeNamed("serx_create_booking_event", {
            body: {
              ...parsed.booking_event,
              raw_event_id: rawEventId,
              org_id: orgId,
            },
          }),
          steps,
        );

        const bookingUid = extractBookingUid(parsed.raw_event.payload);
        const meetingLookup = await executeNamed("serx_get_meeting_by_cal_uid", {
          org_id: orgId,
          cal_event_uid: bookingUid,
        });
        assertStepOk("get_meeting", meetingLookup, steps);

        const meetingId = pickMeetingId(meetingLookup);
        if (meetingId) {
          assertStepOk(
            "update_meeting",
            await executeNamed("serx_update_meeting", {
              org_id: orgId,
              meeting_id: meetingId,
              body: parsed.meeting_update,
            }),
            steps,
          );
        }

        if (parsed.deal_update) {
          const dealId = pickDealId(meetingLookup);
          if (dealId) {
            assertStepOk(
              "update_deal",
              await executeNamed("serx_update_deal", {
                org_id: orgId,
                deal_id: dealId,
                body: parsed.deal_update,
              }),
              steps,
            );
          }
        }

        if (rawEventId) {
          assertStepOk(
            "mark_processed",
            await executeNamed("serx_mark_cal_raw_event_processed", {
              event_id: rawEventId,
              body: {},
            }),
            steps,
          );
        }

        return toMcpResponse({ ok: true, status: 200, data: { workflow: "serx_process_meeting_ended", steps } });
      } catch (error) {
        if (error instanceof WorkflowStepFailed) {
          return buildWorkflowFailureResponse("serx_process_meeting_ended", steps, error.stepName, error.result);
        }
        throw error;
      }
    },
  );
}

async function executeNamed(toolName: string, input: Record<string, unknown>) {
  const tool = coreToolDefinitions.find((candidate) => candidate.name === toolName);
  if (!tool) {
    const missingToolError: SerxToolError = {
      category: "upstream_error",
      message: `Compound workflow references missing tool definition: ${toolName}`,
      retryable: false,
      status: 500,
    };
    return {
      ok: false,
      status: 500,
      data: null,
      error: missingToolError,
    } satisfies CoreResult;
  }
  return executeCoreTool(tool, input);
}

function pickOrgId(result: unknown): string {
  const orgId =
    (result as any)?.data?.org?.id ??
    (result as any)?.data?.event?.org_id ??
    (result as any)?.data?.org_id ??
    "";
  if (!orgId) {
    throw new Error("Unable to resolve org_id from workflow step output.");
  }
  return String(orgId);
}

function pickId(result: unknown): string | null {
  const id = (result as any)?.data?.id ?? (result as any)?.data?.event?.id ?? null;
  return id ? String(id) : null;
}

function pickMeetingId(result: unknown): string | null {
  const id = (result as any)?.data?.meeting?.id ?? (result as any)?.data?.id ?? null;
  return id ? String(id) : null;
}

function pickDealId(result: unknown): string | null {
  const id =
    (result as any)?.data?.meeting?.deal_id ??
    (result as any)?.data?.deal?.id ??
    (result as any)?.data?.deal_id ??
    null;
  return id ? String(id) : null;
}

function extractBookingUid(payload: Record<string, unknown>): string {
  const nested = payload.payload;
  if (typeof nested === "object" && nested && typeof (nested as any).uid === "string") {
    return (nested as any).uid;
  }
  if (typeof payload.uid === "string") {
    return payload.uid;
  }
  throw new Error("Unable to resolve booking UID from raw_event payload.");
}

export async function runHttpServer() {
  const server = buildServer();
  const app = express();

  app.use((_req, res, next) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    if (_req.method === "OPTIONS") {
      res.sendStatus(204);
      return;
    }
    next();
  });

  app.use(express.json({ limit: "2mb" }));

  app.get("/healthz", (_req, res) => {
    res.status(200).json({
      ok: true,
      service: "service-engine-x-mcp",
      drift: buildToolDriftReport(),
    });
  });

  app.post("/mcp", async (req, res) => {
    if (!ensureIngressAuth(req, res)) {
      return;
    }

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });

    res.on("close", () => {
      transport.close();
    });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });

  app.listen(env.PORT, () => {
    console.error(`service-engine-x-mcp listening on http://localhost:${env.PORT}/mcp`);
  });
}

export async function runStdioServer() {
  const server = buildServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("service-engine-x-mcp running via stdio transport");
}
