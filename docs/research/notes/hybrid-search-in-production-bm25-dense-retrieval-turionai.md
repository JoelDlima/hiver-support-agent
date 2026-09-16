---
title: 'Hybrid Search in Production: BM25 + Dense Retrieval | TURION.AI'
id: hybrid-search-in-production-bm25-dense-retrieval-turionai
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:15.003437Z'
source: https://turion.ai/blog/hybrid-search-production-bm25-dense-retrieval/
source_domain: turion.ai
fetched_at: '2026-09-15T02:28:15.001439Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Hybrid Search in Production: BM25 + Dense Retrieval | TURION.AI
/ infrastructure · field note
Hybrid Search in Production: BM25 + Dense Retrieval
Balys Kriksciunas
·
Mon Jul 21 2025
·
7 min read
#ai
#infrastructure
#hybrid-search
#bm25
#rag
#reranker
#retrieval
#vector-database
BM25 + dense retrieval outperforms either alone. Production-ready hybrid search with postgres, reranking, and when to use each approach.
Hybrid Search in Production: BM25 + Dense Retrieval
Ask ten RAG builders what retrieval strategy they use and nine will say “we embed chunks and do vector search.” That works well enough for demos. In production, dense-only retrieval leaves 20–40% of recall on the floor, especially on queries with proper nouns, version numbers, exact phrases, or specialized vocabulary.
The fix — which every serious RAG system eventually adopts — is
hybrid search
: combine keyword-based BM25 with dense vectors, then rerank. This post walks through why, how, and the pitfalls.
Why Dense Alone Misses Things
Dense embeddings capture semantic similarity. “How do I fix a broken login?” and “account access issues resolution” embed close together even though they share few words. That’s the magic.
The failure modes:
1. Proper nouns and rare terms.
“Error code B2-4471” and “error B2-4471 workaround” semantically resemble each other, but both probably embed closer to generic error-related content than to each other.
2. Version numbers and identifiers.
“React 18.2.0” vs “React 18.3.1” — embeddings barely distinguish these, but your docs absolutely must.
3. Short queries.
A 2-word query has little semantic content to work with. Embeddings are noisy on short inputs.
4. Out-of-domain vocabulary.
An embedding model trained on general text may not separate “torque converter stall speed” from “torque converter slip.” Domain-specific terms benefit from exact matching.
5. Multi-intent queries.
“How do I install Python AND set up a virtual env?” — dense search picks one intent; keyword search respects both.
BM25 handles all of these naturally. It’s lexical matching done well: terms, term frequency, inverse document frequency, length normalization.
Why BM25 Alone Misses Things
Flip side:
1. Paraphrasing.
“Subscribe to our newsletter” vs “join our mailing list” — no word overlap, BM25 gives zero.
2. Conceptual queries.
“Best way to handle user authentication” won’t match “JWT tokens with refresh flow” without semantic understanding.
3. Natural-language queries at all.
Modern users phrase queries as questions; BM25 was tuned on keyword-style queries.
Dense handles all of these.
Conclusion:
dense and BM25 are complementary. Good retrieval uses both.
The Production Recipe
Three stages:
Stage 1: Parallel retrieval
Run BM25 and dense search against the same corpus, independently. Get top-K from each (typically K=100).
Stage 2: Fusion
Combine the two ranked lists into one. Most common method:
Reciprocal Rank Fusion (RRF)
, which combines ranks (not scores):
RRF_score(d) = sum over retrievers r of (1 / (k + rank_r(d)))
Typical k=60. Documents in both lists get boosted; documents in one list survive; the top of the combined list is usually better than either individual list.
RRF is simple, parameter-free, and remarkably effective. More sophisticated methods (CombSUM, CombMNZ, learned fusion) exist but RRF is the default we recommend.
Stage 3: Reranking
Take the top ~50 from fused results. Run them through a
cross-encoder reranker
that scores each (query, document) pair with a full attention pass. Keep top 3–10 for the LLM.
Reranking is the single most impactful addition to a RAG stack after fusion. Quality delta is usually larger than any individual retrieval improvement.
Reranker options in 2025:
Cohere Rerank v3
— hosted, strong quality
bge-reranker-v2
— open source, excellent
Jina Reranker v2
— open source, multilingual
mxbai-rerank-large-v1
— open source, competitive
Custom fine-tune
— for domain-specific gains
Rerankers are small enough to run on a single GPU (or even CPU for small volumes). Latency is typically 20–80ms for top-50 scoring.
What The Numbers Look Like
Our internal benchmark on an enterprise technical docs corpus, 250K chunks, 1K held-out queries:
Setup
Recall@10
NDCG@10
Dense only (bge-large)
0.67
0.52
BM25 only
0.58
0.44
Hybrid (RRF fusion)
0.78
0.61
Hybrid + Cohere rerank top 50
0.84
0.72
Hybrid + bge-reranker top 50
0.83
0.71
Hybrid beats either alone by 10–20 points. Reranking adds another 8–10. Together, 30%+ improvement over pure dense.
For consumer search workloads, gains are typically smaller but still positive. For specialized corpora (law, medicine, code, technical docs), hybrid + rerank is essentially required.
Implementation Options
Option 1: Two databases
Run an Elasticsearch or OpenSearch cluster for BM25. Run a separate vector DB (Qdrant, Pinecone) for dense. Application queries both in parallel, fuses, reranks.
Works. Operationally heavy. Two query latencies to manage.
Option 2: Unified database
Some vector databases now support BM25 alongside vectors:
Weaviate
— best-in-class hybrid search with built-in RRF
Milvus 2.5+
— BM25 support
Qdrant
— sparse vectors (BM42) alongside dense
Elasticsearch 8.x
— kNN alongside its mature BM25
OpenSearch 2.9+
— hybrid search with neural plugin
Vespa
— long-time support for both
pgvector + Postgres FTS
— Postgres has full-text search; combine in SQL
Unified is operationally simpler. Use it unless you have a strong reason not to.
Option 3: Use a managed service
Azure AI Search
— built-in hybrid + semantic ranker
Amazon Kendra / OpenSearch Serverless
— AWS options
Algolia
— hybrid search with managed ergonomics
Managed is the fastest path. Cost scales with corpus size and queries.
Hybrid in Weaviate (Example)
Weaviate’s hybrid query is as simple as it should be:
response
=
client
.
collections
.
get
(
"
Docs
"
).
query
.
hybrid
(
query
=
"
how to configure webhooks
"
,
alpha
=
0.5
,
# 0 = pure BM25, 1 = pure vector, 0.5 = even
limit
=
20
,
return_metadata
=[
"
score
"
],
)
alpha
tunes the weighting. Start at 0.5; tune based on eval performance.
Hybrid in pgvector + Postgres FTS
Postgres has excellent full-text search via
tsvector
. Combine with pgvector:
WITH
dense
AS
(
SELECT
id, content,
1
-
(embedding
<=>
$
1
)
AS
dense_score
FROM
docs
ORDER BY
embedding
<=>
$
1
LIMIT
100
),
lex
AS
(
SELECT
id, content, ts_rank_cd(content_tsv, plainto_tsquery($
2
))
AS
bm25_score
FROM
docs
WHERE
content_tsv @@ plainto_tsquery($
2
)
ORDER BY
bm25_score
DESC
LIMIT
100
),
fused
AS
(
SELECT
id,
SUM
(
1
.
0
/
(
60
+
rnk))
AS
rrf_score
FROM
(
SELECT
id,
ROW_NUMBER
()
OVER
(
ORDER BY
dense_score
DESC
)
AS
rnk
FROM
dense
UNION ALL
SELECT
id,
ROW_NUMBER
()
OVER
(
ORDER BY
bm25_score
DESC
)
AS
rnk
FROM
lex
) r
GROUP BY
id
)
SELECT
d
.
id
,
d
.
content
FROM
fused f
JOIN
docs d
ON
d
.
id
=
f
.
id
ORDER BY
f
.
rrf_score
DESC
LIMIT
20
;
Not pretty. Works. For moderate workloads, staying in Postgres is worth the ugliness.
See
pgvector at Scale
.
Tuning Alpha and K
Two knobs that matter:
Alpha (BM25 vs dense weight).
Start at 0.5. Measure eval performance. If your domain is keyword-heavy (legal, technical docs), bias toward BM25 (alpha ~0.3). If paraphrase-heavy (customer support, natural questions), bias toward dense (alpha ~0.7).
Top-K at each stage.
Retrieve 100 from each, fuse to 50, rerank to 5–10. More candidates at retrieval = better recall but higher rerank cost. Less candidates = faster but may miss.
Tune on your eval set. Our defaults work for most cases; don’t over-tune.
Metadata Filtering
Hybrid search with metadata filters is a common real-world need: “find docs matching this query, only from this tenant, only from last 30 days.”
All unified databases (Weaviate, Milvus, etc.) support metadata filtering in hybrid queries. The filter applies before scoring, so it doesn’t compromise recall.
Be careful: filters that are very selective (<1% of docs) can break ANN search’s recall guarantees. Over-retrieve in those cases. See
pgvector’s filtering section
for general patterns.
When NOT To Use Hybrid
A few cases where hybrid isn’t worth the complexity:
1. Tiny corpora.
Under ~5K docs, a well-tuned dense search plus a reranker is often enough. Keep things simple.
2. Perfectly uniform natural language queries.
If your users type clean questions and never proper nouns, pure dense can be competitive.
3. Multilingual corpora where BM25 is hard to tune.
Dense embeddings from multilingual models (e5, BGE-M3) often outperform BM25 here. Tokenization for many languages is a separate fight.
4. When latency is hyper-critical.
A 20ms rerank pass is a non-starter for sub-50ms P95 workloads. Skip rerank; consider skipping hybrid.
For 90% of production RAG, hybrid + rerank is the right default.
Evaluating Retrieval Quality
Before tuning retrieval, you need evals:
Labeled query-document relevance
— gold standard, expensive
Synthetic evals
— use an LLM to generate queries from chunks; use the chunk IDs as ground truth. Cheap, surprisingly effective.
A/B testing in production
— ultimate truth; requires you to be live.
Start with synthetic evals. Build a set of ~100 query/chunk pairs where the “right answer” chunk is known. Measure recall@10 and NDCG@10 across retrieval configs. See
Model Evals in Production
.
The Short Version
Pure dense retrieval is a 2023 pattern
In 2025, production RAG uses
BM25 + dense, fused with RRF, reranked
by a cross-encoder
Weaviate, Milvus, Elasticsearch, Qdrant, and pgvector+FTS all support this natively
Expect 20–40% recall improvement over dense-only
Rerankers add another 8–15% on top
Evaluate on labeled or synthetic queries; don’t guess
Further Reading
Choosing a Vector Database in 2024: A Practical Guide
pgvector at Scale: When Postgres Is Enough
Building RAG Agent with LangChain
Tuning a RAG retrieval stack?
Reach out
— we can audit and improve retrieval quality quickly.
← back to blog
Related Posts
Infrastructure
Context Engineering: Storage, Retrieval, and the New Memory Stack
Agents need more than a vector database. A tour of the memory stack production agents actually use — working, short-term, long-term, semantic, episodic — and the infrastructure behind each.
Mar 17, 2026
Infrastructure
pgvector at Scale: When Postgres Is Enough
pgvector gets faster every release and now handles workloads that used to require a dedicated vector database. When to stick with Postgres, when to graduate, and how to tune either way.
Mar 10, 2025
Infrastructure
Choosing a Vector Database in 2024: A Practical Guide
Pinecone, Qdrant, Weaviate, Milvus, pgvector, and the newer entrants — a working engineer's comparison across latency, recall, cost, and operational complexity. How to pick without regret.
Sep 5, 2024