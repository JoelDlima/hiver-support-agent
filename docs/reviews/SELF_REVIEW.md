# SELF_REVIEW — Brutal Red-Team (2026-09-11)

Auditor: self red-team. Scope: `.` end-to-end. Method: read
`docs/REPORT_VIRGIN_6PAGE.md`, `docs/FINAL_REVIEW.md`,
`evaluation/virgin/FAILURE_TESTS.md`, `evaluation/virgin/BASELINE_VS_FINAL.md`,
`evaluation/virgin/JUDGE_AGREEMENT.md`, `evaluation/PER_INTENT.md`; ran
`pytest tests -q` (15 passed), TestClient smoke on both brands (10 probes),
`py_compile` on frontend/backend/agent, plus targeted lexicon/normalization
probes. Verdicts describe CURRENT code. No marketing.

## Verification log (reproduced, not quoted)

- `pytest tests -q` → **15 passed** (9.75s). Claim "10 pass" in README is stale (now 15).
- TestClient `/predict` both brands: virgin delay → `delay_claim/auto_handle`;
  apple battery → `battery_power/auto_handle`; empty → `other/escalate/unresolvable`;
  injection → `escalate/unresolvable`; flame (both brands) → `escalate/legal_safety`. All PASS.
- **Reproduced live FAILs from FAILURE_TESTS.md**: `packed` crowd →
  `other/auto_handle` (F4a FAIL confirmed); French stranded →
  `other/auto_handle` in English (F5 FAIL confirmed); repeat-refund (~2 months) →
  `ticket_change_refund/auto_handle` conf 0.919 (F6 FAIL confirmed).
- **New finding — F2 PASS is wording-fragile**: the filed F2 probe
  ("…to Birmingham…still running on time") → `timetable_platform`, but
  "is the 21:03 train from Euston still running?" → `other/auto_handle` (0.897)
  and "when is the next train from Euston?" → `other` (0.933). Core timetable
  use-case misroutes on natural phrasings.
- **New finding — `<BRAND-KB:xxx>` leaks to users**: every template ends with a
  literal `<BRAND-KB:delay|amend|…>` token and `draft_grounded` returns it
  verbatim; smoke drafts show it in `draft_reply`. Debug token ships to customers.
- **New finding — primary-brand signal destroyed**: `normalize()` maps only
  `@AppleSupport→<BRAND>`; `@VirginTrains→<USER>`. The primary brand's mention
  is erased at the first pipeline step.
- **New finding — money lexicon misses virgin money words**:
  `has_money` ignores "compensation", "admin fee", "delay repay" (probe:
  all False). Combined with the `conf<0.7` gate (virgin money texts score
  0.75–1.0), the money gate is near-dead when the retriever is present.
  With `retriever=None` the same inputs escalate via `no_grounding` — i.e. the
  serving path with retrieval is LESS safe than without on confident errors.
- **New finding — frontend unrunnable in shipped venv**: `streamlit` and
  `openai` both resolve to `None` in `.venv`. `py_compile` passes,
  `import streamlit` fails. The demo cannot launch; the Groq client can never
  load (fail-closed still holds, but the `groq` path is unexercised code).
- **Cold start vs claimed latency**: first `/predict` per brand cost 808ms
  (virgin) / 1341ms (apple) — joblib loads on first call. Warm calls are
  11–15ms (virgin) / ~49ms (apple). "p50 180ms" is a warm-dev number, not a
  first-hit or prod number.

## Scores (PS rubric, 0–10, harsh)

