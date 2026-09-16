---
title: 'Hybrid Search in Production: Why BM25 Still Wins on the Queries That Matter'
id: hybrid-search-in-production-why-bm25-still-wins-on-the-queries-that-matter
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.934282Z'
source: https://tianpan.co/blog/2026/04/12/hybrid-search-production-bm25-dense-embeddings
source_domain: tianpan.co
fetched_at: '2026-09-15T02:28:17.931283Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Hybrid Search in Production: Why BM25 Still Wins on the Queries That Matter
Skip to main content
Ask AI
BM25 was published in 1994. The math is simple enough to fit on a whiteboard. Yet in production retrieval benchmarks in 2025, it still outperforms multi-billion-parameter dense embedding models on a meaningful slice of real-world queries. Teams that discover this after deploying pure vector search tend to discover it the worst possible way: through hallucination complaints they can't reproduce in evaluation, because their eval set was built from queries that already worked.
This is the retrieval equivalent of sampling bias. Dense retrieval fails on a specific and predictable query shape. The failure is silent — the LLM still produces fluent, confident-sounding answers from whatever fragments it retrieved. No error log fires. No latency spike. Just quietly wrong answers for users querying product SKUs, error codes, API names, or anything that is lexically specific rather than semantically general.
The fix is hybrid search. But "hybrid search" is underspecified as an engineering decision. This post covers what the failure modes actually look like, how to fuse retrieval signals correctly, where the reranking layer goes, and — most critically — how to find the query types your current pipeline is silently failing on before users find them for you.
The Queries Dense Retrieval Gets Wrong
​
Dense embedding models encode a passage into a single fixed-size vector by pooling over all token representations. This pooling is what enables semantic generalization — "vacation" and "time off" end up geometrically close — but it also destroys lexical identity for specific strings.
When a user queries
ERR_SSL_VERSION_OR_CIPHER_MISMATCH
, that exact token sequence gets averaged with every other token in the context window. The resulting vector captures something like "document about SSL errors" rather than "document containing this specific error string." BM25, by contrast, scores against an inverted index of exact tokens. It either finds the term or it doesn't. There is no blurring.
The query types that systematically fail under pure dense retrieval follow a consistent pattern:
Error codes and identifiers
: Exact strings like
0x80070005
,
INV-2024-00847
, or
ENOMEM
have near-zero semantic representation signal. The embedding model has no principled way to distinguish between similar-looking identifiers.
Product SKUs and model numbers
:
RTX-4090
and
RTX-4070
are semantically almost identical — neighboring vectors in embedding space — but they're different products with different specs and prices.
Function names and library identifiers
: Querying for
torch.nn.functional.cross_entropy
produces an embedding close to other PyTorch documentation. It's not reliably close to
documents containing that specific call signature
.
Rare named entities
: When a query contains one rare and highly specific term alongside common words, the rare term's signal gets averaged away. BM25's inverted index is unaffected by rarity — a term that appears in five documents is matched just as precisely as one that appears in five million.
Domain jargon with controlled vocabulary
: Technical documentation, legal text, and medical records use specific terms-of-art that appear consistently. Semantic blurring here introduces errors where precision matters most.
The 2021 BEIR benchmark made this embarrassingly clear: dense retrieval models trained on MS MARCO frequently failed to outperform BM25 in zero-shot cross-domain evaluation. That result prompted most serious RAG teams to stop treating dense retrieval as a BM25 replacement and start treating it as a complement.
The Silent Failure Pattern
​
The harder problem is that these failures don't announce themselves.
When BM25 misses a document, the retrieval set is visibly incomplete. When a dense retriever misses a document because the query contained a rare identifier, the LLM still gets a retrieval set — just the wrong one. It generates a fluent, plausible response from whatever fragments were retrieved. This is exactly the shape of hallucination that is hardest to catch in evaluation: confident, internally consistent, and wrong about specifics.
The diagnostic asymmetry compounds over time. Eval sets built from production query logs contain cases where the system produced answers users accepted. The cases where the system confidently provided wrong specifics to users who didn't know enough to push back are systematically absent from the feedback signal. You end up optimizing retrieval against the queries you already handle well.
The practical consequence: teams deploying dense-only retrieval often have retrieval quality problems that their eval metrics don't reflect. Recall@10 on their internal eval set looks acceptable. Recall@10 on queries involving exact identifiers is low, but no one checked because those queries didn't make it into the eval set.
There's a measurement fix for this, which the diagnosis section covers. But the architectural fix is hybrid search — running both retrieval paths and fusing their results.
Score Fusion: RRF vs. Convex Combination
​
Hybrid retrieval produces two ranked lists — one from BM25, one from dense ANN — and needs to merge them into a single ranked result. The two main approaches have meaningfully different tradeoffs.
Reciprocal Rank Fusion (RRF)
converts each candidate document's position in each ranked list into a score:
1/(k + rank)
, where
k=60
by convention. Documents that rank high in both lists accumulate higher scores. The key advantage is that RRF is score-scale agnostic — BM25 scores and cosine similarities are on completely incompatible scales, and RRF sidesteps normalization by operating on ranks rather than scores.
This makes RRF a safe default. It requires no labeled data, it's robust to distribution shift, and all major vector databases ship it natively: Elasticsearch 8.x, OpenSearch 2.12+, Weaviate, Qdrant. For cold-start hybrid retrieval, start here.
The limitation is that RRF discards score magnitude. A document ranked first with a cosine similarity of 0.99 gets the same RRF contribution as one ranked first with a similarity of 0.51. When your retrieval set has genuine quality signals embedded in the scores — not just ranks — that information is lost.
Convex combination
addresses this:
score = α × score_dense + (1-α) × score_sparse
. Bruch et al. (2022) showed that with as few as ~40 labeled query-relevance pairs, tuning this single
α
parameter consistently outperforms RRF both in-domain and out-of-domain. The normalization method (min-max, z-score, or other linear normalization) is a second-order concern — any linear normalization produces similar results.
In practice,
α
should vary by query domain:
Technical documentation with controlled terminology:
α ≈ 0.3
(weight sparse heavily)
Conversational and policy documents:
α ≈ 0.7–0.8
(weight semantic heavily)
Balanced mixed content:
α ≈ 0.6
The 2025 frontier is per-query dynamic alpha — detecting whether an incoming query is keyword-heavy or semantic, and adjusting
α
accordingly at query time rather than setting it per-collection.
A practical benchmark on Elasticsearch (Wands furniture dataset, 2025) illustrates the gap: plain RRF added ~1.3% NDCG over BM25 baseline, while a tiered approach that boosted all-term-match documents 100x, any-term-match 10x, and fell back to vector at 0.1x added 7.5% — showing that naive RRF significantly undersells what properly tuned hybrid retrieval can achieve.
The Reranking Layer
​
Retrieval is a high-recall problem. Reranking is a high-precision problem. They require different models, and conflating them is a common architectural mistake.
The structure is two-stage:
First stage (retrieval)
: Hybrid BM25 + dense ANN with RRF fusion, fetching top-100 candidates. Fast, high-recall, operating on pre-computed indices.
Second stage (reranking)
: A cross-encoder model scores each (query, candidate) pair jointly — the model sees both simultaneously and produces a relevance score with full attention between tokens. Applied to the top 30–50 candidates, not the full set.
Cross-encoders are dramatically more accurate than bi-encoders because they can capture phrase-level alignment and inter-token dependencies. The cost is that they cannot pre-compute document representations — every (query, document) pair requires a forward pass. This makes them impractical as first-stage retrievers at any meaningful scale, but appropriate for reranking a small candidate set.
The latency arithmetic is non-obvious. A cross-encoder over 30 candidates costs roughly 100–200ms total. The same model applied to 200 candidates blows the latency budget by 5–10x. The practical rule: fix your first-stage recall so you don't need to rerank more than 50 candidates. If you need to rerank 200+ to get acceptable precision, the first-stage retrieval is broken.
ColBERT-style late interaction offers an alternative that sits between bi-encoders and cross-encoders. The MaxSim mechanism computes relevance as the sum of per-query-token maximum similarities across document tokens — preserving phrase-level alignment while allowing document representations to be pre-computed. Models like BGE-M3 (released January 2024) unify dense, sparse, and late-interaction modes in a single 550M parameter checkpoint, substantially reducing infrastructure complexity for teams that previously needed three separate models.
The recommended production pipeline looks like this: hybrid retrieval → top-100 → MMR de-duplication to remove near-identical chunks → cross-encoder reranking → top-5 to top-10 for the LLM context window. Adding MMR before reranking matters because sending near-duplicate chunks to a cross-encoder wastes its capacity and pushes genuinely different relevant documents out of the ranked set.
Diagnosing Which Query Types You're Failing On
​
The standard retrieval metrics — Recall@10, MRR, NDCG@10 — look fine if your eval set is built from production query logs. They catch the queries your system handles. They miss the queries that silently fail.
The fix requires two changes to how eval sets are constructed and analyzed.
Stratify by query type.
Cluster your query logs by structural type: exact identifier queries (contain a specific code, SKU, or name), keyword-heavy queries (contain specific rare technical terms), semantic queries (conceptual questions without specific identifiers), navigational queries (looking for a specific document by title or reference). Compute Recall@K separately for each cluster. If your keyword and identifier clusters have 40% recall while semantic clusters have 85%, you know exactly where to invest.
Synthesize adversarial queries.
Production queries systematically exclude failures. Use an LLM to generate synthetic queries with exact identifiers drawn from your document corpus — model numbers, error codes, function names, contract IDs. Run these through your retrieval pipeline and check whether the source documents come back. These are the failure cases you're currently not measuring.
The embedding rot problem is separate but related: as your document corpus updates, as your LLM is swapped out, and as embedding models get retrained, your vector index degrades gradually. Monitor cosine similarity score distributions over time. A downward drift in average top-1 similarity is a signal that retrieval quality is eroding before it's visible in downstream LLM output quality.
A production system with healthy hybrid retrieval should see Recall@10 around 85–91%, MRR above 0.80, and Hit Rate@10 (at least one relevant document in the top 10) above 90% for FAQ-style applications. These numbers require both the right architecture and the right eval methodology to measure accurately.
What to Actually Build
​
For most teams, the right starting point is RRF-based hybrid search using the native capabilities of their existing vector database. Elasticsearch, Weaviate, OpenSearch, Qdrant, and Pinecone all support it out of the box. The effort is configuration, not implementation.
Once you have 40+ labeled query-relevance pairs for your domain, migrate from RRF to a tuned convex combination. The marginal improvement is consistent across benchmarks and the implementation is straightforward.
Add cross-encoder reranking when you observe a persistent precision gap — when the right documents come back in positions 3–8 but not positions 1–2. Keep the candidate set below 50 to stay within latency budget.
The highest-ROI diagnostic investment is building an adversarial eval set with exact-identifier queries before optimizing anything else. Teams that skip this step optimize retrieval against the queries they already handle, ship hybrid search, and are surprised when hallucination rates for identifier-heavy queries don't improve. The problem wasn't the retrieval architecture — it was that the pipeline never included those queries in the first place, and now you've added hybrid search without measuring whether it helped the query types that needed it.
Dense embeddings are genuinely powerful for semantic retrieval. BM25 is genuinely powerful for lexical retrieval. The production argument stopped being "which one is better" a few years ago. It's now entirely about how precisely you understand where each one fails — and building the measurement infrastructure to know which gap is costing you most.
References
https://ragaboutit.com/hybrid-retrieval-for-enterprise-rag-when-to-use-bm25-vectors-or-both/
https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167
https://softwaredoug.com/blog/2025/03/13/elasticsearch-hybrid-search-strategies
https://weaviate.io/blog/hybrid-search-fusion-algorithms
https://weaviate.io/blog/late-interaction-overview
https://qdrant.tech/articles/hybrid-search/
https://superlinked.com/vectorhub/articles/optimizing-rag-with-hybrid-search-reranking
https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch
https://arxiv.org/abs/2210.11934
https://arxiv.org/abs/2503.23013
https://mljourney.com/sparse-vs-dense-retrieval-for-rag-bm25-embeddings-and-hybrid-search/
https://www.paradedb.com/blog/hybrid-search-in-postgresql-the-missing-manual
Let's stay in touch and follow me for more
Twitter
LinkedIn
Telegram
Discord
小红书
Related articles
10 min read
Live Web Grounding in Production: Why Calling a Search API Is Only the Beginning
Why 'just call a search API' produces a far worse pipeline than engineers expect — the latency math, failure modes, and architectural patterns that separate…
rag
llm
11 min read
Multimodal RAG in Production: When You Need to Search Images, Audio, and Text Together
A practitioner's guide to multimodal RAG: embedding alignment across modalities, cross-modal reranking strategies, cost and latency tradeoffs, and the failure…
insider
rag
10 min read
The Embedding Deprecation That Halved Your Retrieval Recall Without a Deploy
A deprecated embedding endpoint that quietly routes to a 'compatibility' successor can halve your retrieval recall without a deploy. Here's why query/document…
rag
embeddings
9 min read
The Chunk Boundary That Bisected the Sentence Your Answer Depended On
Fixed-size token chunking cuts critical clauses in half, and neither fragment retrieves alone. A look at why the failure is invisible to standard evals and…
insider
rag
9 min read
The Embedding That Aged Out of Meaning
An embedded knowledge base silently rots as the world's vocabulary moves on. Recall dashboards miss it because they grade by yesterday's notion of similar.
insider
rag
Back to All Posts