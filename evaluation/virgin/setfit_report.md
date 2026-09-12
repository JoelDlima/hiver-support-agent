# VirginTrains SetFit/MiniLM challenger — Phase 2A report (report-only)

Date: 2026-09-12. Challenger head: frozen `paraphrase-MiniLM-L6-v2` body
(sentence-transformers 6.0.1, torch 2.14.0+cpu) + sklearn LogReg head
(SetFit 1.2.0's default head design; contrastive body-tuning deliberately
skipped so the comparison isolates features: TF-IDF vs MiniLM). Protocol:
weak-pretrain on 30k weak labels (class-balanced 3,611 rows) → warm-start
fine-tune on 200 human labels with 5x stratified CV (seed 42) → temperature
fit on OOF logits → MSP/Energy abstention. Code: `src/setfit_head.py`,
`scripts/train_setfit_head.py`; artifact: `models/intent_virgin_setfit/`;
contract tests: `tests/test_setfit_head.py` (4 passed, full suite 46 green).

Nothing production was touched: `models/intent_virgin.pkl`, goldens,
`scripts/run_virgin_eval.py`, frontend, and headline CSVs
(`results_human200.csv`, `results_weak200.csv` — `git diff` empty) unchanged.

## 1. CV results vs TF-IDF baseline (human-200)

| System | acc | macro-F1 | note |
|---|---|---|---|
| TF-IDF+LogReg final (baseline, read-only) | 0.795 | 0.803 | resubstitution-style: weak-trained, human-tested |
| Challenger fine-tuned, 5-fold OOF (C=2.0, T=1.7) | 0.340, 95% CI (0.275, 0.405) | **0.349, 95% CI (0.281, 0.406)** | headline challenger number |
| Challenger weak-head-only transfer (no human fitting) | 0.595 | 0.608 | apples-to-apples with baseline regime |
| Challenger ablation C=0.1 / C=0.5 (aligned OOF) | 0.400 / 0.365 | 0.396 / 0.369 | best-C still less than half the baseline |

Per-fold challenger macro-F1: 0.271, 0.258, 0.332, 0.341, 0.467
(mean 0.334; fold acc 0.300, 0.300, 0.300, 0.325, 0.475).
OOF−baseline delta macro-F1 = **−0.454**, CI far from 0 — a real loss, not noise.

Caveat (both directions): the baseline number is resubstitution on its
weak-train distribution while the challenger is OOF on human labels, so the
−0.454 is not a paired delta; but the weak-head-only row (0.608, same
weak-train/human-test regime as the baseline's 0.803) confirms the gap is in
the features/regime, not the CV protocol.

## 2. Per-intent OOF F1 (challenger vs baseline final; support in brackets)

| Intent | baseline final F1 | challenger OOF F1 |
|---|---|---|
| delay_claim (24) | 0.818 | 0.577 |
| ticket_change_refund (23) | 0.791 | 0.298 |
| timetable_platform (21) | 0.773 | 0.200 |
| lost_property (16) | 0.882 | 0.583 |
| complaint_service (23) | 0.727 | 0.227 |
| fare_ticketing (18) | 0.947 | 0.378 |
| accessibility_assistance (14) | 0.848 | 0.207 |
| howto_guidance (17) | 0.703 | 0.176 |
| support_access_followup (15) | 0.882 | 0.581 |
| other_out_of_scope (29) | 0.653 | 0.258 |

Challenger loses on all 10 intents, worst on the keyword-sharp intents
(timetable 0.200, howto 0.176, accessibility 0.207) where TF-IDF n-grams
match the weak-label rules almost exactly.

## 3. Coverage curve (temp-scaled OOF, T=1.7)

MSP (min_conf → coverage / selective-acc / n):

| min_conf | coverage | selective_acc | n |
|---|---|---|---|
| 0.50 | 0.145 | 0.517 | 29 |
| 0.60 | 0.055 | 0.545 | 11 |
| 0.70 | 0.020 | 0.500 | 4 |
| 0.80 | 0.015 | 0.667 | 3 |
| 0.90 | 0.000 | — | 0 |
| 1.00 | 0.000 | — | 0 |

coverage@90%: MSP 0.005 (n=1) / Energy 0.005 (n=1). The model is both
inaccurate and under-confident (no prediction reaches 0.90 MSP): the
abstention gate cannot buy accuracy at any usable coverage — selective
prediction is not a rescue path.

## 4. Latency (CPU, contract test)

Amortized predict (frozen MiniLM encode + head, batch of 20): **2.6 ms/text**.
One-time body load ~5–13 s (cold `SentenceTransformer` init + weights).
Latency is a non-issue; accuracy is the blocker.

## 5. Honest verdict: DO NOT SHIP

* The challenger (OOF macro-F1 0.349, CI 0.281–0.406) underperforms the
  TF-IDF baseline (0.803) by 0.454 — significant, all 10 intents, robust to
  regularization (best-C ablation 0.396).
* Diagnosis, not a bug: with n=200 in a 384-dim space the head memorizes
  (train acc 1.0) and fine-tuning *destroys* the weak prior (weak-only
  transfer 0.608 → fine-tuned OOF 0.349; warm-start converges to the fresh
  solution, verified fold0 agreement 1.0). Keyword-defined weak labels live
  in n-gram space; frozen MiniLM smears exactly the distinctions
  (platform/how-to/accessibility tokens) that TF-IDF preserves.
* Abstention cannot compensate (coverage@90% ≈ 0).
* Keep the TF-IDF head. Revisit MiniLM only with (a) unfrozen contrastive
  body-tuning on weak pairs (full SetFit, GPU budget), or (b) ≥1k human
  labels — until then this artifact stays report-only. No production,
  eval-harness, or headline changes result from this phase.
