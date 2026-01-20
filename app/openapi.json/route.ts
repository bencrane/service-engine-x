import { NextResponse } from "next/server";
import { getOpenAPISpec } from "@/openapi";
import "@/openapi/register"; // Triggers registration

export async function GET() {
  const spec = getOpenAPISpec();

  return NextResponse.json(spec, {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
