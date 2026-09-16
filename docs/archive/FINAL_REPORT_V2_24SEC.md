# Hiver Final Report V2 — AppleSupport Twitter Agent, 24-Section (§42)

Date: 2026-09-10 · Owner: Swarm D · Workspace: `.` · Repro: `README.md` (7 commands, <15min, CPU-only) · Supersedes condensed V1 (`docs/FINAL_REPORT.md`) with measured §21–22/25/27/40 numbers. Headline rule: **human-60 counts, weak-200 does not** (circular — see §16/§18).

## 1. Executive Summary

Deterministic AppleSupport agent (11-intent classify → 89k-reply TF-IDF-NN retrieve → template-grounded draft → trigger escalate), CPU-only, $0 infer, p50 180ms. Human-60 truth: intent 0.433/macro 0.443, esc_F1 0.471 (P 0.400/R 0.571), groundedness 4.72/1.000 ≥4. Keyword baseline wins intent by construction (0.517 weak-trained ceiling κ 0.465) but scores esc_F1 0.000. New in V2: per-intent table + confusion CSV, offline-judge distribution + LLM gating, F1–F8 suite (13 PASS/3 PARTIAL/1 FAIL with queued fixes), differentiation head-to-heads, §40 audit (5 PASS/7 PARTIAL/0 FAIL). Not shippable this week: esc recall 0.50 < 0.90 bar, n=60 CIs ±12%.

## 2. Problem Interpretation

Hiver SDE Intern Twitter agent for AppleSupport, exact statement preserved (`docs/research/problem/problem_decomposition.md`). Good = acknowledge → diagnostic (Settings>General>About) → DM redirect when PII needed; every technical claim cites passage IDs; abstain on link-only/KB-miss; escalate safety/account/human/frustration with handoff packet (intent+confidence+passage IDs+signals). Out of scope: refunds/repairs execution, account actions, live Apple backend, multilingual, post-2017 knowledge. Message-level intent (threads drift mid-conversation).

## 3. Dataset Analysis

`twcs.csv` 2,811,774 rows; AppleSupport ~106,860 outbound, ~97k inbound pool; Oct–Nov 2017 burst (iOS 11/11.1, iPhone 8/X, I→A autocorrect wave); chars mean 123/med 125; URLs 46%, mentions 99.9%, emoji 7%; threads mean 2.42. Dedup → KB 89,694 (template-cap 5; 1.45% exact canned-dup collapse prevented). Inbound pool 97,592. Preprocess: NFKC, URL→\<URL\>, @AppleSupport→\<BRAND\>, hashtag kept, emoji→\<EMOJI\>. Cutoff frozen 2017. See `docs/research/datasets/data_quality.md`.

## 4. Research Findings

10 tracks, 100+ searches (`docs/research_log.md` + Swarm-D DDG appendix 2026-09-10: judge-κ, RAG faithfulness, injection defense, sklearn per-intent, support failure modes). Load-bearing findings: Banking77 errors driven by label overlap not capacity; SetFit 8-shot ≈ full-tune (report mean±std/3 seeds); RAGAS faithfulness 0.95 pairwise but relevance metrics misrank (gate on faithfulness+correctness + abstention); GPT-4 judge ~80% ≈ human–human but position/verbosity biases need swap + reference-guided + CoT mitigations; correlation lies (r=0.95 with κ=0.45) → our κ≥0.60 ship-gate; containment/CSAT/BLEU/recall@k all mislead in known directions → our metric stack (resolution quality + factual accuracy + escalation quality + repeat-contact + policy adherence).

## 5. Existing Solutions

Closest: `ldulcic/customer-support-chatbot` (per-brand seq2seq on TWCS, BLEU-only, ungrounded) — baseline to beat. Academic: Hardalov 2018 IR-vs-seq2seq-vs-Transformer on TWCS. RAG demos: `carlosrod723` (FAISS+MiniLM+GPT-4, 68% precision, k=2–3, no validation/escalation). Guardrail blueprint: `adityanaranje` LangGraph (grounding+confidence+escalate agents). Classifiers: `Vishesh062` 99.5% (keyword-label inflation — cautionary tale), `aniqua14` OOS recall 58% collapse. Commercial: Intercom Fin (7-phase validate→escalate, 76% resolution, ~0.1% hallucination, $0.99/resolution, closed), Zendesk/Decagon/Sierra (procedures + simulators, closed). Platforms: Chatwoot/TGO (inbox plumbing, no eval). Full table: `docs/research/competitors/analysis.md`.

