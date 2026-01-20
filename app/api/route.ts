import { NextRequest, NextResponse } from "next/server";
import { getEndpointList } from "@/openapi";
import "@/openapi/register"; // Triggers registration

/**
 * GET /api
 * Returns API index with list of all registered endpoints.
 * Returns HTML for browsers, JSON for API clients.
 */
export async function GET(request: NextRequest) {
  const endpoints = getEndpointList();
  const accept = request.headers.get("accept") || "";

  // Return JSON if explicitly requested
  if (accept.includes("application/json") && !accept.includes("text/html")) {
    return NextResponse.json(
      {
        name: "ServiceEngine API",
        version: "1.0.0",
        status: "running",
        endpoints,
      },
      {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  }

  // Return HTML for browsers
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ServiceEngine API</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0a0a0a;
      color: #e5e5e5;
      padding: 40px;
      line-height: 1.6;
    }
    h1 {
      font-size: 2rem;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .status {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #22c55e;
      font-size: 0.95rem;
      margin-bottom: 24px;
    }
    .status::before {
      content: '';
      width: 10px;
      height: 10px;
      background: #22c55e;
      border-radius: 50%;
    }
    .spec-link {
      color: #60a5fa;
      text-decoration: none;
      font-size: 0.95rem;
      margin-bottom: 32px;
      display: inline-block;
    }
    .spec-link:hover { text-decoration: underline; }
    h2 {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 32px 0 16px;
    }
    table {
      width: 100%;
      max-width: 900px;
      border-collapse: collapse;
    }
    th {
      text-align: left;
      padding: 12px 16px;
      border-bottom: 1px solid #333;
      font-weight: 600;
      font-size: 0.85rem;
    }
    td {
      padding: 12px 16px;
      border-bottom: 1px solid #1a1a1a;
    }
    tr:hover { background: #111; }
    .method {
      font-weight: 500;
      font-size: 0.85rem;
    }
    .method-get { color: #22c55e; }
    .method-post { color: #3b82f6; }
    .method-put { color: #f59e0b; }
    .method-patch { color: #f59e0b; }
    .method-delete { color: #ef4444; }
    .path {
      color: #60a5fa;
      text-decoration: none;
      font-family: 'SF Mono', Monaco, monospace;
      font-size: 0.9rem;
    }
    .path:hover { text-decoration: underline; }
    .description {
      color: #a3a3a3;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <h1>ServiceEngine API</h1>
  <div class="status">Running</div>
  <a href="/openapi.json" class="spec-link">OpenAPI Specification →</a>

  <h2>Endpoints</h2>
  <table>
    <thead>
      <tr>
        <th>Method</th>
        <th>Path</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      ${endpoints
        .map(
          (ep) => `
        <tr>
          <td class="method method-${ep.method.toLowerCase()}">${ep.method}</td>
          <td><a href="${ep.path}" class="path">${ep.path}</a></td>
          <td class="description">${ep.description}</td>
        </tr>
      `
        )
        .join("")}
    </tbody>
  </table>
</body>
</html>`;

  return new NextResponse(html, {
    headers: {
      "Content-Type": "text/html",
    },
  });
}
