import { proxyJson } from "../../../lib/proxy";

export async function GET() {
  return proxyJson("/metrics");
}

export const dynamic = "force-dynamic";