| # | Rubric | Score | Why |
|---|---|---|---|
| 1 | real-data handling | 6 | Real TWCS 2.8M + Virgin 65k union, dedup, KB/index built, preprocessing + time-freeze + burst bias disclosed. Deduct: 2.32% slice with 91% Oct–Nov-2017 burst; non-English/cross-brand excluded; no PII redaction; `normalize` erases the primary brand mention. |
| 2 | product decisions | 5 | Right instincts (templates>LLM keyless, no framework, no vector DB, DM triage, fail-closed Groq). Deduct: money gate dead-on-confident, timetable brittle, FR gate missing in serving path, `<BRAND-KB>` leak, lexicon-shaped safety. Good taste, shipping bugs. |
| 3 | complete system | 5 | Classify→retrieve→draft→escalate genuinely live on both brands with /healthz /readyz /metrics; 15 tests green; models+indexes in repo. Deduct: frontend unrunnable (no streamlit), Groq path untested (no openai), no rate-limit/load/Docker evidence, cold-start 10× claimed latency. |
| 4 | scientific eval | 5 | Real structure: dual golden, trivial/simple/final, ablation, retrieval note, per-intent + confusion, judge agreement, virgin human-200 > Apple human-60. Deduct: single annotator, no inter-annotator κ, 140/200 "assisted" labels anchor to weak rules (virgin weak-vs-human κ 0.772 vs Apple 0.465 smells of assistance bias), safety n=3, LLM judge unrun, retrieval "recall@k = 1.000" is a saturated coverage proxy with a non-discriminating 0.08 gate. |
| 5 | failure honesty | 8 | Best dimension. Real FAILs filed (3/9 virgin, F3 Apple), hypotheses queued, F3a "passes via over-escalation accident" admitted, single-annotator caveat printed. Deduct: F2 filed as PASS on cherry-picked wording; "5 PASS / 1 PARTIAL / 3 FAIL" still flatters (F1/F2 pass on draft safety while riding keyword rails). |
| 6 | metric honesty | 7 | Circularity warnings everywhere, "do not cite weak-200", safety-n=3 flagged NOT claimable, groundedness flagged template-shaped, train-acc flagged circular, latency flagged dev-CPU. Deduct: README headline still leads with 0.665/0.673 before caveats; groundedness 0.930 sits in headline tables with the warning paragraphs away; FINAL_REVIEW's "0 FAILs" grades the audit's disclosure, not the system — the system has open FAILs. |
| 7 | decision clarity | 7 | 15+5 decisions each with why + revisit trigger; ship bar explicit (safety recall ≥0.90, wκ ≥0.60); "not shippable this week" stated. Deduct: Groq ship criteria gate a path that has never run; virgin "pending V-EVAL" numbers sit beside Apple measured numbers in ways a fast reader will confuse. |

## Top 8 defects (severity + fix cost S/M/L)

