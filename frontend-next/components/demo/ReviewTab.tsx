"use client";

// B1 — "Review" tab: the existing review inbox stays a full page at /review
// (untouched); this tab links to it so all current features stay reachable
// from the shell.

export default function ReviewTab() {
  return (
    <div className="mt-5 space-y-5">
      <section className="rounded-[24px] border border-hairline bg-card p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal">
          Human loop
        </p>
        <h3 className="mt-1 font-display text-xl font-semibold tracking-[-0.03em]">
          Review inbox
        </h3>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">
          Escalated replies queue for a human decision. Approve or escalate with a
          rationale; every action lands in the audit trail. The inbox is a full
          page so reviewers get room to work.
        </p>
        <div className="mt-4">
          <a
            href="/review"
            className="inline-flex rounded-full bg-teal px-5 py-2 text-sm font-semibold text-[#03211f] transition-opacity hover:opacity-85"
          >
            Open review inbox →
          </a>
        </div>
        <p className="mt-3 text-xs text-muted">
          Demo path: run a query in Try it → escalated runs appear in the queue →
          approve → audit trail visible on /review.
        </p>
      </section>
    </div>
  );
}
