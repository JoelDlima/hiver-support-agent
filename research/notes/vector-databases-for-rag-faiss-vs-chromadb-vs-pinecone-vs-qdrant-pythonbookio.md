---
title: Vector Databases for RAG — FAISS vs ChromaDB vs Pinecone vs Qdrant | PythonBook.io
id: vector-databases-for-rag-faiss-vs-chromadb-vs-pinecone-vs-qdrant-pythonbookio
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:15.924198Z'
source: https://pythonbook.io/python/genai-vector-databases-comparison/
source_domain: pythonbook.io
fetched_at: '2026-09-15T02:28:15.920196Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Vector Databases for RAG — FAISS vs ChromaDB vs Pinecone vs Qdrant | PythonBook.io
Skip to main content
Tutorials
ThePythonBook
by Selva Prabhakaran
Notebook
Run All
Clear
Most RAG tutorials gloss over the vector database choice. "Just use ChromaDB," they say. That works — until your dataset outgrows it and you are stuck rewriting your entire retrieval layer.
The truth is, there is no single best vector database. FAISS, ChromaDB, Pinecone, and Qdrant each solve different problems at different scales. Pick wrong, and you either overpay for infrastructure you do not need, or hit a wall at exactly the wrong moment. This guide will help you pick right the first time — or know exactly when and how to migrate.
The Vector Database Landscape
A vector database stores high-dimensional vectors and finds the closest ones to a query vector, fast. That sounds simple, but the engineering trade-offs between speed, scale, cost, and developer experience are enormous.
These five cover the vast majority of RAG deployments today. Each occupies a distinct niche:
Database
Type
Best For
Scale Sweet Spot
FAISS
In-memory library
Prototyping, offline batch search, research
1K–50M vectors (single machine)
ChromaDB
Embedded database
Local dev, small apps, quick experiments
1K–1M vectors
Pinecone
Managed cloud service
Production apps needing zero-ops
1M–1B vectors
Qdrant
Self-hosted / cloud
Production with complex filtering
1M–100M+ vectors
pgvector
PostgreSQL extension
Teams already on PostgreSQL
1K–5M vectors
Think of it this way: FAISS is a high-performance engine you bolt into your own car. ChromaDB is a golf cart — perfect for the neighbourhood, not for the highway. Pinecone is a taxi service — you pay per ride but never worry about maintenance. Qdrant is a sports car you can either buy or lease.
Prerequisites:
You should be comfortable with
RAG fundamentals
and understand what
embedding models
do. Python 3.9+ and NumPy are all you need for the interactive sections.
How Vector Search Actually Works
Before comparing databases, you need to understand what they all do under the hood. Every vector database answers one question:
given a query vector, which stored vectors are most similar?
The naive approach is brute force: compute the distance between the query and every stored vector. Here is that in five lines of NumPy:
[
]
Run
With random 768-dimensional vectors, the top similarities hover around 0.13-0.15. That is because random vectors in high dimensions are nearly orthogonal. Real embedding models produce vectors with meaningful structure, so you would see much higher similarities for relevant documents.
Brute force works, but how does it scale? The next cell wraps the same dot-product-and-sort logic into a
brute_force_search
function, then times it at three dataset sizes: 1K, 10K, and 50K vectors. Each size gets 20 runs and we average the latency. Watch the linear scaling — every 10x more data means roughly 10x slower queries:
[
]
Run
Key insight:
Brute force scales linearly — O(n) per query. At 1 million vectors, expect ~200ms. At 10 million, ~2 seconds. That is why every serious vector database uses
approximate nearest neighbor (ANN)
algorithms instead.
The two most common ANN algorithms are:
HNSW (Hierarchical Navigable Small World):
Builds a multi-layer graph where each node connects to nearby vectors. Searching hops through the graph — like asking locals for directions instead of checking every house. Used by Qdrant, ChromaDB, Pinecone, and FAISS.
IVF (Inverted File Index):
Clusters vectors into buckets, then only searches the closest buckets. Like looking up a word in a dictionary — go to the right section first, then scan. Used by FAISS.
Let\'s build a simplified IVF index from scratch to see how clustering speeds things up. The code below does three things:
build_ivf_index
assigns every vector to its nearest cluster centroid (like k-means),
ivf_search
only scans the closest
n_probe
clusters instead of all vectors, and then we compare the IVF results against brute force to see how many of the true top-5 we still recover:
[
]
Run
The IVF index searched only 10 out of 100 clusters — roughly 10% of the data — and found most or all of the correct results. In practice with real embeddings, you can search 1-5% of the data and still achieve 95%+ recall.
This is the core trade-off every vector database makes:
exact results vs speed.
The
n_probe
parameter (FAISS) or
ef
parameter (HNSW) controls where you land on that curve.
Pro tip:
If you want to see how embedding quality affects these results, try our
embedding models benchmark
. With real embeddings, the recall-speed curve is even more forgiving because semantically similar documents cluster naturally.
Exercise: Speed vs Recall Trade-off
Your task:
Vary
n_probe
from 1 to 50 on our IVF index and measure both query latency and recall (what fraction of the true top-5 results appear in the approximate results).
Hints:
1. Use
brute_force_search
as ground truth
2. Recall =
len(set(ivf_results) & set(bf_results)) / k
Predict before running: at what
n_probe
value will you get 100% recall?
[
]
Run
Solution:
[
]
Run
FAISS: Facebook's In-Memory Speed Demon
FAISS (Facebook AI Similarity Search) is not a database — it is a library. No server, no network calls, no configuration files. You import it, feed it vectors, and search. That simplicity is its greatest strength and its biggest limitation.
FAISS is the right tool whenever you need the fastest possible search on a single machine — offline batch processing, research experiments, or any situation where the vectors fit in RAM.
python
Why teams choose FAISS
Raw speed.
Sub-millisecond queries on millions of vectors. GPU support pushes this to billions.
Index variety.
Flat, IVF, HNSW, PQ (product quantization for memory reduction), and combinations like
IVF+PQ
.
No server overhead.
Runs in your Python process. Zero network latency.
Battle-tested.
Used inside Meta for recommendation systems serving billions of users.
Where FAISS falls short
No metadata filtering.
You cannot say "find similar vectors WHERE category='science'." Filtering is your problem.
No persistence.
Save/load index files manually with
faiss.write_index()
and
faiss.read_index()
.
No CRUD.
Adding vectors is fast, but deleting or updating specific vectors requires rebuilding the index.
Single-machine only.
No built-in distributed mode.
Warning:
FAISS indexes are not thread-safe for concurrent writes. If your application needs to add vectors while serving queries, you will need to handle locking yourself or use a separate write path.
Pick FAISS when:
You have fewer than 50 million vectors, you do not need metadata filtering, and you want the absolute fastest search on a single machine.
ChromaDB: The Developer-Friendly Default
ChromaDB is what FAISS would look like if a product designer got involved. It wraps vector search in a clean Python API with built-in embedding functions, metadata storage, and persistence — zero configuration required.
Every LangChain tutorial defaults to ChromaDB, and for good reason. You go from zero to working RAG in under 10 lines:
python
Notice what ChromaDB handles that FAISS does not: it embeds text for you (using a default sentence-transformer), stores metadata alongside vectors, and supports filtered queries — all in one API call.
Why teams choose ChromaDB
Zero-config setup.
pip install chromadb
and you are running. No Docker, no server, no API keys.
Built-in embeddings.
Pass raw text — ChromaDB embeds it. Swap models with one parameter.
Metadata filtering.
Filter results by any field using
where
clauses.
Persistence.
Data survives restarts with
PersistentClient
.
Where ChromaDB falls short
Performance ceiling.
HNSW is the only index type. No IVF, PQ, or GPU acceleration.
Memory-bound.
The entire index lives in memory. At 1M+ vectors with 768 dimensions, expect 6+ GB RAM.
Single-node.
No built-in replication or sharding.
Query latency at scale.
Above 500K vectors, query times climb noticeably.
Pick ChromaDB when:
You are prototyping, building a demo, or running a small app with fewer than 500K vectors. It is the right starting point for 80% of RAG projects.
Pinecone: Managed Cloud, Zero Operations
Pinecone takes the opposite approach from FAISS and ChromaDB. You never touch the infrastructure — no index to tune, no memory to manage, no server to operate. You send vectors over HTTPS, and Pinecone handles the rest.
That convenience comes at a literal cost. But for teams that value developer time over compute spend, Pinecone removes an entire category of operational headaches.
python
Why teams choose Pinecone
Zero operations.
No servers, no index tuning, no backups. Pinecone handles scaling and replication.
Serverless pricing.
Pay per query and per GB. The free tier gives 2GB storage and 100K reads/month.
Rich filtering.
$eq
,
$gt
,
$in
,
$and
,
$or
operators on metadata fields.
Namespaces.
Partition data within an index for multi-tenant apps.
Scale.
Handles billions of vectors across distributed infrastructure.
Where Pinecone falls short
Network latency.
Every query is an HTTPS round-trip: 30-100ms minimum. FAISS returns in sub-millisecond.
Vendor lock-in.
Your data lives on Pinecone's infrastructure. Migrating out requires re-indexing.
Cost at scale.
At 50M vectors, expect $70-200/month depending on query volume.
No self-hosting.
Cannot run on your own servers. Data sovereignty concerns may apply.
Pick Pinecone when:
Your team does not want to manage infrastructure, you are building a cloud-native app, and you need reliable scaling. Startups shipping fast are Pinecone's sweet spot.
Qdrant: Open-Source with Advanced Filtering
Qdrant hits the sweet spot for production RAG systems. It gives you the indexing control of FAISS, the developer experience of ChromaDB, and the metadata filtering of Pinecone — plus you can self-host or use their managed cloud.
The filtering system is where Qdrant stands apart. Unlike Pinecone's post-search filtering, Qdrant integrates filters directly into the HNSW graph traversal. This means filtered queries run nearly as fast as unfiltered ones — a technical advantage that matters enormously for multi-tenant applications where every query includes a user-scoped filter.
Key insight:
Most databases filter AFTER searching — they find the 100 nearest vectors, then throw away the ones that don't match your filter. Qdrant filters DURING graph traversal, so it never wastes search effort on vectors that will be discarded.
python
Why teams choose Qdrant
Filtered HNSW.
Filters applied during graph traversal, not after. Filtered queries maintain full speed.
Rich payloads.
Nested JSON with integer ranges, keyword matches, geo-distance, and array containment.
Flexible deployment.
Docker (self-hosted), Qdrant Cloud (managed), or embedded mode.
Built-in quantization.
Scalar and product quantization reduce memory by 4-8x with minimal recall loss.
Open-source (Apache 2.0).
Full source code, no vendor lock-in.
Where Qdrant falls short
Self-hosting complexity.
Production means managing Docker, monitoring, backups, and scaling.
Smaller ecosystem.
Fewer tutorials and community resources than FAISS or Pinecone.
Memory overhead.
10M vectors at 768 dimensions needs ~30 GB RAM for the HNSW index.
Write amplification.
Updating vectors triggers graph rebuilds. Heavy write workloads need careful configuration.
Pick Qdrant when:
You need production vector search with complex filtering, want the option to self-host, and value open-source control. It is the natural next step when a project outgrows ChromaDB.
Honourable Mention: pgvector
If your application already runs on PostgreSQL, you might not need a separate vector database at all.
pgvector
is a PostgreSQL extension that adds vector column types, HNSW and IVF indexes, and cosine/L2/inner-product distance — all accessible through standard SQL.
sql
When pgvector wins:
Your vectors live alongside relational data (users, orders, permissions) and you want transactions across both. No new infrastructure, no new deployment, no new backup strategy.
When it falls short:
Above 5 million vectors, query latency climbs. No built-in quantization or GPU acceleration. The HNSW implementation is younger and less optimized than Qdrant's or FAISS's.
Quick check — predict before scrolling:
If you are building a RAG chatbot for a startup with 200K documents, no special filtering needs, and a 3-person team — which database would you pick? Keep your answer in mind as we build the same pipeline on all four.
Build the Same RAG Pipeline on All Four
Enough theory. Same data, same queries, same embedding approach — four different database APIs. If you have already
built a RAG system from scratch
, you know the retrieval step is where the database choice matters most.
Since FAISS, ChromaDB, Pinecone, and Qdrant all require native libraries or API keys, I will build simulators that mirror each database\'s API patterns using pure NumPy. You can run everything in your browser and see the structural differences.
First, let\'s create a shared dataset: 500 document chunks with metadata (category, source, word count) and 768-dimensional embedding vectors. Every simulator below will search the exact same data so you can compare apples to apples:
[
]
Run
FAISS-Style: Raw Vectors, Manual Everything
With FAISS, you store vectors and search. Metadata filtering? That is your problem:
[
]
Run
ChromaDB-Style: One Call Does Everything
ChromaDB bundles vectors, metadata, and filtering into a single
query()
call:
[
]
Run
Qdrant-Style: Rich Payloads, Complex Filters
Qdrant goes further — range queries on numeric fields, nested must/should logic:
[
]
Run
The code complexity tells the story. FAISS needed manual post-filtering (search broadly, then filter yourself). ChromaDB handled it in one call with a
where
clause. Qdrant added range queries on numeric fields.
In production, this API difference compounds. The more your database handles natively, the less boilerplate you maintain — and the fewer bugs you introduce in filtering logic.
Exercise: Pre-Filter vs Post-Filter Performance
Your task:
Compare two filtering strategies on 50K vectors where only 20% match the filter:
1.
Post-filter:
Search all vectors, then filter by metadata
2.
Pre-filter:
Filter vectors first, then search the subset
Measure latency and check if both approaches find the same results.
Hints:
1. For post-filtering, fetch top-50 then filter (to ensure enough matching results)
2. Use
np.where
to create a boolean mask for pre-filtering
[
]
Run
Solution:
[
]
Run
Speed, Cost, and Scalability Compared
Numbers matter more than marketing. Before looking at published benchmarks, let\'s measure something ourselves: how does raw brute-force search scale in plain NumPy? This gives you a baseline to appreciate what optimized C++ libraries and ANN indexes achieve.
[
]
Run
Real databases with optimized C++ and ANN indexes are much faster. These numbers come from published benchmarks and production deployments:
Metric
FAISS (IVF)
ChromaDB
Pinecone
Qdrant
Query latency (1M vectors)
0.5–2 ms
5–20 ms
30–80 ms
2–8 ms
Query latency (10M vectors)
1–5 ms
50–200 ms
40–100 ms
5–15 ms
Indexing speed
~50K vec/sec
~5K vec/sec
~1K vec/sec (API)
~20K vec/sec
Memory (1M x 768d)
~3 GB
~6 GB
Managed
~4 GB
Max practical scale
50M (single node)
500K–1M
Billions
100M+
The latency gap between FAISS and Pinecone looks huge — 0.5ms vs 30ms. But FAISS is an in-process library with zero network overhead. Pinecone's latency is dominated by the HTTPS round-trip, not the search itself.
Real-World Cost Comparison
For a workload of
5M vectors, 768 dimensions, 100 queries/second:
Component
FAISS
ChromaDB
Pinecone
Qdrant Cloud
Compute
$50–150/mo (your server)
$50–150/mo (your server)
Included
$65/mo (1 node)
Storage
RAM only
Disk + RAM
$0.33/GB/mo
$0.10/GB/mo
API calls
Free
Free
$2/M reads
$0.03/M reads
Ops overhead
High (you manage everything)
Low (embedded)
Zero
Medium or Zero
The surprise: self-hosted is not always cheaper. When you factor in engineering time for server management, monitoring, backups, and incident response, Pinecone's premium often pays for itself.
Production Readiness Checklist
Benchmarks tell you which database is fast. This checklist tells you which one is ready for real users. Production RAG systems fail not because of slow queries, but because of missing backups, zero monitoring, or a cold start after a deploy.
Concern
FAISS
ChromaDB
Pinecone
Qdrant
Backup/Restore
Manual
write_index()
Copy data dir
Automatic (managed)
Snapshots API
Monitoring
DIY (log latencies)
Basic metrics
Dashboard + alerts
Prometheus + Grafana
Multi-tenancy
Not supported
Separate collections
Namespaces
Payload-based filtering
Encryption at rest
Not built-in
Not built-in
Yes (managed)
Yes (self-managed or cloud)
Access control (RBAC)
None
None
API key scopes
API key + collection-level
High availability
None (single process)
None (single process)
Built-in (managed)
Raft consensus (cluster mode)
Pro tip:
If your application stores user-specific documents (multi-tenant RAG), your choice narrows quickly. Pinecone's namespaces or Qdrant's filtered HNSW handle this natively. With FAISS or ChromaDB, you are building tenant isolation from scratch.
Decision Framework: Which Should You Pick?
Choosing a vector database is not one-dimensional. Speed, filtering, ease of use, cost, and scale all matter — but their importance shifts based on your situation. A research lab cares about raw speed. A startup cares about ease. An enterprise cares about filtering and scale.
The function below scores each database 0-10 across five dimensions, then weights those dimensions based on your project parameters. Feed it your constraints and it tells you which database fits best. Try the three scenarios at the bottom — each one represents a real project archetype:
[
]
Run
Here is a practical decision tree for choosing a vector database:
Just prototyping?
ChromaDB. You can migrate later.
Already running PostgreSQL?
pgvector. Zero new infrastructure.
Need sub-millisecond latency, no filtering?
FAISS. Nothing else comes close.
Production app, small team, cloud-native?
Pinecone. The managed experience is worth the premium.
Production with complex filtering or data sovereignty?
Qdrant. Self-host or use their cloud.
Over 100M vectors?
Pinecone (managed) or Milvus (self-hosted, designed for billion-scale).
Answer to the earlier prediction:
For a startup with 200K documents, no special filtering, and a 3-person team — ChromaDB is the right choice. It handles 200K vectors easily, the team gets zero-config setup, and they can migrate to Qdrant or Pinecone when they actually hit scale limits.
Migration: Moving Between Vector Databases
The most common migration path is ChromaDB to Qdrant (outgrowing the prototype) or ChromaDB to Pinecone (wanting managed infrastructure). The core pattern is always extract-transform-load: pull vectors and metadata from the source in batches, reshape them into the target\'s format, and batch-upsert.
The code below demonstrates the transform step — converting a list of
{id, vector, meta}
dicts into the format each target database expects. In production, you would add the actual API calls, but the structural transformation is the part most developers get wrong:
[
]
Run
Common Mistakes When Choosing a Vector Database
Mistake 1: Choosing based on benchmarks alone.
Benchmarks measure query speed on uniform random data. Your data has clusters, outliers, and uneven distributions. FAISS benchmarks often show 0.5ms queries, but production data with skewed cluster sizes can push that to 5ms or more. Always benchmark on YOUR data.
Mistake 2: Ignoring filtered search needs.
Every production RAG system eventually needs metadata filtering — "search only in this user's documents" or "only results from 2024." If you start with FAISS and later need filtering, you are rebuilding the entire retrieval layer.
Mistake 3: Over-engineering for scale you don't have.
A common anti-pattern: deploying Pinecone for 10,000 vectors. ChromaDB handles that in milliseconds for free. Start simple, migrate when you hit real limits — not imagined ones.
Mistake 4: Skipping the recall check.
ANN indexes trade accuracy for speed. If your HNSW
ef
parameter is too low, you return results that are close-ish but miss the truly closest documents. Always measure recall@K on a test set before going to production.
Exercise: Build a Vector Database Recommender
Your task:
Modify the
score_databases
function to add a fifth database —
pgvector
(PostgreSQL extension). Score it based on these characteristics:
- Speed: 6 (slower than dedicated DBs, faster than brute force)
- Filtering: 9 (full SQL WHERE clauses)
- Ease: 8 (if you already use PostgreSQL; 4 if not)
- Cost: 9 (free extension on existing PostgreSQL)
- Scale: 5 (comfortable to ~5M vectors)
Hints:
1. Add a
has_postgresql
parameter to adjust the ease score
2. Run the three scenarios again and see where pgvector lands
[
]
Run
Frequently Asked Questions
Can I use multiple vector databases in the same application?
Yes, and it is more common than you think. A typical setup: ChromaDB for development, Qdrant or Pinecone for production. Your retrieval layer should abstract the database behind an interface so swapping is a config change, not a rewrite.
How do I know when I have outgrown ChromaDB?
Three signals: query latency consistently above 100ms, memory usage exceeding available RAM, or needing multi-tenant isolation. If you hit any of these, evaluate Qdrant or Pinecone.
Does the embedding model affect which database to use?
Not directly — all four accept any embedding dimension. But higher-dimensional models (OpenAI's 3072-dim
text-embedding-3-large
) consume more memory and are slower to search. If memory is tight, use a compact model or enable quantization (FAISS and Qdrant support this natively).
What about Milvus and Weaviate?
Both are excellent — I chose not to feature them as primary comparisons because the four above cover the most common use cases.
Milvus
excels at billion-scale deployments with GPU acceleration (FAISS under the hood) and distributed architecture. If you outgrow single-node Qdrant or need GPU-accelerated search, Milvus is the next step. The learning curve is steeper — you are managing a distributed system with etcd, MinIO, and Pulsar.
Weaviate
offers built-in vectorization (pass raw text, it embeds for you) with better scale than ChromaDB. It also supports hybrid search (BM25 + semantic) out of the box. Choose Weaviate if you want a managed experience similar to Pinecone but with more control and an open-source option.
What is HNSW and why does every database use it?
HNSW (Hierarchical Navigable Small World) builds a multi-layer graph connecting nearby vectors. Searching starts at the top layer (few, widely-spaced nodes) and drills down to the bottom (all nodes) — like zooming in on a map. It dominates because it offers the best recall-speed tradeoff and supports dynamic insertions without retraining.
What is hybrid search and when do I need it?
Hybrid search combines keyword matching (BM25) with semantic vector search. Use it when exact keyword matches matter — product SKUs, error codes, proper nouns. Qdrant, Weaviate, and Pinecone all support hybrid search. For a pure semantic use case like Q&A over documents, vector-only search is usually sufficient.
What\'s Next
You now know how each vector database works, when to pick which, and how to migrate between them. Here are natural next steps:
Improve your retrieval quality
— explore
chunking strategies
to optimize what goes into your vector store
Build a complete RAG pipeline
— follow the
RAG with LangChain
tutorial to wire everything end-to-end
Choose the right embedding model
— our
embedding models benchmark
shows which models give the best retrieval accuracy
Add evaluation
— measure your RAG system's output quality, not just retrieval speed
References
FAISS documentation — Facebook Research.
GitHub Wiki
ChromaDB documentation (v0.5+).
Docs
Pinecone documentation (API v5).
Docs
Qdrant documentation (v1.12+).
Docs
pgvector — Open-source vector extension for PostgreSQL.
GitHub
Malkov, Y. & Yashunin, D. — "Efficient and robust approximate nearest neighbor using Hierarchical Navigable Small World graphs." IEEE TPAMI, 2020.
arXiv
Johnson, J., Douze, M. & Jegou, H. — "Billion-scale similarity search with GPUs." IEEE TBD, 2021.
arXiv
ANN Benchmarks — Comparison of approximate nearest neighbor algorithms.
Link
Related Tutorials
Generative AI & LLMs
·
Intermediate
Embedding Models for RAG in Python — Benchmark and Comparison
90
min
3
exercises
Generative AI & LLMs
·
Intermediate
Build RAG with LangChain: The Standard Production Approach
120
min
3
exercises
Generative AI & LLMs
·
Intermediate
Chunking Strategies for RAG: 8 Methods Compared in Python
90
min
0
exercises
Generative AI & LLMs
·
Intermediate
Build a Chat-with-Documents App: LangChain + Streamlit End-to-End
150
min
3
exercises
Save your progress across devices
Never lose your code, challenges, or XP. Sign up free — no password needed.
Sign up
Send me Python tips & updates
Already have an account?
Send magic link