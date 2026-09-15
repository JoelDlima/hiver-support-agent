# Hiver — Fix Plan: the 5 honest risks (implementation spec)

Goal: turn each "why I might NOT pick it" risk into a measured, working improvement.
Rule: no faked numbers; every fix ships with a pass bar and an honest fallback.
Date: 2026-09-15. Repo: C:\Hiver. Venv: C:\Hiver\.venv.

## R1 — Razor-thin +0.005 intent delta (owner: backend agent A)
Root cause: "simple" baseline uses post-fix keyword rules (test-peeked); classifier sees single tweets only.
1. **Re-freeze baseline honestly.** Reconstruct PRE-FIX keyword rules from git history
   (`git log -p -- src/virgin_intents.py`, commits ~8d9be27ומה before), score on human-200 via a new
   script (do not mutate existing eval scripts); publish pre-fix-simple vs final delta. Lead with it.
2. **Miss audit.** Bucket the ~41 human-200 misses (ambiguous / multi-intent / context-dependent / OOS);
   write `evaluation/virgin/MISS_AUDIT.md` with counts + 2 examples per bucket.
3. **Real modeling, in order:** (a) thread-context features (prior 1–2 turns — golden rows carry
   `context_prior_1/2`, classifier must USE them); (b) explicit out-of-scope detector stage;
   (c) per-intent thresholds tuned on WEAK data only, never human-200.
4. **Optional challenger:** fine-tune small Twitter-pretrained encoder (BERTweet-class) on 30k weak,
   eval human-200. Use Context7 MCP to verify current transformers/setfit API before coding.
   If it fails, it joins SetFit/LightGBM as a documented rejection.
5. **Pass bar:** McNemar p<0.05 intent gain, OR documented saturation claim (intent caps ~0.80 for this
   taxonomy; gains live in escalation/groundedness) with per-intent table as evidence.
Files: backend/main.py (append-only), scripts/prefix-new `r1_*`, evaluation/virgin/MISS_AUDIT.md + R1_RESULT.md.
Never train on human-200; never tune rules against golden.

## R2 — Failed judge deliverable (owner: eval agent C)
Root cause: open verdicts, bare prompt, n=30 wide CIs.
1. **Narrow to groundedness** (endpoint exists: POST /judge/groundedness).
2. **Upgrade protocol:** G-Eval-style few-shot anchors (1/3/5 examples in prompt),
   evidence-citation-before-score, judge family ≠ generator family, double-run with disagreement → human.
   New script `scripts/run_groundedness_judge_v2.py` (do not edit existing judge scripts).
3. **Scale the study:** human groundedness 1–5 labels needed for n=100. FIRST check what human
   groundedness labels already exist (results_human200.csv? golden files?). If missing, build a
   blind labeling pack (same pattern as scripts/make_relabel_pack.py) for the USER to fill — do not
   self-label and call it human. Pilot agreement on existing n=30 labels meanwhile.
4. **Pass bar:** weighted κ ≥ 0.60, CI lower ≥ 0.50 → gate flips PASS. Else honest FAIL with n=100 CIs.
Files: scripts/run_groundedness_judge_v2.py + label-pack scripts (new), evaluation/virgin/JUDGE_AGREEMENT_V4.md (new).

## R3 — Template replies, not generation (owner: backend agent A)
1. **Constrained generation mode:** retrieve top-k → LLM draft (citation-before-claim prompt, temp 0.1,
   strict JSON {reply, cited_ids}) → NLI entailment gate ≥0.9 else template fallback + escalate
   grounding_fail → PII/length/policy guards. Template path untouched as fallback.
   New module `backend/generate.py` + thin route in main.py; reuse Groq hook + offline-flag pattern.
2. **A/B decide:** same ~100 queries, template vs constrained-LLM; human + caged-judge groundedness +
   specificity. ~200 short Groq calls; cap cost, log spend.
3. **Pass bar:** LLM wins specificity with NO significant groundedness drop → "expressive mode" default
   w/ template fallback. Else template stays + measured justification. Add clarification behavior for
   multi-intent inputs (ask one question, don't guess).
Files: backend/generate.py (new), backend/main.py route only, scripts/r3_abexp.py (new),
evaluation/virgin/GENERATION_AB.md (new).

## R4 — Single annotator (owner: USER, 1 hour — agents only prep)
Pack exists (`evaluation/virgin/relabel_60_blind.csv`, `scripts/compute_iaa.py`). Human fills blind,
runs script, adjudicates disagreements, publishes provenance table. Agents: nothing to do unless the
R2 pack (agent C) also needs building — then same pattern.

## R5 — Bloat signals (owner: frontend agent B)
1. **Two-tier demo:** main path Try it → Proof → Review ONLY. Move 3D graph, knowledge-graph explorer,
   OTel trace viewer under an "Advanced / Labs" tab with one-line justification each. No deletions of
   working code; re-route navigation.
2. **Report narrative:** every component gets "why it exists + what breaks without it" or leaves the
   main narrative (edit docs/REPORT_VIRGIN_6PAGE.md minimally, or add pointer section).
3. **Pass bar:** architecture describable in one sentence with no mention of graphs/matrices/telemetry.

## Frontend↔backend wiring (owner: frontend agent B, verify live)
- New backend endpoints MUST be callable from UI: /judge/groundedness, /eval/retrieval-ablation,
  /eval/compare (proxies exist from WS-B — wire pending-states to live, keep graceful 404 handling).
- Verify: backend base URL config (env), CORS, offline banner path, compare-strip values == docs.
- Prove it: `npm run build` green + curl transcript of every proxied endpoint in report-back.

## Verification (orchestrator)
- Backend: `.venv/Scripts/python -m pytest tests/ -q` green; new tests for new endpoints.
- Frontend: `npm run build` green; no files outside owned dirs (git status check per agent).
- No commits unless asked. No new pip/npm deps without asking (check requirements.txt first).
