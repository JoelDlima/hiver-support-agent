"use client";

import { useEffect, useRef, useState } from "react";
import { useTheme } from "next-themes";
import { motion } from "framer-motion";
import { Activity, AlertTriangle, Gauge, XCircle } from "lucide-react";
import MetricsPanel from "../components/MetricsPanel";
import PipelineTimeline from "../components/PipelineTimeline";
import Inspector from "../components/proof/Inspector";
import RunAgainDiff from "../components/proof/RunAgainDiff";
import LogTail from "../components/proof/LogTail";
import CurlCopy from "../components/proof/CurlCopy";
import EvalRunner from "../components/proof/EvalRunner";
import EmbedScene from "../components/proof/EmbedScene";
import type { EmbedPoint, Passage, PredictResponse } from "../lib";

type Judge = { groundedness: number; verdict: string } | null;

type RunLogEntry = {
  t: number;
  brand: string;
  intent: string;
  decision: string;
  ms?: number;
};

/* ------------------------- SmartGrey hero helpers ------------------------- */

const STALE_AFTER_MS = 60_000;

const STAGE_PILL: Record<string, string> = {
  LIVE: "border-teal-500/40 bg-teal-500/10 text-teal-700 dark:text-teal-300",
  STALE: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  AWAITING: "border-hairline-soft bg-paper text-muted",
};

function stageStatus(hasResult: boolean, stale: boolean): "LIVE" | "STALE" | "AWAITING" {
  if (!hasResult) return "AWAITING";
  return stale ? "STALE" : "LIVE";
}

function formatMs(v: unknown): string {
  return typeof v === "number" && Number.isFinite(v) ? String(Math.round(v)) : "—";
}

function isEscalateDecision(decision: string | undefined): boolean {
  return /escalate/i.test(decision || "");
}

