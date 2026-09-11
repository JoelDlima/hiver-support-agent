# Kaggle + HuggingFace Scan — Twitter Support Agent Differentiation (Hiver @ C:\Hiver)

**Date:** 2026-09-10 | **Track:** competitors / notebook-grade baseline scan
**Brief:** Same brief for everyone (Twitter support agent). This track owns Kaggle + HF scan.
**Searches:** 10 websearch queries (see §5). All findings from websearch excerpts + HF dataset cards; no invented numbers.

## 1. Executive summary

Notebook-grade work on `thoughtvector/customer-support-on-twitter` (2.8M tweets) clusters into one pattern: **EDA + sentiment + BERT 0.9-claim on a curated/balanced/synthetic-label subset**. The two main HF mirrors (`MohammadOthman/mo-customer-support-tweets-945k`, `TNE-AI/customer-support-on-twitter-conversation` 794k rows) are **repackagings of the same TWCS source, not new labels** — no intent labels, no escalation labels, no grounding annotations, no judge-agreement study.

What notebooks typically do (verified across top results):
- EDA: inbound volume per brand, response-time medians, word counts, sentiment distributions.
- Preprocessing recipe: lowercasing, URL/mention strip, emoji removal (1624-list), punctuation strip, stopword removal, stemming/lemmatization.
- Sentiment or keyword-intent classification with a single accuracy number (BERT/DistilBERT/RoBERTa 0.76–0.998 on curated or synthetic-label splits).

What they never do (gap = our differentiation):
- No escalation policy (no auto-handle vs escalate decision, no precision/recall on escalate, no safety recall).
- No grounding (no retrieval citation, no faithfulness/groundedness score, no abstain-on-empty-retrieval).
- No judge↔human agreement (no κ, no swap-consistency, no bias report).
- No misleading-number disclosure (0.99-style claims reported without noting synthetic/curated-label circularity).

Hiver beats notebook-grade on exactly those four axes with: **Apple KB 89,694 deduped outbound replies (template cap K=5, `scripts/build_kb.py`, verified by local row count)** + **dual golden (200 weak-draft `golden_v1.csv` + 200 human-reviewed `golden_human_200.csv` = 60 blind-manual + 140 rulebook-assisted, 39/60 flips, weak-vs-human κ=0.465)** + **safety recall 0.909 on 11 legal_safety cases with esc F1 0.582 (`evaluation/JUDGE_AGREEMENT_V2.md`)** + **published circularity disclosure (keyword 1.000 on weak-200 is tautological; trustworthy ceiling is human-60)**.

## 2. Comparison table (notebook-grade vs Hiver)

