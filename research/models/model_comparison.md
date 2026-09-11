# Model Comparison — AppleSupport Twitter Agent (Hiver)
**Agent 3 — AI/Model Research | Date: 2026-09-10 | Constraint: cheap, reproducible <15 min, no large GPU assumed**

Tasks: (T1) intent classification 8–12 classes on short noisy tweets, (T2) grounded reply generation, (T3) escalation decision (binary + rationale, machine-readable).

> Number policy: verified vendor/HF numbers are cited with source. Everything else is labeled **ESTIMATE** (relative, must be validated on TWCS/AppleSupport slice). No invented absolute accuracy numbers.

## 1. Verified snapshots (official docs / HF, checked Sept 2026)

### 1.1 Small classifiers / encoders
| Model (HF ID) | Params / arch | License (per HF card) | Notes / source |
|---|---|---|---|
| `distilbert/distilbert-base-uncased` | 66–67M, 6 layers, hidden 768, 512 tok | **Apache-2.0** (LICENSE file on HF) | Distilled BERT, ~60% faster than BERT-base, retains ~97% GLUE per paper. CPU-runnable, ~250 MB checkpoint. Source: huggingface.co/distilbert/distilbert-base-uncased |
| `microsoft/deberta-v3-small` | 44M backbone + 98M embed (128k vocab), 6 layers, 768 hidden | **MIT** | ELECTRA-style pretrain, 160 GB data. Dev MNLI-m/mm 88.3/87.7 (small) per HF card. Best accuracy of the three small encoders, slower + larger embed matrix. Source: huggingface.co/microsoft/deberta-v3-small |
| `sentence-transformers/all-MiniLM-L6-v2` | 22M, 6 layers, 384-dim output, max 256 word-pieces (truncation) | **Apache-2.0** (sentence-transformers) | Contrastive 1B-pair fine-tune of MiniLM. 5× faster than MPNet-base per SBERT docs; general-purpose. Good for embeddings+linear head. Source: huggingface.co/sentence-transformers/all-MiniLM-L6-v2, sbert.net pretrained-models |
| `avsolatorio/GIST-all-MiniLM-L6-v2` (optional variant) | 22M base | Apache-2.0 (check card) | GIST fine-tune on MEDI+MTEB-classification triplets; classification-oriented. Only if baseline MiniLM underfits. |

### 1.2 Embedding models (for T1-as-retrieval / few-shot / grounding)
| Model (HF ID) | Dim / ctx | License | Notes / source |
|---|---|---|---|
| `intfloat/e5-small-v2` | 33.4M, 384-dim, 12 layers, 512 tok, English-only | **MIT** (intfloat) | Prefix with `query:`/`passage:`. Strong retrieval baseline at tiny size. ONNX+INT8 available (`nixiesearch/e5-small-v2-onnx`, Apache-2.0 wrapper). Source: huggingface.co/intfloat/e5-small-v2 |
| `intfloat/multilingual-e5-small` | ~118M (0.1B per card), 384-dim, 12 layers | MIT | Init from Multilingual-MiniLM, 100 langs (low-resource degradation noted). Use only if non-English tweets in scope. Source: HF card |
| `BAAI/bge-m3` | 568M, XLM-RoBERTa-large backbone, 1024-dim dense + sparse + multi-vector, 8192 ctx | **Apache-2.0** (per 2026 benchmarks; VERIFY on HF before prod — some secondary sources list MIT) | Best multilingual/hybrid option, overkill for 8–12-class English intent. Needs GPU for comfortable throughput; CPU ~150 ms/q ESTIMATE. Source: BAAI HF, iotdigitaltwinplm Q2-2026 benchmark, upskillzone.ai 2026 |
| `BAAI/bge-large-en-v1.5` / `bge-base-en-v1.5` | 335M / 109M | MIT/Apache — VERIFY on HF | Strong English retrieval; base is the sane self-host ceiling without GPU. |
| Heavy embedders NOT recommended here: `intfloat/e5-mistral-7b-instruct` (7B, MIT, 4096-dim, 32k ctx), `Alibaba-NLP/gte-Qwen2-7B`, `nvidia/NV-Embed-v2` | 7B class | MIT/Apache/CC — VERIFY | Top MTEB retrieval (nDCG@10 ~65–71 ESTIMATE range per Q2-2026 roundup) but need 14–16 GB VRAM, ~100 ms+/q ESTIMATE. Violates no-large-GPU constraint. Listed only to justify exclusion. |

