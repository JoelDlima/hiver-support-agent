import { NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../lib";

export async function GET() {
  const upstream = await fetch(`${FASTAPI_URL}/metrics`);
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
