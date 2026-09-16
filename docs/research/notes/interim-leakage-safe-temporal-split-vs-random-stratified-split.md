---
title: Interim - leakage-safe temporal split vs random stratified split
id: interim-leakage-safe-temporal-split-vs-random-stratified-split
tags:
- hiver-support-agent-audit-6d951f
- locus-leakage-safe-temporal-split-vs-random-stratified-split
created: '2026-09-15T02:42:11.658221Z'
status: draft
type: interim
deprecated: false
---

# Interim investigator report — leakage-safe temporal split vs random stratified split

Locus: `leakage-safe-temporal-split-vs-random-stratified-split` | run: `hiver-support-agent-audit-6d951f` | step 5 depth-investigator.
Question: does the golden set + eval need conversation-disjoint temporal splits, or does random stratified tweet sampling suffice?

## 1. What the width corpus establishes

**Thread structure exists in the raw data and survives in some derivatives, not others.**
The canonical Kaggle schema (`tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id`) supports full thread reconstruction [[customer-support-on-twitter-openbigdataorg]]. The TNE-AI conversation derivative preserves it explicitly (`conversation_id, company, conversation`, 794k rows) [[tne-aicustomer-support-on-twitter-conversation-datasets-at-hugging-face]]. The 945k input-output-pair derivative DESTROYS it: multi-turn threads are distilled to isolated pairs with slang/emoji/URL normalization [[mohammadothmanmo-customer-support-tweets-945k-datasets-at-hugging-face]] — convenient for fine-tuning, unusable for leakage auditing. Lesson: any pipeline step that flattens threads to pairs silently removes the grouping key the split must respect.

**Three exact leakage mechanisms named in the locus brief are all real on this data:**
(a) same-thread overlap — consecutive turns share entities, phrasing, and resolution state; a classifier or retriever that saw turn k-1 "knows" turn k;
(b) retrieval of the target response — the KB is brand outbound tweets, i.e. it contains the gold answer to many eval queries;
(c) future-data-answering-past — support policy, outage status, and links drift over the 2017 window, so training on later tweets to answer earlier ones is Kapoor L3.1 temporal leakage verbatim.

**IID vs OOD gap is measured, not theoretical.** Across 17 datasets × IID/OOD/adversarial, no selective-prediction method consistently beats MaxProb and gains do not transfer across tasks/settings; MCD wins duplicate-detection but fails NLI, especially OOD [[investigating-selective-prediction-approaches-across-several-tasks-in-iid-ood-an]]. Standard deployment metrics are risk–coverage/AURC with MaxProb as the mandatory floor [[selective-prediction-tasks]]. The OOD survey frames this as generalized OOD detection: deployment on new threads/time is an OOD problem, and IID-only numbers do not license deployment claims [[211011334-generalized-out-of-distribution-detection-a-survey]].

## 2. New depth evidence (5/7 fetch budget used)

- **Kapoor & Narayanan leakage taxonomy (arXiv:2207.07048, 986 citations)** defines exactly our two load-bearing failure modes: **[L3.1] Temporal leakage** — "the test set should not contain any data from a date before the training set"; **[L3.2] Non-independence between train and test** — split "should account for the dependencies in the data," explicitly recommending **block cross-validation** that partitions on the dependency structure [[220707048-leakage-and-the-reproducibility-crisis-in-ml-based-science]]. Threads are the blocks here. Survey scope: 329 papers across 17 fields with wildly overoptimistic conclusions from these errors.
- **Rosenblatt et al., Nature Communications 2024** measures the inflation: leakage via **repeated subjects drastically inflates prediction performance**, and **small datasets exacerbate leakage effects** [[data-leakage-inflates-prediction-performance-in-connectome-based-machine-learnin]]. Direct analog: same-thread tweets = repeated subjects; golden n=150–250 = small dataset. Both risk multipliers are present simultaneously.
- **Sasse et al., J. Big Data 2025** systematizes leakage across the whole ML pipeline (design → implementation → evaluation), reinforcing that split design is a design-phase control, not a post-hoc fix [[overview-of-leakage-scenarios-in-supervised-machine-learning-journal-of-big-data]].
- **sklearn GroupShuffleSplit docs**: the canonical mechanism — split on a third-party `groups` array (here: `thread_id`), where test/train fractions refer to *groups, not samples*, guaranteeing group-disjointness [[groupshufflesplit-scikit-learn-191-documentation]].
- **sklearn TimeSeriesSplit docs**: for time-ordered data, standard CV "would lead to training on future data and evaluating on past data"; train sets are supersets of the past, test is the next fold, with a `gap` parameter to exclude boundary-adjacent samples [[timeseriessplit-scikit-learn-191-documentation]]. The `gap` maps to our no-straddle rule at the temporal cutoff.

