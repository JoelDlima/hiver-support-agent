# Differentiation — Why This Is Not "GPT + RAG + Prompt" (Swarm D, §25/§46)

Date: 2026-09-10 · System: deterministic AppleSupport agent (`src/agent.py`: classify 11 intents → retrieve 89k historical replies → template-grounded draft → 4-trigger escalate) · Full landscape: `research/competitors/analysis.md`, `research/technology-landscape.md`

## The one-paragraph claim (§46 standard: "why better than a wrapper?")

A prompt→LLM wrapper sends the tweet to a model and prints the answer. This system never does that: the reply text comes from 11 frozen intent-conditioned templates, the factual ballast comes from TF-IDF-NN passage IDs returned alongside every reply for audit, the risky calls are intercepted by 4 deterministic escalation triggers before any text ships, and the eval tells you exactly where it loses (human-60 intent 0.433, esc_F1 0.471, per-intent table with two collapsed classes) instead of a single inflated accuracy. Evidence over adjectives — that is the whole differentiation.

## Head-to-head

### 1. vs `ldulcic/customer-support-chatbot` (closest predecessor: per-brand seq2seq on TWCS, 79★)

- They: per-brand generative seq2seq + attention, no retrieval, no intent, no escalation; eval = BLEU script only. Ungrounded by construction — invents versions, links, policies; 2018-era deps, hours to train. (`research/competitors/analysis.md:16`)
- We: no generator at all in v1. Reply = template keyed by classifier intent; every reply carries `grounding_passage_ids` (top-3 TF-IDF-NN over 89,694 deduped AppleSupport replies). BLEU deliberately demoted to "diagnostic-only" (r≈0.22–0.32 with human judgment); headline metrics are intent macroF1 + escalation P/R + heuristic groundedness + latency.
- Beat-condition (honest): we have not run their BLEU script side-by-side; the win claimed is architectural (grounded IDs + escalation exist vs do not exist), not a BLEU delta.

### 2. vs Intercom Fin AI Engine (commercial SOTA: 76% resolution, ~0.1% hallucination, 7-phase validate→escalate)

- They: patented refine→safety-check→bespoke retrieval (`fin-cx-retrieval` + reranker)→generate→certainty-validate→disambiguate-or-answer; proprietary model + reranker, $0.99/resolution, closed eval fixture (200 Q/48 articles). Failure modes observed in the wild: hallucinates features absent from cited sources; long off-topic replies that only stop on human interrupt (community reports, Sep-2026 websearch).
- We: Fin-7-phase-**lite** in ~100 lines of plain Python with zero inference spend: normalize → classify → retrieve (TF-IDF-NN, p50 35ms) → template draft → 4-trigger escalate → validate (schema + IDs). No reranker/LLM yet — openly deferred to week-2 (hybrid BM25+MiniLM + cross-encoder + pinned LLM drafter behind the same Pydantic dataclass + NLI gate). What we replicate today: the *validation-before-answer* discipline (abstain/clarify/escalate instead of guessing) and the *escalation-as-first-class-output* contract (reason codes + handoff packet: intent+confidence+passage IDs+signals).
- Beat-condition (honest): Fin wins on resolution quality and retrieval precision (90–97% claimed vs our unmeasured recall@k — Swarm C owns that number). We win on openness (every rule/weight/threshold in-repo), cost ($0 infer, $6–50/mo to 10k users vs per-resolution billing), and auditability (IDs + reason codes on every output). No claim to out-resolve Fin.

### 3. vs `carlosrod723/X-CustomerSupport-Chatbot` (nearest Twitter-RAG demo: LangChain + FAISS + MiniLM + GPT-4, 68% precision, k=2–3, 300-token context)

- They: dense-only top-k=2–3, no rerank, no grounding validator, no escalation policy, no faithfulness metric; 500-query held-out at 68% precision.
- We: top-5 retrieval with IDs + intent-conditioned templates (no ungrounded generation to validate in the first place) + 4-trigger escalation + full harness (intent/escalation/groundedness/latency/failure F1–F8). KB is 89k thread-aware AppleSupport replies (dedup + template-cap K=5), not 3×100-token docs.
- Beat-condition (honest): embedding quality — MiniLM dense likely beats our TF-IDF on paraphrase (proven: our "batt" slang miss, F7). Week-2 hybrid retrieval closes that gap; v1 trades recall for determinism + $0.

### 4. vs keyword classifiers (`Vishesh062` DistilBERT 99.5% / `aniqua14` CLINC-OOS 58% recall collapse / our own `simple` baseline 1.000)

- They (and our `simple` row): keyword-generated labels evaluated against keyword-generated labels = 99.5%/1.000 by construction. Author of the 99.5% model admits "keyword detector with extra steps". OOS recall collapses to 58% wherever it is actually measured.
- We: publish the circularity instead of the trophy. `evaluation/results.csv` prints the 1.000 with a "do not cite — circular" warning; headline is human-60 (simple 0.517 → final 0.433, with κ 0.465 ceiling disclosed). Dual golden (200 weak-draft + 60 human-reviewed, 39 flips, flip notes in `golden_human_60.csv`) + OOS-as-first-class (`other_out_of_scope` P 0.31/R 0.56/F1 0.40 reported, not buried).
- This is the differentiation that matters most for §46: a wrapper team would ship the 1.000. We ship the 0.433 with the reason.

## Our edge, itemized (each with artifact)

