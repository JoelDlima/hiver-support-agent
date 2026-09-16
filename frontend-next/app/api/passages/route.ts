import { NextRequest } from "next/server";
import { proxyJson } from "../../../lib/proxy";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const brand = searchParams.get("brand") || "virgin";
  const q = (searchParams.get("q") || "").slice(0, 500);
  return proxyJson(
    `/passages?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(q)}`
  );
}

export const dynamic = "force-dynamic";
