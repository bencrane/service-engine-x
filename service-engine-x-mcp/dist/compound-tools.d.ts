import { z } from "zod";
export declare const compoundToolSchemas: {
    serx_process_new_booking: z.ZodObject<{
        event_type_id: z.ZodNumber;
        raw_event: z.ZodObject<{
            trigger_event: z.ZodString;
            payload: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            org_id: z.ZodOptional<z.ZodString>;
            cal_booking_uid: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }>;
        booking_event: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        attendees: z.ZodOptional<z.ZodArray<z.ZodRecord<z.ZodString, z.ZodUnknown>, "many">>;
        meeting: z.ZodRecord<z.ZodString, z.ZodUnknown>;
        deal: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        create_deal: z.ZodDefault<z.ZodBoolean>;
    }, "strict", z.ZodTypeAny, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        booking_event: Record<string, unknown>;
        meeting: Record<string, unknown>;
        create_deal: boolean;
        attendees?: Record<string, unknown>[] | undefined;
        deal?: Record<string, unknown> | undefined;
    }, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        meeting: Record<string, unknown>;
        booking_event?: Record<string, unknown> | undefined;
        attendees?: Record<string, unknown>[] | undefined;
        deal?: Record<string, unknown> | undefined;
        create_deal?: boolean | undefined;
    }>;
    serx_process_booking_reschedule: z.ZodObject<{
        event_type_id: z.ZodNumber;
        raw_event: z.ZodObject<{
            trigger_event: z.ZodString;
            payload: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            org_id: z.ZodOptional<z.ZodString>;
            cal_booking_uid: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }>;
        booking_event: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        attendees: z.ZodOptional<z.ZodArray<z.ZodRecord<z.ZodString, z.ZodUnknown>, "many">>;
        meeting: z.ZodRecord<z.ZodString, z.ZodUnknown>;
    }, "strict", z.ZodTypeAny, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        booking_event: Record<string, unknown>;
        meeting: Record<string, unknown>;
        attendees?: Record<string, unknown>[] | undefined;
    }, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        meeting: Record<string, unknown>;
        booking_event?: Record<string, unknown> | undefined;
        attendees?: Record<string, unknown>[] | undefined;
    }>;
    serx_process_booking_cancelled: z.ZodObject<{
        event_type_id: z.ZodNumber;
        raw_event: z.ZodObject<{
            trigger_event: z.ZodString;
            payload: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            org_id: z.ZodOptional<z.ZodString>;
            cal_booking_uid: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }>;
        booking_event: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        update_deal_to_lost: z.ZodDefault<z.ZodBoolean>;
        lost_reason: z.ZodOptional<z.ZodString>;
    }, "strict", z.ZodTypeAny, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        booking_event: Record<string, unknown>;
        update_deal_to_lost: boolean;
        lost_reason?: string | undefined;
    }, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        booking_event?: Record<string, unknown> | undefined;
        update_deal_to_lost?: boolean | undefined;
        lost_reason?: string | undefined;
    }>;
    serx_process_meeting_ended: z.ZodObject<{
        event_type_id: z.ZodNumber;
        raw_event: z.ZodObject<{
            trigger_event: z.ZodString;
            payload: z.ZodRecord<z.ZodString, z.ZodUnknown>;
            org_id: z.ZodOptional<z.ZodString>;
            cal_booking_uid: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }, {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        }>;
        booking_event: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        meeting_update: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
        deal_update: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    }, "strict", z.ZodTypeAny, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        booking_event: Record<string, unknown>;
        meeting_update: Record<string, unknown>;
        deal_update?: Record<string, unknown> | undefined;
    }, {
        event_type_id: number;
        raw_event: {
            trigger_event: string;
            payload: Record<string, unknown>;
            org_id?: string | undefined;
            cal_booking_uid?: string | undefined;
        };
        booking_event?: Record<string, unknown> | undefined;
        meeting_update?: Record<string, unknown> | undefined;
        deal_update?: Record<string, unknown> | undefined;
    }>;
};
export type CompoundToolName = keyof typeof compoundToolSchemas;
export declare const compoundToolDescriptions: Record<CompoundToolName, string>;
