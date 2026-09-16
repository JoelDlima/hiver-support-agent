import { proxyJson } from "../../../../lib/proxy";

export async function GET() {
  return proxyJson("/review/matrix");
}

export const dynamic = "force-dynamic";
