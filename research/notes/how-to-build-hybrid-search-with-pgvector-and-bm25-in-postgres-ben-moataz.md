---
title: How to Build Hybrid Search with pgvector and BM25 in Postgres | Ben Moataz
id: how-to-build-hybrid-search-with-pgvector-and-bm25-in-postgres-ben-moataz
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:48:02.085923Z'
source: https://www.benmoataz.com/posts/hybrid-search-pgvector-bm25
source_domain: www.benmoataz.com
fetched_at: '2026-09-15T02:48:02.084924Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

How to Build Hybrid Search with pgvector and BM25 in Postgres | Ben Moataz
Skip to content
← Back to writing
search
How to Build Hybrid Search with pgvector and BM25 in Postgres
Build hybrid search in Postgres with pgvector, tsvector, and RRF in one SQL query — the schema, index tuning, and when you actually need real BM25.
Ben Moataz
·
July 12, 2026  ·  10 min read  ·  Updated Jul 12, 2026
search
If your documents already live in Postgres, you can build production hybrid search without a dedicated search cluster: one table with a
tsvector
column for lexical matching and a
vector
column for semantic matching, two indexes, and a single query that fuses the two rankings with Reciprocal Rank Fusion. This guide is the actual build — the schema decisions, the index tuning, the fusion query with metadata filtering pushed down, and the honest bit most vendor tutorials skip: Postgres full-text search is
not
BM25, so I’ll tell you exactly when native ranking is good enough and when you should reach for a real BM25 extension.
If you’re still deciding
whether
hybrid is worth the complexity, read
hybrid search vs vector search
first — that piece argues the why. This one is the how.
The short answer
Put one row per chunk in a table with three things that matter: a generated
tsvector
for keyword search, a
vector
embedding for semantic search, and the metadata you’ll filter on. Index the
tsvector
with GIN and the
vector
with HNSW. At query time, run a lexical CTE and a semantic CTE in parallel, each returning a small ranked candidate set, then fuse them with RRF —
sum(1 / (k + rank))
— in the same SQL statement. That’s a real hybrid retriever on infrastructure you already run, and it’s maybe forty lines of SQL.
The schema: one table, three columns that earn their keep
The whole system hangs off one table. The design decision is which columns you materialize:
CREATE
TABLE
chunks
(
id
bigserial
PRIMARY KEY
,
document_id
bigint
NOT NULL
,
title
text
,
content
text
NOT NULL
,
source
text
,
-- metadata you'll filter/boost on
published_at
timestamptz
,
embedding
vector
(
1024
),
-- match your model's dimensions
fts tsvector
GENERATED
ALWAYS
AS
(
setweight(to_tsvector(
'english'
,
coalesce
(title,
''
)),
'A'
)
||
setweight(to_tsvector(
'english'
, content),
'B'
)
) STORED
);
Two choices here matter more than they look. First,
fts
is a
generated column
— Postgres recomputes it on every insert or update, so the lexical index can never drift out of sync with the text. You never maintain it. Second,
setweight
gives title matches weight
A
and body matches weight
B
, so a keyword in the title outranks the same keyword buried in the body. That’s the cheapest relevance win in the whole stack and it costs one line.
The
embedding
dimension has to match your model exactly — 1024, 1536, 768, whatever you’re using. Get it wrong and inserts fail, which is the good kind of failure.
Postgres full-text search is not BM25 — and when that’s fine
Here’s the thing the vendor blogs gloss over. Postgres
ts_rank
and
ts_rank_cd
are
not
BM25. BM25 is a probabilistic ranking function with IDF term weighting and a specific document-length normalization;
ts_rank
is a simpler term-frequency score, and
ts_rank_cd
adds cover density (how close the matched terms are). They rank differently, and on a keyword-only search the difference is visible.
But look at what the lexical arm actually contributes to a
hybrid
system. The set of documents that match
fts @@ query
is identical no matter which ranking function you use — the
@@
operator decides membership,
ts_rank
only decides the order
within
the lexical list. And RRF throws away the raw scores entirely; it only reads rank position. So the lexical ranking function influences the order of your top ~50 lexical candidates, which then get re-ordered by fusion anyway.
The practical consequence:
for the lexical arm of a hybrid + RRF system, native
ts_rank_cd
is usually good enough
, and “I’m not using true BM25” is a much smaller problem than a first read suggests. Where the gap actually bites you:
Score-based (weighted) fusion.
If you skip RRF and instead normalize and blend raw scores,
ts_rank
values are a shakier signal than BM25 scores, and the blend is harder to reason about.
Lexical-dominant corpora.
Long documents, short keyword queries, big vocabulary — the exact regime where BM25’s length normalization changes the top result, not just the tail order.
You’re replacing Elasticsearch
and someone will diff the two systems’ top-10 side by side.
If none of those describe you, start with native FTS and don’t add a dependency you don’t need yet.
Indexing both sides (and the tuning knobs that matter)
You need one index per retriever:
CREATE
INDEX
chunks_fts_idx
ON
chunks
USING
gin (fts);
CREATE
INDEX
chunks_embedding_idx
ON
chunks
USING
hnsw (embedding vector_cosine_ops);
CREATE
INDEX
chunks_source_idx
ON
chunks (source);
GIN is the right index for
tsvector
; there’s little to tune there. The vector index is where the decisions live:
HNSW vs IVFFlat.
HNSW builds a navigable graph — higher recall, slower to build, more memory, but you can insert into it incrementally without retraining. IVFFlat partitions vectors into lists and is cheaper to build but needs a representative sample to train its lists and degrades if you build it on an near-empty table. For most systems I reach for
HNSW
and accept the build cost, because it tolerates a growing corpus without a rebuild step.
Recall vs latency at query time.
HNSW’s
hnsw.ef_search
(default 40) and IVFFlat’s
ivfflat.probes
(default 1) trade recall for latency. Raise them when you’re missing relevant results, lower them when the vector scan is your latency budget’s problem. These are session settings — tune per workload, measure, don’t guess.
The filtered-search trap.
vector_cosine_ops
matches the
<=>
cosine-distance operator; use
vector_l2_ops
with
<->
if your model wants L2. And be aware that HNSW does its filtering
after
the graph walk by default, so a restrictive metadata filter can make it return fewer than
k
rows. Recent pgvector versions support iterative scans to fix this; if you filter hard, either enable that or keep a partial index for the common filter values.
The fusion query: RRF in one SQL statement
This is the whole retriever. A lexical CTE, a semantic CTE, each bounded to a small candidate set, fused by RRF, with an optional metadata filter pushed down into
both
arms so you never fuse rows you’d have thrown away:
WITH
lexical
AS
(
SELECT
id,
row_number
()
OVER
(
ORDER BY
ts_rank_cd(fts, query)
DESC
)
AS
rank
FROM
chunks, websearch_to_tsquery(
'english'
, $
1
)
AS
query
WHERE
fts @@ query
AND
($
3
::
text
IS
NULL
OR
source
=
$
3
)
ORDER BY
ts_rank_cd(fts, query)
DESC
LIMIT
50
),
semantic
AS
(
SELECT
id,
row_number
()
OVER
(
ORDER BY
embedding
<=>
$
2
::
vector
)
AS
rank
FROM
chunks
WHERE
($
3
::
text
IS
NULL
OR
source
=
$
3
)
ORDER BY
embedding
<=>
$
2
::
vector
LIMIT
50
)
SELECT
id,
sum
(
1
.
0
/
(
60
+
rank))
AS
rrf_score
FROM
(
SELECT
*
FROM
lexical
UNION ALL
SELECT
*
FROM
semantic) fused
GROUP BY
id
ORDER BY
rrf_score
DESC
LIMIT
20
;
Three bind parameters:
$1
is the raw user query text,
$2
is the query embedding,
$3
is an optional
source
filter (pass
NULL
to search everything). A few deliberate choices:
websearch_to_tsquery
, not
plainto_tsquery
. It understands the query syntax users actually type — quoted
"exact phrases"
,
or
, and
-exclusions
— instead of AND-ing every word together. For real user input it’s the honest default.
Filter pushdown into both CTEs.
The
($3 IS NULL OR source = $3)
guard runs inside each retriever, so a scoped query (“only from this source”) narrows the candidate set
before
fusion. Filtering after fusion would waste half your candidate budget on rows you’re about to discard.
60
is the RRF smoothing constant
k
.
Sixty is the standard starting point from the original RRF paper and a fine default. Larger
k
flattens the contribution of top ranks (more democratic across retrievers); smaller
k
lets the #1 in each list dominate. It’s worth tuning, but only after you have an eval set to tune against.
Hand the top 20 to a cross-encoder reranker before the LLM sees them — that second stage is the highest-leverage quality step and it’s covered in the
hybrid search vs vector search
guide, so I won’t repeat it here.
When you actually need a real BM25 extension
If you hit the lexical-dominant regime above, the Postgres ecosystem now has genuine BM25 implementations you can drop in:
ParadeDB’s
pg_search
(a real BM25 index over your text), and the
VectorChord
BM25 extension, among others. They give you true BM25 scoring, field boosting, and phrase handling that native FTS can’t match, and some are explicitly built to replace an Elasticsearch tier.
The honest tradeoff: each is another extension to install, pin, and carry through upgrades — operational surface that native
tsvector
(which ships with Postgres) doesn’t add. My rule is to start on native FTS + RRF, ship it, measure retrieval quality against a real eval set, and adopt a BM25 extension only when the numbers say the lexical arm is the bottleneck. Adding it on day one because a benchmark blog told you to is how you inherit a dependency you never needed.
Keeping both indexes fresh
The
fts
column is generated, so it’s always current — that’s a whole class of bug you designed away. The
embedding is not
, and that’s the failure mode that quietly rots hybrid search: someone updates a chunk’s
content
, the generated
tsvector
refreshes automatically, but the
embedding
still encodes the
old
text. Now your lexical arm is fresh and your semantic arm is lying, and retrieval quality drifts in a way no error log will ever show you.
Fix it structurally. Recompute the embedding in the same write path that changes the content — or, if embedding is async, have the update
NULL
the embedding and let a backfill worker re-embed the nulled rows, so a stale vector can never masquerade as a fresh one. This is the same “ingestion is a state machine, not a script” discipline I wrote about in
scaling the ingest
: the write path owns keeping derived data consistent, and if it doesn’t, the drift is invisible until someone notices the answers got worse.
Latency and the two-stage shape
The query above does two index scans and a small group-and-sort. Keep it fast the obvious ways: bound each retriever’s
LIMIT
(50 candidates each is plenty of recall for a top-20), tune
hnsw.ef_search
to the smallest value that holds your recall, and make sure your metadata filters are indexed. The fusion itself is cheap — you’re summing over at most 100 rows.
Think of this whole query as
stage one
: cheap, broad, bounded recall. Reranking is stage two: expensive, precise, and run only over the fused top-N. That two-stage shape is what lets a retriever be both fast and genuinely relevant, and it’s the same pattern whether your vectors live in Postgres or a dedicated store.
When you don’t need this
Hybrid-in-Postgres is the right call when your data already lives in Postgres and your queries mix meaning with identifiers. It’s the wrong call in a few honest cases. If your corpus is small and every query is a natural-language question with no codes or names, pure
pgvector
search is simpler and fine — skip the lexical arm. If users only ever search exact tokens, plain full-text search alone is enough and the embeddings are dead weight. And if you’re already at a scale where you run a dedicated vector database and a dedicated search cluster and both are earning their keep, don’t collapse them into Postgres for its own sake. Hybrid-in-Postgres earns its place by removing infrastructure, not by proving a point.
FAQ
Do I need the ParadeDB or VectorChord extension to do this?
No. The entire query above runs on stock Postgres with just the
pgvector
extension —
tsvector
and full-text search are built in, and RRF is plain SQL. Reach for a BM25 extension only when you’ve measured that native lexical ranking is your bottleneck.
Is
ts_rank
good enough if it isn’t real BM25?
For the lexical arm of a hybrid + RRF system, usually yes. RRF only uses rank order, and the set of matching documents is the same regardless of ranking function, so
ts_rank_cd
mostly decides intra-list order that fusion re-shuffles anyway. The gap matters most for score-based fusion and long-document, short-query workloads.
RRF or weighted score fusion — which should I use?
Start with RRF. It ignores raw scores, so you don’t have to reconcile
ts_rank
values against cosine distances, which live on completely different scales. Move to a tuned weighted blend only when you need per-query-type control — for example letting the lexical signal dominate on identifier lookups.
How do I set the RRF
k
constant?
Sixty is the standard default and a good starting point. Tune it only once you have an evaluation set: larger
k
spreads credit more evenly across retrievers, smaller
k
rewards being #1 in either list. Tuning it by feel without measurement is how relevance regresses silently —
relevance tuning is an operational discipline
, not a one-time constant.
Can I filter by metadata and still get good hybrid results?
Yes, but push the filter into both retriever CTEs (as shown) so each arm returns filtered candidates before fusion. Watch the HNSW post-filtering trap: a restrictive filter can make the vector arm under-return, so enable iterative scans or keep a partial index for common filter values.
This is the retrieval architecture I design and audit for teams whose search works in the demo and disappoints in production — see
how I approach relevance and correlation scoring
, or the full
hybrid search & RAG guide hub
.
Written by
Ben Moataz
Systems Architect, Consultant, and Product Builder
This article is grounded in hands-on work across Correlation and scoring, including systems such as SOVRINT, TraxinteL, and Viralink.
I write from hands-on work across product systems, evidence pipelines, ranking layers, monitoring surfaces, and automation runtimes that have to stay reliable under operational pressure.
→
Years spent building product systems, automation infrastructure, and operator-facing platforms.
→
Project records and case studies tied directly to the same capability lanes discussed in the writing.
→
A public archive designed to connect essays back to real systems, delivery constraints, and consulting work.
About Ben
Work with Ben →
Relevant work
Expertise and case studies tied to this article.
Relevant services
If this maps to a system problem you're trying to
                          solve, these capability pages are the fastest way into
                          the service side of the site.
