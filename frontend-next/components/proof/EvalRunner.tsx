"use client";

import { useState } from "react";
import { Card } from "../sg/card";

type Row = {
  key: string;
  label: string;
  pass: boolean;
  at: string;
};

type Summary = {
  intentAcc?: number;
  escAcc?: number;
  passed?: number;
  total?: number;
};

function timestamp() {
  return new Date().toLocaleTimeString();
}

export default function EvalRunner({ brand }: { brand: string }) {
  const [n, setN] = useState(20);
  const [seed, setSeed] = useState(11);
  const [rows, setRows] = useState<Row[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setError(null);
    setRows([]);
    setSummary(null);
    try {
      const r = await fetch("/api/eval/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ n, seed, brand }),
      });
      if (!r.ok || !r.body) throw new Error(`eval returned status ${r.status}`);
      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      let fallback = 0;
      for (;;) {
        const { done: dr, value } = await reader.read();
        if (dr) break;
        buf += dec.decode(value, { stream: true });
        const parts = buf.split("\n\n");
        buf = parts.pop() || "";
        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          const payload = line.slice(5).trim();
          if (payload === "[DONE]") continue;
          let ev: Record<string, unknown>;
          try {
            ev = JSON.parse(payload) as Record<string, unknown>;
          } catch {
            continue;
          }
          if (ev.event === "done") {
            if (typeof ev.intent_acc === "number" || typeof ev.esc_acc === "number") {
              setSummary({
                intentAcc: typeof ev.intent_acc === "number" ? ev.intent_acc : undefined,
                escAcc: typeof ev.esc_acc === "number" ? ev.esc_acc : undefined,
              });
            } else if (typeof ev.total === "number") {
              const total = ev.total as number;
              const passed = typeof ev.passed === "number" ? (ev.passed as number) : 0;
              setSummary({
                passed,
                total,
                intentAcc: total > 0 ? passed / total : undefined,
              });
            } else {
              setSummary({});
            }
          } else if (typeof ev.i === "number") {
            const pass =
              ev.esc_ok !== undefined ? Boolean(ev.esc_ok) && Boolean(ev.ok) : Boolean(ev.ok);
            const label =
              ev.pred_intent !== undefined
                ? `${String(ev.pred_intent)} (expected ${String(ev.human_intent ?? "?")})`
                : String(ev.text ?? "").slice(0, 80);
            const key = String(ev.i);
            setRows((prev) => [...prev, { key, label, pass, at: timestamp() }]);
          } else if (ev.event === "item") {
            const key = String(ev.id ?? fallback++);
            const label = String(
              (ev.intent as string | undefined) ?? (ev.note as string | undefined) ?? (ev.text as string | undefined) ?? key
            ).slice(0, 80);
            setRows((prev) => [
              ...prev,
              { key, label, pass: ev.ok !== undefined ? Boolean(ev.ok) : true, at: timestamp() },
            ]);
          }
        }
      }
    } catch (e) {
      setError(`Eval failed (${String(e)})`);
    } finally {
      setRunning(false);
    }
  }

  const gate: "pass" | "block" | "unknown" = !summary
    ? "unknown"
    : rows.some((r) => !r.pass)
      ? "block"
      : "pass";

  const pill =
    gate === "pass"
      ? // Teal tint mirrors --color-teal (#0d5c5c); the arbitrary hex keeps the
        // alpha working under Tailwind v3 CSS-variable colors.
        "border-teal bg-[#0d5c5c]/10 text-teal"
      : gate === "block"
        ? "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300"
        : "border-hairline-soft bg-paper text-muted";

  return (
    <Card className="rounded-[24px] p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Checks
          </p>
          <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
            Eval
          </h3>
        </div>
        <span
          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${pill}`}
        >
          {gate === "pass" ? "PASS" : gate === "block" ? "BLOCK" : "UNKNOWN"}
        </span>
      </div>

      <ol className="mt-4 grid grid-cols-3 gap-2">
        <li className="rounded-2xl border border-hairline-soft bg-paper px-3 py-2">
          <span className="mr-2 text-xs text-muted">01</span>
          <label htmlFor="eval-n" className="text-xs text-muted">
            Sample
          </label>
          <input
            id="eval-n"
            type="number"
            value={n}
            min={1}
            max={500}
            onChange={(e) => setN(Number(e.target.value))}
            className="mt-1 w-full rounded-xl border border-hairline-soft bg-card px-2 py-1 font-mono text-xs text-ink outline-none focus:border-teal"
          />
        </li>
        <li className="rounded-2xl border border-hairline-soft bg-paper px-3 py-2">
          <span className="mr-2 text-xs text-muted">02</span>
          <label htmlFor="eval-seed" className="text-xs text-muted">
            Seed
          </label>
          <input
            id="eval-seed"
            type="number"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value))}
            className="mt-1 w-full rounded-xl border border-hairline-soft bg-card px-2 py-1 font-mono text-xs text-ink outline-none focus:border-teal"
          />
        </li>
        <li className="rounded-2xl border border-hairline-soft bg-paper px-3 py-2">
          <span className="mr-2 text-xs text-muted">03</span>
          <span className="text-xs text-muted">Run</span>
          <div className="mt-1">
            {/* Local primary button (sg Button omits children in its props, so a
                local fallback keeps the teal SmartGrey styling). */}
            <button
              type="button"
              onClick={run}
              disabled={running}
              className="inline-flex h-8 w-full items-center justify-center rounded-full bg-teal px-2 text-xs font-semibold text-white hover:opacity-85 disabled:opacity-50"
            >
              {running ? "Running…" : "Run eval"}
            </button>
          </div>
        </li>
      </ol>

      {error ? (
        <p className="mt-2 text-sm text-red-700 dark:text-red-300">{error}</p>
      ) : null}

      <div className="mt-3 max-h-48 overflow-y-auto">
        {rows.length === 0 ? (
          <p className="text-xs text-muted">
            {running ? "Streaming results…" : "No runs yet."}
          </p>
        ) : (
          <ul>
            {rows.map((row) => (
              <li
                key={row.key}
                className="flex items-baseline justify-between gap-3 border-t border-hairline py-1.5 first:border-t-0"
              >
                <span className="min-w-0 flex-1 truncate text-sm" title={row.label}>
                  {row.label}
                </span>
                <span className="flex shrink-0 items-center gap-2">
                  <time className="font-mono text-xs tabular-nums text-muted">
                    {row.at}
                  </time>
                  <span
                    aria-label={row.pass ? "pass" : "fail"}
                    className={`inline-block size-2 rounded-full ${row.pass ? "bg-teal" : "bg-red-500"}`}
                  />
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {summary ? (
        <div className="mt-3 border-t border-hairline pt-3">
          {summary.intentAcc !== undefined ? (
            <div className="flex items-baseline justify-between gap-3 py-0.5">
              <span className="text-xs text-muted">Intent accuracy</span>
              <span className="font-display text-lg font-semibold tabular-nums">
                {summary.intentAcc.toFixed(3)}
              </span>
            </div>
          ) : null}
          {summary.escAcc !== undefined ? (
            <div className="flex items-baseline justify-between gap-3 py-0.5">
              <span className="text-xs text-muted">Escalation accuracy</span>
              <span className="font-display text-lg font-semibold tabular-nums">
                {summary.escAcc.toFixed(3)}
              </span>
            </div>
          ) : null}
          {summary.passed !== undefined && summary.total !== undefined ? (
            <div className="flex items-baseline justify-between gap-3 py-0.5">
              <span className="text-xs text-muted">Passed</span>
              <span className="font-display text-lg font-semibold tabular-nums">
                {summary.passed}/{summary.total}
              </span>
            </div>
          ) : null}
        </div>
      ) : null}
    </Card>
  );
}
