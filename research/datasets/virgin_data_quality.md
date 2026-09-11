# TWCS Data Quality — VirginTrains Focus (Phase 1 V-DATA)

- **Source:** `C:\Hiver\data\raw\twcs.csv` (2,811,774 rows; TWCS only, PS-strict)
- **Brand focus:** VirginTrains
- **Subset definition (union):** `author_id == "VirginTrains"` OR case-insensitive `@VirginTrains` in `text`
- **Subset size (full scan):** 65,346 rows (2.32% of raw) = 27,817 outbound + 37,530 inbound-mention − 1 overlap (agent self-mention)
- **Analysis sample:** full 65,346-row union — no sampling needed (≤200k speed cap; satisfies plan "sample ≤200k rows")
- **Downstream artifacts:** `C:\Hiver\data\processed\virgin_kb.csv` (27,172 rows, template-cap K=5) + `C:\Hiver\data\processed\virgin_inbound_pool.csv` (37,444 rows)
- **Tooling:** `C:\Hiver\.venv\Scripts\python.exe` (`PYTHONPATH=C:\Hiver`), pandas chunk scan (`chunksize=200k`); builder `scripts/build_virgin_kb.py`; intents `src/virgin_intents.py`
- **Date of inspection:** 2026-09-10

## 1. Schema

Same 7-column TWCS schema as Apple slice (`research/datasets/data_quality.md` §1). Observed on Virgin union:

| Column | Nulls in Virgin union (n=65,346) | Notes |
|---|---|---|
| `tweet_id` | 0 | Unique (`dup_tweet_id=0`). Join key for threads. |
| `author_id` | 0 | `VirginTrains` = agent (27,817); else numeric user ids + 133 other-brand agent tweets (see §8.5). |
| `inbound` | 0 | True 37,396 / False 27,950. `author_id==VirginTrains` rows are ALL `inbound==False`; the 133 extra `False` rows are other operators' agents — use `author_id`, not `inbound`, for brand slices. |
| `created_at` | 0 | Parse fail 0/65,346. |
| `text` | 0 | Min 7 chars; HTML entities + `t.co` short URLs as in Apple slice. |
| `response_tweet_id` | 20,687 (31.7%) | Forward link(s); 6,105 rows (9.3%) multi-id — higher fan-out than Apple (5.6%). Split on `[,;\s]+`. |
| `in_response_to_tweet_id` | 14,516 (22.2%) | Backward link (single). |

## 2. Scale + class balance

