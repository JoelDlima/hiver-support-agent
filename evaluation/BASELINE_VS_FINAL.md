# Baseline vs final — formal tables (§23)

Date: 2026-09-10. Sources (read-only, NOT overwritten): `evaluation/results.csv` (weak-200) + `evaluation/results_human60.csv` (human-60).
Systems: trivial = majority canned, never-escalate; simple/keyword = weak keyword rules (+retrieval top-1); final = TF-IDF LogReg + TF-IDF-NN k=5 + template + 4-trigger rules.

## A. Weak-200 (`golden_v1.csv`: weak keyword labels — CIRCULAR, do not use as headline)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |
|---|---|---|---|---|---|---|---|
| trivial | 0.095 | 0.016 | 0.000 | 0.000 | 0.000 | 3.00 | 0.000 |
| simple (keyword+top-1) | 1.000 | 1.000 | 1.000 | 0.571 | 0.727 | 2.98 | 0.205 |
| final | 0.795 | 0.796 | 0.429 | 1.000 | 0.600 | 4.75 | 1.000 |
Deltas final−simple: acc **−0.205**, macroF1 **−0.204**, esc_F1 **−0.127**, ground_mean +1.77.

## B. Human-60 (`golden_human_60.csv`: single-annotator blind review, 39/60 flipped — HEADLINE)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 |
|---|---|---|---|---|---|
| trivial | 0.217 | 0.032 | 0.000 | 0.000 | 0.000 |
| simple-keyword | **0.517** | **0.547** | 0.000 | 0.000 | 0.000 |
| final | 0.433 | 0.443 | **0.368** | 0.500 | **0.424** |
Deltas final−keyword: acc **−0.084**, macroF1 **−0.104**, esc_F1 **+0.424**.

## Interpretation (incl. circularity warning)
- **§B is the headline; §A is circularity demonstration.** Weak labels ARE the keyword rules' output, so simple scores 1.000/1.000 tautologically (`GOLDEN_NOTE.md`). Final's LogReg generalizes away from the rules → lower vs weak labels by construction. This is expected, not a regression.
- On trustworthy human-60 the intent ranking **inverts**: keyword (0.517/0.547) beats final (0.433/0.443) because keyword reproduces weak labels that overlap human labels 51.7% (weak-vs-human acc 0.517, κ 0.465 per GOLDEN_NOTE). Final pays a small intent price for generalizing off 30k weak bootstraps.
- **Final is justified by escalation + groundedness, not intent acc.** Keyword never escalates (esc F1 0.000 — production-unsafe: safety/human-request cases auto-handled). Final is the only system with a functioning 4-trigger head (esc F1 0.424, R 0.500; misses remain — see FAILURE_TESTS). Groundedness heuristic favors final templates (4.75, 100% ≥4 vs 2.98/20.5%) — heuristic, not human judgment.
- Limits: n=60 single annotator → wide CIs (≈±0.12 on acc); no inter-annotator κ yet; next = double-label 60 + full-200 human + adjudication (GOLDEN_NOTE). Do not claim launch on these numbers.
