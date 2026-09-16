---
title: 'GitHub - kelukes/vps-support-ticket-clustering: Clustering and topic modeling
  of VPS support tickets using LDA and BERTopic (5600+ conversations, multilingual))
  · GitHub'
id: github-kelukesvps-support-ticket-clustering-clustering-and-topic-modeling-of-vps
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:29:14.109470Z'
source: https://github.com/kelukes/vps-support-ticket-clustering
source_domain: github.com
fetched_at: '2026-09-15T02:29:14.107471Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: code
deprecated: false
---

GitHub - kelukes/vps-support-ticket-clustering: Clustering and topic modeling of VPS support tickets using LDA and BERTopic (5600+ conversations, multilingual)) · GitHub
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
kelukes
/
vps-support-ticket-clustering
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
11 Commits
11 Commits
Folders and files
Name
Name
Last commit message
Last commit date
docs
docs
notebooks
notebooks
README.md
README.md
View all files
Repository files navigation
VPS Support Ticket Clustering
NLP-based clustering and topic modeling of VPS hosting support tickets using LDA and BERTopic. Analysis of 2700+ multilingual customer support conversations.
Overview
This project applies unsupervised machine learning to customer support chat logs from a VPS hosting provider to identify recurring issues and improve service efficiency.
Goal:
Reduce repetitive ticket workload and improve response times by identifying common support topics through text analytics.
Methodology
Data:
5000+ anonymized chat logs and email tickets (2021-2025)
Preprocessing:
Text cleaning, language detection, lemmatization, anonymization
Models:
Latent Dirichlet Allocation (LDA) and BERTopic clustering
Validation:
Coherence score 0.63, manual review by support team
Key Findings
Identified 15 main topics including:
Billing & payments (14%)
Trial period requests (10%)
Server access issues (12%)
Technical configuration (18%)
Control panel errors (8%)
Technologies
Python • scikit-learn • gensim • BERTopic • pandas • matplotlib • pyLDAvis
Note on Data
Due to GDPR compliance, the original dataset cannot be shared. The notebook includes all outputs (visualizations, metrics, results) to demonstrate the methodology.
Documentation
Comprehensive project documentation is available in the
/docs
folder:
Project Overview
– business context, problem statement, and KPIs
Solution Design
– data science approach and methodology
Data Evaluation
– data sources, quality assessment, and preprocessing
Ethics Assessment
– privacy, GDPR compliance, and responsible AI practices
About
Clustering and topic modeling of VPS support tickets using LDA and BERTopic (5600+ conversations, multilingual))
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