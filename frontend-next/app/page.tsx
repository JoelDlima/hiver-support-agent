"use client";

import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { Activity, AlertTriangle, Gauge, XCircle } from "lucide-react";
import MetricsPanel from "../components/MetricsPanel";
import PipelineTimeline from "../components/PipelineTimeline";
import PipelineFlow from "../components/graph/PipelineFlow";
import EvidenceView from "../components/graph/EvidenceView";
import Inspector from "../components/proof/Inspector";
import RunAgainDiff from "../components/proof/RunAgainDiff";
import LogTail from "../components/proof/LogTail";
import CurlCopy from "../components/proof/CurlCopy";
import EvalRunner from "../components/proof/EvalRunner";
import EmbedScene from "../components/proof/EmbedScene";
import {
  InspectRecordSchema,
  JudgeSchema,
  PredictResponseSchema,
  parsePassageList,
  parseStreamPayload,
} from "../components/proof/schemas";
import type { EmbedPoint, Passage, PredictResponse } from "../lib";

// The legacy 3D retrieval graph is kept as a lazy toggle only: it mounts on
// demand (ssr:false, code-split) while the React-Flow DAG is the default view.
const RetrievalGraph3D = dynamic(() => import("../components/RetrievalGraph3D"), {
  ssr: false,
  loading: () => <p className="text-sm text-muted">Loading 3D graph…</p>,
});

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

/* ------------- Per-widget liveness badges + copy-as-curl ------------- */

type WidgetStatus = "LIVE" | "STALE" | "AWAITING" | "RUNNING" | "LOADING" | "ERROR";

const BADGE_PILL: Record<WidgetStatus, string> = {
  LIVE: "border-teal-600/40 bg-teal-600/10 text-teal-700 dark:text-teal-300",
  STALE: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  AWAITING: "border-hairline-soft bg-paper text-muted",
  RUNNING:
    "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse",
  LOADING:
    "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse",
  ERROR: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
};

function LiveBadge({
  status,
  requestId,
  ms,
  toks,
  onRetry,
  retryLabel,
}: {
  status: WidgetStatus;
  requestId?: string | null;
  ms?: number;
  toks?: number | null;
  onRetry?: () => void;
  retryLabel?: string;
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-semibold ${BADGE_PILL[status]}`}
      >
        {status === "LIVE" ? "●" : status === "AWAITING" ? "○" : status === "STALE" ? "◐" : "●"}{" "}
        {status}
      </span>
      {requestId ? <span className="font-mono">{requestId}</span> : null}
      {ms !== undefined && Number.isFinite(ms) ? (
        <span className="font-mono tabular-nums">{Math.round(ms)} ms</span>
      ) : null}
      {toks !== undefined && toks !== null && Number.isFinite(toks) ? (
        <span className="font-mono tabular-nums">{toks.toFixed(1)} tok/s</span>
      ) : null}
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="font-semibold text-teal hover:underline"
        >
          {retryLabel || "↻ retry"}
        </button>
      ) : null}
    </div>
  );
}

function CurlButton({ cmd }: { cmd: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(cmd);
      } else {
        const ta = document.createElement("textarea");
        ta.value = cmd;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }
  return (
    <button
      type="button"
      onClick={copy}
      title={cmd}
      className="font-mono text-[11px] text-muted hover:underline"
    >
      {copied ? "copied ✓" : "</> curl"}
    </button>
  );
}

function shellQuote(payload: string): string {
  return `'${payload.replace(/'/g, "'\\''")}'`;
}

function buildPredictCurl(text: string, brand: string): string {
  return `curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d ${shellQuote(
    JSON.stringify({ text, brand })
  )}`;
}

function buildStreamCurl(text: string, brand: string): string {
  return `curl -N -X POST http://127.0.0.1:8000/predict/stream -H "Content-Type: application/json" -H "Accept: text/event-stream" -d ${shellQuote(
    JSON.stringify({ text, brand })
  )}`;
}

