import { NextRequest } from "next/server";
import { proxyJson } from "../../../../lib/proxy";

// BFF proxy: browser never touches FastAPI directly.
// Upstream: POST /eval/retrieval-ablation (workstream A, live).
// Non-OK statuses pass through so the UI renders an honest pending/error state.
// Dead backend -> JSON 502 via proxyJson. Budget 120s (default 8 arms x 60 texts sync).
export async function POST(req: NextRequest) {
  const body = await req.json();
  return proxyJson(
    "/eval/retrieval-ablation",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brand: body.brand || "virgin",
        k_list: Array.isArray(body.k_list) ? body.k_list : [1, 5],
        arms: Array.isArray(body.arms) ? body.arms : ["keyword", "virgin_nn"],
        context_window: Array.isArray(body.context_window) ? body.context_window : [0, 2],
      }),
    },
    120000
  );
}
