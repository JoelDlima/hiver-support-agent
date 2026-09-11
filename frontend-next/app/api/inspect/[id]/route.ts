import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// Thin fetch passthrough: GET /api/inspect/[id] -> GET {FASTAPI_URL}/inspect/[id]
export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  const id = encodeURIComponent(params.id);
  const upstream = await fetch(`${FASTAPI_URL}/inspect/${id}`);
  const data = await upstream.json().catch(() => ({ error: "upstream empty" }));
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
