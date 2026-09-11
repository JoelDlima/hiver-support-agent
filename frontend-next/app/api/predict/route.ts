import { NextRequest, NextResponse } from "next/server";
import { FASTAPI_URL } from "../../../lib";

// BFF proxy: browser never touches FastAPI or keys directly.
export async function POST(req: NextRequest) {
  const body = await req.json();
  const upstream = await fetch(`${FASTAPI_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: String(body.text || "").slice(0, 2000),
      brand: body.brand || "virgin",
    }),
  });
  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
