---
title: 'AI evaluation frameworks: RAGAS, DeepEval, and PromptFoo compared (2026) |
  Knovo'
id: ai-evaluation-frameworks-ragas-deepeval-and-promptfoo-compared-2026-knovo
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:28.225300Z'
source: https://www.knovo.dev/guides/ai-evaluation-frameworks
source_domain: www.knovo.dev
fetched_at: '2026-09-15T02:28:28.223301Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

AI evaluation frameworks: RAGAS, DeepEval, and PromptFoo compared (2026) | Knovo
Shipping an LLM feature is often easier than proving it works.
That sounds backward until you run a real system in production. A prompt can look good in a notebook and still fail on messy user inputs, weak retrieval, stale context, long conversations, or model updates. Traditional software testing catches deterministic logic bugs. It does not tell you whether a RAG system retrieved the right evidence, whether an answer stayed faithful to that evidence, or whether a prompt change quietly made the system worse.
That is why evaluation is the hardest part of production AI. The hard problem is not generating one good answer. The hard problem is creating a repeatable process that tells you whether the system is getting better, getting worse, or drifting in ways humans will only notice after damage is done.
Why eval is the hardest part of production AI
AI systems fail in ways that are subtle, probabilistic, and user-facing.
In ordinary software, a function either returns the wrong value or it does not. With LLMs, many outputs sit in an uncomfortable middle zone:
syntactically valid but semantically weak
plausible but ungrounded
partially correct but operationally useless
great on one prompt set and poor on another
That makes evaluation hard because you are not only testing correctness. You are testing usefulness, reliability, and failure modes under ambiguity.
A second challenge is that most AI systems are multi-stage. A RAG app can fail because chunking is poor, retrieval is weak, the model ignores the retrieved evidence, the answer format drifts, or the whole pipeline optimizes the wrong thing. If you only look at final output quality, you miss where the failure entered the system.
The third challenge is cost. Evals are not free. Many frameworks use models as judges, which means every evaluation run can itself create latency and spend. This pushes teams toward weak manual spot checks unless they design the eval loop intentionally.
What makes LLM eval different from normal software testing
LLM evaluation still includes some ordinary software testing. You should absolutely test parsers, routing logic, prompt templates, and API failure handling with normal unit and integration tests. But those tests are not enough.
What makes LLM eval different is that the core behavior is non-deterministic and quality-based rather than purely rules-based.
Three differences matter most.
You rarely have one exact gold answer. A summary, explanation, or support reply can be acceptable in multiple forms.
Retrieval and generation interact. A weak answer may be caused by bad context rather than bad generation.
Human judgment still matters. Even strong automated metrics can disagree with what real users or reviewers think is useful.
This is why evaluation in AI usually needs a layered stack:
deterministic tests for code behavior
automated metrics for model behavior
human review for ambiguous or high-stakes cases
If you collapse all three into one number, you usually end up optimizing the wrong thing.
The three things you actually need to measure
Most production teams do not need fifty metrics. They need clarity on three layers of system quality.
1. Retrieval quality
If you are building RAG, the first question is whether the system retrieved the right evidence.
This includes questions like:
Did the relevant chunks show up?
Were the retrieved chunks mostly relevant or mostly noise?
Did metadata filters exclude useful evidence?
Did chunking damage retrieval quality?
If this layer is weak, no prompt template will rescue the final answer consistently.
2. Generation quality
The second question is whether the model used the retrieved evidence correctly.
This includes:
faithfulness to context
relevance to the question
hallucination behavior
output completeness and format
A system can retrieve the right evidence and still fail because the answer ignores it or overreaches past it.
3. End-to-end task success
The final question is whether the full workflow solved the user's actual problem.
This is broader than retrieval or generation quality in isolation. A support assistant may produce grounded answers and still fail if it routes tickets badly. A document extractor may emit valid JSON and still fail if the extracted fields are useless to the next system.
This is the layer that matters most to product teams, but it is also the hardest to measure cleanly.
Three Layers of LLM Evaluation
3
Task Success
User outcome · business metric · end-to-end pass/fail
2
Generation Quality
Faithfulness · answer relevancy · hallucination rate
1
Retrieval Quality
Context precision · context recall · chunk relevance
Layer 1 is the foundation — weak retrieval breaks everything above it
Separating retrieval, generation, and task-success layers makes failures far easier to diagnose
A practical eval stack usually starts here:
measure retrieval quality
measure generation quality
measure task success separately
That separation makes debugging far easier than one blended score.
RAGAS
RAGAS is the most directly RAG-focused framework of the three.
The official RAGAS metrics docs center the library around RAG-specific measures such as faithfulness, answer relevancy, context precision, and context recall. That makes RAGAS attractive when your main evaluation problem is not "how do I evaluate any LLM app?" but "how do I evaluate a retrieval-augmented system specifically?"
What it measures
The core RAGAS metrics are useful because they map cleanly onto the RAG pipeline.
Faithfulness asks whether the generated answer is supported by the provided context.
Answer relevancy asks whether the answer actually addresses the question.
Context precision looks at how much of the retrieved context is relevant.
Context recall looks at whether the retrieved context includes the information needed to answer.
That is a strong starting set because it forces teams to separate retrieval mistakes from answer mistakes.
When to use it
RAGAS is strongest when:
your product is clearly RAG-first
you want retrieval-specific metrics rather than generic LLM scoring
you already have evaluation samples with questions, contexts, and answers
you want a research-flavored metric layer rather than prompt-regression tooling
It fits naturally alongside a guide like
How to build a RAG system from scratch
, where retrieval quality is a first-class engineering concern rather than a side detail.
Limitations
RAGAS is not a complete production-evals answer by itself.
Its limitations are mostly practical:
it is strongest on RAG problems, weaker as a general app-eval platform
some metrics rely on judge-model behavior, which introduces cost and variance
good scores do not automatically imply good user experience
it does not replace application-level success metrics
In other words, RAGAS is good at telling you whether a RAG pipeline looks healthy. It is not enough to tell you whether the product is done.
DeepEval
DeepEval is broader and more software-workflow oriented than RAGAS.
Its official site positions it as an evaluation framework for unit-testing LLM systems, with native Pytest integration, CI workflow support, and a wide set of LLM-as-a-judge metrics. That framing matters. DeepEval is not just a metric library. It is trying to fit LLM evaluation into an engineering workflow teams already understand.
What it measures
DeepEval covers many evaluation shapes, but three ideas stand out.
Metric-based testing across multiple use cases, not only RAG
G-Eval style judging for more rubric-based quality evaluation
Hallucination and answer-quality checks that can be embedded into CI
G-Eval matters because it moves beyond raw similarity metrics and uses rubric-like judge logic. That makes it useful when the quality question is not only "did the answer overlap with a reference?" but "did it satisfy a qualitative standard?"
When to use it
DeepEval is strongest when:
you want evals to live near tests and CI
your app has multiple evaluation dimensions beyond retrieval
you want LLM-as-a-judge metrics without building the harness yourself
you need a more general evaluation layer across agents, chat systems, and RAG
This aligns well with teams treating evals as part of
LLMOps
, not as a one-off research notebook.
Limitations
DeepEval's biggest strength is also a caution.
Because it makes metric-driven testing easier, teams can end up over-trusting judge scores. A clean CI gate feels rigorous, but it can hide the fact that the metric itself may not match what users care about.
The main limitations are:
judge-model metrics can drift with provider or prompt changes
CI-friendly numbers can create false confidence
broad framework coverage can tempt teams into measuring everything and understanding little
DeepEval is best when you treat it as an engineering harness around carefully chosen metrics, not as a truth machine.
PromptFoo
PromptFoo comes from a different direction.
The official docs emphasize prompt regression testing, YAML-based configuration, red-teaming, and adversarial testing. That makes PromptFoo especially useful when your main question is: "Did a prompt, model, or config change break known behavior?"
What it measures
PromptFoo is less about RAG-native metrics like context precision and more about controlled evaluation workflows.
Its strengths include:
prompt regression testing
model comparison
red-teaming and vulnerability-oriented test generation
declarative YAML configs that work well in CI
That YAML-first approach is important. It makes eval configuration portable and reviewable in a way many notebook-based eval setups are not.
When to use it
PromptFoo is strongest when:
prompt changes are frequent
you want reproducible regression suites
red-teaming is part of your release process
your team likes config-driven testing more than Python-first eval harnesses
If your main operational pain is prompt drift, PromptFoo often solves the right problem faster than a pure metric framework.
Limitations
PromptFoo is not trying to be a deep RAG-metric framework in the RAGAS sense.
Its limitations are:
less specialized for retrieval diagnosis
more oriented toward behavioral regression than detailed pipeline attribution
still dependent on what you choose to test explicitly
PromptFoo is strongest as a regression and safety tool, not as a complete theory of AI quality.
Side-by-side comparison
The cleanest way to compare these three is by the primary question each one answers.
RAGAS answers: "Is my RAG pipeline retrieving the right context and staying faithful to it?"
DeepEval answers: "Can I turn LLM quality checks into an engineering workflow with metrics and CI?"
PromptFoo answers: "Did this prompt, model, or config change break expected behavior, and can I red-team it systematically?"
Another useful comparison is by default posture.
RAGAS is retrieval-and-generation diagnostic first.
DeepEval is test-framework first.
PromptFoo is regression-and-red-team first.
If your app is heavily RAG-centric, RAGAS is usually the clearest starting point.
If your team wants evals embedded into day-to-day engineering workflows, DeepEval is often the most natural fit.
If your organization is iterating prompts rapidly or cares about adversarial coverage and regression stability, PromptFoo is often the most pragmatic tool.
The mistake is not choosing the "wrong" framework. The mistake is expecting one framework to answer every evaluation question equally well.
Your eval set matters more than your framework
Teams often spend more time comparing frameworks than curating the dataset those frameworks will score.
That is backwards. A weak eval set will produce weak decisions no matter how elegant the tooling looks. If your cases are too easy, too clean, or too narrow, the framework will reward behavior that does not survive real traffic.
A useful eval set should include:
common cases your system handles every day
edge cases that often break retrieval or formatting
adversarial or noisy inputs
historically bad examples from production
cases tied to the business outcome you actually care about
This is where PromptFoo-style regression suites, RAGAS metrics, and DeepEval CI checks all depend on the same upstream truth: if the test set does not represent reality, the metric layer will mostly measure your assumptions.
How to build a minimal eval loop
The smallest useful eval loop is not complicated, but it does need discipline.
A minimal loop usually looks like this:
define a fixed evaluation set
choose one or two metrics tied to the system's actual job
run evals on every meaningful model, prompt, or retrieval change
review failures by category
keep a small human-review pass for ambiguous cases
The example below uses RAGAS-style metrics because they are easy to explain and map cleanly to retrieval systems.
Minimal Eval Loop in CI
Make
Change
Run
Eval Set
Review
Failures
Fix or
Accept
iterate until metrics pass
Treat evals as a repeating CI loop — not a one-off notebook check
# pip install -U ragas datasets
from
datasets
import
Dataset
from
ragas
import
evaluate
from
ragas.metrics
import
faithfulness, answer_relevancy, context_precision, context_recall
eval_data
=
{
"question"
: [
"What does the refund policy say about annual plans?"
],
"answer"
: [
"Annual plans can be refunded within 14 days."
],
"contexts"
: [[
"Refund policy: annual plans are eligible for refund within 14 days of purchase."
]],
"ground_truth"
: [
"Annual plans are eligible for a refund within 14 days of purchase."
],
}
dataset
=
Dataset.from_dict(eval_data)
results
=
evaluate(
dataset,
metrics
=
[
faithfulness,
answer_relevancy,
context_precision,
context_recall,
],
)
print
(results)
This is not a full production pipeline. It is the minimum viable habit. The important part is not the library call. It is the loop around it:
stable dataset
stable metrics
repeated execution
failure review
Without that loop, evals stay ornamental.
What to do when evals disagree with human judgment
This will happen. Expect it.
An eval may say a response is weak while a human reviewer thinks it is useful. Or a metric may score an answer highly while users find it confusing or incomplete. That does not mean evals are useless. It means the metric is only a proxy.
When disagreement appears, do three things.
Check whether the metric matches the product question.
If the product goal is task completion, a faithfulness score alone may be too narrow.
Review failure samples by category rather than by average score.
Often the disagreement is concentrated in one type of case, such as long-context questions or ambiguous prompts.
Promote human judgment into the loop where needed.
For high-stakes workflows, human review is not a temporary crutch. It is part of the evaluation design.
The right mental model is simple: automated evals are instruments, not verdicts. They help you see patterns, catch regressions, and scale review. They do not replace product judgment.
What this means
You do not need one perfect eval framework. You need an eval stack that matches the way your system fails.
If retrieval quality is the main unknown, start with RAGAS.
If your engineering team wants CI-native quality gates, start with DeepEval.
If prompt drift and red-teaming are the real operational risk, start with PromptFoo.
Over time, serious teams often combine ideas from all three. They measure retrieval quality, run regression suites, and keep a small human-review layer for the cases metrics do not capture well. That is what mature evaluation looks like in production AI: not one score, but a system of checks that tells you what changed, why it changed, and whether users will feel it.
Related articles
#
search
#
semantic search
Semantic search vs keyword search: when to use each (2026)
How BM25 and vector search actually work, where each one fails, why hybrid search usually wins in production, and how to decide which approach fits your use case.
10 min read
#
structured output
#
JSON
Structured output: getting reliable JSON from any LLM (2026)
Why structured outputs matter, how JSON mode and schema enforcement differ, and practical patterns for getting reliable JSON from LLMs in production.
11 min read
#
prompt engineering
#
system prompt
How to write a great system prompt (2026)
What system prompts actually do, why they break, and the patterns that make them reliable in production — with examples for assistants, extractors, and agents.
10 min read