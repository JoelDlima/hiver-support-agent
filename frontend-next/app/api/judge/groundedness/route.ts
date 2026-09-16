import { NextRequest } from "next/server";
import { proxyJson } from "../../../../lib/proxy";

// BFF proxy: browser never touches FastAPI or keys directly.
// Upstream: POST /judge/groundedness (workstream A, live: Groq leg when keyed,
// deterministic offline heuristic otherwise). Non-OK statuses pass through so
// the UI renders an honest pending/error state instead of fake data.
// Dead backend -> JSON 502 via proxyJson.
export async function POST(req: NextRequest) {
  const body = await req.json();
  return proxyJson("/judge/groundedness", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brand: body.brand || "virgin",
      text: String(body.text || "").slice(0, 2000),
      reply: String(body.reply || "").slice(0, 2000),
      passage_ids: Array.isArray(body.passage_ids) ? body.passage_ids : [],
    }),
  });
}