export default function Page() {
  const { theme, setTheme } = useTheme();
  const [brand, setBrand] = useState("virgin");
  const [text, setText] = useState("My train from Euston was delayed 45 minutes, how do I claim delay repay?");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState("");
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [resultAt, setResultAt] = useState<number | null>(null);
  const [runLog, setRunLog] = useState<RunLogEntry[]>([]);
  const [judge, setJudge] = useState<Judge>(null);
  const [passages, setPassages] = useState<Passage[]>([]);
  const [embed, setEmbed] = useState<EmbedPoint[] | null>(null);
  const [embedLoading, setEmbedLoading] = useState(false);
  const [inspectId, setInspectId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Ticking clock for the 60s stale-after rule (mirrors the SmartGrey gauge).
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  async function loadEmbed(currentBrand: string, query: string) {
    setEmbedLoading(true);
    try {
      const r = await fetch(
        `/api/embed2d?brand=${encodeURIComponent(currentBrand)}&q=${encodeURIComponent(query.slice(0, 200))}`
      );
      if (!r.ok) {
        setEmbed(null);
        return;
      }
      const j = await r.json();
      const points: EmbedPoint[] | null = Array.isArray(j)
        ? (j as EmbedPoint[])
        : ((j.points || j.data || null) as EmbedPoint[] | null);
      setEmbed(points);
    } catch {
      setEmbed(null);
    } finally {
      setEmbedLoading(false);
    }
  }

  function appendRunLog(j: PredictResponse) {
    setRunLog((log) =>
      [
        ...log.slice(-19),
        {
          t: Date.now(),
          brand: j.brand || brand,
          intent: j.intent,
          decision: j.decision,
          ms: j.latency_ms,
        },
      ] as RunLogEntry[]
    );
  }

  async function runPredict() {
    setLoading(true);
    setError(null);
    setStreaming("");
    setJudge(null);
    try {
      const r = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, brand }),
      });
      const j: PredictResponse = await r.json();
      setResult(j);
      setResultAt(Date.now());
      appendRunLog(j);
      setInspectId(j.request_id || null);
      await loadPassages(j);
      await loadJudge(j);
      await loadEmbed(j.brand || brand, text);
    } catch (e) {
      setError(`Predict failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  async function loadPassages(j: PredictResponse) {
    try {
      const r = await fetch(`/api/passages?brand=${j.brand}&q=${encodeURIComponent(text.slice(0, 200))}`);
      if (r.ok) setPassages(await r.json());
      else
        setPassages(
          (j.grounding_passage_ids || []).map((id, i) => ({ tweet_id: id, score: 1 - i * 0.05, text: "" }))
        );
    } catch {
      setPassages(
        (j.grounding_passage_ids || []).map((id, i) => ({ tweet_id: id, score: 1 - i * 0.05, text: "" }))
      );
    }
  }

  async function loadJudge(j: PredictResponse) {
    try {
      const r = await fetch("/api/judge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          intent: j.intent,
          draft_reply: j.draft_reply,
          passage_ids: j.grounding_passage_ids,
          inbound: text,
        }),
      });
      if (r.ok) setJudge(await r.json());
    } catch {
      /* judge is advisory */
    }
  }

  async function runStream() {
    setLoading(true);
    setError(null);
    setResult(null);
    setResultAt(null);
    setStreaming("");
    setJudge(null);
    setPassages([]);
    abortRef.current?.abort();
    const ctl = new AbortController();
    abortRef.current = ctl;
    try {
      const r = await fetch("/api/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, brand }),
        signal: ctl.signal,
      });
      const reader = r.body?.getReader();
      const dec = new TextDecoder();
      let buf = "";
      let final: PredictResponse | null = null;
      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const parts = buf.split("\n\n");
        buf = parts.pop() || "";
        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data:")) continue;
          const payload = line.slice(5).trim();
          if (payload === "[DONE]") continue;
          try {
            const ev = JSON.parse(payload);
            if (ev.event === "token") setStreaming((s) => s + (ev.text || ""));
            else if (ev.event === "stages") {
              setResult(
                (prev) =>
                  ({
                    ...(prev as PredictResponse),
                    intent: ev.intent,
                    intent_confidence: ev.intent_confidence,
                    signals: {
                      ...(prev?.signals || {}),
                      classify_ms: ev.classify_ms,
                      retrieve_ms: ev.retrieve_ms,
                      draft_ms: ev.draft_ms,
                    },
                  }) as PredictResponse
              );
              setResultAt(Date.now());
            } else if (ev.event === "final") {
              final = ev as PredictResponse;
              setResult(final);
              setResultAt(Date.now());
            }
          } catch {
            /* keep-alive */
          }
        }
      }
      if (final) {
        appendRunLog(final as PredictResponse);
        setInspectId((final as PredictResponse).request_id || null);
        await loadPassages(final as PredictResponse);
        await loadJudge(final as PredictResponse);
        await loadEmbed((final as PredictResponse).brand || brand, text);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") setError(`Stream failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  const sig = result?.signals || {};
  const stages = [
    {
      name: "Validate and normalize",
      ms: undefined,
      state: result ? ("done" as const) : ("idle" as const),
    },
    {
      name: "Classify intent",
      ms: sig.classify_ms as number | undefined,
      state: result ? ("done" as const) : ("idle" as const),
      note: result ? `${result.intent} at ${Number(result.intent_confidence || 0).toFixed(3)}` : undefined,
    },
    {
      name: "Retrieve top passages",
      ms: sig.retrieve_ms as number | undefined,
      state: result ? ("done" as const) : ("idle" as const),
      note: result ? `${(result.grounding_passage_ids || []).length} passages` : undefined,
    },
    {
      name: `Draft (${String(sig.draft_path || "template")})`,
      ms: sig.draft_ms as number | undefined,
      state: loading ? ("active" as const) : result ? ("done" as const) : ("idle" as const),
      note: String(
        (sig as Record<string, unknown>).groq_reason ||
          (sig.draft_path === "groq" ? "groq live" : "template")
      ),
    },
    {
      name: "Escalate decision",
      ms: result?.latency_ms,
      state: result ? ("done" as const) : ("idle" as const),
      note: result ? `${result.decision} (${result.escalate_reason})` : undefined,
    },
  ];

  const draftText = streaming || result?.draft_reply || "";

  /* ---- SmartGrey hero derivations (left column only) ---- */
  const stale = resultAt !== null && now - resultAt > STALE_AFTER_MS;
  const cardStatus = stageStatus(result !== null, stale);
  const conf = Number(result?.intent_confidence || 0);
  const confPct = Math.round(Math.min(Math.max(conf, 0), 1) * 100);
  const topK = (result?.grounding_passage_ids || []).length;
  const draftPath = String(sig.draft_path || "template");
  const groqReason = String(
    (sig as Record<string, unknown>).groq_reason ||
      (sig.draft_path === "groq" ? "groq live" : "template")
  );
  const escalated = isEscalateDecision(result?.decision);

  const gaugePill = !result
    ? { label: "AWAITING", cls: "border-hairline-soft bg-paper text-muted", Icon: Gauge }
    : stale
      ? { label: "STALE", cls: STAGE_PILL.STALE, Icon: AlertTriangle }
      : conf < 0.45
        ? { label: "LOW-CONF", cls: STAGE_PILL.STALE, Icon: AlertTriangle }
        : escalated
          ? { label: "ESCALATE", cls: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300", Icon: XCircle }
          : { label: "AUTO", cls: STAGE_PILL.LIVE, Icon: Activity };

  const stageCards = [
    {
      title: "Classify",
      value: formatMs(sig.classify_ms),
      unit: "ms",
      pin: result ? `${result.intent} @ ${conf.toFixed(3)}` : "no run yet",
      hint: "Escalate below 0.45",
      dot: !result ? null : conf >= 0.45 ? "bg-teal" : "bg-red-500",
    },
    {
      title: "Retrieve",
      value: formatMs(sig.retrieve_ms),
      unit: "ms",
      pin: result ? `top-k ${topK}` : "no run yet",
      hint: "Grounded passages",
      dot: null as string | null,
    },
    {
      title: "Draft",
      value: formatMs(sig.draft_ms),
      unit: "ms",
      pin: result ? draftPath : "no run yet",
      hint: result ? groqReason : "Template or groq live",
      dot: null as string | null,
    },
    {
      title: "Decide",
      value: formatMs(result?.latency_ms),
      unit: "ms",
      pin: result ? (result.decision || "—") : "no run yet",
      hint: result ? result.escalate_reason || "—" : "Auto vs escalate",
      dot: !result ? null : escalated ? "bg-red-500" : "bg-teal",
    },
  ];

  return (
    <div className="min-h-screen bg-canvas font-sans text-ink">
      <header className="border-b border-line">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <div>
            <h1 className="text-xl font-semibold">Hiver support triage</h1>
            <p className="text-sm text-muted">Control room for grounded replies and escalation</p>
          </div>
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="rounded-lg border border-line bg-surface px-3 py-1.5 text-sm font-medium"
          >
            {theme === "dark" ? "Switch to light" : "Switch to dark"}
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="min-w-0 space-y-5">
            {/* 1. compact hero line */}
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
                  Hiver live triage console
                </p>
                <h1 className="mt-1 font-display text-5xl font-bold tracking-[-0.03em] md:text-7xl">
                  Triage
                </h1>
              </div>
              <nav className="flex flex-wrap gap-2 text-sm font-medium" aria-label="Triage sections">
                <a
                  href="#triage"
                  className="rounded-full border border-hairline-soft px-4 py-1.5 hover:border-hairline-strong hover:opacity-75"
                >
                  #triage
                </a>
                <a
                  href="#proof"
                  className="rounded-full border border-hairline-soft px-4 py-1.5 hover:border-hairline-strong hover:opacity-75"
                >
                  #proof
                </a>
                <a
                  href="#eval"
                  className="rounded-full border border-hairline-soft px-4 py-1.5 hover:border-hairline-strong hover:opacity-75"
                >
                  #eval
                </a>
              </nav>
            </div>

            {/* 2. decision status banner */}
            <div
              role="status"
              className={`flex flex-wrap items-center justify-between gap-3 rounded-[24px] border p-4 md:p-5 ${
                !result
                  ? "border-hairline bg-card text-muted"
                  : escalated
                    ? "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300"
                    : "border-teal bg-teal/10 text-teal"
              }`}
            >
              <p className="text-sm font-semibold">
                {!result ? (
                  <>
                    ○ Sandbox open — paste any customer message, even nonsense, and hit Predict.
                    Nothing is gated.
                  </>
                ) : escalated ? (
                  <>
                    ● Needs a human — {result.decision} · {result.escalate_reason} · via{" "}
                    {draftPath}
                  </>
                ) : (
                  <>
                    ● Auto-handle — {result.decision} · {result.escalate_reason} · via{" "}
                    {draftPath}
                  </>
                )}
              </p>
              {result ? (
                <span className="font-mono text-xs tabular-nums opacity-80">
                  {result.latency_ms} ms · {result.request_id}
                </span>
              ) : null}
            </div>

            {/* 3. pipeline stage cards */}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {stageCards.map((c) => (
                <article key={c.title} className="rounded-[24px] border border-hairline bg-card p-6">
                  <div className="flex items-center justify-between gap-2">
                    <h2 className="font-display text-lg font-semibold tracking-[-0.03em]">
                      {c.title}
                    </h2>
                    <span
                      className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${STAGE_PILL[cardStatus]}`}
                    >
                      {cardStatus}
                    </span>
                  </div>
                  <p className="mt-3 flex items-baseline gap-2">
                    <span className="font-display text-4xl font-semibold tabular-nums tracking-tight">
                      {c.value}
                    </span>
                    <span className="text-sm text-muted">{c.unit}</span>
                  </p>
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center rounded-full bg-teal px-2.5 py-1 text-xs font-semibold text-white">
                      {c.pin}
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-xs text-muted">
                      {c.dot && (
                        <span
                          aria-hidden
                          className={`inline-block size-2 rounded-full ${c.dot}`}
                        />
                      )}
                      {c.hint}
                    </span>
                  </div>
                </article>
              ))}
            </div>

            {/* 4. confidence gauge card */}
            <section className="flex flex-col gap-4 rounded-[24px] border border-hairline bg-card p-6">
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs font-medium uppercase tracking-widest text-muted">
                  Intent confidence
                </p>
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold ${gaugePill.cls}`}
                >
                  <gaugePill.Icon className="h-3.5 w-3.5" />
                  {gaugePill.label}
                </span>
              </div>

              <div className="flex items-baseline gap-2">
                <motion.span
                  key={result ? `${resultAt}-${confPct}` : "empty"}
                  initial={{ opacity: 0.4 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.25 }}
                  className="font-display text-6xl font-bold tabular-nums tracking-tight"
                >
                  {result ? confPct : "—"}
                </motion.span>
                <span className="text-lg font-medium text-muted">%</span>
              </div>

              <dl className="grid grid-cols-3 gap-3 border-t border-hairline pt-4 text-sm">
                <div>
                  <dt className="text-xs text-muted">Intent</dt>
                  <dd className="truncate font-mono font-semibold tabular-nums">
                    {result?.intent || "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">Draft path</dt>
                  <dd className="truncate font-mono font-semibold tabular-nums">
                    {result ? draftPath : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-muted">Latency</dt>
                  <dd className="font-mono font-semibold tabular-nums">
                    {result ? `${result.latency_ms} ms` : "—"}
                  </dd>
                </div>
              </dl>

              {stale && result && (
                <p className="rounded-md border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-700 dark:text-amber-300">
                  Stale — last run was over 60s ago. Hit Predict again for a fresh read.
                </p>
              )}
              {!result && (
                <p className="text-xs text-muted">
                  Waiting for the first run — type anything in the composer below and hit
                  Predict.
                </p>
              )}
            </section>

            {/* 5. composer (handlers identical, SmartGrey skin only) */}
            <section id="triage" className="rounded-[24px] border border-hairline bg-card p-6">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm text-muted">Brand</span>
                <div className="flex rounded-full border border-hairline-soft bg-paper p-1">
                  <button
                    onClick={() => setBrand("virgin")}
                    className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                      brand === "virgin"
                        ? "bg-teal font-semibold text-[#03211f]"
                        : "text-muted hover:opacity-75"
                    }`}
                  >
                    VirginTrains
                  </button>
                  <button
                    onClick={() => setBrand("apple")}
                    className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                      brand === "apple"
                        ? "bg-teal font-semibold text-[#03211f]"
                        : "text-muted hover:opacity-75"
                    }`}
                  >
                    AppleSupport
                  </button>
                </div>
                <span className="text-xs text-muted">Primary is VirginTrains, Apple kept for evidence</span>
              </div>

              <div className="mt-4">
                <label htmlFor="composer" className="text-sm font-medium">
                  Customer message
                </label>
                <textarea
                  id="composer"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={3}
                  maxLength={2000}
                  className="mt-1 w-full rounded-2xl border border-hairline-soft bg-paper p-3 text-sm placeholder:text-muted"
                  placeholder="Type a customer message"
                />
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <button
                    onClick={runPredict}
                    disabled={loading}
                    className="rounded-full bg-teal px-5 py-2 text-sm font-semibold text-[#03211f] transition-opacity hover:opacity-85 disabled:opacity-50"
                  >
                    {loading ? "Running" : "Predict"}
                  </button>
                  <button
                    onClick={runStream}
                    disabled={loading}
                    className="rounded-full border border-hairline-soft px-5 py-2 text-sm font-semibold transition-opacity hover:opacity-75 disabled:opacity-50"
                  >
                    Stream draft
                  </button>
                  {error ? (
                    <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
                  ) : null}
                </div>
              </div>

              <div className="mt-5 border-t border-hairline pt-4">
                <h2 className="font-display text-xl font-semibold tracking-[-0.03em]">Draft reply</h2>
                <p className="mt-1 min-h-16 whitespace-pre-wrap text-[15px] leading-relaxed">
                  {draftText || <span className="text-muted">Run a prediction to see the draft.</span>}
                </p>
                {result ? (
                  <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
                    <span>
                      Request <span className="font-mono">{result.request_id}</span>
                    </span>
                    <span>
                      Latency <span className="font-mono tabular-nums">{result.latency_ms} ms</span>
                    </span>
                    <span>
                      Draft path <span className="font-mono">{draftPath}</span>
                    </span>
                    <span>
                      Confidence <span className="font-mono tabular-nums">{confPct}%</span>
                    </span>
                  </div>
                ) : null}
              </div>
            </section>

            {/* 6. run log */}
            <section className="rounded-[24px] border border-hairline bg-card p-6">
              <h2 className="font-display text-xl font-semibold tracking-[-0.03em]">Run log</h2>
              {runLog.length === 0 ? (
                <p className="mt-2 text-sm text-muted">
                  No runs yet — the sandbox is open, run anything.
                </p>
              ) : (
                <ul className="mt-3 space-y-2 text-sm">
                  {[...runLog].reverse().map((e, i) => (
                    <li
                      key={`${e.t}-${i}`}
                      className="flex items-baseline justify-between gap-3 border-t border-hairline pt-2"
                    >
                      <span>
                        {e.brand} · {e.intent} · {e.decision}
                      </span>
                      <span className="shrink-0 font-mono text-xs tabular-nums text-muted">
                        {new Date(e.t).toLocaleTimeString()} · {e.ms ?? "—"} ms
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="rounded-xl border border-line bg-surface p-4 shadow-sm">
              <h2 className="text-sm font-medium">Embedding map</h2>
              <p className="mb-2 text-xs text-muted">Two dimensional projection of retrieved passages</p>
              <EmbedScene embed={embed} loading={embedLoading} />
              {passages.length > 0 ? (
                <ol className="mt-2 space-y-1 text-xs">
                  {passages.map((p) => (
                    <li
                      key={p.tweet_id}
                      className="flex justify-between gap-2 rounded-lg border border-line px-2 py-1"
                    >
                      <span className="truncate font-mono">{p.tweet_id}</span>
                      <span className="font-mono tabular-nums text-muted">{p.score.toFixed(3)}</span>
                    </li>
                  ))}
                </ol>
              ) : null}
            </section>

            <div id="proof" className="space-y-5">
              <RunAgainDiff text={text} brand={brand} firstDraft={result?.draft_reply || ""} />
              <Inspector inspectId={inspectId} />
            </div>
          </div>

          <aside className="space-y-3 self-start lg:sticky lg:top-4">
            <div className="rail-panel rounded-md p-2">
              <h2 className="px-1 pb-1 text-sm font-medium">Pipeline</h2>
              <PipelineTimeline stages={stages} />
            </div>

            <div className="rail-panel rounded-md p-2">
              <h2 className="px-1 pb-1 text-sm font-medium">Judge</h2>
              {judge ? (
                <p className="px-1 text-sm">
                  Groundedness <span className="font-mono tabular-nums">{judge.groundedness}/5</span>,
                  verdict <span className="font-medium">{judge.verdict}</span>
                </p>
              ) : (
                <p className="px-1 text-sm text-muted">Runs on each prediction, advisory only.</p>
              )}
            </div>

            <div className="rail-panel rounded-md p-2">
              <h2 className="px-1 pb-1 text-sm font-medium">Service metrics</h2>
              <MetricsPanel />
            </div>

            <LogTail />
            <CurlCopy text={text} brand={brand} />
            <EvalRunner brand={brand} />
          </aside>
        </div>
      </main>

      <footer className="border-t border-line">
        <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted">
          Browser calls the local API routes, which proxy FastAPI. Groq key stays server side.
        </p>
      </footer>
    </div>
  );
}
