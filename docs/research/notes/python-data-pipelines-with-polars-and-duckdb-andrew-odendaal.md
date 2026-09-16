---
title: Python Data Pipelines with Polars and DuckDB | Andrew Odendaal
id: python-data-pipelines-with-polars-and-duckdb-andrew-odendaal
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:15.681525Z'
source: https://andrewodendaal.com/python-data-pipelines-polars-duckdb/
source_domain: andrewodendaal.com
fetched_at: '2026-09-15T02:28:15.678524Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Python Data Pipelines with Polars and DuckDB | Andrew Odendaal
Skip to content
All
Recent
Popular Tags
Start typing to search articles...
↑
↓
Navigate
Enter
Select
Esc
Close
I’m going to say something that’ll upset a lot of people: pandas had its run. Polars is just better.
I don’t mean that lightly. I spent years writing pandas code. I taught pandas to junior developers. I built production systems on pandas. But after migrating several data pipelines to Polars and DuckDB over the past year, I can’t go back. The performance difference isn’t incremental — it’s a different universe.
This isn’t a theoretical comparison. I’m going to walk you through building real data pipelines with Polars and DuckDB, share the war story that convinced me to switch, and give you enough code to start migrating your own work today.
The Pipeline That Broke Me
Last year I inherited a daily ETL pipeline at work. It pulled transaction data from S3, joined it with customer records, ran a bunch of aggregations, and wrote the results to Parquet files for our analytics team. Standard stuff.
The problem? It took 45 minutes to run. Every single day.
The pipeline processed about 80 million rows across three datasets. The pandas code looked reasonable — whoever wrote it wasn’t doing anything obviously wrong. They used
merge()
for joins,
groupby()
for aggregations,
read_parquet()
for I/O. Textbook pandas.
But pandas was choking on it. Memory usage peaked at 32GB. The joins alone took 20 minutes. And because pandas is single-threaded for most operations, it was using one core of a 16-core machine while the other 15 sat idle.
I’d been reading about Polars and figured I had nothing to lose. I rewrote the pipeline over a weekend. Same logic, same inputs, same outputs.
It ran in 90 seconds.
Not 90 minutes. Ninety seconds. A 30x improvement with roughly the same amount of code. That’s when I knew pandas was done for me.
Why Polars and DuckDB Are Faster
Before we get into code, it’s worth understanding why these tools are so much faster. It’s not magic — it’s better engineering decisions.
Polars is written in Rust and built on Apache Arrow’s columnar memory format. That gives it three massive advantages over pandas. First, it uses all your CPU cores automatically. No
multiprocessing
hacks, no
swifter
, no
dask
— just parallel execution out of the box. Second, it has a lazy evaluation engine that optimizes your query plan before executing it. It’ll reorder operations, push down predicates, and eliminate unnecessary work. Third, Arrow’s columnar format means better cache locality and zero-copy interop with other tools.
DuckDB takes a different approach. It’s an embedded analytical database — think SQLite but designed for OLAP workloads instead of OLTP. It runs inside your Python process with no server to manage. It can query Parquet files, CSV files, and even pandas DataFrames directly using SQL. And it’s absurdly fast at aggregations and joins because it uses vectorized execution.
The beautiful thing is that Polars and DuckDB complement each other perfectly. Use Polars for DataFrame-style transformations and DuckDB when SQL is more natural. They both speak Arrow, so passing data between them is essentially free.
Getting Started with Polars
Let’s start with Polars basics. If you’ve used pandas, the API will feel familiar but different enough to trip you up.
import
polars
as
pl
# Reading data - similar to pandas but returns a Polars DataFrame
df
=
pl
.
read_parquet(
"transactions.parquet"
)
# Lazy reading - doesn't load data until you collect()
lf
=
pl
.
scan_parquet(
"transactions.parquet"
)
# Basic selection and filtering
result
=
(
lf
.
filter(pl
.
col(
"amount"
)
>
100
)
.
select([
"customer_id"
,
"amount"
,
"timestamp"
])
.
collect()
)
The biggest mental shift is lazy evaluation. In pandas, every operation executes immediately. In Polars, you build up a query plan with
scan_
and method chains, then call
.collect()
to execute it all at once. This lets the query optimizer do its thing.
Here’s where it gets interesting — expressions. Polars expressions are way more powerful than anything pandas offers:
result
=
(
pl
.
scan_parquet(
"transactions.parquet"
)
.
with_columns([
(pl
.
col(
"amount"
)
*
pl
.
col(
"quantity"
))
.
alias(
"total"
),
pl
.
col(
"timestamp"
)
.
dt
.
month()
.
alias(
"month"
),
pl
.
col(
"category"
)
.
cast(pl
.
Categorical),
])
.
filter(pl
.
col(
"total"
)
>
50
)
.
group_by([
"customer_id"
,
"month"
])
.
agg([
pl
.
col(
"total"
)
.
sum()
.
alias(
"monthly_spend"
),
pl
.
col(
"total"
)
.
mean()
.
alias(
"avg_transaction"
),
pl
.
len()
.
alias(
"transaction_count"
),
])
.
sort(
"monthly_spend"
, descending
=
True
)
.
collect()
)
That entire chain gets optimized as a single query plan. Polars will figure out that it only needs to read certain columns from the Parquet file, apply the filter as early as possible, and parallelize the aggregation across cores. You don’t have to think about any of that — it just happens.
DuckDB: SQL Where It Makes Sense
I’ll be honest — sometimes SQL is just the right tool. Complex joins, window functions, CTEs — I can write those faster in SQL than in any DataFrame API. That’s where DuckDB shines.
import
duckdb
# Query Parquet files directly with SQL - no loading step
result
=
duckdb
.
sql(
"""
SELECT
customer_id,
DATE_TRUNC('month', timestamp) AS month,
SUM(amount * quantity) AS monthly_spend,
COUNT(*) AS transactions
FROM 'transactions.parquet'
WHERE amount > 0
GROUP BY customer_id, month
ORDER BY monthly_spend DESC
"""
)
.
pl()
# .pl() returns a Polars DataFrame
That
.pl()
at the end is the secret sauce. DuckDB returns results as a Polars DataFrame with zero-copy thanks to Arrow. You can also go the other direction — DuckDB can query Polars DataFrames directly:
import
polars
as
pl
import
duckdb
df
=
pl
.
read_parquet(
"customers.parquet"
)
# DuckDB can query Polars DataFrames by name
enriched
=
duckdb
.
sql(
"""
SELECT
t.customer_id,
c.segment,
SUM(t.amount) AS total_spend
FROM 'transactions.parquet' t
JOIN df c ON t.customer_id = c.customer_id
GROUP BY t.customer_id, c.segment
"""
)
.
pl()
DuckDB automatically recognizes Python variables that are DataFrames and makes them available as tables. It’s genuinely magical the first time you see it work.
For window functions, DuckDB’s SQL is hard to beat:
ranked
=
duckdb
.
sql(
"""
SELECT *,
ROW_NUMBER() OVER (
PARTITION BY customer_id
ORDER BY timestamp DESC
) AS recency_rank
FROM 'transactions.parquet'
QUALIFY recency_rank <= 5
"""
)
.
pl()
Try writing that
QUALIFY
clause in pandas. I’ll wait.
Building a Real ETL Pipeline
Let me show you the pipeline pattern I’ve settled on after building several of these. It combines Polars for transformations and DuckDB for complex joins and aggregations.
import
polars
as
pl
import
duckdb
from
pathlib
import
Path
def
extract
(source_dir: Path)
->
dict[str, pl
.
LazyFrame]:
"""Scan all source files lazily."""
return
{
"transactions"
: pl
.
scan_parquet(source_dir
/
"transactions/*.parquet"
),
"customers"
: pl
.
scan_parquet(source_dir
/
"customers.parquet"
),
"products"
: pl
.
scan_parquet(source_dir
/
"products.parquet"
),
}
def
transform
(sources: dict[str, pl
.
LazyFrame])
->
pl
.
DataFrame:
"""Transform and join data."""
# Clean transactions with Polars
clean_txn
=
(
sources[
"transactions"
]
.
filter(pl
.
col(
"amount"
)
>
0
)
.
with_columns([
pl
.
col(
"timestamp"
)
.
cast(pl
.
Date)
.
alias(
"date"
),
(pl
.
col(
"amount"
)
*
pl
.
col(
"quantity"
))
.
alias(
"total"
),
])
.
collect()
)
customers
=
sources[
"customers"
]
.
collect()
products
=
sources[
"products"
]
.
collect()
# Complex join and aggregation with DuckDB
return
duckdb
.
sql(
"""
SELECT
c.segment,
p.category,
DATE_TRUNC('week', t.date) AS week,
SUM(t.total) AS revenue,
COUNT(DISTINCT t.customer_id) AS unique_customers,
AVG(t.total) AS avg_order_value
FROM clean_txn t
JOIN customers c ON t.customer_id = c.customer_id
JOIN products p ON t.product_id = p.product_id
GROUP BY c.segment, p.category, week
ORDER BY week, revenue DESC
"""
)
.
pl()
def
load
(df: pl
.
DataFrame, output_path: Path)
->
None
:
"""Write results partitioned by segment."""
for
segment
in
df[
"segment"
]
.
unique():
segment_df
=
df
.
filter(pl
.
col(
"segment"
)
==
segment)
out
=
output_path
/
f
"segment=
{
segment
}
"
out
.
mkdir(parents
=
True
, exist_ok
=
True
)
segment_df
.
write_parquet(out
/
"data.parquet"
)
# Run the pipeline
sources
=
extract(Path(
"data/raw"
))
result
=
transform(sources)
load(result, Path(
"data/processed"
))
This pattern is clean, testable, and fast. Each function has a single responsibility. The extract phase is lazy so we don’t load data we don’t need. The transform phase uses the right tool for each job. The load phase handles partitioning.
Compare that to the pandas version I replaced — it was 400 lines of code doing the same thing, peppered with
.copy()
calls to avoid the dreaded
SettingWithCopyWarning
, and it still leaked memory like a sieve.
Performance: The Numbers Don’t Lie
I’ve benchmarked these tools extensively and the results are consistent. Here’s what I see on a typical 10 million row dataset with mixed types on a 16-core machine:
Reading a 2GB Parquet file: pandas takes about 8 seconds, Polars takes 1.2 seconds, DuckDB takes 0.9 seconds. That’s before you do anything with the data.
A group-by aggregation across three columns: pandas clocks in around 4 seconds, Polars does it in 0.3 seconds, DuckDB in 0.25 seconds. That’s a 15x difference on a dataset that isn’t even that big. Scale up to hundreds of millions of rows and the gap widens further because pandas starts thrashing memory.
Joins are where pandas really falls apart. A many-to-many join on two 10 million row DataFrames: pandas takes 45 seconds and uses 12GB of RAM. Polars does it in 3 seconds using 4GB. DuckDB finishes in 2.5 seconds using even less because it streams the join.
The memory story matters just as much as speed. I’ve run Polars pipelines on datasets that would crash pandas with an
OutOfMemoryError
. Polars’ streaming mode can process data larger than RAM by breaking it into chunks automatically:
result
=
(
pl
.
scan_parquet(
"huge_dataset/*.parquet"
)
.
filter(pl
.
col(
"status"
)
==
"active"
)
.
group_by(
"region"
)
.
agg(pl
.
col(
"revenue"
)
.
sum())
.
collect(streaming
=
True
)
)
That
streaming=True
flag is all it takes. No chunking logic, no manual memory management. If you’ve ever written a
for chunk in pd.read_csv(path, chunksize=10000)
loop, you know how painful the pandas alternative is.
I wrote about general
Python performance optimization
before, and profiling is still important. But switching to Polars is the single biggest performance win I’ve ever gotten from a library swap.
Patterns I Keep Coming Back To
After building a dozen or so pipelines with these tools, a few patterns have become second nature.
Lazy all the way down.
Start with
scan_parquet()
or
scan_csv()
and stay lazy as long as possible. Every time you call
.collect()
you’re telling Polars “stop optimizing, just run it.” I try to have exactly one
.collect()
call per logical pipeline stage.
DuckDB for joins, Polars for transforms.
This isn’t a hard rule, but I find DuckDB’s SQL more readable for multi-table joins with conditions, and Polars’ expression API more natural for column-level transformations. The zero-copy interop means there’s no penalty for mixing them.
Schema validation up front.
Polars is strict about types, which is actually a feature. I validate schemas at the extract stage so I catch data quality issues before they cascade:
expected_schema
=
{
"customer_id"
: pl
.
Int64,
"amount"
: pl
.
Float64,
"timestamp"
: pl
.
Datetime,
}
df
=
pl
.
scan_parquet(
"data.parquet"
)
for
col, dtype
in
expected_schema
.
items():
assert
col
in
df
.
columns,
f
"Missing column:
{
col
}
"
assert
df
.
schema[col]
==
dtype,
f
"Wrong type for
{
col
}
"
Sink to Parquet for intermediate results.
If your pipeline has multiple stages, write intermediate results to Parquet rather than holding everything in memory. Polars and DuckDB both read Parquet incredibly fast, so the I/O overhead is minimal:
# Stage 1: clean and write
(
pl
.
scan_parquet(
"raw/*.parquet"
)
.
filter(pl
.
col(
"amount"
)
>
0
)
.
sink_parquet(
"intermediate/cleaned.parquet"
)
)
# Stage 2: aggregate from intermediate
result
=
(
pl
.
scan_parquet(
"intermediate/cleaned.parquet"
)
.
group_by(
"customer_id"
)
.
agg(pl
.
col(
"amount"
)
.
sum())
.
collect()
)
If you’re working with
async Python patterns
, you can even run multiple pipeline stages concurrently when they don’t depend on each other. I’ve used
asyncio.gather()
to kick off independent extract jobs in parallel before joining the results.
Migrating From Pandas Without Losing Your Mind
I won’t sugarcoat it — migrating existing pandas code takes effort. The APIs are similar enough to be dangerous. You’ll reach for
.iloc
and it won’t be there. You’ll try
.apply()
and Polars will yell at you (rightfully so — if you’re using
.apply()
you’re doing it wrong in both libraries).
Here’s my migration cheat sheet for the operations that trip people up:
# Pandas: df['new_col'] = df['a'] + df['b']
# Polars:
df
=
df
.
with_columns((pl
.
col(
"a"
)
+
pl
.
col(
"b"
))
.
alias(
"new_col"
))
# Pandas: df[df['amount'] > 100]
# Polars:
df
=
df
.
filter(pl
.
col(
"amount"
)
>
100
)
# Pandas: df.groupby('cat').agg({'amount': ['sum', 'mean']})
# Polars:
df
=
df
.
group_by(
"cat"
)
.
agg(
pl
.
col(
"amount"
)
.
sum()
.
alias(
"total"
),
pl
.
col(
"amount"
)
.
mean()
.
alias(
"avg"
),
)
# Pandas: df.merge(other, on='id', how='left')
# Polars:
df
=
df
.
join(other, on
=
"id"
, how
=
"left"
)
# Pandas: df.fillna(0)
# Polars:
df
=
df
.
fill_null(
0
)
The biggest gotcha is that Polars DataFrames are immutable. Every operation returns a new DataFrame. There’s no
inplace=True
parameter, and that’s by design — it makes the code easier to reason about and enables the query optimizer to work its magic.
The other thing that’ll bite you is null handling. Pandas uses
NaN
for missing floats and
None
for missing objects, which leads to all sorts of type coercion nightmares. Polars uses
null
consistently across all types. It’s cleaner, but your null-checking code will need updating.
My advice: don’t try to migrate everything at once. Pick your slowest pipeline, rewrite it in Polars, and measure the difference. Once you see a 10x speedup on real data, the motivation to migrate everything else takes care of itself.
If you’re coming from a
data science background
, the transition is especially worthwhile. Most of the exploratory analysis patterns you know from pandas have direct Polars equivalents, and the speed means you spend less time waiting and more time iterating on your analysis.
When to Use What
I get asked this a lot, so here’s my decision framework.
Use
Polars
when you’re doing DataFrame-style transformations — filtering, selecting, creating columns, reshaping data. Its expression API is the most powerful I’ve used in any language. Use it when you want lazy evaluation and automatic parallelism. Use it when your pipeline is primarily Python and you want everything in one ecosystem.
Use
DuckDB
when SQL is the natural way to express your query. Multi-table joins with complex conditions, window functions, CTEs, recursive queries — DuckDB handles all of these elegantly. Use it when you want to query files directly without loading them into memory first. Use it when your team already thinks in SQL.
Use
both
when you’re building production pipelines. I almost always do. DuckDB for the heavy analytical queries, Polars for the transformation and I/O layer. They pass data between each other through Arrow with zero overhead.
Don’t use either for
streaming data
— they’re batch-oriented tools. For real-time pipelines, look at Kafka, Flink, or even
Python’s async capabilities
for lighter workloads.
And don’t use either as a
database replacement
. If you need ACID transactions, concurrent writes, or persistent storage with access control, use a proper database. DuckDB is embedded and single-process — it’s an analytical engine, not a database server.
The Ecosystem Is Moving Fast
The Python data ecosystem is in the middle of a generational shift. Arrow has become the lingua franca for columnar data. Polars adoption is accelerating — I see it in more job postings every month. DuckDB just hit 1.0 and the community is exploding.
Libraries are catching up too. Scikit-learn can now accept Polars DataFrames. Plotly and Altair work with them. If you’re building
ML pipelines
, you can go from raw data to trained model without touching pandas at all.
The tooling around
Python’s advanced features
like type hints and protocols also plays nicely with Polars. Its API is well-typed, so your IDE gives you proper autocomplete and your type checker catches errors before runtime. Try getting that with pandas.
Where I’ve Landed
That 45-minute pipeline I mentioned at the start? It’s been running in production for eight months now. Ninety seconds, every day, without a single failure. It uses less than 4GB of RAM on a machine that used to need 32GB for the pandas version. I actually downsized the instance and saved money.
I’m not saying pandas is useless. It has the largest ecosystem, the most Stack Overflow answers, and it’s what most tutorials teach. If you’re doing quick exploratory analysis on small datasets, pandas is fine.
But for anything that matters — production pipelines, large datasets, performance-sensitive work — Polars and DuckDB are the answer. The learning curve is a weekend. The performance gains last forever.
Stop waiting for pandas to get faster. It won’t. The architecture doesn’t allow it. Polars and DuckDB were built from scratch with modern hardware in mind, and it shows in every benchmark and every pipeline I’ve built with them.
Make the switch. You’ll wonder why you didn’t do it sooner.
Andrew Odendaal
Writing about cloud architecture, DevOps, distributed systems, and software development since 2007.
About this site →
Related Articles
Python Performance Optimization: Profiling and Tuning Guide
Mar 2026
Python Async Programming: asyncio, Tasks, and Real-World Patterns
Jan 2026
Rust Async Runtime Deep Dive: Tokio Architecture
May 2026
Rust WebAssembly: Building High-Performance Web Applications
Apr 2026
AWS Aurora Serverless v2: Architecture and Performance Guide
Apr 2026
Python Packaging in 2026: uv, Poetry, and the Modern Ecosystem
Apr 2026
Go Concurrency Patterns for Microservices
Feb 2026
Python Type Hints and Static Analysis in Production Codebases
Feb 2026
☰
↑