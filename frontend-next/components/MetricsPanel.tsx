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
    return <p className="text-sm text-muted">Metrics: backend not reached yet (start FastAPI on port 8000).</p>;
  return (
    <div className="grid grid-cols-2 gap-1.5 text-sm">
      {(["predict_count", "escalate_count", "auto_count", "avg_latency_ms"] as const).map((k) => (
        <div key={k} className="rounded-md border border-line bg-canvas px-2 py-1.5">
          <div className="text-xs text-muted">{k.replace(/_/g, " ")}</div>
          <div className="font-mono text-base font-semibold tabular-nums">{String(metrics[k] ?? "none")}</div>
        </div>
      ))}
    </div>
  );
}
