"use client";

// B5 — Liveness/latency pill + local-inference strip. Polls the existing
// GET /api/metrics (proxied to FastAPI /metrics): reachable → green LIVE pill
// with session-average latency; unreachable → RED pill, never fake-green.
// Reuses STAGE_PILL / STALE_AFTER_MS styling from the hero.
// NOTE: /metrics exposes avg_latency_ms (session mean), not p50 — the pill
// labels it honestly as avg. A dedicated p50 needs a backend histogram.

import { useEffect, useState } from "react";
import { STAGE_PILL } from "./stageUI";

type Metrics = {
  predict_count?: number;
  avg_latency_ms?: number;
};

export function useBackendLiveness(pollMs = 10_000): {
  apiOk: boolean | null;
  avgMs: number | null;
  nonce: number;
  recheck: () => void;
} {
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [avgMs, setAvgMs] = useState<number | null>(null);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const r = await fetch("/api/metrics");
        if (!r.ok) throw new Error(`status ${r.status}`);
        const j = (await r.json()) as Metrics;
        if (!alive) return;
        setApiOk(true);
        setAvgMs(typeof j.avg_latency_ms === "number" ? j.avg_latency_ms : null);
      } catch {
        if (!alive) return;
        setApiOk(false);
        setAvgMs(null);
      }
    };
    tick();
    const id = window.setInterval(tick, pollMs);
    return () => {
      alive = false;
      window.clearInterval(id);
    };
  }, [pollMs, nonce]);

  return { apiOk, avgMs, nonce, recheck: () => setNonce((v) => v + 1) };
}

export default function LivenessPill({
  apiOk,
  avgMs,
  onRecheck,
}: {
  apiOk: boolean | null;
  avgMs: number | null;
  onRecheck?: () => void;
}) {
  if (apiOk === true) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold ${STAGE_PILL.LIVE}`}
      >
        ● backend live
        {avgMs !== null && Number.isFinite(avgMs) ? (
          <span className="font-mono tabular-nums">· avg {Math.round(avgMs)} ms (session)</span>
        ) : null}
        {onRecheck ? (
          <button type="button" onClick={onRecheck} className="underline hover:opacity-75">
            re-check
          </button>
        ) : null}
      </span>
    );
  }
  if (apiOk === false) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/40 bg-red-500/10 px-2.5 py-1 text-[11px] font-semibold text-red-700 dark:text-red-300">
        ● backend down — start FastAPI on :8000
        {onRecheck ? (
          <button type="button" onClick={onRecheck} className="underline hover:opacity-75">
            re-check
          </button>
        ) : null}
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold ${STAGE_PILL.AWAITING}`}
    >
      ○ checking backend…
    </span>
  );
}

export function LocalInferenceStrip() {
  return (
    <div className="rounded-[24px] border border-hairline bg-card p-4 text-center">
      <p className="text-sm font-semibold">100% local inference</p>
      <p className="mx-auto mt-1 max-w-2xl text-xs leading-relaxed text-muted">
        Intent classifier (TF-IDF LogReg) + retrieval (virgin NN over the local
        passage index) run on this machine — no per-query cloud calls for triage.
        Draft path is shown per run: Groq live when a key is present, template
        fallback otherwise (OFFLINE banner when the response echoes offline=true).
      </p>
    </div>
  );
}
