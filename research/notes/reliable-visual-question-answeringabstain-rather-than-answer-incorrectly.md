---
title: Reliable Visual Question Answering:Abstain Rather Than Answer Incorrectly
id: reliable-visual-question-answeringabstain-rather-than-answer-incorrectly
tags:
- hiver-support-agent-audit-6d951f
- locus-escalation-calibration-under-shift
created: '2026-09-15T02:40:15.500487Z'
source: https://arxiv.org/html/2204.13631v2
source_domain: arxiv.org
fetched_at: '2026-09-15T02:40:15.498476Z'
fetch_provider: builtin
status: draft
type: note
tier: institutional
content_type: paper
deprecated: false
---

Reliable Visual Question Answering:Abstain Rather Than Answer Incorrectly
Title:
Content selection saved. Describe the issue below:
Description:
arXiv is now an independent nonprofit!
Learn more
×
License: arXiv.org perpetual non-exclusive license
arXiv:2204.13631v2 [cs.CV] 27 Jul 2022
Reliable Visual Question Answering:
Abstain Rather Than Answer Incorrectly
Spencer Whitehead
⋆
Affiliation:
Meta AI
Suzanne Petryk
⋆
Affiliation:
Meta AI
Affiliation:
UC Berkeley
Vedaad Shakib
Affiliation:
UC Berkeley
Joseph Gonzalez
Affiliation:
UC Berkeley
Trevor Darrell
Affiliation:
UC Berkeley
Anna Rohrbach
Affiliation:
UC Berkeley
Marcus Rohrbach
Affiliation:
Meta AI
Abstract
Machine learning has advanced dramatically, narrowing the accuracy gap to humans in multimodal tasks like visual question answering (VQA).
However, while humans can say “
I don’t know
” when they are uncertain (i.e.,
abstain
from answering a question), such ability has been largely neglected in multimodal research, despite the importance of this problem to the usage of VQA in real settings.
In this work, we promote a problem formulation for
reliable VQA
, where we prefer abstention over providing an incorrect answer. We first enable abstention capabilities for several VQA models, and analyze both their
coverage
, the portion of questions answered, and
risk
, the error on that portion.
For that, we explore several abstention approaches.
We find that although the best performing models achieve over 71% accuracy on the VQA v2 dataset, introducing the option to abstain by directly using a model’s softmax scores limits them to answering less than 8% of the questions to achieve a low risk of error (i.e., 1%).
This motivates us to utilize a multimodal selection function to directly estimate the correctness of the predicted answers, which we show can increase the coverage by, for example, 2.4
×
\times
from 6.8% to 16.3% at 1% risk.
While it is important to analyze both coverage and risk, these metrics have a trade-off which makes comparing VQA models challenging.
To address this, we also propose an
Effective Reliability
metric for VQA that places a larger cost on incorrect answers compared to abstentions.
This new problem formulation, metric, and analysis for VQA provide the groundwork for building effective and reliable VQA models that have the self-awareness to abstain if and only if they don’t know the answer.
1
1
1
Code and models:
https://github.com/facebookresearch/reliable_vqa
1
1
footnotetext:
Equal contribution
1
Introduction
Visual Question Answering (VQA) is an important task and one core application of VQA is to provide a multimodal assistant, such as one that can answer questions to help with daily tasks for a user with visual impairments
[
5
,
29
]
.
To provide such utility, users must be able to trust the output of these tools as they may be basing decisions or actions on the output
[
6
,
27
,
54
,
56
]
.
While improving the accuracy of approaches may be an important factor for trusting models, models are imperfect and will inevitably produce some incorrect answers.
In many scenarios, there is a price associated with a model giving an inaccurate answer as it may mislead the user and cause them to make a mistake that could be anywhere from mildly inconvenient to very serious.
This is especially true for the example of helping users with visual impairments, since they likely do not have a method of verifying the outputs themselves.
Figure 1
:
In the standard VQA problem, a model must answer all questions, even if it is likely to produce errors that could mislead a user, e.g., (a). A reliable VQA model, on the other hand, operates at
low risk
by having the option to abstain from answering if uncertain. In (b), at 1% risk of error, a SoTA model
[
69
]
can answer only
∼
\sim
7% of questions when using vanilla model probabilities to choose when to abstain. Using a learned, multimodal selection function to estimate confidences can more than double the amount of questions answered, yet there remains much room for improvement (best possible, i.e., perfect abstention).
One way to avoid providing incorrect information and misleading users is to
abstain
from making a prediction, as in the framework of selective prediction
[
14
,
20
,
23
,
24
]
.
Consider Fig.
1
(a): when a model is correct, we naturally would like it to give us an answer. However, when it is unable to do so (e.g., cannot “read” the brand name) or is very uncertain, in many application we may prefer if the model communicated “
I don’t know
”, i.e., abstain
[
30
,
44
]
.
We say that VQA models are reliable, if they make highly accurate predictions when they choose to answer.
Ideally, reliable models should also abstain as little as possible to be effective.
Although reliability is often critical for the usage of VQA in real settings, this aspect has not received direct attention in the VQA literature aside from efforts to recognize difficult, unanswerable, or false premise questions
[
12
,
29
,
40
,
64
,
75
]
.
Also, past efforts on selective prediction have not focused on the multimodal setting, where both an image and a question can be valid or in-distribution when considered independently, yet challenging in tandem.
In this work, we formalize and explore the notion of reliability in VQA.
We propose to frame the task as a selective prediction problem
[
14
,
20
]
in which models must either predict an answer or abstain from answering.
This requires two techniques that have not been widely explored for VQA models: (1) gauging uncertainty of predictions and (2) learning when to abstain.
To operationalize this framework, we measure performance with
coverage
(how many questions are answered) and
risk
(the error on these questions)
[
20
,
42
]
.
While low risk and high coverage are the goal, in practice there often is a trade-off between the two.
To provide a scalar measure that captures this trade-off and allows for clearer model comparisons, we introduce a new
Effective Reliability
metric, which accounts for abstention while also introducing a cost for giving an incorrect answer.
This also provides an alternative evaluation for domains where it may be more intuitive to specify the penalty for an individual error instead of a bound on risk.
Under this framework, we first show that existing VQA approaches leave much room for improvement.
In particular, we demonstrate that, for a number of models, the common approach of using the maximum probability to determine abstention
[
33
,
42
]
(by thresholding the softmax scores) limits the model to answering a small fraction of questions with a low risk of error (e.g., answering less than 8% of questions at 1% risk of error), despite having high standard VQA accuracy.
This inability to answer a larger number of questions at low risk indicates low utility of the existing VQA models.
To address this, we explore two other approaches: calibration and training a multimodal selection function.
We find that calibration often leads to a better risk-coverage trade-off compared to using the original model probabilities.
We improve beyond this by training a multimodal selection function that can better learn to predict if a the model’s answer is correct, based on intermediate representations as well as the answer from the VQA model.
This selection function consistently improves the coverage of different VQA models across varying risks of error, particularly for low levels of risk.
However, we show that there is still room to improve the effectiveness of these models (see Fig.
1
(b)). Finally, we evaluate VQA models with our new Effective Reliability metric, and see that it correlates with risk and coverage in a meaningful way – the user-defined cost of an error impacts the risk at which the model operates.
In summary, our contributions are: (1) we are the first to analyze and operationalize reliability for multimodal VQA models; (2) we expose the issue of low coverage in VQA models when asked to operate at low risk levels; (3) we explore several methods for incorporating abstention, showing that a simple yet effective multimodal selection function outperforms other methods; (4) we propose a novel
Effective Reliability
metric for this problem, establishing a new benchmark for effective and reliable VQA models.
2
Related Work
VQA methods.
VQA is a popular task with a plethora of methods proposed in recent years
[
2
,
5
,
11
,
21
,
22
,
37
,
38
,
49
,
51
,
53
,
69
,
83
,
84
,
85
]
.
To the best of our knowledge, there are no VQA models with a built-in abstention mechanism (i.e., they predict an answer for every image and question pair). We discuss a few exceptions with non-standard problem statements in the following.
Our work analyzes VQA models’ reliability by introducing the ability to abstain into several prominent VQA models
[
38
,
49
,
53
,
69
]
.
Detecting intrinsic difficulty.
Some prior work on VQA involves the categorization and detection of questions that are intrinsically difficult to answer, regardless of model ability.
For example, the VizWiz VQA dataset contains labels for questions which are unanswerable
[
29
]
and reasons for annotation entropy, such as low image quality or question ambiguity
[
7
]
.
[
16
]
define a similar categorization of unanswerable questions in VQA.
[
75
]
compute precision/recall based on VQA model confidences and show that these can be reflective of the ambiguities of the ground truth answers.
Other work focuses on detecting whether the question incorrectly describes the visual semantics
[
40
,
50
,
55
,
64
]
.
Identifying intrinsically difficult examples has important implications in active learning, where such examples can stifle the ability of different methods to select useful examples to train on
[
43
]
.
In this work, we focus on predicting uncertainty specific to a model as opposed to the intrinsic difficulty from data itself.
However, in Sec.
5.5
, we find that a subset of questions on which a model abstains from answering are ambiguous or unanswerable.
Calibration.
In classification settings, calibration typically refers to probabilistic calibration, where the predicted confidence for a given class should be representative of the probability of the prediction being correct
[
28
,
33
,
48
,
59
,
61
]
.
One popular parametric method is Platt scaling
[
61
]
, in which a logistic regression model is trained on classifier outputs on the validation set to return calibrated probabilities.
In our work, we explore the effectiveness of vector scaling, a multi-class extension of Platt scaling, for improving selective prediction performance.
Selective prediction.
This refers to when models have the option to abstain from providing a prediction. It is also known as sample rejection
[
13
,
14
]
or selective classification
[
20
]
.
[
17
,
36
,
77
]
propose various related evaluation metrics.
[
17
]
assigns cost coefficients to misclassified, abstained, and correctly classified samples. Concurrently with our work,
[
77
]
defines reliability as out-of-the-box performance for large-scale pretrained models across many unimodal vision or language tasks, including selective prediction.
Other works integrate abstention in multi-stage networks or ensembles
[
8
,
15
,
45
,
62
,
80
]
.
[
39
,
82
]
study selective prediction and transformer uncertainty within NLP tasks.
[
26
,
42
,
78
]
explore selective prediction performance on out-of-distribution data.
[
42
]
focuses on selective prediction for text-based question answering.
However, they show that their method does not generalize to questions from the same domain which are intrinsically unanswerable, whereas this represents an important portion of difficult VQA samples.
[
23
,
24
]
optimize selective models for specific coverage levels in image classification.
We explore learned selection functions, but in the multimodal VQA setting, where the complex interaction between modalities must be modeled and more than one output may be considered correct to varying degrees.
In the multimodal space,
[
32
]
addresses gender bias in image captioning, where the model can “abstain” by predicting gender-neutral words when it is uncertain.
With our proposed metric, the cost of error (e.g., misclassifying gender) can be user-defined and potentially be made class-specific.
3
Visual Question Answering with Abstention
Visual question answering is currently formulated and evaluated in the literature
[
5
,
25
,
29
,
34
]
as
always
predicting an answer from the answer space,
𝒜
\mathcal{A}
, annotated in the dataset.
So, a model
f
:
𝒳
↦
𝒜
f:\mathcal{X}\mapsto\mathcal{A}
predicts an answer
a
∈
𝒜
a\in\mathcal{A}
for each input
x
=
(
v
,
q
)
∈
𝒳
x=(v,q)\in\mathcal{X}
, with image
v
v
and question
q
q
.
This problem formulation forces the model to answer even if it is likely wrong, thus providing unreliable answers.
To address this, we propose to extend the VQA problem formulation so that a model is given the option to
abstain
from answering a question (i.e., effectively saying “
I don’t know
”).
Outside VQA, this formulation has also been referred to as “
classification with a reject option
”
[
13
,
17
,
24
,
30
,
62
]
or “
selective prediction/classification
”
[
20
,
23
]
.
We first discuss the problem definition in Sec.
3.1
, and then the metrics to evaluate this problem in Sec.
3.2
.
3.1
Problem Definition
We extend the standard VQA formulation to the setting where a model can either provide an answer from
𝒜
\mathcal{A}
or choose to abstain (denoted by
∅
\emptyset
):
h
:
𝒳
↦
𝒜
∪
{
∅
}
h:\mathcal{X}\mapsto\mathcal{A}\cup\{\emptyset\}
.
We refer to
h
h
as a
selective model
.
One way to formulate and achieve this is by decomposing
h
h
into two functions,
f
f
and
g
g
, which jointly comprise a selective model
[
20
,
23
,
24
]
.
f
f
denotes the VQA model that predicts answers and
g
:
𝒳
↦
{
0
,
1
}
g:\mathcal{X}\mapsto\{0,1\}
is the selection function that determines whether the model answers or abstains from answering:
h
⁡
(
x
)
=
(
f
,
g
)
​
(
x
)
=
{
f
⁡
(
x
)
if
​
g
​
(
x
)
=
1
,
∅
if
​
g
​
(
x
)
=
0
.
h(x)=(f,g)(x)=\begin{cases}f(x)&\text{if}\ g(x)=1,\\
\emptyset&\text{if}\ g(x)=0.\\
\end{cases}
(1)
Given an input
x
x
, the selective model yields an output from
f
f
when the selection function predicts that an answer should be given, or abstains if the selection function predicts that the model should not answer.
One straightforward way to formulate the selection function
g
g
is based on a threshold
γ
\gamma
, where the function
g
′
:
𝒳
↦
[
0
,
1
]
g^{\prime}:\mathcal{X}\mapsto[0,1]
predicts a confidence in the correctness
2
2
2
While we define the output space of
g
′
g^{\prime}
as
[
0
,
1
]
[0,1]
as is the case for the common softmax, one can similarly define an output space which covers, e.g., all real values
ℝ
\mathbb{R}
.
of the model
f
⁡
(
x
)
f(x)
[
42
]
:
g
⁡
(
x
)
=
{
1
if
​
g
′
​
(
x
)
≥
γ
,
0
if
​
g
′
​
(
x
)
<
γ
.
g(x)=\begin{cases}1&\text{if}\ g^{\prime}(x)\geq\gamma,\\
0&\text{if}\ g^{\prime}(x)<\gamma.\\
\end{cases}
(2)
In general, a good function
g
′
​
(
x
)
g^{\prime}(x)
for abstention should yield high values when
f
⁡
(
x
)
f(x)
is correct and low values when it is incorrect. In Sec.
4
, we will further discuss how to define
g
′
​
(
x
)
g^{\prime}(x)
.
3.2
Evaluation Metrics
To evaluate a VQA model with an ability to abstain, we consider two types of evaluation and discuss how we adapt them for VQA: first,
coverage
and
risk
[
20
]
and, second, a cost-based metric for balancing the two.
Risk and Coverage.
Coverage
is the portion of questions that the model opted to answer, while
risk
is the error on that portion of questions
[
20
]
.
Ideally, a reliable model should exhibit high coverage at low levels of risk, meaning it answers many questions with high accuracy and abstains on others.
Concretely, coverage for dataset
𝒟
\mathcal{D}
with inputs
x
i
x_{i}
and ground truth answers
y
i
y_{i}
is given by:
𝒞
⁡
(
g
)
=
1
|
𝒟
|
​
∑
(
x
i
,
y
i
)
∈
𝒟
g
⁡
(
x
i
)
,
\mathcal{C}(g)=\frac{1}{|\mathcal{D}|}\sum_{(x_{i},y_{i})\in\mathcal{D}}g(x_{i}),
(3)
and risk is defined as:
ℛ
⁡
(
f
,
g
)
=
1
|
𝒟
|
​
∑
(
x
i
,
y
i
)
∈
𝒟
ℓ
⁡
(
f
⁡
(
x
i
)
,
y
i
)
⋅
g
⁡
(
x
i
)
𝒞
⁡
(
g
)
,
\mathcal{R}(f,g)=\frac{\frac{1}{|\mathcal{D}|}\sum_{(x_{i},y_{i})\in\mathcal{D}}\ell(f(x_{i}),y_{i})\cdot g(x_{i})}{\mathcal{C}(g)},
(4)
where
ℓ
\ell
is a cost function that measures the error between the predicted answer
f
⁡
(
x
i
)
f(x_{i})
and the corresponding ground truth answer
y
i
y_{i}
.
Assuming
g
g
follows Eq.
2
, if the threshold
γ
\gamma
decreases, coverage will increase, but risk will increase as well.
Hence, there is a risk-coverage trade-off that models can aim to optimize.
Applying this to VQA, the composite function
(
f
,
g
)
(f,g)
becomes our selective VQA model, where
f
f
produces an answer and
g
g
decides whether to abstain.
However, the open-ended nature of the VQA task requires careful consideration for designing the risk-coverage metrics.
A given question might have multiple possible answers which could all be considered correct to varying degrees.
As a result, the error for a prediction on a given input is not necessarily binary.
When calculating risk, we must use a cost function that accurately represents this multi-class nature.
We follow
[
5
]
to define VQA accuracy for a given model answer
f
⁡
(
x
)
f(x)
as
A
​
c
​
c
​
(
f
⁡
(
x
)
,
y
)
=
min
⁡
(
# annotations that match
​
f
​
(
x
)
3
,
1
)
Acc(f(x),y)=\min\left(\frac{\text{\# annotations that match }f(x)}{3},1\right)
and average these accuracies over all 10 choose 9 subsets of human annotated answers for the input question, similar to other VQA evaluations
[
25
,
29
,
72
]
.
Under this, an answer is considered fully correct if it matches at least four of the human annotations, and receives partial credit for predicting an answer with one, two, or three humans in agreement.
Thus, our risk measurement becomes:
ℛ
⁡
(
f
,
g
)
=
1
|
𝒟
|
​
∑
(
x
i
,
y
i
)
∈
𝒟
(
1
−
A
​
c
​
c
​
(
f
⁡
(
x
i
)
,
y
i
)
)
⋅
g
⁡
(
x
i
)
𝒞
⁡
(
g
)
.
\mathcal{R}(f,g)=\frac{\frac{1}{|\mathcal{D}|}\sum_{(x_{i},y_{i})\in\mathcal{D}}(1-Acc(f(x_{i}),y_{i}))\cdot g(x_{i})}{\mathcal{C}(g)}.
(5)
In practice, the level of risk in model predictions that a user is willing to tolerate depends highly on the scenario.
Therefore, we evaluate by computing coverage at a range of risk levels (
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
), such as coverage at 1% or 10% risk.
We can also summarize this over the distribution of risk levels by plotting coverage versus corresponding risk, and computing the area under this risk-coverage curve (AUC)
[
42
]
.
Moreover, for an evaluation that controls for how the threshold
γ
\gamma
for
g
g
is chosen, we compute the maximum coverage for each risk level, allowing for a more direct comparison of the selection function design.
Effective Reliability.
Recall the trade-off between risk and coverage: a standard VQA model may have high risk at 100% coverage, but a reliable model may have low risk yet abstain on a large portion of questions (see Fig.
1
(b)).
In practice, for a model to be reliable and effective, it should ideally achieve both low risk and high coverage.
To jointly measure these two desirable qualities, we define a metric which assigns a reward to questions that are answered correctly, a penalty to those answered entirely incorrectly, and zero reward to those abstained on.
We refer to this as
Effective Reliability
, or
Φ
c
\Phi_{c}
for a given penalty
c
c
, inspired by the “effectiveness function” introduced by
[
17
]
.
Formally, we define Effective Reliability for an input
x
x
as
Φ
c
​
(
x
)
\Phi_{c}(x)
(Eq.
6
), where
c
c
is the cost for answering incorrectly,
g
g
is the selection function, and
A
​
c
​
c
Acc
is a measure of a model’s correctness.
In this case,
A
​
c
​
c
Acc
is the VQA accuracy
[
5
]
.
Φ
c
​
(
x
)
=
{
A
​
c
​
c
​
(
x
)
if
​
g
​
(
x
)
=
1
​
and
​
A
​
c
​
c
​
(
x
)
>
0
,
−
c
if
​
g
​
(
x
)
=
1
​
and
​
A
​
c
​
c
​
(
x
)
=
0
,
0
if
​
g
​
(
x
)
=
0
.
\Phi_{c}(x)=\begin{cases}Acc(x)&\text{if}\ g(x)=1\ \text{and}\ Acc(x)>0,\\
-c&\text{if}\ g(x)=1\ \text{and}\ Acc(x)=0,\\
0&\text{if}\ g(x)=0.\end{cases}
(6)
We define the total score
Φ
c
=
1
n
​
∑
x
Φ
c
​
(
x
)
\Phi_{c}=\frac{1}{n}\sum_{x}\Phi_{c}(x)
, a mean over all
n
n
samples
x
x
.
This formulation assigns a reward to answers which are at least partially correct (i.e.,
A
​
c
​
c
​
(
x
)
>
0
Acc(x)>0
) – an important property of the VQA accuracy, where the correctness of answers can vary based on the number of human annotators in agreement. The choice of
c
c
depends on the deployment-specific cost of providing an incorrect answer. In Sec.
5.3
, we report
Φ
c
\Phi_{c}
with cost values of 1, 10, and 100 (
Φ
1
\Phi_{1}
,
Φ
10
\Phi_{10}
,
Φ
100
\Phi_{100}
).
While
[
17
]
suggest setting
Φ
c
​
(
x
)
<
0
\Phi_{c}(x)<0
for
g
⁡
(
x
)
=
0
g(x)=0
, we set
Φ
c
​
(
x
)
=
0
\Phi_{c}(x)=0
(i.e., a score of 0 when abstaining).
This enables our formulation to have the clear upper bound for models which abstain perfectly (Lemma
1
).
We provide a simple proof for this in Appendix
0.K
.
It is also confirmed in our experiments in Tab.
2
.
Lemma 1
The Effective Reliability score is equal to the VQA Accuracy (
Φ
c
​
(
x
)
=
A
​
c
​
c
​
(
x
)
\Phi_{c}(x)=Acc(x)
) if a model abstains (
g
⁡
(
x
)
=
0
g(x)=0
)
iff
it is incorrect (
A
​
c
​
c
​
(
x
)
=
0
Acc(x)=0
).
In our experiments, we choose a threshold
γ
\gamma
which optimizes
Φ
c
\Phi_{c}
on a validation set to compute a model’s Effective Reliability with the form of the selection function
g
g
defined in Eq.
2
.
Additionally, the Effective Reliability score
Φ
c
\Phi_{c}
can be evaluated for any model, even those which do not incorporate the option to abstain from providing a prediction (i.e.,
g
⁡
(
x
)
g(x)
is always 1).
Beyond its connection to VQA Accuracy (Lemma
1
), Effective Reliability has several other advantages.
We show that it meaningfully correlates with risk-coverage (Tab.
2
), yet provides a single metric to compare models.
This offers simpler comparisons that can be used to rank approaches (e.g., evaluating on a challenge server).
It also provides an alternative evaluation for settings where it may be easier or more intuitive to define a cost for an incorrect answer as opposed to a target level of risk.
4
Selection Functions
We investigate three promising directions to extend VQA models to abstain by exploring different options for
g
′
​
(
x
)
g^{\prime}(x)
introduced in Sec.
3.1
.
Additional implementation details for the selection functions can be found in Appendix
0.I.2
.
MaxProb.
Without any additional training, a model can be extended to abstain by defining
g
′
g^{\prime}
as the softmax probability of the model’s predicted class (i.e., maximum probability) and is thus refered to as MaxProb
[
33
,
42
,
48
]
.
Essentially, MaxProb trusts that if the model gives a high probability to one class, it is quite certain that the answer is correct and should be given:
g
MaxProb
′
​
(
x
)
=
max
⁡
(
f
′
​
(
x
)
)
g^{\prime}_{\text{MaxProb}}(x)=\max(f^{\prime}(x))
, where
f
′
​
(
x
)
f^{\prime}(x)
represents the answer probabilities.
Calibration.
Calibration techniques tune the absolute confidence values
[
61
]
to make the predicted probability for an output representative of the likelihood of that output being correct.
Selective prediction has more to do with relative confidence rankings
[
20
]
, but, nevertheless, a poorly calibrated model might also imply poor confidence rankings
[
42
]
.
Temperature scaling
[
28
,
61
]
is a popular calibration method, but it does not change the confidence rankings between examples and has no effect on the risk-coverage curve.
Thus, we do not consider it in this work, but instead use vector scaling
[
28
,
61
]
to calibrate the model logits.
We then apply MaxProb on top of these calibrated logits.
Appendix
0.G
has evaluations of how well the scores are calibrated.
Multimodal selection function: Selector.
Vector scaling essentially trains an additional component on top of the VQA model to refine the model confidences.
We move beyond this by training a component (Selector) to predict whether the answer is correct
[
19
,
42
,
61
]
.
Different from prior work on confidence estimation in other tasks
[
19
,
24
,
42
,
80
]
, the multimodal nature of VQA presents unique challenges where the model must consider the interaction between the image, question, and answer.
To model this, we extract the image
v
v
, question
q
q
, multimodal
r
r
, and answer
f
′
​
(
x
)
f^{\prime}(x)
representations from the VQA model and input these to the Selector, which gives it access to representations of both the answer itself as well as the evidence on which the answer is based.
The Selector is a multi-layered perceptron that takes these representations as input and predicts the correctness of an answer with respect to the image-question pair.
To train this component, the simplest method may be to treat this as a binary classification problem (correct or incorrect).
However, this does not account for answers that may be partially correct, or where one answer may be more correct than another, as is the case with VQA.
Therefore, we propose to treat correctness prediction as a regression task where the target value is the VQA accuracy, allowing us to scale confidence scores with correctness.
5
Experiments
5.1
Data and Models
We experiment on the VQA v2 dataset
[
25
]
and require annotations for evaluation.
As annotations for the test-dev and test-std sets of VQA v2 are not publicly available, we use questions from the official validation split for our evaluation as is common
[
1
,
67
,
81
]
.
As a reminder, under our selective prediction setup, the VQA model is the function
f
f
, the selection function is
g
g
, and the composition of the two form a selective model
h
h
.
We train the VQA models (
f
f
) on the training set of VQA v2.
Meanwhile, we split the 214k examples in the VQA v2 validation set into three subsets: a split with 86k examples (40%) for validating VQA models as well as training selection functions (
g
g
), another with 22k examples (10%) for validating the selection functions, and a held out test split of 106k examples (50%) that we use strictly for evaluating the full models (
h
h
).
We benchmark the selection functions introduced in Sec.
4
in combination with VQA models with varying architectures and performance (test-std VQA v2 accuracy in parentheses):
Pythia
[
38
]
(70.24%), an optimization of the widely used bottom-up top-down VQA model
[
2
]
;
ViLBERT
[
53
]
(70.92%), a two-stream transformer, and
VisualBERT
[
49
]
(71.00%), a single-stream transformer, both of which use multimodal pretraining
[
71
]
;
CLIP-ViL
[
69
]
(74.17%), which is the MoVie+MCAN
[
58
]
model with a visual encoder from CLIP
[
63
]
.
In Tab.
1
, Tab.
2
, and Fig.
2
, we report mean results over 10 random seeds for Pythia and CLIP-ViL (standard deviations in Appendix
0.J
), while we report single runs for ViLBERT and VisualBERT using existing pretrained and fine-tuned models.
All other results are single runs from the same randomly chosen seed.
Details of data and model setups are in Appendix
0.H
and Appendix
0.I
.
5.2
Benchmarking Risk and Coverage
Model
f
f
Selection
VQA
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
↑
\uparrow
AUC
↓
\downarrow
function
g
g
Acc.
↑
\uparrow
ℛ
=
1
%
\mathcal{R}=1\%
ℛ
=
5
%
\mathcal{R}=5\%
ℛ
=
10
%
\mathcal{R}=10\%
ℛ
=
20
%
\mathcal{R}=20\%
Pythia
[
38
]
MaxProb
66.17
6.00
24.71
40.99
71.45
13.88
Calibration
66.45
6.50
25.07
41.95
73.44
13.52
Selector
66.17
8.79
26.92
43.24
73.40
13.30
Best Possible (
𝒞
\mathcal{C}
)
66.17
62.67
68.41
73.52
82.71
6.68
ViLBERT
[
53
]
MaxProb
69.20
7.51
29.01
47.99
79.89
11.78
Calibration
69.16
10.07
30.15
48.75
79.96
11.62
Selector
69.20
11.82
32.44
50.20
79.97
11.31
Best Possible (
𝒞
\mathcal{C}
)
69.20
65.66
71.67
76.89
86.50
5.49
VisualBERT
[
49
]
MaxProb
70.18
6.85
30.78
50.46
81.78
11.21
Calibration
70.02
9.78
32.09
51.14
81.92
11.21
Selector
70.18
11.47
34.14
52.53
82.04
10.75
Best Possible (
𝒞
\mathcal{C}
)
70.18
66.70
72.76
77.98
87.73
5.13
CLIP-ViL
[
69
]
MaxProb
71.75
6.78
34.69
55.72
85.13
10.23
Calibration
71.71
13.12
37.06
56.06
85.23
9.91
Selector
71.75
16.34
39.48
58.16
85.37
9.52
Best Possible (
𝒞
\mathcal{C}
)
71.75
68.49
74.55
79.72
89.69
4.58
Table 1
:
Risk-coverage metrics for different selection functions. For coverage at risk (
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
) and VQA Acc., higher is better. For AUC, lower is better. All in
%
\%
.
As discussed in Sec.
3.2
, we measure the maximum coverage for a given risk (
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
) as well as AUC for the risk-coverage curves and overall accuracy for each model.
We include the best possible performance on these metrics for each model, which would be a selective model that abstains only when the prediction is incorrect.
Results are reported on the test test.
Selector outperforms other methods.
From Tab.
1
, we see that adding the Selector consistently outperforms MaxProb in coverage for all risk tolerances as well as AUC.
The strongest improvements occur at lower risk tolerances (e.g., 1% and 5%), becoming smaller as the tolerance increases (e.g., 10% and 20%).
Notably, CLIP-ViL with Selector can improve
𝒞
​
@
\mathcal{C}@
1% to 2.4
×
\times
that of CLIP-ViL with MaxProb.
Fig.
2
illustrates how, for low risk levels, the addition of the selector maintains noticeably better risk as coverage increases compared to MaxProb.
It generally appears that the more accurate a model is overall, the more it may potentially improve in coverage at low risk tolerances when using Selector.
For instance, when adding the Selector, we observe the largest improvements in
𝒞
​
@
\mathcal{C}@
1% and
𝒞
​
@
\mathcal{C}@
5% with CLIP-ViL (9.56% and 4.79%, respectively), which also has the highest accuracy.
Meanwhile, Pythia has the lowest accuracy and exhibits the smallest improvements with the Selector at these tolerances (2.79% and 2.21%, respectively).
Fig.
2
depicts this between 0-5% risk, where the gap between MaxProb and Selector appears to widen as we move to more accurate models (left to right).
Lastly, we observe that Calibration can improve coverage beyond MaxProb as well, but largely less so than the Selector, especially at low risk tolerances (e.g., 1%, 5%), and not as consistently.
Because Calibration modifies the output logits, it also slightly changes model accuracy.
Figure 2
:
Risk-coverage plots for each model up to 5% risk.
Better accuracy
⇏
\nRightarrow
better coverage at low risk.
While accuracy appears to positively correlate with a better risk-coverage trade-off, the results in Tab.
1
also imply that higher accuracy does not guarantee better coverage at low risk.
For example, CLIP-ViL has 2.55% higher accuracy than ViLBERT, but, with default MaxProb, ViLBERT has 0.73% higher
𝒞
​
@
\mathcal{C}@
1% than CLIP-ViL.
Appendix
0.B
also shows that augmenting the VQA model training data with the selection function training data and using MaxProb still has worse coverage at low risk than when using this data for Selector training, despite having higher accuracy.
These results imply that improving upon the risk-coverage trade-off requires not only building more accurate models but also learning better abstention policies.
Still room for improvement.
Though the evidence presented in Tab.
1
and Fig.
2
show that coverage at different risk tolerances can be improved, these approaches still fall short of the best possible.
For example, in Tab.
1
, the difference in
𝒞
​
@
\mathcal{C}@
1% between each model with Selector and their respective best possibles is still
>
>
50%.
Although achieving the best possible may not be realistic, more work is needed to have reliable models with high accuracy and wide coverage that shrink this gap further.
Thresholds generalize to test-time.
Thus far, we have evaluated the maximum coverage at an exact risk level.
In practice, however, a threshold
γ
\gamma
must be chosen, e.g., on a validation set, and used at test-time.
We evaluate how close the actual test-time risk is to the target risk when using the validation threshold with VisualBERT, with results in Appendix
0.F
.
We find relatively small differences in risk, showing that the thresholds generalize reasonably well.
This aligns with prior findings on other tasks
[
24
]
.
However, since the actual risks are now slightly different between models, we can no longer compare the corresponding coverages directly.
This motivates Effective Reliability, which compares models based on a predefined cost for wrong answers as opposed to an exact risk level.
5.3
Effective Reliability
Model
f
f
Selection
c
c
=1
c
c
=10
c
c
=100
function
g
g
Φ
1
\Phi_{1}
↑
\uparrow
ℛ
\mathcal{R}
↓
\downarrow
𝒞
\mathcal{C}
↑
\uparrow
Φ
10
\Phi_{10}
↑
\uparrow
ℛ
\mathcal{R}
↓
\downarrow
𝒞
\mathcal{C}
↑
\uparrow
Φ
100
\Phi_{100}
↑
\uparrow
ℛ
\mathcal{R}
↓
\downarrow
𝒞
\mathcal{C}
↑
\uparrow
Pythia
[
38
]
—
38.49
33.83
100
-210.62
33.83
100
−
-
2701.68
33.83
100
MaxProb
47.28
21.62
76.03
15.15
5.24
25.62
2.27
0.85
4.89
Calibration
48.06
21.21
76.18
15.23
5.85
28.06
2.19
0.94
5.88
Selector
48.16
20.67
74.84
17.12
5.99
30.16
3.84
0.94
8.23
Best Possible (
Φ
c
\Phi_{c}
)
66.17
8.51
72.32
66.17
8.51
72.32
66.17
8.51
72.32
ViLBERT
[
53
]
—
44.57
30.80
100
−
-
177.05
30.80
100
−
-
2393.23
30.80
100
MaxProb
52.41
20.01
79.92
18.00
6.26
34.50
1.67
1.33
10.18
Calibration
52.51
19.53
78.93
18.29
6.10
34.24
2.92
1.12
10.47
Selector
52.65
19.37
78.60
21.02
5.56
34.57
5.41
0.90
11.06
Best Possible (
Φ
c
\Phi_{c}
)
69.20
8.20
75.38
69.20
8.20
75.38
69.20
8.20
75.38
VisualBERT
[
49
]
—
46.49
29.82
100
−
-
166.77
29.82
100
−
-
2299.33
29.82
100
MaxProb
53.72
19.09
79.83
19.29
5.63
33.64
2.49
1.02
6.89
Calibration
53.80
19.07
79.84
19.96
5.57
34.37
3.83
0.87
8.42
Selector
54.12
18.72
79.34
22.04
5.13
34.61
4.82
1.00
11.34
Best Possible (
Φ
c
\Phi_{c}
)
70.18
8.02
76.30
70.18
8.02
76.30
70.18
8.02
70.18
CLIP-ViL
[
69
]
—
49.41
28.25
100
-151.70
28.25
100
-2162.80
28.25
100
MaxProb
55.82
19.22
83.45
22.03
5.59
37.67
2.85
0.96
6.97
Calibration
56.03
18.30
81.61
23.24
4.95
36.82
5.30
0.73
9.97
Selector
56.45
17.44
80.09
26.06
5.03
39.59
8.01
0.55
11.38
Best Possible (
Φ
c
\Phi_{c}
)
71.75
7.60
77.66
71.75
7.60
77.66
71.75
7.60
77.66
Table 2
:
Effective Reliability
Φ
c
\Phi_{c}
for VQA models with and without abstention options. The best possible
Φ
c
\Phi_{c}
is computed by only selecting correct predictions, and is equal to the model’s VQA accuracy. All in %.
We evaluate Effective Reliability (
Φ
c
\Phi_{c}
) defined in Sec.
3.1
, which assigns a cost to incorrect predictions, a reward to correct predictions, and zero to questions on which a model abstained from answering.
This provides a single measure to jointly consider reliability (i.e., low risk) and effectiveness (i.e., high coverage).
In Tab.
2
, we choose cost values
c
c
of 1, 10, and 100, to observe how models compare when the consequences for providing an incorrect prediction become high.
Additionally, we can now directly compare to the original VQA formulation, where models do not have an option to abstain, denoted by a null selection function
g
g
. We also include
Φ
c
\Phi_{c}
for the best possible
g
g
, where a model abstains exactly on those inputs which would result in incorrect predictions. As discussed in Sec.
3.1
, this is equivalent to the model accuracy. Results are reported on the test set, with an abstention threshold selected to optimize
Φ
c
\Phi_{c}
on the validation set. We include the corresponding risk and coverage for the selected threshold.
Selector still outperforms other methods.
The Selector produces the highest Effective Reliability scores across all models and cost levels.
As the penalty for wrong answers increases, the gap between the performance of Selector and the next best model generally increases as well.
For example, the improvement of Selector over MaxProb for ViLBERT is 0.24% for
Φ
1
\Phi_{1}
, yet it is 3.74% for
Φ
100
\Phi_{100}
.
Further, the gap between Selector and MaxProb for
Φ
100
\Phi_{100}
generally increases as the VQA model itself has higher accuracy (or best possible performance).
We observe a similar effect in Fig.
2
, where more accurate models have larger gaps in risk between Selector and MaxProb at a given coverage.
Cost implicitly controls risk and coverage.
When the penalty for a wrong answer is high, one might expect a selective model to operate in the low-risk regime.
This is indeed reflected in Tab.
2
, where the range of risk levels for selective models at
Φ
100
\Phi_{100}
(
ℛ
≈
\mathcal{R}\approx
0.5–1.3%) is much lower than the range of risk at
Φ
1
\Phi_{1}
(
ℛ
≈
\mathcal{R}\approx
17–22%).
This directly translates to a similar trend in coverage, where selective models answer about 5–11% of questions at
Φ
100
\Phi_{100}
, and about 76–83% of questions at
Φ
1
\Phi_{1}
. This shows that Effective Reliability behaves intuitively around the influence of a user-selected cost on model risk and coverage.
Human evaluation shows noise has little effect even with high cost values.
For high costs (e.g.,
c
=
100
c=100
), models are strongly penalized for producing incorrect predictions.
Given these strict penalties on errors, it becomes pertinent to ask to what degree noise in the annotations might be contributing to these penalties, though the potential impact of noise is certainly not unique to our evaluations and is a challenging problem in VQA
[
5
,
41
,
68
]
.
To see if our results for
Φ
100
\Phi_{100}
are significantly affected by annotation noise, in Appendix
0.C
, we manually examine each sample where the model predictions were marked incorrect (and thus heavily penalized when computing
Φ
100
\Phi_{100}
).
We annotate cases where models may have been unfairly penalized and recompute
Φ
100
\Phi_{100}
when removing this penalty.
We find that vast majority of incorrect predictions that contribute to these penalties are properly marked as incorrect.
We also see that label noise does slightly change the Effective Reliability scores at high cost, but the rankings between models and selection functions are preserved.
All models without an abstention option perform poorly.
When the cost of a wrong answer is equal to the reward of getting an answer entirely correct (
c
=
1
c=1
), all models without a selection function
g
g
underperform their selective model counterparts. As
c
c
increases, this gap widens dramatically, with non-abstaining models reaching
Φ
c
\Phi_{c}
values firmly in the negative range.
Meanwhile, all selective models reach a positive
Φ
c
\Phi_{c}
, even at high cost, illustrating the necessity of the abstention option for building models which are reliable and effective.
5.4
Selection Function Ablations
Features
Unimodal
Loss
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
↑
\uparrow
AUC
↓
\downarrow
Φ
c
\Phi_{c}
↑
\uparrow
ℛ
=
1
%
\mathcal{R}=1\%
ℛ
=
5
%
\mathcal{R}=5\%
ℛ
=
10
%
\mathcal{R}=10\%
ℛ
=
20
%
\mathcal{R}=20\%
c
c
=1
c
c
=10
c
c
=100
v
~
\tilde{v}
✓
Regression
0.00
0.00
0.00
16.09
23.23
48.83
0.00
0.00
q
q
✓
Regression
0.02
11.03
35.88
79.70
13.39
52.99
10.36
1.33
f
′
​
(
x
)
f^{\prime}(x)
Regression
5.24
36.10
56.30
84.79
10.08
56.03
23.14
5.88
v
v
Regression
11.60
36.43
53.74
83.51
10.32
54.84
23.91
6.10
r
r
Regression
13.42
34.69
53.90
82.95
10.43
54.35
22.34
7.77
f
′
​
(
x
)
f^{\prime}(x)
+
v
~
\tilde{v}
Regression
3.67
36.40
56.33
84.79
10.07
55.97
23.63
4.60
f
′
​
(
x
)
f^{\prime}(x)
+
q
q
Regression
10.67
37.41
56.95
84.76
9.86
56.01
24.35
5.32
f
′
​
(
x
)
f^{\prime}(x)
+
r
r
Regression
12.02
37.44
57.68
84.93
9.81
56.07
24.28
5.51
f
′
​
(
x
)
f^{\prime}(x)
+
v
v
Regression
13.24
38.51
57.44
84.92
9.76
56.20
25.11
7.03
f
′
​
(
x
)
f^{\prime}(x)
+
q
q
+
v
v
+
r
r
Classification
6.64
35.80
57.29
84.18
10.06
55.61
23.23
4.36
f
′
​
(
x
)
f^{\prime}(x)
+
q
q
+
v
v
+
r
r
Regression
13.32
38.02
58.16
85.03
9.73
56.09
24.85
7.32
Table 3
:
Ablations of Selector with CLIP-ViL
[
69
]
on our selection function validation set. The overall best performance is in bold and second best is underlined.
f
′
​
(
x
)
f^{\prime}(x)
,
q
q
,
v
~
\tilde{v}
, and
r
r
are the answer, question, image, and multimodal representations, respectively. Note,
v
v
is a question conditioned image representation that is not unimodal (see Appendix
0.A
for details). All in %.
Tab.
3
provides ablations for the selection function design.
In the following, we distill the main observations.
Additional discussion is in Appendix
0.A
.
Selector requires multimodal input.
Tab.
3
shows the importance of using multimodal information for coverage at low risk levels.
When using each representation in isolation, we see that multimodal representations (
r
r
,
v
v
, and
f
′
​
(
x
)
f^{\prime}(x)
) yield much stronger
𝒞
​
@
\mathcal{C}@
1%,
𝒞
​
@
\mathcal{C}@
5%,
Φ
10
\Phi_{10}
, and
Φ
100
\Phi_{100}
than unimodal representations (image
v
~
\tilde{v}
or question
q
q
).
For highly reliable models (
𝒞
​
@
\mathcal{C}@
1%,
Φ
100
\Phi_{100}
), unimodal selection functions fail (coverage
≤
\leq
0.02%,
Φ
100
<
2
%
\Phi_{100}<2\%
), suggesting that building reliable and effective VQA models is a truly multimodal problem.
Combining all representations generally performs best, so we use this setup in all experiments.
Regressing to VQA accuracy is important.
We find that formulating the objective as a regression of the answer accuracy, rather than classifying whether the answer is correct, offers significant improvements (Tab.
3
), especially at low risk.
This is likely because predicting the fine-grained accuracy allows the model to account for partially correct answers and learn to rank answers that are more correct higher, as opposed to classification where the distinction between partially correct answers is lost.
Selector Architecture.
Appendix
0.A
presents results using different Selector architectures, where a less complex architecture can degrade performance, but a more complex one does not necessarily improve it.
Together with Tab.
3
, we find that, rather than the network layout, the
input
to the Selector and optimization target are more critical to the performance when using the Selector.
5.5
Qualitative Analysis
Fig.
3
visualizes MaxProb and Selector decisions with CLIP-ViL for several examples on the test set (more in Appendix
0.E
).
The abstention threshold is chosen to maximize
Φ
100
\Phi_{100}
on validation.
Fig.
3
(left) shows an example of a question that requires commonsense reasoning to answer that the VQA model may not be certain of (and gets wrong), so Selector abstains.
Similarly, in Fig.
3
(middle), we see a false premise question
[
64
]
where Selector abstains again as the question does not make sense for the image, while MaxProb yields an incorrect answer.
Fig.
3
(right) presents an example with synonymous answers where the model is correct yet MaxProb chooses to abstain and Selector chooses to answer.
In a classification-based VQA model, synonyms can split the maximum softmax score used by MaxProb, whereas the Selector can potentially learn these answer similarities and adjust the confidence.
These examples contribute to the higher coverage at low risk observed quantitatively in our experiments.
We also find that MaxProb chooses to answer many simple questions, while Selector additionally chooses to answer more difficult, multimodal ones as well (see Appendix
0.D
).
Figure 3
:
Qualitative test set examples with CLIP-ViL selective model predictions.
6
Conclusion
The standard VQA formulation does not include an option for models to abstain from answering if they are uncertain.
However, for many applications, it is important that the model only provides an answer if there is a low risk of error.
In this work, we promote a problem formulation for VQA which includes an option to abstain and discuss how to evaluate this, including a metric that rewards correct predictions but expects models to abstain if they are incorrect.
We benchmark several VQA models in combination with approaches for abstention.
If we want a reliable model with 1% risk of error, we find that a state-of-the-art VQA model
[
69
]
only answers less than 7% of the questions when using its softmax probabilities as estimates of model confidence.
Using calibration can improve this, but we find that the best results are consistently achieved by training a multimodal selection function to estimate correctness directly.
This increases the coverage from 6.78% to 16.34%.
While this is a marked improvement, one has to consider that this model achieves 71.75% standard VQA accuracy on the same set of data.
With our
Effective Reliability
metric, the performance drops from 71.75% (for perfect abstention) to 8.01% (our best abstention baseline) with high penalties for wrong answers.
We believe this new framework and metric for VQA will encourage the community to build VQA models which are both reliable and effective, as well as offer an opportunity for many exciting directions to improve the self-awareness of models.
Acknowledgements:
We thank Anastasios Angelopoulos and Kurt Shuster for helpful discussions. Authors, as part of their affiliation with UC Berkeley, were supported in part by the NSF CISE Expeditions Award CCF-1730628; DoD, including DARPA’s LwLL, PTG, and/or SemaFor programs; the Berkeley Artificial Intelligence Research (BAIR) industrial alliance program as well as gifts from Amazon Web Services, Ant Group, Ericsson, Facebook, Futurewei, Google, Intel, Microsoft, Scotiabank, and VMware.
References
[1]
Agrawal, A., Batra, D., Parikh, D., Kembhavi, A.: Don’t just assume; look and
answer: Overcoming priors for visual question answering. In: CVPR (2018)
[2]
Anderson, P., He, X., Buehler, C., Teney, D., Johnson, M., Gould, S., Zhang,
L.: Bottom-up and top-down attention for image captioning and visual question
answering. In: Proceedings of the IEEE conference on computer vision and
pattern recognition. pp. 6077–6086 (2018)
[3]
Angelopoulos, A.N., Bates, S.: A gentle introduction to conformal prediction
and distribution-free uncertainty quantification. arXiv preprint
arXiv:2107.07511 (2021)
[4]
Angelopoulos, A.N., Bates, S., Candès, E.J., Jordan, M.I., Lei, L.: Learn
then test: Calibrating predictive algorithms to achieve risk control. arXiv
preprint arXiv:2110.01052 (2021)
[5]
Antol, S., Agrawal, A., Lu, J., Mitchell, M., Batra, D., Lawrence Zitnick, C.,
Parikh, D.: Vqa: Visual question answering. In: Proceedings of the IEEE
international conference on computer vision. pp. 2425–2433 (2015)
[6]
Asan, O., Bayrak, A.E., Choudhury, A., et al.: Artificial intelligence and
human trust in healthcare: focus on clinicians. Journal of medical Internet
research
22
(6), e15154 (2020)
[7]
Bhattacharya, N., Li, Q., Gurari, D.: Why does a visual question have different
answers? In: Proceedings of the IEEE/CVF International Conference on Computer
Vision. pp. 4271–4280 (2019)
[8]
Black, E., Leino, K., Fredrikson, M.: Selective ensembles for consistent
predictions. In: International Conference on Learning Representations (2022)
[9]
Cao, J., Gan, Z., Cheng, Y., Yu, L., Chen, Y.C., Liu, J.: Behind the scene:
Revealing the secrets of pre-trained vision-and-language models. In: European
Conference on Computer Vision. pp. 565–580. Springer (2020)
[10]
Chen, X., Fang, H., Lin, T.Y., Vedantam, R., Gupta, S., Dollár, P.,
Zitnick, C.L.: Microsoft COCO captions: Data collection and evaluation
server. arXiv preprint arXiv:1504.00325 (2015)
[11]
Chen, Y.C., Li, L., Yu, L., El Kholy, A., Ahmed, F., Gan, Z., Cheng, Y., Liu,
J.: UNITER: Universal image-text representation learning. In: ECCV. ECCV
(2020)
[12]
Chiu, T.Y., Zhao, Y., Gurari, D.: Assessing image quality issues for real-world
problems. In: Proceedings of the IEEE/CVF Conference on Computer Vision and
Pattern Recognition. pp. 3646–3656 (2020)
[13]
Chow, C.: On optimum recognition error and reject tradeoff. IEEE Transactions
on information theory
16
(1), 41–46 (1970)
[14]
Chow, C.K.: An optimum character recognition system using decision functions.
IRE Transactions on Electronic Computers
EC-6
(4), 247–254 (1957)
[15]
Corbière, C., Thome, N., Bar-Hen, A., Cord, M., Pérez, P.: Addressing
failure prediction by learning model confidence. Advances in Neural
Information Processing Systems
32
(2019)
[16]
Davis, E.: Unanswerable questions about images and texts. Frontiers in
Artificial Intelligence
3
,  51 (2020)
[17]
De Stefano, C., Sansone, C., Vento, M.: To reject or not to reject: that is the
question-an answer in case of neural classifiers. IEEE Transactions on
Systems, Man, and Cybernetics, Part C (Applications and Reviews)
30
(1), 84–94 (2000). https://doi.org/10.1109/5326.827457
[18]
Devlin, J., Chang, M.W., Lee, K., Toutanova, K.: Bert: Pre-training of deep
bidirectional transformers for language understanding. arXiv preprint
arXiv:1810.04805 (2018)
[19]
Dong, L., Quirk, C., Lapata, M.: Confidence modeling for neural semantic
parsing. In: Proceedings of the 56th Annual Meeting of the Association for
Computational Linguistics (Volume 1: Long Papers). pp. 743–753. Association
for Computational Linguistics, Melbourne, Australia (Jul 2018).
https://doi.org/10.18653/v1/P18-1069,
https://aclanthology.org/P18-1069
[20]
El-Yaniv, R., Wiener, Y.: On the foundations of noise-free selective
classification. Journal of Machine Learning Research
11
,
1605–1641 (2010)
[21]
Fukui, A., Park, D.H., Yang, D., Rohrbach, A., Darrell, T., Rohrbach, M.:
Multimodal compact bilinear pooling for visual question answering and visual
grounding. In: EMNLP (2016)
[22]
Gao, P., Jiang, Z., You, H., Lu, P., Hoi, S.C., Wang, X., Li, H.: Dynamic
fusion with intra-and inter-modality attention flow for visual question
answering. In: CVPR (2019)
[23]
Geifman, Y., El-Yaniv, R.: Selective classification for deep neural networks.
Advances in neural information processing systems
30
(2017)
[24]
Geifman, Y., El-Yaniv, R.: Selectivenet: A deep neural network with an
integrated reject option. In: International Conference on Machine Learning.
pp. 2151–2159. PMLR (2019)
[25]
Goyal, Y., Khot, T., Summers-Stay, D., Batra, D., Parikh, D.: Making the v in
vqa matter: Elevating the role of image understanding in visual question
answering. In: Proceedings of the IEEE Conference on Computer Vision and
Pattern Recognition. pp. 6904–6913 (2017)
[26]
Guillory, D., Shankar, V., Ebrahimi, S., Darrell, T., Schmidt, L.: Predicting
with confidence on unseen distributions. In: Proceedings of the IEEE/CVF
International Conference on Computer Vision. pp. 1134–1144 (2021)
[27]
Gulshan, V., Peng, L., Coram, M., Stumpe, M.C., Wu, D., Narayanaswamy, A.,
Venugopalan, S., Widner, K., Madams, T., Cuadros, J., Kim, R., Raman, R.,
Nelson, P.C., Mega, J.L., Webster, D.R.: Development and validation of a deep
learning algorithm for detection of diabetic retinopathy in retinal fundus
photographs. JAMA
316
(22), 2402–2410 (12 2016).
https://doi.org/10.1001/jama.2016.17216,
https://doi.org/10.1001/jama.2016.17216
[28]
Guo, C., Pleiss, G., Sun, Y., Weinberger, K.Q.: On calibration of modern neural
networks. In: International Conference on Machine Learning. pp. 1321–1330.
PMLR (2017)
[29]
Gurari, D., Li, Q., Stangl, A.J., Guo, A., Lin, C., Grauman, K., Luo, J.,
Bigham, J.P.: Vizwiz grand challenge: Answering visual questions from blind
people. In: Proceedings of the IEEE Conference on Computer Vision and Pattern
Recognition. pp. 3608–3617 (2018)
[30]
Hanczar, B., Dougherty, E.R.: Classification with reject option in gene
expression data. Bioinformatics
24
(17), 1889–1895 (2008)
[31]
He, K., Zhang, X., Ren, S., Sun, J.: Deep residual learning for image
recognition. In: Proceedings of the IEEE conference on computer vision and
pattern recognition. pp. 770–778 (2016)
[32]
Hendricks, L.A., Burns, K., Saenko, K., Darrell, T., Rohrbach, A.: Women also
snowboard: Overcoming bias in captioning models. In: Proceedings of the
European Conference on Computer Vision (ECCV). pp. 771–787 (2018)
[33]
Hendrycks, D., Gimpel, K.: A baseline for detecting misclassified and
out-of-distribution examples in neural networks. In: Proceedings of
International Conference on Learning Representations (2017)
[34]
Hudson, D.A., Manning, C.D.: Gqa: A new dataset for real-world visual reasoning
and compositional question answering. In: Proceedings of the IEEE/CVF
conference on computer vision and pattern recognition. pp. 6700–6709 (2019)
[35]
Ji, X., Pascanu, R., Hjelm, D., Lakshminarayanan, B., Vedaldi, A.: Test sample
accuracy scales with training sample density in neural networks. arXiv
preprint arXiv:2106.08365 (2021)
[36]
Jiang, H., Kim, B., Guan, M., Gupta, M.: To trust or not to trust a classifier.
In: Bengio, S., Wallach, H., Larochelle, H., Grauman, K., Cesa-Bianchi, N.,
Garnett, R. (eds.) Advances in Neural Information Processing Systems.
vol. 31. Curran Associates, Inc. (2018),
https://proceedings.neurips.cc/paper/2018/file/7180cffd6a8e829dacfc2a31b3f72ece-Paper.pdf
[37]
Jiang, H., Misra, I., Rohrbach, M., Learned-Miller, E., Chen, X.: In defense of
grid features for visual question answering. In: Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition. pp. 10267–10276
(2020)
[38]
Jiang, Y., Natarajan, V., Chen, X., Rohrbach, M., Batra, D., Parikh, D.: Pythia
v0. 1: the winning entry to the vqa challenge 2018. arXiv preprint
arXiv:1807.09956 (2018)
[39]
Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E.,
Schiefer, N., Dodds, Z.H., DasSarma, N., Tran-Johnson, E., et al.: Language
models (mostly) know what they know. arXiv preprint arXiv:2207.05221 (2022)
[40]
Kafle, K., Kanan, C.: An analysis of visual question answering algorithms. In:
ICCV (2017)
[41]
Kafle, K., Kanan, C.: Visual question answering: Datasets, algorithms, and
future challenges. Computer Vision and Image Understanding
163
,
3–20 (2017)
[42]
Kamath, A., Jia, R., Liang, P.: Selective question answering under domain
shift. In: Proceedings of the 58th Annual Meeting of the Association for
Computational Linguistics. pp. 5684–5696. Association for Computational
Linguistics, Online (Jul 2020). https://doi.org/10.18653/v1/2020.acl-main.503,
https://aclanthology.org/2020.acl-main.503
[43]
Karamcheti, S., Krishna, R., Fei-Fei, L., Manning, C.: Mind your outliers!
investigating the negative impact of outliers on active learning for visual
question answering. In: Proceedings of the 59th Annual Meeting of the
Association for Computational Linguistics and the 11th International Joint
Conference on Natural Language Processing (Volume 1: Long Papers). pp.
7265–7281. Association for Computational Linguistics, Online (Aug 2021).
https://doi.org/10.18653/v1/2021.acl-long.564,
https://aclanthology.org/2021.acl-long.564
[44]
Khan, J., Wei, J.S., Ringner, M., Saal, L.H., Ladanyi, M., Westermann, F.,
Berthold, F., Schwab, M., Antonescu, C.R., Peterson, C., et al.:
Classification and diagnostic prediction of cancers using gene expression
profiling and artificial neural networks. Nature medicine
7
(6),
673–679 (2001)
[45]
Khani, F., Rinard, M., Liang, P.: Unanimous prediction for 100% precision with
application to learning semantic mappings. arXiv preprint arXiv:1606.06368
(2016)
[46]
Kingma, D.P., Ba, J.: Adam: A method for stochastic optimization. In:
Proceedings of the International Conference on Learning Representations
(2015)
[47]
Krishna, R., Zhu, Y., Groth, O., Johnson, J., Hata, K., Kravitz, J., Chen, S.,
Kalantidis, Y., Li, L.J., Shamma, D.A., et al.: Visual genome: Connecting
language and vision using crowdsourced dense image annotations. International
journal of computer vision
123
(1), 32–73 (2017)
[48]
Lakshminarayanan, B., Pritzel, A., Blundell, C.: Simple and scalable predictive
uncertainty estimation using deep ensembles. In: Advances in neural
information processing systems. vol. 30 (2017)
[49]
Li, L.H., Yatskar, M., Yin, D., Hsieh, C.J., Chang, K.W.: Visualbert: A simple
and performant baseline for vision and language. In: Arxiv (2019)
[50]
Li, M., Weber, C., Wermter, S.: Neural networks for detecting irrelevant
questions during visual question answering. In: International Conference on
Artificial Neural Networks. pp. 786–797. Springer (2020)
[51]
Li, X., Yin, X., Li, C., Zhang, P., Hu, X., Zhang, L., Wang, L., Hu, H., Dong,
L., Wei, F., et al.: Oscar: Object-semantics aligned pre-training for
vision-language tasks. In: European Conference on Computer Vision. pp.
121–137. Springer (2020)
[52]
Loshchilov, I., Hutter, F.: Decoupled weight decay regularization. arXiv
preprint arXiv:1711.05101 (2017)
[53]
Lu, J., Batra, D., Parikh, D., Lee, S.: Vilbert: Pretraining task-agnostic
visiolinguistic representations for vision-and-language tasks. Advances in
neural information processing systems
32
(2019)
[54]
Lütkenhöner, B., Basel, T.: Predictive modeling for diagnostic tests
with high specificity, but low sensitivity: a study of the glycerol test in
patients with suspected meniere’s disease. PLoS One
8
(11),
e79315 (2013)
[55]
Mahendru, A., Prabhu, V., Mohapatra, A., Batra, D., Lee, S.: The promise of
premise: Harnessing question premises in visual question answering. In: EMNLP
(2017)
[56]
Mcknight, D.H., Carter, M., Thatcher, J.B., Clay, P.F.: Trust in a specific
technology: An investigation of its components and measures. ACM Transactions
Management Information Systems
2
(2) (jul 2011).
https://doi.org/10.1145/1985347.1985353,
https://doi.org/10.1145/1985347.1985353
[57]
Naeini, M.P., Cooper, G., Hauskrecht, M.: Obtaining well calibrated
probabilities using bayesian binning. In: Twenty-Ninth AAAI Conference on
Artificial Intelligence (2015)
[58]
Nguyen, D.K., Goswami, V., Chen, X.: Movie: Revisiting modulated convolutions
for visual counting and beyond. In: Proceedings of the International
Conference on Learning Representations (2021)
[59]
Niculescu-Mizil, A., Caruana, R.: Predicting good probabilities with supervised
learning. In: Proceedings of the 22nd international conference on Machine
learning. pp. 625–632 (2005)
[60]
Pennington, J., Socher, R., Manning, C.D.: Glove: Global vectors for word
representation. In: Proceedings of the 2014 conference on empirical methods
in natural language processing (EMNLP). pp. 1532–1543 (2014)
[61]
Platt, J., et al.: Probabilistic outputs for support vector machines and
comparisons to regularized likelihood methods. Advances in large margin
classifiers
10
(3), 61–74 (1999)
[62]
Pudil, P., Novovicova, J., Blaha, S., Kittler, J.: Multistage pattern
recognition with reject option. In: Proceedings., 11th IAPR International
Conference on Pattern Recognition. Vol.II. Conference B: Pattern Recognition
Methodology and Systems. pp. 92–95 (1992). https://doi.org/10.1109/ICPR.1992.201729
[63]
Radford, A., Kim, J.W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry,
G., Askell, A., Mishkin, P., Clark, J., et al.: Learning transferable visual
models from natural language supervision. In: International Conference on
Machine Learning. pp. 8748–8763. PMLR (2021)
[64]
Ray, A., Christie, G., Bansal, M., Batra, D., Parikh, D.: Question relevance in
vqa: Identifying non-visual and false-premise questions. In: Proceedings of
the 2016 Conference on Empirical Methods in Natural Language Processing. pp.
919–924 (2016)
[65]
Ren, S., He, K., Girshick, R., Sun, J.: Faster r-cnn: Towards real-time object
detection with region proposal networks. Advances in neural information
processing systems
28
(2015)
[66]
Shafer, G., Vovk, V.: A tutorial on conformal prediction. Journal of Machine
Learning Research
9
(3) (2008)
[67]
Shah, M., Chen, X., Rohrbach, M., Parikh, D.: Cycle-consistency for robust
visual question answering. In: CVPR (2019)
[68]
Sharma, H., Jalal, A.S.: A survey of methods, datasets and evaluation metrics
for visual question answering. Image and Vision Computing
116
,
104327 (2021)
[69]
Shen, S., Li, L.H., Tan, H., Bansal, M., Rohrbach, A., Chang, K.W., Yao, Z.,
Keutzer, K.: How much can clip benefit vision-and-language tasks? arXiv
preprint arXiv:2107.06383 (2021)
[70]
Singh, A., Goswami, V., Natarajan, V., Jiang, Y., Chen, X., Shah, M., Rohrbach,
M., Batra, D., Parikh, D.: Mmf: A multimodal framework for vision and
language research.
https://github.com/facebookresearch/mmf
(2020)
[71]
Singh, A., Goswami, V., Parikh, D.: Are we pretraining it right? digging deeper
into visio-linguistic pretraining. arXiv preprint arXiv:2004.08744 (2020)
[72]
Singh, A., Natarjan, V., Shah, M., Jiang, Y., Chen, X., Parikh, D., Rohrbach,
M.: Towards vqa models that can read. In: Proceedings of the IEEE Conference
on Computer Vision and Pattern Recognition. pp. 8317–8326 (2019)
[73]
Tan, H., Bansal, M.: LXMERT: Learning cross-modality encoder representations
from transformers. In: Proceedings of the 2019 Conference on Empirical
Methods in Natural Language Processing and the 9th International Joint
Conference on Natural Language Processing. pp. 5100–5111 (2019).
https://doi.org/10.18653/v1/D19-1514,
https://www.aclweb.org/anthology/D19-1514
[74]
Teney, D., Anderson, P., He, X., Van Den Hengel, A.: Tips and tricks for visual
question answering: Learnings from the 2017 challenge. In: CVPR (2018)
[75]
Teney, D., Liu, L., van Den Hengel, A.: Graph-structured representations for
visual question answering. In: Proceedings of the IEEE Conference on Computer
Vision and Pattern Recognition. pp. 1–9 (2017)
[76]
Terao, K., Tamaki, T., Raytchev, B., Kaneda, K., Satoh, S.: Which visual
questions are difficult to answer? analysis with entropy of answer
distributions. arXiv preprint arXiv:2004.05595 (2020)
[77]
Tran, D., Liu, J., Dusenberry, M.W., Phan, D., Collier, M., Ren, J., Han, K.,
Wang, Z., Mariet, Z., Hu, H., Band, N., Rudner, T.G.J., Singhal, K., Nado,
Z., van Amersfoort, J., Kirsch, A., Jenatton, R., Thain, N., Yuan, H.,
Buchanan, K., Murphy, K., Sculley, D., Gal, Y., Ghahramani, Z., Snoek, J.,
Lakshminarayanan, B.: Plex: Towards reliability using pretrained large model
extensions (2022). https://doi.org/10.48550/ARXIV.2207.07411,
https://arxiv.org/abs/2207.07411
[78]
Varshney, N., Mishra, S., Baral, C.: Investigating selective prediction
approaches across several tasks in IID, OOD, and adversarial settings.
In: Findings of the Association for Computational Linguistics: ACL 2022. pp.
1995–2002 (2022). https://doi.org/10.18653/v1/2022.findings-acl.158,
https://aclanthology.org/2022.findings-acl.158
[79]
Vovk, V., Gammerman, A., Shafer, G.: Algorithmic learning in a random world.
Springer Science & Business Media (2005)
[80]
Wang, X., Luo, Y., Crankshaw, D., Tumanov, A., Yu, F., Gonzalez, J.E.: Idk
cascades: Fast deep learning by learning not to overthink. arXiv preprint
arXiv:1706.00885 (2017)
[81]
Whitehead, S., Wu, H., Ji, H., Feris, R., Saenko, K.: Separating skills and
concepts for novel visual question answering. In: Proceedings of the IEEE/CVF
Conference on Computer Vision and Pattern Recognition. pp. 5632–5641 (2021)
[82]
Xin, J., Tang, R., Yu, Y., Lin, J.: The art of abstention: Selective prediction
and error regularization for natural language processing. In: Proceedings of
the 59th Annual Meeting of the Association for Computational Linguistics and
the 11th International Joint Conference on Natural Language Processing
(Volume 1: Long Papers). pp. 1040–1051 (2021)
[83]
Yang, Z., He, X., Gao, J., Deng, L., Smola, A.: Stacked attention networks for
image question answering. In: CVPR (2016)
[84]
Yu, Z., Yu, J., Cui, Y., Tao, D., Tian, Q.: Deep modular co-attention networks
for visual question answering. In: Proceedings of the IEEE/CVF Conference on
Computer Vision and Pattern Recognition. pp. 6281–6290 (2019)
[85]
Zhang, P., Li, X., Hu, X., Yang, J., Zhang, L., Wang, L., Choi, Y., Gao, J.:
Vinvl: Revisiting visual representations in vision-language models. In:
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Recognition. pp. 5579–5588 (2021)
Appendix to
Reliable Visual Question Answering:
Abstain Rather Than Answer Incorrectly
Appendix
0.A
has more discussion on Selector ablations.
Appendix
0.B
shows an experiment with data augmentation for MaxProb.
Appendix
0.C
provides a manual evaluation of the label noise.
Appendix
0.D
gives further analysis comparing Selector versus MaxProb decisions.
Appendix
0.E
provides more qualitative results.
Appendix
0.F
presents results on threshold generalization.
Appendix
0.G
looks at the calibration metric ECE.
Appendix
0.H
has additional details on the dataset splits.
Appendix
0.I
has additional model details.
Appendix
0.J
provides standard deviations for results in Tab.
1
and Tab.
2
.
Appendix
0.K
provides a proof of Lemma 1, providing a motivation for the definition of the Effective Reliability score
Φ
c
\Phi_{c}
.
Appendix
0.L
discusses the relevance of related conformal prediction works.
Appendix 0.A
Selector Design Ablations
Extending the discussion in Sec.
5.4
, we are isolating the effects of different features/modalities on the risk-coverage trade-off when using Selector.
In this direction, we experiment with different input representation variants from CLIP-ViL
[
69
]
in Tab.
3
by ablating the question
q
q
, multimodal
r
r
, and answer
f
′
​
(
x
)
f^{\prime}(x)
representations as well as different image representations.
For image representations, we ablate the usage of the visual representation
v
~
\tilde{v}
directly from the CLIP visual encoder
[
63
]
, as well as the visual representation
v
v
that is the concatenation of the respective pooled outputs from MCAN’s self-guided attention module
[
84
]
and MoVie’s modulated convolutional bottleneck
[
58
]
, which are visual representations that also contain multimodal information from the question.
Question representations are taken from the output of MCAN’s self-attention module.
The multimodal representation is the concatentation of the multimodal representations that are used as inputs to the softmax output (i.e., classification) layer of CLIP-ViL.
For the answer representation, we use the logits just before the softmax in the output layer.
The results in Tab.
3
show the importance of using multimodal information for coverage at low risk levels.
When comparing using each representation in isolation, we see that multimodal representations (
r
r
,
v
v
, and
f
′
​
(
x
)
f^{\prime}(x)
) yield much stronger
𝒞
​
@
\mathcal{C}@
1%,
𝒞
​
@
\mathcal{C}@
5%,
Φ
10
\Phi_{10}
and
Φ
100
\Phi_{100}
than unimodal representations (
v
~
\tilde{v}
and
q
q
).
We also observe that the answer representation achieves the best performance for
𝒞
​
@
\mathcal{C}@
10% and
𝒞
​
@
\mathcal{C}@
20% when each input representation is used in isolation.
Overall, we find that considering multimodal information (i.e., combinations of multimodal representations and unimodal representations from different modalities) to be most effective, with the top performers being the models that incorporate the answer representation alongside multimodal representations (
f
′
​
(
x
)
f^{\prime}(x)
+
r
r
,
f
′
​
(
x
)
f^{\prime}(x)
+
v
v
, and
f
′
​
(
x
)
f^{\prime}(x)
+
q
q
+
v
v
+
r
r
).
Lastly, we also experiment with other architectures for the Selector using the same features as above.
Our Selector is a 2-layer multi-layered perceptron (MLP) (Appendix
0.I.2
).
In Tab.
4
, we see that a simpler, 1-layer Selector has slightly higher
Φ
100
\Phi_{100}
, yet lowers
𝒞
​
@
\mathcal{C}@
1% by about 2.4%. A more complex Transformer yields comparable performance to our 2-layer Selector.
Given these results as well as those in Tab.
3
, we observe that the input representations and training objectives appear to be most important, and efforts for improving learned selection function performance can potentially focus on these.
Architecture
𝒞
​
@
\mathcal{C}@
1%
↑
\uparrow
AUC
↓
\downarrow
Φ
100
\Phi_{100}
↑
\uparrow
1-layer Linear
10.95
10.68
7.47
2-layer MLP (ours)
13.32
9.73
7.32
4-layer Transformer
13.48
9.78
7.35
Table 4
:
Different Selector architectures with CLIP-ViL on our selection function validation split (Val in Tab.
9
). All in %.
Appendix 0.B
Comparing to Data Augmentation
In our experiments, we use a separate set to validate VQA models and train the selection functions (Dev in Tab.
9
).
However, one could use this data to augment the VQA training data, which could potentially improve performance for MaxProb as there is a relationship between accuracy and these reliability metrics (Sec.
5.2
).
Tab.
5
presents these results where we see that using this data to train the Selector is more effective for improving coverage at low risk levels and
Φ
c
\Phi_{c}
with a high cost.
Since the extra data helps improve accuracy, as the risk tolerance nears the error rate of the model and coverage approaches 100%, MaxProb surpasses Selector in coverage (i.e.,
𝒞
​
@
\mathcal{C}@
20%) and Effective Reliability (i.e.,
Φ
1
\Phi_{1}
).
However, overall, these results suggest that using this data to train a Selector can be more beneficial to model reliability than using it for augmentation.
Model
f
f
Selection
Acc.
↑
\uparrow
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
↑
\uparrow
AUC
↓
\downarrow
Φ
c
\Phi_{c}
↑
\uparrow
function
g
g
ℛ
=
1
%
\mathcal{R}=1\%
ℛ
=
5
%
\mathcal{R}=5\%
ℛ
=
10
%
\mathcal{R}=10\%
ℛ
=
20
%
\mathcal{R}=20\%
c
c
=1
c
c
=10
c
c
=100
CLIP-ViL
MaxProb
71.48
3.33
31.92
53.93
84.36
10.59
55.10
20.22
1.93
MaxProb-Aug
72.31
6.57
33.62
56.18
86.20
10.14
56.64
22.13
2.97
Selector
71.48
13.32
38.02
58.16
85.03
9.73
56.09
24.85
7.32
Table 5
:
Comparison between augmenting the training data of CLIP-ViL with our dev set for MaxProb versus utilizing our dev split for training Selector. Results are on our selection function validation split (Val in Tab.
9
). All in %.
Figure 4
:
Example questions, images, annotations, and model predictions for each category of label noise we discover.
Appendix 0.C
Manual Evaluation of Label Noise
As discussed in Sec.
5.3
, we provide further details on our manual annotation for label noise as well as
Φ
100
\Phi_{100}
when accounting for cases where the model may have been unfairly penalized.
We specifically annotate image-question-answer triples, and discovered the following cases (Fig.
4
provides examples of each):
Incomplete Ground Truth
: The ground truth is in some way incomplete and simply misses the predicted answer.
Semantic Match
: The predicted answer is semantically correct but does not exactly match the ground truth.
Incomplete Prediction
: The predicted answer is incomplete but has part of the correct answer.
Singular/Plural
: The predicted answer is singular/plural while the ground truth is plural/singular (though only if providing the opposite singular/plural version is still correct).
We do these annotations for each considered VQA model and selection function trained to optimize
Φ
100
\Phi_{100}
(i.e., the strongest penalty for wrong answers) and focus our efforts on questions with VQA accuracy of 0, meaning questions that contribute negatively to
Φ
100
\Phi_{100}
. Once we have the annotations of unfairly penalized questions, we recompute the Effective Reliability score
Φ
100
′
\Phi_{100}^{\prime}
when counting those questions as either abstentions or as answered questions that achieved a VQA accuracy of 100%. Although the selection function decided to answer each of the unfairly penalized questions that we annotated, we compute
Φ
100
′
\Phi_{100}^{\prime}
under these two cases because it is unclear exactly how correct these non-matching answers should be considered. Counting them as abstentions serves as a lower bound for
Φ
100
′
\Phi_{100}^{\prime}
, whereas assigning a VQA accuracy of 100% is an upper bound.
We present the results before (
Φ
100
\Phi_{100}
) and after (
Φ
100
′
\Phi_{100}^{\prime}
) controlling for noise in Tab.
6
.
We find that while this noise does contribute to some differences in performance, it does not affect the rankings between selection functions.
For example, relative to each
Φ
100
\Phi_{100}
with CLIP-ViL,
Φ
100
′
\Phi_{100}^{\prime}
yields an increase of 0.27% for MaxProb, 0.38% for Calibration, and 0.56% for Selector, yet the rankings remain the same.
Qualitatively, we observe that there tends to be a very significant overlap in unfairly penalized examples between selection functions, which is likely part of why the rankings remain the same.
Moreover, the amount of these label errors tends to be small, and the vast majority of questions contributing to the penalties in
Φ
100
\Phi_{100}
across all models are properly marked as incorrect (
∼
\sim
93%).
Since the score for an incorrect sample (-100) is considerably lower than a sample marked as 100% correct (+1), there is also little difference in
Φ
100
′
\Phi_{100}^{\prime}
when considering these few unfairly penalized questions as abstentions versus as correct answers.
These results imply that the comparisons between different selection functions at high cost (or low risk) for a given model are still meaningful despite the potential presence of noise.
Model
f
f
Selection
% Correct GT
Φ
100
\Phi_{100}
↑
\uparrow
Φ
100
′
\Phi_{100}^{\prime}
↑
\uparrow
function
g
g
Abstain
Correct
Pythia
[
38
]
MaxProb
91.30
1.81
2.00
2.00
Calibration
93.55
2.14
2.32
2.33
Selector
87.50
4.12
4.49
4.50
ViLBERT
[
53
]
MaxProb
97.75
1.67
1.86
1.86
Calibration
94.94
2.92
3.30
3.30
Selector
88.14
5.41
6.07
6.08
VisualBERT
[
49
]
MaxProb
100.00
2.49
2.49
2.49
Calibration
97.92
3.83
3.93
3.93
Selector
85.29
4.82
5.77
5.78
CLIP-ViL
[
69
]
MaxProb
94.74
1.82
2.09
2.09
Calibration
93.44
5.78
6.16
6.16
Selector
87.23
8.76
9.32
9.32
Table 6
:
Effect of label noise on
Φ
100
\Phi_{100}
. % Correct GT indicates the percentage of answered samples with a VQA accuracy of 0, where the ground truth and resulting VQA accuracy was considered correct based on the question, image, annotations, and model prediction.
Φ
100
\Phi_{100}
indicates the original score, whereas
Φ
100
′
\Phi_{100}^{\prime}
indicates the score when counting answered questions where label errors led to a VQA accuracy of 0 as abstentions (
Abstain
) or having a VQA accuracy of 100% (
Correct
) instead of being counted as incorrect. Although there is a small amount of label noise, it does not affect the ranking between selection functions with respect to Effective Reliability. All in %.
Appendix 0.D
Analysis of Selector Decisions
We would like to understand any differences in the types of questions that the Selector chooses to abstain or answer as compared to MaxProb. We compare decisions on our test split for the two selective models, where thresholds were chosen to optimize
Φ
100
\Phi_{100}
on validation. We use labels from
[
76
]
which assign one of the following categories to each question, in order of difficulty: unimodal (Level 1), where the question could be answered without looking at the image, “simple-multimodal” (Level 2), where the question is simple to answer when additionally considering the image, and “difficult-multimodal” (Level 3), where the question is difficult to answer even when considering both modalities. Fig.
5
compares the number of questions answered in each difficulty level by the MaxProb and Selector models. We find that the Selector not only answers 1.2
×
\times
more unimodal questions than MaxProb, but also 1.9
×
\times
more “simple-multimodal” and, impressively, 9.6
×
\times
more “difficult-multimodal” questions.
Figure 5
:
Number of questions in our test split that the MaxProb and Selector selection functions chose to answer, grouped by difficulty level
[
76
]
. Level 1 corresponds to simple questions that could be answered without the image, Level 2 questions are simple to answer when considering both the question and image, and Level 3 questions are difficult to answer even when considering both modalities. Thresholds for the selection functions are chosen on the validation set to maximize
Φ
100
\Phi_{100}
.
Appendix 0.E
More Qualitative Analysis
In Fig.
6
, we show several more examples of cases from our test split that illustrate Selector and MaxProb decisions, where we use CLIP-ViL with selection functions optimized for
Φ
100
\Phi_{100}
on the validation set (same as Fig.
3
).
In particular, we show cases where the decisions of Selector and MaxProb differed — where Selector chooses to answer while MaxProb abstains, and vice-versa.
We see some cases where the MaxProb decision to abstain may have been influenced by variability in possible answers that may cause model confidence values to be split, yet the annotations themselves have underlying semantic agreement (e.g., Fig.
6
top left, where “
sunny
” weather conditions are also described as “
nice
” or “
clear
”).
On the other hand, we also see cases where the model was incorrect on questions which may have been unclear or surprising, and Selector chose to abstain whereas MaxProb chose to answer (e.g., the second example on row (c) asks the unusual question “
Is the bear wearing a helmet?
”).
In these cases, we would expect a selective VQA model to abstain from answering to avoid providing an incorrect answer.
Additionally, we show several failure cases of Selector, which chose to answer on an incorrect question while MaxProb chose to abstain.
Figure 6
:
More qualitative test set examples with CLIP-ViL selective model predictions, when optimized for
Φ
100
\Phi_{100}
on validation. Rows (a) and (b) show cases where the model was correct, yet MaxProb chose to abstain and Selector chose to answer. Rows (c) and (d) show examples of the opposite case, where the model was wrong, yet MaxProb chose to answer (contributing to the risk) and Selector chose to abstain. Row (e) shows failure cases of Selector, which chose to answer on an incorrect sample when MaxProb chose to abstain.
Appendix 0.F
Threshold Generalization
As discussed in Sec.
5.2
, we evaluate how well a threshold selected for a target risk level on validation can achieve a similar level of risk on our test split.
Experimenting with VisualBERT, comparing MaxProb and Selector, we see in Tab.
7
that the differences in risk for both selection functions tend to be at most 0.25%. Likewise, we observe corresponding differences in achieved coverage between the validation threshold and the maximum coverage (
Δ
​
𝒞
\Delta\mathcal{C}
). This demonstrates that the thresholds can generalize reasonably well, although it does not allow for a direct comparison of coverage for the same risk.
Effective Reliability, on the other hand, can use thresholds chosen from validation and still result in a clear comparison of models as it is a single metric.
Selection
Δ
​
ℛ
\Delta\mathcal{R}
Δ
​
𝒞
\Delta\mathcal{C}
function
g
g
ℛ
=
\mathcal{R}=
1%
5%
10%
20%
1%
5%
10%
20%
MaxProb
+
+
0.12
−
-
0.14
+
+
0.17
−
-
0.09
+
+
0.92
−
-
0.55
+
+
0.81
−
-
0.20
Selector
+
+
0.14
+
+
0.25
+
+
0.17
−
-
0.23
+
+
2.00
+
+
1.09
+
+
0.59
−
-
0.49
Table 7
:
Generalization of abstention thresholds
γ
\gamma
from validation to test, with VisualBERT.
Δ
​
ℛ
\Delta\mathcal{R}
and
Δ
​
𝒞
\Delta\mathcal{C}
are the differences in risk and coverage percentages, respectively, when using
γ
\gamma
selected for the target risk
ℛ
\mathcal{R}
on validation vs.
γ
\gamma
with maximum
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
.
Appendix 0.G
Effect of Model Calibration
We report the calibration performance of the vector scaling.
Specifically, we measure the expected calibration error (ECE)
[
28
,
57
]
, which measures the expected difference between the model confidence and accuracy.
The lower the ECE, the more that the model’s confidence scores correspond to the actual accuracy of the predictions.
Note that the ECE metric is designed for single label classification problems.
To use the ECE metric for VQA, where there can be multiple possible answers for a question, we simply consider the most frequent human annotated answer as the ground truth for each question.
We see in Tab.
8
that vector scaling does indeed improve calibration for all models.
Taking this observation in combination with the improvements over MaxProb on
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
, AUC, and Effective Reliability seen in Tab.
1
and Tab.
2
, it appears that improving model calibration can help improve the risk-coverage trade-off.
However, as discussed in Sec.
4
, it is necessary to use calibration techniques that can change the relative confidence rankings, such as vector scaling.
Pythia
ViLBERT
VisualBERT
CLIP-ViL
MaxProb
Calib.
MaxProb
Calib.
MaxProb
Calib.
MaxProb
Calib.
ECE
↓
\downarrow
0.1702
0.0938
0.1457
0.1120
0.1458
0.1169
0.1978
0.1521
Table 8
:
ECE of different models with (Calibration, denoted Calib.) and without (MaxProb) the vector scaling calibration on our test split. Lower is better.
Appendix 0.H
Additional Dataset Split Details
Source
Split Name
Usage
% src
#I
#Q
#A
VQA v2 train
Train
Train
f
f
100%
82,783
443,757
4,437,570
VQA v2 val
Dev
Validate
f
f
/ Train
g
g
40%
16,202
86,138
861,380
Val
Validate
g
g
10%
4,050
21,878
218,780
Test
Test
h
h
50%
20,252
106,338
1,063,380
Table 9
:
Table of statistics for the dataset splits used for training as well as validating VQA models (
f
f
), training as well as validating selection functions (
g
g
), and testing full selective models (
h
=
(
f
,
g
)
h=(f,g)
). % src indicates the percentage of the source data (Source) that each split represents. #I, #Q, and #A indicate the number of images, questions, and answers, respectively.
We experiment on the VQA v2 dataset
[
25
]
, which contains a large amount of human-annotated image-question-answer triplets.
Tab.
9
lays out the data splits we use in our experiments.
We create splits of the VQA v2 validation set since we require answer annotations to evaluate risk, coverage, and Effective Reliability.
These splits are created such that no images (and therefore no question-answer annotations) are shared between them.
Note that the data in the held out test set (Test in Tab.
9
) is never seen during the training or validation of any component (
f
f
or
g
g
) and is only used for evaluations.
All presented results are on our test set unless otherwise specified.
Appendix 0.I
Model Details
In this section, we present the details of the models used in our experiments.
Hyperparameters
Pythia
ViLBERT
†
VisualBERT
†
CLIP-ViL
Batch Size
512
896
896
32
Hidden Size
5,000
1,024
768
1,024
# Layers
L-1, V-1
L-12, V-6
12
6 / 4
Optimizer
Adamax
[
46
]
AdamW
[
52
]
AdamW
[
52
]
AdamW
[
52
]
Adam
ϵ
\epsilon
1e-8
1e-8
1e-8
1e-9
Adam
β
1
\beta_{1}
0.9
0.9
0.9
0.9
Adam
β
2
\beta_{2}
0.999
0.98
0.98
0.98
Learning rate
0.01
5e-5
5e-5
5e-5
Dropout
–
0.1
0.1
0.1
# Steps
22,000
88,000
88,000
236,000
# Warmup Steps
1,000
2,000
2,000
54,000
Max Grad. L2-Norm
0.25
–
–
5
Table 10
:
Hyperparameters of each model used in our experiments. Max Grad. L2-Norm is used for gradient clipping. L and V indicate language and vision layers, respectively. The 6 / 4 for CLIP-ViL indicates that the model has 6 MCAN layers and 4 MoVie layers.
†
\dagger
indicates that the hyperparameters are reported directly from
[
71
]
.
0.I.1
VQA Models
We use the open-source MMF framework
[
70
]
for all our experiments, which contains implementations of each VQA model.
3
3
3
https://mmf.sh/
For training VQA models, we follow the hyperparameters from MMF, which we list in Tab.
10
.
All models treat VQA as a classification task and are trained with VQA accuracy as soft target scores via a binary cross-entropy loss
[
74
]
.
We briefly discuss the models and settings used in our experiments, extending Sec.
5.1
:
Pythia
[
38
]
:
A previous state-of-the-art model that won the 2018 VQA challenge and is an optimization of the widely used bottom-up top-down (BUTD) VQA model
[
2
]
.
This model uses BUTD object detection features
[
2
]
trained on Visual Genome
[
47
]
, but the features are extracted from a ResNext-152 based FasterRCNN
[
65
]
.
Pythia’s implementation further uses grid features from a ResNet-152
[
31
]
as additional inputs to improve performance
[
38
]
.
GloVe embeddings
[
60
]
are used to initialize the word representations.
We train this model from scratch on the VQA v2 training data.
ViLBERT
[
53
]
:
A two-stream vision-and-language transformer model
[
9
,
73
]
that also uses object detection features.
The same object detection features from Pythia are used, but without the addition of grid features.
We use the pretrained and fine-tuned model provided by MMF.
4
4
4
https://github.com/facebookresearch/mmf/tree/main/projects/pretrain_vl_right
The MMF version of this model is from
[
71
]
is pretrained on the VQA v2 training data
[
25
]
using self-supervised objectives (masked language modeling and masked image modeling).
The VQA model is initialized with the pretrained encoder weights, and then fine-tuned on the VQA v2 training data.
VisualBERT
[
49
]
:
This model is a single-stream transformer architecture, like BERT
[
18
]
.
Here, the setup is very similar to ViLBERT and we use the same visual features as ViLBERT.
We again use the pretrained and fine-tuned model provided by MMF.
4
This MMF version of VisualBERT
[
71
]
is pretrained on MSCOCO captions
[
10
]
using a masked language modeling objective.
Just like ViLBERT, the VQA model is also initialized with the pretrained encoder weights and fine-tuned on VQA v2.
CLIP-ViL
[
69
]
:
This represents a state-of-the-art model that is trained from scratch on the VQA data whose visual encoder is from the CLIP model
[
63
]
.
The visual representations are grid features that are obtained from the visual encoder of the CLIP model
[
63
]
.
We use the implementation provided by the authors of
[
69
]
to extract the visual features.
5
5
5
https://github.com/clip-vil/CLIP-ViL/tree/master/CLIP-ViL-Direct/vqa
The VQA architecture, MoVie+MCAN
[
58
]
, is an ensemble of a transformer encoder-decoder
[
84
]
and modulated convolutional
[
58
]
model, which won the 2020 VQA challenge.
GloVe embeddings
[
60
]
are also used to initialize the word representations.
Like Pythia, we train this VQA model from scratch on VQA v2 training data.
0.I.2
Selection Functions
We detail the Calibration and Selector selection functions here.
We do not cover MaxProb as no additional training is required.
While training each selection function, we freeze the weights of the VQA model.
Calibration.
The inputs to the calibration are the unnormalized answer logits (i.e., answer representation just before the softmax) of the VQA model, and the outputs are the calibrated logits.
Since we use vector scaling
[
28
,
61
]
, we input the logits from the VQA model into a linear layer with a diagonal weight matrix and a bias term.
During training, after the linear layer, we apply a sigmoid activation and, in contrast to
[
28
]
, use these as input to a binary cross entropy loss with the soft VQA labels
[
74
]
.
We train the linear layer using the AdamW optimizer
[
52
]
with a learning rate of 0.01 and a weight decay of 1e-4.
At test time, we use the output of this linear layer as our calibrated logits, apply a softmax, and use the same abstention procedure as MaxProb (Sec.
4
).
Selector.
The inputs to Selector are the answer, question, image, and multimodal representations.
For each input, we have a specific 1-layer MLP with a ReLU activation and hidden size of 512.
We then concatenate the outputs of these layers and input them to a 2-layer MLP with ReLU activations and hidden size of 1,024, followed by a binary output layer to produce a confidence value.
This architecture remains exactly the same for all models.
However, if a model produces a set of representations for the image or question, then we max pool these features to collapse them to a single representation.
For optimization, we employ the AdamW optimizer
[
52
]
with a learning rate of 1e-4, a batch size of 256, and gradient clipping with a max gradient L2 norm of 0.25.
Appendix 0.J
Extended Results
Tab.
11
and Tab.
12
provide the mean and standard deviation over the 10 random seeds for Pythia and CLIP-ViL results.
Due to difficulties reproducing the pretrained and fine-tuned performance of ViLBERT and VisualBERT, we simply use existing checkpoints in MMF
4
and report single run metrics for these VQA models.
Model
f
f
Selection
Acc.
↑
\uparrow
𝒞
​
@
​
ℛ
\mathcal{C}@\mathcal{R}
↑
\uparrow
AUC
↓
\downarrow
function
g
g
ℛ
=
1
%
\mathcal{R}=1\%
ℛ
=
5
%
\mathcal{R}=5\%
ℛ
=
10
%
\mathcal{R}=10\%
ℛ
=
20
%
\mathcal{R}=20\%
Pythia
MaxProb
66.17
±
\pm
0.10
6.00
±
\pm
0.37
24.71
±
\pm
0.46
40.99
±
\pm
0.39
71.45
±
\pm
0.25
13.88
±
\pm
0.08
Calibration
66.45
±
\pm
0.09
6.50
±
\pm
0.43
25.07
±
\pm
0.46
41.95
±
\pm
0.38
73.44
±
\pm
0.27
13.52
±
\pm
0.08
Selector
66.17
±
\pm
0.10
8.79
±
\pm
0.52
26.92
±
\pm
0.31
43.24
±
\pm
0.43
73.40
±
\pm
0.25
13.30
±
\pm
0.07
Best Possible (
𝒞
\mathcal{C}
)
66.17
±
\pm
0.10
62.67
±
\pm
0.11
68.41
±
\pm
0.12
73.52
±
\pm
0.11
82.71
±
\pm
0.13
6.68
±
\pm
0.04
CLIP-ViL
MaxProb
71.75
±
\pm
0.13
6.78
±
\pm
1.98
34.69
±
\pm
1.30
55.72
±
\pm
0.43
85.13
±
\pm
0.23
10.23
±
\pm
0.13
Calibration
71.71
±
\pm
0.11
13.12
±
\pm
0.72
37.06
±
\pm
0.35
56.06
±
\pm
0.35
85.23
±
\pm
0.20
9.91
±
\pm
0.07
Selector
71.75
±
\pm
0.13
16.34
±
\pm
0.73
39.48
±
\pm
0.29
58.16
±
\pm
0.40
85.37
±
\pm
0.25
9.52
±
\pm
0.07
Best Possible (
𝒞
\mathcal{C}
)
71.75
±
\pm
0.13
68.49
±
\pm
0.15
74.55
±
\pm
0.15
79.72
±
\pm
0.14
89.69
±
\pm
0.16
4.58
±
\pm
0.05
Table 11
:
Mean and standard deviations for risk-coverage metrics for different selection functions. All in %.
Model
f
f
Selection
c
c
=1
c
c
=10
c
c
=100
function
g
g
Φ
1
\Phi_{1}
↑
\uparrow
ℛ
\mathcal{R}
↓
\downarrow
𝒞
\mathcal{C}
↑
\uparrow
Φ
10
\Phi_{10}
↑
\uparrow
ℛ
\mathcal{R}
↓
\downarrow
𝒞
\mathcal{C}
↑
\uparrow
Φ
100
\Phi_{100}
↑
\uparrow
ℛ
\mathcal{R}
↓
\downarrow
𝒞
\mathcal{C}
↑
\uparrow
Pythia
—
38.49
±
\pm
0.19
33.83
±
\pm
0.10
100
±
\pm
0.00
-210.62
±
\pm
1.01
33.83
±
\pm
0.10
100
±
\pm
0.00
−
-
2701.68
±
\pm
9.19
33.83
±
\pm
0.10
100
±
\pm
0.00
MaxProb
47.28
±
\pm
0.12
21.62
±
\pm
0.27
76.03
±
\pm
0.57
15.15
±
\pm
0.35
5.24
±
\pm
0.40
25.62
±
\pm
1.42
2.27
±
\pm
0.18
0.85
±
\pm
0.15
4.89
±
\pm
1.04
Calibration
48.06
±
\pm
0.15
21.21
±
\pm
0.34
76.18
±
\pm
0.73
15.23
±
\pm
0.36
5.85
±
\pm
0.68
28.06
±
\pm
2.31
2.19
±
\pm
0.66
0.94
±
\pm
0.28
5.88
±
\pm
1.62
Selector
48.16
±
\pm
0.16
20.67
±
\pm
0.65
74.84
±
\pm
1.26
17.12
±
\pm
0.24
5.99
±
\pm
0.23
30.16
±
\pm
0.75
3.84
±
\pm
0.39
0.94
±
\pm
0.18
8.23
±
\pm
1.33
Best Possible (
Φ
c
\Phi_{c}
)
66.17
±
\pm
0.10
8.51
±
\pm
0.05
72.32
±
\pm
0.09
66.17
±
\pm
0.10
8.51
±
\pm
0.05
72.32
±
\pm
0.09
66.17
±
\pm
0.10
8.51
±
\pm
0.05
72.32
±
\pm
0.09
CLIP-ViL
—
49.41
±
\pm
0.25
28.25
±
\pm
0.13
100
±
\pm
0.00
-151.70
±
\pm
1.32
28.25
±
\pm
0.13
100
±
\pm
0.00
-2162.80
±
\pm
12.06
28.25
±
\pm
0.13
100
±
\pm
0.00
MaxProb
55.82
±
\pm
0.14
19.22
±
\pm
0.30
83.45
±
\pm
0.65
22.03
±
\pm
0.59
5.59
±
\pm
0.34
37.67
±
\pm
1.31
2.85
±
\pm
0.75
0.96
±
\pm
0.23
6.97
±
\pm
2.39
Calibration
56.03
±
\pm
0.17
18.30
±
\pm
0.44
81.61
±
\pm
0.98
23.24
±
\pm
0.34
4.95
±
\pm
0.46
36.82
±
\pm
1.91
5.30
±
\pm
0.71
0.73
±
\pm
0.20
9.97
±
\pm
2.35
Selector
56.45
±
\pm
0.16
17.44
±
\pm
0.53
80.09
±
\pm
1.13
26.06
±
\pm
0.30
5.03
±
\pm
0.48
39.59
±
\pm
2.04
8.01
±
\pm
0.68
0.55
±
\pm
0.15
11.38
±
\pm
2.10
Best Possible (
Φ
c
\Phi_{c}
)
71.75
±
\pm
0.13
7.60
±
\pm
0.07
77.66
±
\pm
0.12
71.75
±
\pm
0.13
7.60
±
\pm
0.07
77.66
±
\pm
0.12
71.75
±
\pm
0.13
7.60
±
\pm
0.07
77.66
±
\pm
0.12
Table 12
:
Mean and standard deviation for Effective Reliability
Φ
c
\Phi_{c}
over 10 trials. All in %.
Appendix 0.K
Proof of Lemma 1
Lemma 1 states that if a model abstains “perfectly”, the introduced Effective Reliability score is equal to the VQA Accuracy.
In this section, we provide a proof of Lemma 1 in the main paper, which we repeat here for ease of understanding the proof:
Lemma 1.
The Effective Reliability score is equal to the VQA Accuracy (
Φ
c
​
(
x
)
=
A
​
c
​
c
​
(
x
)
\Phi_{c}(x)=Acc(x)
) if a model abstains (
g
⁡
(
x
)
=
0
g(x)=0
)
iff
it is incorrect (
A
​
c
​
c
​
(
x
)
=
0
Acc(x)=0
).
Distilling this to the mathematical notation:
(
g
(
x
)
=
0
↔
A
c
c
(
x
)
=
0
)
⟶
Φ
c
(
x
)
=
A
c
c
(
x
)
(g(x)=0\leftrightarrow Acc(x)=0)\longrightarrow\Phi_{c}(x)=Acc(x)
(7)
Extending Eq. 6 to both cases,
A
​
c
​
c
​
(
x
)
=
0
Acc(x)=0
and
A
​
c
​
c
​
(
x
)
>
0
Acc(x)>0
(note, that Acc cannot be smaller than 0):
Φ
c
​
(
x
)
=
{
A
​
c
​
c
​
(
x
)
if
​
g
​
(
x
)
=
1
​
and
​
A
​
c
​
c
​
(
x
)
>
0
,
−
c
if
​
g
​
(
x
)
=
1
​
and
​
A
​
c
​
c
​
(
x
)
=
0
,
0
if
​
g
​
(
x
)
=
0
​
and
​
A
​
c
​
c
​
(
x
)
>
0
,
0
if
​
g
​
(
x
)
=
0
​
and
​
A
​
c
​
c
​
(
x
)
=
0
.
\Phi_{c}(x)=\begin{cases}Acc(x)&\text{if}\ g(x)=1\ \text{and}\ Acc(x)>0,\\
-c&\text{if}\ g(x)=1\ \text{and}\ Acc(x)=0,\\
0&\text{if}\ g(x)=0\ \text{and}\ Acc(x)>0,\\
0&\text{if}\ g(x)=0\ \text{and}\ Acc(x)=0.\end{cases}
(8)
To prove Lemma 1, we must show that the condition
(
g
(
x
)
=
0
↔
A
c
c
(
x
)
=
0
)
(g(x)=0\leftrightarrow Acc(x)=0)
implies
Φ
c
​
(
x
)
=
A
​
c
​
c
​
(
x
)
\Phi_{c}(x)=Acc(x)
. The condition
(
g
(
x
)
=
0
↔
A
c
c
(
x
)
=
0
)
(g(x)=0\leftrightarrow Acc(x)=0)
simplifies Eq.
8
as the second and third line contradict the condition:
Φ
c
​
(
x
)
=
{
A
​
c
​
c
​
(
x
)
if
​
g
​
(
x
)
=
1
​
and
​
A
​
c
​
c
​
(
x
)
>
0
,
0
if
​
g
​
(
x
)
=
0
​
and
​
A
​
c
​
c
​
(
x
)
=
0
.
\Phi_{c}(x)=\begin{cases}Acc(x)&\text{if}\ g(x)=1\ \text{and}\ Acc(x)>0,\\
0&\text{if}\ g(x)=0\ \text{and}\ Acc(x)=0.\\
\end{cases}
(9)
As the
A
​
c
​
c
​
(
x
)
=
0
Acc(x)=0
, the second line can be re-written as:
Φ
c
​
(
x
)
=
{
A
​
c
​
c
​
(
x
)
if
​
g
​
(
x
)
=
1
​
and
​
A
​
c
​
c
​
(
x
)
>
0
,
A
​
c
​
c
​
(
x
)
if
​
g
​
(
x
)
=
0
​
and
​
A
​
c
​
c
​
(
x
)
=
0
.
\Phi_{c}(x)=\begin{cases}Acc(x)&\text{if}\ g(x)=1\ \text{and}\ Acc(x)>0,\\
Acc(x)&\text{if}\ g(x)=0\ \text{and}\ Acc(x)=0.\\
\end{cases}
(10)
Now, in both cases
Φ
c
​
(
x
)
=
A
​
c
​
c
​
(
x
)
\Phi_{c}(x)=Acc(x)
∎
Appendix 0.L
Relation to Conformal Prediction
Conformal prediction aims to predict a set of outputs, with a guarantee that the set contains the correct output with a specified probability
[
79
,
66
]
.
In VQA, the criterion of a set containing the “correct output” is harder to define. For example, two distinct answers might be both be true (
“yellow”,“brown”
) for
“What color are the bananas?”
, but others sets might be contradictory (
“yes”,“no”
). Further research might focus on how to best convey answer sets to users in VQA and how semantic similarity of answers should be modeled, or on the design of better criteria to determine a set-based risk.
More generally, the field of risk control, which does not require variable-size output sets, provides theoretical guarantees that a given error measure is below a tolerance level with some specified probability
[
3
,
35
]
.
[
4
]
describes how to choose a prediction threshold to satisfy a guarantee on error bound.
[
35
]
relates these guarantees to test sample accuracy based on training sample density.
We view these probabilistic guarantees on error bounds as complementary to our framework, with opportunities for future work to incorporate them both.