import { FASTAPI_URL } from "../../../lib";

// Thin SSE passthrough: GET /api/logs -> {FASTAPI_URL}/logs/stream
export async function GET() {
  const upstream = await fetch(`${FASTAPI_URL}/logs/stream`, {
    headers: { Accept: "text/event-stream" },
  });
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

export const dynamic = "force-dynamic";
