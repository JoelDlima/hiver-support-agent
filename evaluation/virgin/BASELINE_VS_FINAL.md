# Virgin baseline vs final — formal tables (brand=virgin)

Date: 2026-09-11 (re-run after F2/F4a/F7 keyword fixes + retrain). Sources (read-only): `evaluation/virgin/golden_v1.csv` (weak-200, frozen with pre-fix rules) + `evaluation/virgin/golden_human_200.csv` (human-200: 60 manual-style + 140 rulebook-assisted, 41/200 intent flips, weak-vs-human acc 0.795 κ 0.772).
Systems: trivial = generic canned, never-escalate; simple = virgin keyword rules (post-fix) + virgin NN top-1; final = TF-IDF LogReg (`models/intent_virgin.pkl`, 30k weak post-fix, train-subset acc 0.950 optimistic) + virgin NN k=5 + virgin templates + brand-aware 4-trigger rules (rail SAFETY_ADDONS, money_intents, crowd remap).

## A. Weak-200 (keyword labels — CIRCULAR, do not use as headline)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |
|---|---|---|---|---|---|---|---|
| trivial (generic canned, never-escalate) | 0.095 | 0.017 | 0.000 | 0.000 | 0.000 | 3.00 | 0.000 |
| simple (virgin keyword + top-1) | 0.975 | 0.974 | 1.000 | 0.179 | 0.303 | 2.33 | 0.015 |
| final (TFIDF-LogReg + virgin NN k=5 + template + rules) | 0.785 | 0.786 | 0.481 | 0.893 | 0.625 | 4.21 | 0.935 |
Deltas final−simple: acc -0.190, macroF1 -0.188, esc_F1 +0.322.

## B. Human-200 (HEADLINE: single-annotator AI-assisted review)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |
|---|---|---|---|---|---|---|---|
| trivial (generic canned, never-escalate) | 0.075 | 0.014 | 0.000 | 0.000 | 0.000 | 3.00 | 0.000 |
| simple (virgin keyword + top-1) | 0.790 | 0.796 | 1.000 | 0.135 | 0.238 | 2.33 | 0.015 |
| final (TFIDF-LogReg + virgin NN k=5 + template + rules) | 0.670 | 0.685 | 0.558 | 0.784 | 0.652 | 4.21 | 0.935 |
Deltas final−simple: acc -0.120, macroF1 -0.111, esc_F1 +0.414.

## C. Per-intent F1 on human-200 (simple vs final; support in brackets)
| Intent | simple F1 | final F1 |
|---|---|---|
| delay_claim | 0.844 (24) | 0.791 (24) |
| ticket_change_refund | 0.773 (23) | 0.711 (23) |
| timetable_platform | 0.773 (21) | 0.667 (21) |
| lost_property | 0.812 (16) | 0.733 (16) |
| complaint_service | 0.727 (23) | 0.612 (23) |
| fare_ticketing | 0.947 (18) | 0.774 (18) |
| accessibility_assistance | 0.848 (14) | 0.571 (14) |
| howto_guidance | 0.703 (17) | 0.667 (17) |
| support_access_followup | 0.882 (15) | 0.833 (15) |
| other_out_of_scope | 0.653 (29) | 0.493 (29) |

## Interpretation (incl. simple-can-win honesty)
- **§B is the headline; §A is circularity demonstration.** Weak labels were frozen with pre-fix keyword rules, so post-fix simple scores 0.975 (not 1.000 — the 5 misses are the fixed cases) and final's LogReg generalizes off 30k weak bootstraps → lower vs weak labels by construction. This is expected, not a regression.
- **If simple beats final on human intent acc/macroF1, that is reported as-is** (table B deltas go negative — same pattern as Apple v1 where keyword 0.517/0.547 beat final 0.433/0.443 on human-60). Keyword reproduces weak labels that overlap human labels (weak-vs-human acc 0.795, κ 0.772); final pays an intent price for generalizing.
- **Final is justified by escalation + groundedness, not intent acc.** Simple escalates only on explicit human/safety words (near-zero esc recall — production-unsafe on money/safety cases). Final is the only system with a functioning 4-trigger head (rail safety add-ons, money_threshold, human_request, unresolvable). Groundedness heuristic favours final templates by construction (DM + 'Check' + length + cite) — heuristic, not human judgment.

## What is misleading (mandatory)
- Weak-200 numbers (§A) flatter simple (0.975 post-fix; 1.000 pre-fix) and punish final for generalizing — never quote §A without the circularity warning. Train-subset acc 0.950 (vs weak) is equally circular.
- Groundedness ≥4 rate for final (~1.0) is heuristic-shaped (template contains the scored tokens), not span-attributed faithfulness; pair with correctness + retrieval before any quality claim.
- Human-200 is single-annotator AI-assisted (60 manual-style + 140 rulebook-assisted, 41 flips); no inter-annotator κ yet; n=200 → CIs ≈±0.07 on acc. Safety slice is tiny (3 legal_safety) — see JUDGE_AGREEMENT.md. Do not claim launch on these numbers.