| # | Artifact (type) | What it does | Labels / eval | Reported number (with caveat) | What it never does | Hiver delta |
|---|---|---|---|---|---|---|
| 1 | Kaggle `thoughtvector/customer-support-on-twitter` (source dataset, 2.8M, CC BY-NC-SA 4.0, 7 cols) | Raw tweets + replies, thread via response/in_response_to IDs | No intent / resolution / CSAT labels | n/a (source) | No task definition | Hiver builds task on top: 11-intent taxonomy + 4-trigger escalation + grounded draft + dual golden |
| 2 | Kaggle top notebooks: `Getting started with Text Preprocessing` (1847▲), `Sentimental Analysis Using Naive-Bayes` (338▲), `Customer Support meets Spacy` | EDA + cleaning recipe (lower/URL/emoji/stop/stem) + sentiment demo | No held-out intent eval | n/a (recipe, not classifier) | No escalation, grounding, judge, disclosure | Hiver reuses recipe (`src/text_norm.py`) but adds decision head + eval harness |
| 3 | Kaggle/HF pattern: `haneenhossam/customer-support-twitter-preprocessing-modelling`, `naman-tiwari/Customer-Support-on-Twitter`, `amruta33/Customer-Support-on-Twitter`, `yash9516/Customer_Support_Analysis` | Preprocess (emoji 1624-list, punctuation/URL strip, misspell fix) → sentiment / topic-model / seq2seq demo | Sample/100k subset, no human labels | Qualitative only | No intent taxonomy, no escalation, no grounding metric | Hiver: same preprocessing lineage, plus 11-intent weak→human pipeline with κ |
| 4 | Kaggle sentiment/BERT pattern: `AhmedAbdAlkreem/Sentiment-Analysis` (BERT), `avulaankith/Twitter-Sentiment-Analysis` (BERT/CNN/LSTM/BiLSTM), `ubaidshah/twitter-sentiment-analysis`, `siddharthmandgi/twitter-sentiment-analysis` | Sentiment classification (pos/neu/neg) on balanced Twitter sample | Curated/balanced split (e.g. 25k+25k Sentiment140 sample) | BERT ~0.76 acc (AhmedAbdAlkreem, 3-class); fusion BERT-CNN/LSTM "superior" (no pinned numbers) | Sentiment ≠ intent ≠ action; no escalation/grounding/judge | Hiver: 11 action-oriented intents (not sentiment); reports per-intent P/R/F1 + confusion (`evaluation/PER_INTENT.md`, `confusion_human60.csv`) |
| 5 | HF `MohammadOthman/mo-customer-support-tweets-945k` (945k rows, CC BY-NC-SA 4.0, input/output strings) | TWCS repackaging for fine-tuning (conversational pairs) | No intent/escalation labels; license inherits NC-SA | n/a (data only) | No eval, no labels beyond pairs | Hiver uses primary `twcs.csv` 2.8M directly (kagglehub) + builds own Apple KB; 945k mirror adds no label value |
| 6 | HF `TNE-AI/customer-support-on-twitter-conversation` (794,335 rows, 217 MB, conversation_id/company/conversation/summary) | TWCS repackaging into conversations (109 companies) | README empty; no label schema | n/a (data only, 216 downloads/mo) | No intent/grounding/escalation annotations | Hiver: thread reconstruction is inbound→response + AppleSupport filter (204k union per data_quality scan), not generic conversation dump |
| 7 | HF `Vishesh062/customer-support-tweet-classifier` (DistilBERT 67M, 7 classes) — **cautionary tale** | Fine-tuned `distilbert-base-uncased` on 50k stratified TWCS | **Synthetic keyword labels**; held-out 307,569 tweets | Acc 0.995, macro F1 0.991, weighted 0.994 **(author admits: "keyword detector with extra steps")** | No human annotation, no OOS handling, no escalation/grounding/judge | Hiver discloses same circularity in own weak-200 (keyword 1.000/1.000 tautological) and reports trustworthy human-60 instead (keyword 0.517 / final 0.433) |
| 8 | HF `vineetsharma/customer-support-intent-albert` (ALBERT 11.7M, Bitext synthetic) + `Dragneel/ticket-classification-v1` (DistilBERT, 4 classes, 94.85%) | Intent classification on synthetic/clean ticket data | Curated balanced set, not Twitter brevity/noise | ALBERT 0.9988 acc; Dragneel 0.9485 acc | 0.9+ only on clean curated sets; no Twitter slang/mention/DM-handoff handling; no escalation | Hiver: Twitter-native (mention/DM/short-fragment/link-only rules), single-brand AppleSupport, temporal-cutoff honesty |
| 9 | HF `cardiffnlp/twitter-roberta-base-sentiment` (RoBERTa-base, 58M tweets pretrain, TweetEval) / `-latest` (124M tweets) | Twitter-pretrained sentiment (Neg/Neu/Pos) | TweetEval benchmark | Micro/macro F1 ~0.71 on TweetEval-sentiment (self-reported `cardiffnlp/roberta-base-sentiment` card); NOT 0.9+ on raw support traffic | Sentiment only; short-text subjectivity caps real-world F1 (~0.80–0.83 even in 2025 short-text studies, not 0.9+) | Hiver cites twitter-roberta + hashtag/emoji handling as T1 encoder option (academic_review) but does not claim 0.9+ on support intents |
| 10 | Banking77 / SetFit literature (Casanueva BERT 93.6% full / 85.1% 10-shot; Loukas SetFit MPNet-v2 10-shot 88.1 μ-F1 / 20-shot 91.2; Ying-Thomas 1,428/14% label errors, +4.5% F1 after trim; ibra-dotcom 90.8% DistilBERT with overlap-driven errors) | Fine-grained intent SOTA + few-shot method | Human labels BUT banking domain, overlapping semantics (pending_transfer vs pending_card_payment, etc.) | 0.9+ valid **in-domain curated**; errors driven by label overlap not capacity | Banking77 ≠ Twitter; overlap lesson rarely applied in notebooks (no consolidation/hierarchy/clarify-fallback) | Hiver: Banking77 inspected for **intent design only** (README: "not used for training, insufficient Twitter overlap"); applies overlap lesson via 11 coarse mutually-exclusive intents + Other catcher + confidence→clarify/escalate |

