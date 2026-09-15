---
title: Interim — setfit-vs-llm-intent-with-uncertainty-routing
id: interim-setfit-vs-llm-intent-with-uncertainty-routing
tags:
- hiver-support-agent-audit-6d951f
- locus-setfit-vs-llm-intent-with-uncertainty-routing
created: '2026-09-15T02:40:48.429573Z'
status: draft
type: interim
deprecated: false
---

# Interim — setfit-vs-llm-intent-with-uncertainty-routing (depth-investigator)

corpus_tag: hiver-support-agent-audit-6d951f
locus: setfit-vs-llm-intent-with-uncertainty-routing
question: Can SetFit-first with MC-dropout uncertainty routing to an LLM match native-LLM few-shot intent accuracy on noisy Twitter text at a fraction of cost and latency?

Inputs read (full text): intent-detection-in-the-age-of-llms (Arora et al. 2024 EMNLP-Industry / arXiv:2410.01627); making-llms-worth-every-penny (Loukas et al. ICAIF 2023 / arXiv:2311.06102); 230814634-breaking-the-bank (Loukas et al. FinNLP 2023 preprint); 220911055-efficient-few-shot-without-prompts (Tunstall et al. SetFit); effectiveness-of-pre-training-for-few-shot-intent (Zhang et al. IntentBERT 2021); data-augmentation-for-intent-with-off-the-shelf-LLMs (Sahu et al. NLP4ConvAI 2022); github-huggingfacesetfit; polyaibanking77 dataset card. Additional fetches (6 of 8 budget): FrugalGPT (arXiv:2305.05176); BERTweet (ACL 2020 EMNLP-demos.2); Beyond-the-Known OOD-LLM eval (arXiv:2402.17256); Dropout-as-Bayesian-approximation (arXiv:1506.02142); plus in-vault selective-prediction notes (Varshney et al. 2022 Findings ACL; Art-of-Abstention). Two mistaken fetches (wrong arXiv IDs) consumed budget without evidence; HINT3 direct fetch skipped — HINT3 details taken from Arora tables.

## 1. What the controlled numbers actually say

**Arora et al. 2024 (the load-bearing hybrid paper — 7 LLMs × SetFit on 6 real TODS datasets: HINT3 SOFMattress/Curekart/PowerPlay11 + internal AID3 ALC 8-intent / ADP 13-intent / OADP shift):**
- SetFit baseline (MPNet + linear/sigmoid head, Optuna-tuned): avg F1 0.600 at p50 latency 0.030s.
- + Negative augmentation (KeyBERT keyword remove 50% / replace-with-random-5-char 50%, |U|=0.2|D|): 0.600 → 0.658 avg F1 (**>+5%**, replicated across datasets). Still ~8 pts behind best LLM (Claude v3 Haiku avg 0.736; Mistral Large 0.735).
- Native best LLM latency: Haiku 1.697s p50, Sonnet 4.592s, v2 11.795s. **SetFit ~56× faster than Haiku** (0.030 vs 1.697).
- Hybrid (SNA + MC-dropout variance routing to Haiku/Mistral-L, M=5/10/20, dropout 0.1): M=10 + Haiku → 0.696 avg incl. OADP / 0.737 ex-OADP vs native Haiku 0.736/0.760. **Gap ~2% ex-shift, ~4% incl. shift, at ~50% latency cut** (0.748–1.005s vs 2.345s native; routed fraction 0.32–0.43). M=5 already captures most gain; M=10→20 flat. Batched MC sampling would cut further (authors did sequential).
- Routing rule (App. A.2): M stochastic forwards; uncertain iff number of distinct argmax predictions >1 OR < M/2 (upper cap for stability). Variance proxy, not calibrated probability.
- OOS is bad for everyone: OOS-recall@best-F1 avg — Mistral-L 0.641, Haiku 0.601, SNA 0.489, baseline SetFit 0.378. **Shift kills SetFit most**: ADP→OADP F1 drop ~15% for SetFit vs smaller for LLMs. Two-step LLM-internal-rep OOS fix: >+5% overall on HINT3 at +~300ms V100 encode cost, but in-scope accuracy drops — threshold-tunable tradeoff.

