---
title: 'ChromaDB vs Qdrant vs FAISS vs pgvector: Vector Database for Local RAG | local-llm.net'
id: chromadb-vs-qdrant-vs-faiss-vs-pgvector-vector-database-for-local-rag-local-llmn
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.505755Z'
source: https://www.local-llm.net/compare/chromadb-vs-qdrant-vs-faiss-vs-pgvector/
source_domain: www.local-llm.net
fetched_at: '2026-09-15T02:28:17.502757Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

ChromaDB vs Qdrant vs FAISS vs pgvector: Vector Database for Local RAG | local-llm.net
Every retrieval-augmented generation system needs a place to store and search embeddings, and the choice of vector database significantly affects both developer experience and application performance. ChromaDB, Qdrant, FAISS, and pgvector represent four distinct approaches to vector storage — from embedded libraries to purpose-built databases to PostgreSQL extensions — and the right choice depends on your scale, infrastructure, and how much operational complexity you are willing to manage. This comparison covers the dimensions that matter most for local RAG applications: performance, setup friction, local-first design, metadata filtering, and production readiness.
Quick Comparison
Feature
ChromaDB
Qdrant
FAISS
pgvector
Type
Embedded vector DB
Vector search engine
Vector search library
PostgreSQL extension
Developer
Chroma
Qdrant
Meta (Facebook)
pgvector community
Language
Python (Rust core)
Rust
C++ (Python bindings)
C (PostgreSQL extension)
Deployment
In-process or client-server
Client-server or cloud
In-process (library)
PostgreSQL server
Setup
pip install chromadb
Docker or binary
pip install faiss-cpu
PostgreSQL +
CREATE EXTENSION
Persistence
Built-in (SQLite + files)
Built-in (custom storage)
Manual (save/load to disk)
PostgreSQL storage
CRUD operations
Full (add, update, delete)
Full (upsert, delete, scroll)
Limited (add, search; delete is complex)
Full (SQL INSERT, UPDATE, DELETE)
Metadata filtering
Yes (where clause)
Yes (rich filter syntax)
No (external filtering)
Yes (SQL WHERE)
Index types
HNSW
HNSW, IVF, scalar/product quantization
IVF, PQ, HNSW, Flat, LSH, many others
IVF-Flat, HNSW
GPU acceleration
No
No
Yes (faiss-gpu)
No
Max vectors (practical)
~5M
100M+
Billions (with proper indexing)
~10M
Disk-based indexing
No
Yes (mmap)
Yes (on-disk indexes)
Yes (PostgreSQL pages)
Multi-tenancy
Collections
Collections + payload indexes
Manual
Schemas/tables
License
Apache 2.0
Apache 2.0
MIT
PostgreSQL License
Cloud offering
Chroma Cloud
Qdrant Cloud
N/A (library)
Managed PostgreSQL providers
Performance at Scale Benchmark
The following benchmarks show approximate query latency (p50) for cosine similarity search returning top-10 results across different dataset sizes. All tests use 1536-dimensional vectors (OpenAI ada-002 size) on a machine with 32 GB RAM and NVMe SSD.
Dataset Size
ChromaDB
Qdrant
FAISS (HNSW)
pgvector (HNSW)
10K vectors
<5ms
<3ms
<1ms
<5ms
100K vectors
~8ms
~4ms
~1ms
~10ms
500K vectors
~15ms
~6ms
~2ms
~25ms
1M vectors
~30ms
~8ms
~3ms
~45ms
5M vectors
~150ms
~12ms
~4ms
~120ms
10M vectors
Degraded
~15ms
~5ms
~200ms
Key observations:
FAISS is the fastest at every scale because it is a pure in-memory search library with highly optimized algorithms and no database overhead
Qdrant is the fastest purpose-built database, maintaining low latency even at 10M+ vectors
ChromaDB performs well up to ~1M vectors but degrades at larger scales
pgvector’s latency increases more steeply due to PostgreSQL’s general-purpose storage engine
For most local RAG applications, dataset sizes are under 1M vectors, where all four options perform well. The performance differences become significant only at larger scales.
Ease of Setup
ChromaDB
ChromaDB has the lowest setup friction of any vector database:
import
chromadb
client
=
chromadb.Client()
# In-memory
# or
client
=
chromadb.PersistentClient(
path
=
"./chroma_data"
)
# Persistent
collection
=
client.create_collection(
"my_docs"
)
collection.add(
documents
=
[
"doc1"
,
"doc2"
],
ids
=
[
"id1"
,
"id2"
]
)
results
=
collection.query(
query_texts
=
[
"search query"
],
n_results
=
5
)
No server to start, no configuration files, no Docker containers. ChromaDB runs in your Python process and persists to the local filesystem. It even handles embedding generation automatically if you do not provide pre-computed embeddings.
This simplicity makes ChromaDB the default choice in tutorials, documentation, and starter projects. LlamaIndex uses ChromaDB as its default vector store, and LangChain’s RAG tutorials frequently feature it.
Qdrant
Qdrant requires running a server, typically via Docker:
docker
run
-p
6333:6333
qdrant/qdrant
Then connect from Python:
from
qdrant_client
import
QdrantClient
client
=
QdrantClient(
host
=
"localhost"
,
port
=
6333
)
The Docker approach adds a setup step but provides a proper client-server architecture from the start. Qdrant also offers an in-memory mode for testing and a local persistent mode that does not require Docker, reducing friction for development.
FAISS
FAISS is a library, not a service:
import
faiss
import
numpy
as
np
dimension
=
1536
index
=
faiss.IndexHNSWFlat(dimension,
32
)
index.add(np.array(vectors,
dtype
=
'float32'
))
D, I
=
index.search(np.array(query,
dtype
=
'float32'
),
k
=
10
)
FAISS setup is minimal — install the package and start indexing. However, FAISS does not handle persistence, metadata, or CRUD operations. You must implement saving/loading indexes to disk, maintain a separate mapping from index IDs to document metadata, and handle deletions (which many FAISS index types do not support natively).
FAISS is the easiest to start with for pure search but the hardest to build a complete application around.
pgvector
pgvector requires a running PostgreSQL instance:
CREATE
EXTENSION
vector
;
CREATE
TABLE
documents
(
id
SERIAL
PRIMARY KEY
,
content
TEXT
,
embedding
vector
(
1536
)
);
CREATE
INDEX
ON
documents
USING
hnsw (embedding vector_cosine_ops);
If you already have PostgreSQL in your stack, adding pgvector is straightforward — install the extension and create a vector column. If you do not have PostgreSQL, the setup overhead is significant compared to ChromaDB or FAISS.
Local-First Design
ChromaDB
ChromaDB is the most local-first option. It runs entirely in your process, stores data on the local filesystem, and has no external dependencies. There is no network communication, no server process, and no containerization required. For local RAG applications where data should never leave the machine, ChromaDB’s embedded architecture is ideal.
FAISS
FAISS is inherently local — it is a library that operates on in-memory data structures. There is no server, no network, and no external storage. FAISS is as local as it gets, but the lack of built-in persistence means you need to implement local storage yourself.
Qdrant
Qdrant is a client-server system, but it runs locally in Docker or as a native binary. Data stays on your machine. For local development, the in-memory or local persistent modes eliminate the need for Docker entirely.
pgvector
pgvector is as local as your PostgreSQL installation. If PostgreSQL runs on the same machine, data stays local. However, PostgreSQL is a full database server with its own processes, connections, and resource management — more infrastructure than ChromaDB or FAISS for a purely local use case.
Metadata Filtering
Metadata filtering is essential for RAG applications that need to filter results by document type, date, source, or other attributes.
Qdrant
Qdrant has the most powerful metadata filtering. Its payload filtering supports nested objects, arrays, numeric ranges, string matching, geo-coordinates, and boolean combinations. Payload indexes can be created for frequently filtered fields, ensuring filter performance does not degrade with scale.
client.search(
collection_name
=
"docs"
,
query_vector
=
embedding,
query_filter
=
Filter(
must
=
[
FieldCondition(
key
=
"source"
,
match
=
MatchValue(
value
=
"annual_report"
)),
FieldCondition(
key
=
"year"
,
range
=
Range(
gte
=
2024
))
]
),
limit
=
10
)
pgvector
pgvector inherits PostgreSQL’s full SQL filtering capabilities. Any column in the table can be used in WHERE clauses alongside vector similarity search. This is extremely powerful — you can filter on complex conditions, joins, and subqueries that no purpose-built vector database supports.
SELECT
*
FROM
documents
WHERE
category
=
'report'
AND
created_at
>
'2024-01-01'
ORDER BY
embedding
<=>
query_vector
LIMIT
10
;
ChromaDB
ChromaDB supports metadata filtering through its
where
parameter with operators like
$eq
,
$ne
,
$gt
,
$lt
,
$in
, and
$nin
. The filtering is functional for common use cases but less expressive than Qdrant’s or pgvector’s.
FAISS
FAISS has no built-in metadata filtering. You must implement pre-filtering (select candidate IDs before search) or post-filtering (filter results after search) in your application code. This is the most flexible approach (you can implement any filtering logic) but requires the most work.
Production Readiness
Dimension
ChromaDB
Qdrant
FAISS
pgvector
Persistence
Reliable (SQLite-backed)
Reliable (WAL, snapshots)
Manual
PostgreSQL (battle-tested)
Backup/restore
File copy
Snapshots, replication
File copy
pg_dump, replication
Monitoring
Basic
Prometheus metrics
None (library)
PostgreSQL monitoring
Replication
No
Yes (Raft consensus)
No
PostgreSQL replication
Sharding
No
Yes (distributed mode)
Manual
Citus extension
Authentication
Basic API key
API key, TLS
N/A
PostgreSQL auth
Availability
Single node
Distributed cluster
N/A
PostgreSQL HA
Qdrant
is the most production-ready purpose-built vector database — distributed mode, replication, snapshots, and monitoring.
pgvector
inherits PostgreSQL’s decades of production hardening — replication, point-in-time recovery, monitoring, authentication, and the entire PostgreSQL operations ecosystem.
ChromaDB
is production-capable for small-to-medium workloads but lacks replication and distributed features.
FAISS
is a library and requires building all production infrastructure around it.
The Bottom Line
Choose ChromaDB
for local RAG projects, prototyping, and applications with under 1M vectors. Its zero-configuration embedded design gets you started fastest.
Choose Qdrant
for production RAG applications that need to scale, especially when metadata filtering is important. It offers the best combination of performance, features, and operational maturity among purpose-built vector databases.
Choose FAISS
when search speed is the absolute priority and you are willing to build persistence, metadata, and management infrastructure around it. FAISS is ideal as a component inside a larger system, not as a standalone database.
Choose pgvector
when you already run PostgreSQL and want to avoid adding another database to your stack. The ability to query vectors alongside relational data with SQL is uniquely powerful, and PostgreSQL’s operational maturity compensates for pgvector’s performance limitations at scale.
Frequently Asked Questions
Which vector database should I use for a simple local RAG project?
ChromaDB is the best choice for simple local RAG. It runs in-process with zero configuration — just pip install chromadb and start storing embeddings. It is the default vector store in LlamaIndex and is well-supported in LangChain. For projects with under 1 million documents, ChromaDB's simplicity is hard to beat.
Can pgvector compete with purpose-built vector databases?
For small to medium workloads (under 5 million vectors), pgvector performs well enough for most RAG applications, especially with HNSW indexes. Its main advantage is that you can store vectors alongside relational data in a single PostgreSQL database, avoiding the operational overhead of a separate vector database. For large-scale or latency-critical workloads, Qdrant and FAISS will outperform pgvector.
Is FAISS a database or just a library?
FAISS is a library, not a database. It provides efficient similarity search algorithms but does not include persistence, client-server architecture, metadata storage, or CRUD operations. You must handle storage, updates, and metadata yourself. FAISS is ideal when you need maximum search speed and are willing to build the infrastructure around it, or when you embed it within another system.