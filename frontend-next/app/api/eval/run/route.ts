import { NextRequest } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// Thin SSE passthrough: POST /api/eval/run -> {FASTAPI_URL}/eval/run (forward JSON body)
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const upstream = await fetch(`${FASTAPI_URL}/eval/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(body),
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
