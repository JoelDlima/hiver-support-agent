# Hiver — Hackathon Win Plan (implementation-ready)

**Goal:** close the reviewer-attackable gaps (judge gate advisory-only, +0.005 intent delta story,
single-annotator gold) and turn the demo into a guided grading-rubric walkthrough.
**Constraint:** proof over system; no mocked numbers anywhere; every new claim ships with a CSV/MD artifact.
**Date:** 2026-09-15. **Stack:** FastAPI single-file backend (`backend/main.py`),
Next.js 14 frontend (`frontend-next/`), pytest suite (`tests/`), venv at `.venv`.

## Workstream A — Backend proof endpoints (owner: backend agent)

**Files owned:** `backend/main.py` (APPEND-ONLY new endpoints + helpers; do not refactor existing
handlers), `scripts/run_groundedness_judge.py` (new), `scripts/run_retrieval_ablation.py` (new),
`evaluation/virgin/JUDGE_AGREEMENT_V3.md` (new), `evaluation/virgin/RETRIEVAL_ABLATION.md` (new).
Do NOT touch `frontend-next/` or existing eval CSVs.

### A1. `POST /judge/groundedness` + V3 agreement study (highest leverage)
- **Why:** `/judge` verdict agreement missed the gate twice (v1 κ 0.253, v2 negative → advisory-only).
  Groundedness-only judgments (is each draft claim entailed by cited passages?) get far higher
  human–LLM agreement than open verdicts. A passing groundedness gate repairs the "prove it works" story.
- **Implement:** new `GroundIn {brand, text, reply, passage_ids?}` model; reuse `_collect_passages`
  and `_build_llm_block` patterns; deterministic claim-split (sentence split) + per-claim
  entail/passage-cite check via existing Groq hook (`openai/gpt-oss-20b`, temp 0, fallback
  `qwen/qwen3.8-27b` per README); response `{claims: [{text, supported, passage_id}], score, model}`.
  Add `frontend-next/app/api/judge/groundedness/route.ts`? NO — that is workstream B's file; backend
  agent only documents the contract here.
- **Study:** `scripts/run_groundedness_judge.py` scores `evaluation/virgin/golden_human_200.csv`
  (reuse final-system drafts from `results_human200.csv` where present; else draft live) and compares
  against human groundedness labels; write `JUDGE_AGREEMENT_V3.md` with κ + 95% CI, n, model, temp,
  and an explicit PASS/FAIL vs the `wκ ≥ 0.60` ship gate. If it misses, report honestly with CIs —
  do not tune the rubric to the test set.
- **Accept:** `pytest tests/test_virgin_fixes.py` green; endpoint returns schema-valid JSON on 5 probe
  texts; V3 MD exists with κ, CI, n, and gate verdict.

### A2. `POST /eval/retrieval-ablation` (reframes the thin +0.005 delta)
- **Why:** final beats simple by +0.005 acc on intent; the real wins are groundedness (4.21 vs 2.33)
  and esc F1 (+0.529). Prove groundedness comes from retrieval: k=1 vs k=5, keyword-NN vs virgin-NN,
  with/without thread-window context.
- **Implement:** `AblIn {brand="virgin", k_list=[1,5], arms=["keyword","virgin_nn"], context_window=[0,2]}`;
  reuse `_make_retriever_for_brand` / `_collect_passages`; return per-arm
  `{recall_proxy, groundedness_mean, groundedness_ge4_rate, p50_ms, p95_ms}` on a fixed 60-item
  slice (`golden_human_60.csv`) + write `RETRIEVAL_ABLATION.md` with the table.
- **Accept:** numbers reproduce via script; no new data files mutated; docs table matches endpoint output.

### A3. `GET /eval/compare?brands=virgin,apple` (transfer matrix in one call)
- **Why:** "does it generalize?" is the predictable reviewer question; Virgin primary + Apple transfer
  is currently scattered across docs.
- **Implement:** run existing eval harness per brand (reuse `scripts/run_virgin_eval.py` logic paths,
  Apple equivalents already in repo); return `{brand: {intent_acc, macro_f1, esc_f1, ground_mean, n}}`.
  Cache results to `evaluation/compare_cache.json` (new file OK) so demo never recomputes.
- **Accept:** response < 2s on cache hit; values match `BASELINE_VS_FINAL.md` tables within rounding.

