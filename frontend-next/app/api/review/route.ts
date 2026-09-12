import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../lib";

// GET /api/review -> FastAPI GET /review/queue (live inbox polling).
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const qs = new URLSearchParams();
  const status = searchParams.get("status");
  const brand = searchParams.get("brand");
  const limit = searchParams.get("limit");
  if (status) qs.set("status", status);
  if (brand) qs.set("brand", brand);
  if (limit) qs.set("limit", limit);
  const upstream = await fetch(`${FASTAPI_URL}/review/queue?${qs.toString()}`);
  const data = await upstream.json().catch(() => ({ items: [], count: 0 }));
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
