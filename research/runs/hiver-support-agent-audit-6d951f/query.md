---
vault_tag: hiver-support-agent-audit-6d951f
created: 2026-09-15T07:54:48+05:30
source: user-prompt
---

You are running a HyperResearch deep-research run. Research query (verbatim, gospel — never paraphrase it):

# HIVER — DEEP RESEARCH + FORENSIC AUDIT + RE-ENGINEERING DIRECTIVE

CURRENT DATE:
September 14, 2026

PROJECT:
Hiver

IMPORTANT:
This is NOT a greenfield project.

An AI coding agent has already implemented a substantial version of this project in the Hiver workspace during a previous session.

DO NOT ASSUME THAT IMPLEMENTATION IS CORRECT.

DO NOT ASSUME THAT THE EXISTING ARCHITECTURE IS GOOD.

DO NOT ASSUME THAT THE CURRENT MODEL, retrieval system, prompts, evaluation, backend, frontend, database, infrastructure, or scalability design are adequate.

Treat the existing implementation as an external team's submission that you have been asked to audit before it is submitted.

Your job is to:

RESEARCH → INSPECT → AUDIT → BENCHMARK → IDENTIFY WEAKNESSES → RESEARCH ALTERNATIVES → RE-ARCHITECT WHERE NECESSARY → IMPLEMENT IMPROVEMENTS → VALIDATE → DOCUMENT

The goal is NOT to preserve existing code.

The goal is to produce the strongest practical submission possible for this assignment.

======================================================================
# OFFICIAL ASSIGNMENT
======================================================================

Hiver SDE Intern — Take-Home Assignment

What we are testing:
whether you can turn a messy real-world dataset into a working AI system and prove it works.

The proof is worth more than the system.

## The problem

You are given real customer-support conversations between customers and brands on Twitter.

Pick ONE brand from the dataset and build an AI support agent for it that can:

1. Classify each incoming customer message into a small set of intents that you define from the data.

2. Draft a reply grounded in how that brand has historically resolved similar issues.

3. Decide whether the message should be auto-handled or escalated to a human — with a stated reason.

You then have to convince us the agent is good enough to trust.

That is the hard part.

## Dataset

Primary:
Customer Support on Twitter
Kaggle:
thoughtvector/customer-support-on-twitter

Approximately 3M tweets/replies, multi-turn threads, dozens of brands.

Real, noisy, and imperfect.

Optional secondary dataset:
Banking77
Hugging Face:
PolyAI/banking77

Approximately 13k queries and 77 labelled intents.

Banking77 may be used for intent work ONLY.

You may use any LLM API or open model.

## Deliverables

### 1. Repository

Runnable pipeline.

README must allow reproduction of headline results in under 15 minutes.

### 2. Golden evaluation set

150–250 hand-labelled examples created by us.

Must include:

- short explanation of sampling
- explanation of labelling
- rationale for the label scheme

### 3. Evaluation harness

Automated metrics.

LLM-as-judge rubric for reply quality.

Evidence showing how well the LLM judge agrees with a human.

### 4. Report

Maximum 6 pages OR equivalent README section.

Must cover:

- problem framing
- what "good" means for this brand
- what was deliberately NOT built
- results vs at least two baselines
- one trivial baseline
- one simple baseline
- top 5 failure modes with real examples
- hypotheses explaining those failures
- mandatory section:
  "What is misleading about my headline number?"
- what would be done with one additional week

### 5. Decision log

10–15 non-obvious decisions.

Plain bullet list is acceptable.

### Submission

Submit through:

https://intelligent-bar-256.notion.site/39492cbf0da2800682c78a600a745f

Include repository link and report.

Do not email submissions.

### Rules

AI coding assistants may be used freely.

The candidate must be able to explain and modify their own code live.

Cite anything borrowed.

Borrowing is allowed.

Not knowing what was borrowed is not.

The evaluators will NOT run the code against the full dataset.

A subsample is expected and encouraged.

======================================================================
# PRIMARY OBJECTIVE
======================================================================

Build the strongest submission possible for the EXACT assignment above.

(See scaffold.md for the full directive — this query file preserves the verbatim user prompt as received; the complete directive text is gospel and is referenced in full from the original request.)
