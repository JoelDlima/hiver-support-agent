import { NextRequest } from "next/server";
import { proxyJson } from "../../../lib/proxy";

// Thin passthrough: GET /api/embed2d?brand&q -> {FASTAPI_URL}/embed2d
// Dead backend -> JSON 502 via proxyJson.
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const brand = searchParams.get("brand") || "virgin";
  const q = (searchParams.get("q") || "").slice(0, 500);
  return proxyJson(
    `/embed2d?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(q)}`
  );
}

export const dynamic = "force-dynamic";
