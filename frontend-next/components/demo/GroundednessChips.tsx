"use client";

// B2 — "grounded claim → passage" chips. Calls POST /api/judge/groundedness
// (proxied to workstream A's POST /judge/groundedness). The endpoint may NOT
// exist yet: non-OK upstream statuses render an explicit pending/unreachable
// state. Data is never fabricated.

import { useEffect, useState } from "react";
import { GroundednessSchema, type GroundednessPayload } from "../proof/schemas";
import type { PredictResult } from "./types";
import { CurlButton, LiveBadge, buildGroundednessCurl } from "./widgets";

type Status = "idle" | "loading" | "live" | "pending" | "unreachable";

export default function GroundednessChips({
  result,
  inbound,
}: {
  result: PredictResult | null;
  inbound: string;
}) {
  const [status, setStatus] = useState<Status>("idle");
  const [detail, setDetail] = useState<string | null>(null);
  const [data, setData] = useState<GroundednessPayload | null>(null);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    if (!result?.draft_reply) {
      setStatus("idle");
      setData(null);
      setDetail(null);
      return;
    }
    let cancelled = false;
    setStatus("loading");
    setDetail(null);
    fetch("/api/judge/groundedness", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        brand: result.brand || "virgin",
        text: inbound,
        reply: result.draft_reply,
        passage_ids: result.grounding_passage_ids || [],
      }),
    })
      .then(async (r) => {
        if (!r.ok) {
          // 404/405/501 from FastAPI (or the Next proxy) = endpoint not built
          // yet → pending. Anything else (502/500/network) = unreachable.
          if ([404, 405, 501].includes(r.status)) {
            if (!cancelled) {
              setStatus("pending");
              setDetail(`POST /judge/groundedness returned ${r.status} — endpoint pending (workstream A).`);
            }
          } else if (!cancelled) {
            setStatus("unreachable");
            setDetail(`Groundedness judge unreachable (status ${r.status}).`);
          }
          return;
        }
        const parsed = GroundednessSchema.safeParse((await r.json()) as unknown);
        if (!parsed.success) throw new Error("groundedness payload failed validation");
        if (!cancelled) {
          setData(parsed.data);
          setStatus("live");
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setStatus("unreachable");
          setDetail(`Groundedness judge unreachable (${String(e)}).`);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [result?.request_id, nonce]); // eslint-disable-line react-hooks/exhaustive-deps

  const badge: Record<Status, "AWAITING" | "LOADING" | "LIVE" | "ERROR" | "STALE"> = {
    idle: "AWAITING",
    loading: "LOADING",
    live: "LIVE",
    pending: "STALE",
    unreachable: "ERROR",
  };

  return (
    <section
      aria-label="Groundedness check"
      className="rounded-[24px] border border-hairline bg-card p-6"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
        Groundedness
      </p>
      <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
        Grounded claims → passages
      </h3>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <LiveBadge
          status={badge[status]}
          requestId={result?.request_id}
          onRetry={result ? () => setNonce((v) => v + 1) : undefined}
        />
        {result ? (
          <CurlButton
            cmd={buildGroundednessCurl({
              brand: result.brand || "virgin",
              text: inbound,
              reply: result.draft_reply || "",
              ids: result.grounding_passage_ids || [],
            })}
          />
        ) : null}
      </div>

      {status === "idle" ? (
        <p className="mt-2 text-sm text-muted">Run a prediction to check claim grounding.</p>
      ) : status === "loading" ? (
        <p className="mt-2 font-mono text-xs text-muted">Scoring claims…</p>
      ) : status === "pending" ? (
        <p className="mt-2 rounded-2xl border border-hairline-soft bg-paper p-3 text-sm text-muted">
          Endpoint pending — {detail} No scores are shown rather than estimates.
        </p>
      ) : status === "unreachable" ? (
        <p className="mt-2 text-sm text-red-700 dark:text-red-300">{detail}</p>
      ) : data ? (
        <div className="mt-3">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
            {typeof data.score === "number" ? (
              <span>
                Score <span className="font-mono tabular-nums">{data.score.toFixed(2)}</span>
              </span>
            ) : null}
            {data.model ? <span className="font-mono">{data.model}</span> : null}
          </div>
          <ul className="mt-2 space-y-2">
            {data.claims.map((c, i) => (
              <li
                key={i}
                className="flex flex-wrap items-center gap-2 rounded-2xl border border-hairline-soft bg-paper px-3 py-2 text-sm"
              >
                <span
                  aria-label={c.supported ? "supported" : "unsupported"}
                  className={`inline-block size-2 shrink-0 rounded-full ${c.supported ? "bg-teal" : "bg-red-500"}`}
                />
                <span className="min-w-0 flex-1">{c.text}</span>
                {c.passage_id ? (
                  <span className="shrink-0 rounded-full border border-hairline-soft bg-card px-2 py-0.5 font-mono text-[11px]">
                    → {c.passage_id}
                  </span>
                ) : (
                  <span className="shrink-0 text-[11px] text-muted">no passage cite</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
