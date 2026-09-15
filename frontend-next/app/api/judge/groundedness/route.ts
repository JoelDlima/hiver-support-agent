import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// BFF proxy: browser never touches FastAPI or keys directly.
// Upstream POST /judge/groundedness may not exist yet (workstream A builds it
// in parallel) — the status code passes through so the UI can render an honest
// "endpoint pending" state instead of fake data.
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
