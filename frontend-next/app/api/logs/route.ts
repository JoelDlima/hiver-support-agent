import { proxyStream } from "../../../lib/proxy";

// Thin SSE passthrough: GET /api/logs -> {FASTAPI_URL}/logs/stream
// Dead backend -> JSON 502 via proxyStream (never a hung stream).
export async function GET() {
  return proxyStream("/logs/stream", {
    headers: { Accept: "text/event-stream" },
  });
}

export const dynamic = "force-dynamic";
