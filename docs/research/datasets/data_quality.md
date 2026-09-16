# TWCS Data Quality — AppleSupport Focus (AGENT 6)

- **Source:** `data\raw\twcs.csv` (2,811,774 rows)
- **Brand focus:** AppleSupport
- **Subset definition (union):** `author_id == "AppleSupport"` OR case-insensitive `@AppleSupport` in `text`
- **Subset size (full scan):** 204,772 rows (7.28% of raw) = 106,860 outbound + 97,913 inbound-mention − 1 overlap
- **Analysis sample:** 200,000 rows, uniform random, `seed=42` (97.66% of Apple union; used for all stats below unless noted)
- **Downstream sample:** `data\intermediate\apple_sample.csv` (5,000 rows, random `seed=42`, UTF-8, full schema)
- **Tooling:** `.venv\Scripts\python.exe`, pandas chunk scan (`chunksize=200k`); script `scripts/apple_inspect_tmp.py`
- **Date of inspection:** 2026-09-10

## 1. Schema

| Column | Observed dtype (raw) | Nulls in Apple union (n=204,772) | Notes |
|---|---|---|---|
| `tweet_id` | int-like (stored str in scan) | 0 | Unique in 200k sample (`dup_tweet_id=0`). Join key for threads. |
| `author_id` | str | 0 | `AppleSupport` = agent; else numeric user id (e.g. `115858`). Top mention `@115858` (9,531 hits) shows high-cardinality user-id mentions. |
| `inbound` | bool (`True`=user, `False`=agent) | 0 | 95,652 inbound (47.8%) / 104,348 outbound (52.2%) in 200k sample. `author_id==AppleSupport` (104,332) aligns with `inbound==False` up to rounding/sampling. |
| `created_at` | str, `%a %b %d %H:%M:%S %z %Y` (e.g. `Tue Oct 31 22:10:47 +0000 2017`) | 0 | Parse fail = 0/200k. |
| `text` | str | 0 (also 0 empty-after-strip) | Min 13 chars; always non-empty. Contains HTML entities (`&amp;`, `&gt;`), smart quotes (`’`, `“`), `t.co` short URLs. |
| `response_tweet_id` | mixed: float-like OR comma-separated str (e.g. `706,704`) | 88,764 (43.35%) | Forward link(s). 11,130 rows (5.57% of 200k) have **multi-ids** (`,`/`;`/space separated). Must split on `[,;\s]+`. |
| `in_response_to_tweet_id` | int-like str | 51,658 (25.23%) | Backward link (single). In 200k sample: 50,479 missing (25.24%). |

> Null counting detail: `missing` table above is on the full 204,772 union; `response_missing=86,668 / in_response_missing=50,479` are the same fields measured on the 200k analysis sample (43.33% / 25.24% — consistent).

## 2. Scale + class balance

- Raw: 2,811,774. Apple union: 204,772.
- Analysis (200k): inbound 47.8% / outbound 52.2% — near-balanced, good for intent + response modeling without resampling.
- Mention overlap: only 1 row in both sets (agent tweet self-mentioning `@AppleSupport`); i.e. sets are near-disjoint. `mention=95,669` in sample ≈ inbound count; `author==AppleSupport (104,332)` ≈ outbound count.

## 3. Temporal span

- Min: `2016-03-03 13:00:08+00:00`, Max: `2017-12-03 23:12:28+00:00`, span **640.4 days**, parse failures 0.
- Extremely skewed to iOS-11 launch window (top months in 200k sample):
  - `2017-11`: 107,492 (53.7%), `2017-10`: 82,752 (41.4%), `2017-12`: 9,337 (4.7%)
  - `2017-09`: 311, `2017-08`: 25, all other months ≤15 each.
- **Implication:** random splits leak the same Oct–Nov burst into train/test. Use **time-based split** (e.g. train ≤ 2017-11-15, test > 2017-11-15) + report per-month metrics. Do not treat as stationary.

## 4. Text-length distribution (200k sample)

Char length: mean 122.78, median 125.0, std 51.16, min 13, max 362, p25 92, p75 146, p90 182, p95 226.
Word count: mean 20.54, median 20.0, std 9.30, min 1, max 94, p25 15, p75 25, p90 31.

Histogram (chars): `0–50`: 15,580 (7.8%), `50–100`: 43,668 (21.8%), `100–140`: 79,897 (40.0%), `140–200`: 45,617 (22.8%), `200–280`: 13,588 (6.8%), `280+`: 1,650 (0.8%).

Short tail = confirmations (`Both`, `yes`, `yes any - houses…` needs context); long tail = multi-symptom complaints + outbound multi-sentence triage with 1–2 URLs.

