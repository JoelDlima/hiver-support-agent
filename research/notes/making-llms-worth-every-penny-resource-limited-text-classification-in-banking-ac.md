---
title: 'Making LLMs Worth Every Penny: Resource-Limited Text Classification in Banking
  (ACM ICAIF 2023)'
id: making-llms-worth-every-penny-resource-limited-text-classification-in-banking-ac
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:05.943194Z'
source: https://helvia.ai/labs/making-llms-worth-every-penny-resource-limited-text-classification-in-banking/
source_domain: helvia.ai
fetched_at: '2026-09-15T02:28:05.939180Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Making LLMs Worth Every Penny: Resource-Limited Text Classification in Banking (ACM ICAIF 2023)
Lefteris Loukas, Ilias Stogiannidis, Odysseas Diamantopoulos, Prodromos Malakasiotis, Stavros Vassos
Read the full paper here:
https://arxiv.org/abs/2311.06102
Abstract
Standard Full-Data classifiers in NLP demand thousands of labeled examples, which is impractical in data-limited domains. Few-shot methods offer an alternative, utilizing contrastive learning techniques that can be effective with as little as 20 examples per class. Similarly, Large Language Models (LLMs) like GPT-4 can perform effectively with just 1-5 examples per class. However, the performance-cost trade-offs of these methods remain underexplored, a critical concern for budget-limited organizations. Our work addresses this gap by studying the aforementioned approaches over the Banking77 financial intent detection dataset, including the evaluation of cutting-edge LLMs by OpenAI, Cohere, and Anthropic in a comprehensive set of few-shot scenarios. We complete the picture with two additional methods: first, a cost-effective querying method for LLMs based on retrieval-augmented generation (RAG), able to reduce operational costs multiple times compared to classic few-shot approaches, and second, a data augmentation method using GPT-4, able to improve performance in data-limited scenarios. Finally, to inspire future research, we provide a human expert’s curated subset of Banking77, along with extensive error analysis.
Motivation
We study how we can approach text classification effectively in terms of both performance and cost. We use the Banking77 dataset (
https://huggingface.co/datasets/PolyAI/banking77
), composed of customer support dialogs and their labels. We mainly study Few-shot Settings, where we have limited samples per class (resource-limited scenario), typically 1 to 20 samples per class. For the sake of completeness, we also present some results in the Full-Data Setting, where one can fine-tune models on thousands of samples (which is often impractical).
To the best of our knowledge, this is the first study on the performance-cost investigation of LLMs versus MLMs. Many companies tend to use the most modern models like proprietary LLMs (OpenAI GPT-4), which come at a pretty heavy cost without comparing their performance with cheaper, older models that might perform equally.
After benchmarking the performance-cost tradeoffs of LLMs and MLMs in
Banking77
(a real-life conversational dataset of a bank's customer support with 77 labels), we introduce a
cost-effective LLM inference method
based on active learning, similar to how
RAG (Retrieval-Augmented Generation)
is performed nowadays in question-answering chatbots. This is able to reduce LLM costs more than 3 times in real-life business settings. Then, we follow with an extra study showing
how much synthetic data can one generate
in such resource-limited scenarios.
Methodology Outline
We tackle text classification in Few-Shot Settings (where we have limited samples per class) in 2 ways:
Contrastive Learning (SetFit)
with Masked Language Models
(MLMs)
In-Context Learning (Prompting)
with Large Language Models
(LLMs)
An overview of Contrastive Learning (SetFit), as used in MLMs. Setfit was first introduced by HuggingFace (Tunstall et al., 2022). It utilizes Sentence Transformers (like MPNet) in a Siamese + Supervised Fine-Tuning Manner by having an objective function to minimize the distance between samples of the same labels. The result is that it produces rich vector representations, even when providing only 10 to 20 samples per class for your text classification problem.
An overview of In-Context Learning, as used in LLMs.We leverage the pre-trained knowledge of LLMs and extend it with our specific task instructions and a few examples per class. This is done for each inference sample. We use a variety of proprietary LLMs, like OpenAI GPT-3.5 and GPT-4, Anthropic Claude 2, and Cohere's Command-Nightly.
Results (#1)
We then employ SetFit methodology on the MPNet-v2 model, a state-of-the-art sentence transformer based on BERT, according to
https://sbert.net/
.
We also utilize In-Context Learning for multiple proprietary LLMs like OpenAI GPT-3.5, GPT-4, Anthropic Claude 1 & 2, and, Cohere's Command-nightly.
For the MPNet models (and the SetFit technique), we use different settings of 3/5/10/15/20 samples per class, as SetFit typically requires around 10-20 samples to work well.
For the LLMs, we use 1 and 3 samples per class, due to context length limitations (OpenAI had 4K context length limitations at the time of the development). Also, for the LLMs, we use both random samples from the dataset and "representative" samples, as selected by a domain expert. The intuition here is that representative samples will outperform randomly sampled ones and we believe that it is feasible for a company to pick 3 "good" samples for each class in a dataset.
First, let's focus on LLMs. GPT-4 performs the best across 1-shot settings, outperforming competitors like Anthropic Claude and Cohere's Command-nightly. In the 3-shot setting, GPT-4 also works the best. Surprisingly, GPT-3.5's performance in the 3-shot setting drops, compared to the 1-shot setting, probably due to GPT-3.5 getting "Lost In The Middle" (
https://arxiv.org/abs/2307.03172
) when having a bigger context. As expected, the representative samples work better than random samples in all of our ablation experiments (using OpenAI models). On the other side of MLMs, MPNet might start with a low of 57.4 in the 1-shot setting (vs GPT-4's 80.4) but has a comparable 76.7 in the 3-shot setting (vs GPT-4's 83.1). After providing more samples to the MLM, something which is impossible to the LLMs (due to maximum 4K context capacity), the MPNet models reach a top 91.2 micro-F1 Score, which is 3 points lower than fine-tuning in the typical Full Data Setting with hundreds/thousands of samples per class (94.1)
Cost Analysis
Proprietary LLMs might work well but they cost a lot, due to hefty costs in their API usage per token. Thus, apart from their performance, we analyze their costs. This is the first time that this industrial point-of-view (performance/cost tradeoff) is reported.
In the 1-shot setting, where we show 1 example per class to the LLM, GPT-4 has 80.4 F1 score but costs 620$, while Anthropic Claude 2 costs only 15$ but has 76.8$ micro-f1. It depends on you and your preference on which to choose (money over slight performance increase?). Also, in the 3-shot setting, GPT-4 outperforms GPT-3.5 by nearly 20 points, but costs around 10 times more. We perform 3,080 queries in the test set, one for each inference sample.
RAG (or Dynamic Few-Shot Prompting) for Cost-Effective LLM Inference
Right now, for each class, we feed the LLM N examples per class (classic N-shot settings). For example, in the 3-shot settings and 77 classes,
we feed the model
3x77 =
231 samples, hitting the limit of the 4K context window and having a high API cost of the OpenAI and other LLM providers.
Instead of feeding so many samples to the model each time we want to classify a test sample, we found out that during inference,
we can retrieve only the top K similar (and their labels), and perform better while reducing the context size (and associated costs).
This is called
Dynamic Few-Shot Prompting
since we dynamically change the examples we show to the LLM via the prompt or
RAG (Retrieval-Augmented Generation)
, since the LLM generates after the prompt is being augmented after a retrieval step (as seen in the classic question-answering tasks nowadays). We retrieve the most similar examples and their labels by utilizing the cosine similarity in the sentence embeddings (encoded through MPNet).
Results (#2) with RAG/Dynamic Few-Shot Prompting
After performing RAG (or Dynamic Few-Shot Prompting) with K=5/10/20 top similar examples (and their labels) from their training set, one call at a time for each inference/test sample, we also report the results and their (spoiler alert!) heavily reduced associated dollar costs.
Seeing GPT-4 results with RAG (this table) and without RAG (previous table), it seems better (and cheaper) to use LLMs with this dynamic prompting approach (with 5/10/20 samples total), instead of having a classic Few-Shot approach where one shows 3x77 samples per class (231 samples total). Also, Claude 2 on K=20 similar (RAG) yields
85.5% on only 42$, out
vs. GPT-4’s original
83.1% on 740$
(previous table) 🤯 We perform 3,080 queries in the test set, one for each inference sample.
Extra: Are LLMs capable for synthetic data generation?
Data augmentation or synthetic data generation is especially important since when one performs Few-Shot approaches, they are doing this mostly because they are data-limited. And as always, the more the data, the better.
So, we tested if we can trust LLMs for synthetic data generation and the answer is:
yes, but up to a point.
Previous reports show that data augmentation for tasks with large and overlapping label tasks is difficult (see
https://aclanthology.org/2022.nlp4convai-1.5/
). For this reason, we did a semantic clustering of the 77 labels and 3 of their examples into N=10 groups. Then, we fed each group to GPT-4 (label + 3 examples), asking it to generate 20 more.
💡 The intuition behind this is that the LLM will understand the overlapping differences of the 77 labels and their examples and will be able to create synthetic data which can be differentiated from one class to another.
After doing that, we put them to the test with the MPNet models (using the SetFit Few-Shot approach).
In this result, we suppose that we have at least N=3 real samples per class, and we want to test and compare how synthetic/augmented data perform vs. actual real ones. Following the
black
line, we do see an increase when using the augmented 5 and 10 samples in the Few-Shot Scenario. However, the performance drops after 10 samples, which seems to be the sweet spot for this experiment. For reference reasons, we also have the real data plotted in green line, which indicate that real data are better than GPT-4 generated data.
Takeaways
Our work provides a practical rule of thumb for text classification in settings with lots of classes, such as intent detection in chatbot use cases:
If you have more than 5 examples per class, it's better to finetune a pretrained model such as MPNet using a contrastive learning technique such as SetFit.
If you have less than 5 examples per class, it's better to use LLMs.
To reduce the costs of LLMs, one can employ "dynamic" few-shot prompting (employing RAG) that performs better and costs a fraction of the regular few-shot prompting.
Synthetic data can be used to enhance performance, but we found that it hurts the results after incorporating N=7 synthetic examples. As expected though, real data is much better than GPT-4 generated data.
Citation
@inproceedings{10.1145/3604237.3626891,
author = {Loukas, Lefteris and Stogiannidis, Ilias and Diamantopoulos, Odysseas and Malakasiotis, Prodromos and Vassos, Stavros},
title = {Making LLMs Worth Every Penny: Resource-Limited Text Classification in Banking},
year = {2023},
isbn = {9798400702402},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3604237.3626891},
doi = {10.1145/3604237.3626891},
pages = {392–400},
numpages = {9},
keywords = {Anthropic, Cohere, OpenAI, LLMs, NLP, Claude, GPT, Few-shot},
location = {Brooklyn, NY, USA},
series = {ICAIF '23}
}
Resources
Paper:
https://arxiv.org/abs/2311.06102
Kudos (ACM Showcase) Blogpost:
https://www.growkudos.com/publications/10.1145%25252F3604237.3626891/reader
Dataset (Banking77):
https://huggingface.co/datasets/PolyAI/banking77
Representative Samples curated by a domain expert (3 samples per class):
https://huggingface.co/datasets/helvia/banking77-representative-samples
Acknowledgments
This work has received funding from European Union’s Horizon 2020 research and innovation programme under grant agreement No 101021714 ("LAW GAME"). Also, we would like to sincerely thank the Hellenic Artificial Intelligence Society (EETN) for their sponsorship.