### 1.3 Rerankers (cross-encoders)
| Model | Params / base | License | Notes / source |
|---|---|---|---|
| `BAAI/bge-reranker-base` | 278M (XLM-RoBERTa-base) | Apache-2.0/MIT — VERIFY on HF | Query+doc joint scoring, re-rank top-k (e.g., 20–50). CPU-viable at small k, GPU preferred. Source: huggingface.co/BAAI/bge-reranker-base, bge-model.com |
| `BAAI/bge-reranker-large` | 560M (XLM-RoBERTa-large) | Same — VERIFY | More accurate, 2.24 GB. Skip unless GPU present. |
| `BAAI/bge-reranker-v2-m3` | bge-m3 backbone, multilingual, longer ctx | Same — VERIFY | Default if multilingual or long chunks. `FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)`. Source: HF card + ai-tldr.dev 2026-06-14 |
| `BAAI/bge-reranker-v2-gemma` / `v2-minicpm-layerwise` | 2B class | VERIFY (Gemma/MiniCPM upstream terms) | Higher quality, needs GPU. **Not recommended** for this project. |
| **Decision for this project:** reranker OPTIONAL, Phase 2 only. T1/T2/T3 do not need RAG reranking at v1 (KB is small, templates + small LLM suffice). If grounding KB grows, add `bge-reranker-base` over top-20 only. |

### 1.4 Frontier / small LLMs (for T2 reply + T3 escalation)
| Model / API ID | Context / output cap | Price (verified, standard tier) | License / access | Structured output | Source |
|---|---|---|---|---|---|
| `gpt-4o-mini` (OpenAI, `gpt-4o-mini-2024-07-18` current) | 128k in / 16,384 out | **$0.15 / $0.60 per 1M in/out**; cached in $0.075; batch −50% | Proprietary API. Stable, fine-tune + Batch + vision. | `response_format: {type:"json_schema", json_schema:{...}, strict:true}` + `strict:true` tools. JSON mode legacy. | developers.openai.com/api/docs/models/gpt-4o-mini, /pricing; openai.com 2024-07-18 launch |
| `claude-haiku-4-5` (`claude-haiku-4-5-20251001`) | 200k in / 64k out | **$1 / $5 per 1M in/out**; cache-read $0.10; batch −50% | Proprietary API (Claude API + Bedrock + Vertex + Foundry). Active, retirement not sooner than 2026-10-15. | Structured Outputs GA (Nov 2025 beta → GA Jan 29 2026): `output_config.format` + `strict:true` tools. | platform.claude.com/docs/models/haiku-4-5, /pricing; anthropic.com/news/claude-haiku-4-5 (2025-10-15) |
| `claude-haiku-3.5` | 200k | $0.80 / $4.00 | **Retired on 1P API** (Bedrock/Vertex only) — do NOT pin new work to it. | Strict tool use where available | platform.claude.com pricing deprecation note |
| `meta-llama/Llama-3.1-8B-Instruct` (+ 3.2 1B/3B, 3.3 70B family) | 128k | Self-host (8B ≈ 16 GB VRAM fp16; quant needed for CPU) or hosted ~$0.90/1M ESTIMATE via Together-class providers | **Llama 3.1/3.3 Community License (custom, NOT OSI open)**: attribution + "Built with Llama", 700M MAU re-license clause, use-policy applies. Gated HF access. | Via OSS constrained decoding (vLLM `guided_json` + Outlines/XGrammar), not vendor guarantee. | huggingface.co/meta-llama/Llama-3.1-8B-Instruct, developer.meta.com/ai/models/llama-3, github.com/meta-llama/llama-models |
| `mistralai/Mistral-7B-Instruct-v0.3` (base `Mistral-7B-v0.1/v0.3`) | 32k (v0.3) | Self-host or Mistral Small API $0.15/$0.60 (Small 4, 262k ctx — distinct model, same price point as gpt-4o-mini per apicents.com comparison) | **Apache-2.0** for 7B weights (per mistral.ai/news/announcing-mistral-7b). Commercial self-host note on pricing page — read current terms before ship. | OSS constrained decoding only. | huggingface.co/mistralai/Mistral-7B-v0.1, mistral.ai/pricing |
| `google/gemma-2-2b-it` / `gemma-2-9b-it` (+ 27b) | 8k | Self-host (2B laptop-viable, 9B desktop/GPU) | **Gemma Terms of Use (custom, gated — must click-accept on HF/Kaggle)**. Not Apache/MIT. | OSS constrained decoding only. | huggingface.co/google/gemma-2-2b, ai.google.dev/gemma/docs |
| `gemini-2.0-flash` (reference point, not primary) | large | ~$0.10/$0.40 (per Benchwright May 2026 roundup — VERIFY on Google pricing before use) | Proprietary | `response_schema` | benchwright.polsia.app/blog/llm-production-cost |

