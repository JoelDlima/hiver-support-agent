---
title: 'GitHub - vibrantlabsai/ragas: Supercharge Your LLM Application Evaluations
  🚀 · GitHub'
id: github-vibrantlabsairagas-supercharge-your-llm-application-evaluations-github
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:30:29.935716Z'
source: https://github.com/explodinggradients/ragas
source_domain: github.com
fetched_at: '2026-09-15T02:30:29.931016Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: code
deprecated: false
---

GitHub - vibrantlabsai/ragas: Supercharge Your LLM Application Evaluations 🚀 · GitHub
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
Uh oh!
There was an error while loading.
Please reload this page
.
vibrantlabsai
/
ragas
Public
Notifications
You must be signed in to change notification settings
Fork
1.7k
Star
15.7k
main
Branches
Tags
Go to file
Code
Open more actions menu
Latest commit
History
1,147 Commits
1,147 Commits
Folders and files
Name
Name
Last commit message
Last commit date
.claude/
commands
.claude/
commands
.cursor
.cursor
.github
.github
docs
docs
examples
examples
scripts
scripts
src/
ragas
src/
ragas
tests
tests
.dockerignore
.dockerignore
.gitattributes
.gitattributes
.gitignore
.gitignore
.pre-commit-config.yaml
.pre-commit-config.yaml
.readthedocs.yml
.readthedocs.yml
CLAUDE.md
CLAUDE.md
CODE_OF_CONDUCT.md
CODE_OF_CONDUCT.md
CONTRIBUTING.md
CONTRIBUTING.md
LICENSE
LICENSE
Makefile
Makefile
README.md
README.md
SECURITY.md
SECURITY.md
mkdocs-pdf.yml
mkdocs-pdf.yml
mkdocs.yml
mkdocs.yml
pyproject.toml
pyproject.toml
View all files
Repository files navigation
Supercharge Your LLM Application Evaluations 🚀
Documentation
|
Quick start
|
Join Discord
|
Blog
|
NewsLetter
|
Careers
Objective metrics, intelligent test generation, and data-driven insights for LLM apps
Ragas is your ultimate toolkit for evaluating and optimizing Large Language Model (LLM) applications. Say goodbye to time-consuming, subjective assessments and hello to data-driven, efficient evaluation workflows.
Don't have a test dataset ready? We also do production-aligned test set generation.
Key Features
🎯 Objective Metrics: Evaluate your LLM applications with precision using both LLM-based and traditional metrics.
🧪 Test Data Generation: Automatically create comprehensive test datasets covering a wide range of scenarios.
🔗 Seamless Integrations: Works flawlessly with popular LLM frameworks like LangChain and major observability tools.
📊 Build feedback loops: Leverage production data to continually improve your LLM applications.
🛡️ Installation
Pypi:
pip install ragas
Alternatively, from source:
pip install git+https://github.com/vibrantlabsai/ragas
🔥 Quickstart
Clone a Complete Example Project
The fastest way to get started is to use the
ragas quickstart
command:
#
List available templates
ragas quickstart
#
Create a RAG evaluation project
ragas quickstart rag_eval
#
Specify where you want to create it.
ragas quickstart rag_eval -o ./my-project
Available templates:
rag_eval
- Evaluate RAG systems
Coming Soon:
agent_evals
- Evaluate AI agents
benchmark_llm
- Benchmark and compare LLMs
prompt_evals
- Evaluate prompt variations
workflow_eval
- Evaluate complex workflows
Evaluate your LLM App
ragas
comes with pre-built metrics for common evaluation tasks. For example, Aspect Critique evaluates any aspect of your output using
DiscreteMetric
:
import
asyncio
from
openai
import
AsyncOpenAI
from
ragas
.
metrics
import
DiscreteMetric
from
ragas
.
llms
import
llm_factory
# Setup your LLM
client
=
AsyncOpenAI
()
llm
=
llm_factory
(
"gpt-4o"
,
client
=
client
)
# Create a custom aspect evaluator
metric
=
DiscreteMetric
(
name
=
"summary_accuracy"
,
allowed_values
=
[
"accurate"
,
"inaccurate"
],
prompt
=
"""Evaluate if the summary is accurate and captures key information.
Response: {response}
Answer with only 'accurate' or 'inaccurate'."""
)
# Score your application's output
async
def
main
():
score
=
await
metric
.
ascore
(
llm
=
llm
,
response
=
"The summary of the text is..."
)
print
(
f"Score:
{
score
.
value
}
"
)
# 'accurate' or 'inaccurate'
print
(
f"Reason:
{
score
.
reason
}
"
)
if
__name__
==
"__main__"
:
asyncio
.
run
(
main
())
Note
: Make sure your
OPENAI_API_KEY
environment variable is set.
Find the complete
Quickstart Guide
Want help in improving your AI application using evals?
In the past 2 years, we have seen and helped improve many AI applications using evals. If you want help with improving and scaling up your AI application using evals.
🔗 Book a
slot
or drop us a line:
founders@vibrantlabs.com
.
🫂 Community
If you want to get more involved with Ragas, check out our
discord server
. It's a fun community where we geek out about LLM, Retrieval, Production issues, and more.
Contributors
+----------------------------------------------------------------------------+
|     +----------------------------------------------------------------+     |
|     | Developers
:
Those who built with `ragas`.                      |     |
|     | (You have `import ragas` somewhere in your project)            |     |
|     |     +----------------------------------------------------+     |     |
|     |     | Contributors
:
Those who make `ragas` better.       |     |     |
|     |     | (You make PR to this repo)                         |     |     |
|     |     +----------------------------------------------------+     |     |
|     +----------------------------------------------------------------+     |
+----------------------------------------------------------------------------+
We welcome contributions from the community! Whether it's bug fixes, feature additions, or documentation improvements, your input is valuable.
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
🔍 Open Analytics
At Ragas, we believe in transparency. We collect minimal, anonymized usage data to improve our product and guide our development efforts.
✅ No personal or company-identifying information
✅ Open-source data collection
code
✅ Publicly available aggregated
data
To opt-out, set the
RAGAS_DO_NOT_TRACK
environment variable to
true
.
Cite Us
@misc{ragas2024,
  author       = {VibrantLabs},
  title        = {Ragas: Supercharge Your LLM Application Evaluations},
  year         = {2024},
  howpublished = {\url{https://github.com/vibrantlabsai/ragas}},
}
About
Supercharge Your LLM Application Evaluations 🚀
docs.ragas.io
Topics
evaluation
llm
llmops
Resources
Readme
Apache-2.0 license
Code of conduct
Code of conduct
Contributing
Contributing
Security policy
Security policy
Activity
Custom properties
Stars
15.7k
stars
Watchers
64
watching
Forks
1.7k
forks
Report repository
Releases
Used by
Contributors
Languages
You can’t perform that action at this time.