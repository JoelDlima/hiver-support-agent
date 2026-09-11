# Virgin baseline vs final — formal tables (brand=virgin)

Date: 2026-09-11 (post-fix: keywords + class_weight=balanced retrain + PII gate + DR30 template). Sources (read-only): `evaluation/virgin/golden_v1.csv` (weak-200, frozen with pre-fix rules) + `evaluation/virgin/golden_human_200.csv` (human-200: 60 manual-style + 140 rulebook-assisted, 41/200 intent flips, weak-vs-human acc 0.795 κ 0.772).
Systems: trivial = generic canned, never-escalate; simple = virgin keyword rules (post-fix) + virgin NN top-1; final = TF-IDF LogReg (`models/intent_virgin.pkl`, 30k weak post-fix, class_weight=balanced, train-subset acc 0.969 optimistic) + virgin NN k=5 + virgin templates (delay w/ DR30 bands) + brand-aware triggers (rail SAFETY_ADDONS, money_intents, crowd remap, PII gate).

## A. Weak-200 (keyword labels — CIRCULAR, do not use as headline)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |
|---|---|---|---|---|---|---|---|
| trivial (generic canned, never-escalate) | 0.095 | 0.017 | 0.000 | 0.000 | 0.000 | 3.00 | 0.000 |
| simple (virgin keyword + top-1) | 0.975 | 0.974 | 1.000 | 0.179 | 0.303 | 2.33 | 0.015 |
| final (TFIDF-LogReg + virgin NN k=5 + template + rules) | 0.970 | 0.970 | 0.694 | 0.893 | 0.781 | 4.21 | 0.900 |
Deltas final−simple: acc -0.005, macroF1 -0.004, esc_F1 +0.478.

## B. Human-200 (HEADLINE: single-annotator AI-assisted review)
| System | intent_acc | macroF1 | esc_P | esc_R | esc_F1 | ground_mean | ground≥4 |
|---|---|---|---|---|---|---|---|
| trivial (generic canned, never-escalate) | 0.075 | 0.014 | 0.000 | 0.000 | 0.000 | 3.00 | 0.000 |
| simple (virgin keyword + top-1) | 0.790 | 0.796 | 1.000 | 0.135 | 0.238 | 2.33 | 0.015 |
| final (TFIDF-LogReg + virgin NN k=5 + template + rules) | 0.795 | 0.803 | 0.778 | 0.757 | 0.767 | 4.21 | 0.900 |
Deltas final−simple: acc +0.005, macroF1 +0.007, esc_F1 +0.529.

## C. Per-intent F1 on human-200 (simple vs final; support in brackets)
| Intent | simple F1 | final F1 |
|---|---|---|
| delay_claim | 0.844 (24) | 0.818 (24) |
| ticket_change_refund | 0.773 (23) | 0.791 (23) |
| timetable_platform | 0.773 (21) | 0.773 (21) |
| lost_property | 0.812 (16) | 0.882 (16) |
| complaint_service | 0.727 (23) | 0.727 (23) |
| fare_ticketing | 0.947 (18) | 0.947 (18) |
| accessibility_assistance | 0.848 (14) | 0.848 (14) |
| howto_guidance | 0.703 (17) | 0.703 (17) |
| support_access_followup | 0.882 (15) | 0.882 (15) |
| other_out_of_scope | 0.653 (29) | 0.653 (29) |

## Interpretation (post balanced-retrain honesty)
- **§B is the headline; §A is circularity demonstration.** Weak labels were frozen with pre-fix keyword rules, so post-fix simple scores 0.975 (the 5 misses ARE the fixed cases). Final's LogReg generalizes off 30k weak bootstraps.
- **Final now leads simple on human intent too** (table B deltas positive — balanced class weights fixed the accessibility tail collapse: 0.500→0.848, matching simple; lost/refund now beat simple). Small-n caveat stands (±~20%/stratum). The Apple-v1 pattern (keyword wins intent) no longer holds here — reported as-is.
- **Final is justified by escalation + groundedness AND intent now.** Simple escalates only on explicit human/safety words (near-zero esc recall — production-unsafe on money/safety cases). Final is the only system with a functioning trigger head (rail safety add-ons, money_threshold, human_request, unresolvable, PII, crowd remap). Groundedness heuristic favours final templates by construction (DM + 'Check' + length + cite) — heuristic, not human judgment.

## What is misleading (mandatory)
- Weak-200 numbers (§A) flatter simple (0.975 post-fix; 1.000 pre-fix) and punish final for generalizing — never quote §A without the circularity warning. Train-subset acc 0.969 (vs weak) is equally circular.
- Groundedness ≥4 rate for final (~1.0) is heuristic-shaped (template contains the scored tokens), not span-attributed faithfulness; pair with correctness + retrieval before any quality claim.
- Human-200 is single-annotator AI-assisted (60 manual-style + 140 rulebook-assisted, 41 flips); no inter-annotator κ yet; n=200 → CIs ≈±0.07 on acc. Safety slice is tiny (3 legal_safety) — see JUDGE_AGREEMENT.md. Do not claim launch on these numbers.
