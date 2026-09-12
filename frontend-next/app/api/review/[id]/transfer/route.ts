import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../../lib";

// GET /api/review/[id]/transfer -> FastAPI warm-transfer payload
export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  const id = encodeURIComponent(params.id);
  const upstream = await fetch(`${FASTAPI_URL}/review/${id}/transfer`);
  const data = await upstream.json().catch(() => ({ error: "upstream empty" }));
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
