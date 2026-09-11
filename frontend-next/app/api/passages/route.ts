import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../lib";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const brand = searchParams.get("brand") || "virgin";
  const q = (searchParams.get("q") || "").slice(0, 500);
  const upstream = await fetch(
    `${FASTAPI_URL}/passages?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(q)}`
  );
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
