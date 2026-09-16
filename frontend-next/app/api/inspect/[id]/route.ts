import { NextRequest } from "next/server";
import { proxyJson } from "../../../../lib/proxy";

// Thin fetch passthrough: GET /api/inspect/[id] -> GET {FASTAPI_URL}/inspect/[id]
// Dead backend -> JSON 502 via proxyJson.
export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  const id = encodeURIComponent(params.id);
  return proxyJson(`/inspect/${id}`);
}

export const dynamic = "force-dynamic";
