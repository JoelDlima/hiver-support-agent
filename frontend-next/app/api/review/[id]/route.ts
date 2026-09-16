import { NextRequest } from "next/server";
import { proxyJson } from "../../../../lib/proxy";

// GET /api/review/[id] -> FastAPI GET /review/[id]
// Dead backend -> JSON 502 via proxyJson.
export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  const id = encodeURIComponent(params.id);
  return proxyJson(`/review/${id}`);
}

export const dynamic = "force-dynamic";
