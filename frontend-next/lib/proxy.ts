// Server-only BFF helpers (route.ts files only — never import from client components).
// Every /api/* proxy funnels upstream fetch through these so a dead backend surfaces
// as JSON 502 ("backend unreachable") instead of an unhandled rejection -> Next 500
// HTML -> client "Predict failed: SyntaxError" cascade.
import { NextResponse } from "next/server";
import { FASTAPI_URL } from "../lib";

export function backendUnreachable() {
  return NextResponse.json(
    { detail: "backend unreachable — start FastAPI on :8000 (FASTAPI_URL)" },
    { status: 502 }
  );
}

// Server-side API key forwarding: when the operator sets HIVER_API_KEY for the
// Next.js server, every upstream call carries it as X-API-Key. Browser clients
// never see it (BFF pattern); direct-to-FastAPI callers must send it themselves.
function withApiKey(init?: RequestInit): RequestInit {
  const key = (process.env.HIVER_API_KEY || "").trim();
  if (!key) return init || {};
  const headers = new Headers(init?.headers);
  if (!headers.has("X-API-Key")) headers.set("X-API-Key", key);
  return { ...init, headers };
}

// JSON proxy with timeout (default 25s; long eval routes pass their own budget).
export async function proxyJson(path: string, init?: RequestInit, timeoutMs = 25000) {
  try {
    const upstream = await fetch(`${FASTAPI_URL}${path}`, {
      ...withApiKey(init),
      signal: AbortSignal.timeout(timeoutMs),
    });
    let data: unknown;
    try {
      data = await upstream.json();
    } catch {
      data = { detail: "upstream returned non-JSON" };
    }
    return NextResponse.json(data, { status: upstream.status });
  } catch {
    return backendUnreachable();
  }
}

// SSE passthrough (no timeout — streams stay open; connect errors still 502).
export async function proxyStream(path: string, init?: RequestInit) {
  try {
    const upstream = await fetch(`${FASTAPI_URL}${path}`, { ...withApiKey(init) });
    if (!upstream.body) return backendUnreachable();
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch {
    return backendUnreachable();
  }
}
