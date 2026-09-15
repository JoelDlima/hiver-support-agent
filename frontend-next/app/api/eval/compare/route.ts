import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../lib";

// BFF proxy: browser never touches FastAPI directly.
// Upstream: GET /eval/compare (workstream A, live, file-cached).
// Non-OK statuses pass through so the UI renders an honest pending/error state.
export async function GET(req: NextRequest) {
  const qs = req.nextUrl.searchParams.toString();
  const upstream = await fetch(`${FASTAPI_URL}/eval/compare${qs ? `?${qs}` : ""}`);
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}

export const dynamic = "force-dynamic";
