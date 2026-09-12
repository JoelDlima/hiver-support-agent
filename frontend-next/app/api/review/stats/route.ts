import { NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

export async function GET() {
  const upstream = await fetch(`${FASTAPI_URL}/review/stats`);
  const data = await upstream.json().catch(() => ({ total: 0 }));
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
