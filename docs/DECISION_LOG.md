# Decision Log — 15 non-obvious decisions (Hiver AppleSupport)

1. **Brand = AppleSupport, not AmazonHelp** (largest Amazon 169k vs Apple 106k). Apple intents partition by KB slice (battery/update/iCloud), Amazon intents diffuse (orders/refunds need PII). Apple voice consistent → template grounding works.
2. **11 intents (10+other), message-level, not thread-level.** Threads drift (follow-up “It’s 11.0.1” ≠ update issue). Single-label + secondary note; multi-intent rate to measure, revisit if >15%.
3. **No vector DB (no Pinecone/Qdrant).** 89k short tweets: sklearn TF-IDF NN builds 17s, p50 35ms, 44MB. Managed DB adds cost/latency without recall gain. Revisit at >1M docs or multilingual.
4. **No agent framework (no LangChain/Graph, LlamaIndex, CrewAI).** Fixed 5-step pipeline; agents compound error (0.95¹⁰≈0.60), break repro. Plain Python + Pydantic dataclass.
5. **Template-grounded replies, not free LLM generation.** No API key in repro, zero hallucinated iOS versions/links, groundedness heuristic 4.75/5. LLM only as optional drafter behind same schema (future).
6. **TF-IDF+LogReg for intent, not fine-tuned BERT.** CPU <2min, 0.945 weak-train acc, interpretable. MiniLM/BERT deferred until human labels >500 (weak-label ceiling 0.517, bigger model just memorizes keywords).
7. **Weak keyword bootstrapping, explicitly labeled as weak.** Needed to start without labels; disclosed circularity (simple 1.0). Human-60 flips=39 prove keywords ≠ truth.
8. **English-only v1; non-English → other + escalate.** ES/PT 800+ rows; translating-and-guessing unsafe. Covers iOS-era cutoff (no post-2017 knowledge).
9. **Four-trigger escalation, not single confidence threshold.** can't-ground / policy-risk / frustration / human-request. Single threshold misses flame/burn (fixed post-smoke-test) and over-escalates short thanks.
10. **DM-deflection treated as triage, not resolution.** 45%+ outbound contain DM; deflection-only passages never ground technical claims. Prevents evasion learning.
11. **Golden 200 weak + 60 human-reviewed, not 200 human.** Time-box: 200 stratified weak for coverage, 60 blind-reviewed for trust (κ reported). Full 200-human is week-2 work.
12. **Judge = heuristic (offline) + LLM hook, not LLM-only.** Heuristic groundedness/actionability runs offline; LLM judge version-pinned, needs wκ≥0.60 + safety-recall≥0.90 to ship, else advisory. Avoids correlation≠agreement trap.
13. **Dedup + template-cap K=5 in KB.** 106k→89k; 1.45% exact duplicates (canned “DM us”). Prevents retrieval collapse to same template.
14. **Stateless FastAPI + SQLite/joblib + LRU, no K8s/Redis.** p50 180ms/p95 192ms on 2vCPU, $6–50/mo to 10k users. Scale via workers → replicas → ANN only on metric triggers.
15. **Report headline = human-60, not weak-200.** Weak-200 simple 1.0 is misleading; human-60 final esc_F1 0.424 + ground 1.0 is the trust claim. “Misleading number” section mandatory in every results print.

## Addendum — Virgin revamp V2 (Phase 2 V-APP, 2026-09-10)

16. **Why VirginTrains primary (not Apple-only):** Apple/Amazon are reviewer-common; Virgin (27,817 outbound, UK rail Delay Repay) is memorable yet still >>200 golden, TWCS-strict (PS datasets only); Apple kept as v1 evidence + transfer proof, not deleted.
17. **Brand-agnostic dict (`src/brands.py`), not forked pipelines:** per-brand {intent_module, model_path+legacy fallback, index_dir+legacy fallback, sensitive/money sets, safety add-ons} + `DEFAULT_BRAND=virgin`; agent/backend/frontend all normalize unknown→virgin so Apple path preserved exactly.
18. **Groq-behind-gate, fail-closed to template (`src/groq_draft.py`):** keyless default; Groq `llama-3.3-70b-versatile` via `GROQ_API_KEY` + `base_url=https://api.groq.com/openai/v1` + JSON-schema `{draft_reply}` only if key set AND ≤280 chars AND £/HH:MM grounded, else template (reason `no-key|no-client|validation-fail|error` in signals; UI/API show `draft_path|groq_reason`).
19. **Rail safety add-ons, not base lexicon edit:** `overcrowd/evacuation/injury/stranded/stampede/derail` live in brand config + `virgin_intents.SAFETY_ADDONS` and OR into `legal_safety` at decision time; base `text_norm` untouched so Apple safety behavior unchanged.
20. **Money-intent escalation per brand, not single threshold:** Apple `purchase_billing_service` vs Virgin `delay_claim/ticket_change_refund/fare_ticketing` each gate at conf<0.70 + money signal (£/refund); delay↔amendment overlap dual-flagged in golden (V-EVAL) so arguable intent still escalates correctly.
