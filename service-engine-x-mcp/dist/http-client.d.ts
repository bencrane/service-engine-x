import { type SerxToolError } from "./errors.js";
export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
export type AuthMode = "internal" | "service";
export interface ApiCallArgs {
    toolName: string;
    method: HttpMethod;
    path: string;
    authMode: AuthMode;
    query?: Record<string, unknown>;
    body?: unknown;
}
export interface ApiCallResult {
    ok: boolean;
    status: number;
    data: unknown;
    error?: SerxToolError;
}
export declare function callSerxApi(args: ApiCallArgs): Promise<ApiCallResult>;
