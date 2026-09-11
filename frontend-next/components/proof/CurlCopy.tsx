"use client";

import { useMemo, useState } from "react";
import { Card } from "../sg/card";

export default function CurlCopy({ text, brand }: { text: string; brand: string }) {
  const [copied, setCopied] = useState(false);

  const cmd = useMemo(() => {
    const payload = JSON.stringify({ text, brand }).replace(/'/g, "'\\''");
    return `curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '${payload}'`;
  }, [text, brand]);

  async function copy() {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
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
    <Card className="rounded-[24px] p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
            Replay
          </p>
          <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
            Replay as curl
          </h3>
        </div>
        {/* Local secondary button (sg Button omits children in its props, so a
            local fallback keeps the same SmartGrey pill styling). */}
        <div className="flex flex-col items-end gap-1">
          <p className="text-xs text-muted">
            Local API · 127.0.0.1:8000 — paste in your own terminal, bypasses
            this UI.
          </p>
          <button
            type="button"
            onClick={copy}
            className="inline-flex h-8 items-center justify-center rounded-full border border-hairline bg-card px-4 text-sm font-medium text-ink hover:border-hairline-strong hover:bg-paper"
          >
            {copied ? "Copied" : "Copy curl"}
          </button>
        </div>
      </div>
      <pre className="mt-3 max-h-32 overflow-y-auto whitespace-pre-wrap break-all rounded-2xl border border-hairline-soft bg-paper p-3 font-mono text-[11px] leading-relaxed">
        {cmd}
      </pre>
    </Card>
  );
}
