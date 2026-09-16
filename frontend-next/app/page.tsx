"use client";

// Demo tab shell (B1): Try it / Proof / Review. All triage state and loaders
// live here; the sections render from the shared DemoVM in components/demo/.
// Every pre-existing widget stays mounted and reachable via the three tabs.

import { useEffect, useRef, useState } from "react";
import {
  InspectRecordSchema,
  JudgeSchema,
  PredictResponseSchema,
  parsePassageList,
  parseStreamPayload,
} from "../components/proof/schemas";
import type { EmbedPoint, Passage } from "../lib";
import TryIt from "../components/demo/TryIt";
import ProofTab from "../components/demo/ProofTab";
import ReviewTab from "../components/demo/ReviewTab";
import LivenessPill, { useBackendLiveness } from "../components/demo/LivenessPill";
import type { DemoVM, JudgeState, PredictResult, RetrievalView, RunLogEntry } from "../components/demo/types";

type TabId = "try" | "proof" | "review";

export default function Page() {
  const [tab, setTab] = useState<TabId>("try");
  const [brand, setBrand] = useState("virgin");
  const [text, setText] = useState("My train from Euston was delayed 45 minutes, how do I claim delay repay?");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState("");
  const [result, setResult] = useState<PredictResult | null>(null);
  const [resultAt, setResultAt] = useState<number | null>(null);
  const [runLog, setRunLog] = useState<RunLogEntry[]>([]);
  const [judge, setJudge] = useState<JudgeState>(null);
  const [passages, setPassages] = useState<Passage[]>([]);
  const [embed, setEmbed] = useState<EmbedPoint[] | null>(null);
  const [embedLoading, setEmbedLoading] = useState(false);
  const [inspectId, setInspectId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  // B5 liveness: single hook polling GET /api/metrics (avg latency included).
  const { apiOk, avgMs, recheck: recheckLiveness } = useBackendLiveness(10_000);
  // Phase 4B verification-viz widget state (all fed by live backend routes).
  const [retrievalView, setRetrievalView] = useState<RetrievalView>("flow");
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

  function appendRunLog(j: PredictResult) {
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

  async function runPredict(nextBrand?: string) {
    const b = nextBrand || brand;
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
        body: JSON.stringify({ text, brand: b }),
      });
      const raw: unknown = await r.json();
      // zod-validated: malformed payloads surface as an error, not a crash.
      const parsed = PredictResponseSchema.safeParse(raw);
      if (!parsed.success) throw new Error("predict payload failed validation");
      const j = parsed.data as unknown as PredictResult;
      setResult(j);
      setResultAt(Date.now());
      appendRunLog(j);
      setInspectId(j.request_id || null);
      await loadPassages(j);
      await loadJudge(j);
      await loadEmbed(j.brand || b, text);
    } catch (e) {
      setError(`Predict failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  async function loadPassages(j: PredictResult) {
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

  async function loadJudge(j: PredictResult) {
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
      let final: PredictResult | null = null;
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
                  ...(prev as PredictResult),
                  intent: ev.intent,
                  intent_confidence: ev.intent_confidence,
                  signals: {
                    ...((prev as PredictResult | null)?.signals || {}),
                    classify_ms: ev.classify_ms,
                    retrieve_ms: ev.retrieve_ms,
                    draft_ms: ev.draft_ms,
                  },
                }) as PredictResult
            );
            setResultAt(Date.now());
          } else if (ev.event === "final") {
            final = ev as unknown as PredictResult;
            setResult(final);
            setResultAt(Date.now());
          }
        }
      }
      if (final) {
        appendRunLog(final as PredictResult);
        setInspectId((final as PredictResult).request_id || null);
        await loadPassages(final as PredictResult);
        await loadJudge(final as PredictResult);
        await loadEmbed((final as PredictResult).brand || brand, text);
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") setError(`Stream failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  const vm: DemoVM = {
    brand,
    text,
    loading,
    streaming,
    result,
    resultAt,
    now,
    runLog,
    judge,
    passages,
    embed,
    embedLoading,
    inspectId,
    error,
    apiOk,
    retrievalView,
    passagesLoading,
    passagesError,
    judgeLoading,
    judgeError,
    streamChunks,
    streamToks,
    metricsNonce,
    setBrand,
    setText,
    setRetrievalView,
    runPredict,
    runStream,
    loadPassages,
    loadJudge,
    loadEmbed,
    bumpMetrics: () => {
      setMetricsNonce((v) => v + 1);
      recheckLiveness();
    },
    goProof: () => setTab("proof"),
  };

  const tabs: Array<{ id: TabId; label: string }> = [
    { id: "try", label: "Try it" },
    { id: "proof", label: "Proof" },
    { id: "review", label: "Review" },
  ];

  return (
    <div className="min-h-screen bg-canvas font-sans text-ink">
      <main className="mx-auto max-w-6xl px-4 py-6">
        {/* 1. Title block */}
        <div id="triage" className="scroll-mt-20">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Hiver Support Intelligence
          </p>
          <h1 className="mt-1 font-display text-4xl font-bold tracking-[-0.03em]">Live Triage</h1>
          <p className="mt-1 text-sm text-muted">
            Test a customer request and inspect exactly how the agent reached its decision.
          </p>
          <p className="mt-1 text-xs text-muted">
            <a className="underline hover:opacity-75" href="/review">Review inbox</a>
            {" · "}
            <a className="underline hover:opacity-75" href="/api/graph" target="_blank" rel="noreferrer">Advanced — repository knowledge graph</a>
            <span> (offline-built code+docs map — see graphify-out/)</span>
          </p>
        </div>

        {/* 2. Tabs + liveness */}
        <div id="proof" className="mt-4 flex scroll-mt-20 flex-wrap items-center gap-2">
          <div className="inline-flex rounded-full border border-hairline-soft bg-paper p-1">
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
          <LivenessPill apiOk={apiOk} avgMs={avgMs} onRecheck={recheckLiveness} />
        </div>

        {tab === "try" ? <TryIt vm={vm} /> : null}
        {tab === "proof" ? <ProofTab vm={vm} /> : null}
        {tab === "review" ? <ReviewTab /> : null}
      </main>

      <footer id="eval" className="scroll-mt-20 border-t border-line">
        <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted">
          Local backend FastAPI 127.0.0.1:8000 · browser → /api/* → FastAPI · Groq key server-only.
        </p>
      </footer>
    </div>
  );
}
