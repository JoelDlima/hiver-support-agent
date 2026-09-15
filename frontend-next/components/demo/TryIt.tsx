"use client";

// B1 — "Try it" section: query hero → result. Moved from app/page.tsx's triage
// tab so the shell stays a tab container. Includes the brand switcher (B4:
// switching brand re-runs the hero query when a result exists), the decision
// banner, stage cards, intent-confidence gauge, draft reply, run log, and the
// per-query proof receipt (B2).

import { motion } from "framer-motion";
import { Activity, AlertTriangle, Gauge, XCircle } from "lucide-react";
import type { DemoVM } from "./types";
import { STAGE_PILL, formatMs, isEscalateDecision, isStale, stageStatus } from "./stageUI";
import { CurlButton, LiveBadge, buildPredictCurl, buildStreamCurl } from "./widgets";
import ProofReceipt from "./ProofReceipt";

export default function TryIt({ vm }: { vm: DemoVM }) {
  const { brand, text, loading, streaming, result, resultAt, now, runLog, error, streamToks, streamChunks, apiOk } = vm;

  const sig = (result?.signals || {}) as Record<string, unknown>;
  const stale = isStale(resultAt, now);
  const cardStatus = stageStatus(result !== null, stale);
  const displayPill = loading ? "RUNNING" : cardStatus;
  const conf = Number(result?.intent_confidence || 0);
  const confPct = Math.round(Math.min(Math.max(conf, 0), 1) * 100);
  const topK = (result?.grounding_passage_ids || []).length;
  const draftPath = String(sig.draft_path || result?.draft_path || "template");
  const groqReason = String(sig.groq_reason || result?.groq_reason || (draftPath === "groq" ? "groq live" : "template"));
  const escalated = isEscalateDecision(result?.decision);
  const draftText = streaming || result?.draft_reply || "";

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
      pin: result ? result.decision || "—" : "—",
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

  function switchBrand(b: string) {
    if (b === brand) return;
    vm.setBrand(b);
    // B4 accept: switching brand re-runs the hero query when one exists.
    if (result) vm.runPredict(b);
  }

  return (
    <div className="mt-5 space-y-5">
      {/* Hero FIRST */}
      <section className="rounded-[24px] border border-hairline bg-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex rounded-full border border-hairline-soft bg-paper p-1">
            <button
              onClick={() => switchBrand("virgin")}
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
              onClick={() => switchBrand("apple")}
              className={`flex flex-col items-start rounded-full px-4 py-1.5 text-left ${
                brand === "apple"
                  ? "bg-teal font-semibold text-[#03211f]"
                  : "text-muted hover:opacity-75"
              }`}
            >
              <span className="text-sm font-medium">Apple Support</span>
              <span className="text-[11px] opacity-70">Transfer evidence</span>
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
            onChange={(e) => vm.setText(e.target.value)}
            rows={5}
            maxLength={2000}
            className="mt-1 w-full rounded-2xl border border-hairline-soft bg-paper p-3 text-sm placeholder:text-muted"
            placeholder="Type a customer message"
          />
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              onClick={() => vm.runPredict()}
              disabled={loading}
              className="rounded-full bg-teal px-5 py-2 text-sm font-semibold text-[#03211f] transition-opacity hover:opacity-85 disabled:opacity-50"
            >
              {loading ? "Running…" : "Run live analysis"}
            </button>
            <button
              onClick={vm.runStream}
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
              onRetry={() => vm.runPredict()}
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

      {/* Below hero */}
      {!result && !loading ? (
        emptyCard
      ) : (
        <>
          {decisionBanner}

          {result ? <ProofReceipt result={result} onOpenInspector={vm.goProof} /> : null}

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
                onRetry={vm.runStream}
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
  );
}
