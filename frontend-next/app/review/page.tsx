"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ReviewRow, { type ReviewItem } from "../../components/review/ReviewRow";
import ThresholdSlider from "../../components/review/ThresholdSlider";

type Stats = { total: number; by_status: Record<string, number> } | null;

export default function ReviewPage() {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [stats, setStats] = useState<Stats>(null);
  const [brand, setBrand] = useState<string>("");
  const [reviewer, setReviewer] = useState("demo-reviewer");
  const [rationale, setRationale] = useState("");
  const [sel, setSel] = useState(0);
  const [threshold, setThreshold] = useState(0.45);
  const [onlyBelow, setOnlyBelow] = useState(false);
  const [busyIds, setBusyIds] = useState<ReadonlySet<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const selRef = useRef(0);
  selRef.current = sel;

  const load = useCallback(async () => {
    try {
      const qs = new URLSearchParams({ status: "PENDING", limit: "50" });
      if (brand) qs.set("brand", brand);
      const r = await fetch(`/api/review?${qs.toString()}`);
      if (!r.ok) throw new Error(`queue ${r.status}`);
      const j = await r.json();
      setItems(Array.isArray(j.items) ? j.items : []);
      setApiOk(true);
      setSel((s) => Math.min(s, Math.max((j.items || []).length - 1, 0)));
    } catch (e) {
      setApiOk(false);
      setError(`Queue load failed: ${e}`);
    }
    try {
      const s = await fetch("/api/review/stats");
      if (s.ok) setStats(await s.json());
    } catch {
      /* stats advisory */
    }
  }, [brand]);

  useEffect(() => {
    load();
    const id = window.setInterval(load, 5000);
    return () => window.clearInterval(id);
  }, [load]);

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  async function act(id: string, kind: "approve" | "edit" | "reject", finalText?: string) {
    if (busyIds.has(id)) return;
    setBusyIds((prev) => new Set(prev).add(id));
    setError(null);
    try {
      const r = await fetch(`/api/review/${encodeURIComponent(id)}/${kind}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reviewer: reviewer || "reviewer",
          rationale,
          ...(kind === "edit" ? { final_text: finalText || "" } : {}),
        }),
      });
      if (!r.ok) {
        const j = await r.json().catch(() => ({}));
        throw new Error((j as { detail?: string }).detail || `status ${r.status}`);
      }
      await load();
    } catch (e) {
      setError(`Action failed: ${e}`);
    } finally {
      setBusyIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  // Keyboard triage: j/k move, r approve, s reject, e handled per-row via tab.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const tag = (document.activeElement?.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") return;
      // Avoid accidental approve/reject when a button has focus (e.g. after click + pressing r/s).
      if (tag === "button" && e.key !== "j" && e.key !== "k") return;
      if (e.key === "j") setSel((s) => Math.min(s + 1, Math.max(items.length - 1, 0)));
      else if (e.key === "k") setSel((s) => Math.max(s - 1, 0));
      else if (e.key === "r" || e.key === "a") {
        const it = items[selRef.current];
        if (it) act(it.id, "approve");
      } else if (e.key === "s" || e.key === "x") {
        const it = items[selRef.current];
        if (it) act(it.id, "reject");
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items]);

  const pending = items.length;
  const belowCount = items.filter((it) => Number(it.intent_confidence ?? 1) < threshold).length;
  const visible = onlyBelow
    ? items.filter((it) => Number(it.intent_confidence ?? 1) < threshold)
    : items;

  return (
    <div className="min-h-screen bg-canvas font-sans text-ink">
      <main className="mx-auto max-w-6xl px-4 py-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
          Hiver Support Intelligence
        </p>
        <h1 className="mt-1 font-display text-4xl font-bold tracking-[-0.03em]">Review queue</h1>
        <p className="mt-1 text-sm text-muted">
          Human-in-the-loop inbox for agent escalations. Polls live every 5s.{" "}
          {apiOk === false ? "API offline — start FastAPI on :8000." : ""}
        </p>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <div className="flex rounded-full border border-hairline-soft bg-paper p-1">
            {["", "virgin", "apple"].map((b) => (
              <button
                key={b || "all"}
                onClick={() => setBrand(b)}
                aria-pressed={brand === b}
                className={`rounded-full px-4 py-1.5 text-sm font-medium ${
                  brand === b ? "bg-teal font-semibold text-[#03211f]" : "text-muted hover:opacity-75"
                }`}
              >
                {b === "" ? "All brands" : b === "virgin" ? "Virgin Trains" : "Apple Support"}
              </button>
            ))}
          </div>
          <input
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="reviewer"
            aria-label="Reviewer name"
            className="rounded-full border border-hairline-soft bg-paper px-4 py-1.5 text-sm"
          />
          <input
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            placeholder="rationale (stored in audit)"
            aria-label="Rationale"
            className="min-w-52 flex-1 rounded-full border border-hairline-soft bg-paper px-4 py-1.5 text-sm"
          />
        </div>

        {stats ? (
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            {(["PENDING", "APPROVED", "APPROVED_WITH_EDITS", "REJECTED", "EXPIRED"] as const).map(
              (s) => (
                <span
                  key={s}
                  className="inline-flex items-center rounded-full border border-hairline-soft bg-paper px-2.5 py-1 font-mono tabular-nums"
                >
                  {s}: {stats.by_status?.[s] ?? 0}
                </span>
              )
            )}
          </div>
        ) : null}

        <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-[1fr_320px]">
          <section className="space-y-4">
            <p className="text-sm text-muted">
              {pending === 0
                ? "Inbox empty — enqueue an escalation via POST /review/enqueue or the triage page."
                : `${pending} pending · ${belowCount} below threshold ${threshold.toFixed(2)} · j/k move · r approve · s escalate · e edit inline`}
            </p>
            <label className="flex items-center gap-2 text-sm text-muted">
              <input
                type="checkbox"
                checked={onlyBelow}
                onChange={(e) => setOnlyBelow(e.target.checked)}
                className="size-4"
              />
              Show only below-threshold rows (client-side display filter)
            </label>
            {error ? <p className="text-sm text-red-700 dark:text-red-300">{error}</p> : null}
            {visible.map((it) => {
              const i = items.indexOf(it);
              const below = Number(it.intent_confidence ?? 1) < threshold;
              return (
                <div key={it.id} onClick={() => setSel(i)}>
                  {below ? (
                    <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-amber-700 dark:text-amber-300">
                      Below threshold {threshold.toFixed(2)}
                    </p>
                  ) : null}
                  <ReviewRow
                    item={it}
                    selected={i === sel}
                    now={now}
                    reviewer={reviewer}
                    onAction={act}
                  />
                </div>
              );
            })}
          </section>
          <aside className="space-y-4">
            <ThresholdSlider value={threshold} onChange={setThreshold} />
            <div className="rounded-[24px] border border-hairline bg-card p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
                Handoff
              </p>
              <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
                Warm transfer
              </h3>
              <p className="mt-2 text-sm text-muted">
                Every row carries a transfer payload (transcript, intent/conf, reason code, draft,
                next step, SLA due) at <span className="font-mono">/review/[id]/transfer</span> —
                the agent hands off, the human never re-asks.
              </p>
            </div>
          </aside>
        </div>
      </main>
      <footer className="border-t border-line">
        <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted">
          Local backend FastAPI 127.0.0.1:8000 · browser → /api/review/* → FastAPI · audit
          append-only.
        </p>
      </footer>
    </div>
  );
}
