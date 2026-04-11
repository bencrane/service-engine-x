import { createServer, request as httpRequest } from "node:http";

const PUBLIC_PORT = parseInt(process.env.PORT || "8080", 10);
const BACKEND_PORT = parseInt(process.env.MCP_PROXY_PORT || "9090", 10);

const server = createServer((clientReq, clientRes) => {
  const headers = { ...clientReq.headers };

  // Normalize Authorization: Bearer → X-API-Key so mcp-proxy accepts it
  if (!headers["x-api-key"] && headers.authorization) {
    const match = headers.authorization.match(/^Bearer\s+(.+)$/i);
    if (match) {
      headers["x-api-key"] = match[1];
    }
  }

  delete headers.host;

  const proxyReq = httpRequest(
    {
      hostname: "127.0.0.1",
      port: BACKEND_PORT,
      path: clientReq.url,
      method: clientReq.method,
      headers,
    },
    (proxyRes) => {
      clientRes.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(clientRes, { end: true });
    },
  );

  proxyReq.on("error", (err) => {
    console.error("[auth-proxy] backend error:", err.message);
    if (!clientRes.headersSent) {
      clientRes.writeHead(502, { "Content-Type": "application/json" });
    }
    clientRes.end(JSON.stringify({ error: "backend unavailable" }));
  });

  clientReq.pipe(proxyReq, { end: true });
});

server.listen(PUBLIC_PORT, "::", () => {
  console.log(
    `[auth-proxy] listening on :${PUBLIC_PORT}, forwarding to mcp-proxy on :${BACKEND_PORT}`,
  );
});