## 5. Thread reconstruction (via `response_tweet_id` / `in_response_to_tweet_id`)

Method: undirected union-find over 200k-sample ids; `response_tweet_id` split on commas/semicolons/whitespace, `X.0` → `X` normalized; edge added only if endpoint id exists in sample.

- Threads found: **82,699**; size mean 2.42, median 2.0, min 1, max **268**.
- Size distribution: `1`: 24,168 (29.2%), `2`: 35,986 (43.5%), `3–5`: 17,752 (21.5%), `6–10`: 4,436 (5.4%), `11+`: 357 (0.43%).
- Links: response edges 133,259 total, 15,958 dangling (11.97%); in-response edges 149,521 total, 32,220 dangling (21.55%).
- Multi-response rows: 11,130 (5.57%) — e.g. `712,715`: agent fan-out or merged threads; needs deterministic resolution (prefer `in_response_to` chain, then smallest id).
- Direction markers: outbound starts with `@`: 99.93%; inbound starts with `@`: 81.35% (remainder are follow-upside messages without re-mentioning, e.g. `Both`, `yes , that is what i did`).
- Example chain shape (ids 696–700): `700(in,NaN→698) → 698(in,696→700) → 696(out,697→698) → 697(in,699→696) → 699(out,NaN→697)` — doubly-linked list with head `in_response=NaN` and tail `response=NaN`.

**Caveats:** (a) subsetting to Apple breaks cross-brand threads only marginally (Apple threads are self-contained); (b) the 200k subsample itself orphans ~2.3% of edges — full 204,772-thread rebuild is recommended for training; (c) 29% singletons are mostly heads/tails orphaned by sampling or deleted tweets — exclude singletons from next-response training, keep for intent classification with a `is_singleton` flag.

## 6. URLs / mentions / hashtags / emoji / language noise (200k sample)

- URLs (`https?://`/`www.`): **46.31%** rows (92,625). Manual check: near-all are `https://t.co/...` short links; outbound triage templates carry 1–2 links (`...DM us... https://t.co/GDrqU22YpT`), KB/workaround links (`...steps here: https://t.co/...`). Target URL unresolvable offline — treat as categorical signal, not content.
- Mentions (`@\w+`): **99.96%** rows, mean 1.12/tweet. Top: `@applesupport` 96,556; numeric user-ids `@115858` 9,531, `@116333` 678, `@115948` 587…; cross-brand `@att` 120, `@tmobilehelp` 118, `@upshelp` 111 (carrier-confusion / multi-tagging).
- Hashtags: **3.33%** rows (6,655), 2,768 unique. Top: `#ios11` 1,427, `#apple` 836, `#iphone` 642, `#iphonex` 490, `#help` 270, `#ios` 260, `#iphone7` 145… — sparse but high-precision intent signal (keep, don’t drop).
- Emoji (Unicode ranges incl. variation selector/Fitzpatrick): **7.07%** (14,139). Mostly inbound sentiment markers; outbound rarely uses emoji.
- Non-ASCII (any `ord>127`): **26.12%** (52,240) — dominated by smart punctuation (`’`, `“”`, `…`), `&amp;`-decoded `&` is ASCII but co-occurs; NOT primarily non-English.
- Replacement char `�` (U+FFFD): **0** in Apple subset (seen in other brands’ chunks — confirms Apple slice is encoding-clean).
- Non-Latin scripts (Cyrillic/Arabic/CJK/Thai/Korean regex): **0.085%**. Heuristic lexicon hits: Spanish-like (`gracias/hola/ayuda/que`) 689 (0.34%), French-like 117, Dutch-like 34. Apple slice is **overwhelmingly English** with a small multilingual tail.
- HTML entities observed: `&amp;`, `&gt;` (e.g. `Settings &gt; General &gt; Software Update`) — must unescape before tokenization.

## 7. Missing / duplicates

- Core fields (`tweet_id, author_id, inbound, created_at, text`): **0 missing**, 0 empty texts, 0 full-row dups.
- Link fields: `response_tweet_id` ~43.3% null (tail messages), `in_response_to_tweet_id` ~25.2% null (heads) — expected for chain endpoints, not a defect.
- `tweet_id` dups: 0. `text` dups: 2,904/200k (**1.45%**) — near-all are outbound canned templates (`Thank you for reaching out… DM…`, `backup then update to iOS 11.1.1…`, `Let us know if that fixes it…`). Keep for frequency/prior estimation; **deduplicate or cap per-template** for classifier training to avoid template overfitting.

## 8. Quality issues (actionable)

