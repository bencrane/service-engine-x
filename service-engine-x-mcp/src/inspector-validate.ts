import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");

async function main() {
  const serverEntry = path.resolve(projectRoot, "dist/index.js");
  const client = new Client(
    {
      name: "serx-mcp-validator",
      version: "1.0.0",
    },
    {
      capabilities: {},
    },
  );

  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [serverEntry],
    cwd: projectRoot,
    env: {
      ...process.env,
      SERX_TRANSPORT: "stdio",
      SERX_MCP_AUTH_TOKEN: "validation-secret",
      SERX_INTERNAL_API_BASE_URL: "http://127.0.0.1:3000",
      SERX_INTERNAL_API_KEY: "validation-internal-key",
      SERX_SERVICE_API_TOKEN: "validation-service-token",
      SERX_ALLOW_DESTRUCTIVE_TOOLS: "false",
    },
  });

  try {
    await client.connect(transport);
    const toolList = await client.listTools();
    const toolNames = toolList.tools.map((tool) => tool.name).sort();

    const requiredTools = [
      "serx_create_cal_raw_event",
      "serx_process_new_booking",
      "serx_process_booking_cancelled",
      "serx_list_clients",
      "serx_create_order",
    ];

    const missing = requiredTools.filter((name) => !toolNames.includes(name));
    if (missing.length > 0) {
      throw new Error(`Missing required tools in MCP registration: ${missing.join(", ")}`);
    }

    console.log(
      JSON.stringify(
        {
          ok: true,
          total_tools: toolNames.length,
          required_tools_validated: requiredTools,
        },
        null,
        2,
      ),
    );
  } finally {
    await client.close();
  }
}

main().catch((error) => {
  console.error("Inspector validation failed:", error);
  process.exit(1);
});
