# R1a — Honest pre-fix baseline (FIX_PLAN R1.1)

- Pre-fix rules: `git show 87cecde:src/virgin_intents.py` (KEYWORDS extracted verbatim, no retraining).
- Scored on `evaluation/virgin/golden_human_200.csv` (n=200, read-only).
- Per-row CSV: `r1_prefix_simple200.csv`. Bootstrap 2000 resamples, seed 20260912.

## Headline (human-200)
| system | intent acc | intent macroF1 | esc P | esc R | esc F1 |
|---|---|---|---|---|---|
| simple (PRE-FIX rules, reconstructed) | 0.775 | 0.783 | 1.000 | 0.108 | 0.195 |
| simple (post-fix rules, current) | 0.790 | — | — | — | — |
| final (frozen artifact) | 0.795 | 0.803 | — | — | 0.767 |

## Deltas
- final − simple(pre-fix) acc: **+0.020** (bootstrap 95% CI [-0.035, +0.080])
- final − simple(pre-fix) macroF1: **+0.020**
- final − simple(pre-fix) esc F1: **+0.572**

## Pre-fix vs post-fix keyword rules (McNemar exact on discordant pairs)
- pre-fix right / post-fix wrong: b=4; pre-fix wrong / post-fix right: c=7
- exact p = 0.5488 (not significant at 0.05)

## What is misleading (mandatory)
- The published weak-200 'simple 0.975' is post-fix rules vs pre-fix frozen labels — circular, disclosed in BASELINE_VS_FINAL.md §A.
- This table is the honest version: pre-fix rules measured on the same human-200 the final system reports on.
- The keyword-fix lift itself (post-fix vs pre-fix, same system shape) is +3 net rows; the CLASSIFIER-vs-KEYWORDS story remains the final-vs-simple comparison above.

## Reproduce
```powershell
python scripts/r1_prefix_baseline.py           # real run (reads git history + goldens, read-only)
python scripts/r1_prefix_baseline.py --selftest  # synthetic math check
```
