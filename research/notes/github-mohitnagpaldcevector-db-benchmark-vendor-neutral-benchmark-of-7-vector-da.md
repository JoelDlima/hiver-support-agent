---
title: 'GitHub - MohitNagpaldce/vector-db-benchmark: Vendor-neutral benchmark of 7
  vector databases (Qdrant, Weaviate, Milvus, pgvector, Chroma, LanceDB, FAISS) at
  1M and 10M scale · GitHub'
id: github-mohitnagpaldcevector-db-benchmark-vendor-neutral-benchmark-of-7-vector-da
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.195163Z'
source: https://github.com/MohitNagpaldce/vector-db-benchmark
source_domain: github.com
fetched_at: '2026-09-15T02:28:17.192162Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: code
deprecated: false
---

GitHub - MohitNagpaldce/vector-db-benchmark: Vendor-neutral benchmark of 7 vector databases (Qdrant, Weaviate, Milvus, pgvector, Chroma, LanceDB, FAISS) at 1M and 10M scale · GitHub
Skip to content
You signed in with another tab or window.
Reload
to refresh your session.
You signed out in another tab or window.
Reload
to refresh your session.
You switched accounts on another tab or window.
Reload
to refresh your session.
Dismiss alert
MohitNagpaldce
/
vector-db-benchmark
Public
Notifications
You must be signed in to change notification settings
Fork
0
Star
0
main
Branches
Tags
Go to file
Code
Open more actions menu
Latest commit
History
2 Commits
2 Commits
Folders and files
Name
Name
Last commit message
Last commit date
analysis
analysis
outputs/
figures
outputs/
figures
paper
paper
results
results
scripts
scripts
src
src
.gitignore
.gitignore
PLAN.md
PLAN.md
README.md
README.md
docker-compose.yml
docker-compose.yml
package.json
package.json
requirements.txt
requirements.txt
View all files
Repository files navigation
Vector DB Benchmark
Reproducible benchmark harness comparing vector database engines on
recall, latency, throughput, index build time, and memory footprint —
currently covering Qdrant, Weaviate, Milvus, pgvector, Chroma, LanceDB,
and FAISS across SIFT1M (L2) and GloVe-1.2M (cosine). See
PLAN.md
for
the full paper plan and methodology.
Running
pip install -r requirements.txt
docker-compose up -d
#
server-based engines
python scripts/download_datasets.py --dataset all
python scripts/smoke_test.py --all
#
fast sanity check, 10K synthetic vectors
python src/runner.py --dataset all --vectors 1000000 --runs 3
python analysis/plot_results.py --results results/results_all_1000000.csv
src/runner.py --engines qdrant,milvus
runs a subset — useful when only
re-testing an engine you just added or fixed.
Adding a new vector DB
The engine layer is a plugin registry, not a hardcoded list — adding a
new DB never requires editing
runner.py
,
smoke_test.py
, or the
analysis scripts.
Copy
src/engines/_template_engine.py.example
to
src/engines/<yourdb>_engine.py
and implement the methods against
your DB's client library.
If it runs as a server, add a service to
docker-compose.yml
.
Run
python scripts/smoke_test.py --all
— your engine is picked up
automatically (importing the
engines
package auto-discovers every
module in
src/engines/
and registers whichever
VectorDBEngine
subclasses are decorated with
@register_engine
).
Run
python src/runner.py --dataset sift --vectors 100000 --engines yourdb
to sanity-check on a small slice before a full 1M-vector run.
Before trusting the numbers, check your adapter against three real bugs
found while building the existing seven (details in the template file
and in the "claude sessions" doc history):
match the distance metric to the dataset's actual metric (don't fake
cosine with raw dot product on unnormalized vectors — corrupted
Milvus's recall to ~11% until fixed)
confirm the index actually finished building after insert, using an
index-specific counter, not a generic "healthy" status (a Qdrant
config bug silently fell back to brute-force search for an entire
benchmark run because "green" status doesn't mean "indexed")
confirm
set_query_params()
takes effect on a query issued right
after calling it, not just at build time (Chroma's
ef_search
update
doesn't propagate post-creation in
chromadb==0.5.0
— a known,
documented limitation, not yet fixed)
Results
results/results_all_1000000.csv
is the merged, final dataset (7
engines x 2 datasets x 5
ef_search
values = 70 rows). Figures land in
outputs/figures/
:
recall_latency_{sift,glove}.png
— the key recall/latency tradeoff curve
qps_at_recall{095,09}.png
— best throughput at a fixed recall bar
(the standard ann-benchmarks comparison axis — more meaningful across
engines than comparing QPS at the same raw
ef_search
, since that
parameter isn't on the same scale across algorithms)
build_time.png
,
peak_memory.png
,
qps_ef64.png
— operational cost
About
Vendor-neutral benchmark of 7 vector databases (Qdrant, Weaviate, Milvus, pgvector, Chroma, LanceDB, FAISS) at 1M and 10M scale
Resources
Readme
Activity
Stars
0
stars
Watchers
0
watching
Forks
0
forks
Report repository
Releases
Packages
Contributors
Languages
You can’t perform that action at this time.