# Virgin per-intent thresholds (post-hoc policy; model FROZEN)

Source: `evaluation/virgin/judge_scores_200.csv` (n=200). Scores: frozen `models/intent_virgin.pkl` predict_proba (read-only). Method: per-intent one-vs-rest `roc_curve` / `precision_recall_curve`; money intents precision-first (max-P s.t. recall>=0.50), others F1-optimal; global MSP floor 0.45 (= production low_conf gate).

## Operating points
| Intent | thr | P | R | F1 | sup | ROC-AUC | AP | rule |
|---|---|---|---|---|---|---|---|---|
| accessibility_assistance | 0.8345 | 0.778 | 1.000 | 0.875 | 14 | 0.988 | 0.752 | F1-max |
| complaint_service | 0.2754 | 0.773 | 0.739 | 0.756 | 23 | 0.925 | 0.762 | F1-max |
| delay_claim | 0.4771 | 0.947 | 0.750 | 0.837 | 24 | 0.973 | 0.920 | max-P,R>=.5 |
| fare_ticketing | 0.6945 | 0.941 | 0.889 | 0.914 | 18 | 0.996 | 0.949 | max-P,R>=.5 |
| howto_guidance | 0.5324 | 0.650 | 0.765 | 0.703 | 17 | 0.857 | 0.620 | F1-max |
| lost_property | 0.1474 | 0.800 | 1.000 | 0.889 | 16 | 0.988 | 0.826 | F1-max |
| other_out_of_scope | 0.3371 | 0.800 | 0.552 | 0.653 | 29 | 0.736 | 0.622 | F1-max |
| support_access_followup | 0.5854 | 0.789 | 1.000 | 0.882 | 15 | 0.985 | 0.761 | F1-max |
| ticket_change_refund | 0.7083 | 0.867 | 0.565 | 0.684 | 23 | 0.941 | 0.776 | max-P,R>=.5 |
| timetable_platform | 0.6979 | 0.810 | 0.810 | 0.810 | 21 | 0.885 | 0.662 | F1-max |

## MSP floor grid (argmax policy, same 200 — descriptive, not tuned)
| floor | coverage | covered acc | n abstain |
|---|---|---|---|
| 0.30 | 0.995 | 0.794 | 1 |
| 0.35 | 0.990 | 0.793 | 2 |
| 0.40 | 0.985 | 0.792 | 3 |
| 0.45 | 0.970 | 0.799 | 6 |
| 0.50 | 0.945 | 0.804 | 11 |
| 0.55 | 0.900 | 0.8 | 20 |
| 0.60 | 0.855 | 0.801 | 29 |
| 0.65 | 0.810 | 0.802 | 38 |
| 0.70 | 0.745 | 0.812 | 51 |

## End-to-end gate preview (floor + per-intent gates, same 200)
accept-rate 0.895 (179/200); accuracy on accepted 0.816; abstentions route to escalate (unresolvable/low_conf or below_operating_point).

## Caveats (mandatory)
- n=200 (~14-29/intent): thresholds are noisy point estimates, no held-out split.
- ticket_change_refund precision costs recall (0.867/0.565 at thr 0.708): money_review escalation still applies downstream — the gate is additive, not a replacement.
- MSP floor barely moves covered accuracy (0.79->0.80): it buys abstention, not correctness.
- Re-tune on >=500 human labels before launch-blocking use.