## 6. Technology Landscape

Classifier: LogReg-small (chosen) > MiniLM-head (week-2) > BERT (needs 500+ human labels). Retrieval: TF-IDF/BM25 (chosen) > MiniLM dense (paraphrase better, needs DL) > hybrid+rerank (week-2) > Pinecone/Qdrant (cost, unjustified <1M docs). Orchestration: custom deterministic > LangGraph/LlamaIndex/PydanticAI/CrewAI/MAF/ADK (all stable 2025–26, all overkill). Serve: FastAPI+uvicorn stateless + LRU; no K8s/Redis v1. Eval: sklearn + heuristic judge + gated LLM judge (κ/α/swap-consistency); RAGAS faithfulness+correctness pair; BLEU/ROUGE diagnostic-only. Security: ingress PII-natural handling, secret blocklist, fail-close (OWASP LLM01). Condensed map: `docs/research/technology-landscape.md`.

## 7. Selected Architecture

`src/agent.py:AppleAgent.handle`: normalize (`text_norm.py`) → TF-IDF+LogReg intent + confidence (`classifier.py`) → TF-IDF-NN top-5 + IDs (`retriever.py`) → intent-conditioned frozen template draft (`intents.py:TEMPLATES`) → 4-trigger escalation (`decide_escalation`) → `AgentResult` dataclass (intent, confidence, draft, passage IDs, decision, reason, signals, latency, unsupported-claims). Stateless FastAPI (`backend/`), joblib+CSV store, LRU. No vector DB, no agent framework, no LLM in v1 path.

## 8. Why This Architecture

15 logged decisions (`docs/DECISION_LOG.md`), each with revisit trigger: per-brand Apple KB (voice-consistent → templates ground); 11 message-level intents (threads drift); TF-IDF-NN (17s build, p50 35ms, 44MB — managed DB adds cost without recall gain <1M docs); no framework (0.95¹⁰≈0.60 compounding); templates>LLM (zero hallucinated versions/links, no key in repro); 4 triggers>1 threshold (flame/burn miss proved it); DM-as-triage (45%+ outbound deflection ≠ resolution); dual golden (weak-start disclosed, human-60 headline). Capability-landscape + decision-record: `docs/research/architecture/architecture_decision.md`.

## 9. Model Selection

TF-IDF (30k, 1–2gram, sublinear) + LogReg C=2.0, weak-label bootstrapped, 0.945 train-vs-weak; CPU <2min. Deferred: MiniLM-L6-v2 + linear head (primary week-2 once 200-human lands), e5-small-v2 alt, bge-reranker phase-2, gpt-4o-mini `json_schema/strict:true` drafter behind same dataclass (max 2 retries → template fallback). Excluded v1: 7B embedders/large LLMs (GPU/cost), Haiku-4.5 except quality-ceiling eval. Bigger models memorize keywords better (simple 1.000 proves it) — they do not understand better (ceiling κ 0.465). See `docs/research/models/model_comparison.md`.

## 10. Retrieval Strategy

Corpus: 89,694 deduped AppleSupport replies (thread-aware, template-cap 5). Index: TF-IDF NN, 17s build, p50 35ms, top-5 + IDs + scores. Contract: cite-or-flag — every draft carries `grounding_passage_ids[:3]`; empty/low-score (<0.08) → `no_grounding` escalate; never invent. Week-2: hybrid BM25+MiniLM + cross-encoder rerank, recall@3≥0.85/intent, per-intent score floors (fixes F3 link-only FAIL). Recall@k/MRR/NDCG measurement owned by Swarm C — the one retrieval number still missing.

## 11. Agent/Workflow Strategy

No agents — deterministic 5-step workflow with typed outputs, ≤2 retries → template fallback. Escalation ladder: clarify → answer-with-caveat → escalate-with-packet → refuse-redirect. Handoff packet = intent + confidence + transcript + attempts + passage IDs + next step. Healthy-handoff band 10–20% (literature); ours currently escalates 19/60 (31.7%) — over-escalation bias, safe direction. E7–E9 auto-escalate rules (account_security/money_threshold/human_request) inline in `decide_escalation`.

## 12. Database Strategy

