"use client";

import { useEffect, useRef, useState } from "react";
import { Card } from "../sg/card";

function splitLine(line: string): { time: string; message: string } {
  const m = /^(\d{2}:\d{2}:\d{2})\s+([\s\S]*)$/.exec(line);
  if (m) return { time: m[1], message: m[2] };
  return { time: "", message: line };
}

export default function LogTail() {
  const [lines, setLines] = useState<string[]>([]);
  const [paused, setPaused] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  const [copied, setCopied] = useState(false);
  const pausedRef = useRef(false);
  const boxRef = useRef<HTMLDivElement>(null);
  pausedRef.current = paused;

  const curl = "curl -N http://127.0.0.1:8000/logs/stream";

  async function copyCurl() {
    try {
      await navigator.clipboard.writeText(curl);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  useEffect(() => {
    const es = new EventSource("/api/logs");
    es.onmessage = (e) => {
      if (pausedRef.current) return;
      setError(null);
      const line = typeof e.data === "string" ? e.data : "";
      setLines((prev) => [...prev.slice(-199), line]);
    };
    es.onerror = () => {
      setError("Log stream unavailable, retrying");
    };
    return () => es.close();
  }, [nonce]);

  useEffect(() => {
    const el = boxRef.current;
    if (el && !paused) el.scrollTop = el.scrollHeight;
  }, [lines, paused]);

  const pauseSwitch = (
    <button
      type="button"
      role="switch"
      aria-checked={paused}
      onClick={() => setPaused((p) => !p)}
      title={paused ? "Resume live log" : "Pause live log"}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border transition-colors ${
        paused
          ? "border-teal bg-teal"
          : "border-hairline bg-paper hover:border-hairline-strong"
      }`}
    >
      <span className="sr-only">{paused ? "Resume" : "Pause"} log</span>
      <span
        className={`inline-block h-4 w-4 rounded-full shadow transition-transform ${
          paused ? "translate-x-6 bg-white" : "translate-x-1 bg-hairline-strong"
        }`}
      />
    </button>
  );

  if (lines.length === 0) {
    return (
      <Card className="rounded-[24px] p-6">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-muted">
            Service log · waiting for lines
          </p>
          {pauseSwitch}
        </div>
        {/* Liveness: status · retry · copy-as-curl. */}
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-semibold ${
              error
                ? "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300"
                : "border-hairline-soft bg-paper"
            }`}
          >
            {error ? "● ERROR" : "○ AWAITING"}
          </span>
          <button
            type="button"
            onClick={() => setNonce((v) => v + 1)}
            className="font-semibold text-teal hover:underline"
          >
            ↻ retry
          </button>
          <button
            type="button"
            onClick={copyCurl}
            title={curl}
            className="font-mono hover:underline"
          >
            {copied ? "copied ✓" : "</> curl"}
          </button>
        </div>
        {error ? (
          <p className="mt-2 font-mono text-[11px] text-red-700 dark:text-red-300">
            {error}
          </p>
        ) : null}
      </Card>
    );
  }

  return (
    <Card className="rounded-[24px] p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Service
          </p>
          <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
            Service log
          </h3>
          {/* Liveness: status · buffered lines · retry · copy-as-curl. */}
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-semibold ${
                error
                  ? "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300"
                  : paused
                    ? "border-hairline-soft bg-paper"
                    : "border-teal-600/40 bg-teal-600/10 text-teal-700 dark:text-teal-300"
              }`}
            >
              {error ? "● ERROR" : paused ? "❚❚ PAUSED" : "● LIVE"}
            </span>
            <span className="font-mono tabular-nums">{lines.length} lines</span>
            <button
              type="button"
              onClick={() => setNonce((v) => v + 1)}
              className="font-semibold text-teal hover:underline"
            >
              ↻ retry
            </button>
            <button
              type="button"
              onClick={copyCurl}
              title={curl}
              className="font-mono hover:underline"
            >
              {copied ? "copied ✓" : "</> curl"}
            </button>
          </div>
        </div>
        {pauseSwitch}
      </div>
      {error ? (
        <p className="mt-2 font-mono text-[11px] text-red-700 dark:text-red-300">
          {error}
        </p>
      ) : null}
      <div
        ref={boxRef}
        className="mt-3 h-48 overflow-y-auto rounded-2xl border border-hairline-soft bg-paper p-3"
      >
        <ul>
          {lines.map((l, k) => {
            const { time, message } = splitLine(l);
            return (
              <li
                key={k}
                className="flex items-baseline justify-between gap-3 border-t border-hairline py-1.5 text-sm first:border-t-0"
              >
                <span className="min-w-0 flex-1 break-words">{message}</span>
                {time ? (
                  <time className="shrink-0 font-mono text-xs tabular-nums text-muted">
                    {new Date(`1970-01-01T${time}`).toLocaleTimeString()}
                  </time>
                ) : null}
              </li>
            );
          })}
        </ul>
      </div>
      <p className="mt-2 text-xs text-muted">
        {paused
          ? `Paused, holding ${lines.length} lines`
          : `${lines.length} lines buffered, scrolls automatically`}
      </p>
    </Card>
  );
}