function buildJudgeCurl(args: { intent: string; draft: string; ids: string[]; inbound: string }): string {
  return `curl -X POST http://127.0.0.1:8000/judge -H "Content-Type: application/json" -d ${shellQuote(
    JSON.stringify({
      intent: args.intent,
      draft_reply: args.draft,
      passage_ids: args.ids,
      inbound: args.inbound.slice(0, 800),
    })
  )}`;
}

function buildPassagesCurl(brand: string, q: string): string {
  return `curl "http://127.0.0.1:8000/passages?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(
    q.slice(0, 200)
  )}"`;
}

function buildEmbedCurl(brand: string, q: string): string {
  return `curl "http://127.0.0.1:8000/embed2d?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(
    q.slice(0, 200)
  )}"`;
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
  // Phase 4B verification-viz widget state (all fed by live backend routes).
  const [retrievalView, setRetrievalView] = useState<"flow" | "3d">("flow");
  const [passagesLoading, setPassagesLoading] = useState(false);
  const [passagesError, setPassagesError] = useState<string | null>(null);
  const [judgeLoading, setJudgeLoading] = useState(false);
  const [judgeError, setJudgeError] = useState<string | null>(null);
  const [streamChunks, setStreamChunks] = useState(0);
  const [streamToks, setStreamToks] = useState<number | null>(null);
  const [metricsNonce, setMetricsNonce] = useState(0);
  const streamStartRef = useRef<number | null>(null);
  const streamCountRef = useRef(0);
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
    setJudgeError(null);
    setStreamChunks(0);
    setStreamToks(null);
    streamStartRef.current = null;
    streamCountRef.current = 0;
    try {
      const r = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, brand }),
      });
      const raw: unknown = await r.json();
      // zod-validated: malformed payloads surface as an error, not a crash.
      const parsed = PredictResponseSchema.safeParse(raw);
      if (!parsed.success) throw new Error("predict payload failed validation");
      const j = parsed.data as unknown as PredictResponse;
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
    setPassagesLoading(true);
    setPassagesError(null);
    try {
      const r = await fetch(`/api/passages?brand=${j.brand}&q=${encodeURIComponent(text.slice(0, 200))}`);
      if (r.ok) {
        const validated = parsePassageList((await r.json()) as unknown);
        if (validated) {
          setPassages(validated);
          return;
        }
      }
      // Honest fallback: the inspect record stores the same live retrieval
      // rows with real scores. Scores are never synthesized client-side.
      try {
        const ir = await fetch(`/api/inspect/${encodeURIComponent(j.request_id)}`);
        if (ir.ok) {
          const rec = InspectRecordSchema.safeParse((await ir.json()) as unknown);
          const fromInspect = rec.success ? parsePassageList(rec.data.passages) : null;
          if (fromInspect && fromInspect.length > 0) {
            setPassages(fromInspect);
            return;
          }
        }
      } catch {
        /* fall through to the empty state below */
      }
      setPassages([]);
      setPassagesError("Passages unavailable — /passages and /inspect both failed.");
    } catch {
      setPassages([]);
      setPassagesError("Passages unavailable — backend not reached.");
    } finally {
      setPassagesLoading(false);
    }
  }

  async function loadJudge(j: PredictResponse) {
    setJudgeLoading(true);
    setJudgeError(null);
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
      if (!r.ok) throw new Error(`judge returned status ${r.status}`);
      // zod-validated: a malformed verdict surfaces as an error, not a crash.
      const parsed = JudgeSchema.safeParse((await r.json()) as unknown);
      if (!parsed.success) throw new Error("judge payload failed validation");
      setJudge({ groundedness: parsed.data.groundedness, verdict: parsed.data.verdict });
    } catch (e) {
      setJudge(null);
      setJudgeError(`Judge unavailable (${String(e)})`);
    } finally {
      setJudgeLoading(false);
    }
  }

  async function runStream() {
    setLoading(true);
    setError(null);
    setResult(null);
    setResultAt(null);
    setStreaming("");
    setJudge(null);
    setJudgeError(null);
    setPassages([]);
    setPassagesError(null);
    setStreamChunks(0);
    setStreamToks(null);
    streamStartRef.current = Date.now();
    streamCountRef.current = 0;
    const noteToks = () => {
      const t0 = streamStartRef.current;
      if (t0 === null) return;
      streamCountRef.current += 1;
      const count = streamCountRef.current;
      const elapsed = Math.max((Date.now() - t0) / 1000, 0.1);
      setStreamChunks(count);
      setStreamToks(count / elapsed);
    };
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
          // zod-validated: malformed chunks are skipped, never crash the run.
          const ev = parseStreamPayload(line.slice(5).trim());
          if (!ev) continue;
          if (ev.event === "token") {
            setStreaming((s) => s + ev.text);
            noteToks();
          } else if (ev.event === "stages") {
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
            final = ev as unknown as PredictResponse;
            setResult(final);
            setResultAt(Date.now());
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
                <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1">
                  <LiveBadge
                    status={loading ? "RUNNING" : result ? (stale ? "STALE" : "LIVE") : "AWAITING"}
                    requestId={result?.request_id}
                    ms={result?.latency_ms}
                    toks={streamToks}
                    onRetry={runPredict}
                  />
                  <CurlButton cmd={buildPredictCurl(text, brand)} />
                  <CurlButton cmd={buildStreamCurl(text, brand)} />
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
                  <div className="mt-1">
                    <LiveBadge
                      status={
                        loading && !result
                          ? "RUNNING"
                          : draftText
                            ? stale
                              ? "STALE"
                              : "LIVE"
                            : "AWAITING"
                      }
                      requestId={result?.request_id}
                      toks={streamToks}
                      onRetry={runStream}
                      retryLabel="↻ re-stream"
                    />
                  </div>
                  <p className="mt-1 min-h-16 whitespace-pre-wrap text-[15px] leading-relaxed">
                    {draftText || (
                      <span className="text-muted">Run a prediction to see the draft.</span>
                    )}
                  </p>
                  {result ? (
                    <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
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
                      {streamChunks > 0 ? (
                        <span>
                          Stream{" "}
                          <span className="font-mono tabular-nums">
                            {streamChunks} chunks
                            {streamToks !== null ? ` · ${streamToks.toFixed(1)} tok/s` : ""}
                          </span>
                        </span>
                      ) : null}
                      <CurlButton cmd={buildStreamCurl(text, brand)} />
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
                  <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                    <LiveBadge
                      status={loading ? "RUNNING" : result ? (stale ? "STALE" : "LIVE") : "AWAITING"}
                      requestId={result?.request_id}
                      ms={result?.latency_ms}
                      onRetry={runPredict}
                    />
                    <CurlButton cmd={buildPredictCurl(text, brand)} />
                  </div>
                  <div className="mt-3">
                    <PipelineFlow
                      classifyMs={sig.classify_ms as number | undefined}
                      retrieveMs={sig.retrieve_ms as number | undefined}
                      draftMs={sig.draft_ms as number | undefined}
                      latencyMs={result?.latency_ms}
                      intent={result?.intent}
                      intentConfidence={result?.intent_confidence}
                      draftPath={draftPath}
                      decision={result?.decision}
                      requestId={result?.request_id}
                      running={loading}
                      hasResult={result !== null}
                    />
                  </div>
                  <div className="mt-3">
                    <PipelineTimeline stages={stages} />
                  </div>
                </section>

                <section className="rounded-[24px] border border-hairline bg-card p-6">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
                    Evidence
                  </p>
                  <div className="mt-1 flex flex-wrap items-center justify-between gap-3">
                    <h3 className="font-display text-xl font-semibold tracking-[-0.03em]">
                      Retrieval evidence
                    </h3>
                    {/* React-Flow is the default retrieval view; the 3D graph
                        is a lazy toggle and only mounts on demand. */}
                    <div className="inline-flex rounded-full border border-hairline-soft bg-paper p-1">
                      <button
                        type="button"
                        onClick={() => setRetrievalView("flow")}
                        aria-pressed={retrievalView === "flow"}
                        className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                          retrievalView === "flow"
                            ? "bg-teal font-semibold text-[#03211f]"
                            : "text-muted hover:opacity-75"
                        }`}
                      >
                        Flow + links
                      </button>
                      <button
                        type="button"
                        onClick={() => setRetrievalView("3d")}
                        aria-pressed={retrievalView === "3d"}
                        className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                          retrievalView === "3d"
                            ? "bg-teal font-semibold text-[#03211f]"
                            : "text-muted hover:opacity-75"
                        }`}
                      >
                        3D graph
                      </button>
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                    <LiveBadge
                      status={
                        passagesLoading
                          ? "LOADING"
                          : passagesError
                            ? "ERROR"
                            : passages.length > 0
                              ? stale
                                ? "STALE"
                                : "LIVE"
                              : "AWAITING"
                      }
                      requestId={result?.request_id}
                      ms={sig.retrieve_ms as number | undefined}
                      onRetry={result ? () => loadPassages(result) : undefined}
                    />
                    <CurlButton cmd={buildPassagesCurl(result?.brand || brand, text)} />
                  </div>
                  <p className="mt-2 text-xs text-muted">
                    {passages.length > 0
                      ? `${passages.length} passages`
                      : `${topK} passages`}
                  </p>
                  {retrievalView === "3d" ? (
                    <div className="mt-3">
                      <RetrievalGraph3D passages={passages} />
                    </div>
                  ) : (
                    <div className="mt-3">
                      <EvidenceView
                        draftReply={result.draft_reply || ""}
                        groundingIds={result.grounding_passage_ids || []}
                        passages={passages}
                        loading={passagesLoading}
                        loadError={passagesError}
                      />
                    </div>
                  )}
                </section>

                <EmbedScene
                  embed={embed}
                  loading={embedLoading}
                  onRetry={() => loadEmbed(result.brand || brand, text)}
                  curl={buildEmbedCurl(result.brand || brand, text)}
                />

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
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                <LiveBadge
                  status={
                    judgeLoading ? "LOADING" : judgeError ? "ERROR" : judge ? "LIVE" : "AWAITING"
                  }
                  requestId={result?.request_id}
                  onRetry={result ? () => loadJudge(result) : undefined}
                />
                {result ? (
                  <CurlButton
                    cmd={buildJudgeCurl({
                      intent: result.intent,
                      draft: result.draft_reply,
                      ids: result.grounding_passage_ids || [],
                      inbound: text,
                    })}
                  />
                ) : null}
              </div>
              {judge ? (
                <p className="mt-2 text-sm">
                  Groundedness{" "}
                  <span className="font-mono tabular-nums">{judge.groundedness}/5</span>, verdict{" "}
                  <span className="font-medium">{judge.verdict}</span>
                </p>
              ) : (
                <p className="mt-2 text-sm text-muted">
                  {judgeError || "Runs on each prediction, advisory only."}
                </p>
              )}
            </section>

            <section className="rounded-[24px] border border-hairline bg-card p-6">
              <h3 className="font-display text-xl font-semibold tracking-[-0.03em]">
                Session metrics · Since server start
              </h3>
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                <LiveBadge
                  status={apiOk ? "LIVE" : apiOk === false ? "ERROR" : "AWAITING"}
                  onRetry={() => setMetricsNonce((v) => v + 1)}
                />
                <CurlButton cmd="curl http://127.0.0.1:8000/metrics" />
              </div>
              <div className="mt-3">
                <MetricsPanel key={metricsNonce} />
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
