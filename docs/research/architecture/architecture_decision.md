# Architecture Decision — evidence-driven (Hiver AppleSupport, 2026-09-10)

## Selected
`validate → normalize → TFIDF-LogReg classify (11) → TFIDF-NN retrieve top-5 (Apple KB 89k) → template-grounded draft + cite IDs → 4-trigger escalate → typed output`

- Classifier: TF-IDF 1-2g (30k feats) + LogReg C=2, trained 30k weak labels, `models/intent_classifier.pkl`. Train acc vs weak 0.945 (optimistic).
- Retrieval: TF-IDF + sklearn NN cosine, `data/indexes/`, 17s build, p50 35ms. Chunk = single tweet + thread context at query time. No reranker v1 (heuristic score = 1-dist).
- Draft: per-intent template (brand voice: acknowledge → diagnostic → DM redirect) + passage IDs. No free generation → no invented versions/links.
- Escalate: rules (legal_safety incl. flame/burn fix, account/data-loss, human_request, injection, money_threshold, low_conf<0.45/no_grounding/link_only, frustration+sensitive, huge). See `src/agent.py`.
- Serve: FastAPI stateless `/predict`, joblib load-once, LRU future, request-ID logs.

## Per-component evidence

| Component | Candidates | Evidence/Exp | Selected | Why / rejected |
|---|---|---|---|---|
| Intent | keyword, TFIDF-LogReg, MiniLM+LogReg, DistilBERT | weak-200: keyword 1.0 (circular), LogReg 0.795; human-60: keyword 0.517, LogReg 0.433; MiniLM needs torch/GPU, +2-3% est. | TFIDF-LogReg | CPU <2min, interpretable, within weak ceiling; BERT overkill until human labels |
| Retrieval | BM25/TFIDF, MiniLM dense, hybrid+rerank, Pinecone/Qdrant | 89k docs, TFIDF p50 35ms, 44MB; hybrid +3-5% recall est. but needs embeddings DL; managed $$$ | TFIDF-NN | sufficient, offline, repro; hybrid week-2 |
| Draft | canned, keyword top-1 copy, template, small LLM (gpt-4o-mini) | template ground 4.75/5, ≥4 rate 1.0 vs copy 2.98; LLM $0.0002-5/req + key + halluc risk | template | safe, keyless, brand-consistent |
| Escalate | threshold-only, 4-trigger rules, LLM judge | threshold misses flame (smoke-test fail → fixed), rules esc_F1 0.471 vs 0.0 baselines on human-60 | 4-trigger | safety recall > precision; threshold anti-pattern |
| Orchestration | LangGraph, LlamaIndex, custom | 5 fixed steps, no planning/tool-choice needed | custom deterministic | frameworks add failure/cost, no benefit |
| Store | SQLite/joblib/JSONL, pgvector, Redis | <100k docs, read-only, single-process | joblib + CSV | simplest; SQLite FTS optional |
| Eval judge | heuristic, LLM-as-judge | heuristic offline; LLM needs κ≥0.60 gate | heuristic now, LLM gated | avoids judge-hacking |

## Cost/complexity/failure
- Cost: $0 inference (CPU), 180ms p50. LLM path would be $0.0002-5/req.
- Failure: empty→escalate; link-only→escalate; no-retrieval→escalate (score<0.08); injection→escalate (added); safety lexicon patched (flame/burn). Intent miss on safety still possible → escalation guardrail covers decision even when intent wrong.
- Scale: workers=cores → replicas → ANN. No rewrite needed.

## Tech audit
Considered: MiniLM/e5, bge-reranker, Llama-3/Mistral, LangChain/Graph, Qdrant/Pinecone, Redis/K8s. Selected: sklearn/pandas/FastAPI/pytest only. Rejected: cost/complexity without measured gain. Revisit: hybrid+rerank + supervised classifier on 500+ human labels + pinned LLM drafter with NLI gate (week-2).
