#!/usr/bin/env node
import { env } from "./env.js";
import { runHttpServer, runStdioServer } from "./server.js";
async function main() {
    if (env.SERX_TRANSPORT === "stdio") {
        await runStdioServer();
        return;
    }
    await runHttpServer();
}
main().catch((error) => {
    console.error("Failed to start service-engine-x-mcp:", error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map