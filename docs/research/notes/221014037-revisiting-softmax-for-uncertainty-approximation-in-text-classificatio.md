---
title: '[2210.14037] Revisiting Softmax for Uncertainty Approximation in Text Classification'
id: 221014037-revisiting-softmax-for-uncertainty-approximation-in-text-classificatio
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:48:02.430576Z'
source: https://arxiv.org/abs/2210.14037
source_domain: arxiv.org
fetched_at: '2026-09-15T02:48:02.429577Z'
fetch_provider: builtin
status: draft
type: note
tier: institutional
content_type: paper
deprecated: false
doi: arXiv:2210.14037
---

[2210.14037] Revisiting Softmax for Uncertainty Approximation in Text Classification
Skip to main content
Search arXiv
Press Enter to search ·
Advanced search
Computer Science > Machine Learning
arXiv:2210.14037
(cs)
[Submitted on 25 Oct 2022 (
v1
), last revised 19 Jul 2023 (this version, v2)]
Title:
Revisiting Softmax for Uncertainty Approximation in Text Classification
Authors:
Andreas Nugaard Holm
,
Dustin Wright
,
Isabelle Augenstein
View a PDF of the paper titled Revisiting Softmax for Uncertainty Approximation in Text Classification, by Andreas Nugaard Holm and 2 other authors
View PDF
HTML (experimental)
Abstract:
Uncertainty approximation in text classification is an important area with applications in domain adaptation and interpretability. One of the most widely used uncertainty approximation methods is Monte Carlo (MC) Dropout, which is computationally expensive as it requires multiple forward passes through the model. A cheaper alternative is to simply use the softmax based on a single forward pass without dropout to estimate model uncertainty. However, prior work has indicated that these predictions tend to be overconfident. In this paper, we perform a thorough empirical analysis of these methods on five datasets with two base neural architectures in order to identify the trade-offs between the two. We compare both softmax and an efficient version of MC Dropout on their uncertainty approximations and downstream text classification performance, while weighing their runtime (cost) against performance (benefit). We find that, while MC dropout produces the best uncertainty approximations, using a simple softmax leads to competitive and in some cases better uncertainty estimation for text classification at a much lower computational cost, suggesting that softmax can in fact be a sufficient uncertainty estimate when computational resources are a concern.
Subjects:
Machine Learning (cs.LG)
; Computation and Language (cs.CL)
Cite as:
arXiv:2210.14037
[cs.LG]
(or
arXiv:2210.14037v2
[cs.LG]
for this version)
https://doi.org/10.48550/arXiv.2210.14037
Focus to learn more
arXiv-issued DOI via DataCite
Submission history
From: Isabelle Augenstein [
view email
]
[v1]
Tue, 25 Oct 2022 14:13:53 UTC (7,462 KB)
[v2]
Wed, 19 Jul 2023 13:43:07 UTC (8,092 KB)
Full-text links:
Access Paper:
View a PDF of the paper titled Revisiting Softmax for Uncertainty Approximation in Text Classification, by Andreas Nugaard Holm and 2 other authors
View PDF
HTML (experimental)
TeX Source
view license
Current browse context:
cs.LG
< prev
|
next >
new
|
recent
|
2022-10
Change to browse by:
cs
cs.CL
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
IArxiv recommender toggle
IArxiv Recommender
(
What is IArxiv?
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