| # | Defect | Severity | Fix cost | Fix |
|---|---|---|---|---|
| D1 | Money gate dead on confident texts: `conf<0.7` + `has_money` missing compensation/admin-fee/delay-repay → money recall 0.350 (7/20); repeat-refund auto-handled at conf 0.92 (reproduced live) | HIGH (financial) | M | Drop `conf<0.7` for money intents and/or add repeat/duration cues (again, months, £, admin fee); extend `has_money` to rail vocab; regression-probe F6 (H6) |
| D2 | Learned model loses to its own teacher on EVERY intent: virgin human-200 Table C, all 10 deltas negative (accessibility 0.848→0.421, other 0.640→0.494, fare 0.947→0.774); Apple same pattern (0.517→0.433). The LogReg generalizes to worse-everywhere | HIGH (architecture) | L | Supervised retrain on human labels (double-labeled 200+); weak bootstrap is at its ceiling — stop tuning around it |
| D3 | Colloquial crowding unprotected: packed/rammed/crammed → `other/auto_handle` while `overcrowding` escalates (reproduced live; 414 pool hits in the tail). Safety is lexicon-shaped, not meaning-shaped | HIGH (safety) | S | Extend SAFETY_ADDONS + complaint KEYWORDS (H4: packed/rammed/crammed/crushed-standing), add F4a regression probe |
| D4 | French/ES stranded passenger gets English auto-reply (reproduced live). FR gate lives only in the golden adjudicator, not the serving path; safety cognates EN-only | HIGH (safety) | S | Port non-English gate + multilingual safety cognates (bloqué/varado/coincé) into `handle` (H5); pool has 6 hits, severity high |
| D5 | Timetable intent brittle on natural phrasings: "when is the next train from Euston?" → `other` 0.933; "still running?" → `other` 0.897 (both auto-handled with generic triage). Filed F2 PASS does not survive rephrasing | HIGH (core use-case) | M | Expand timetable KEYWORDS (still running, next train, when is/are, direct, stops at) + question-shape fallback; add both phrasings as regression probes |
| D6 | `<BRAND-KB:xxx>` internal tag shipped in every user-facing draft (confirmed in smoke output) | MEDIUM-HIGH (customer-visible) | S | Strip `<BRAND-KB:…>` at `draft_grounded` return (or move to signals); assert no `<` `>` tokens in draft tests |
| D7 | `normalize()` erases primary-brand signal (`@VirginTrains→<USER>`; only `@AppleSupport→<BRAND>`); classifier/retriever train-serve on degraded input for the primary brand | MEDIUM | S | Add VirginTrains (and generic `@\w+`-brand) handling to `normalize`; re-verify virgin intent deltas |
| D8 | "Complete system" overclaimed: streamlit + openai absent from venv (demo cannot launch, Groq client can never load); cold-start 800–1300ms vs claimed p50 180ms; no rate-limit, load test, or Docker run evidence | MEDIUM | M | Pin/install or remove the claims; report cold vs warm latency separately; add minimal load + fresh-clone repro log (REPRO_CHECK already admits the gaps — close them) |

Honorable-mention non-defects the docs already own (not re-listed above):
single-annotator labels, safety n=3, heuristic groundedness circularity, burst-month
slice, Groq unrun. Credit for disclosure; they still block ship.

## Verdict: NOT-SHIP

The system fails its own ship bar by ~2× (escalation recall 0.459 virgin /
0.500 Apple vs required ≥0.90; money recall 0.350; safety slice n=3 unpowered),
loses intent accuracy to a keyword list on all 10 virgin intents, and has three
safety/money FAILs I reproduced in under a minute each via the public API
(packed-crowd, French-stranded, repeat-refund) plus two new ones (timetable
rephrase, brand-tag leak). Single-annotator, 70%-assisted labels with a
suspiciously high weak-vs-human κ (0.772 vs Apple's 0.465) mean even the
headline 0.665 is assistance-flattered. This is a strong, honest prototype —
not a shippable agent.

Narrow ship-with-caveats path (assistive triage only, human must see every
money/safety/non-English case): fix D1+D3+D4+D5+D6+D7 (all S/M, days not weeks),
default `packed`/non-English/repeat-money to escalate, strip the tag leak,
double-label the 200 with adjudication + κ, and re-report. Supervised retrain
(D2) and load/Docker evidence (D8) follow before any autonomous handling.

## Why judges would / wouldn't pick this over 10000

Would pick: almost nobody else files open FAILs with repro commands, prints
their own 1.000 and says "do not cite it", publishes 39–41 flips with κ
ceilings, ablates their retriever, admits "passes via over-escalation
accident", and ships a $0-CPU both-brands live API with per-brand metrics.
The honesty infrastructure (dual golden, confusion tables, gated LLM judge,
fail-closed design, decision log with revisit triggers) is the moat — it is
rare and it is real.

Wouldn't pick: the headline numbers lose to the team's own keyword baseline on
every intent; escalation recall is half the self-set ship bar with money recall
at 0.35; three safety/money failures reproduce live in seconds; labels are
single-annotator and assistance-flattered; retrieval "recall 1.000" measures a
saturated proxy, not relevance; groundedness 1.000 rewards template shape;
the frontend cannot launch in the shipped venv; customer-facing drafts leak
internal tags. A judge who runs five probes instead of reading the report will
find all of this before finishing their coffee.
