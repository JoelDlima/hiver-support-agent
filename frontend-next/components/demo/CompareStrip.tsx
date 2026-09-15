"use client";

// B4 — Brand compare strip. Renders GET /api/eval/compare
// (proxied to workstream A's GET /eval/compare?brands=virgin,apple) when live.
// Until then: explicit pending state, never fake numbers. A static,
// clearly-labeled table of the published doc baselines sits alongside so the
// strip is useful before the endpoint lands — doc values, not live claims.
// Apple is labeled "transfer evidence".

import { useEffect, useState } from "react";
import { CompareSchema } from "../proof/schemas";
import { CurlButton, LiveBadge } from "./widgets";

type Row = {
  brand: string;
  tag: string;
  intent_acc: string;
  macro_f1: string;
  esc_f1: string;
  ground_mean: string;
  n: string;
  source: string;
};

// Published baselines, transcribed from docs (static — not live results).
const DOC_ROWS: Row[] = [
  {
    brand: "virgin",
    tag: "Primary corpus",
    intent_acc: "0.795",
    macro_f1: "0.803",
    esc_f1: "0.767",
    ground_mean: "4.21",
    n: "200",
    source: "evaluation/virgin/BASELINE_VS_FINAL.md §B final (human-200)",
  },
  {
    brand: "apple",
    tag: "Transfer evidence",
    intent_acc: "0.433",
    macro_f1: "0.443",
    esc_f1: "0.471",
    ground_mean: "4.75",
    n: "60",
    source: "evaluation/BASELINE_VS_FINAL.md §B final (human-60; single annotator, wide CIs)",
  },
];

function StaticTable({ rows, caption }: { rows: Row[]; caption: string }) {
  return (
    <div>
      <p className="text-xs text-muted">{caption}</p>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[560px] text-left text-xs">
          <thead>
            <tr className="border-b border-hairline text-muted">
              <th className="py-1.5 pr-3 font-medium">Brand</th>
              <th className="py-1.5 pr-3 font-medium">Intent acc</th>
              <th className="py-1.5 pr-3 font-medium">Macro F1</th>
              <th className="py-1.5 pr-3 font-medium">Esc F1</th>
              <th className="py-1.5 pr-3 font-medium">Ground mean</th>
              <th className="py-1.5 pr-3 font-medium">n</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.brand} className="border-b border-hairline last:border-b-0">
                <td className="py-1.5 pr-3">
                  <span className="font-mono font-semibold">{r.brand}</span>{" "}
                  <span className="text-muted">· {r.tag}</span>
                  <span className="block text-[11px] text-muted">{r.source}</span>
                </td>
                <td className="py-1.5 pr-3 font-mono tabular-nums">{r.intent_acc}</td>
                <td className="py-1.5 pr-3 font-mono tabular-nums">{r.macro_f1}</td>
                <td className="py-1.5 pr-3 font-mono tabular-nums">{r.esc_f1}</td>
                <td className="py-1.5 pr-3 font-mono tabular-nums">{r.ground_mean}</td>
                <td className="py-1.5 pr-3 font-mono tabular-nums">{r.n}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function CompareStrip() {
  const [live, setLive] = useState<Row[] | null>(null);
  const [pending, setPending] = useState(true);
  const [detail, setDetail] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  const curl = "curl http://127.0.0.1:8000/eval/compare?brands=virgin,apple";

  useEffect(() => {
    let cancelled = false;
    fetch("/api/eval/compare?brands=virgin,apple")
      .then(async (r) => {
        if (!r.ok) {
          if (!cancelled) {
            setPending(true);
            setDetail(
              `GET /eval/compare returned ${r.status} — endpoint pending (workstream A).`
            );
          }
          return;
        }
        const parsed = CompareSchema.safeParse((await r.json()) as unknown);
        if (!parsed.success) throw new Error("compare payload failed validation");
        if (!cancelled) {
          const rows: Row[] = Object.entries(parsed.data.results).map(([brand, v]) => ({
            brand,
            tag: brand === "apple" ? "Transfer evidence" : "Primary corpus",
            intent_acc: fmt(v.intent_acc),
            macro_f1: fmt(v.macro_f1),
            esc_f1: fmt(v.esc_f1),
            ground_mean: fmt(v.ground_mean),
            n: v.n !== undefined ? String(v.n) : "—",
            source: "live · GET /eval/compare",
          }));
          setLive(rows);
          setPending(false);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setPending(true);
          setDetail(`Compare endpoint unreachable (${String(e)}).`);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [nonce]);

  return (
    <section
      aria-label="Brand compare"
      className="rounded-[24px] border border-hairline bg-card p-6"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
        Transfer
      </p>
      <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
        Virgin vs Apple — compare strip
      </h3>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <LiveBadge
          status={live && !pending ? "LIVE" : "STALE"}
          onRetry={() => setNonce((v) => v + 1)}
          retryLabel="↻ re-check endpoint"
        />
        <CurlButton cmd={curl} />
      </div>

      {pending ? (
        <p className="mt-2 rounded-2xl border border-hairline-soft bg-paper p-3 text-sm text-muted">
          Live endpoint pending — {detail} The table below is the static published
          baseline from docs (not live results).
        </p>
      ) : null}

      {live && !pending ? (
        <div className="mt-3">
          <StaticTable rows={live} caption="Live · GET /eval/compare (must equal doc tables within rounding)." />
        </div>
      ) : (
        <div className="mt-3">
          <StaticTable rows={DOC_ROWS} caption="Published baselines (static, from docs — not live results)." />
        </div>
      )}
    </section>
  );
}

function fmt(v: number | undefined): string {
  return typeof v === "number" && Number.isFinite(v) ? v.toFixed(3) : "—";
}