API stability notes (verified):
- OpenAI structured outputs GA since 2024-08-06; `json_schema/strict` is production default, `json_object` is legacy. Handle `refusal` + `finish_reason=="length"` explicitly — guarantee voids on refusal/truncation/filter.
- Anthropic strict tool use GA 2026-01-29 (no beta header after that); extended-thinking + forced `tool_choice:any/tool` conflict (use `auto` with thinking). Schema subset: NO `minimum/maximum/multipleOf/minLength/maxLength`, no recursion, `additionalProperties:false` required, `minItems` only 0/1, ≤20 strict tools. OpenAI accepts-but-ignores range/pattern keywords — validate in app code for portability.
- Llama/Mistral/Gemma have no vendor structured-output SLA; enforce via JSON-schema validation + retry in code, or vLLM guided decoding if self-hosting.

## 2. Decision matrix for our 3 tasks

Latency/cost below are **ESTIMATES** for AppleSupport-tweet-shaped inputs (~30–60 tokens + small system prompt) unless marked verified. Validate on project hardware.

| Candidate | T1 Intent (8–12 cls) fit | T2 Grounded reply fit | T3 Escalation fit | Cost | Latency (ESTIMATE) | Ctx | Struct-out | Reliability / risk |
|---|---|---|---|---|---|---|---|---|
| **TF-IDF (1–2g, ≤500k feats) + LogReg (C≈2)** — REQUIRED baseline | Strong baseline: 76–81% acc ESTIMATE on tweet sentiment analogues (Sentiment140 79.7%, US-Airline 76.4% — same short-noisy regime, not our label set). Interpretable, trains in seconds on CPU. | N/A (not generative) | Usable as feature/threshold signal only | $0 (CPU) | Train <1 min, infer <5 ms CPU ESTIMATE | N/A | N/A (sklearn `predict_proba`) | High reliability, low variance. Fails sarcasm/mixed sentiment. |
| **`all-MiniLM-L6-v2` (22M) + linear/LogReg head** — RECOMMENDED primary T1 | Best cost/accuracy trade: fine-tune or freeze-embed+LogReg; GIST variant if needed. Domain gap smaller than SST-2→tweets because we fine-tune on our 8–12 intents. | N/A (encoder) | Can emit calibrated escalation score as 2nd head or shared encoder | $0 (CPU) | Infer ~5–15 ms CPU / <5 ms GPU ESTIMATE; trains <10 min CPU | 256 WP (truncate long threads) | Softmax + threshold (calibrate) | High. License Apache-2.0. Repro <15 min. |
| `DistilBERT-base` fine-tune (66M) — fallback T1 | Slightly above MiniLM on formal text ESTIMATE; on tweets needs domain fine-tune (Twitter-RoBERTa lesson: generic pretrain underperforms tweet-pretrained by ~2× on TweetEval in cited study). Heavier than MiniLM for marginal gain. | N/A | Same as above | $0 (CPU-trainable, slow) | ~20–50 ms CPU ESTIMATE | 512 | Same | Medium-high. Keep as ablation, not default. |
| `DeBERTa-v3-small` fine-tune (44M+98M embed) — accuracy-ceiling ablation | Highest GLUE/MNLI of the three (verified 88.3 MNLI-m) but embed matrix heavy; SST-2 91% ≠ tweet performance. Only if MiniLM/DistilBERT plateau. | N/A | Same | $0 but slower train | Slower than DistilBERT ESTIMATE | 512 | Same | Medium. MIT. Optional. |
| `e5-small-v2` (33M) embeddings + classifier | ≈ MiniLM quality, retrieval-oriented (`query:`/`passage:` prefixes). Pick if we unify T1 + grounding retrieval on one encoder. | Supports grounding retrieval (embed KB articles + tweet, cosine top-k) | Same as MiniLM | $0 | ≈ MiniLM ESTIMATE | 512 (trunc) | Same | High. MIT. Good alt-primary. |
| `bge-m3` / `e5-mistral-7b` / 7B embedders | Overkill for 8–12 classes; no measurable win worth 5–25× size. | Only if KB scales multilingual/long-doc | No | GPU + ops cost | 30–100+ ms ESTIMATE | 8k–32k | N/A | Low value/cost here. EXCLUDE v1. |
| `bge-reranker-base/v2-m3` | N/A | +1–3 pts top-k precision ESTIMATE if KB large; adds 20–50 forward passes/req | N/A | $0 + latency | Dominates p95 on CPU ESTIMATE | joint QA limit — chunk ≤256 tok | scores (uncalibrated, rank-only) | Medium. DEFER to Phase 2. |
| **`gpt-4o-mini` API — RECOMMENDED for T2+T3** | Capable but wasteful vs encoder (use only as T1 fallback/teacher for distillation) | Primary: grounded replies w/ KB-in-prompt + template fallback. 128k ample. 0.8–1.2 s e2e ESTIMATE on short tasks; TTFT ~300–600 ms ESTIMATE/measured in cited benches | Primary: `{escalate: bool, reason: str, confidence: float}` via `json_schema/strict:true`, `parallel_tool_calls:false`, app-side range validation | Verified $0.15/$0.60 → ~$0.0002–0.0005/req at our sizes; $45/mo per 100k reqs at 1k-in/0.5k-out (verified calc) | Fastest cheap API ESTIMATE | 128k verified | Strong (grammar-constrained) | High API stability, fine-tune + batch available. Watch: complex-schema tool drift 8–12% in one cited test — keep T3 schema tiny + `strict:true` + retry. |
| `claude-haiku-4-5` API — premium alt for T2+T3 | Same note | Better tone/instruction-fidelity per cited comparisons; 200k ctx | 97%+ first-try valid JSON in one cited agent test (ESTIMATE, schema-dependent) | Verified $1/$5 → ~4–8× gpt-4o-mini at our sizes | TTFT ~500–900 ms ESTIMATE | 200k verified | Strong (GA 2026) | High, but 4–8× cost. Use only if reply-quality eval justifies it, or as quality-ceiling in eval. |
| `Llama-3.1-8B-Inst` / `Mistral-7B-Inst-v0.3` / `Gemma-2-2B/9B-it` self-host | Possible via prompting but weaker struct guarantee + ops burden | Possible offline path; 1–3B variants CPU-quant viable, 7–9B need GPU/quant | Possible but must hand-roll validation/retry | $0 tokens + infra/ops | CPU-quant 0.5–3 s/tok-stream ESTIMATE; GPU needed for SLA | 8k–128k | App-enforced only | Medium-low for <15-min repro. Keep as offline/contingency track, not default. Templates remain the hard fallback. |

