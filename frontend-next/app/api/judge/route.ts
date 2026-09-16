import { NextRequest } from "next/server";
import { proxyJson } from "../../../lib/proxy";

export async function POST(req: NextRequest) {
  const body = await req.json();
  return proxyJson("/judge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      intent: body.intent || "other_out_of_scope",
      draft_reply: body.draft_reply || "",
      passage_ids: body.passage_ids || [],
      inbound: String(body.inbound || "").slice(0, 800),
    }),
  });
}