1. **Thread-aware Apple KB (89,694 deduped, template-cap 5)** — `data/processed/apple_kb.csv`, `scripts/build_kb.py`. Filters TWCS→AppleSupport threads, preserves @-mention/DM-handoff structure, dedups canned "DM us" collapse (1.45% exact dups). Competitors use generic KBs or 300-token contexts.
2. **Templates with passage IDs** — `src/intents.py:TEMPLATES`, `src/agent.py:draft_grounded`. Frozen brand voice (acknowledge→diagnostic→DM-redirect, Apple IA paths) + `grounding_passage_ids[:3]` on every `AgentResult` for audit. No invented order numbers/links/dates — structurally impossible in v1.
3. **4-trigger escalation (not a threshold)** — `src/agent.py:decide_escalation` + `src/text_norm.py:features_for_escalation`. can't-ground / policy-risk / frustration / human-request, with reason codes + signals dict. Single-threshold systems miss flame/burn (our pre-fix miss, now regression-tested) and over-escalate thanks.
4. **Dual golden + disclosed circularity** — `evaluation/golden_v1.csv` + `golden_human_60.csv` + `GOLDEN_NOTE.md` + `PER_INTENT.md` + `FAILURE_TESTS.md`. 39/60 flips published with reasons; weak-vs-human κ 0.465/0.015 printed next to every headline.
5. **Failure suite as spec** — F1–F8 with real outputs including 1 FAIL + 3 PARTIALs filed openly. Toy bots report zero eval; commercial vendors report selected metrics. We report the misses with queued fixes.
6. **Deterministic + $0 + 180ms** — p50 180ms/p95 192ms end-to-end, 44MB index, CPU-only, <15min repro. No API key, no GPU, no managed DB, no framework. Scale path (workers→replicas→ANN) triggers on metrics, not anticipation (§9).

## What we do NOT claim

- Not higher intent accuracy than keyword baselines on weak labels (we lose: 0.795 vs 1.000) — by design.
- Not Fin-level resolution or retrieval precision — unmeasured (recall@k owned by Swarm C) and almost surely lower.
- Not paraphrase-robust (F7 slang miss), multilingual (English-only, non-English→escalate policy), or thread-aware beyond single messages (2-turn context is week-2).
- Not LLM-judged (gated; see `evaluation/JUDGE_AGREEMENT.md`).

## Verdict for §46

Better than a wrapper because: grounded IDs on every output, measured escalation with reason codes, dual golden with published flips and kappa ceilings, failure suite with open FAILs, and a cost/latency profile a wrapper cannot touch — all reproducible offline in <15 minutes. The evidence is the differentiation.

---

# V2 — Eval moat (2026-09-10; V1 above untouched)

Full analysis: `research/competitors/eval_moat.md` (10 websearch queries, 2026-09-10). One-line thesis: everyone has the same build brief — our moat is the proof layer, and the proof is engineered to lose honestly where it loses.

- **Dual golden, flips published:** weak-200 (draft, circular — simple-keyword 1.000 labeled do-not-cite) + human-200/human-60 headline (39/60 flips; final human-60 intent 0.433/macroF1 0.443; human-200 esc acc 0.835 κ 0.487 P 0.469 R 0.767 F1 0.582). Typical submissions: accuracy-only or keyword-circular trophies, no agreement numbers.
- **Kappa ceilings disclosed:** weak-vs-human intent κ **0.465** / esc κ **0.015** next to every headline; final-vs-human κ 0.363/0.213 (n=60). Literature bar (Judge's Verdict Tier-1 κ 0.781–0.816, |z|<1; 21-judge Δκ 33–41pp deflation; binary r=ρ=τ=φ=MCC identity) is why we report chance-corrected agreement + protocol + confusion matrix instead of correlation.
- **Judge gated, not faked:** heuristic $0 judge (human-60 mean 4.72 / human-200 4.83, ≥4 rate 1.000, disclosed circular) + pinned LLM hook (`evaluation/judge.py` JUDGE_PROMPT judge-v1-2026-09-10, temp 0, `gpt-4o-mini-2026-07-01`, JSON-schema, double-run) behind wκ≥0.60 + safety-recall≥0.90. Zero LLM scores claimed.
- **Safety recall 0.909** (11 human legal_safety cases, gate ≥0.90 — met, n=11 CI wide, stated); human-60 esc 2×2 `[[34 12][6 8]]` P 0.400/R 0.571/F1 0.471 published with recall<0.90-bar admission (PII gate 2026-09-11 converted one FN→TP). Single-threshold escalation is the documented production bug; ours is triggers + reason codes + handoff packet (intent+confidence+passage IDs+signals).
- **Retrieval ⊥ generation:** proxy recall@k 1.000 labeled coverage-not-relevance (0.08 gate = safety net, recalibration queued) alongside answer-level groundedness; ablation isolates it (no-retrieval esc_P 0.233→0.400, unresolvable 0.833→0.133, intent Δ 0.000). Faithful-but-wrong is the #1 production failure — recall-alone can't see it, our 2×2 reading rule can.
- **Per-intent + confusion + open FAILs:** two collapsed classes (connectivity/hardware 0.00), top-7 confusions, F1–F8 13 PASS/3 PARTIAL/1 FAIL with queued fixes, flame regression PASS(decision)+intent-miss disclosed. Plus ABLATION/PERFORMANCE (p50 230ms/p95 248ms, 4.3 qps, 42MB)/COST (flat $6–50/mo EST. vs linear LLM $0.0002–0.0005/req) docs.
- **Misleading metrics contained by policy:** no containment/CSAT/BLEU-as-proof anywhere; §9 disclosure in every report; BLEU diagnostic-only (r≈0.22–0.32). The three numbers typical submissions headline are the three the literature bans.