- Raw: 2,811,774. Virgin union: 65,346.
- `inbound==True` 57.2% / `False` 42.8% — inbound-heavy (vs Apple's near-balanced 47.8/52.2). Good for intent modeling; KB side still large (27k outbound >> golden needs).
- Mention overlap: 1 row in both sets (agent self-mention) — sets near-disjoint.

## 3. Temporal span

- Min: `2012-03-12`, Max: `2017-12-03` (~5.7 y span) but **burst-concentrated like Apple**: top months `2017-11`: 34,671 (53.1%), `2017-10`: 24,984 (38.2%), `2017-12`: 5,459 (8.4%); all other months ≤143 each (long thin tail back to 2012).
- **Implication:** same as Apple §3 — random splits leak the Oct–Nov 2017 burst. Use **time-based split** (train ≤ 2017-11-15, test > 2017-11-15) + per-month metrics. Thin pre-2017 tail = distribution-shift eval slice, not training.

## 4. Text-length distribution (union n=65,346)

| | mean | median | std | min | max | p25 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|---|---|
| chars (all) | 99.3 | 94.0 | 50.6 | 7 | 358 | 60 | 131 | 156 | 189 |
| words (all) | 16.9 | 16.0 | 9.0 | 1 | 62 | 10 | 22 | 27 | 33 |
| chars outbound (n=27,817) | 84.9 | 79.0 | 40.3 | 7 | 304 | 54 | 111 | 133 | 151 |
| chars inbound-mention (n=37,529) | 110.1 | 110.0 | 54.6 | 13 | 358 | 69 | 140 | 169 | 213 |

Shorter than Apple on both sides (Apple union mean 122.8/med 125). Inbound top exact-text dups are all short acks (`Thank you` 82, `Thanks` 73, `Morning` 22, `Yes` 18) — context-dependent turns needing thread windows.

## 5. Thread reconstruction (via `response_tweet_id` / `in_response_to_tweet_id`)

Method: undirected union-find over full 65,346 union (no sampling loss); multi-ids split on commas/semicolons/whitespace; edge only if endpoint id in union.

- Threads: **14,972**; size mean 4.36, median 3.0, min 1, max **203**. (Longer threads than Apple: mean 2.42/med 2.0 — rail disruption conversations run longer.)
- Size distribution: `1`: 80 (0.5%), `2`: 5,766 (38.5%), `3–5`: 5,959 (39.8%), `6–10`: 2,431 (16.2%), `11+`: 736 (4.9%).
- Links: response edges 55,619, dangling 5,245 (9.4%); in-response edges 50,830, dangling 456 (0.9%).
- Multi-response rows: 6,105 (9.3%) — agent fan-out/merged threads; resolve by preferring `in_response_to` chain, then smallest id.
- Direction markers: outbound starts with `@`: 98.99%; inbound starts with `@`: 86.8% (rest are mid-thread follow-ups without re-mention).
- Singletons only 0.5% (vs Apple 29% — Apple figure was a 200k-subsample artifact; full-union rebuild confirms).

## 6. URLs / mentions / hashtags / emoji (union n=65,346)

- URLs: **10.6%** rows (6,918) — far lower than Apple (46.3%). Split: outbound 13.2% / inbound 8.6%. Rail agents link less; triage is conversational (DM + booking ref), not KB-link based. Retrieval design must not rely on URL presence as a triage signal.
- Mentions (`@\w+`): **99.6%** rows, mean 1.29/tweet. Top: `@virgintrains` 38,055; numeric user-ids `@120576` 4,131, `@127472` 807…; cross-brand `@londonmidland` 680, `@nationalrailenq` 334 (West-Coast corridor confusion / multi-tagging).
- Hashtags: **4.5%** (2,950). Top: `#virgintrains` 126, `#euston` 70, `#vtupdate` 68, `#london` 57 — sparse, keep (operational tags `#vtupdate/#vtinfo` mark disruption comms).
- Emoji: **9.6%** (6,305) — mostly inbound sentiment markers.
- Outbound exact-text dups are chit-chat, not templates: max group 5 (`Hi Becky ^JH`), 124 groups hit cap 5. No dominant canned template — KB dedup removed only 642 rows (vs Apple's heavier template mass).

## 7. KB / pool build (what `scripts/build_virgin_kb.py` did)

- `virgin_kb.csv`: 27,817 outbound → 27,814 len>10 → **27,172** after template-cap K=5 (642 rows cut, 124 groups capped, max group 5, 1,201 residual dup pairs kept by design to preserve prior). Columns `tweet_id,author_id,inbound,text,clean` (`clean` via `src/text_norm.normalize`; note: normalizer maps `@AppleSupport→<BRAND>`, so `@VirginTrains→<USER>` — V-MODEL should add a Virgin brand token; recorded, not patched here).
- `virgin_inbound_pool.csv`: 37,530 mentions → **37,444** len>10 (1,090 residual exact dups, mostly thanks-acks — keep for prior, stratify around them for golden).
- Clean-length: KB mean 82.1/med 76; pool mean 103.0/med 103.

## 8. Quality issues (actionable)

1. **Temporal burst bias** (91% in Oct–Nov 2017). Time-split, never random-split.
2. **High multi-response fan-out** (9.3% rows) — deterministic resolution rule required.
3. **Inbound-heavy + short-ack mass** (`Thank you/Thanks/Morning/Yes` top dups) — golden must stratify on weak labels, not random-sample (else thanks-acks dominate).
4. **Station names are slot entities, not intents** (`euston` in 4,220 inbound / `manchester` 1,442 / `london` 3,342) — never keyword on them; they fill journey slots.
5. **Cross-brand agent tweets in threads** (133 rows: LondonMidland 60, GWRHelp 26, nationalrailenq 24…) — exclude non-`VirginTrains` `inbound==False` rows from KB/training; keep flagged for robustness eval.
6. **`ticket` too generic for keywords** (3,900 inbound / 2,025 outbound) — fare vs amendment distinguished by modifiers (refund/advance/fare/railcard), not bare `ticket`.
7. **URL signal weak** (10.6%) — retrieval/triage features must use Delay-Repay/amendment lexicon + booking-ref requests, not link presence.
8. **Rare safety-critical tail**: accessibility (wheelchair 27, ramp 22, disabled 71), lost-property specifics (`left my` 58) — oversample by design (see sampling note).
9. **Money intents overlap** (`refund` spans delay_claim ↔ ticket_change_refund) — order delay_claim first (distinctive `delay repay/delayed/cancelled/compensation` win), refund-amendment second; adjudicate overlaps in golden.
10. **No resolution/CSAT labels** (TWCS-wide) — golden needs human escalation labels per money/safety thresholds.

## 9. Preprocessing plan (for intent + retrieval/response stages)

Same P0–P2 as Apple §9 with Virgin deltas: (a) time-split at 2017-11-15; (b) rebuild threads on full 65,346 union (done stats above); multi-id split + `in_response_to`-first resolution; (c) normalize identically (store `text_raw` + `text_norm`); mask numeric `@user→<USER>`, add `has_cross_brand` (`londonmidland|nationalrailenq|gwrhelp|sw_help…`); keep hashtags incl. `#vtupdate/#vtinfo`; (d) dedup cap K=5 already applied in KB; (e) context window = current + up to 2 prior turns (covers `Both`/`Yes`/thanks-acks); (f) exclude 133 cross-brand agent rows from training.

## 10. Intent taxonomy rationale (10 intents, `src/virgin_intents.py`)

Plan list kept; keyword grounding counts are inbound/outbound hits from §6/keyword scan:

| # | Intent | Triggers (keyword evidence) |
|---|---|---|
| 1 | `delay_claim` | delay 2602/1757, delayed 1326/534, late 1400/583, cancel 1387/275, delay repay 291/432, compensation 251/357 |
| 2 | `ticket_change_refund` | refund 1224/308, advance 607/342, booking 400/391, booking ref 45/205, off-peak 48/98, admin fee |
| 3 | `timetable_platform` | platform 356/59, timetable 50/45 + departure/arrival/engineering-works phrasing |
| 4 | `lost_property` | lost 214/154, left 494/52, left my 58/0, bag 138/16, luggage 97/14 |
| 5 | `complaint_service` | complaint 365/390, rude 185/1 + seat 2347/872, first class 925/222, wifi 712/259, toilet 373/28 (onboard experience) |
| 6 | `fare_ticketing` | fare/railcard/penalty/season/collect/machine/office (bare `ticket` excluded as keyword) |
| 7 | `accessibility_assistance` | assistance 78/62, wheelchair 27/2, disabled 71/6, ramp 22/0 — rare, oversample |
| 8 | `howto_guidance` | how/where question shape |
| 9 | `support_access_followup` | Thank you 82, Thanks 73, Morning 22, Yes 18, dm-sent variants — matched LAST so content wins over thanks-tails |
| 10 | `other_out_of_scope` | catcher (weak-label residual 54.9% — station-only tweets, fragments, non-rail) |

Weak-label coverage on pool (first-match, followup-last): non-other 16,892/37,444 (45.1%); per-intent: delay 4,003 / complaint 4,405 / followup 4,515 / amendment 1,657 / timetable 885 / fare 594 / howto 338 / lost 347 / accessibility 148 / other 20,552. **Circular by design** (cf. Apple κ 0.465 lesson) — golden labels must be human-adjudicated; weak labels only stratify sampling.

**Label workflow:** weak-label → stratify ~20/intent (near-census for accessibility/lost/howto; see `evaluation/virgin/SAMPLING_NOTE.md`) → human-adjudicate 200 thread-complete conversations (current + ≤2 prior turns) → train on `text_norm` + context + `has_cross_brand/n_urls` features; report per-intent F1 + burst-month slice.

## 11. Reproducibility + next steps

- Repro: `$env:PYTHONPATH="C:\Hiver"; & "C:\Hiver\.venv\Scripts\python.exe" "C:\Hiver\scripts\build_virgin_kb.py"` → `STATS outbound=27172 inbound_pool=37444`. All paths under `C:\Hiver` only.
- Next (V-MODEL / V-EVAL): brand token for `@VirginTrains` in `text_norm`; train virgin classifier on weak+human labels; build virgin index over `virgin_kb.csv`; golden-200 per sampling note.
- Limitations: `t.co` targets unresolved; multilingual slice not yet quantified for Virgin (assume Apple-like ~0.5%, verify at golden sampling); sentiment/urgency not yet scored.
