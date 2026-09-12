# LightGBM baseline arm vs frozen LogReg (report-only, Phase 2B)

Config: LGBMClassifier {'objective': 'multiclass', 'num_class': 10, 'num_leaves': 31, 'min_child_samples': 100, 'learning_rate': 0.05, 'n_estimators': 500, 'reg_lambda': 1.0, 'deterministic': True, 'random_state': 42, 'n_jobs': -1, 'verbosity': -1} + early_stopping(50) on val multi_logloss; 30000 weak sample (seed 42), TF-IDF recipe identical to scripts/train_virgin.py; stratified 90/10 train/val (seed 42). Fit wall-time 25.1s (budget 600s); best_iteration=122; lightgbm==4.7.0.
Frozen reference: models/intent_virgin.pkl (predict-only; headline acc 0.795 untouched).
Note: LogReg 0.790 here = raw pipeline predict on human-200; the 0.795 headline adds agent-side crowd-remap/language gates (identical frozen weights). Both arms scored as raw classifiers for a like-for-like comparison.
Eval: evaluation/virgin/golden_human_200.csv (n=200); bootstrap 2000 resamples seed 20260912 (same convention as run_virgin_eval.py).

## Head-to-head (human-200)
| Arm | acc | macro-F1 |
|---|---|---|
| LogReg (frozen) | 0.790 | 0.798 |
| LightGBM (new) | 0.670 | 0.681 |
| Delta (LGBM-LogReg) | -0.120 95% CI [-0.180, -0.065] | -0.117 95% CI [-0.176, -0.063] |

## Per-intent F1 (LogReg vs LGBM; support in brackets)
| Intent | LogReg F1 | LGBM F1 | Delta |
|---|---|---|---|
| delay_claim | 0.818 (24) | 0.818 (24) | +0.000 |
| ticket_change_refund | 0.791 (23) | 0.732 (23) | -0.059 |
| timetable_platform | 0.773 (21) | 0.698 (21) | -0.075 |
| lost_property | 0.882 (16) | 0.812 (16) | -0.070 |
| complaint_service | 0.698 (23) | 0.596 (23) | -0.102 |
| fare_ticketing | 0.947 (18) | 0.593 (18) | -0.355 |
| accessibility_assistance | 0.848 (14) | 0.600 (14) | -0.248 |
| howto_guidance | 0.703 (17) | 0.647 (17) | -0.056 |
| support_access_followup | 0.882 (15) | 0.811 (15) | -0.072 |
| other_out_of_scope | 0.640 (29) | 0.507 (29) | -0.133 |

## Verdict: NO-SHIP
Rule (fixed a priori): SHIP iff macro-F1 Delta 95% CI lies strictly above 0; else NO-SHIP. Report-only arm: no artifact written, nothing wired into src/agent.py. Small-n caveat (n=200, ~14-29/intent) applies to both arms equally.

## What this does NOT claim
- Weak-30k training labels are keyword-bootstrapped (circular by construction); the comparison measures headroom of a stronger learner on weak signal, not quality gains.
- No calibration / threshold analysis was done for the LGBM arm (see thresholds.json for LogReg).
