import { NextRequest, NextResponse } from "next/server";
import { listProposals } from "./list-proposals";
import { createProposal } from "./create-proposal";
import { validateApiToken, extractBearerToken } from "@/lib/auth";

export async function GET(request: NextRequest) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid || !auth.orgId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return listProposals(request, auth.orgId);
}

export async function POST(request: NextRequest) {
  const token = extractBearerToken(request.headers.get("authorization"));
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const auth = await validateApiToken(token);
  if (!auth.valid || !auth.orgId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return createProposal(request, auth.orgId);
}