1. **Temporal burst bias** (95% in Oct–Nov 2017, iOS 11). Random split overstates generalization.
2. **Thread fragmentation**: 29% singletons + 12–22% dangling edges (partly sampling artifact, partly deleted/private tweets + multi-response fan-out `706,704`).
3. **Multi-response ambiguity** (5.57% rows): comma-joined forward links; no documented precedence.
4. **Template duplication** (1.45% exact-text dups, higher near-dup): outbound DM/KB templates dominate; will bias generative metrics (BLEU/ROUGE) if not capped.
5. **Identifier leakage**: numeric `@user` mentions (e.g. `@115858` ×9,531) — high-cardinality, privacy-sensitive; must mask.
6. **Short context-dependent turns** (`Both`, `yes…`, `iPhone 8 plus with iOS 11.1`): uninterpretable without thread window.
7. **HTML entities + smart quotes** inflate non-ASCII (26%) and break naive tokenizers.
8. **Shortened URLs**: all signal, no content (`t.co`); do not attempt live resolve in pipeline.
9. **Cross-brand mentions** (`@tmobilehelp`, `@att`): carrier-vs-Apple attribution ambiguity.
10. **Multilingual tail** (~0.5% ES/FR/NL + 0.085% non-Latin): keep for robustness testing, exclude from primary English-intent training or tag with `lang_proxy`.

## 9. Preprocessing plan (for intent + retrieval/response stages)

**P0 — structural (do first):**
1. `created_at` → UTC timestamp; add `month`, `is_burst (2017-10/11)`; time-split, never random-split.
2. Rebuild threads on the **full 204,772** union (not the 200k sample) with union-find; split multi-`response_tweet_id` on `[,;\s]+`, normalize `X.0→X`; resolve conflicts by preferring `in_response_to` chain, then lexicographically smallest forward id; emit `thread_id`, `turn_index`, `thread_len`, `is_singleton`, `has_dangling`.
3. Drop `is_singleton==True` threads from next-response/context training; keep for intent eval with flag.

**P1 — text normalization (apply identically at train/serve; store both `text_raw` and `text_norm`):**
4. Unicode NFKC + HTML-unescape (`&amp;→&`, `&gt;→>`, `&lt;→<`); strip zero-width/format chars; collapse whitespace; keep original in `text_raw`.
5. **Lowercase for modeling, keep case for display**: `text_norm=text_raw.lower()` after step 4. (Rationale: `iPhone/iOS` casing carries no intent signal beyond lexicon; lowercasing shrinks vocab ~8–12%. Keep `text_raw` for response generation/UX.)
6. `URL_RE (https?://\S+|www\.\S+) → <URL>`; add numeric feature `n_urls` (0/1/2+). Do NOT delete (46% prevalence; URL presence separates triage/KB replies from chit-chat; position matters — append `<URL>` in place).
7. Mentions: `@applesupport → <BRAND>`; any other `@\w+` (incl. numeric user ids) `→ <USER>`; add `n_mentions`, `has_cross_brand` (matches `@att|@tmobilehelp|@verizon|@sprint|@upshelp…`). Never leave raw numeric ids in model input.
8. Hashtags: **keep surface form** lowercased (`#ios11`, `#iphonex`) — 3.3% prevalence but high precision for `ios_update`/`device` intents; additionally add `has_hashtag` flag. Do not map to `<TAG>`.
9. Emoji: replace each match with ` <EMOJI> ` (single token per emoji cluster, preserve count up to 3, cap beyond) + `n_emoji` feature; do NOT strip (7% prevalence, sentiment/urgency signal: `wtf`, `?!`, 🙏/😡 clusters co-occur with complaints).
10. Punctuation: normalize smart quotes/dashes to ASCII (`’→'`, `“”→"`, `—→-`); keep `?`/`!` (urgency); cap character repetitions at 3 (`!!!!→!!!`, `soooo→sooo`).

**P2 — filtering/dedup/splits:**
11. Dedup: exact-`text_norm` group-by — for intent training cap each group at K=5 (keeps prior, kills template dominance); for retrieval eval keep one instance per template + separate template-frequency table. `tweet_id` is PK — assert uniqueness after every join.
12. Language: primary English training = exclude `nonlatin==True` + heuristic ES/FR/NL hits (~0.5%); keep them as a `noise_robustness` eval slice. No external lang-id dependency (none installed); revisit with `langdetect`/`fasttext-lid` if multilingual scope grows.
13. Context windows: model input = current tweet + up to 2 prior turns in same `thread_id` (covers `Both`/`yes…` follow-ups); ablate 0 vs 2 turns.

