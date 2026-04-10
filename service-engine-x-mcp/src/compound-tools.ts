import { z } from "zod";

export const compoundToolSchemas = {
  serx_process_new_booking: z
    .object({
      event_type_id: z.number().int().positive(),
      raw_event: z.object({
        trigger_event: z.string().min(1),
        payload: z.record(z.unknown()),
        org_id: z.string().uuid().optional(),
        cal_booking_uid: z.string().optional(),
      }),
      booking_event: z.record(z.unknown()).default({}),
      attendees: z.array(z.record(z.unknown())).optional(),
      meeting: z.record(z.unknown()),
      deal: z.record(z.unknown()).optional(),
      create_deal: z.boolean().default(false),
    })
    .strict(),
  serx_process_booking_reschedule: z
    .object({
      event_type_id: z.number().int().positive(),
      raw_event: z.object({
        trigger_event: z.string().min(1),
        payload: z.record(z.unknown()),
        org_id: z.string().uuid().optional(),
        cal_booking_uid: z.string().optional(),
      }),
      booking_event: z.record(z.unknown()).default({}),
      attendees: z.array(z.record(z.unknown())).optional(),
      meeting: z.record(z.unknown()),
    })
    .strict(),
  serx_process_booking_cancelled: z
    .object({
      event_type_id: z.number().int().positive(),
      raw_event: z.object({
        trigger_event: z.string().min(1),
        payload: z.record(z.unknown()),
        org_id: z.string().uuid().optional(),
        cal_booking_uid: z.string().optional(),
      }),
      booking_event: z.record(z.unknown()).default({}),
      update_deal_to_lost: z.boolean().default(false),
      lost_reason: z.string().optional(),
    })
    .strict(),
  serx_process_meeting_ended: z
    .object({
      event_type_id: z.number().int().positive(),
      raw_event: z.object({
        trigger_event: z.string().min(1),
        payload: z.record(z.unknown()),
        org_id: z.string().uuid().optional(),
        cal_booking_uid: z.string().optional(),
      }),
      booking_event: z.record(z.unknown()).default({}),
      meeting_update: z.record(z.unknown()).default({ status: "completed" }),
      deal_update: z.record(z.unknown()).optional(),
    })
    .strict(),
};

export type CompoundToolName = keyof typeof compoundToolSchemas;

export const compoundToolDescriptions: Record<CompoundToolName, string> = {
  serx_process_new_booking:
    "Guardrailed workflow for BOOKING_CREATED handling: resolves org, stores raw event, normalizes booking event, upserts attendees, creates/dedupes meeting, optionally creates deal, and marks raw event processed with step-level diagnostics.",
  serx_process_booking_reschedule:
    "Guardrailed workflow for BOOKING_RESCHEDULED handling: resolves org, stores raw event, normalizes booking event, upserts attendees, creates/dedupes meeting with reschedule context, and marks raw event processed.",
  serx_process_booking_cancelled:
    "Guardrailed workflow for BOOKING_CANCELLED handling: resolves org, stores raw event, normalizes booking event, cancels matching meeting, optionally transitions linked deal to lost, then marks raw event processed.",
  serx_process_meeting_ended:
    "Guardrailed workflow for MEETING_ENDED handling: resolves org, stores raw event, normalizes booking event, updates meeting completion/no-show fields, optionally advances deal state, and marks raw event processed.",
};
