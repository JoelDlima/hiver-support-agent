import { NextRequest } from "next/server";
import { proxyJson } from "../../../../lib/proxy";

// BFF proxy: browser never touches FastAPI directly.
// Upstream: GET /eval/compare (workstream A, live, file-cached).
// Non-OK statuses pass through so the UI renders an honest pending/error state.
// Dead backend -> JSON 502 via proxyJson.
export async function GET(req: NextRequest) {
  const qs = req.nextUrl.searchParams.toString();
  return proxyJson(`/eval/compare${qs ? `?${qs}` : ""}`);
}

export const dynamic = "force-dynamic";
