import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// BFF proxy: browser never touches FastAPI or keys directly.
// Upstream: POST /judge/groundedness (workstream A, live: Groq leg when keyed,
// deterministic offline heuristic otherwise). Non-OK statuses pass through so
// the UI renders an honest pending/error state instead of fake data.
export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${FASTAPI_URL}/judge/groundedness`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brand: body.brand || "virgin",
      text: String(body.text || "").slice(0, 2000),
      reply: String(body.reply || "").slice(0, 2000),
      passage_ids: Array.isArray(body.passage_ids) ? body.passage_ids : [],
    }),
  });
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
