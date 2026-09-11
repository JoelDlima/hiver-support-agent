"use client";

export default function ConfidenceBars({
  confidence,
  decision,
}: {
  confidence: number;
  decision: string;
}) {
  const pct = Math.round(Math.min(Math.max(confidence, 0), 1) * 100);
  const band = confidence < 0.45 ? "LOW → escalate (<0.45)" : confidence < 0.7 ? "MEDIUM → review" : "HIGH → auto-eligible";
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-slate-400">
        <span>Intent confidence</span>
        <span className="tabular-nums">{pct}% · {band}</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full ${confidence < 0.45 ? "bg-red-400" : confidence < 0.7 ? "bg-amber-300" : "bg-emerald-400"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="mt-1 text-xs text-slate-400">
        Decision: <span className="font-semibold text-slate-200">{decision}</span>
      </div>
    </div>
  );
}
