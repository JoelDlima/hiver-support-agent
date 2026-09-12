"use client";

import { useEffect, useState } from "react";
import type { InspectRecord } from "../../lib";
import { Card } from "../sg/card";
import { InspectRecordSchema } from "./schemas";

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3 border-t border-hairline py-1.5 first:border-t-0 first:pt-0">
      <span className="shrink-0 text-xs text-muted">{label}</span>
      <span className="truncate font-mono text-xs text-ink" title={value}>
        {value}
      </span>
    </div>
  );
}

export default function Inspector({ inspectId }: { inspectId: string | null }) {
  const [record, setRecord] = useState<InspectRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSystem, setShowSystem] = useState(false);
  const [nonce, setNonce] = useState(0);
  const [copied, setCopied] = useState(false);

  const curl = inspectId
    ? `curl http://127.0.0.1:8000/inspect/${encodeURIComponent(inspectId)}`
    : "";

  async function copyCurl() {
    if (!curl) return;
    try {
      await navigator.clipboard.writeText(curl);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  useEffect(() => {
    if (!inspectId) {
      setRecord(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    setShowSystem(false);
    fetch(`/api/inspect/${encodeURIComponent(inspectId)}`)
      .then(async (r) => {
        if (!r.ok) throw new Error(`inspect returned status ${r.status}`);
        return (await r.json()) as unknown;
      })
      .then((j) => {
        // zod-validated: a malformed record surfaces as an error, not a crash.
        const parsed = InspectRecordSchema.safeParse(j);
        if (!parsed.success) throw new Error("inspect payload failed validation");
        if (!cancelled) setRecord(parsed.data as unknown as InspectRecord);
      })
      .catch((e) => {
        if (!cancelled) {
          setRecord(null);
          setError(`Could not load record (${String(e)})`);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [inspectId, nonce]);

  const timings = record
    ? Object.entries(record.timings || {}).filter(
        (e): e is [string, number] => typeof e[1] === "number"
      )
    : [];

  return (
    <Card className="rounded-[24px] p-6">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
        Raw call
      </p>
      <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
        Inspector
      </h3>
      {/* Liveness: status · request_id · measured timings · retry · copy-as-curl. */}
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-semibold ${
            loading
              ? "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse"
              : error
                ? "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300"
                : record
                  ? "border-teal-600/40 bg-teal-600/10 text-teal-700 dark:text-teal-300"
                  : "border-hairline-soft bg-paper"
          }`}
        >
          {loading ? "● LOADING" : error ? "● ERROR" : record ? "● LIVE" : "○ AWAITING"}
        </span>
        {inspectId ? <span className="font-mono">{inspectId}</span> : null}
        {inspectId ? (
          <button
            type="button"
            onClick={() => setNonce((v) => v + 1)}
            disabled={loading}
            className="font-semibold text-teal hover:underline disabled:opacity-50"
          >
            ↻ retry
          </button>
        ) : null}
        {curl ? (
          <button type="button" onClick={copyCurl} title={curl} className="font-mono hover:underline">
            {copied ? "copied ✓" : "</> curl"}
          </button>
        ) : null}
      </div>
      {!inspectId ? (
        <p className="mt-2 text-sm text-muted">Run a prediction to inspect its record.</p>
      ) : loading ? (
        <p className="mt-2 font-mono text-xs text-muted">Loading {inspectId}…</p>
      ) : error ? (
        <p className="mt-2 text-sm text-red-700 dark:text-red-300">{error}</p>
      ) : record ? (
        <div className="mt-3">
          <MetaRow label="Request" value={record.request_id} />
          <MetaRow label="Model" value={record.llm?.model || "unknown"} />
          <MetaRow label="Timestamp" value={record.timestamp} />
          <MetaRow
            label="Tokens"
            value={`${record.llm?.prompt_tokens ?? 0} in / ${record.llm?.completion_tokens ?? 0} out`}
          />
          <div className="mt-3">
            <button
              type="button"
              onClick={() => setShowSystem((s) => !s)}
              className="rounded-full border border-hairline-soft bg-paper px-3 py-1 text-xs font-medium text-ink hover:border-hairline-strong"
            >
              {showSystem ? "Hide system prompt" : "Show system prompt"}
            </button>
            {showSystem ? (
              <pre className="mt-2 max-h-40 overflow-y-auto whitespace-pre-wrap break-words rounded-2xl border border-hairline-soft bg-paper p-3 font-mono text-[11px] leading-relaxed text-ink">
                {record.llm?.system || "(empty)"}
              </pre>
            ) : null}
          </div>
          <div className="mt-3">
            <p className="text-xs text-muted">User prompt</p>
            <p className="mt-1 whitespace-pre-wrap rounded-2xl border border-hairline-soft bg-paper p-3 text-sm leading-relaxed">
              {record.llm?.user || record.text}
            </p>
          </div>
          <div className="mt-3">
            <p className="text-xs text-muted">Completion</p>
            <p className="mt-1 whitespace-pre-wrap rounded-2xl border border-hairline-soft bg-paper p-3 text-sm leading-relaxed">
              {record.llm?.completion || "(empty)"}
            </p>
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5 border-t border-hairline pt-3">
            <span className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 text-[11px] font-semibold">
              {record.decision} ({record.escalate_reason})
            </span>
            {timings.map(([k, v]) => (
              <span
                key={k}
                className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono text-[11px] tabular-nums text-muted"
              >
                {k} {v} ms
              </span>
            ))}
          </div>
        </div>
      ) : null}
    </Card>
  );
}
