"use client";

// B2 — Proof receipt per query. Renders the machine-checkable facts of one run:
// intent + ConfidenceBars + retrieved passage IDs + template/draft-path id +
// escalation reason + request_id linking to the Inspector (/inspect/{id}).
// Shows an OFFLINE banner when response.offline is true (workstream A4).

import ConfidenceBars from "../ConfidenceBars";
import type { PredictResult } from "./types";

export default function ProofReceipt({
  result,
  onOpenInspector,
}: {
  result: PredictResult;
  onOpenInspector: () => void;
}) {
  const offline = result.offline === true;
  const sig = (result.signals || {}) as Record<string, unknown>;
  // Backend has no `template_id` field yet — the draft identity is draft_path
  // (+ groq_reason). Show template_id when the contract lands, else the
  // draft_path honestly labeled.
  const templateId =
    result.template_id || String(sig.draft_path || result.draft_path || "template");
  const ids = result.grounding_passage_ids || [];

  return (
    <section
      aria-label="Proof receipt"
      className="rounded-[24px] border border-hairline bg-card p-6"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
        Receipt
      </p>
      <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
        Proof receipt
      </h3>

      {offline ? (
        <p
          role="status"
          className="mt-3 rounded-2xl border border-amber-500/40 bg-amber-500/10 px-4 py-2.5 text-sm font-semibold text-amber-700 dark:text-amber-300"
        >
          OFFLINE — template only. Response echoed offline=true: no LLM calls were
          attempted for this run.
        </p>
      ) : null}

      <div className="mt-3">
        <ConfidenceBars
          confidence={Number(result.intent_confidence || 0)}
          decision={result.decision || "—"}
        />
      </div>

      <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-xs text-muted">Intent</dt>
          <dd className="font-mono font-semibold">{result.intent || "—"}</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Template / draft path</dt>
          <dd className="font-mono font-semibold" title={String(sig.groq_reason || "")}>
            {templateId}
          </dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Escalation reason</dt>
          <dd className="font-medium">{result.escalate_reason || "—"}</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Request</dt>
          <dd>
            <button
              type="button"
              onClick={onOpenInspector}
              title="Open this run in the Inspector (Proof tab)"
              className="font-mono text-xs text-teal hover:underline"
            >
              {result.request_id} →
            </button>
          </dd>
        </div>
      </dl>

      <div className="mt-3">
        <p className="text-xs text-muted">
          Grounding passages ({ids.length})
        </p>
        {ids.length > 0 ? (
          <ul className="mt-1.5 flex flex-wrap gap-1.5">
            {ids.map((id) => (
              <li
                key={id}
                className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono text-[11px]"
              >
                {id}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-1 text-xs text-muted">No passage IDs on this response.</p>
        )}
      </div>
    </section>
  );
}
