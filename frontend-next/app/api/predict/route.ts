import { NextRequest } from "next/server";
import { proxyJson } from "../../../lib/proxy";

// BFF proxy: browser never touches FastAPI or keys directly.
// Dead backend -> JSON 502 via proxyJson (never a Next 500 HTML cascade).
export async function POST(req: NextRequest) {
  const body = await req.json();
  return proxyJson("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: String(body.text || "").slice(0, 2000),
      brand: body.brand || "virgin",
    }),
  });
}