Why not default to largest: 7B LLM embedders / rerankers / frontier-large (GPT-4o, Sonnet/Opus, Llama-70B) add 5–50× cost/latency and GPU/ops requirements for single-digit-point gains on 8–12 short-text intents (ESTIMATE direction from MTEB + TweetEval domain-gap evidence). Encoder + small-LLM splits the problem at its natural seam: cheap deterministic classification/escalation-signal + small generative model constrained to KB + templates.

## 3. Recommended stack (cheap, <15 min, no large GPU)

1. **T1 Intent — `all-MiniLM-L6-v2` + lightweight head (primary); TF-IDF+LogReg (mandatory baseline).**
   - Baseline: `TfidfVectorizer(ngram 1–2, max_features 50–500k) + LogisticRegression(C=2, max_iter=1000)`. Expect ~76–80% acc ESTIMATE; ship as `/baseline` for eval comparison.
   - Primary: `sentence-transformers/all-MiniLM-L6-v2` → freeze → LogReg first (2 min), then unfreeze top-layer fine-tune if time (`transformers.Trainer`, 3 epochs, lr 2e-5, batch 32, CPU). Alt encoder: `intfloat/e5-small-v2` if retrieval unification desired.
   - Ablations (time-boxed): DistilBERT, then DeBERTa-v3-small. Twitter-pretrained variant (`cardiffnlp/twitter-roberta-base`) only if generic encoders show domain gap.
