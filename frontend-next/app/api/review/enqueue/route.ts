import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// POST /api/review/enqueue -> FastAPI POST /review/enqueue
export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${FASTAPI_URL}/review/enqueue`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: String(body.text || "").slice(0, 2000),
      brand: body.brand || "virgin",
      idempotency_key: body.idempotency_key || null,
      sla_minutes: body.sla_minutes ?? null,
    }),
  });
  const data = await upstream.json().catch(() => ({ error: "upstream empty" }));
  return NextResponse.json(data, { status: upstream.status });
}