### A4. Offline fallback flag (demo insurance)
- **Why:** live demo must survive dead Groq keys / 429s.
- **Implement:** `PredictIn.offline: bool = False` (+ `HIVer_OFFLINE=1` env); when set, skip LLM block,
  return template-only draft with `"offline": true` in response + inspect record; frontend shows banner
  (B's job). Never silently degrade — the flag is always echoed.
- **Accept:** existing tests green + new test: offline predict returns 200 with `offline: true`, no HTTP
  calls attempted (assert via monkeypatched Groq client or env kill).

## Workstream B — Frontend demo restructure (owner: frontend agent)

**Files owned:** `frontend-next/app/page.tsx`, `frontend-next/components/*` (new subfolders OK),
`frontend-next/app/api/*` (new proxy routes ONLY: `judge/groundedness`, `eval/ablation`, `eval/compare`;
mirror existing `route.ts` proxy style). Do NOT touch `backend/` or `evaluation/`.

### API contracts (backend builds these in parallel; code defensively)
- `POST /judge/groundedness` → `{claims: [{text, supported, passage_id}], score, model}`.
  Until live: component renders "endpoint pending" state, never fake data.
- `POST /eval/retrieval-ablation` → `{arms: [{name, k, groundedness_mean, ge4_rate, p50_ms}]}`.
- `GET /eval/compare?brands=virgin,apple` → `{results: {virgin: {...}, apple: {...}}}`.
- `POST /predict` gains `offline: bool`; response gains `offline: bool`.

### B1. Three-tab demo shell (`Try it` / `Proof` / `Review`)
- Refactor `page.tsx` (48KB single component) into tab container + three section components under
  `components/demo/` (new): `TryIt.tsx` (query hero → result), `ProofTab.tsx`, keep existing review
  page linked as third tab. Preserve all existing imports/components (Inspector, EvalRunner, PipelineFlow…).
  Grading-rubric order inside Proof tab: baselines → golden/agreement → failure gallery → latency.
- **Accept:** `npm run build` passes; no existing component deleted; all current features reachable.

### B2. Proof receipt per query
- Extend result panel: intent + ConfidenceBars (exists) + retrieved passage IDs (from `/passages` shape)
  + template id + escalation reason + `request_id` linking to existing `Inspector` (`/inspect/{id}`).
  Render "grounded: claim → passage" chips when `/judge/groundedness` is live.
- **Accept:** receipt renders for virgin + apple; offline responses show "OFFLINE — template only" banner.

### B3. Failure-mode gallery (Proof tab)
- 3–4 side-by-side before/after cards sourced from `evaluation/virgin/FAILURE_TESTS.md`
  (F1 DR30 bands, F3b PII gate, + 1–2 more): input → old behavior → fixed behavior → probe status.
  Hardcode from the MD (static content, not fetched) with a link to the file.
- **Accept:** content matches FAILURE_TESTS.md verbatim claims (9/9 pass).

### B4. Brand switcher + compare strip
- Virgin/Apple toggle driving existing predict flow (`brand` param already exists) + compare strip
  rendering `/eval/compare` table. Apple numbers must match docs; label Apple as "transfer evidence."
- **Accept:** switching brand re-runs hero query; compare values equal doc tables.

### B5. Liveness/latency pill
- Header pill from `/healthz` + `/metrics`: "backend live • p50 Xms"; stale-state styling exists
  (`STAGE_PILL`, `STALE_AFTER_MS`) — reuse. "100% local inference" strip; offline banner when
  `offline: true`.
- **Accept:** pill reflects killed-backend state correctly (red, not fake-green).

## Workstream C — Eval hardening: double-label κ (owner: eval agent)

**Files owned:** `scripts/make_relabel_pack.py` (new), `scripts/compute_iaa.py` (new),
`evaluation/virgin/relabel_60_blind.csv` (new), `evaluation/virgin/GOLDEN_NOTE_APPENDIX_IAA.md` (new).
Do NOT touch `backend/`, `frontend-next/`, or existing golden CSVs. **Needs 1 human hour** (the user).

### C1. Blinded relabel pack
- Sample 60 rows from `golden_human_200.csv` stratified by intent (script, seed 7 to match repo
  convention); emit CSV with `text` (+ prior-turn context per SAMPLING_NOTE) and EMPTY label columns,
  shuffled row order, no weak-label leakage. Print labeling instructions header into the CSV comment
  or companion MD (reuse `docs/ANNOTATION_PROTOCOL.md`).
- **Accept:** 60 rows, intent strata ≥4 each, zero label leakage (grep-assert in script).

### C2. κ computation + appendix note
- `compute_iaa.py` reads blinded second labels (user fills them in) + original labels; outputs
  Cohen's κ overall + per-intent, agreement rate, confusion pairs; writes the appendix MD with the
  table, n=60 caveat, and impact statement ("single-annotator → κ=0.XX bounded limitation").
  Must run cleanly on a filled template (ship a `--selftest` synthetic mode).
- **Accept:** selftest passes; script refuses to run on unleaked/empty input with a clear error.

## Execution & verification
- Order: A + B + C in parallel (contracts above decouple them). B renders pending-states until A's
  endpoints land; A never blocks on B.
- Backend tests: `.venv/Scripts/python -m pytest tests/test_virgin_fixes.py -q` (plus full suite if fast).
  Frontend: `npm run build` in `frontend-next/`. No commits unless asked; report diffs at the end.
- Demo rehearsal checklist (post-merge): kill Groq key → offline banner shows; airplane-mode compare →
  cache serves; review-queue approve → audit trail visible; embed2d/graph tabs load.

## Risks
- V3 groundedness κ may still miss 0.60 → honest FAIL + CIs is the deliverable, not a tuned pass.
- `backend/main.py` merge conflicts between A-tasks → A is a single agent, append-only edits.
- `page.tsx` refactor regressions → B keeps every existing component mounted; build-gated.
