export declare const env: {
    allowDestructiveTools: boolean;
    enableResources: boolean;
    enablePrompts: boolean;
    NODE_ENV: "development" | "test" | "production";
    PORT: number;
    SERX_MCP_SHARED_SECRET: string;
    SERX_INTERNAL_API_BASE_URL: string;
    SERX_INTERNAL_API_KEY: string;
    SERX_SERVICE_API_TOKEN: string;
    SERX_ALLOW_DESTRUCTIVE_TOOLS: "true" | "false";
    SERX_ENABLE_RESOURCES: "true" | "false";
    SERX_ENABLE_PROMPTS: "true" | "false";
    SERX_TRANSPORT: "http" | "stdio";
};
export type Env = typeof env;