Capability
Correlation and scoring
Entity resolution, de-duplication, ranking, and confidence models for turning noisy signals into usable intelligence.
entity resolution
ranking systems
Open capability
→
Related case studies
These project records show the same operating logic in
                          shipped systems, products, or internal platforms.
Project record
2024 - present
SOVRINT
A narrative intelligence platform for tracking coordinated messaging, propagation paths, and sentiment drift across the open web.
Open project
→
Project record
2024 - present
TraxinteL
A modular intelligence core for ingest, enrichment, entity resolution, ranking, and delivery.
Open project
→
Project record
2024
Viralink
A propagation and reach analytics engine for measuring how information spreads, accelerates, and compounds across platforms.
Open project
→
Related reading
More writing on adjacent systems problems.
Embedding Model Selection for Retrieval: How to Choose Without Trusting a Leaderboard
How I pick an embedding model for retrieval: the constraints that decide it before quality does, a bake-off you can run, and the re-index nobody prices.
search
How to Evaluate RAG Retrieval: Eval Sets, Metrics, and Ship Gates
Retrieval eval is 20% metrics and 80% eval set. How I build one that survives re-indexing, which number to read at which k, and how to gate a change.
search
RAG Chunking Strategy: How to Split Documents So Retrieval Works
Chunking decides what your retriever can find. Here's how I split real documents — structure-first boundaries, parent-child units, and how to prove it worked.
search
Next article
Hybrid Search vs Vector Search: Why RAG Retrieval Needs Both
Vector search understands meaning but fumbles exact identifiers; keyword search is the opposite. Here's how I build hybrid retrieval that does both — with fusion, reranking, and a pgvector setup.
Work with me
Building or fixing a system like this?
This is exactly the kind of work I get brought in for. Teams unsure whether a system, architecture, or workflow will hold up under real load and scrutiny.
System Audit
Start here · fixed scope
→
A focused review of the system, architecture, or codebase in question.
→
A clear map of the risks, bottlenecks, and failure modes that matter.
→
A prioritized roadmap — what to fix first, and what to leave alone.
See how to work with me →
Reserve a call
Subscribe
Get new essays by email
Field notes on intelligence systems, evidence engineering, and automation that survives reality. No noise.
Subscribe via RSS →
Email capture isn't wired up yet — the RSS feed is live now.
ESC
Navigation
Home
Landing page and featured essays
Work With Me
Open work with me
Projects
Open projects
About
Open about
Writing
Open writing
Projects
SOVRINT
A narrative intelligence platform for tracking coordinated messaging, propagation paths, and sentiment drift across the open web.
100mL
A gated procurement marketplace connecting vetted hotels with premium amenity, wellness, and lifestyle brands, built around a provable money path.
TraxinteL
A modular intelligence core for ingest, enrichment, entity resolution, ranking, and delivery.
WingAgent
An automation and intelligence system for high-scale behavior orchestration, capture, and feedback loops inside fast-moving platform environments.
Viralink
A propagation and reach analytics engine for measuring how information spreads, accelerates, and compounds across platforms.
Capabilities
Collection and orchestration
Browser automation, distributed workers, scheduling, and fleet-level recovery for public-data systems that need to keep working under drift.
Correlation and scoring
Entity resolution, de-duplication, ranking, and confidence models for turning noisy signals into usable intelligence.
Evidence and forensics
Capture pipelines, artifact integrity, provenance, and review-ready delivery for teams that need defensible outputs.
Monitoring and operations
Observability, alert routing, SLAs, and operator-grade feedback loops for systems that cannot fail silently.
SEO hubs
Solutions
Use-case hub pages across cities and sources
Cities
Location-based landing page hubs
Integrations
Source-specific landing page hubs
Industries
Industry-specific landing page hubs
Compare
Comparison pages for build vs buy and workflow tradeoffs
Answers
Query-targeted reference pages
Solution pages
Due diligence
Screening workflows break when identities are fragmented and review trails depend on manual search tabs.
Brand protection
Brand monitoring becomes noisy when listings, impersonation cases, and evidence live in disconnected tools.
Executive protection
Executive-risk workflows fail when exposure signals cannot be triaged, preserved, and escalated quickly.
Entity resolution
Raw search results stay noisy unless fragmented records can be stitched into explainable entities.
Evidence capture
Screenshots without provenance and supporting context rarely survive serious downstream review.
Investigations workflows
Case work slows down when search, enrichment, and evidence review happen in different systems.
Social monitoring
Social monitoring becomes fragile when surface drift, rate limits, and review overload all hit at once.
Threat intelligence
Threat workflows degrade when collection, retrieval, and review are treated like separate problems.
Industry pages
Financial services
adverse media, diligence, and exposure review
Corporate security
executive protection, exposure monitoring, and escalation design
Trust and safety
abuse detection, narrative shifts, and response loops
Compliance
screening, evidence retention, and defensible review trails
Investigations firms
case enrichment, evidence capture, and client-ready delivery
Brand protection
impersonation response, marketplace monitoring, and evidence capture
Media and reputation
narrative monitoring, publisher coverage, and escalation context
Marketplace operations
seller intelligence, listing drift, and enforcement workflows
Public sector
investigative review, evidence integrity, and operational clarity
Compare pages
Custom OSINT Platform vs Off-the-Shelf Tools
Teams with repeatable workflows usually outgrow generic tools once evidence quality, reliability, and operator fit all matter.
Hybrid Search vs Vector-Only Search
Hybrid retrieval wins when exact identifiers and contextual relevance both matter inside the same workflow.
Evidence Capture Pipelines vs Screenshots Alone
Screenshot-only workflows are easy to start with but weak under serious review or chain-of-custody pressure.
Monitoring Control Plane vs Basic Alerting
Basic alerts tell you something broke. A control plane helps operators understand why and what to do next.
Entity Resolution System vs Manual Research
Manual work helps exploration, but systems win once confidence, repeatability, and review quality matter.
Distributed Worker Fleets vs Single-Node Scrapers
Single-node setups are fine for prototypes, but fleets are what make reliability and replay manageable at scale.
Answer pages
How to build an OSINT pipeline for investigations
A reference page for teams asking how to build an OSINT pipeline for investigations without letting the workflow collapse under scale or ambiguity.
How to build an OSINT pipeline for due diligence
A reference page for teams asking how to build an OSINT pipeline for due diligence without letting the workflow collapse under scale or ambiguity.
How to build an OSINT pipeline for brand protection
A reference page for teams asking how to build an OSINT pipeline for brand protection without letting the workflow collapse under scale or ambiguity.
How to design an entity resolution system for investigations
A reference page for teams asking how to design an entity resolution system for investigations without letting the workflow collapse under scale or ambiguity.
How to design an entity resolution system for due diligence
A reference page for teams asking how to design an entity resolution system for due diligence without letting the workflow collapse under scale or ambiguity.
How to design an entity resolution system for brand protection
A reference page for teams asking how to design an entity resolution system for brand protection without letting the workflow collapse under scale or ambiguity.
How to design an evidence capture workflow for investigations
A reference page for teams asking how to design an evidence capture workflow for investigations without letting the workflow collapse under scale or ambiguity.
How to design an evidence capture workflow for due diligence
A reference page for teams asking how to design an evidence capture workflow for due diligence without letting the workflow collapse under scale or ambiguity.
Recent posts
Embedding Model Selection for Retrieval: How to Choose Without Trusting a Leaderboard
How I pick an embedding model for retrieval: the constraints that decide it before quality does, a bake-off you can run, and the re-index nobody prices.
Worker Fleet Architecture at Scale: Pools, Scaling Signals, and Draining
Scaling a worker fleet isn't adding workers to one queue. Here's how I partition pools, pick the scaling signal, and drain workers without losing jobs.
How to Evaluate RAG Retrieval: Eval Sets, Metrics, and Ship Gates
Retrieval eval is 20% metrics and 80% eval set. How I build one that survives re-indexing, which number to read at which k, and how to gate a change.
RAG Chunking Strategy: How to Split Documents So Retrieval Works
Chunking decides what your retriever can find. Here's how I split real documents — structure-first boundaries, parent-child units, and how to prove it worked.
Why Is My RAG Retrieval Bad? A Diagnostic Order of Operations
Bad RAG retrieval is four or five distinct failures wearing one costume. Here's how I localize which one you have before changing anything.
Retry with Exponential Backoff and Jitter (and the Retry Budget Nobody Sets)
Exponential backoff caps how fast a client retries; jitter stops every client retrying together. Here's the retry logic I actually ship, and the two limits most teams miss.
Reranking in RAG: How a Cross-Encoder Fixes Retrieval Quality
A cross-encoder reranker re-scores your top candidates by reading query and document together. Here's how I add one, size it, and prove it worked.
Dead Letter Queue Design Patterns (Routing, Envelopes, and Redrive)
A DLQ is the giving-up mechanism, and most teams build it wrong. The routing, envelope, isolation, and redrive patterns I use to make failed messages recoverable.
No matches yet. Try a project name, a topic like
search
, or a page title.