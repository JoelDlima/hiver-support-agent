// GET /api/graph -> FastAPI GET /graph (Graphify repository knowledge graph HTML).
// Dead backend -> plain-text 502 (never an unhandled rejection).
export async function GET() {
  try {
    // HTML (not SSE) — fetch with timeout, pass text through with backend status.
    const { FASTAPI_URL } = await import("../../../lib");
    const upstream = await fetch(`${FASTAPI_URL}/graph`, {
      signal: AbortSignal.timeout(25000),
    });
    const html = await upstream.text();
    return new Response(html, {
      status: upstream.status,
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  } catch {
    return new Response("backend unreachable — start FastAPI on :8000 (FASTAPI_URL)", {
      status: 502,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }
}

export const dynamic = "force-dynamic";