## 3. What notebooks typically do (pattern, with sources)

1. **EDA first, eval last (or never).** Inbound volume top-20 brands, response-time medians (AppleSupport ~106k replies, median ~71 min per JJtheNOOB/abh2050 recounts), sentiment/entity distributions, LDA topic viz (`yash9516/Customer_Support_Analysis`). Modeling stops at a demo.
2. **Fixed preprocessing recipe.** Lowercase → URL/mention → emoji (1624 Unicode v6.0 list) → punctuation → misspell → retweet-symbol strip (`naman-tiwari` README; `Getting started with Text Preprocessing`). Hiver keeps this lineage in `src/text_norm.py`.
3. **Sentiment as proxy for support quality.** Naive-Bayes/TF-IDF-LogReg/BERT on balanced pos/neg samples (Sentiment140 25k+25k pattern in `fajardgb`/`Jeremyhudsonchan`). Sentiment answers "tone?" not "what action?".
4. **BERT 0.9-claims on curated or synthetic sets.** ALBERT 0.9988 (Bitext synthetic), DistilBERT 0.995 (keyword labels, self-flagged as circular), ticket-classifier 0.9485 (4 clean classes), Banking77 0.936 (curated banking). None transfer to raw AppleSupport Twitter fragments without a drop — Hiver measures the drop openly (weak 0.795 → human-60 0.433 for final; keyword 1.000 → 0.517).
5. **Single accuracy number, no per-intent / OOS / escalation table.** No `classification_report` with fixed 11-class order, no confusion matrix, no OOS recall (cf. `aniqua14/intent-classifier` OOS R 58% collapse — same trap notebooks ignore).

## 4. What they never do (four gaps = Hiver differentiation)

