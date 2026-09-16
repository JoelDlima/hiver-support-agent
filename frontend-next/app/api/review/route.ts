import { NextRequest } from "next/server";
import { proxyJson } from "../../../lib/proxy";

// GET /api/review -> FastAPI GET /review/queue (live inbox polling).
// Dead backend -> JSON 502 via proxyJson.
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const qs = new URLSearchParams();
  const status = searchParams.get("status");
  const brand = searchParams.get("brand");
  const limit = searchParams.get("limit");
  if (status) qs.set("status", status);
  if (brand) qs.set("brand", brand);
  if (limit) qs.set("limit", limit);
  return proxyJson(`/review/queue?${qs.toString()}`);
}

export const dynamic = "force-dynamic";
