"use client";

// Retrieval-ablation panel. POSTs /api/eval/ablation (proxied to workstream A's
// POST /eval/retrieval-ablation) on demand — the run may compute, so it is
// button-triggered, not auto-fetched. Pending/unreachable states are explicit;
// nothing is rendered until the endpoint answers with schema-valid JSON.

import { useState } from "react";
import { AblationSchema, type AblationPayload } from "../proof/schemas";
import { CurlButton, LiveBadge } from "./widgets";

const BODY = { brand: "virgin", k_list: [1, 5], arms: ["keyword", "virgin_nn"], context_window: [0, 2] };

export default function AblationPanel() {
  const [running, setRunning] = useState(false);
  const [data, setData] = useState<AblationPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const curl = `curl -X POST http://127.0.0.1:8000/eval/retrieval-ablation -H "Content-Type: application/json" -d '${JSON.stringify(BODY).replace(/'/g, "'\\''")}'`;

  async function run() {
    setRunning(true);
    setError(null);
    try {
      const r = await fetch("/api/eval/ablation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(BODY),
      });
      if (!r.ok) {
        if ([404, 405, 501].includes(r.status)) {
          throw new Error(`endpoint pending (status ${r.status}, workstream A)`);
        }
        throw new Error(`ablation returned status ${r.status}`);
      }
      const parsed = AblationSchema.safeParse((await r.json()) as unknown);
      if (!parsed.success) throw new Error("ablation payload failed validation");
      setData(parsed.data);
    } catch (e) {
      setData(null);
      setError(`Ablation unavailable (${String(e)})`);
    } finally {
      setRunning(false);
    }
  }

  return (
    <section
      aria-label="Retrieval ablation"
      className="rounded-[24px] border border-hairline bg-card p-6"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
        Ablation
      </p>
      <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
        Retrieval ablation — where groundedness comes from
      </h3>
      <p className="mt-1 text-xs text-muted">
        k=1 vs k=5 · keyword-NN vs virgin-NN · with/without thread-window context,
        on a fixed 60-item slice. Proves groundedness comes from retrieval.
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <LiveBadge
          status={running ? "RUNNING" : error ? "ERROR" : data ? "LIVE" : "AWAITING"}
          onRetry={run}
          retryLabel={data ? "↻ re-run" : "Run ablation"}
        />
        <CurlButton cmd={curl} />
      </div>

      {!data && !error && !running ? (
        <p className="mt-2 rounded-2xl border border-hairline-soft bg-paper p-3 text-sm text-muted">
          Not run yet — the endpoint may still be pending (workstream A). Hit “Run
          ablation”; a pending endpoint reports itself instead of fake numbers.
        </p>
      ) : null}
      {error ? <p className="mt-2 text-sm text-red-700 dark:text-red-300">{error}</p> : null}
      {running ? <p className="mt-2 font-mono text-xs text-muted">Running ablation…</p> : null}

      {data ? (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-xs">
            <thead>
              <tr className="border-b border-hairline text-muted">
                <th className="py-1.5 pr-3 font-medium">Arm</th>
                <th className="py-1.5 pr-3 font-medium">k</th>
                <th className="py-1.5 pr-3 font-medium">Groundedness mean</th>
                <th className="py-1.5 pr-3 font-medium">≥4 rate</th>
                <th className="py-1.5 pr-3 font-medium">p50 ms</th>
              </tr>
            </thead>
            <tbody>
              {data.arms.map((a, i) => (
                <tr key={i} className="border-b border-hairline last:border-b-0">
                  <td className="py-1.5 pr-3 font-mono font-semibold">{a.name ?? `arm ${i + 1}`}</td>
                  <td className="py-1.5 pr-3 font-mono tabular-nums">{a.k ?? "—"}</td>
                  <td className="py-1.5 pr-3 font-mono tabular-nums">{fmt(a.groundedness_mean)}</td>
                  <td className="py-1.5 pr-3 font-mono tabular-nums">{fmt(a.ge4_rate)}</td>
                  <td className="py-1.5 pr-3 font-mono tabular-nums">
                    {a.p50_ms !== undefined ? Math.round(a.p50_ms) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}

function fmt(v: number | undefined): string {
  return typeof v === "number" && Number.isFinite(v) ? v.toFixed(3) : "—";
}
