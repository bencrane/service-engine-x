import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const hostname = request.headers.get("host") || "";
  const pathname = request.nextUrl.pathname;

  // Handle api.serviceengine.xyz subdomain
  if (hostname.startsWith("api.")) {
    // If visiting root of api subdomain, serve /api
    if (pathname === "/") {
      return NextResponse.rewrite(new URL("/api", request.url));
    }

    // If visiting /clients on api subdomain, serve /api/clients
    // (allows api.serviceengine.xyz/clients instead of api.serviceengine.xyz/api/clients)
    if (!pathname.startsWith("/api") && !pathname.startsWith("/_next")) {
      return NextResponse.rewrite(new URL(`/api${pathname}`, request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match all paths except static files
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
