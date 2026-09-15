"use client";

// SmartGrey hero helpers shared by the demo shell. These exact class maps and
// thresholds previously lived inline in app/page.tsx; they are factored out so
// the tab sections reuse identical styling (B5 requires STAGE_PILL /
// STALE_AFTER_MS reuse for the liveness pill).

export const STALE_AFTER_MS = 60_000;

export const STAGE_PILL: Record<string, string> = {
  LIVE: "border-teal-500/40 bg-teal-500/10 text-teal-700 dark:text-teal-300",
  STALE: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  AWAITING: "border-hairline-soft bg-paper text-muted",
  RUNNING:
    "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse",
};

export function stageStatus(hasResult: boolean, stale: boolean): "LIVE" | "STALE" | "AWAITING" {
  if (!hasResult) return "AWAITING";
  return stale ? "STALE" : "LIVE";
}

export function isStale(resultAt: number | null, now: number): boolean {
  return resultAt !== null && now - resultAt > STALE_AFTER_MS;
}

export function formatMs(v: unknown): string {
  return typeof v === "number" && Number.isFinite(v) ? String(Math.round(v)) : "—";
}

export function isEscalateDecision(decision: string | undefined): boolean {
  return /escalate/i.test(decision || "");
}
