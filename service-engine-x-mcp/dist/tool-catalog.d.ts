import { z } from "zod";
import { type ApiCallResult, type AuthMode, type HttpMethod } from "./http-client.js";
export type ToolKind = "RO" | "IDEMP" | "MUT" | "DEST";
export interface ToolDefinition {
    name: string;
    kind: ToolKind;
    method: HttpMethod;
    path: string;
    authMode: AuthMode;
    description: string;
    allowBody?: boolean;
    suggestedTools?: string[];
}
export declare const ToolOutputSchema: {
    ok: z.ZodBoolean;
    status: z.ZodNumber;
    data: z.ZodUnknown;
    error: z.ZodOptional<z.ZodObject<{
        category: z.ZodEnum<["auth_error", "validation_error", "not_found", "conflict", "upstream_error"]>;
        message: z.ZodString;
        retryable: z.ZodOptional<z.ZodBoolean>;
        suggestedTools: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
        status: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        message: string;
        category: "auth_error" | "validation_error" | "not_found" | "conflict" | "upstream_error";
        status?: number | undefined;
        retryable?: boolean | undefined;
        suggestedTools?: string[] | undefined;
    }, {
        message: string;
        category: "auth_error" | "validation_error" | "not_found" | "conflict" | "upstream_error";
        status?: number | undefined;
        retryable?: boolean | undefined;
        suggestedTools?: string[] | undefined;
    }>>;
};
export declare function annotationFromKind(kind: ToolKind): {
    readOnlyHint: boolean;
    idempotentHint: boolean;
    destructiveHint: boolean;
    openWorldHint: boolean;
};
export declare const coreToolDefinitions: ToolDefinition[];
export declare function isDestructiveBlocked(def: ToolDefinition): boolean;
export declare function executeCoreTool(def: ToolDefinition, input: Record<string, unknown>): Promise<ApiCallResult>;
export declare function getToolInputSchema(def: ToolDefinition): z.ZodObject<Record<string, z.ZodTypeAny>, "passthrough", z.ZodTypeAny, z.objectOutputType<Record<string, z.ZodTypeAny>, z.ZodTypeAny, "passthrough">, z.objectInputType<Record<string, z.ZodTypeAny>, z.ZodTypeAny, "passthrough">>;
