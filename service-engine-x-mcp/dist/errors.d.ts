export type SerxErrorCategory = "auth_error" | "validation_error" | "not_found" | "conflict" | "upstream_error";
export interface SerxToolError {
    category: SerxErrorCategory;
    message: string;
    retryable?: boolean;
    suggestedTools?: string[];
    status?: number;
}
export declare function classifyHttpStatus(status: number): SerxErrorCategory;
export declare function buildActionableMessage(category: SerxErrorCategory, detail: string, toolName: string): string;
