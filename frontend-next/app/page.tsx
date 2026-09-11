"use client";

import dynamic from "next/dynamic";
import { useRef, useState } from "react";
import ConfidenceBars from "../components/ConfidenceBars";
import MetricsPanel from "../components/MetricsPanel";
import PipelineTimeline from "../components/PipelineTimeline";
import type { Passage, PredictResponse } from "../lib";

const RetrievalGraph3D = dynamic(() => import("../components/RetrievalGraph3D"), { ssr: false });

type Judge = { groundedness: number; verdict: string } | null;

export default function Page() {
  const [brand, setBrand] = useState("virgin");
  const [text, setText] = useState("My train from Euston was delayed 45 minutes, how do I claim delay repay?");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState("");
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [judge, setJudge] = useState<Judge>(null);
  const [passages, setPassages] = useState<Passage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  async function runPredict() {
    setLoading(true); setError(null); setStreaming(""); setJudge(null);
    try {
      const r = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, brand }),
      });
      const j: PredictResponse = await r.json();
      setResult(j);
      await loadPassages(j);
      await loadJudge(j);
    } catch (e) {
      setError(`Predict failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  async function loadPassages(j: PredictResponse) {
    // Live retrieval evidence comes from the backend KB lookup endpoint.
    try {
      const r = await fetch(`/api/passages?brand=${j.brand}&q=${encodeURIComponent(text.slice(0, 200))}`);
      if (r.ok) setPassages(await r.json());
      else setPassages((j.grounding_passage_ids || []).map((id, i) => ({ tweet_id: id, score: 1 - i * 0.05, text: "" })));
    } catch {
      setPassages((j.grounding_passage_ids || []).map((id, i) => ({ tweet_id: id, score: 1 - i * 0.05, text: "" })));
    }
  }

  async function loadJudge(j: PredictResponse) {
    try {
      const r = await fetch("/api/judge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intent: j.intent, draft_reply: j.draft_reply, passage_ids: j.grounding_passage_ids, inbound: text }),
      });
      if (r.ok) setJudge(await r.json());
    } catch { /* judge is advisory */ }
  }

  async function runStream() {
    setLoading(true); setError(null); setResult(null); setStreaming(""); setJudge(null); setPassages([]);
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
            else if (ev.event === "stages") setResult((prev) => ({ ...(prev as PredictResponse), intent: ev.intent, intent_confidence: ev.intent_confidence, signals: { ...(prev?.signals || {}), classify_ms: ev.classify_ms, retrieve_ms: ev.retrieve_ms, draft_ms: ev.draft_ms } } as PredictResponse));
            else if (ev.event === "final") { final = ev as PredictResponse; setResult(final); }
          } catch { /* keep-alive */ }
        }
      }
      if (final) { await loadPassages(final); await loadJudge(final); }
    } catch (e) {
      if ((e as Error).name !== "AbortError") setError(`Stream failed: ${e}`);
    } finally {
      setLoading(false);
    }
  }

  const sig = result?.signals || {};
  const stages = [
    { name: "Validate + normalize", ms: undefined, state: result ? ("done" as const) : ("idle" as const) },
    { name: "Classify intent", ms: sig.classify_ms as number | undefined, state: result ? ("done" as const) : ("idle" as const), note: result ? `${result.intent} @ ${Number(result.intent_confidence || 0).toFixed(3)}` : undefined },
    { name: "Retrieve top-5 KB", ms: sig.retrieve_ms as number | undefined, state: result ? ("done" as const) : ("idle" as const), note: result ? `${(result.grounding_passage_ids || []).length} passages` : undefined },
    { name: `Draft (${String(sig.draft_path || "template")})`, ms: sig.draft_ms as number | undefined, state: loading ? ("active" as const) : result ? ("done" as const) : ("idle" as const), note: String((sig as Record<string, unknown>).groq_reason || (sig.draft_path === "groq" ? "groq live" : "template")) },
    { name: "Escalate decision", ms: result?.latency_ms, state: result ? ("done" as const) : ("idle" as const), note: result ? `${result.decision} (${result.escalate_reason})` : undefined },
  ];

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Hiver — Support Triage Agent</h1>
          <p className="text-sm text-slate-400">
            VirginTrains primary · AppleSupport kept · Groq <code>qwen/qwen3.8-27b</code> gated behind £/time/URL validation
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <label className="text-slate-400">Brand</label>
          <select value={brand} onChange={(e) => setBrand(e.target.value)} className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1">
            <option value="virgin">VirginTrains (primary)</option>
            <option value="apple">AppleSupport (v1 evidence)</option>
          </select>
        </div>
      </header>

      <section className="mb-4 rounded-lg border border-slate-800 bg-slate-900/40 p-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          maxLength={2000}
          className="w-full rounded-md border border-slate-700 bg-black/50 p-3 text-sm"
          placeholder="Type a customer message…"
        />
        <div className="mt-3 flex gap-2">
          <button onClick={runPredict} disabled={loading} className="rounded-md bg-cyan-500 px-4 py-2 text-sm font-semibold text-black disabled:opacity-50">
            {loading ? "Running…" : "Predict (live technicals)"}
          </button>
          <button onClick={runStream} disabled={loading} className="rounded-md border border-cyan-500 px-4 py-2 text-sm font-semibold text-cyan-300 disabled:opacity-50">
            Stream draft live (SSE + Groq)
          </button>
          {error ? <span className="text-sm text-red-400">{error}</span> : null}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Draft reply (live)</h2>
          <p className="min-h-16 whitespace-pre-wrap text-[15px] leading-relaxed">
            {streaming || result?.draft_reply || <span className="text-slate-600">Run a prediction…</span>}
          </p>
          {result ? (
            <div className="mt-3 border-t border-slate-800 pt-3">
              <ConfidenceBars confidence={result.intent_confidence} decision={`${result.decision} (${result.escalate_reason})`} />
            </div>
          ) : null}
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Pipeline (measured live, ms)</h2>
          <PipelineTimeline stages={stages} />
        </div>
      </section>

      <section className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Retrieval — live top-k (3D + ranked)</h2>
          <RetrievalGraph3D passages={passages} />
          <ol className="mt-2 space-y-1 text-xs">
            {passages.map((p) => (
              <li key={p.tweet_id} className="flex justify-between gap-2 rounded border border-slate-800 px-2 py-1">
                <span className="truncate font-mono">{p.tweet_id}</span>
                <span className="tabular-nums text-slate-300">score {p.score.toFixed(3)}</span>
              </li>
            ))}
            {!passages.length ? <li className="text-slate-600">No passages yet.</li> : null}
          </ol>
        </div>
        <div className="flex flex-col gap-4">
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Judge (live heuristic, advisory)</h2>
            {judge ? (
              <p className="text-sm">Groundedness <b className="tabular-nums">{judge.groundedness}/5</b> · verdict <b>{judge.verdict}</b> <span className="text-slate-500">(rubric v1; LLM hook gated)</span></p>
            ) : (
              <p className="text-sm text-slate-500">Runs on each prediction…</p>
            )}
            {result ? (
              <p className="mt-1 text-xs text-slate-500">
                req <code>{result.request_id}</code> · passages {result.grounding_passage_ids.length} · draft_path <code>{String(sig.draft_path)}</code> · total <span className="tabular-nums">{result.latency_ms} ms</span>
              </p>
            ) : null}
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-400">Service metrics (live, 5s poll)</h2>
            <MetricsPanel />
          </div>
        </div>
      </section>

      <footer className="mt-6 text-xs text-slate-500">
        BFF proxy: browser → /api/* → FastAPI :8000 (GROQ key server-only). Streaming: SSE tokens live. Grounding IDs cite the KB; £/time/URL validated or draft falls back to template.
      </footer>
    </main>
  );
}
