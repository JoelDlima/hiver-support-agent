# Per-Intent Evaluation — Human-60 Headline Set (Swarm D, §21–22)

Date: 2026-09-10 · Source: `evaluation/golden_human_60.csv` (human_* columns are truth) · System: final (`TFIDF-LogReg + TFIDF-NN + template + rules`, `src/agent.py:AppleAgent.handle`) · Method: `sklearn.metrics.classification_report` + `confusion_matrix(labels=INTENTS, zero_division=0)` · Repro: `PYTHONPATH=C:\Hiver C:\Hiver\.venv\Scripts\python.exe scripts/eval_human60.py`

## Headline (do NOT cite weak-200 as headline — see §"misleading")

| system | intent_acc | macroF1 | esc_P | esc_R | esc_F1 |
|---|---|---|---|---|---|
| trivial | 0.217 | 0.032 | 0.000 | 0.000 | 0.000 |
| simple-keyword | 0.517 | 0.547 | 0.000 | 0.000 | 0.000 |
| **final** | **0.433** | **0.443** | **0.368** | **0.500** | **0.424** |

Weak-200 for contrast only (circular — golden labels = keyword rules): trivial 0.095/0.016/0.000 · simple 1.000/1.000/0.727 · final 0.795/0.796/0.600. Simple "wins" intent by construction; final wins escalation + groundedness.

## Per-intent P/R/F1 — final vs human-60 (n=60)

| intent (support) | P | R | F1 | read |
|---|---|---|---|---|
| software_update (6) | 0.40 | 0.33 | 0.36 | loses 3/6 to hardware_device (iOS keyboard/copy-paste regressions read as hardware) |
| battery_power (4) | 0.75 | 0.75 | 0.75 | best non-trivial; 1 leak to setup_transfer_restore |
| connectivity (5) | 0.00 | 0.00 | 0.00 | total collapse: 3→other, 1→hardware, 1→setup; follow-up phrasing ("It happens randomly… not the WiFi") not caught |
| apple_id_icloud (3) | 1.00 | 1.00 | 1.00 | perfect but n=3; keyword "apple id/icloud/login" is unambiguous |
| apps_media (6) | 0.67 | 0.33 | 0.44 | scattered: 1 each to software_update / howto / followup / other |
| hardware_device (5) | 0.00 | 0.00 | 0.00 | total collapse: 2→purchase_billing, 1 each battery/followup/other; charger-wire + swollen-battery cases misrouted |
| setup_transfer_restore (3) | 0.40 | 0.67 | 0.50 | 1 leak to other |
| purchase_billing_service (5) | 0.50 | 0.40 | 0.44 | 3/5 leak to other (delivery-status, commendation, charger-wire read as non-billing) |
| howto_guidance (1) | 0.25 | 1.00 | 0.40 | n=1, unstable — do not interpret |
| support_access_followup (13) | 0.75 | 0.46 | 0.57 | largest class; leaks 2 each to software_update + hardware_device (short version-answers "It's 11.0.1" read as new issues) |
| other_out_of_scope (9) | 0.31 | 0.56 | 0.40 | catcher over-fires on connectivity/purchase/hardware; 4 leaks out (apps/hardware/setup/howto 1 each) |
| accuracy | — | — | **0.433** | 26/60 |
| macro avg | 0.46* | 0.50* | **0.443** | *P/R macro display-rounded; F1 macro recomputed = 0.443 |
| weighted avg | 0.48 | 0.43 | 0.43 | — |

Note: macro 0.443 verified two ways (`average='macro'` with and without `labels=INTENTS` — identical). Earlier draft table print showed P/R macro 0.46/0.50 from display rounding; F1 0.443 is exact.

## Agreement context (why 0.433 is the ceiling story, not a failure story)

| pair | intent acc | intent κ | esc acc | esc κ |
|---|---|---|---|---|
| weak labels vs human (label quality) | 0.517 | **0.465** | 0.700 | **0.015** |
| final vs human (system) | 0.433 | 0.363 | 0.683 | 0.213 |

Weak-vs-human intent κ 0.465 = the ceiling any weak-trained model can meaningfully beat; final 0.433 sits below simple 0.517 because both train on weak labels and the bigger model does not escape them. Escalation weak κ 0.015 ≈ random — weak esc labels are meaningless, which is why only human-60 esc_F1 0.424 counts. Final esc κ 0.213 beats weak, showing rules add signal over noise.

## Escalation 2×2 — final vs human (labels [auto=0, escalate=1])

```
[[TN 34  FP 12]
 [FN  7  TP  7]]
```

P 0.368 / R 0.500 / F1 0.424. Recall 0.50 < 0.90 ship bar (see FINAL_REVIEW Q7). 12 FPs are cheap (over-escalation); 7 FNs are the risk — audit list in JUDGE_AGREEMENT/FAILURE_TESTS.

## Confusion matrix

File: `evaluation/confusion_human60.csv` (rows true, cols pred, label order = `src/intents.py:INTENTS`). Top excerpt: apple_id row is clean `[0 0 0 3 0 0 0 0 0 0 0]`; connectivity row `[0 0 0 0 0 1 1 0 0 0 3]`; hardware row `[0 1 0 0 0 0 0 2 0 1 1]`.

## Top confusions (true → pred, count)

1. 3× software_update → hardware_device (iOS keyboard/autocorrect/copy-paste bugs)
2. 3× connectivity → other_out_of_scope (follow-up phrasing, "No SIM" without carrier words)
3. 3× purchase_billing_service → other_out_of_scope (delivery/commendation/charger-wire)
4. 2× hardware_device → purchase_billing_service ("store/repair/cost" words hijack)
5. 2× support_access_followup → software_update (version-number short replies)
6. 2× support_access_followup → hardware_device (spec-drops "Macbook pro late 2011…")
7. 1× each: 9 singleton leaks (see probe log; howto n=1 unstable)

## What this prescribes (week-2, no new claims)

1. Thread context (2-turn) — fixes follow-up class (largest support, 13) and connectivity collapse.
2. Carrier/SIM + safety lexicon pass — "no sim", swollen-battery, flame/burn already fixed; extend to "swelling/bulging/sparking".
3. Supervised retrain on 200-human (double-labeled) — weak ceiling 0.517 cannot be prompt-engineered away.
4. OOS calibration — other over-fires on connectivity/purchase; report OOS recall explicitly (CLINC lesson: 58% collapse is systemic).
5. n=60 CIs ±~12%; per-intent F1 on support ≤6 is directional only. Full 200-human + adjudication before ship.
