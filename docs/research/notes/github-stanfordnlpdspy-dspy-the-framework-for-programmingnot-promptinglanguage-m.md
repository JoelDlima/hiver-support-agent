---
title: 'GitHub - stanfordnlp/dspy: DSPy: The framework for programming—not prompting—language
  models · GitHub'
id: github-stanfordnlpdspy-dspy-the-framework-for-programmingnot-promptinglanguage-m
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:30:39.285859Z'
source: https://github.com/stanfordnlp/dspy
source_domain: github.com
fetched_at: '2026-09-15T02:30:39.283859Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: code
deprecated: false
---

GitHub - stanfordnlp/dspy: DSPy: The framework for programming—not prompting—language models · GitHub
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
stanfordnlp
/
dspy
Public
Notifications
You must be signed in to change notification settings
Fork
3.3k
Star
38k
main
Branches
Tags
Go to file
Code
Open more actions menu
Latest commit
History
4,698 Commits
4,698 Commits
Folders and files
Name
Name
Last commit message
Last commit date
.github
.github
docs
docs
dspy
dspy
scripts
scripts
tests
tests
.gitignore
.gitignore
.pre-commit-config.yaml
.pre-commit-config.yaml
CONTRIBUTING.md
CONTRIBUTING.md
LICENSE
LICENSE
README.md
README.md
SECURITY.md
SECURITY.md
pyproject.toml
pyproject.toml
uv.lock
uv.lock
View all files
Repository files navigation
DSPy:
Programming
—not prompting—Foundation Models
Documentation:
DSPy Docs
DSPy is the framework for
programming—rather than prompting—language models
. It allows you to iterate fast on
building modular AI systems
and offers algorithms for
optimizing their prompts and weights
, whether you're building simple classifiers, sophisticated RAG pipelines, or Agent loops.
DSPy stands for Declarative Self-improving Python. Instead of brittle prompts, you write compositional
Python code
and use DSPy to
teach your LM to deliver high-quality outputs
. Learn more via our
official documentation site
or meet the community, seek help, or start contributing via this GitHub repo and our
Discord server
.
Documentation:
dspy.ai
Please go to the
DSPy Docs at dspy.ai
Installation
pip install dspy
To install the very latest from
main
:
pip install git+https://github.com/stanfordnlp/dspy.git
📜 Citation & Reading More
If you're looking to understand the framework, please go to the
DSPy Docs at dspy.ai
.
If you're looking to understand the underlying research, this is a set of our papers:
[Jul'25]
GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning
[Jun'24]
Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs
[Oct'23]
DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines
[Jul'24]
Fine-Tuning and Prompt Optimization: Two Great Steps that Work Better Together
[Jun'24]
Prompts as Auto-Optimized Training Hyperparameters
[Feb'24]
Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models
[Jan'24]
In-Context Learning for Extreme Multi-Label Classification
[Dec'23]
DSPy Assertions: Computational Constraints for Self-Refining Language Model Pipelines
[Dec'22]
Demonstrate-Search-Predict: Composing Retrieval & Language Models for Knowledge-Intensive NLP
To stay up to date or learn more, follow
@DSPyOSS
on Twitter or the DSPy page on LinkedIn.
The
DSPy
logo is designed by
Chuyi Zhang
.
If you use DSPy or DSP in a research paper, please cite our work as follows:
@inproceedings{khattab2024dspy,
  title={DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines},
  author={Khattab, Omar and Singhvi, Arnav and Maheshwari, Paridhi and Zhang, Zhiyuan and Santhanam, Keshav and Vardhamanan, Sri and Haq, Saiful and Sharma, Ashutosh and Joshi, Thomas T. and Moazam, Hanna and Miller, Heather and Zaharia, Matei and Potts, Christopher},
  journal={The Twelfth International Conference on Learning Representations},
  year={2024}
}
@article{khattab2022demonstrate,
  title={Demonstrate-Search-Predict: Composing Retrieval and Language Models for Knowledge-Intensive {NLP}},
  author={Khattab, Omar and Santhanam, Keshav and Li, Xiang Lisa and Hall, David and Liang, Percy and Potts, Christopher and Zaharia, Matei},
  journal={arXiv preprint arXiv:2212.14024},
  year={2022}
}
About
DSPy: The framework for programming—not prompting—language models
dspy.ai
Resources
Readme
MIT license
Contributing
Contributing
Security policy
Security policy
Activity
Custom properties
Stars
38.0k
stars
Watchers
215
watching
Forks
3.3k
forks
Report repository
Releases
Used by
Contributors
Languages
You can’t perform that action at this time.