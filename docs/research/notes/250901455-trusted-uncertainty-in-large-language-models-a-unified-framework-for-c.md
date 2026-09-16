---
title: '[2509.01455] Trusted Uncertainty in Large Language Models: A Unified Framework
  for Confidence Calibration and Risk-Controlled Refusal'
id: 250901455-trusted-uncertainty-in-large-language-models-a-unified-framework-for-c
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:48:05.896373Z'
source: https://arxiv.org/abs/2509.01455
source_domain: arxiv.org
fetched_at: '2026-09-15T02:48:05.895407Z'
fetch_provider: builtin
status: draft
type: note
tier: institutional
content_type: paper
deprecated: false
doi: arXiv:2509.01455
---

[2509.01455] Trusted Uncertainty in Large Language Models: A Unified Framework for Confidence Calibration and Risk-Controlled Refusal
Skip to main content
Search arXiv
Press Enter to search ·
Advanced search
Computer Science > Computation and Language
arXiv:2509.01455
(cs)
This paper has been withdrawn by arXiv Admin
[Submitted on 1 Sep 2025 (
v1
), last revised 11 Jun 2026 (this version, v4)]
Title:
Trusted Uncertainty in Large Language Models: A Unified Framework for Confidence Calibration and Risk-Controlled Refusal
Authors:
Markus Oehri
,
Giulia Conti
,
Kaviraj Pather
,
Alexandre Rossi
,
Laia Serra
,
Adrian Parody
,
Rogvi Johannesen
,
Aviaja Petersen
,
Arben Krasniqi
View a PDF of the paper titled Trusted Uncertainty in Large Language Models: A Unified Framework for Confidence Calibration and Risk-Controlled Refusal, by Markus Oehri and 8 other authors
No PDF available, click to view other formats
Abstract:
Deployed language models must decide not only what to answer but also when not to answer. We present UniCR, a unified framework that turns heterogeneous uncertainty evidence including sequence likelihoods, self-consistency dispersion, retrieval compatibility, and tool or verifier feedback into a calibrated probability of correctness and then enforces a user-specified error budget via principled refusal. UniCR learns a lightweight calibration head with temperature scaling and proper scoring, supports API-only models through black-box features, and offers distribution-free guarantees using conformal risk control. For long-form generation, we align confidence with semantic fidelity by supervising on atomic factuality scores derived from retrieved evidence, reducing confident hallucinations while preserving coverage. Experiments on short-form QA, code generation with execution tests, and retrieval-augmented long-form QA show consistent improvements in calibration metrics, lower area under the risk-coverage curve, and higher coverage at fixed risk compared to entropy or logit thresholds, post-hoc calibrators, and end-to-end selective baselines. Analyses reveal that evidence contradiction, semantic dispersion, and tool inconsistency are the dominant drivers of abstention, yielding informative user-facing refusal messages. The result is a portable recipe of evidence fusion to calibrated probability to risk-controlled decision that improves trustworthiness without fine-tuning the base model and remains valid under distribution shift.
Comments:
arXiv admin note: This paper has been withdrawn by arXiv due to unverifiable authorship and affiliation
Subjects:
Computation and Language (cs.CL)
MSC
classes:
68T50
ACM
classes:
I.2.7
Cite as:
arXiv:2509.01455
[cs.CL]
(or
arXiv:2509.01455v4
[cs.CL]
for this version)
https://doi.org/10.48550/arXiv.2509.01455
Focus to learn more
arXiv-issued DOI via DataCite
Submission history
From: arXiv Admin [
view email
]
[v1]
Mon, 1 Sep 2025 13:14:58 UTC (175 KB)
[v2]
Fri, 26 Dec 2025 08:03:24 UTC (167 KB)
[v3]
Mon, 29 Dec 2025 09:37:43 UTC (166 KB)
[v4]
Thu, 11 Jun 2026 18:26:26 UTC (1 KB)
(withdrawn)
Full-text links:
Access Paper:
View a PDF of the paper titled Trusted Uncertainty in Large Language Models: A Unified Framework for Confidence Calibration and Risk-Controlled Refusal, by Markus Oehri and 8 other authors
Withdrawn
No license for this version due to withdrawn
Current browse context:
cs.CL
< prev
|
next >
new
|
recent
|
2025-09
Change to browse by:
cs
References & Citations
NASA ADS
Google Scholar
Semantic Scholar
export BibTeX citation
Loading...
BibTeX formatted citation
×
loading...
Data provided by:
Bookmark
Bibliographic Tools
Bibliographic and Citation Tools
Bibliographic Explorer Toggle
Bibliographic Explorer
(
What is the Explorer?
)
Connected Papers Toggle
Connected Papers
(
What is Connected Papers?
)
Litmaps Toggle
Litmaps
(
What is Litmaps?
)
scite.ai Toggle
scite Smart Citations
(
What are Smart Citations?
)
Code, Data, Media
Code, Data and Media Associated with this Article
alphaXiv Toggle
alphaXiv
(
What is alphaXiv?
)
Links to Code Toggle
CatalyzeX Code Finder for Papers
(
What is CatalyzeX?
)
DagsHub Toggle
DagsHub
(
What is DagsHub?
)
GotitPub Toggle
Gotit.pub
(
What is GotitPub?
)
Huggingface Toggle
Hugging Face
(
What is Huggingface?
)
ScienceCast Toggle
ScienceCast
(
What is ScienceCast?
)
Demos
Demos
Replicate Toggle
Replicate
(
What is Replicate?
)
Spaces Toggle
Hugging Face Spaces
(
What is Spaces?
)
Spaces Toggle
TXYZ.AI
(
What is TXYZ.AI?
)
Related Papers
Recommenders and Search Tools
Link to Influence Flower
Influence Flower
(
What are Influence Flowers?
)
Core recommender toggle
CORE Recommender
(
What is CORE?
)
Author
Venue
Institution
Topic
About arXivLabs
arXivLabs: experimental projects with community collaborators
arXivLabs is a framework that allows collaborators to develop and share new arXiv features directly on our website.
Both individuals and organizations that work with arXivLabs have embraced and accepted our values of openness, community, excellence, and user data privacy. arXiv is committed to these values and only works with partners that adhere to them.
Have an idea for a project that will add value for arXiv's community?
Learn more about arXivLabs
.
Which authors of this paper are endorsers?
|
Disable MathJax
(
What is MathJax?
)