| Gap | Notebook status | Hiver answer (verified local path) |
|---|---|---|
| **Escalation** | Zero notebooks reviewed emit auto-handle vs escalate with reason + P/R. Best case is a template Slack ping (`DecentralizedJM` Mudrex intern, not a notebook). `simple-keyword` never escalates (esc F1 0.000 on human-60). | 4-trigger head (can't-ground / policy-risk / frustration / explicit-human-request) + ladder; final esc F1 0.424 (P 0.368/R 0.500) on human-60, 0.639 on weak-200; **safety recall 0.909** (10/11 legal_safety) in `evaluation/JUDGE_AGREEMENT_V2.md`; misses in `evaluation/FAILURE_TESTS.md` F1–F8 |
| **Grounding** | No retrieval citation, no faithfulness score, no abstain path. RAG demos (`ejazalam831`, k=2 MiniLM+Chroma) claim "eliminates hallucinations" with no metric. | Apple KB **89,694 rows** (`data/processed/apple_kb.csv`, outbound AppleSupport deduped, template-cap K=5) + TF-IDF NN top-5 with passage IDs + template-behind-contract; groundedness mean 4.75/100% ≥4 on weak-200 (heuristic, disclosed as circular-by-design); span-attribution + NLI gate queued week-2 |
| **Judge agreement** | No κ / swap-consistency / verbosity-bias report anywhere in notebook corpus. | Rubric `evaluation/rubric.md` (5 dims, groundedness+safety gates) + ship-gate (weighted-κ ≥0.60 AND safety-FAIL recall ≥0.90) + 75-pair blinded protocol (academic_review); current heuristic advisory-only, LLM judge gated — zero LLM-judge scores claimed |
| **Misleading disclosure** | 0.99-style numbers reported without label-caveat (except Vishesh062 author note). | `docs/FINAL_REPORT.md` §§16–18 + `evaluation/BASELINE_VS_FINAL.md` + `GOLDEN_NOTE.md`: weak-200 circularity explicit ("eval labels ARE keyword outputs"); headline = human-60 + escalation + groundedness, never weak accuracy; weak-vs-human κ 0.465 / esc κ 0.015 published |

## 5. Queries run (10)

1. `Kaggle customer-support-on-twitter notebooks intent classification EDA` → dataset card (3M, 7 cols, CC BY-NC-SA) + `integratedhero`, `haneenhossam`, `scodepy/customer-support-intent-dataset`.
2. `Kaggle customer support twitter sentiment analysis BERT accuracy notebook` → Sentiment140 1.6M pattern, `AhmedAbdAlkreem` BERT 0.76, `avulaankith` BERT-fusion, `fajardgb` 25k+25k sample.
3. `HuggingFace mo-customer-support-tweets-945k dataset` → card: 945k rows, input/output strings, CC BY-NC-SA 4.0, fine-tune repackaging, no intent labels.
4. `HuggingFace TNE-AI customer-support-on-twitter-conversation 794k dataset` → card: 794,335 rows, conversation_id/company/conversation/summary, 217 MB, empty README, no labels.
5. `Banking77 intent overlap handling label confusion` → Ying-Thomas 14% errors/+4.5% F1; ACM resource-limited (overlap groups, TopUp Failed vs Reverted); ibra-dotcom 90.8% + confusion pairs.
6. `SetFit few-shot intent classification Banking77 8-shot accuracy` → Tunstall SetFit 8-shot ≈ full-tune; Loukas MPNet-v2 SetFit 1/3/5/10/20-shot table (57.4→91.2 μ-F1); Casanueva baseline 93.6 full / 85.1 10-shot.
7. `Vishesh062 customer-support-tweet-classifier DistilBERT keyword labels 99 percent` → card: 50k stratified, 307k held-out, 0.995/0.991/0.994 + author limitation "synthetic keyword matching… keyword detector with extra steps".
8. `twitter-roberta-base-sentiment short text classification accuracy curated balanced` → 58M-tweet pretrain + TweetEval; self-reported F1 ~0.71 on TweetEval-sentiment; 2025 short-text studies ~0.80–0.83 F1, subjectivity-capped.
9. `customer support chatbot escalation grounding hallucination evaluation missing Kaggle` → `ejazalam831` RAG (k=2, no metric); HalluDetect F1 68.9; support-hallucination user-impact study; EvalView tool-verify + grounding-check pattern.
10. `Kaggle Getting started Text Preprocessing customer support twitter top notebook EDA sentiment` → 1847▲ preprocessing recipe; `haneenhossam` TWCS preprocessing&modelling; beginners-guide TF-IDF/BOW/sentiment pattern.

## 6. How Hiver beats notebook-grade (claim → evidence, all inside C:\Hiver)

- **Apple KB 89k deduped > no-KB generative demos.** `scripts/build_kb.py` (outbound AppleSupport, clean-len>10, exact-clean template cap K=5) → `data/processed/apple_kb.csv` **89,694 rows** (counted 2026-09-10) + `apple_inbound_pool.csv` (~97k). Notebooks have no KB; RAG demos use k=2 generic FAQ. Hiver retrieves top-5 TF-IDF NN with passage IDs (p50 ~35ms) over Apple-only resolutions.
- **Dual golden 200 (60 manual) > 0 human labels.** `evaluation/golden_v1.csv` (200 stratified weak-draft, seed 7) + `evaluation/golden_human_60.csv` (60 blind-manual, 39 flips) + `evaluation/golden_human_200.csv` (200 = 60 manual + 140 rulebook-assisted via `scripts/human_review_200.py` + `spotcheck_30.csv` audit). Weak-vs-human: intent acc 0.517, κ 0.465; esc κ 0.015 (heuristic labels ~random) — published in `GOLDEN_NOTE.md`.
- **Safety recall 0.909 + esc F1 > never-escalate.** `JUDGE_AGREEMENT_V2.md`: 11 human legal_safety cases, system recall **0.909** (gate ≥0.90 PASS); esc vs human acc 0.835 κ 0.487 P 0.469 R 0.767 F1 **0.582** (n=200); human-60 esc F1 **0.424** vs keyword 0.000. Keyword "wins" intent on human-60 (0.517 vs 0.433) only because it reproduces weak labels; final wins the production-relevant heads (escalation + groundedness + p50 180ms/p95 192ms).
- **Disclosure > 0.9-claims.** Every Hiver report carries a "What is misleading" section naming weak-200 circularity and the true ceiling (weak-vs-human 0.517). No notebook reviewed does this except the Vishesh062 author note — which Hiver cites as precedent.

## 7. Honest limits (ours)

- n=60 single-annotator (AI-as-annotator), no inter-annotator κ yet; CIs ±0.12 on acc. Next: double-label 60 + full-200 human + adjudication (`GOLDEN_NOTE.md`).
- Groundedness 4.75/1.000 is heuristic-shaped (DM+diagnostic+length+cite), not span-grounded; LLM judge gated, not shipped.
- Apple KB dedup is exact-clean cap only (no cosine>0.7 near-dedup yet); temporal cutoff frozen at 2017 (iOS11/iPhoneX era); English-only v1.
- Banking77/SetFit numbers above are literature values, not Hiver runs — cited for method license only.

## 8. Sources (key URLs)

- TWCS Kaggle: https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter
- HF 945k: https://huggingface.co/datasets/MohammadOthman/mo-customer-support-tweets-945k
- HF 794k: https://huggingface.co/datasets/TNE-AI/customer-support-on-twitter-conversation
- Vishesh062 classifier: https://huggingface.co/Vishesh062/customer-support-tweet-classifier
- ALBERT intent: https://huggingface.co/vineetsharma/customer-support-intent-albert
- Ticket classifier: https://huggingface.co/Dragneel/ticket-classification-v1
- twitter-roberta-sentiment: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment
- TweetEval paper: https://arxiv.org/abs/2010.12421
- Banking77 HF: https://huggingface.co/datasets/PolyAI/banking77
- Label Errors (Ying & Thomas 2022): https://aclanthology.org/2022.insights-1.19
- Making LLMs Worth Every Penny (Banking77+SetFit): https://arxiv.org/pdf/2311.06102 and https://dl.acm.org/doi/fullHtml/10.1145/3604237.3626891
- Breaking the Bank with ChatGPT (SetFit SOTA): https://arxiv.org/abs/2308.14634
- SetFit docs: https://huggingface.co/docs/setfit/index and https://github.com/huggingface/setfit
- Banking77 held-out ProtoNet (2026): https://github.com/victor201202/banking77-heldout-intent-benchmark
- ibra-dotcom Banking77 90.8% + overlap analysis: https://github.com/ibra-dotcom/banking77-intent-classifier
- Preprocessing lineage: https://github.com/naman-tiwari/Customer-Support-on-Twitter, https://github.com/yash9516/Customer_Support_Analysis, https://www.kaggle.com/code/sudalairajkumar/getting-started-with-text-preprocessing
