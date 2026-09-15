---
title: Evaluation of LLM Applications - Langfuse
id: evaluation-of-llm-applications-langfuse
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:30:39.052795Z'
source: https://langfuse.com/docs/evaluation/overview
source_domain: langfuse.com
fetched_at: '2026-09-15T02:30:39.051795Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: docs
deprecated: false
---

Evaluation of LLM Applications - Langfuse
Langfuse v4: up to 165× faster ·
Read more
Langfuse v4 is here: real-time, up to 165× faster ·
Read more
Docs
Overview
Docs
Evaluation
Overview
Copy page
Evaluation Overview
Evals give you a repeatable check of your LLM application's behavior. You replace guesswork with data, and catch regressions before you ship a change.
Evaluation runs across most of the
AI engineering loop
: you score live traces in production, turn interesting examples into datasets, run experiments to compare changes, and judge the results with manual or automated evaluators. It happens both
online
, on live production traces, and
offline
, before you ship a change.
Deploy
Online
Trace
traces · sessions · agents · prompts
Online
Monitor
dashboards · LLM-as-judge · feedback
Offline
Build
datasets
datasets · features-as-tests
Offline
Experiment
prompts · models · code variants
Offline
Evaluate
judges · custom evals · annotation
🚀
Want to see it in action?
Create a free account
and explore Langfuse Evaluation in the
interactive example project
.
Getting Started
You can evaluate both:
live incoming traces
to measure quality on production data and track trends over time.
your existing application on a pre-defined dataset
, to make sure your changes are ready for production.
For more information on how evaluators, scores, datasets, and experiments fit together, read
Core Concepts
.
To catch regressions before they ship, run experiments in CI: add the
langfuse/experiment-action
GitHub Action to a
pull_request
workflow and raise
RegressionError
from your experiment script when a score violates your threshold; the action then fails the job. It works with Langfuse Cloud and self-hosted Langfuse.
If you're looking for another specific workflow, use the table below to find the right feature page:
If you want to...
Use this Langfuse feature
Review and rate traces manually
Annotation Queues
,
Scores via UI
Collect feedback from your end users
User Feedback
Leave open-ended notes on traces
Text scores
,
Annotation Queues
Build a reusable set of test cases
Datasets
Compare prompt, model, or code changes side by side
Experiments via UI
,
Experiments via SDK
,
Experiments via OpenTelemetry
Block deploys on regressions
CI/CD experiments
Reuse checks in your application or CI process
Evaluate an existing application
Run deterministic checks
Code Evaluators
Automatically score live production traces
LLM-as-a-Judge
,
Scores via API/SDK
See how scores trend over time
Score Analytics
,
custom dashboards
Already know what you're looking for? Browse
Evaluation Methods
and
Experiments
in the sidebar.
GitHub Discussions
Was this page helpful?
Good
Bad
Support
Last updated on
Previous
Troubleshooting and FAQ
Next
Evaluate Production Traffic
On this page
Evaluation Overview
Getting Started
GitHub Discussions
Actions
Give us feedback
Edit this page on GitHub
Contributors
Last edited
Jannik Maierhöfer
Marc Klingen
Lotte Verheyden
+
7
more
GitHub
X
Ask AI
A
A