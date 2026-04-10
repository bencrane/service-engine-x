import { z } from "zod";
const EnvSchema = z.object({
    NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
    PORT: z.coerce.number().int().positive().default(3011),
    SERX_MCP_SHARED_SECRET: z.string().min(1),
    SERX_INTERNAL_API_BASE_URL: z.string().url(),
    SERX_INTERNAL_API_KEY: z.string().min(1),
    SERX_SERVICE_API_TOKEN: z.string().min(1),
    SERX_ALLOW_DESTRUCTIVE_TOOLS: z.enum(["true", "false"]).default("false"),
    SERX_ENABLE_RESOURCES: z.enum(["true", "false"]).default("false"),
    SERX_ENABLE_PROMPTS: z.enum(["true", "false"]).default("false"),
    SERX_TRANSPORT: z.enum(["http", "stdio"]).default("http"),
});
const parsed = EnvSchema.safeParse(process.env);
if (!parsed.success) {
    const details = parsed.error.issues
        .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
        .join("; ");
    throw new Error(`Invalid MCP environment configuration: ${details}`);
}
export const env = {
    ...parsed.data,
    allowDestructiveTools: parsed.data.SERX_ALLOW_DESTRUCTIVE_TOOLS === "true",
    enableResources: parsed.data.SERX_ENABLE_RESOURCES === "true",
    enablePrompts: parsed.data.SERX_ENABLE_PROMPTS === "true",
};
//# sourceMappingURL=env.js.map