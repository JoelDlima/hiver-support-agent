import { proxyJson } from "../../../../lib/proxy";

export async function GET() {
  return proxyJson("/review/stats");
}

export const dynamic = "force-dynamic";