## 10. Intent taxonomy draft (11 intents, grounded in observed data)

Derived from 5,000-row sample keyword counts (inbound n=2,379: `iphone` 525, `ios` 442, `update` 412, `ios 11` 225, `fix` 228, `help` 185, `battery` 176, `issue` 134, `screen` 131…) + outbound template verbs (`DM` 1,380/2,621 outbound ≈53%, `update` 339, `let us know` 356, `restart` 83…) + hashtags (`#ios11` 1,427, `#iphonex` 490). All examples below are paraphrased patterns, not verbatim PII.

| # | Intent | Definition / triggers | Observed grounding |
|---|---|---|---|
| 1 | `battery_drain` | Rapid drain/heat/charging complaints, esp. post-update | `battery` 176, `drain` 50, `dying in 1/2 a day`, `drains to 0 in minutes`; outbound `battery life… check… DM iOS version` |
| 2 | `ios_update_help` | How to install/wait for update, beta notices, backup-before-update | `update` 412 (both sides), outbound `backup then update to iOS 11.1.1`, `Settings > General > Software Update`, `beta updates` |
| 3 | `post_update_regression` | New bugs after 11.x: freeze/slow/crash, keyboard/autocorrect (`I→?`), Touch/gesture | `ios 11` 225, `slow` 52, `freeze` 37, `crash` 55, `I's changing to ?'s`, `slow and freezes since 11.1`; `#ios11`, `#ios1103` |
| 4 | `connectivity` | Wi-Fi/Bluetooth/cellular/carrier, settings reset didn’t help | `wifi` 59, `bluetooth` 23, `went to EE… reset WiFi… didn’t help`; cross-mentions `@tmobilehelp/@att` |
| 5 | `device_hardware` | Model-specific/screen/power: won’t turn on, screen, storage, charger/watch/iPad/Mac | `screen` 131, `iphone` 525, `ipad` 51, `watch` 54, `mac` 93, `storage` 11; `iPhone 8 plus with iOS 11.1` (needs slot-fill) |
| 6 | `data_loss_backup` | Deleted texts/photos, backup/restore/iCloud recovery | `deleted/lost` ~15 each, `restore` 27, `backup` 17, `icloud` 47, `phone deleted all my texts` |
| 7 | `media_apps` | Music/App Store/downloads/iMessage/FaceTime/Siri playback or login | `shuffle but can't select songs`, `resume the downloads`, `itunes` 46, `app store` 20, `imessage` 21, `siri` 18, `facetime` 8 |
| 8 | `account_access` | Apple ID/password/locked/forgot (low-volume, high-risk) | `password` 19, `apple id` 15, `locked` 18, `forgot` 7 — route to DM, never ask secrets publicly |
| 9 | `troubleshoot_followup` | Short slot answers/confirmations mid-thread (`yes`, `both`, model+version) | `Both`, `yes, that is what i did`, anticipating-bugfix replies; 81% inbound start with `@` → rest depend on 1–2 prior turns |
| 10 | `gratitude_closure` | Thanks/confirmation fix worked | `Brilliant… worked a treat… Thanks`, outbound `We appreciate that, thank you!`; closure detector for thread-end |
| 11 | `complaint_escalation` | Formal complaint/carrier blame/highest-complaint, multi-tag | `highest complaint level in the UK`, `@187567 Same for me too`, `@att/@tmobilehelp` co-tags; route to human/DM + `has_cross_brand` |

Out-of-scope bucket (`other_vague`, e.g. single emoji, dato-only `iPhone 8 plus…`) → low-confidence fallback to DM-triage template (outbound `DM us + which iOS/iPhone` covers ~53% of agent turns and is the safe default action).

**Suggested label workflow:** weak-label with keyword+hashtag rules above → human-adjudicate 300–500/thread-complete conversations (never singletons alone) → train classifier on `text_norm` + 2-turn context + `n_urls/has_hashtag/n_emoji` features; report per-intent F1 + burst-month slice.

## 11. Reproducibility + next steps

- Repro: re-run `.venv\Scripts\python.exe scripts/apple_inspect_tmp.py` (full-scan union → 200k `seed=42` analysis → `STATS_JSON` + 5k sample). All paths under `.` only.
- Next (downstream agents): time-split threads → apply §9 normalization → weak-label §10 → adjudication sample → baseline TF-IDF+LogReg / MiniLM classifier before any LLM fine-tune.
- Limitations: `t.co` targets unresolved; 200k-sample thread stats understate true thread lengths by ~2–3% (rebuild on full 204,772 for training); multilingual labels are heuristic (no `langdetect` installed); sentiment/urgency not yet scored.
