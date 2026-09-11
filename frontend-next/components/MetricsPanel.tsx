"use client";

import { useEffect, useState } from "react";

// Live /metrics polling (5s). No extra deps.
export default function MetricsPanel() {
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const r = await fetch("/api/metrics");
        const j = await r.json();
        if (alive) setMetrics(j);
      } catch {
        /* backend may be down during demo setup */
      }
    };
    tick();
    const id = setInterval(tick, 5000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);
  if (!metrics)
    return <p className="text-sm text-slate-500">Metrics: backend not reached yet (start FastAPI on :8000).</p>;
  return (
    <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
      {(["predict_count", "escalate_count", "auto_count", "avg_latency_ms"] as const).map((k) => (
        <div key={k} className="rounded-md border border-slate-800 bg-slate-900/50 px-3 py-2">
          <div className="text-xs text-slate-500">{k}</div>
          <div className="tabular-nums text-lg font-semibold">{String(metrics[k] ?? "—")}</div>
        </div>
      ))}
    </div>
  );
}
