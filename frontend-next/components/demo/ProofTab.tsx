"use client";

// B1 — "Proof" section in grading-rubric order: per-query receipt → pipeline
// trace → retrieval evidence → groundedness chips → Inspector → baselines
// (EvalRunner, compare strip, ablation) → golden/agreement (judge summary) →
// failure gallery → latency (metrics, liveness, local-inference strip) →
// grounding notes + replay tools. Every pre-existing widget stays mounted.

import dynamic from "next/dynamic";
import PipelineTimeline from "../PipelineTimeline";
import PipelineFlow from "../graph/PipelineFlow";
import EvidenceView from "../graph/EvidenceView";
import Inspector from "../proof/Inspector";
import RunAgainDiff from "../proof/RunAgainDiff";
import LogTail from "../proof/LogTail";
import CurlCopy from "../proof/CurlCopy";
import EvalRunner from "../proof/EvalRunner";
import EmbedScene from "../proof/EmbedScene";
import MetricsPanel from "../MetricsPanel";
import type { DemoVM } from "./types";
import { isEscalateDecision, isStale } from "./stageUI";
import {
  CurlButton,
  LiveBadge,
  buildEmbedCurl,
  buildJudgeCurl,
  buildPassagesCurl,
  buildPredictCurl,
} from "./widgets";
import ProofReceipt from "./ProofReceipt";
import GroundednessChips from "./GroundednessChips";
import FailureGallery from "./FailureGallery";
import CompareStrip from "./CompareStrip";
import AblationPanel from "./AblationPanel";
import LivenessPill, { LocalInferenceStrip } from "./LivenessPill";

// The legacy 3D retrieval graph is kept as a lazy toggle only: it mounts on
// demand (ssr:false, code-split) while the React-Flow DAG is the default view.
const RetrievalGraph3D = dynamic(() => import("../RetrievalGraph3D"), {
  ssr: false,
  loading: () => <p className="text-sm text-muted">Loading 3D graph…</p>,
});

export default function ProofTab({ vm }: { vm: DemoVM }) {
  const {
    brand, text, loading, result, resultAt, now,
    judge, passages, embed, embedLoading, inspectId,
    retrievalView, passagesLoading, passagesError,
    judgeLoading, judgeError, metricsNonce, apiOk,
  } = vm;

  const emptyCard = (
    <div className="rounded-[24px] border border-hairline bg-card p-6">
      <p className="text-sm text-muted">
        No analysis yet — run a query in the Try it tab, then inspect exactly how
        the agent reached its decision here.
      </p>
    </div>
  );

  if (!result) return <div className="mt-5 space-y-5">{emptyCard}</div>;

  const sig = (result.signals || {}) as Record<string, unknown>;
  const stale = isStale(resultAt, now);
  const topK = (result.grounding_passage_ids || []).length;
  const draftPath = String(sig.draft_path || result.draft_path || "template");
  const groqReason = String(sig.groq_reason || result.groq_reason || (draftPath === "groq" ? "groq live" : "template"));
  const groqChip = String(sig.groq_reason || "template default");
  const escalated = isEscalateDecision(result.decision);

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
      name: `Draft (${draftPath})`,
      ms: sig.draft_ms as number | undefined,
      state: loading ? ("active" as const) : result ? ("done" as const) : ("idle" as const),
      note: groqReason,
    },
    {
      name: "Escalate decision",
      ms: result?.latency_ms,
      state: result ? ("done" as const) : ("idle" as const),
      note: result ? `${result.decision} (${result.escalate_reason})` : undefined,
    },
  ];

  const decisionBanner = (
    <div
      role="status"
      className={`flex flex-wrap items-center justify-between gap-3 rounded-[24px] border p-4 md:p-5 ${
        escalated
          ? "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300"
          : "border-teal bg-teal/10 text-teal"
      }`}
    >
      <p className="text-sm font-semibold">
        {escalated ? (
          <>
            ● Needs a human — {result.decision} · {result.escalate_reason} · via {draftPath}
          </>
        ) : (
          <>
            ● Auto-handle — {result.decision} · {result.escalate_reason} · via {draftPath}
          </>
        )}
      </p>
      <span className="font-mono text-xs tabular-nums opacity-80">
        {result.latency_ms} ms · {result.request_id}
      </span>
    </div>
  );

  return (
    <div className="mt-5 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-[24px] border border-hairline bg-card p-6">
        <span className="font-mono text-xs tabular-nums">{result.request_id}</span>
        <button
          type="button"
          onClick={() => vm.runPredict()}
          disabled={loading}
          className="inline-flex h-8 items-center justify-center rounded-full border border-hairline bg-card px-4 text-sm font-medium text-ink hover:border-hairline-strong hover:bg-paper disabled:opacity-50"
        >
          {loading ? "Running…" : "Replay this exact run"}
        </button>
      </div>

      {decisionBanner}

      <ProofReceipt result={result} onOpenInspector={vm.goProof} />

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
            onRetry={() => vm.runPredict()}
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
              onClick={() => vm.setRetrievalView("flow")}
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
              onClick={() => vm.setRetrievalView("3d")}
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
            onRetry={result ? () => vm.loadPassages(result) : undefined}
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
        onRetry={() => vm.loadEmbed(result.brand || brand, text)}
        curl={buildEmbedCurl(result.brand || brand, text)}
      />

      <GroundednessChips result={result} inbound={text} />

      <Inspector inspectId={inspectId} />

      {/* Rubric: baselines */}
      <EvalRunner brand={brand} />

      <CompareStrip />

      <AblationPanel />

      <div className="rounded-[24px] border border-hairline bg-card p-6">
        <p className="text-sm text-muted">
          Offline evaluation (measured 2026-09-11, CPU): VirginTrains human-200 headline —
          intent 0.795 acc / 0.803 macroF1, escalation P 0.778 R 0.757 F1 0.767; full tables
          in docs/REPORT_VIRGIN_6PAGE.md.
        </p>
      </div>

      {/* Rubric: golden / agreement */}
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
            onRetry={result ? () => vm.loadJudge(result) : undefined}
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
        <p className="mt-3 border-t border-hairline pt-3 text-xs leading-relaxed text-muted">
          Agreement status: open-verdict judge agreement missed the gate twice (v1 κ
          0.253, v2 negative → advisory-only). A groundedness-only V3 study
          (κ + 95% CI vs the wκ ≥ 0.60 ship gate) is pending — see
          evaluation/virgin/JUDGE_AGREEMENT_V3.md when workstream A lands it, and
          the groundedness chips above for per-query scores.
        </p>
      </section>

      {/* Rubric: failure gallery */}
      <FailureGallery />

      {/* Rubric: latency */}
      <section className="rounded-[24px] border border-hairline bg-card p-6">
        <h3 className="font-display text-xl font-semibold tracking-[-0.03em]">
          Session metrics · Since server start
        </h3>
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
          <LiveBadge
            status={apiOk ? "LIVE" : apiOk === false ? "ERROR" : "AWAITING"}
            onRetry={vm.bumpMetrics}
          />
          <LivenessPill apiOk={apiOk} avgMs={null} onRecheck={vm.bumpMetrics} />
          <CurlButton cmd="curl http://127.0.0.1:8000/metrics" />
        </div>
        <div className="mt-3">
          <MetricsPanel key={metricsNonce} />
        </div>
      </section>

      <LocalInferenceStrip />

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
    </div>
  );
}