2. **Grounding KB — static mini-KB (10–30 AppleSupport help snippets) + cosine retrieval with the SAME MiniLM/e5 encoder.** No vector DB v1 (in-memory numpy). Reranker deferred.
3. **T2 Reply + T3 Escalation — `gpt-4o-mini` with `json_schema/strict:true`, templates fallback.**
   - One call returns `{intent (enum 8–12), escalate: bool, reason: string, confidence: number, reply: string}` OR split T3 into deterministic rules + LLM reason. Keep schema ≤2 levels, `additionalProperties:false`, all-fields-`required` + nullable optionals, `parallel_tool_calls:false`.
   - System prompt pins KB-only grounding ("if KB top-1 score < τ, use safe template + escalate=true"). App-side: jsonschema validation → 1 retry with repair prompt → template fallback (never free-form hallucinated steps like "DFU/restore" unless in KB).
   - Cost control: cap `max_tokens` (e.g., 300), cache static system/KB prefix (prompt caching), batch eval via Batch API.
   - Quality ceiling: run same eval on `claude-haiku-4-5` once; promote only if blind human/A/B eval delta > retry-adjusted cost delta.
4. **Offline/contingency — templates alone (zero-model) → `gemma-2-2b-it-QINT8` or `Llama-3.2-1B/3B-quant` if API unavailable.** No SLA claimed; eval only.
5. **Repro recipe (<15 min on laptop CPU):** `pip install scikit-learn sentence-transformers transformers torch --index-url cpu` → run `experiments/` T1 notebook (TF-IDF 2 min → MiniLM-frozen 3 min → fine-tune 5–8 min) → `scripts/eval_intent.py` prints macro-F1 + latency → T2/T3 demo uses `gpt-4o-mini` with `OPENAI_API_KEY` or `--templates-only`.

## 4. Risks / open questions
- Tweet domain gap: generic encoders underperform tweet-pretrained on social benchmarks (DeBERTa-v3 40.6 vs Twitter-RoBERTa 72.4 macro-F1 on TweetEval in cited study — verified figures from that study, not our task). Mitigation: fine-tune on our AppleSupport slice.
- Structured-output portability: keep schemas in the OpenAI∩Anthropic subset (§1.4); range/pattern checks in code.
- Escalation calibration: LLM confidence is uncalibrated — combine with encoder margin + rule triggers (e.g., warranty/legal/safety keywords, repeated failure) and tune τ on held-out set.
- License hygiene: Llama/Gemma are custom-gated (not OSI); BGE-M3 license conflict in secondary sources — confirm on HF file view before bundling weights.

## 5. Sources (queries run 2026-09-10, 14 total)
DistilBERT/DeBERTa benchmarks + HF cards (`microsoft/deberta-v3-small`, `distilbert-base-uncased`); MiniLM (`all-MiniLM-L6-v2`, GIST variant, SBERT docs); BGE vs E5 (upskillzone.ai 2026-05-06, besthub.dev 2026-04-21, iotdigitaltwinplm Q2-2026, knowledgesdk 2026-03-20, arXiv 2607.23507); BGE rerankers (BAAI HF cards, bge-model.com, ai-tldr.dev 2026-06-14); GPT-4o-mini pricing/structured (developers.openai.com models+pricing, openai.com 2024-07-18, openrouter); Claude Haiku 4.5/3.5 pricing/latency (platform.claude.com docs+pricing, anthropic.com/news 2025-10-15); Llama 3.1/3.2/3.3 licensing (developer.meta.com, meta-llama HF, llama-models GitHub); Mistral 7B/Small pricing+Apache-2.0 (mistral.ai/news/announcing-mistral-7b, mistral.ai/pricing, HF mistralai/Mistral-7B-v0.1/v0.3); Gemma 2/3 terms (ai.google.dev model card+get-started, HF google/gemma-2-2b/9b); structured-output mechanics (ai-tldr.dev 2026-06-12, janeer.com, toolchew.com, towardsdatascience 2026-06-18); TF-IDF+LogReg tweet baselines (Sentiment140 79.7%/80 F1 study 2025-05-30, US-Airline 76.4% 2025-11-30, kokilamariyayi 81% vs RoBERTa 74% comparison); small-LLM cost/latency (apicents.com gpt-4o-mini vs Mistral Small 4, dev.to chasebot, panelsai.com, unpromptedmind.com 2026-03-23, benchwright May 2026).
