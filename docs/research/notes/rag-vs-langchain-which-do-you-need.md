---
title: 'RAG vs LangChain: Which Do You Need?'
id: rag-vs-langchain-which-do-you-need
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:20.163369Z'
source: https://krunalkanojiya.com/blog/rag-vs-langchain
source_domain: krunalkanojiya.com
fetched_at: '2026-09-15T02:28:20.161358Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

RAG vs LangChain: Which Do You Need?
On this page
Every few months a new developer joins an AI engineering channel and asks some version of the same question: "Should I use RAG or LangChain for my chatbot?"
The question is understandable. Both terms appear constantly in the same tutorials, the same GitHub repos, and the same job descriptions. They are treated as alternatives when they are not. One is a retrieval technique. The other is a framework. Comparing them directly is like asking whether you should use SQL or PostgreSQL for your database.
The question developers are actually asking is different: "Do I need LangChain to build a RAG system? Is it required, or is it optional overhead?" That question has a real answer. This article gives it.
What RAG Is
RAG stands for Retrieval-Augmented Generation. It is an architectural pattern, not a product or a library. The pattern has three steps: index your documents into a vector database, retrieve the most relevant chunks at query time, and pass those chunks as context to an LLM that generates a grounded answer.
The original RAG paper came from researchers at Meta AI, University College London, and New York University in 2020. By 2026,
RAG has become the standard architecture for enterprise AI applications that need to answer questions from private or current data
. It is a technique you implement. It is not a piece of software you install.
You can implement RAG in plain Python, in LangChain, in LlamaIndex, in Haystack, in DSPy, or in any other stack that can call an embedding API, write to a vector database, and call an LLM. None of those choices is RAG itself. They are tools you use to build it.
What LangChain Is
LangChain is a Python and JavaScript framework for building LLM-powered applications.
It provides standardized interfaces for connecting LLMs to external data sources, tools, and APIs.
It reached v1.0 stable in October 2025, and as of early 2026 it has over 126,000 GitHub stars and 500-plus integrations covering LLM providers, vector databases, document loaders, and API tools.
LangChain's core building blocks are chains (sequences of operations), prompt templates, document loaders, vector store wrappers, and LLM provider wrappers. Its extended ecosystem includes LangGraph for stateful multi-agent workflows and LangSmith for observability, tracing, and evaluation.
LangChain was built to address the need for structured, modular approaches to LLM applications. As AI applications grew in complexity, the need for a tool that could integrate different language models and manage their interactions became evident.
LangChain implements RAG. It does not define it.
Where They Actually Intersect
The reason people confuse the two is that LangChain is one of the most common ways to implement RAG, and most RAG tutorials written between 2022 and 2024 used LangChain as the default implementation layer. That tutorial dominance created the impression that the two are equivalent.
They are not equivalent. The relationship is this:
plaintext
Copy
RAG (technique)
|
v
Needs: embedding model + vector database + LLM
Implementation options:
+------------------+-------------------+------------------+
| LangChain        | LlamaIndex        | Plain Python     |
| (orchestration   | (retrieval-first  | (no abstraction  |
|  framework)      |  framework)       |  layer)          |
+------------------+-------------------+------------------+
| Haystack         | DSPy              | Custom stack     |
| (production-     | (signature-       | (full control,   |
|  ready pipeline) |  first)           |  full ownership) |
+------------------+-------------------+------------------+
All of these build RAG. None of them is RAG.
The real decision is not RAG versus LangChain. It is which implementation approach fits your use case, your team, and your production requirements.
The Case for LangChain
LangChain earns its overhead in specific situations.
Multi-step agent workflows.
When a RAG system needs to do more than retrieve-and-generate - when it needs to decompose questions, route to different tools, evaluate intermediate results, and loop back for additional retrieval - LangGraph's graph-based execution model handles that complexity cleanly.
According to Databricks' State of AI Agents report, multi-agent workflows grew by 327% between June and October 2025
, which is the use case LangChain's ecosystem is most directly designed for.
Rapid integration with a large ecosystem.
LangChain has wrappers for over 500 integrations. If your pipeline needs to talk to Notion, Confluence, Salesforce, Slack, and four different vector databases, the integration work is largely done.
LangChain works with major LLM providers - OpenAI, Anthropic, Azure - vector databases including Pinecone, Weaviate, and Milvus, and document loaders for CSV, PDFs, websites, and Notion.
Writing those wrappers from scratch is real engineering time.
Observability with LangSmith.
LangSmith provides request-level tracing on every LLM call, retrieval step, and tool invocation. It shows what prompts were sent, what the LLM returned, how long each step took, and the token cost of each call.
The free tier includes 5,000 traces. The Plus plan is $39 per month per seat.
For teams that need this level of pipeline visibility, LangSmith with LangChain is faster to set up than integrating a third-party tracer with a custom stack.
Team already in the LangChain ecosystem.
If your team has existing LangChain code, LangChain skills, and LangSmith dashboards, the switching cost of moving to plain Python or LlamaIndex for a new project is real. Ecosystem consistency has value.
Here is a LangChain LCEL chain implementing a basic RAG pipeline:
python
Copy
from
langchain_openai
import
ChatOpenAI, OpenAIEmbeddings
from
langchain_community.vectorstores
import
Qdrant
from
langchain_core.prompts
import
ChatPromptTemplate
from
langchain_core.runnables
import
RunnablePassthrough
from
langchain_core.output_parsers
import
StrOutputParser
from
qdrant_client
import
QdrantClient
# Setup
embeddings
=
OpenAIEmbeddings
(
model
=
"text-embedding-3-small"
)
llm
=
ChatOpenAI
(
model
=
"gpt-4o"
,
temperature
=
0
)
# Connect to vector store
qdrant_client
=
QdrantClient
(
url
=
"http://localhost:6333"
)
vectorstore
=
Qdrant
(
client
=
qdrant_client,
collection_name
=
"company_docs"
,
embeddings
=
embeddings
)
retriever
=
vectorstore.
as_retriever
(
search_kwargs
=
{
"k"
:
5
})
# Prompt template
prompt
=
ChatPromptTemplate.
from_template
(
"""
Answer the question using only the context below.
If the context does not contain the answer, say so clearly.
Context:
{context}
Question:
{question}
"""
)
# LCEL chain: composable, streaming-friendly
def
format_docs
(
docs
):
return
"
\n\n
"
.
join
(doc.page_content
for
doc
in
docs)
rag_chain
=
(
{
"context"
: retriever
|
format_docs,
"question"
:
RunnablePassthrough
()}
|
prompt
|
llm
|
StrOutputParser
()
)
# Invoke
answer
=
rag_chain.
invoke
(
"What is the refund policy for enterprise customers?"
)
print
(answer)
LCEL chains are more composable and streaming-friendly than earlier LangChain patterns, with production deployments showing 15 to 25% better performance in complex orchestration scenarios compared to the legacy RetrievalQA chain.
The Case Against LangChain for Simple RAG
LangChain has accumulated a real criticism in the developer community since 2024: for simple retrieval pipelines, it is over-engineered.
For many teams, plain Python combined with direct OpenAI or Anthropic APIs, a vector database, and lightweight retrieval logic is faster to build, easier to debug, and simpler to maintain.
When an API call fails in plain Python, the traceback points exactly to the line that failed. When it fails inside a LangChain abstraction, you are debugging through multiple layers of wrappers to find the actual API call that produced the error.
In 2025 and 2026 discussions, many developers note LangChain can feel bloated for simple RAG. Some prefer lighter alternatives like LlamaIndex or plain Python combined with the OpenAI SDK.
Here is the same basic RAG pipeline without LangChain:
python
Copy
import
openai
from
qdrant_client
import
QdrantClient
from
qdrant_client.models
import
Filter
# Direct API clients - no framework abstraction
oai
=
openai.
OpenAI
(
api_key
=
"your-openai-api-key"
)
qdrant
=
QdrantClient
(
url
=
"http://localhost:6333"
)
SYSTEM_PROMPT
=
"""Answer the question using only the context provided.
If the context does not contain the answer, say so clearly."""
def
embed
(
text
:
str
) -> list[
float
]:
response
=
oai.embeddings.
create
(
model
=
"text-embedding-3-small"
,
input
=
text
)
return
response.data[
0
].embedding
def
retrieve
(
query
:
str
,
top_k
:
int
=
5
) -> list[
str
]:
query_vector
=
embed
(query)
results
=
qdrant.
search
(
collection_name
=
"company_docs"
,
query_vector
=
query_vector,
limit
=
top_k,
with_payload
=
True
)
return
[hit.payload[
"text"
]
for
hit
in
results]
def
generate
(
query
:
str
,
context_chunks
: list[
str
]) ->
str
:
context
=
"
\n\n
"
.
join
(context_chunks)
response
=
oai.chat.completions.
create
(
model
=
"gpt-4o"
,
messages
=
[
{
"role"
:
"system"
,
"content"
:
SYSTEM_PROMPT
},
{
"role"
:
"user"
,
"content"
:
f
"Context:
\n
{
context
}
\n\n
Question:
{
query
}
"
}
]
)
return
response.choices[
0
].message.content
def
rag
(
query
:
str
) ->
str
:
chunks
=
retrieve
(query)
return
generate
(query, chunks)
print
(
rag
(
"What is the refund policy for enterprise customers?"
))
Both examples do the same thing. The plain Python version is easier to read, easier to test, and produces cleaner error messages. The LangChain version becomes more valuable as the pipeline grows in complexity - when streaming, chaining multiple steps, or adding agent behavior.
LangChain vs LlamaIndex for RAG
When developers move past plain Python and reach for a framework, the real comparison is LangChain versus LlamaIndex - because LlamaIndex is purpose-built for retrieval tasks.
LlamaIndex is purpose-built for RAG: hierarchical chunking, auto-merging retrieval, and sub-question decomposition produce better results with less tuning than LangChain's component-based approach.
In a direct code comparison,
LlamaIndex requires 30 to 40% less code for equivalent RAG pipelines
because its abstractions are designed specifically around the retrieval use case rather than general LLM orchestration.
The performance numbers from a
standardized benchmark across 100 queries using identical models - GPT-4.1-mini, BGE-small embeddings, Qdrant retriever
- are:
Framework
Avg Framework Overhead
Avg Token Usage
Best For
DSPy
3.53ms
~2.03K
Minimal boilerplate, contract-driven
Haystack
5.9ms
~1.57K
Production-ready, testable pipelines
LlamaIndex
6ms
~1.60K
Retrieval-heavy RAG, fast iteration
LangChain
10ms
~2.40K
Rapid prototyping, broad integrations
LangGraph
14ms
~2.03K
Multi-agent stateful workflows
Source:
AIMutiple RAG framework benchmark, January 2026
LangChain's higher token overhead comes from how it serializes prompts and message formatting internally.
Each framework wraps the same logical content with slightly different formatting before sending it to the LLM, creating small but consistent token deltas.
At low query volumes these deltas are irrelevant. At 100 or more concurrent users, a 0.8K token overhead per query compounds into meaningful cost differences.
LlamaIndex has a cleaner version history with fewer breaking changes. LangGraph went through significant breaking changes between versions 0.1 and 0.3 before stabilizing at 1.0 in October 2025.
Teams that built on LangGraph in 2024 frequently had to rewrite orchestration code during upgrades. LlamaIndex's more conservative release cadence means less unplanned maintenance.
The ecosystem trade-off runs the other way. LangChain's 500-plus integrations versus LlamaIndex's 300-plus data connectors. For teams building pipelines that span many third-party services, LangChain's breadth is a real advantage.
The Agentic RAG Case for LangGraph
The comparison changes when the RAG system needs to do more than retrieve-and-generate.
Agentic RAG - where an LLM orchestrates multiple retrieval steps, evaluates whether retrieved context is sufficient, and loops back for additional retrieval when it is not - does not fit naturally into a linear chain. It requires a decision-making loop with conditional transitions between nodes.
LangGraph provides a graph-based framework for agent orchestration with explicit state management, conditional logic, and human-in-the-loop workflows.
Each node in the graph is an operation - a retrieval call, an LLM call, a tool invocation, a grading step. Edges define the transitions between nodes, including conditional branches that route to different nodes based on intermediate results.
python
Copy
from
langgraph.graph
import
StateGraph,
END
from
typing
import
TypedDict, Annotated
import
operator
class
AgentState
(
TypedDict
):
query:
str
retrieved_docs: list[
str
]
doc_grade:
str
# "relevant" or "not_relevant"
answer:
str
def
retrieve_node
(
state
: AgentState) -> AgentState:
"""Retrieve chunks from vector database."""
chunks
=
retrieve
(state[
"query"
])
# your retrieval function
return
{
"retrieved_docs"
: chunks}
def
grade_docs_node
(
state
: AgentState) -> AgentState:
"""Ask LLM to grade whether retrieved docs are relevant."""
docs_text
=
"
\n
"
.
join
(state[
"retrieved_docs"
])
grade
=
oai.chat.completions.
create
(
model
=
"gpt-4o-mini"
,
messages
=
[{
"role"
:
"user"
,
"content"
: (
f
"Are these documents relevant to the question: '
{
state[
'query'
]
}
'?
\n\n
"
f
"Documents:
\n
{
docs_text
}
\n\n
"
"Reply with only 'relevant' or 'not_relevant'."
)
}]
).choices[
0
].message.content.
strip
().
lower
()
return
{
"doc_grade"
: grade}
def
generate_node
(
state
: AgentState) -> AgentState:
"""Generate answer from retrieved context."""
answer
=
generate
(state[
"query"
], state[
"retrieved_docs"
])
return
{
"answer"
: answer}
def
web_fallback_node
(
state
: AgentState) -> AgentState:
"""Web search fallback when retrieval is not relevant."""
# Your web search implementation here
return
{
"retrieved_docs"
: [
"[web search results]"
],
"doc_grade"
:
"relevant"
}
def
should_generate
(
state
: AgentState) ->
str
:
"""Route based on document relevance grade."""
return
"generate"
if
state[
"doc_grade"
]
==
"relevant"
else
"web_fallback"
# Build the graph
workflow
=
StateGraph
(AgentState)
workflow.
add_node
(
"retrieve"
, retrieve_node)
workflow.
add_node
(
"grade_docs"
, grade_docs_node)
workflow.
add_node
(
"generate"
, generate_node)
workflow.
add_node
(
"web_fallback"
, web_fallback_node)
workflow.
set_entry_point
(
"retrieve"
)
workflow.
add_edge
(
"retrieve"
,
"grade_docs"
)
workflow.
add_conditional_edges
(
"grade_docs"
,
should_generate,
{
"generate"
:
"generate"
,
"web_fallback"
:
"web_fallback"
}
)
workflow.
add_edge
(
"web_fallback"
,
"generate"
)
workflow.
add_edge
(
"generate"
,
END
)
app
=
workflow.
compile
()
result
=
app.
invoke
({
"query"
:
"What is our refund policy for enterprise customers?"
})
print
(result[
"answer"
])
Analysis of LangSmith production traces from 150 enterprises in Q4 2025 shows agentic approaches improve complex query handling by 35 to 50% but increase latency by 200 to 400ms compared to simple one-pass retrieval.
That trade-off makes sense for complex multi-hop questions and high-stakes domains. It does not make sense for single-fact lookups from a well-indexed knowledge base.
LangGraph went through significant breaking changes between versions 0.1 and 0.3. If you are starting a new project on LangGraph in 2026, start directly on v1.0 and use the current documentation at docs.langchain.com/langgraph rather than tutorials written before October 2025. The API changed substantially and older code examples will not work without modification.
Head-to-Head Comparison
Dimension
RAG (technique)
LangChain
LlamaIndex
Plain Python
What it is
Retrieval pattern
Orchestration framework
Retrieval framework
No framework
GitHub stars
N/A
126K+
44K+
N/A
Framework overhead
N/A
~10ms
~6ms
~0ms
Token overhead
N/A
~2.4K
~1.6K
~0 (your prompt only)
Code volume for basic RAG
N/A
Medium
Low
Low
Multi-agent support
Pattern, not tool
LangGraph (strong)
LlamaIndex Workflows
Build yourself
Observability
RAGAS (external)
LangSmith (native)
Third-party
Third-party
Breaking changes history
N/A
Frequent (pre-v1.0)
More stable
N/A
Best for
All RAG use cases
Complex agents, broad integrations
Retrieval-heavy pipelines
Simple pipelines, full control
The Decision Framework
Work through these questions in order before choosing an implementation approach.
Is the pipeline a simple linear retrieve-then-generate loop with no branching?
If yes, start with plain Python. It is easier to debug, has no abstraction overhead, and produces cleaner production code. Add a framework when the pipeline grows complex enough to need one. For how the basic loop works, see
What Is RAG in AI
.
Does the pipeline need multi-step agent behavior - routing, loops, document grading, conditional retrieval?
If yes, LangGraph is the right orchestration layer. The graph-based execution model handles conditional transitions cleanly. Use LlamaIndex for the retrieval components inside those nodes if retrieval quality is a priority.
Is retrieval quality the primary concern, and does the knowledge base require advanced indexing - hierarchical chunking, auto-merging retrieval, sub-question decomposition?
If yes, LlamaIndex is the stronger choice for the retrieval layer. Its purpose-built retrieval abstractions require less tuning and less code than LangChain's more general component-based approach. For details on what makes retrieval quality fail, see
Why RAG Fails
.
Does the team need built-in observability without integrating a third-party tracer?
If yes, LangSmith inside the LangChain ecosystem is the fastest path. It provides full trace visibility with minimal setup. Third-party options like Arize Phoenix and Langfuse work with any stack but require more integration work.
Does the pipeline need 500-plus integrations with third-party services across many providers?
If yes, LangChain's integration breadth is a genuine advantage. Writing those wrappers yourself is real work that LangChain has already done.
plaintext
Copy
START
|
v
Is this a simple single-step retrieve + generate pipeline?
|-- Yes --> Plain Python. No framework needed.
|-- No  --> Continue.
|
v
Does it need multi-step agent behavior with loops and routing?
|-- Yes --> LangGraph for orchestration.
|           Use LlamaIndex for retrieval inside nodes.
|-- No  --> Continue.
|
v
Is retrieval quality and iteration speed the priority?
|-- Yes --> LlamaIndex. Less code, better retrieval abstractions.
|-- No  --> Continue.
|
v
Does the team need LangSmith observability natively,
or broad third-party integrations out of the box?
|-- Yes --> LangChain / LangGraph.
|-- No  --> Plain Python or LlamaIndex with third-party tracing.
What Production Stacks Look Like in 2026
The most capable production RAG stacks in 2026 do not pick one framework and use it for everything. They compose the right tool for each layer.
Many production teams use LlamaIndex as the retrieval layer and LangGraph as the orchestration layer together.
LlamaIndex handles document loading, chunking, indexing, and retrieval with its purpose-built abstractions. LangGraph handles the agent loop that decides when to retrieve, which retrieval tool to call, how to evaluate retrieved context, and when to return an answer.
For teams that do not need agent orchestration, a common 2026 stack is LlamaIndex for retrieval plus direct OpenAI or Anthropic API calls for generation, with Arize Phoenix or Langfuse for tracing. No LangChain required.
According to G2 reviews of LangChain, its modular architecture is well-regarded for flexible workflow composition and its extensive integration ecosystem. Common criticisms include documentation that is overloaded with new releases and leaves users confused, a steep learning curve for chains and agents, and latency and maintainability issues at production scale.
These are real trade-offs, not edge cases. Teams that evaluate LangChain against their production requirements regularly conclude it is the right tool. Teams that adopt it reflexively because it is the most-discussed framework sometimes spend significant time debugging abstractions on pipelines that plain Python would have served better.
Addressing the Actual Confusion
The reason people search "RAG vs LangChain" is that most learning resources treat LangChain as the default implementation layer for RAG. Tutorial after tutorial teaches RAG using LangChain code, creating the impression that the two are inseparable.
They are not.
LangChain is one way to build RAG. For simple retrieval pipelines, it is arguably the wrong way.
For complex agentic workflows, it is one of the best available tools. The right question is not "RAG or LangChain?" It is "What does my RAG pipeline actually need, and which implementation approach serves that without unnecessary overhead?"
For most teams starting their first RAG system: build it in plain Python first. Understand the retrieve-then-generate loop directly. Add a framework when the plain Python version has a clear gap that the framework fills. Do not add abstraction speculatively.
For the underlying concepts that apply regardless of which implementation you choose - how the retrieval works, how the vector database stores and indexes embeddings, how chunking affects retrieval quality - the RAG series on this site covers each component in depth. Start with
What Is RAG in AI
for the full picture. If you are evaluating frameworks specifically to build production pipelines,
RAG Architecture Explained
covers the pipeline components that matter most before any framework choice. And if a system you already built is not performing well,
Why RAG Fails
covers the retrieval failure modes that no framework protects you from automatically.
Related Reading
What is RAG in AI? A simple explanation with examples
Sources
github.com
squirro.com
It provides standardized interfaces for connecting LLMs to external data sources, tools, and APIs.
medium.com
According to Databricks' State of AI Agents report, multi-agent workflows grew by 327% between June and October 2025
meilisearch.com
The free tier includes 5,000 traces. The Plus plan is $39 per month per seat.
medium.com
Frequently Asked Questions
Is RAG the same as LangChain?
+
No. RAG and LangChain are different categories of thing. RAG - Retrieval-Augmented Generation - is a technique for grounding LLM answers in retrieved documents. LangChain is a Python and JavaScript framework for building applications that use LLMs. LangChain is one tool you can use to implement RAG. You can also build RAG with plain Python, LlamaIndex, Haystack, or any other approach. RAG does not require LangChain, and LangChain does more than just RAG.
Do I need LangChain to build a RAG system?
+
No. A working RAG system requires an embedding model, a vector database, and an LLM. None of those require LangChain. For simple pipelines - index documents, retrieve chunks, generate an answer - plain Python with the OpenAI SDK and Qdrant or Chroma is faster to build, easier to debug, and simpler to maintain. LangChain earns its overhead when you need multi-step agent workflows, composable chains across multiple tools, or tight integration with LangSmith for observability.
What is LangChain actually used for?
+
LangChain is an orchestration framework for LLM applications. It provides standardized wrappers for LLM providers, document loaders, vector store integrations, prompt templates, and chain composition. In practice, it is used for RAG pipelines, conversational agents, tool-calling workflows, and any application that combines LLMs with external data sources or APIs. LangGraph, built on top of LangChain, handles stateful multi-agent workflows with graph-based execution.
What is the performance overhead of using LangChain for RAG?
+
In a standardized benchmark across 100 queries using identical models and retrievers, LangChain introduced approximately 10ms of framework orchestration overhead per query, compared to 6ms for LlamaIndex, 5.9ms for Haystack, and 3.5ms for DSPy. LangChain also consumed roughly 2.4K tokens per query versus LlamaIndex's 1.6K and Haystack's 1.57K. These differences are negligible at low query volumes but compound meaningfully at 100 or more concurrent users.
What is LangGraph and how does it relate to RAG?
+
LangGraph is an extension of LangChain that provides a graph-based execution model for multi-agent workflows. Instead of a linear chain, LangGraph defines nodes (LLM calls, retrievals, tool uses) and edges (transitions between nodes) with explicit state management, conditional logic, and loop support. For agentic RAG - where an LLM orchestrates multiple retrieval steps, evaluates retrieved context, and decides whether to fetch more information - LangGraph is the standard implementation layer in the LangChain ecosystem.
LangChain vs LlamaIndex: which is better for RAG?
+
It depends on what you are optimizing for. LlamaIndex is purpose-built for retrieval and produces better retrieval quality with less code for equivalent RAG pipelines, with roughly 30 to 40% less code and 6ms versus 14ms framework overhead for LangGraph-based workflows. LangChain is stronger for complex multi-step agent workflows and has a larger integration ecosystem. Many production teams in 2026 use LlamaIndex as the retrieval layer and LangGraph as the orchestration layer together.
When should I use plain Python instead of LangChain for RAG?
+
When your pipeline is a single retrieve-then-generate loop with no branching, no multi-step reasoning, and no agent behavior. Plain Python with the OpenAI SDK and a vector database client is faster to prototype, produces cleaner tracebacks on failure, and has no abstraction layer hiding what the code actually does. The threshold most experienced developers use: if the pipeline fits in under 100 lines of Python with direct API calls, it does not need LangChain.
Follow on Google
Add as a preferred source in Search & Discover
Add as preferred source
Appears in Google Discover
Krunal Kanojiya
Technical Content Writer
Krunal is a technical content writer at Lucent Innovation and a former full-stack developer with professional technology experience since 2021. He publishes source-backed, practical guides on AI engineering, RAG, vector search, data engineering, algorithms, and software development.
Experience & credentials
Editorial standards
GitHub
LinkedIn
X
Related Posts
RAG vs Traditional Search: What Changed, What Did Not, and Why BM25 Is Not Dead
May 08, 2026
·
11 min read
How to Build a RAG Application with LangChain and Pinecone
Jul 01, 2026
·
13 min read
How to Choose Chunk Size for RAG: A Practical Guide
Jul 16, 2026
·
16 min read