joblib (vectorizer + NN index + classifier) + CSV (`apple_kb.csv`, `doc_ids.csv`, golden/results CSVs). SQLite optional. Rationale: 89k short docs need no server; 44MB total; fresh build <15min. Revisit at >1M docs, multilingual embeddings, or multi-writer needs → ANN (FAISS/Chroma) + Postgres/pgvector per landscape triggers.

## 13. Scalability Strategy

Stateless FastAPI → workers → replicas → ANN, each step gated on metric triggers (p95, throughput, index size). Measured dev-CPU: p50 180ms/p95 192ms end-to-end (20-sample), retrieval p50 35ms. Missing: cold/warm split, p99, throughput, mem/CPU/GPU under load, Docker load test (Swarm C PERFORMANCE.md). No K8s/Redis anticipatory spend (§9 proportional). $6–50/mo to 10k users on current profile.

## 14. Security Strategy

Threat model OWASP LLM01: system prompt holds no secrets (nothing to leak); no action tools (no refund/email/send — injection blast radius nil by architecture); deterministic input lexicon (injection/jailbreak → escalate, F4/F8 5/5 PASS); output-safe templates (F6 PII never echoed); fail-close on classifier/retriever exceptions. Gaps filed: PII→escalate rule, URL-allowlist + credential-harvest rule, obfuscation coverage, formal scan (`docs/SECURITY_REVIEW.md` + Swarm A). See `evaluation/FAILURE_TESTS.md` F4/F5/F6/F8.

## 15. Evaluation Methodology

Dual golden: 200 stratified weak-draft (seed 7, coverage) + 60 human-reviewed (seed 11, 39 flips with notes — truth). Metrics: intent acc + macroF1 + per-intent P/R/F1 (sklearn, `evaluation/PER_INTENT.md`), esc P/R/F1 + 2×2 (recall≥0.90 target), heuristic groundedness 1–5 (DM+diagnostic+length+cite), recall@k diagnostic (Swarm C), judge-human κ gate (LLM judge deferred). Baselines: trivial (majority+canned) + simple (keyword+BM25). Failure suite F1–F8 + flame regression. Rubric: `evaluation/rubric.md`; protocol: `docs/research/evaluation/eval_strategy.md`. Mandatory misleading-numbers section in every report (§18 V1 carried forward).

## 16. Baseline Results

Weak-200 (circular, do-not-cite): trivial 0.095/0.016/0.000 (ground 3.00/0.000) · simple 1.000/1.000/0.686 (ground 2.98/0.205) · final 0.795/0.796/0.630 (ground 4.75/1.000). Human-60 (headline): trivial 0.217/0.032/0.000 · simple-keyword 0.517/0.547/0.000 · final 0.433/0.443/0.471. Deltas final−simple (human): intent −0.084, macro −0.104, esc_F1 +0.471. Reading: simple memorizes keyword labels; final trades intent for escalation + groundedness. Weak-vs-human agreement (label ceiling): intent acc 0.517 κ 0.465; esc acc 0.70 κ 0.015 (≈random — weak esc meaningless).

## 17. Final Results

Human-60 final: 26/60 intent, esc 2×2 [[34,12],[7,7]]. Per-intent highs: apple_id 1.00 (n=3), battery 0.75, followup 0.57; collapses: connectivity 0.00, hardware 0.00 (see §18 for why these are the most informative rows); catcher other 0.40. Final-vs-human κ: intent 0.363, esc 0.213 (beats weak esc-noise). Heuristic groundedness: {5:43, 4:17}, mean 4.72, ≥4 rate 1.000 — circular-by-design (templates self-reward), disclosed. Latency p50 180ms/p95 192ms. Full tables: `evaluation/PER_INTENT.md` + `evaluation/confusion_human60.csv`.

## 18. Ablation Results

Inferred (components removed one-by-one, no reranker/LLM to ablate in v1): −retrieval → groundedness 4.75→~3.0 (IDs gone, templates generic); −rules → esc_F1→~0 (simple row = classifier-without-rules); −classifier→keyword (simple row: intent up on weak, esc dead); −templates→copy (simple ground 2.98: raw retrieved text, no diagnostic structure). Each component earns its place on a different axis: classifier→intent signal, retrieval→grounding IDs, rules→escalation, templates→brand-safe surface. Formal rerun with seeds (Swarm C ABLATION.md) pending 200-human labels.

## 19. Failure Testing

