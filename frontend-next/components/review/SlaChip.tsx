"use client";

export function slaState(slaDueAt: string | null | undefined, now: number): "ok" | "soon" | "overdue" | "none" {
  if (!slaDueAt) return "none";
  const due = Date.parse(slaDueAt);
  if (!Number.isFinite(due)) return "none";
  const ms = due - now;
  if (ms < 0) return "overdue";
  if (ms < 5 * 60_000) return "soon";
  return "ok";
}

export function slaLabel(slaDueAt: string | null | undefined, now: number): string {
  if (!slaDueAt) return "no SLA";
  const due = Date.parse(slaDueAt);
  if (!Number.isFinite(due)) return "no SLA";
  const ms = due - now;
  const abs = Math.abs(ms);
  const mins = Math.floor(abs / 60_000);
  const secs = Math.floor((abs % 60_000) / 1000);
  if (ms < 0) return `overdue ${mins}m`;
  if (mins < 1) return `${secs}s left`;
  return `${mins}m left`;
}

const CLS: Record<string, string> = {
  ok: "border-teal-500/40 bg-teal-500/10 text-teal-700 dark:text-teal-300",
  soon: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  overdue: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
  none: "border-hairline-soft bg-paper text-muted",
};

export default function SlaChip({ slaDueAt, now }: { slaDueAt?: string | null; now: number }) {
  const st = slaState(slaDueAt, now);
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold tabular-nums ${CLS[st]}`}
      title={slaDueAt || "no SLA deadline"}
    >
      {st === "overdue" ? "● " : st === "soon" ? "◐ " : "○ "}
      {slaLabel(slaDueAt, now)}
    </span>
  );
}