**Loukas et al. ICAIF 2023 / FinNLP 2023 (Banking77, 77 intents, 3,080 test queries — the cost paper):**
- 1-shot: GPT-4 80.4 micro-F1 ($620) vs Claude 2 76.8 ($15) vs MPNet-SetFit 57.4 (local). 3-shot: GPT-4 83.1, MPNet 76.7. Full SetFit (10–20/class) 91.2 vs full-data fine-tune 94.1. GPT-3.5 *drops* 1→3-shot (lost-in-the-middle, 4k context).
- Representative (expert-picked) > random demos, always.
- **Dynamic/RAG few-shot (retrieve top-K=5/10/20 by MPNet cosine, 1 call per query): Claude 2 K=20 → 85.5% at $42 BEATS GPT-4 classic 3×77=231 demos 83.1% at $740.** Both cheaper AND better. Classic N-shot over 77 classes hits context/cost wall.
- Rule of thumb: **>5 examples/class → fine-tune MPNet/SetFit; <5 → LLM.** Synthetic GPT-4 augmentation (cluster 77 labels into 10 semantic groups, 3 real + generate 20): helps to +5/+10 total, **hurts past ~+7 synthetic**, real always > synthetic.
- Banking77 card: 10,003 train / 3,080 test, avg 59.5/54.2 chars, clean single-domain banking English. Explicitly NOT Twitter.

**Sahu et al. 2022 (the caveat on synthetic):** GPT-3 augmentation boosts only when intents are *distinct*; with semantically close intents GPT generates utterances belonging to the *neighbor* intent. Directly predicts failure if brand taxonomy has overlapping intents (e.g., delayed vs lost vs damaged; billing vs refund) — and Banking77-style fine-grained overlap is the worst case.

**Wang et al. 2024 Beyond-the-Known (ChatGPT vs SCL/KNN-CL/UniNL on Banking + CLINC OOD):** ZSD-LLM trails discriminative SOTA badly (Banking-50%: IND-ACC −13.4, OOD-Recall −56%, OOD-F1 −47% vs UniNL). LLM wins ONLY when IND N small (N=5: ChatGPT beats UniNL; N=10–20: wins IND, loses OOD; N=30–40: loses everywhere, ALL-ACC −21). More demos → IND up, OOD inverted-U then *down* (negative transfer / noise). Fine-grained single-domain Banking gap larger than multi-domain CLINC. At N=150, 8.49% task failures (novel labels, ignored format) from long instructions. Converges with Arora scope/size finding.

**OOS scope/size controlled experiment (Arora §4.1, 20-leaf hierarchy, S∈[1,5] scope × L∈[1,5] labels, 10 random draws):** LLM OOS-AUCROC degrades *faster* than SetFit with broader scope S and larger L. LLM in-scope accuracy immune to S but falls with L; OOS fall is steeper. Novel guidance: **fine-grained + small label spaces favor LLM OOS** — i.e., class design matters more for LLMs than for encoders.

**Routing-mechanics foundations and warnings:**
- Gal & Ghahramani 2015: MC-dropout = Bayesian approx; predictive variance ≈ sample variance over T forwards + τ⁻¹I; concurrent forwards ≈ constant time; but variational, typically *underestimates* uncertainty. Softmax output ≠ confidence (Fig.1/MNIST rotation: p≈1 with full-space uncertainty).
- Varshney et al. 2022 (17 datasets, IID/OOD/ADV): **nothing consistently beats MaxProb** despite extra data/compute; MC-dropout best on duplicate-detection, poor on NLI especially OOD; gains don't transfer across tasks. Binding implication: MC-variance routing must be *measured against MaxProb + temperature scaling* in the harness, not assumed.
- FrugalGPT (Chen et al. 2023): learned cascade matches GPT-4 at **−98% cost** or +4% acc same cost; pricing spreads two orders of magnitude. Supports cascade economics generally, but via *learned router*, not pure variance threshold.
- Zhang IntentBERT 2021: ~1k labeled utterances → IntentBERT beats prior pretraining for few-shot cross-domain; intent tasks share structure learnable from little data — supports small-encoder viability for brand domain with ~hundreds of labels, not thousands.
- SetFit paper/repo: contrastive Siamese ST + head, no prompts/verbalizers, order-of-magnitude faster train/infer than PET/PEFT, 2.8k stars, `pip install setfit`, MPNet default; Twitter use requires swapping backbone.

**Twitter-transfer gap (Banking77 limits):**
- BERTweet (Nguyen et al. 2020): same BERT-base arch, RoBERTa procedure on 850M English tweets; beats RoBERTa-base and XLM-R-base on POS/NER/classification for tweets. Generic MPNet/paraphrase encoders are trained on clean paraphrase/NLI, not @handles/hashtags/typos/elongations. Expect a domain gap; Arora's worst SetFit shift result (ADP→OADP) is the closest analog and it is large.
- No corpus source gives SetFit-vs-LLM numbers *on* Customer-Support-on-Twitter; all accuracy deltas above are clean/shopping/banking. Transfer must be demonstrated, not cited.

## 2. Dialectic — why both extremes lose

