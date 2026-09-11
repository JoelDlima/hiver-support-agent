# LLM-Judge Agreement — Offline Attempt + Gating Decision (Swarm D, §21–22)

Date: 2026-09-10 · Rubric: `evaluation/rubric.md` (DRAFT v1, 5 dims, weights 0.35/0.25/0.15/0.15/0.10, gates groundedness≤2 / safety≤2 = FAIL, PASS if overall ≥3.5) · Status: **LLM judge NOT shipped — gated. Heuristic offline judge only.**

## What was attempted offline (no API key in repro — real constraint, not a skip)

1. **Heuristic judge runs offline** (`scripts/run_eval.py:groundedness_heuristic`): DM-mention + diagnostic-step + length≥15 + passages-nonempty → 1–5. This is the shipped "judge": deterministic, zero-cost, reproducible.
2. **Heuristic score distribution, final system:**
   - human-60 (truth set): `{5: 43, 4: 17}` · mean **4.72** · ≥4 rate **1.000** (60/60). Probed 2026-09-10 via `scripts/run_eval.py` logic.
   - weak-200 (for contrast): mean 4.75 · ≥4 rate 1.000 (see `evaluation/results.csv`); trivial 3.00/0.000, simple 2.98/0.205.
   - Reading: templates score 4–5 **by construction** (every template contains a DM redirect + diagnostic step + ≥15 words + passage IDs). This is a self-reward artifact — disclosed, not a factuality claim.
3. **LLM judge call attempted: NO.** No `OPENAI_API_KEY` / Anthropic key in the offline repro environment and no vendored judge weights; the rubric's judge prompt block was written but never executed against a pinned model. Faking scores would violate §36 (no pretend). So: protocol + gate specified, execution deferred.

## Why the LLM judge is gated (two independent bars, both must pass)

- **Needs API key + pinned model version.** Scores are not transferable across judge models (Siro et al. 2026 cross-model disagreement; see research log Agent-1 Q5 + Agent-8). Running an unpinned judge once and citing the number is the correlation≠agreement trap (Han 54-LLM study: r=0.95 with κ=0.45).
- **Needs κ ≥ 0.60 (groundedness weighted-κ) AND safety-FAIL recall ≥ 0.90** on the 60-overlap calibration set before any LLM score appears in a headline (`evaluation/rubric.md` Judge↔human calibration protocol). Heuristic judge has not been κ-scored either — same bar applies.

## Current agreement evidence (the numbers that exist today)

| pair | intent acc | intent κ | esc acc | esc κ | source |
|---|---|---|---|---|---|
| weak labels vs human (60) | 0.517 | **0.465** | 0.700 | **0.015** | `scripts/human_correct_60.py` output; `evaluation/GOLDEN_NOTE.md` |
| final predictions vs human (60) | 0.433 | 0.363 | 0.683 | 0.213 | probe 2026-09-10 (`cohen_kappa_score`) |
| heuristic-judge vs human | — | **not yet scored** | — | — | week-2 item; GOLDEN_NOTE states this explicitly |

- Weak-vs-human intent κ **0.465** (moderate) = label-noise ceiling; esc κ **0.015** (slight/chance) = weak escalation labels are noise, not signal.
- Human–human benchmark for context: Judge's Verdict static baseline κ̄=0.801; Tier-1 LLM judges reach κ 0.781–0.816 with |z|<1 (websearch 2026-09-10). Our 0.465/0.015 sits far below — honest distance-to-ship.
- BFF-Bench lesson (websearch): reference-free judges agree with experts only where the judge could itself answer correctly (κ 0.78→0.30 collapse on judge-wrong items); human-written references recover κ to ~0.83–0.92. Implication for us: any future LLM judge MUST be reference-guided (passages + human label as reference), never free-floating.

## 75-pair protocol — next (frozen, from `research/papers/academic_review.md`)

50 grade pairs + 25 attack/swap pairs, blinded, 2 humans + 1 pinned judge, same rubric. Report per-dimension quadratically-weighted κ + Spearman ρ + mean bias, and PASS/FAIL Cohen's κ with safety-FAIL recall. Ship-gate: groundedness wκ ≥ 0.60 AND safety-FAIL recall ≥ 0.90. Run judge twice; report self-consistency + swap-consistency ≥85% + verbosity-correlation. Pin model version; re-calibrate on any model change. This is the week-2 study that un-gates the LLM judge — not a claim that it passed.

## Bottom line

Offline judge = heuristic distribution reported above (real, reproducible, circular-by-design). LLM judge = rubric + frozen protocol, zero scores claimed, gated on key + κ≥0.60 + safety-recall≥0.90. Anyone citing an LLM-judge number for this repo today is citing a number that does not exist.
