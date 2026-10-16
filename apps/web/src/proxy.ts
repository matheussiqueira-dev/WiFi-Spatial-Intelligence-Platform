import { NextRequest, NextResponse } from "next/server";
import { randomBytes } from "node:crypto";

export function proxy(request: NextRequest) {
  const nonce = randomBytes(24).toString("base64");
  const endpoint = new URL(
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
  );
  const websocket = new URL(endpoint);
  websocket.protocol = endpoint.protocol === "https:" ? "wss:" : "ws:";
  const policy = [
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "img-src 'self' data:",
    "font-src 'self'",
    `connect-src 'self' ${endpoint.origin} ${websocket.origin}`,
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${process.env.NODE_ENV === "development" ? " 'unsafe-eval'" : ""}`,
    // React's bounded chart style attributes remain necessary; no inline scripts.
    "style-src 'self' 'unsafe-inline'",
  ].join("; ");
  const headers = new Headers(request.headers);
  headers.set("x-nonce", nonce);
  headers.set("Content-Security-Policy", policy);
  const response = NextResponse.next({ request: { headers } });
  response.headers.set("Content-Security-Policy", policy);
  response.headers.set("Cache-Control", "private, no-store");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
