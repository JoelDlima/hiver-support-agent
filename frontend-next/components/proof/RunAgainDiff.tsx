"use client";

import { useState } from "react";

type Tok = { w: string; op: "same" | "del" | "ins" };

function wordDiff(a: string, b: string): Tok[] {
  const aw = a.split(/\s+/).filter(Boolean);
  const bw = b.split(/\s+/).filter(Boolean);
  const n = aw.length;
  const m = bw.length;
  if (n === 0 || m === 0) {
    return [
      ...aw.map((w) => ({ w, op: "del" as const })),
      ...bw.map((w) => ({ w, op: "ins" as const })),
    ];
  }
  const W = m + 1;
  const dp = new Uint32Array((n + 1) * W);
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i * W + j] =
        aw[i] === bw[j]
          ? dp[(i + 1) * W + j + 1] + 1
          : Math.max(dp[(i + 1) * W + j], dp[i * W + j + 1]);
    }
  }
  const out: Tok[] = [];
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (aw[i] === bw[j]) {
      out.push({ w: aw[i], op: "same" });
      i++;
      j++;
    } else if (dp[(i + 1) * W + j] >= dp[i * W + j + 1]) {
      out.push({ w: aw[i], op: "del" });
      i++;
    } else {
      out.push({ w: bw[j], op: "ins" });
      j++;
    }
  }
  while (i < n) out.push({ w: aw[i++], op: "del" });
  while (j < m) out.push({ w: bw[j++], op: "ins" });
  return out;
}

export default function RunAgainDiff({
  text,
  brand,
  firstDraft,
}: {
  text: string;
  brand: string;
  firstDraft: string;
}) {
  const [second, setSecond] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runAgain() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, brand }),
      });
      if (!r.ok) throw new Error(`predict returned status ${r.status}`);
      const j = await r.json();
      setSecond(String(j.draft_reply || ""));
    } catch (e) {
      setError(`Re-run failed (${String(e)})`);
    } finally {
      setLoading(false);
    }
  }

  const toks = second !== null ? wordDiff(firstDraft || "", second) : null;
  const same = toks ? toks.filter((t) => t.op === "same").length : 0;
  const denom = toks
    ? Math.max(
        firstDraft.split(/\s+/).filter(Boolean).length,
        second !== null ? second.split(/\s+/).filter(Boolean).length : 0,
        1
      )
    : 1;
  const pct = toks ? Math.round((same / denom) * 100) : null;

  return (
    <div className="rounded-2xl border border-hairline-soft bg-paper px-4 py-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Consistency
          </p>
          <h3 className="mt-0.5 font-display text-lg font-semibold tracking-[-0.03em] text-ink">
            Run again
          </h3>
        </div>
        {pct !== null ? (
          <span className="font-display text-xl font-semibold tabular-nums text-ink">
            {pct}
            <span className="ml-1 text-sm font-medium text-muted">% identical</span>
          </span>
        ) : null}
      </div>
      <div className="mt-2">
        {/* Local secondary button (sg Button omits children in its props, so a
            local fallback keeps the same SmartGrey pill styling). */}
        <button
          type="button"
          onClick={runAgain}
          disabled={loading || !text}
          className="inline-flex h-8 items-center justify-center rounded-full border border-hairline bg-card px-4 text-sm font-medium text-ink hover:border-hairline-strong hover:bg-paper disabled:opacity-50"
        >
          {loading ? "Running…" : "Run again"}
        </button>
      </div>
      {error ? (
        <p className="mt-2 text-sm text-red-700 dark:text-red-300">{error}</p>
      ) : null}
      {toks ? (
        <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-ink">
          {toks.map((t, k) =>
            t.op === "same" ? (
              <span key={k}>{t.w} </span>
            ) : t.op === "del" ? (
              <span
                key={k}
                className="rounded bg-red-500/10 px-0.5 text-red-700 line-through dark:text-red-300"
              >
                {t.w}{" "}
              </span>
            ) : (
              // Teal tint mirrors --color-teal (#0d5c5c); the arbitrary hex keeps
              // the alpha working under Tailwind v3 CSS-variable colors.
              <span key={k} className="rounded bg-[#0d5c5c]/15 px-0.5 text-ink">
                {t.w}{" "}
              </span>
            )
          )}
        </p>
      ) : (
        <p className="mt-2 text-sm text-muted">
          Re-posts the same text and brand, then diffs the new draft against the first.
        </p>
      )}
    </div>
  );
}
