import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../../../lib";

// POST /api/review/[id]/edit -> APPROVED_WITH_EDITS (feeds golden candidates)
export async function POST(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await req.json().catch(() => ({}));
  const id = encodeURIComponent(params.id);
  const upstream = await fetch(`${FASTAPI_URL}/review/${id}/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      reviewer: body.reviewer || "reviewer",
      rationale: body.rationale || "",
      final_text: body.final_text || "",
      corrected_intent: body.corrected_intent || null,
    }),
  });
  const data = await upstream.json().catch(() => ({ error: "upstream empty" }));
  return NextResponse.json(data, { status: upstream.status });
}
