import { NextRequest } from "next/server";
import { proxyJson } from "../../../../../lib/proxy";

// POST /api/review/[id]/edit -> APPROVED_WITH_EDITS (feeds golden candidates)
// Dead backend -> JSON 502 via proxyJson.
export async function POST(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await req.json().catch(() => ({}));
  const id = encodeURIComponent(params.id);
  return proxyJson(`/review/${id}/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      reviewer: body.reviewer || "reviewer",
      rationale: body.rationale || "",
      final_text: body.final_text || "",
      corrected_intent: body.corrected_intent || null,
    }),
  });
}