## 3. Forensic measurements on the CURRENT workspace (untrusted implementation)

Measured 2026-09-15 against `data/processed/*` and `evaluation/*` (Apple = headline brand):

1. `apple_inbound_pool.csv` (97,592 rows) columns = `tweet_id, author_id, inbound, text, clean`. **No `thread_id`, no `created_at`.** Conversation-disjoint or temporal splitting is *impossible* from this artifact; the grouping key was dropped upstream.
2. `evaluation/golden_v1.csv` (200 rows) columns = `text, intent, escalate, escalate_reason`. **No `tweet_id`, no `thread_id`, no timestamp — provenance untraceable.** Overlap with KB/few-shot set is unauditable by construction. (Also: weak keyword labels, seed 7, per GOLDEN_NOTE.md — circular with the simple baseline.)
3. **200/200 golden texts match pool texts verbatim.** Golden was drawn from the same population that feeds training/retrieval.
4. `apple_kb.csv` (89,694 rows) is **100% outbound (`inbound=False`)** with `tweet_id` preserved — i.e. the KB structurally contains the brand's gold responses, while golden queries are inbound from the same brand threads. Verbatim golden-query-text in KB = 0/200 (expected — opposite direction), but **same-thread target-response containment cannot be checked** because neither artifact carries `thread_id`. The highest-value contamination (retriever fetching the exact gold answer → judge sees near-perfect groundedness) is currently *unmeasurable*, which is itself the finding.
5. Positive control: `virgin_threads.parquet` (65,346 rows) **already has** `thread_id, created_at, position_in_thread, thread_size, gap_split` — the thread-preserving recipe exists in-repo but was not applied to the headline Apple pipeline.

Conclusion: the current headline numbers (whatever they are) sit on a random tweet-level stratified split with no disjointness, no temporal order, no retrieval exclusion, and no provenance. Under Kapoor L3.1+L3.2 + Rosenblatt inflation, they must be treated as **upper bounds, not deployment estimates**.

## 4. Analysis — why random stratified sampling fails here, specifically

- **Unit-of-analysis error.** Random stratified sampling treats correlated turns as i.i.d. Tweets within a thread share author, entity, and discourse state; intent labels and escalation status propagate within threads. Stratifying tweets (not threads) balances labels while scattering same-thread turns across train/golden — exactly L3.2.
- **Retrieval contamination is directional.** For RAG reply generation, the leak is not query-in-KB but *answer-in-KB*: the eval query's own thread response sits in the index. Random splits maximize this (every thread's turns spray across pool and KB). Only thread-aware KB construction + same-thread exclusion at eval time closes it.
- **Temporal validity of the trust claim.** The report must convince evaluators the agent is "good enough to trust" in deployment = on *future* messages. A random split answers "how well do we interpolate the 2017 snapshot," including future-answers-past (L3.1). Varshney shows IID→OOD degradation is the norm; the golden set should BE the OOD slice (later time window), not a random IID slice.
- **Counter-case (steelman):** random stratified suffices IF the claim is explicitly scoped to "performance on the static 2017 snapshot distribution" AND thread-disjointness holds AND retrieval exclusion holds. But that scoped claim is nearly worthless for the assignment's trust argument, and the current implementation does not even meet the AND-conditions. Cost of temporal+grouped: slightly worse intent balance in golden (rare intents thin in the late window) — handled by stratifying *threads within the post-cutoff window* with one documented backfill exception rule, not by abandoning the design.

