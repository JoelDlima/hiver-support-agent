import { NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

export async function GET() {
  const upstream = await fetch(`${FASTAPI_URL}/review/matrix`);
  const data = await upstream.json().catch(() => ({ matrix: null }));
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
