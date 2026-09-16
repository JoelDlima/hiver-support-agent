import { NextRequest } from "next/server";
import { proxyStream } from "../../../lib/proxy";

// SSE passthrough: FastAPI streams Groq tokens live; we relay bytes untouched.
// Dead backend -> JSON 502 via proxyStream (never a hung stream).
export async function POST(req: NextRequest) {
  const body = await req.json();
  return proxyStream("/predict/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({
      text: String(body.text || "").slice(0, 2000),
      brand: body.brand || "virgin",
    }),
  });
}

export const dynamic = "force-dynamic";
