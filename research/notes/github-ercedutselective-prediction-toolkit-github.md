---
title: GitHub - ercedut/selective-prediction-toolkit · GitHub
id: github-ercedutselective-prediction-toolkit-github
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.001244Z'
source: https://github.com/ercedut/selective-prediction-toolkit
source_domain: github.com
fetched_at: '2026-09-15T02:28:16.999244Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: code
deprecated: false
---

GitHub - ercedut/selective-prediction-toolkit · GitHub
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
ercedut
/
selective-prediction-toolkit
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
src
src
tests
tests
.gitattributes
.gitattributes
README.md
README.md
requirements.txt
requirements.txt
View all files
Repository files navigation
Selective Prediction Toolkit
Overview
This repository provides a small, production-ready toolkit for selective prediction with abstention. It computes risk coverage curves, AURC, and a generalized risk coverage area (AUGRC), and includes a policy wrapper that picks a threshold to meet a target coverage using a calibration split. It also includes sanity checks that reveal evaluation traps such as equal accuracy but very different selective behavior.
What selective prediction is (abstention)
Selective prediction accepts a prediction only if the model confidence is high enough. Given a confidence score s(x) and a threshold tau, a prediction is accepted when s(x) >= tau and abstained otherwise. The goal is to lower risk on accepted samples while controlling coverage.
Risk coverage curve definition and computation
Coverage at threshold tau is the fraction of accepted samples. Risk is computed only on accepted samples, using classification error or log loss. The toolkit computes the full risk coverage curve by sorting samples by score in descending order and evaluating the selective risk as more samples are accepted. It also provides a threshold grid version to match operational thresholds.
AURC definition and common reporting traps
AURC is the area under the risk coverage curve, computed with the trapezoidal rule over coverage in (0, 1]. A common trap is reporting overall accuracy without checking selective behavior. Two models can have the same accuracy but drastically different AURC, depending on how informative their confidence scores are.
AUGRC and why it can be more robust in practice
AUGRC generalizes AURC by explicitly penalizing abstention. For coverage c, the generalized risk coverage cost is GRC(c) = risk(c) + gamma * (1 - c). The area under this curve captures both selective risk and the cost of abstaining. A higher gamma penalizes low coverage more strongly. The default gamma is 0.5, and you can pass other values in the CLI.
Policy wrapper: choosing threshold for target coverage (calibration split)
To target a desired coverage, the policy wrapper fits a threshold on a calibration set by selecting the score at a quantile that matches the target coverage. This threshold is then applied to test scores to measure achieved coverage and selective risk. The toolkit handles repeated scores and extreme target coverages.
Sanity checks: why same accuracy can still be misleading
The sanity suite constructs cases where two models have identical accuracy but different score distributions. It also includes score corruption, random acceptance, and perfect ranking. These checks validate that AURC and AUGRC respond to true selectivity rather than accuracy alone.
How to run (CLI examples)
python -m src.cli --mode demo --dataset breast_cancer --model logreg --score maxprob --reports reports/
python -m src.cli --mode demo --dataset breast_cancer --model rf --score maxprob --target-coverages 0.7,0.9 --reports reports/
python -m src.cli --mode sanity --reports reports/
python -m src.cli --mode compare --dataset digits --models logreg,rf --reports reports/
Outputs and how to interpret them
The demo and compare modes write:
reports/curves.csv with coverage and risk per model and score type
reports/metrics.json with AURC, AUGRC, and selective risk at target coverages
reports/risk_coverage.png with risk coverage curves
reports/grc_curve.png with generalized risk coverage curves
reports/run_summary.txt with a concise run log
The sanity mode writes reports/sanity_checks.png and appends to run_summary.txt.
About
No description, website, or topics provided.
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