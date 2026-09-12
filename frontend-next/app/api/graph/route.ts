// GET /api/graph -> FastAPI GET /graph (Graphify repository knowledge graph HTML).
import { FASTAPI_URL } from "../../../lib";

export async function GET() {
  const upstream = await fetch(`${FASTAPI_URL}/graph`);
  const html = await upstream.text();
  return new Response(html, {
    status: upstream.status,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

export const dynamic = "force-dynamic";
