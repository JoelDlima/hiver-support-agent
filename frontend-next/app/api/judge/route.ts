import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../lib";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${FASTAPI_URL}/judge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      intent: body.intent || "other_out_of_scope",
      draft_reply: body.draft_reply || "",
      passage_ids: body.passage_ids || [],
      inbound: String(body.inbound || "").slice(0, 800),
    }),
  });
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
