import { NextResponse } from "next/server";
import { getEndpointList } from "@/openapi";
import "@/openapi/register"; // Triggers registration

/**
 * GET /api
 * Returns API index with list of all registered endpoints.
 * Endpoint list is derived from OpenAPI registry (not hardcoded).
 */
export async function GET() {
  const endpoints = getEndpointList();

  const response = {
    name: "ServiceEngine API",
    version: "1.0.0",
    status: "running",
    endpoints,
  };

  return NextResponse.json(response, {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
