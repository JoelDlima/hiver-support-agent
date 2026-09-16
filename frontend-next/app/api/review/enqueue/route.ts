import { NextRequest } from "next/server";
import { proxyJson } from "../../../../lib/proxy";

// POST /api/review/enqueue -> FastAPI POST /review/enqueue
// Dead backend -> JSON 502 via proxyJson.
export async function POST(req: NextRequest) {
  const body = await req.json();
  return proxyJson("/review/enqueue", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: String(body.text || "").slice(0, 2000),
      brand: body.brand || "virgin",
      idempotency_key: body.idempotency_key || null,
      sla_minutes: body.sla_minutes ?? null,
    }),
  });
}