## 5. Exact split recipe (implementable from raw `twcs.csv`)

1. **Rebuild with linkage.** Brand slice from raw `twcs.csv` preserving `tweet_id, author_id, inbound, created_at, text, in_response_to_tweet_id, response_tweet_id`. Never drop these columns downstream (pool, KB, golden all carry `tweet_id, thread_id, created_at`).
2. **Thread reconstruction.** Connected components over the reply graph → `thread_id`; thread start = min `created_at`; record `position_in_thread, thread_size`. Quarantine orphans (no linkage) into a separate stratum, excluded from golden.
3. **Near-dupe collapse (Kapoor L1.4).** Normalized-text exact match + SimHash/embedding threshold to flag template replies and reposts *across* threads; keep one representative for golden eligibility, mark the rest train/KB-only.
4. **Temporal cutoff.** Sort threads by start time. `KB + classifier-train + few-shot ≤ T1 < golden/eval window`. No thread straddles T1 (assign by start time). Golden (150–250) sampled ONLY post-cutoff. This makes the headline a forward-looking claim.
5. **Conversation-disjointness everywhere.** All train/dev/test partitions via group-aware split (`groups=thread_id`, GroupShuffleSplit semantics); assert zero thread overlap between golden and any train/KB/few-shot artifact in the harness (fail-closed assertion). Report author overlap separately.
6. **Retrieval-corpus exclusion.** KB = pre-cutoff outbound only. At eval, exclude any KB doc from the query's own thread (defense in depth against linkage errors). Report groundedness/judge scores **with and without** the exclusion as a leakage diagnostic in the "misleading headline" section.
7. **Stratification (subordinate to 4–6).** Stratify *threads* within the post-cutoff window by weak-intent bucket + escalate flag + thread-size bucket; accept approximate balance. If a rare intent is unfillable post-cutoff, backfill from the latest pre-cutoff threads for that stratum ONLY, and disclose counts per stratum in the golden note.
8. **Provenance.** Golden CSV columns: `tweet_id, thread_id, created_at, text, intent, escalate, escalate_reason, stratum`. Re-run the overlap assertions on every harness invocation.

## Committed position

Random tweet-level stratified sampling is **insufficient and must be replaced**: the golden set and eval MUST be conversation-disjoint (split unit = thread via `thread_id` group partitioning, fail-closed zero-overlap assertion) AND temporally posterior (KB/train/few-shots strictly pre-cutoff, golden strictly post-cutoff, no straddling threads), with retrieval-corpus exclusion (KB = pre-cutoff outbound only + same-thread doc exclusion at eval, reported with/without as a diagnostic) and thread-level — not tweet-level — stratification with provenance columns (`tweet_id, thread_id, created_at`) on every artifact. Justification: measured workspace forensics (no thread/time keys, 200/200 golden-in-pool, unauditable target-in-KB) plus Kapoor L3.1/L3.2 block-design requirement, Rosenblatt's measured inflation from repeated-subject leakage amplified in small eval sets, and Varshney's IID→OOD degradation result — together they make the current numbers unlicensable as trust evidence. Confidence: **high** on conversation-disjointness and retrieval exclusion (mechanism + measurement agree); **medium-high** on the temporal cutoff (required if the claim is deployment trust, which the assignment demands; a purely snapshot-scoped claim could waive it, but that claim is worthless here). What would change my mind: a controlled ablation on the rebuilt threaded data showing <2pp delta on intent accuracy AND on judge-groundedness (exclusion on/off) between random-stratified and the leakage-safe recipe, with CIs from the agreed agreement-gated judge — i.e., evidence the leak is negligible, not assertion.
