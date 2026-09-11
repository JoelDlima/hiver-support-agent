import { NextRequest } from "next/server";
import { FASTAPI_URL } from "../../../lib";

// SSE passthrough: FastAPI streams Groq tokens live; we relay bytes untouched.
export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${FASTAPI_URL}/predict/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({
      text: String(body.text || "").slice(0, 2000),
      brand: body.brand || "virgin",
    }),
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
