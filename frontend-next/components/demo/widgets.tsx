"use client";

// Per-widget liveness badges, copy-as-curl buttons, and curl builders shared by
// the demo sections. Moved verbatim from app/page.tsx so every section keeps
// identical status language (LIVE / STALE / AWAITING / RUNNING / LOADING / ERROR).

import { useState } from "react";

export type WidgetStatus = "LIVE" | "STALE" | "AWAITING" | "RUNNING" | "LOADING" | "ERROR";

export const BADGE_PILL: Record<WidgetStatus, string> = {
  LIVE: "border-teal-600/40 bg-teal-600/10 text-teal-700 dark:text-teal-300",
  STALE: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  AWAITING: "border-hairline-soft bg-paper text-muted",
  RUNNING:
    "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse",
  LOADING:
    "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 animate-pulse",
  ERROR: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
};

export function LiveBadge({
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

export function CurlButton({ cmd }: { cmd: string }) {
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

export function buildPredictCurl(text: string, brand: string): string {
  return `curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d ${shellQuote(
    JSON.stringify({ text, brand })
  )}`;
}

export function buildStreamCurl(text: string, brand: string): string {
  return `curl -N -X POST http://127.0.0.1:8000/predict/stream -H "Content-Type: application/json" -H "Accept: text/event-stream" -d ${shellQuote(
    JSON.stringify({ text, brand })
  )}`;
}

export function buildJudgeCurl(args: { intent: string; draft: string; ids: string[]; inbound: string }): string {
  return `curl -X POST http://127.0.0.1:8000/judge -H "Content-Type: application/json" -d ${shellQuote(
    JSON.stringify({
      intent: args.intent,
      draft_reply: args.draft,
      passage_ids: args.ids,
      inbound: args.inbound.slice(0, 800),
    })
  )}`;
}

export function buildGroundednessCurl(args: { brand: string; text: string; reply: string; ids: string[] }): string {
  return `curl -X POST http://127.0.0.1:8000/judge/groundedness -H "Content-Type: application/json" -d ${shellQuote(
    JSON.stringify({
      brand: args.brand,
      text: args.text.slice(0, 2000),
      reply: args.reply.slice(0, 2000),
      passage_ids: args.ids,
    })
  )}`;
}

export function buildPassagesCurl(brand: string, q: string): string {
  return `curl "http://127.0.0.1:8000/passages?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(
    q.slice(0, 200)
  )}"`;
}

export function buildEmbedCurl(brand: string, q: string): string {
  return `curl "http://127.0.0.1:8000/embed2d?brand=${encodeURIComponent(brand)}&q=${encodeURIComponent(
    q.slice(0, 200)
  )}"`;
}
