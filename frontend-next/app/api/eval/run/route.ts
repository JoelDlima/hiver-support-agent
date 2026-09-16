import { NextRequest } from "next/server";
import { proxyStream } from "../../../../lib/proxy";

// Thin SSE passthrough: POST /api/eval/run -> {FASTAPI_URL}/eval/run (forward JSON body)
// Dead backend -> JSON 502 via proxyStream (never a hung stream).
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  return proxyStream("/eval/run", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(body),
  });
}

export const dynamic = "force-dynamic";
