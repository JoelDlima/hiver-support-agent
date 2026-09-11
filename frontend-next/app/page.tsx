"use client";

import { useEffect, useRef, useState } from "react";
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
  RUNNING:
    "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse",
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
  const [tab, setTab] = useState<"triage" | "proof" | "eval">("triage");
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
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Ticking clock for the 60s stale-after rule (mirrors the SmartGrey gauge).
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  // LIVE indicator: poll GET /api/metrics on mount + every 10s into apiOk state.
  useEffect(() => {
    let alive = true;
    const tick = async () => {
      try {
        const r = await fetch("/api/metrics");
        if (!r.ok) throw new Error(`status ${r.status}`);
        await r.json();
        if (alive) setApiOk(true);
      } catch {
        if (alive) setApiOk(false);
      }
    };
    tick();
    const id = window.setInterval(tick, 10_000);
    return () => {
      alive = false;
      window.clearInterval(id);
    };
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
  const displayPill = loading ? "RUNNING" : cardStatus;
  const conf = Number(result?.intent_confidence || 0);
  const confPct = Math.round(Math.min(Math.max(conf, 0), 1) * 100);
  const topK = (result?.grounding_passage_ids || []).length;
  const draftPath = String(sig.draft_path || "template");
  const groqReason = String(
    (sig as Record<string, unknown>).groq_reason ||
      (sig.draft_path === "groq" ? "groq live" : "template")
  );
  const groqChip = String((sig as Record<string, unknown>).groq_reason || "template default");
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
      pin: result ? `${result.intent} @ ${conf.toFixed(3)}` : "—",
      hint: "Escalate below 0.45",
      dot: !result ? null : conf >= 0.45 ? "bg-teal" : "bg-red-500",
    },
    {
      title: "Retrieve",
      value: formatMs(sig.retrieve_ms),
      unit: "ms",
      pin: result ? `top-k ${topK}` : "—",
      hint: "Grounded passages",
      dot: null as string | null,
    },
    {
      title: "Draft",
      value: formatMs(sig.draft_ms),
      unit: "ms",
      pin: result ? draftPath : "—",
      hint: result ? groqReason : "Template or groq live",
      dot: null as string | null,
    },
    {
      title: "Decide",
      value: formatMs(result?.latency_ms),
      unit: "ms",
      pin: result ? (result.decision || "—") : "—",
      hint: result ? result.escalate_reason || "—" : "Auto vs escalate",
      dot: !result ? null : escalated ? "bg-red-500" : "bg-teal",
    },
  ];

  const emptyCard = (
    <div className="rounded-[24px] border border-hairline bg-card p-6">
      <p className="text-sm text-muted">No analysis yet — enter a customer message and run the pipeline.</p>
    </div>
  );

  const decisionBanner = (
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
            ● Needs a human — {result.decision} · {result.escalate_reason} · via {draftPath}
          </>
        ) : (
          <>
            ● Auto-handle — {result.decision} · {result.escalate_reason} · via {draftPath}
          </>
        )}
      </p>
      {result ? (
        <span className="font-mono text-xs tabular-nums opacity-80">
          {result.latency_ms} ms · {result.request_id}
        </span>
      ) : null}
    </div>
  );

  const liveIndicator = loading ? (
    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-700 dark:text-amber-300 animate-pulse">
      ◉ Executing
    </span>
  ) : apiOk ? (
    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal">
      ● API connected · local 127.0.0.1:8000
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 text-xs text-muted">
      ○ API offline — start FastAPI on :8000
    </span>
  );

  const tabs: Array<{ id: "triage" | "proof" | "eval"; label: string }> = [
    { id: "triage", label: "Triage" },
    { id: "proof", label: "Proof" },
    { id: "eval", label: "Eval" },
  ];

  return (
    <div className="min-h-screen bg-canvas font-sans text-ink">
      <main className="mx-auto max-w-6xl px-4 py-6">
        {/* 1. Title block */}
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Hiver Support Intelligence
          </p>
          <h1 className="mt-1 font-display text-4xl font-bold tracking-[-0.03em]">Live Triage</h1>
          <p className="mt-1 text-sm text-muted">
            Test a customer request and inspect exactly how the agent reached its decision.
          </p>
        </div>

        {/* 2. Tabs */}
        <div className="mt-4 inline-flex rounded-full border border-hairline-soft bg-paper p-1">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              aria-pressed={tab === t.id}
              className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                tab === t.id ? "bg-teal font-semibold text-[#03211f]" : "text-muted hover:opacity-75"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "triage" ? (
          <div className="mt-5 space-y-5">
            {/* 3. TRIAGE hero FIRST */}
            <section className="rounded-[24px] border border-hairline bg-card p-6">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex rounded-full border border-hairline-soft bg-paper p-1">
                  <button
                    onClick={() => setBrand("virgin")}
                    className={`flex flex-col items-start rounded-full px-4 py-1.5 text-left ${
                      brand === "virgin"
                        ? "bg-teal font-semibold text-[#03211f]"
                        : "text-muted hover:opacity-75"
                    }`}
                  >
                    <span className="text-sm font-medium">Virgin Trains</span>
                    <span className="text-[11px] opacity-70">Primary corpus</span>
                  </button>
                  <button
                    onClick={() => setBrand("apple")}
                    className={`flex flex-col items-start rounded-full px-4 py-1.5 text-left ${
                      brand === "apple"
                        ? "bg-teal font-semibold text-[#03211f]"
                        : "text-muted hover:opacity-75"
                    }`}
                  >
                    <span className="text-sm font-medium">Apple Support</span>
                    <span className="text-[11px] opacity-70">Secondary brand</span>
                  </button>
                </div>
                {liveIndicator}
              </div>

              <div className="mt-4">
                <label htmlFor="composer" className="text-sm font-medium">
                  Customer message
                </label>
                <textarea
                  id="composer"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={5}
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
                    {loading ? "Running…" : "Run live analysis"}
                  </button>
                  <button
                    onClick={runStream}
                    disabled={loading}
                    className="rounded-full border border-hairline-soft px-5 py-2 text-sm font-semibold transition-opacity hover:opacity-75 disabled:opacity-50"
                  >
                    Stream execution
                  </button>
                  {error ? (
                    <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
                  ) : null}
                </div>
                <p className="mt-3 text-xs text-muted">
                  Sandbox open · Try any customer message, including unseen queries. No demo
                  fixtures required.
                </p>
              </div>
            </section>

            {/* 4. Below hero */}
            {!result && !loading ? (
              emptyCard
            ) : (
              <>
                {decisionBanner}

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {stageCards.map((c) => (
                    <article
                      key={c.title}
                      className="rounded-[24px] border border-hairline bg-card p-6"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <h2 className="font-display text-lg font-semibold tracking-[-0.03em]">
                          {c.title}
                        </h2>
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${STAGE_PILL[displayPill]}`}
                        >
                          {displayPill}
                        </span>
                      </div>
                      <p className="mt-3 flex items-baseline gap-2">
                        <span className="font-display text-4xl font-semibold tabular-nums tracking-tight">
                          {loading ? "…" : !result ? "—" : c.value}
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
                  {!result && <p className="text-xs text-muted">Awaiting first run.</p>}
                </section>

                <section className="rounded-[24px] border border-hairline bg-card p-6">
                  <h2 className="font-display text-xl font-semibold tracking-[-0.03em]">
                    Draft reply
                  </h2>
                  <p className="mt-1 min-h-16 whitespace-pre-wrap text-[15px] leading-relaxed">
                    {draftText || (
                      <span className="text-muted">Run a prediction to see the draft.</span>
                    )}
                  </p>
                  {result ? (
                    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted">
                      <span>
                        Request <span className="font-mono">{result.request_id}</span>
                      </span>
                      <span>
                        Latency{" "}
                        <span className="font-mono tabular-nums">{result.latency_ms} ms</span>
                      </span>
                      <span>
                        Draft path <span className="font-mono">{draftPath}</span>
                      </span>
                      <span>
                        Confidence <span className="font-mono tabular-nums">{confPct}%</span>
                      </span>
                    </div>
                  ) : null}
                </section>

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
              </>
            )}
          </div>
        ) : null}

        {tab === "proof" ? (
          <div className="mt-5 space-y-5">
            {!result ? (
              emptyCard
            ) : (
              <>
                <div className="flex flex-wrap items-center justify-between gap-3 rounded-[24px] border border-hairline bg-card p-6">
                  <span className="font-mono text-xs tabular-nums">{result.request_id}</span>
                  <button
                    type="button"
                    onClick={runPredict}
                    disabled={loading}
                    className="inline-flex h-8 items-center justify-center rounded-full border border-hairline bg-card px-4 text-sm font-medium text-ink hover:border-hairline-strong hover:bg-paper disabled:opacity-50"
                  >
                    {loading ? "Running…" : "Replay this exact run"}
                  </button>
                </div>

                {decisionBanner}

                <section className="rounded-[24px] border border-hairline bg-card p-6">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
                    Trace
                  </p>
                  <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
                    Pipeline trace
                  </h3>
                  <div className="mt-3">
                    <PipelineTimeline stages={stages} />
                  </div>
                </section>

                <section className="rounded-[24px] border border-hairline bg-card p-6">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
                    Evidence
                  </p>
                  <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
                    Retrieval evidence
                  </h3>
                  <p className="mt-1 text-xs text-muted">
                    {passages.length > 0
                      ? `${passages.length} passages`
                      : `${topK} passages`}
                  </p>
                  {passages.length > 0 ? (
                    <ol className="mt-3 space-y-2 text-sm">
                      {passages.map((p) => (
                        <li
                          key={p.tweet_id}
                          className="rounded-2xl border border-hairline-soft bg-paper p-3"
                        >
                          <div className="flex items-baseline justify-between gap-3">
                            <span className="truncate font-mono text-xs">{p.tweet_id}</span>
                            <span className="shrink-0 font-mono text-xs tabular-nums text-muted">
                              {Number(p.score ?? 0).toFixed(3)}
                            </span>
                          </div>
                          {p.text ? (
                            <p className="mt-1 whitespace-pre-wrap text-[13px] leading-relaxed">
                              {p.text}
                            </p>
                          ) : null}
                        </li>
                      ))}
                    </ol>
                  ) : (
                    <p className="mt-2 text-sm text-muted">
                      {(result.grounding_passage_ids || []).join(", ") || "No passages returned."}
                    </p>
                  )}
                </section>

                <EmbedScene embed={embed} loading={embedLoading} />

                <Inspector inspectId={inspectId} />

                <RunAgainDiff text={text} brand={brand} firstDraft={result?.draft_reply || ""} />

                <CurlCopy text={text} brand={brand} />

                <LogTail />

                <section className="rounded-[24px] border border-hairline bg-card p-6">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
                    Grounding
                  </p>
                  <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
                    Grounding
                  </h3>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono text-[11px]">
                      {draftPath}
                    </span>
                    <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono text-[11px]">
                      {groqChip}
                    </span>
                    <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono text-[11px] tabular-nums">
                      {topK} passages
                    </span>
                    <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 text-[11px] font-semibold">
                      no invented £/time/URL — validation gate
                    </span>
                  </div>
                </section>

                <details className="rounded-[24px] border border-hairline bg-card p-6">
                  <summary className="cursor-pointer text-sm font-medium">Raw JSON</summary>
                  <pre className="mt-3 max-h-96 overflow-y-auto whitespace-pre-wrap break-words rounded-2xl border border-hairline-soft bg-paper p-3 font-mono text-[11px] leading-relaxed">
                    {JSON.stringify({ request: { text, brand }, response: result }, null, 2)}
                  </pre>
                </details>
              </>
            )}
          </div>
        ) : null}

        {tab === "eval" ? (
          <div className="mt-5 space-y-5">
            <EvalRunner brand={brand} />

            <section className="rounded-[24px] border border-hairline bg-card p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">Judge</p>
              <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
                Judge summary
              </h3>
              {judge ? (
                <p className="mt-2 text-sm">
                  Groundedness{" "}
                  <span className="font-mono tabular-nums">{judge.groundedness}/5</span>, verdict{" "}
                  <span className="font-medium">{judge.verdict}</span>
                </p>
              ) : (
                <p className="mt-2 text-sm text-muted">Runs on each prediction, advisory only.</p>
              )}
            </section>

            <section className="rounded-[24px] border border-hairline bg-card p-6">
              <h3 className="font-display text-xl font-semibold tracking-[-0.03em]">
                Session metrics · Since server start
              </h3>
              <div className="mt-3">
                <MetricsPanel />
              </div>
            </section>

            <div className="rounded-[24px] border border-hairline bg-card p-6">
              <p className="text-sm text-muted">
                Offline evaluation (measured 2026-09-11, CPU): VirginTrains human-200 headline —
                intent 0.795 acc / 0.803 macroF1, escalation P 0.778 R 0.757 F1 0.767; full tables
                in docs/REPORT_VIRGIN_6PAGE.md.
              </p>
            </div>
          </div>
        ) : null}
      </main>

      <footer className="border-t border-line">
        <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted">
          Local backend FastAPI 127.0.0.1:8000 · browser → /api/* → FastAPI · Groq key server-only.
        </p>
      </footer>
    </div>
  );
}
