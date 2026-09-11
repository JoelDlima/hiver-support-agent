# Virgin Golden-200 — Sampling Note (Phase 1 V-DATA)

Target: 200 golden items for V-EVAL (60 manual-style + 140 assisted, per plan pattern), stratified from `data/processed/virgin_inbound_pool.csv` (**pool n=37,444**).

## Pool + weak-label strata (first-match, followup-last; circular — stratify only)

| Stratum (weak) | Pool hits | Share | Sample take (~20/intent) | Method |
|---|---|---|---|---|
| `delay_claim` | 4,003 | 10.7% | 20 | random seed 7 |
| `ticket_change_refund` | 1,657 | 4.4% | 20 | random seed 7 |
| `timetable_platform` | 885 | 2.4% | 20 | random seed 7 |
| `lost_property` | 347 | 0.9% | 20 | random seed 7 (≈6% of stratum) |
| `complaint_service` | 4,405 | 11.8% | 20 | random seed 7 |
| `fare_ticketing` | 594 | 1.6% | 20 | random seed 7 |
| `accessibility_assistance` | 148 | 0.4% | 20 | random seed 7 (≈14% of stratum — near-census, see rare-note) |
| `howto_guidance` | 338 | 0.9% | 20 | random seed 7 (≈6% of stratum) |
| `support_access_followup` | 4,515 | 12.1% | 20 | random seed 7, cap thanks-acks (`Thank you/Thanks` dups) at ≤8 of the 20 |
| `other_out_of_scope` | 20,552 | 54.9% | 20 | random seed 7, force-include: station-only tweets, non-English, link-only, cross-brand multi-tags |
| **Total** | 37,444 | 100% | **200** | |

## Rare money/safety oversampling (deliberate)

- `accessibility_assistance` (148 weak, safety-critical): take 20 (≈14% stratum rate vs 0.5% population) + reserve 10 extra Passenger-Assist/ramp/wheelchair hits as safety-probe extras (report separately, not in headline 200).
- `lost_property` (347) + `howto_guidance` (338): 20 each (≈6% rate).
- Money overlap (`refund` spans delay↔amendment): during adjudication, dual-flag ambiguous delay/amendment items and record primary-ask + secondary note (Apple §12 pattern); report overlap rate.
- Escalation labels per item: money_threshold (refund/compensation claims), safety (overcrowd/evacuation/injury/stranded lexicon + `SAFETY_ADDONS`), human_request, unresolvable (link-only/short/non-English).

## Context + adjudication rules

- Input per item = current tweet + up to 2 prior thread turns (covers `Yes`/`Both`/thanks-ack follow-ups); exclude singleton-orphans from context training but keep flagged in golden.
- Exclude the 133 cross-brand agent rows (`inbound==False`, non-Virgin author) from the 200; keep 5 as robustness extras.
- Weak-vs-human agreement will be reported (expect Apple-like κ ~0.4–0.5 — weak labels are keyword-circular by design; headline metrics use human labels only).
- 60 manual-style first (blind review + flip log), then 140 assisted; record flips and per-intent F1 + burst-month (post-2017-11-15) slice.

## Repro

Pool: `$env:PYTHONPATH="C:\Hiver"; & "C:\Hiver\.venv\Scripts\python.exe" "C:\Hiver\scripts\build_virgin_kb.py"` → `inbound_pool=37444`. Sampling script: `scripts/build_virgin_golden.py` (V-EVAL) with seed 7, strata above.
