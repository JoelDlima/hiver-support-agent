import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// BFF proxy: browser never touches FastAPI directly.
// Upstream POST /eval/retrieval-ablation may not exist yet (workstream A builds
// it in parallel) — the status code passes through so the UI can render an
// honest "endpoint pending" state instead of fake data.
export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${FASTAPI_URL}/eval/retrieval-ablation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      brand: body.brand || "virgin",
      k_list: Array.isArray(body.k_list) ? body.k_list : [1, 5],
      arms: Array.isArray(body.arms) ? body.arms : ["keyword", "virgin_nn"],
      context_window: Array.isArray(body.context_window) ? body.context_window : [0, 2],
    }),
  });
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
