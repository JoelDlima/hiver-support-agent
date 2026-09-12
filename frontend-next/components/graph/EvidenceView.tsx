"use client";

import { useMemo, useState } from "react";
import type { Passage } from "../../lib";

export type EvidenceViewProps = {
  draftReply: string;
  groundingIds: string[];
  passages: Passage[];
  /** True while /api/passages is in flight. */
  loading?: boolean;
  /** Set when /api/passages failed and no inspect fallback was available. */
  loadError?: string | null;
};

type Claim = { id: string; text: string };
type Link = { passageIdx: number; overlap: number };

const STOP = new Set(
  "a,an,the,and,or,but,if,then,else,for,to,of,in,on,at,by,with,from,as,is,are,was,were,be,been,it,its,this,that,these,those,you,your,we,our,they,their,he,she,his,her,i,me,my,do,does,did,can,could,should,would,will,just,please,here,there,what,when,where,who,how,not,no,yes,up,out,so,very,more,most,any,all,have,has,had".split(
    ","
  )
);

function tokenize(s: string): string[] {
  return (s.toLowerCase().match(/[a-z0-9']+/g) || []).filter((w) => !STOP.has(w) && w.length > 1);
}

/** Split a live draft into sentence-level claims. Pure function of the draft text. */
export function splitClaims(draft: string, cap = 8): Claim[] {
  const parts = (draft || "").match(/[^.!?\n]+[.!?…]?/g) || [];
  return parts
    .map((p) => p.trim())
    .filter((p) => p.length > 0)
    .slice(0, cap)
    .map((text, i) => ({ id: `C${i + 1}`, text }));
}

/** Token-overlap between a claim and a passage, computed live from their texts. */
export function claimPassageOverlap(claim: string, passageText: string): number {
  const c = tokenize(claim);
  if (c.length === 0 || !passageText) return 0;
  const p = new Set(tokenize(passageText));
  if (p.size === 0) return 0;
  let hit = 0;
  for (const w of new Set(c)) if (p.has(w)) hit += 1;
  return hit / new Set(c).size;
}

function formatScore(v: unknown): string {
  return typeof v === "number" && Number.isFinite(v) ? v.toFixed(3) : "—";
}

export default function EvidenceView({
  draftReply,
  groundingIds,
  passages,
  loading,
  loadError,
}: EvidenceViewProps) {
  const [selClaim, setSelClaim] = useState<number | null>(null);
  const [selPassage, setSelPassage] = useState<number | null>(null);

  const ranked = useMemo(
    () => [...passages].sort((a, b) => (b.score ?? 0) - (a.score ?? 0)),
    [passages]
  );
  const grounded = useMemo(() => new Set(groundingIds || []), [groundingIds]);
  const claims = useMemo(() => splitClaims(draftReply), [draftReply]);

  // Bipartite links: claim -> passages ranked by live token overlap.
  const links = useMemo<Map<number, Link[]>>(() => {
    const m = new Map<number, Link[]>();
    claims.forEach((c, ci) => {
      const scored = ranked
        .map((p, pi) => ({ passageIdx: pi, overlap: claimPassageOverlap(c.text, p.text || "") }))
        .filter((l) => l.overlap > 0)
        .sort((a, b) => b.overlap - a.overlap)
        .slice(0, 3);
      m.set(ci, scored);
    });
    return m;
  }, [claims, ranked]);

  const linkedPassages = selClaim !== null ? new Set((links.get(selClaim) || []).map((l) => l.passageIdx)) : null;
  const linkedClaims =
    selPassage !== null
      ? new Set(
          [...links.entries()].filter(([, ls]) => ls.some((l) => l.passageIdx === selPassage)).map(([ci]) => ci)
        )
      : null;

  return (
    <div className="space-y-4">
      {/* Ranked list is primary: every row is a live /passages row. */}
      <div>
        <p className="text-xs font-medium uppercase tracking-widest text-muted">
          Ranked passages · live scores
        </p>
        {loading ? (
          <p className="mt-2 text-sm text-muted">Loading passages…</p>
        ) : ranked.length === 0 ? (
          <div className="mt-2 rounded-2xl border border-hairline-soft bg-paper p-3">
            <p className="text-sm text-muted">
              {loadError || "No passages returned for this run."}{" "}
              {groundingIds.length > 0 ? (
                <>
                  Grounding ids from /predict:{" "}
                  <span className="font-mono text-xs">{groundingIds.join(", ")}</span> (scores
                  unavailable — not invented here).
                </>
              ) : null}
            </p>
          </div>
        ) : (
          <ol className="mt-2 space-y-2 text-sm">
            {ranked.map((p, i) => {
              const dim = linkedPassages !== null && !linkedPassages.has(i);
              const hot = selPassage === i;
              return (
                <li key={`${p.tweet_id}-${i}`}>
                  <button
                    type="button"
                    onClick={() => setSelPassage(hot ? null : i)}
                    aria-pressed={hot}
                    className={`w-full rounded-2xl border bg-paper p-3 text-left transition-opacity ${
                      hot ? "border-teal" : "border-hairline-soft"
                    } ${dim ? "opacity-40" : ""}`}
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="min-w-0 truncate">
                        <span className="mr-2 font-mono text-xs font-semibold tabular-nums text-teal">
                          #{i + 1}
                        </span>
                        <span className="truncate font-mono text-xs">{p.tweet_id}</span>
                      </span>
                      <span className="shrink-0 font-mono text-xs tabular-nums text-muted">
                        {formatScore(p.score)}
                      </span>
                    </div>
                    {p.text ? (
                      <p className="mt-1 whitespace-pre-wrap text-[13px] leading-relaxed">{p.text}</p>
                    ) : (
                      <p className="mt-1 text-[13px] italic text-muted">
                        text unavailable — id only, from grounding list
                      </p>
                    )}
                    {grounded.has(p.tweet_id) ? (
                      <span className="mt-1.5 inline-flex items-center rounded-full bg-teal px-2 py-0.5 text-[11px] font-semibold text-white">
                        cited by draft
                      </span>
                    ) : null}
                  </button>
                </li>
              );
            })}
          </ol>
        )}
      </div>

      {/* Bipartite claim -> passage view, derived live from draft + passages. */}
      <div>
        <p className="text-xs font-medium uppercase tracking-widest text-muted">
          Claim ↔ passage links · token overlap
        </p>
        {claims.length === 0 ? (
          <p className="mt-2 text-sm text-muted">No draft yet — run a prediction to split claims.</p>
        ) : ranked.length === 0 ? (
          <p className="mt-2 text-sm text-muted">Links need passages — none available for this run.</p>
        ) : (
          <div className="mt-2 grid grid-cols-1 gap-3 md:grid-cols-2">
            <div className="space-y-2">
              {claims.map((c, ci) => {
                const dim = linkedClaims !== null && !linkedClaims.has(ci);
                const hot = selClaim === ci;
                const ls = links.get(ci) || [];
                return (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => {
                      setSelClaim(hot ? null : ci);
                      setSelPassage(null);
                    }}
                    aria-pressed={hot}
                    className={`w-full rounded-2xl border bg-paper p-3 text-left text-[13px] leading-relaxed ${
                      hot ? "border-teal" : "border-hairline-soft"
                    } ${dim ? "opacity-40" : ""}`}
                  >
                    <span className="mr-2 font-mono text-[11px] font-semibold text-teal">{c.id}</span>
                    {c.text}
                    <span className="mt-1.5 flex flex-wrap gap-1">
                      {ls.length === 0 ? (
                        <span className="text-[11px] italic text-muted">no overlapping passage</span>
                      ) : (
                        ls.map((l) => (
                          <span
                            key={l.passageIdx}
                            className="inline-flex items-center rounded-full border border-hairline-soft bg-card px-2 py-0.5 font-mono text-[11px] tabular-nums text-muted"
                          >
                            → P{l.passageIdx + 1} {(l.overlap * 100).toFixed(0)}%
                          </span>
                        ))
                      )}
                    </span>
                  </button>
                );
              })}
            </div>
            <div className="space-y-2">
              {ranked.map((p, pi) => {
                const dim = linkedPassages !== null && !linkedPassages.has(pi);
                return (
                  <div
                    key={`col-${p.tweet_id}-${pi}`}
                    className={`rounded-2xl border border-hairline-soft bg-paper p-3 ${
                      dim ? "opacity-40" : ""
                    }`}
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="font-mono text-[11px] font-semibold text-teal">P{pi + 1}</span>
                      <span className="truncate font-mono text-[11px]">{p.tweet_id}</span>
                      <span className="shrink-0 font-mono text-[11px] tabular-nums text-muted">
                        {formatScore(p.score)}
                      </span>
                    </div>
                    <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-card">
                      <div
                        className="h-full rounded-full bg-teal"
                        style={{ width: `${Math.round(Math.min(Math.max(p.score ?? 0, 0), 1) * 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        <p className="mt-2 text-[11px] text-muted">
          Click a claim or ranked passage to highlight its links. Overlap is measured live from
          the draft and passage texts — no stored edges.
        </p>
      </div>
    </div>
  );
}
