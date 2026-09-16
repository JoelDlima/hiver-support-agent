---
title: '[2209.11055] Efficient Few-Shot Learning Without Prompts'
id: 220911055-efficient-few-shot-learning-without-prompts
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:30:30.549176Z'
source: https://arxiv.org/abs/2209.11055
source_domain: arxiv.org
fetched_at: '2026-09-15T02:30:30.548173Z'
fetch_provider: builtin
status: draft
type: note
tier: institutional
content_type: paper
deprecated: false
doi: arXiv:2209.11055
citation_count: 320
venue: arXiv.org
is_retracted: false
---

[2209.11055] Efficient Few-Shot Learning Without Prompts
Skip to main content
Search arXiv
Press Enter to search ·
Advanced search
Computer Science > Computation and Language
arXiv:2209.11055
(cs)
[Submitted on 22 Sep 2022]
Title:
Efficient Few-Shot Learning Without Prompts
Authors:
Lewis Tunstall
,
Nils Reimers
,
Unso Eun Seo Jo
,
Luke Bates
,
Daniel Korat
,
Moshe Wasserblat
,
Oren Pereg
View a PDF of the paper titled Efficient Few-Shot Learning Without Prompts, by Lewis Tunstall and 6 other authors
View PDF
HTML (experimental)
Abstract:
Recent few-shot methods, such as parameter-efficient fine-tuning (PEFT) and pattern exploiting training (PET), have achieved impressive results in label-scarce settings. However, they are difficult to employ since they are subject to high variability from manually crafted prompts, and typically require billion-parameter language models to achieve high accuracy. To address these shortcomings, we propose SetFit (Sentence Transformer Fine-tuning), an efficient and prompt-free framework for few-shot fine-tuning of Sentence Transformers (ST). SetFit works by first fine-tuning a pretrained ST on a small number of text pairs, in a contrastive Siamese manner. The resulting model is then used to generate rich text embeddings, which are used to train a classification head. This simple framework requires no prompts or verbalizers, and achieves high accuracy with orders of magnitude less parameters than existing techniques. Our experiments show that SetFit obtains comparable results with PEFT and PET techniques, while being an order of magnitude faster to train. We also show that SetFit can be applied in multilingual settings by simply switching the ST body. Our code is available at
this https URL
and our datasets at
this https URL
.
Subjects:
Computation and Language (cs.CL)
Cite as:
arXiv:2209.11055
[cs.CL]
(or
arXiv:2209.11055v1
[cs.CL]
for this version)
https://doi.org/10.48550/arXiv.2209.11055
Focus to learn more
arXiv-issued DOI via DataCite
Submission history
From: Daniel Korat [
view email
]
[v1]
Thu, 22 Sep 2022 14:48:11 UTC (7,160 KB)
Full-text links:
Access Paper:
View a PDF of the paper titled Efficient Few-Shot Learning Without Prompts, by Lewis Tunstall and 6 other authors
View PDF
HTML (experimental)
TeX Source
view license
Current browse context:
cs.CL
< prev
|
next >
new
|
recent
|
2022-09
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