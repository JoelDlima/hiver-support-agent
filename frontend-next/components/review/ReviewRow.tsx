"use client";

import { useState } from "react";
import SlaChip from "./SlaChip";

export type ReviewItem = {
  id: string;
  brand: string;
  intent: string;
  intent_confidence: number;
  text: string;
  draft_reply: string;
  grounding_passage_ids: string[];
  reason_code: string;
  status: string;
  reviewer?: string | null;
  sla_due_at?: string | null;
  created_at?: string | null;
};

export default function ReviewRow({
  item,
  selected,
  now,
  reviewer,
  onAction,
}: {
  item: ReviewItem;
  selected: boolean;
  now: number;
  reviewer: string;
  onAction: (id: string, kind: "approve" | "edit" | "reject", finalText?: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(item.draft_reply || "");
  const conf = Math.round(Math.min(Math.max(Number(item.intent_confidence || 0), 0), 1) * 100);

  return (
    <article
      className={`rounded-[24px] border bg-card p-5 ${
        selected ? "border-teal" : "border-hairline"
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="inline-flex items-center rounded-full bg-teal px-2.5 py-1 font-mono text-[11px] font-semibold text-white">
          {item.intent}
        </span>
        <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono text-[11px] tabular-nums">
          {conf}%
        </span>
        <span
          className="inline-flex items-center rounded-full border border-amber-500/40 bg-amber-500/10 px-2.5 py-1 text-[11px] font-semibold text-amber-700 dark:text-amber-300"
          title="Why the agent abstained instead of auto-handling"
        >
          abstain: {item.reason_code}
        </span>
        <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 text-[11px]">
          {item.brand}
        </span>
        <SlaChip slaDueAt={item.sla_due_at} now={now} />
        <span className="ml-auto font-mono text-[11px] text-muted">{item.id}</span>
      </div>

      <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed">{item.text}</p>

      {!editing ? (
        <p className="mt-2 whitespace-pre-wrap rounded-2xl border border-hairline-soft bg-paper p-3 text-sm leading-relaxed">
          {item.draft_reply}
        </p>
      ) : (
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          rows={4}
          className="mt-2 w-full rounded-2xl border border-hairline-soft bg-paper p-3 text-sm"
          aria-label="Edited reply"
        />
      )}

      <div className="mt-3 flex flex-wrap items-center gap-2">
        {!editing ? (
          <>
            <button
              onClick={() => onAction(item.id, "approve")}
              className="rounded-full bg-teal px-4 py-1.5 text-sm font-semibold text-[#03211f] hover:opacity-85"
            >
              Approve
            </button>
            <button
              onClick={() => setEditing(true)}
              className="rounded-full border border-hairline-soft px-4 py-1.5 text-sm font-semibold hover:opacity-75"
            >
              Edit
            </button>
            <button
              onClick={() => onAction(item.id, "reject")}
              className="rounded-full border border-red-500/40 px-4 py-1.5 text-sm font-semibold text-red-700 dark:text-red-300 hover:opacity-75"
            >
              Escalate
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => {
                onAction(item.id, "edit", draft);
                setEditing(false);
              }}
              disabled={!draft.trim()}
              className="rounded-full bg-teal px-4 py-1.5 text-sm font-semibold text-[#03211f] hover:opacity-85 disabled:opacity-50"
            >
              Save edit
            </button>
            <button
              onClick={() => {
                setDraft(item.draft_reply || "");
                setEditing(false);
              }}
              className="rounded-full border border-hairline-soft px-4 py-1.5 text-sm font-semibold hover:opacity-75"
            >
              Cancel
            </button>
          </>
        )}
        <span className="text-xs text-muted">
          {(item.grounding_passage_ids || []).length} passages · reviewer {reviewer || "—"}
        </span>
      </div>
    </article>
  );
}
