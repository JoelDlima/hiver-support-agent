import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// BFF proxy: browser never touches FastAPI directly.
// Upstream GET /eval/compare may not exist yet (workstream A builds it in
// parallel) — the status code passes through so the UI can render an honest
// "endpoint pending" state instead of fake data.
export async function GET(req: NextRequest) {
  const qs = req.nextUrl.searchParams.toString();
  const upstream = await fetch(`${FASTAPI_URL}/eval/compare${qs ? `?${qs}` : ""}`);
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