*Native-LLM-first case:* best raw F1/OOS-recall, best shift robustness, zero training, handles <5/class. Loses on: 56× latency, $15–$740/3k queries (vs local ~$0), 4k-context wall at 77 classes (needs RAG anyway), OOD collapse at large N, 8.5% format failures, prompt-length forgetting. Infeasible as every-query path for a reproducible <15-min student submission and indefensible on cost/latency story.
*Pure-SetFit case:* 30ms CPU, free, no prompts, +5% from cheap neg-aug, 91% at 10–20/class on clean data. Loses on: −8% vs LLM clean, −15% under shift, OOS recall ~0.49 vs ~0.64, no world knowledge for novel phrasing, MPNet backbone mismatched to tweet noise. Infeasible as trust story for auto-handle/escalate.
*Hybrid wins iff* routing sends the *right* 30–45% to LLM and LLM sees RAG-filtered short prompts. Arora proves the mechanism; Loukas proves the prompt must be retrieval-filtered; Varshney constrains the claim (must beat MaxProb); Wang/Arora-scope constrains the taxonomy (small, fine-grained, distinct + explicit OOS).

## 3. Design consequences for the Hiver submission

- Backbone: do NOT default to paraphrase-mpnet-base-v2. Primary: Twitter-pretrained sentence encoder (e.g., vinai/bertweet-base + SetFit head, or twitter-roberta-base sentence variant); ablation vs MPNet on golden set quantifies the transfer gap. Normalize tweets minimally (lowercase handles/URLs → tokens) but preserve identifiers for hybrid-retrieval locus.
- Neg-aug (free +5%): KeyBERT remove/replace 20% as OOS; ablate on/off. Do NOT use GPT synthetic as primary (Sahu + Loukas: bleeds on close intents, sweet-spot ≤+7, real>synthetic). Optional tiny synthetic ablation only.
- Router: MC-dropout M=10 (M=5 min), dropout 0.1, rule as Arora; tune threshold on held-out calibration split to fix route-rate 30–45% AND report AURC / risk-coverage. Mandatory baseline: MaxProb + temperature scaling. Pick winner by AURC on golden-shift split, not by faith. Log latency with batched MC.
- LLM stage (only routed): cheap instruct model (Haiku-class), dynamic RAG top-K=5–10 per predicted neighborhood (not 3×N full prompt), masked Label-xx names + one-line intent descriptions (Arora anti-spurious control), explicit OOS/other label. Fixes cost (Loukas $42-vs-$740 pattern) and length-collapse (Wang 8.5% failure) simultaneously.
- Taxonomy: 6–10 intents max, fine-grained but *mutually distinct* with one-line scope definitions + explicit OOS/other; Banking77-77 is a counter-model (too many, too overlapping, clean-grammar). Validate distinctness by inter-intent confusion on golden set; merge any pair with >15% cross-confusion.
- Metrics to quote: micro/macro-F1, OOS recall + AUCROC, route-rate, p50/p95 latency, $/1k queries, AURC. Headline must be hybrid-vs-native-LLM delta at fixed route-rate, with shift split (temporal/conversation-disjoint per leakage locus) reported separately — never pooled.

## Committed position
Recommend **SetFit-first with MC-dropout (M=10, dropout 0.1) uncertainty routing to a cheap LLM with retrieval-filtered dynamic few-shot (top-K=5–10), on a Twitter-pretrained backbone with KeyBERT negative augmentation (20%)**, because controlled evidence shows it lands **within ~2% of native-LLM F1 (0.737 vs 0.760 ex-shift; ~4% incl. shift) at ~50–57% latency cut (∼1.0s vs 2.35s) and order-of-magnitude cost cut (RAG pattern: $42 vs $740/3k; local base ~30ms vs 1.7s, 56×)**, with M>10 adding nothing and neg-aug adding >5%; cap the brand taxonomy at **6–10 distinct fine-grained intents plus explicit OOS/other** since LLM OOS-AUCROC collapses faster than encoders as scope/label-count grow and single-domain fine-grained sets (Banking77-77) maximize confusion and prompt-length failures, and Banking77 numbers must NOT be quoted as Twitter proof given clean-vs-noisy mismatch (BERTweet beats generic encoders on tweets; SetFit drops ~15% under shift). Confidence **moderate-high (0.72)** — mechanism replicated but Twitter transfer unmeasured and MC-variance has never beaten MaxProb universally. What would change my mind: golden-set A/B showing **MaxProb+temperature beats MC-variance on AURC**, routed-rate needed to match LLM exceeding **~60%**, **no gain from Twitter backbone over MPNet**, or OOS recall staying **<0.50** after neg-aug — any of these flips the recommendation to LLM-first-with-RAG or to shrinking/merging the taxonomy.