F1–F8, 17 probes, real outputs (`evaluation/FAILURE_TESTS.md`): F1 empty/whitespace PASS; F2 huge PASS (1 over-escalation noted); F3 link-only 1 FAIL (9-word link case auto-handles — word-count gate bug, queued fix) + 1 PASS; F4 direct injection 2/2 PASS; F5 indirect 1 PASS + 1 PARTIAL (evil-URL auto-handles, draft safe — URL-allowlist queued); F6 PII 2 PARTIAL (drafts safe, escalate missing — PII rule queued); F7 paraphrase 1 PASS + 1 PARTIAL ("batt" slang miss, safe escalate — slang map queued); F8 jailbreak/roleplay/human 3/3 PASS. Flame regression: pre-fix other/auto → post-fix legal_safety/escalate (intent miss remains, guardrail covers). Scoreboard 13/3/1; zero unsafe outputs (no PII echoed, no instruction complied with, no action tool to hijack).

## 20. Cost Analysis

Measured: $0 inference, 44MB index, CPU-only. Tiers: 100 users $6–12 / 1k $12–25 / 10k $25–50/mo vs $300–6k LLM-per-request. LLM path (optional drafter): $0.0002–5/req ESTIMATE (labeled, not measured). Ingest/embed/retrieval: one-time CPU minutes, $0 marginal. No invented precision; estimates marked per §13. Owner detail: Swarm C COST.md.

## 21. Competitive Differentiation

Not "GPT+RAG": thread-aware 89k Apple KB + frozen intent-templates with passage IDs + 4-trigger escalate + dual golden with 39 published flips + printed-and-disclaimed 1.000 + open failure suite. Vs ldulcic seq2seq: grounded IDs + escalation exist vs absent. Vs Fin: openness + $0 + auditability vs resolution crown (theirs, honestly). Vs X-RAG demo: top-5 + validation + escalation + harness vs k=2 no-guardrails. Vs keyword classifiers: we publish circularity instead of trophying it. Full head-to-heads with beat-conditions: `docs/DIFFERENTIATION.md`. §46 one-liner: the evidence is the differentiation.

## 22. Known Limitations

Escalation recall 0.571 < 0.90 bar (FNs audited); intent 0.433 < 0.85 bar (connectivity/hardware collapsed); n=60 ±12% CIs, single annotator, no inter-annotator κ; per-intent support ≤13 (howto n=1 — do not interpret); groundedness heuristic self-rewards templates; recall@k unmeasured; 1 FAIL + 3 PARTIALs open in F1–F8; English-only; single-message (no thread context); dev-CPU latency ≠ prod; frontend/ empty; no fresh-clone witness log. Every limitation has an owner + queued fix (§23). Nothing material omitted — §36 no-pretend enforced.

## 23. Future Improvements

Week-2 in dependency order: (1) label 200-human (double-label 60, adjudicate; unblocks ceiling) → supervised LogReg/MiniLM + time-split; (2) hybrid BM25+MiniLM + rerank, recall@3≥0.85/intent + per-intent score floors; (3) pinned LLM drafter (json_schema) + NLI grounding gate + 75-pair judge-human study (κ≥0.60 + safety-recall≥0.90 un-gates LLM judge); (4) 4 escalation-rule fixes (link gate, URL-allowlist, PII→escalate, slang map) + language ID + PII redactor + 2-turn thread context; (5) FastAPI metrics/cache/rate-limit + Docker compose load test + fresh-clone witness + Streamlit triage UI. Each maps to a PARTIAL in FINAL_REVIEW.

## 24. How To Run

Inside `.`, venv `.venv`, `PYTHONPATH=.`: install → `.venv\Scripts\python.exe scripts/train_classifier.py` → `scripts/build_kb.py` → `scripts/build_retrieval_baseline.py` → `scripts/run_eval.py` (+ `scripts/eval_human60.py` for headline) → `.venv\Scripts\python.exe scripts/smoke_fail.py` → `pytest tests -q` (4 pass) → API `POST /predict {text}` → `{intent, confidence, draft_reply, grounding_passage_ids, decision, escalate_reason}`. Artifacts: `models/intent_classifier.pkl`, `data/processed/apple_kb.csv`, `data/indexes/`, `evaluation/golden_v1.csv`, `golden_human_60.csv`, `confusion_human60.csv`, `results*.csv`, `PER_INTENT.md`, `JUDGE_AGREEMENT.md`, `FAILURE_TESTS.md`. Full command list: `README.md`. Data: CC BY-NC-SA (TWCS); synthetic PII in eval only.
