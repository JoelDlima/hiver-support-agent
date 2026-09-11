"use client";

export default function ConfidenceBars({
  confidence,
  decision,
}: {
  confidence: number;
  decision: string;
}) {
  const pct = Math.round(Math.min(Math.max(confidence, 0), 1) * 100);
  const band =
    confidence < 0.45 ? "Low, escalate below 0.45" : confidence < 0.7 ? "Medium, review" : "High, auto eligible";
  const bar =
    confidence < 0.45 ? "var(--danger)" : confidence < 0.7 ? "var(--warning)" : "var(--success)";
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-muted">
        <span>Intent confidence</span>
        <span className="font-mono tabular-nums">{pct}%</span>
      </div>
      <div className="h-2.5 overflow-hidden rounded-full border border-line bg-canvas">
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: bar }} />
      </div>
      <p className="mt-1 text-xs text-muted">{band}</p>
      <p className="mt-1 text-xs text-muted">
        Decision: <span className="font-semibold text-ink">{decision}</span>
      </p>
    </div>
  );
}
