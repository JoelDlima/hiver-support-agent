---
title: 'Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation - Interactive'
id: cohen-fleiss-krippendorff-iaa-metrics-implementation-interactive
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:18.347420Z'
source: https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability
source_domain: mbrenndoerfer.com
fetched_at: '2026-09-15T02:28:18.343411Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation - Interactive
Back
Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation
Back
Michael Brenndoerfer
·
Published:
March 8, 2026
March 8, 2026
·
47
min read
Part of
Language AI Handbook
Data, Analytics & AI
Machine Learning
Language AI Handbook
Covers chance-corrected agreement metrics for NLP annotation reliability. Calculate Cohen's kappa, Fleiss' kappa, and Krippendorff's alpha with Python examples.
Reading Level
Choose your expertise level to adjust how many terms are explained. Beginners see more tooltips, experts see fewer to maintain reading flow. Hover over
underlined terms
for instant definitions.
Beginner
·
Maximum help
Intermediate
·
Medium help
Expert
·
Minimal help
Hide All
·
No tooltips
Article links
Make inline references clickable
On
Inter-Annotator Agreement
Link Copied
Every supervised learning system rests on labeled data, and labeled data rests on human judgment. But human judgment is neither infallible nor consistent. Two linguists reading the same sentence may disagree about whether it expresses sincere anger or mild frustration. Two medical text annotators may draw entity boundaries at different places. Two quality raters evaluating an LLM response may have completely different intuitions about what "helpful" means. When we train a model on these annotations or use them as benchmarks, we inherit whatever inconsistencies the annotation process contained.
This is not a theoretical concern. Datasets built without systematic agreement checking have been shown to contain systematic disagreements that bias model behavior in surprising ways. A model trained on sentiment data where one
annotator
was consistently stricter than others will learn to predict a blend of their standards rather than any coherent human judgment. An evaluation
benchmark
where raters frequently disagree will produce unstable leaderboard rankings that change more with the choice of raters than with the actual capability of the models being tested.
Inter-annotator agreement
(IAA) provides the statistical machinery to quantify this
reliability
. It measures how consistently multiple annotators
label
the same data, correcting for the possibility that they might agree simply by chance. Without this correction, a dataset with 90% positive examples and only two labels might show 82% "agreement" even if annotators are guessing randomly. This chapter explores the mathematics of chance-corrected agreement, from Cohen's foundational kappa for pairs of annotators through
Krippendorff's alpha
, which generalizes to any number of raters, any measurement scale, and
missing data
. Along the way, we examine how to handle the disagreements that inevitably arise, when high agreement can mislead you, and how to choose the right metric for your annotation task.
As we discussed in
Part VI: Sequence Labeling
,
named entity recognition
and part-of-speech tagging require careful annotation protocols. The metrics we develop here tell us whether those protocols are sufficiently clear to produce reproducible labels. In
Part XXXVII: Alignment and RLHF
, we saw that
human preference
data drives
reward modeling
. Before using such data, we must verify that human raters agree on what constitutes a "better" response. We'll explore preference-specific evaluation in the next chapter on
Preference Evaluation
, but the foundations we build here apply universally across all annotation tasks.
The Problem of Chance Agreement
Link Copied
Consider a simple
binary classification
task: determining whether a movie review is positive or negative. Two annotators
label
100 reviews. They agree on 75 reviews and disagree on 25. Their
raw agreement
is 75%, which seems respectable. But what if 90 of those reviews are positive, a highly imbalanced dataset?
If both annotators simply guessed "positive" every time without reading a single review, they would agree on 90 reviews by chance alone. Their 75% observed agreement would be
below
chance expectation, showing systematic disagreement masked by
class imbalance
.
Raw agreement
percentages, often called "percentage of agreement" or
P
o
P_o
, fail to tell us anything useful without accounting for how much agreement chance alone would produce.
This
prevalence
problem becomes even more acute in real-world NLP tasks.
Named entity recognition
datasets often have a high proportion of "O" (outside) tokens compared to entity tokens. If 95% of tokens have no entity
label
, two annotators who both copy-paste the majority class would agree 90% of the time. A chance-corrected coefficient would expose this false agreement immediately.
Chance-Corrected Agreement
A chance-corrected agreement coefficient compares observed agreement (
P
o
P_o
) against expected agreement by chance (
P
e
P_e
), normalized by the maximum possible improvement:
Coefficient
=
P
o
−
P
e
1
−
P
e
\text{Coefficient} = \frac{P_o - P_e}{1 - P_e}
where:
P
o
P_o
: the observed agreement proportion (the fraction of items on which raters agree)
P
e
P_e
: the expected agreement by chance (the fraction of items on which raters would agree if guessing randomly based on marginal distributions)
When observed agreement equals
chance agreement
, the coefficient is zero. When observed agreement is perfect (1.0), the coefficient reaches 1.0. Negative values indicate agreement worse than chance.
The denominator
1
−
P
e
1 - P_e
represents the maximum possible improvement over chance. If
chance agreement
is already high (say 0.9 due to
class imbalance
), there is little room for improvement, making high coefficient values difficult to achieve even with careful annotators. This explains why kappa coefficients sometimes show paradoxical behavior that we examine later. Understanding this denominator is key to understanding both the power and the limitations of chance-corrected metrics.
The logic behind chance-corrected agreement can be thought of as asking: "Given how frequently each
annotator
uses each
label
, what agreement would we expect if their decisions were statistically independent?" If
annotator
A uses the "positive"
label
70% of the time and
annotator
B uses it 60% of the time, and they are operating independently, we would expect them to both say "positive" on
0.70
×
0.60
=
0.42
0.70 \times 0.60 = 0.42
of items purely by coincidence. Any agreement beyond that reflects
reliability
in the annotation process.
Cohen's Kappa
Link Copied
Cohen's kappa
(
κ
\kappa
), introduced by Jacob Cohen in 1960, remains the most widely cited agreement statistic for exactly two raters working with categorical data. It assumes that the raters are distinct individuals with potentially different tendencies (one might be stricter or more lenient than the other), and it does not assume the categories are ordered. Virtually every annotation paper in NLP that involves two raters reports this coefficient.
Mathematical Formulation
Link Copied
The starting point for
Cohen's kappa
is the contingency table (often called the
agreement matrix
) that shows how often each rater assigned each category. For two raters and
k
k
categories, this is a
k
×
k
k \times k
matrix where cell
(
i
,
j
)
(i, j)
shows how many items rater 1 assigned to category
i
i
while rater 2 assigned them to category
j
j
.
Let
p
i
j
p_{ij}
represent the proportion of items in cell
(
i
,
j
)
(i, j)
. The observed agreement
P
o
P_o
is the sum of diagonal elements, since diagonal cells represent cases where both raters agreed:
P
o
=
∑
i
=
1
k
p
i
i
P_o = \sum_{i=1}^{k} p_{ii}
where:
p
i
i
p_{ii}
: the proportion of items that both raters assign to category
i
i
(the diagonal elements of the
agreement matrix
)
k
k
: the number of categories
P
o
P_o
: the total observed agreement (sum of diagonal proportions)
The expected agreement by chance
P
e
P_e
is computed under the assumption that the two raters' decisions are statistically independent. If rater 1 assigns fraction
p
i
+
p_{i+}
to category
i
i
, and rater 2 independently assigns fraction
p
+
i
p_{+i}
to category
i
i
, then the expected fraction of items where both agree on category
i
i
is simply the product of these marginals:
P
e
=
∑
i
=
1
k
p
i
+
⋅
p
+
i
P_e = \sum_{i=1}^{k} p_{i+} \cdot p_{+i}
where:
p
i
+
p_{i+}
: the row marginal proportion (the proportion of items rater 1 assigns to category
i
i
)
p
+
i
p_{+i}
: the column marginal proportion (the proportion of items rater 2 assigns to category
i
i
)
P
e
P_e
: the expected agreement by chance, calculated as the sum of products of marginal proportions
This is simply the probability that two independent draws from the respective marginal distributions would land on the same category, summed over all categories.
Cohen's kappa
then combines these into the familiar chance-corrected formula:
κ
=
P
o
−
P
e
1
−
P
e
=
∑
i
p
i
i
−
∑
i
p
i
+
p
+
i
1
−
∑
i
p
i
+
p
+
i
\begin{aligned}
\kappa &= \frac{P_o - P_e}{1 - P_e} \\
&= \frac{\sum_{i} p_{ii} - \sum_{i} p_{i+} p_{+i}}{1 - \sum_{i} p_{i+} p_{+i}}
\end{aligned}
where:
κ
\kappa
:
Cohen's kappa
coefficient (chance-corrected agreement ranging from
−
1
-1
to
1
1
)
P
o
P_o
: the observed agreement proportion
P
e
P_e
: the expected agreement by chance
p
i
i
p_{ii}
: the proportion of agreement on category
i
i
p
i
+
p_{i+}
,
p
+
i
p_{+i}
: the marginal proportions for category
i
i
Properties and Assumptions
Link Copied
Cohen's kappa
treats the raters as fixed entities. We are measuring agreement between these specific two people, not generalizing to a population of potential raters. This is the basic philosophical difference between
Cohen's kappa
and later metrics like
Fleiss' kappa
and
Krippendorff's alpha
: those metrics treat raters as interchangeable samples from some broader rater population.
The metric is symmetric: swapping rater 1 and rater 2 does not change the value. This makes it appropriate when there is no natural distinction between the two raters, such as two independent coders annotating the same corpus. When one rater is designated "gold standard" and the other is being evaluated, weighted agreement with the gold standard might be more informative.
Cohen's kappa
also assumes that all disagreements are equally costly. If your categories are "negative," "neutral," and "positive," kappa penalizes a "negative" vs "positive" disagreement exactly as much as a "negative" vs "neutral" disagreement. This is appropriate for nominal scales but becomes problematic for
ordinal data
.
Weighted kappa
addresses this limitation by letting you to specify that some disagreements are worse than others.
Scott's Pi
Before
Cohen's kappa
, Scott (1955) proposed
π
\pi
, which uses a single pooled
marginal distribution
rather than separate marginals for each rater.
Scott's pi
assumes both raters draw from the same underlying category distribution, which makes it appropriate when raters are interchangeable samples from a rater population rather than specific individuals. Cohen argued that raters often have different biases: one
annotator
might apply the "positive"
label
more liberally than another, making separate marginals more faithful to reality. In practice, the two metrics give similar results when rater biases are small.
Weighted Kappa for Ordinal Scales
Link Copied
When categories have a natural ordering, the gap between Cohen's standard kappa and what you care about can be substantial. Consider a 5-point toxicity scale ranging from 1 (completely benign) to 5 (highly toxic). Standard kappa treats a rater disagreement of 1 vs 2 the same as 1 vs 5, even though the latter represents a far more serious discrepancy for downstream use.
Weighted kappa
introduces a penalty matrix
w
i
j
w_{ij}
that specifies how much credit to give for each type of agreement or near-agreement. The weighted observed and expected agreement become:
P
o
w
=
∑
i
=
1
k
∑
j
=
1
k
w
i
j
⋅
p
i
j
P_o^w = \sum_{i=1}^{k} \sum_{j=1}^{k} w_{ij} \cdot p_{ij}
P
e
w
=
∑
i
=
1
k
∑
j
=
1
k
w
i
j
⋅
p
i
+
⋅
p
+
j
P_e^w = \sum_{i=1}^{k} \sum_{j=1}^{k} w_{ij} \cdot p_{i+} \cdot p_{+j}
and
weighted kappa
is:
κ
w
=
P
o
w
−
P
e
w
1
−
P
e
w
\kappa_w = \frac{P_o^w - P_e^w}{1 - P_e^w}
where:
w
i
j
w_{ij}
: the agreement weight for the pair of labels
(
i
,
j
)
(i, j)
, ranging from 1 (full credit) to 0 (no credit)
P
o
w
P_o^w
: the weighted observed agreement
P
e
w
P_e^w
: the weighted expected agreement
κ
w
\kappa_w
: the
weighted kappa
coefficient
Two common weighting schemes are linear weighting (
w
i
j
=
1
−
∣
i
−
j
∣
k
−
1
w_{ij} = 1 - \frac{|i-j|}{k-1}
) and quadratic weighting (
w
i
j
=
1
−
(
i
−
j
)
2
(
k
−
1
)
2
w_{ij} = 1 - \frac{(i-j)^2}{(k-1)^2}
). Quadratic weighting penalizes large disagreements disproportionately, which makes it the preferred choice when large errors are particularly harmful. Cohen's quadratic
weighted kappa
is identical to the intraclass
correlation coefficient
(ICC) under certain distributional assumptions, connecting it to the broader literature on
reliability
in psychology and medicine.
Interpretation Benchmarks
Link Copied
Landis and Koch (1977) proposed widely cited benchmarks for interpreting kappa values:
<
0.00
< 0.00
: Poor agreement
0.00
−
0.20
0.00 - 0.20
: Slight agreement
0.21
−
0.40
0.21 - 0.40
: Fair agreement
0.41
−
0.60
0.41 - 0.60
: Moderate agreement
0.61
−
0.80
0.61 - 0.80
: Substantial agreement
0.81
−
1.00
0.81 - 1.00
: Almost perfect agreement
However, these benchmarks face significant criticism and should not be applied mechanically. Kappa values depend heavily on
prevalence
and the difficulty of the task. A
κ
\kappa
of 0.6 might represent excellent agreement for subtle pragmatic phenomena like sarcasm detection, but poor agreement for clear-cut factual
entity recognition
where experienced annotators should achieve
κ
>
0.9
\kappa > 0.9
. The benchmarks were derived empirically from medical studies and do not generalize automatically to NLP. Always interpret kappa values in the context of your task, your annotators' expertise, and the guidelines you provided.
A more principled approach is to set task-specific thresholds before annotation begins, based on your application requirements. If a model will be deployed in a high-stakes setting, you might require
κ
>
0.8
\kappa > 0.8
before accepting any annotation. If you are exploring a new task where guidelines are still being developed,
κ
>
0.5
\kappa > 0.5
with careful analysis of disagreement patterns might be acceptable.
Fleiss' Kappa
Link Copied
Cohen's kappa
does not generalize to more than two raters. When you have a
crowdsourcing
setup with ten workers or a research project where five domain experts each annotate the full corpus, you need a different approach.
Fleiss' kappa
(1971) extends the concept to any fixed number of raters
n
≥
2
n \geq 2
, though it assumes the raters are interchangeable rather than distinct individuals.
This assumption of interchangeability is what distinguishes
Fleiss' kappa
from Cohen's. When you use
Fleiss' kappa
, you are implicitly treating your raters as random samples from a population of potential annotators, not specific individuals whose particular biases you care about. This makes it appropriate for
crowdsourcing
platforms like Amazon Mechanical Turk, where annotators are indeed sampled from a large pool.
Mathematical Structure
Link Copied
Consider
N
N
items and
k
k
categories. For each item
i
i
, let
n
i
j
n_{ij}
be the number of raters who assigned it to category
j
j
, where
∑
j
=
1
k
n
i
j
=
n
\sum_{j=1}^{k} n_{ij} = n
(each item gets exactly
n
n
ratings). The proportion of raters assigning item
i
i
to category
j
j
is:
p
i
j
=
n
i
j
n
p_{ij} = \frac{n_{ij}}{n}
where:
n
i
j
n_{ij}
: the number of raters who assigned item
i
i
to category
j
j
n
n
: the total number of raters per item
p
i
j
p_{ij}
: the proportion of raters assigning item
i
i
to category
j
j
The observed agreement for item
i
i
measures the extent to which raters agree on that specific item. Think of it as counting all pairs of raters who agreed and expressing this as a fraction of all possible rater pairs:
P
i
=
1
n
(
n
−
1
)
∑
j
=
1
k
n
i
j
(
n
i
j
−
1
)
=
1
n
(
n
−
1
)
[
(
∑
j
=
1
k
n
i
j
2
)
−
n
]
\begin{aligned}
P_i &= \frac{1}{n(n-1)} \sum_{j=1}^{k} n_{ij}(n_{ij} - 1) \\
&= \frac{1}{n(n-1)} \left[ \left(\sum_{j=1}^{k} n_{ij}^2\right) - n \right]
\end{aligned}
where:
P
i
P_i
: the extent of agreement among raters for item
i
i
(ranging from 0 to 1)
n
i
j
n_{ij}
: the count of raters assigning item
i
i
to category
j
j
n
n
: the total number of raters
k
k
: the number of categories
The first form counts agreeing pairs directly; the second simplifies computation using the sum of squares
To understand this formula, consider what happens at the extremes. If all
n
n
raters choose the same category
j
j
, then
n
i
j
=
n
n_{ij} = n
and
n
i
j
(
n
i
j
−
1
)
=
n
(
n
−
1
)
n_{ij}(n_{ij} - 1) = n(n-1)
. The sum equals
n
(
n
−
1
)
n(n-1)
and
P
i
=
1
P_i = 1
. If raters split perfectly (each choosing a different category), then
n
i
j
=
1
n_{ij} = 1
for each
j
j
and
n
i
j
(
n
i
j
−
1
)
=
0
n_{ij}(n_{ij} - 1) = 0
for all
j
j
, giving
P
i
=
0
P_i = 0
.
The mean observed agreement across all
N
N
items is:
P
o
=
1
N
∑
i
=
1
N
P
i
P_o = \frac{1}{N} \sum_{i=1}^{N} P_i
where:
P
o
P_o
: the mean observed agreement across all items
N
N
: the total number of items being rated
P
i
P_i
: the agreement score for item
i
i
The
chance agreement
P
e
P_e
uses the proportion of all assignments falling into each category. This is a single pooled distribution across all raters, which reflects the interchangeability assumption:
P
j
=
1
N
⋅
n
∑
i
=
1
N
n
i
j
P_j = \frac{1}{N \cdot n} \sum_{i=1}^{N} n_{ij}
P
e
=
∑
j
=
1
k
P
j
2
P_e = \sum_{j=1}^{k} P_j^2
where:
P
j
P_j
: the overall proportion of assignments to category
j
j
across all items and raters
P
e
P_e
: the expected
chance agreement
(the sum of squared category proportions)
The intuition for
P
e
=
∑
j
P
j
2
P_e = \sum_j P_j^2
is clean: if we sampled two raters at random and both assigned labels independently from the pooled distribution, the probability they would pick the same category
j
j
is
P
j
⋅
P
j
=
P
j
2
P_j \cdot P_j = P_j^2
. Summing over all categories gives the total
chance agreement
.
Fleiss' kappa
is then:
κ
F
=
P
o
−
P
e
1
−
P
e
\kappa_F = \frac{P_o - P_e}{1 - P_e}
where:
κ
F
\kappa_F
:
Fleiss' kappa
coefficient
P
o
P_o
: the mean observed agreement across items
P
e
P_e
: the expected
chance agreement
based on category proportions
Key Differences from Cohen's Kappa
Link Copied
The most important practical difference between Fleiss' and
Cohen's kappa
is the choice of marginal distributions.
Cohen's kappa
uses separate marginals for each rater (
p
i
+
p_{i+}
for rater 1 and
p
+
i
p_{+i}
for rater 2). This reflects the fact that rater 1 might use "positive" 70% of the time while rater 2 uses it only 50% of the time.
Fleiss' kappa
uses a single pooled marginal (
P
j
P_j
), treating all raters as if they draw from the same distribution. This pooled approach is identical to what
Scott's pi
uses for two raters.
This has a subtle but important consequence. If you have exactly two raters with different biases and you apply
Fleiss' kappa
, you get
Scott's pi
rather than
Cohen's kappa
. The two coefficients can give substantially different values when rater biases differ substantially. When choosing between them, consider whether rater-specific tendencies are meaningful information (use
Cohen's kappa
) or noise to be averaged away (use
Fleiss' kappa
or
Krippendorff's alpha
).
When you have many raters or view raters as interchangeable samples from a larger population,
Fleiss' kappa
is the natural choice. In
crowdsourcing
research, it is particularly common because the identity of individual workers is less important than the overall
reliability
of the pool.
Krippendorff's Alpha
Link Copied
Krippendorff's alpha
(
α
\alpha
) represents the most general agreement coefficient available. It accommodates:
Any number of raters (varying per item if needed)
Any number of categories
Any measurement scale (nominal, ordinal, interval, ratio)
Missing data
, where some items receive fewer ratings than others
This flexibility makes it the preferred metric for complex annotation schemes in modern NLP, particularly when different items might have different numbers of ratings, when using ordinal scales like Likert items, or when the annotation project spans a long period where not all raters annotate all items. Klaus Krippendorff, who introduced the metric in 1970 and refined it extensively in subsequent decades, designed it explicitly for the messiness of real-world content analysis.
The General Form
Link Copied
Krippendorff's alpha
uses a disagreement-based formulation rather than an agreement-based one, but the underlying logic is identical to the
chance-correction framework
we have seen throughout this chapter:
α
=
1
−
D
o
D
e
\alpha = 1 - \frac{D_o}{D_e}
where:
α
\alpha
:
Krippendorff's alpha
coefficient
D
o
D_o
: the observed disagreement among raters
D
e
D_e
: the expected disagreement by chance
When
D
o
=
0
D_o = 0
(perfect agreement),
α
=
1
\alpha = 1
. When
D
o
=
D
e
D_o = D_e
(agreement equals chance),
α
=
0
\alpha = 0
. When
D
o
>
D
e
D_o > D_e
(worse than chance),
α
<
0
\alpha < 0
.
For
nominal data
(categories without order), the observed disagreement for an item is the proportion of rater pairs that disagree:
D
o
=
1
n
(
n
−
1
)
∑
c
n
c
(
n
−
n
c
)
D_o = \frac{1}{n(n-1)} \sum_{c} n_c (n - n_c)
where:
D
o
D_o
: the observed disagreement for an item
n
c
n_c
: the count of raters choosing category
c
c
n
n
: the total number of raters for that item
The sum is taken over all categories
c
c
The expected disagreement assumes a
multinomial distribution
based on the overall category frequencies across all data. If the probability of any given annotation being category
c
c
is
π
c
\pi_c
, then the probability that two independent annotations disagree is:
D
e
=
1
−
∑
c
π
c
2
D_e = 1 - \sum_{c} \pi_c^2
where:
D
e
D_e
: the expected disagreement by chance
π
c
\pi_c
: the overall proportion of assignments to category
c
c
across all data
The term
∑
c
π
c
2
\sum_{c} \pi_c^2
represents the probability of
chance agreement
(the same formula as
P
e
P_e
in
Fleiss' kappa
)
Notice that for
nominal data
with complete observations,
Krippendorff's alpha
and
Fleiss' kappa
give identical results. The differences between them emerge when data is missing or when using non-nominal measurement scales.
Handling Missing Data
Link Copied
This is where
Krippendorff's alpha
truly distinguishes itself. Real annotation projects almost always have
missing data
. Annotators drop out, items are too difficult for some raters, or different items are assigned to different subsets of raters.
Cohen's kappa
and
Fleiss' kappa
require complete data for each item.
Krippendorff's alpha
handles missing data through coincidence matrices rather than contingency tables. Instead of requiring every rater to
label
every item, we compute the observed disagreement from all pairs of observations that are present. For each item
i
i
with
m
i
≥
2
m_i \geq 2
valid ratings, we consider all ordered pairs of raters and record which categories they chose. Items with fewer than 2 valid ratings are simply skipped.
For
m
m
items with varying numbers of raters, we construct a
coincidence matrix
where cell
(
c
,
k
)
(c, k)
contains the number of times any rater pair for any item assigned one to category
c
c
and the other to category
k
k
. The diagonal contains agreements; off-diagonals contain disagreements. This matrix is symmetric, and each item with
n
i
n_i
raters contributes
n
i
(
n
i
−
1
)
n_i(n_i - 1)
entries.
The resulting
coincidence matrix
is a sufficient statistic for computing both
D
o
D_o
and
D
e
D_e
, regardless of how many ratings each item has. This is the elegant mathematical property that lets alpha handle arbitrary missingness patterns without any special-casing.
Weighting Schemes
Link Copied
For ordinal, interval, or ratio scales, not all disagreements are equal. A 5-star quality rater who gives 3 stars while their colleague gives 4 stars is closer to agreement than one who gives 1 star.
Krippendorff's alpha
incorporates a difference function
δ
c
k
2
\delta_{ck}^2
that weights disagreements by their distance:
α
=
1
−
∑
c
,
k
o
c
k
δ
c
k
2
∑
c
,
k
e
c
k
δ
c
k
2
\alpha = 1 - \frac{\sum_{c,k} o_{ck} \delta_{ck}^2}{\sum_{c,k} e_{ck} \delta_{ck}^2}
where:
o
c
k
o_{ck}
: the observed coincidences between categories
c
c
and
k
k
e
c
k
e_{ck}
: the expected coincidences between categories
c
c
and
k
k
δ
c
k
2
\delta_{ck}^2
: the squared distance between categories
c
c
and
k
k
(weighting function)
The numerator sums observed disagreements weighted by distance; the denominator sums expected disagreements weighted by distance
Different measurement scales suggest different distance functions:
Nominal:
δ
c
k
2
=
0
\delta_{ck}^2 = 0
if
c
=
k
c = k
, else
1
1
(binary disagreement, all errors equal)
Ordinal:
δ
c
k
2
=
(
∑
g
=
min
⁡
(
c
,
k
)
max
⁡
(
c
,
k
)
n
g
−
n
c
+
n
k
2
)
2
\delta_{ck}^2 = \left(\sum_{g=\min(c,k)}^{\max(c,k)} n_g - \frac{n_c + n_k}{2}\right)^2
(rank-based distances)
Interval:
δ
c
k
2
=
(
c
−
k
)
2
\delta_{ck}^2 = (c - k)^2
(squared difference in values)
Ratio:
δ
c
k
2
=
(
c
−
k
c
+
k
)
2
\delta_{ck}^2 = \left(\frac{c - k}{c + k}\right)^2
(squared relative difference)
For Likert-scale ratings of LLM response quality, interval alpha is usually appropriate because the scale is treated as having equal spacing between levels. For judgments that have a natural zero point and where the ratio between values is meaningful (such as response latency in milliseconds), ratio alpha is more appropriate. The choice of
distance function
should be driven by the measurement theory underlying your scale, not by which choice makes the number look best.
Worked Example
Link Copied
Let's calculate all three metrics on a concrete example. Suppose three annotators (A, B, C)
label
10 sentences for sentiment: Positive (P), Neutral (N), or Negative (G).
Sentiment annotations for 10 items by three annotators.
Item
A
B
C
1
P
P
P
2
P
P
N
3
N
N
N
4
P
P
P
5
N
P
N
6
G
G
G
7
P
N
P
8
N
N
N
9
P
P
P
10
G
P
G
Six items (1, 3, 4, 6, 8, 9) are unanimously agreed upon. The four disagreement items (2, 5, 7, 10) each have a 2-1 split, with different categories causing trouble in each case.
Cohen's Kappa (A vs B)
Link Copied
First, construct the
agreement matrix
between A and B:
Agreement matrix between annotators A and B.
B:P
B:N
B:G
A:P
4
1
0
A:N
1
2
0
A:G
1
0
1
Observed agreement:
P
o
=
4
+
2
+
1
10
=
0.7
\begin{aligned}
P_o &= \frac{4 + 2 + 1}{10} \\
&= 0.7
\end{aligned}
Row marginals for A:
p
P
+
=
0.5
p_{P+} = 0.5
,
p
N
+
=
0.3
p_{N+} = 0.3
,
p
G
+
=
0.2
p_{G+} = 0.2
Column marginals for B:
p
+
P
=
0.6
p_{+P} = 0.6
,
p
+
N
=
0.3
p_{+N} = 0.3
,
p
+
G
=
0.1
p_{+G} = 0.1
Expected agreement:
P
e
=
(
0.5
×
0.6
)
+
(
0.3
×
0.3
)
+
(
0.2
×
0.1
)
=
0.30
+
0.09
+
0.02
=
0.41
\begin{aligned}
P_e &= (0.5 \times 0.6) + (0.3 \times 0.3) + (0.2 \times 0.1) \\
&= 0.30 + 0.09 + 0.02 \\
&= 0.41
\end{aligned}
Cohen's kappa
:
κ
=
0.7
−
0.41
1
−
0.41
=
0.29
0.59
≈
0.492
\begin{aligned}
\kappa &= \frac{0.7 - 0.41}{1 - 0.41} \\
&= \frac{0.29}{0.59} \\
&\approx 0.492
\end{aligned}
This falls in the "moderate" range. Notice that A uses "Negative" 20% of the time while B uses it only 10% of the time. This rater-level difference in base rates is exactly what
Cohen's kappa
captures through separate marginals.
Fleiss' Kappa (All Three)
Link Copied
For
Fleiss' kappa
, we calculate
P
i
P_i
for each item:
Item 1 (P,P,P):
P
1
=
1
3
(
2
)
(
3
2
−
3
)
=
6
6
=
1.0
\begin{aligned}
P_1 &= \frac{1}{3(2)}(3^2 - 3) \\
&= \frac{6}{6} \\
&= 1.0
\end{aligned}
Item 2 (P,P,N):
P
2
=
1
6
(
2
2
+
1
2
+
0
−
3
)
=
3
6
=
0.333
\begin{aligned}
P_2 &= \frac{1}{6}(2^2 + 1^2 + 0 - 3) \\
&= \frac{3}{6} \\
&= 0.333
\end{aligned}
Item 3 (N,N,N):
1.0
1.0
Item 4 (P,P,P):
1.0
1.0
Item 5 (N,P,N):
P
5
=
1
6
(
1
2
+
2
2
−
3
)
=
2
6
=
0.333
\begin{aligned}
P_5 &= \frac{1}{6}(1^2 + 2^2 - 3) \\
&= \frac{2}{6} \\
&= 0.333
\end{aligned}
Item 6 (G,G,G):
1.0
1.0
Item 7 (P,N,P):
P
7
=
1
6
(
2
2
+
1
2
−
3
)
=
0.333
\begin{aligned}
P_7 &= \frac{1}{6}(2^2 + 1^2 - 3) \\
&= 0.333
\end{aligned}
Item 8 (N,N,N):
1.0
1.0
Item 9 (P,P,P):
1.0
1.0
Item 10 (G,P,G):
P
10
=
1
6
(
1
2
+
2
2
−
3
)
=
0.333
\begin{aligned}
P_{10} &= \frac{1}{6}(1^2 + 2^2 - 3) \\
&= 0.333
\end{aligned}
Mean observed agreement:
P
o
=
1
10
(
1
+
0.333
+
1
+
1
+
0.333
+
1
+
0.333
+
1
+
1
+
0.333
)
=
7.332
10
=
0.733
\begin{aligned}
P_o &= \frac{1}{10}(1 + 0.333 + 1 + 1 + 0.333 + 1 + 0.333 + 1 + 1 + 0.333) \\
&= \frac{7.332}{10} \\
&= 0.733
\end{aligned}
Category proportions (total assignments = 10 items
×
\times
3 raters = 30):
P
P
=
15
/
30
=
0.5
P_P = 15/30 = 0.5
P
N
=
10
/
30
=
0.333
P_N = 10/30 = 0.333
P
G
=
5
/
30
=
0.167
P_G = 5/30 = 0.167
Expected agreement:
P
e
=
0.5
2
+
0.333
2
+
0.167
2
=
0.25
+
0.111
+
0.028
=
0.389
\begin{aligned}
P_e &= 0.5^2 + 0.333^2 + 0.167^2 \\
&= 0.25 + 0.111 + 0.028 \\
&= 0.389
\end{aligned}
Fleiss' kappa
:
κ
F
=
0.733
−
0.389
1
−
0.389
=
0.344
0.611
≈
0.563
\begin{aligned}
\kappa_F &= \frac{0.733 - 0.389}{1 - 0.389} \\
&= \frac{0.344}{0.611} \\
&\approx 0.563
\end{aligned}
Krippendorff's Alpha
Link Copied
For
nominal data
with 3 raters per item, we build the
coincidence matrix
. Each item contributes ordered pairs of ratings, one per ordered pair of raters.
Item 5: A(N), B(P), C(N). Ordered pairs:
(
A
,
B
)
:
N
(A,B):N
-
P
P
,
(
A
,
C
)
:
N
(A,C):N
-
N
N
,
(
B
,
A
)
:
P
(B,A):P
-
N
N
,
(
B
,
C
)
:
P
(B,C):P
-
N
N
,
(
C
,
A
)
:
N
(C,A):N
-
N
N
,
(
C
,
B
)
:
N
(C,B):N
-
P
P
. This contributes
o
N
P
+
=
2
o_{NP} += 2
,
o
P
N
+
=
2
o_{PN} += 2
,
o
N
N
+
=
2
o_{NN} += 2
.
Counting all contributions:
o
P
P
o_{PP}
: Items 1(6), 2(2), 4(6), 7(2), 9(6)
=
22
= 22
o
N
N
o_{NN}
: Items 3(6), 5(2), 8(6)
=
14
= 14
o
G
G
o_{GG}
: Items 6(6), 10(2)
=
8
= 8
o
P
N
=
o
N
P
o_{PN} = o_{NP}
: Items 2(2), 5(2), 7(2)
=
6
= 6
each
o
P
G
=
o
G
P
o_{PG} = o_{GP}
: Item 10(2)
=
2
= 2
each
o
N
G
=
o
G
N
o_{NG} = o_{GN}
: None
=
0
= 0
Total:
22
+
14
+
8
+
6
+
6
+
2
+
2
=
60
22 + 14 + 8 + 6 + 6 + 2 + 2 = 60
(which matches
10
×
3
×
2
=
60
10 \times 3 \times 2 = 60
ordered pairs).
Observed disagreement:
D
o
=
o
P
N
+
o
N
P
+
o
P
G
+
o
G
P
60
=
6
+
6
+
2
+
2
60
=
16
60
=
0.267
\begin{aligned}
D_o &= \frac{o_{PN} + o_{NP} + o_{PG} + o_{GP}}{60} \\
&= \frac{6 + 6 + 2 + 2}{60} \\
&= \frac{16}{60} \\
&= 0.267
\end{aligned}
Expected disagreement:
D
e
=
1
−
(
P
P
2
+
P
N
2
+
P
G
2
)
=
1
−
(
0.5
2
+
0.333
2
+
0.167
2
)
=
1
−
0.389
=
0.611
\begin{aligned}
D_e &= 1 - (P_P^2 + P_N^2 + P_G^2) \\
&= 1 - (0.5^2 + 0.333^2 + 0.167^2) \\
&= 1 - 0.389 \\
&= 0.611
\end{aligned}
Alpha:
α
=
1
−
0.267
0.611
=
1
−
0.437
=
0.563
\begin{aligned}
\alpha &= 1 - \frac{0.267}{0.611} \\
&= 1 - 0.437 \\
&= 0.563
\end{aligned}
For this case with complete data and nominal categories,
Fleiss' kappa
and
Krippendorff's alpha
give the same value (0.563), as theory predicts.
Cohen's kappa
between specific rater pairs varies. The A vs B pair showed
κ
=
0.492
\kappa = 0.492
; A vs C and B vs C would produce different values because each pair has different marginal distributions.
Code Implementation
Link Copied
Let's implement these calculations in Python, verifying our manual computation and showing library usage. The code also handles a missing-data scenario that illustrates
Krippendorff's alpha
's unique capabilities.
In
[
4
]:
Code
import
numpy
as
np
# Define our annotation data: 10 items, 3 annotators (A, B, C)
# Categories: 0=Negative(G), 1=Neutral(N), 2=Positive(P)
annotations
=
np
.
array
(
[
[
2
,
2
,
2
],
# Item 1: P,P,P
[
2
,
2
,
1
],
# Item 2: P,P,N
[
1
,
1
,
1
],
# Item 3: N,N,N
[
2
,
2
,
2
],
# Item 4: P,P,P
[
1
,
2
,
1
],
# Item 5: N,P,N
[
0
,
0
,
0
],
# Item 6: G,G,G
[
2
,
1
,
2
],
# Item 7: P,N,P
[
1
,
1
,
1
],
# Item 8: N,N,N
[
2
,
2
,
2
],
# Item 9: P,P,P
[
0
,
2
,
0
],
# Item 10: G,P,G
]
)
n_items
,
n_raters
=
annotations
.
shape
categories
=
np
.
unique
(
annotations
)
k
=
len
(
categories
)
Now we calculate
Cohen's kappa
between annotators A (column 0) and B (column 1).
In
[
5
]:
Code
# Cohen's Kappa between A and B
rater_a
=
annotations
[:,
0
]
rater_b
=
annotations
[:,
1
]
# Using sklearn
kappa_sklearn
=
cohen_kappa_score
(
rater_a
,
rater_b
)
# Manual calculation for verification
def
cohens_kappa_manual
(
rater1
,
rater2
,
categories
):
n
=
len
(
rater1
)
# Agreement matrix
agreement
=
np
.
zeros
((
len
(
categories
),
len
(
categories
)))
for
i
in
range
(
n
):
idx1
=
np
.
where
(
categories
==
rater1
[
i
])[
0
][
0
]
idx2
=
np
.
where
(
categories
==
rater2
[
i
])[
0
][
0
]
agreement
[
idx1
,
idx2
]
+=
1
agreement
=
agreement
/
n
# Convert to proportions
# Observed agreement
p_o
=
np
.
trace
(
agreement
)
# Expected agreement (marginals)
p_i_plus
=
np
.
sum
(
agreement
,
axis
=
1
)
p_plus_j
=
np
.
sum
(
agreement
,
axis
=
0
)
p_e
=
np
.
sum
(
p_i_plus
*
p_plus_j
)
kappa
=
(
p_o
-
p_e
)
/
(
1
-
p_e
)
return
kappa
,
p_o
,
p_e
kappa_manual
,
p_o
,
p_e
=
cohens_kappa_manual
(
rater_a
,
rater_b
,
categories
)
Out
[
6
]:
Console
Cohen's Kappa (A vs B) using sklearn: 0.492
Manual calculation: kappa = (0.70 - 0.41) / (1 - 0.41) = 0.492
The manual calculation confirms our earlier arithmetic, showing moderate agreement between annotators A and B.
Out
[
7
]:
Visualization
Agreement matrix between annotators A and B showing the count of label assignments in each category pair. Diagonal cells (upper-left to lower-right) represent items where both raters agreed. The three off-diagonal disagreements are spread evenly across category boundaries, with no single category pair accounting for all errors.
Next, we implement
Fleiss' kappa
for all three raters.
In
[
8
]:
Code
def
fleiss_kappa
(
annotations
,
categories
):
"""
Calculate Fleiss' kappa for multiple raters.
annotations: n_items x n_raters array
"""
n_items
,
n_raters
=
annotations
.
shape
k
=
len
(
categories
)
# Count matrix: n_items x k
count_matrix
=
np
.
zeros
((
n_items
,
k
))
for
i
in
range
(
n_items
):
for
j
in
range
(
n_raters
):
cat_idx
=
np
.
where
(
categories
==
annotations
[
i
,
j
])[
0
][
0
]
count_matrix
[
i
,
cat_idx
]
+=
1
# P_i for each item: proportion of agreeing ordered rater pairs
P_i
=
(
np
.
sum
(
count_matrix
**
2
,
axis
=
1
)
-
n_raters
)
/
(
n_raters
*
(
n_raters
-
1
)
)
P_bar
=
np
.
mean
(
P_i
)
# Overall proportion of assignments to each category
P_j
=
np
.
sum
(
count_matrix
,
axis
=
0
)
/
(
n_items
*
n_raters
)
# Expected agreement
P_e
=
np
.
sum
(
P_j
**
2
)
kappa
=
(
P_bar
-
P_e
)
/
(
1
-
P_e
)
if
(
1
-
P_e
)
!=
0
else
0
return
kappa
,
P_bar
,
P_e
,
P_j
,
P_i
,
count_matrix
kappa_fleiss
,
p_bar
,
p_e_fleiss
,
cat_props
,
P_i_values
,
count_mat
=
(
fleiss_kappa
(
annotations
,
categories
)
)
Out
[
9
]:
Console
Fleiss' Kappa: 0.564
Observed agreement (P_bar): 0.733
Expected agreement (P_e): 0.389
Category proportions: {'G': '0.167', 'N': '0.333', 'P': '0.500'}
Fleiss' kappa
shows moderate agreement across all three raters, slightly higher than the pairwise
Cohen's kappa
between A and B. Pooling all three raters raises the observed agreement while producing a slightly lower chance-agreement baseline for this dataset.
Out
[
10
]:
Visualization
Per-item agreement scores ($P_i$) for the Fleiss kappa calculation. Items 1, 3, 4, 6, 8, and 9 show perfect unanimous agreement ($P_i = 1.0$, shown in teal), while the four disagreement items (2, 5, 7, 10) each score 0.33, corresponding to a 2-vs-1 split among the three raters. The horizontal dashed line marks the mean observed agreement $P_o = 0.733$.
Now we implement
Krippendorff's alpha
, which requires building the
coincidence matrix
.
In
[
11
]:
Code
def
krippendorff_alpha
(
annotations
,
categories
,
metric
=
"
nominal
"
):
"""
Calculate Krippendorff's alpha.
Handles varying numbers of raters per item (missing data via NaN).
"""
n_items
,
n_raters
=
annotations
.
shape
k
=
len
(
categories
)
# Build coincidence matrix
coincidence
=
np
.
zeros
((
k
,
k
))
for
i
in
range
(
n_items
):
# Get valid annotations for this item (non-NaN if we had missing data)
valid
=
annotations
[
i
,
:]
n_valid
=
len
(
valid
)
# All ordered pairs of raters
for
r1
,
r2
in
itertools
.
product
(
range
(
n_valid
),
range
(
n_valid
)):
if
r1
!=
r2
:
c1
=
np
.
where
(
categories
==
valid
[
r1
])[
0
][
0
]
c2
=
np
.
where
(
categories
==
valid
[
r2
])[
0
][
0
]
coincidence
[
c1
,
c2
]
+=
1
total_coincidences
=
np
.
sum
(
coincidence
)
# Observed disagreement (for nominal: proportion of off-diagonal)
if
metric
==
"
nominal
"
:
D_o
=
(
total_coincidences
-
np
.
trace
(
coincidence
))
/
total_coincidences
else
:
raise
NotImplementedError
(
"
Only nominal metric implemented here
"
)
# Expected disagreement based on marginals
category_counts
=
np
.
sum
(
coincidence
,
axis
=
1
)
n_total
=
np
.
sum
(
category_counts
)
probs
=
category_counts
/
n_total
D_e
=
1
-
np
.
sum
(
probs
**
2
)
alpha
=
1
-
(
D_o
/
D_e
)
if
D_e
!=
0
else
0
return
alpha
,
D_o
,
D_e
,
coincidence
alpha
,
d_o
,
d_e
,
coin_mat
=
krippendorff_alpha
(
annotations
,
categories
)
Out
[
12
]:
Console
Krippendorff's Alpha: 0.564
Observed disagreement (D_o): 0.267
Expected disagreement (D_e): 0.611
Krippendorff's alpha
matches
Fleiss' kappa
in this case because we have complete data, fixed numbers of raters, and nominal categories. The advantage of alpha becomes apparent with
missing data
or ordinal scales.
Out
[
13
]:
Visualization
Coincidence matrix for Krippendorff's alpha, showing the frequency of ordered rater-pair label combinations across all items. Diagonal elements represent agreements between rater pairs. The dominant off-diagonal entries (P-N and N-P) indicate that positive-vs-neutral confusion accounts for most disagreements, while positive-negative confusion is rare.
Out
[
14
]:
Visualization
Side-by-side comparison of the three inter-annotator agreement metrics on the worked example. Cohen's kappa for the A-B pair falls in the moderate range, which reflects the specific divergence in base rates between those two annotators. Fleiss kappa and Krippendorff alpha agree to three decimal places because the data is complete and nominal, placing the three-rater agreement in the moderate range according to Landis-Koch benchmarks. Background bands show the conventional interpretation regions.
Let's demonstrate handling
missing data
, a key strength of
Krippendorff's alpha
. We remove two ratings and observe that alpha remains computable and close to the complete-data value.
In
[
15
]:
Code
# Simulate missing data: remove some annotations
annotations_missing
=
annotations
.
copy
().
astype
(
float
)
annotations_missing
[
2
,
1
]
=
np
.
nan
# Item 3, rater B missing
annotations_missing
[
7
,
2
]
=
np
.
nan
# Item 8, rater C missing
def
krippendorff_alpha_missing
(
annotations
,
categories
):
"""
Alpha with missing data handling.
"""
n_items
,
n_raters
=
annotations
.
shape
k
=
len
(
categories
)
coincidence
=
np
.
zeros
((
k
,
k
))
for
i
in
range
(
n_items
):
# Filter out NaN values
valid
=
annotations
[
i
,
~
np
.
isnan
(
annotations
[
i
,
:])]
n_valid
=
len
(
valid
)
if
n_valid
<
2
:
continue
for
r1
,
r2
in
itertools
.
product
(
range
(
n_valid
),
range
(
n_valid
)):
if
r1
!=
r2
:
c1
=
np
.
where
(
categories
==
valid
[
r1
])[
0
][
0
]
c2
=
np
.
where
(
categories
==
valid
[
r2
])[
0
][
0
]
coincidence
[
c1
,
c2
]
+=
1
total
=
np
.
sum
(
coincidence
)
D_o
=
(
total
-
np
.
trace
(
coincidence
))
/
total
probs
=
np
.
sum
(
coincidence
,
axis
=
1
)
/
total
D_e
=
1
-
np
.
sum
(
probs
**
2
)
return
1
-
(
D_o
/
D_e
)
alpha_missing
=
krippendorff_alpha_missing
(
annotations_missing
,
categories
)
Out
[
16
]:
Console
Annotations with missing data (NaN):
[[ 2.  2.  2.]
 [ 2.  2.  1.]
 [ 1. nan  1.]
 [ 2.  2.  2.]
 [ 1.  2.  1.]
 [ 0.  0.  0.]
 [ 2.  1.  2.]
 [ 1.  1. nan]
 [ 2.  2.  2.]
 [ 0.  2.  0.]]

Krippendorff's Alpha with missing data: 0.467
Original (complete data): 0.564
The alpha coefficient remains stable even with missing annotations. This makes it suitable for real-world annotation projects where not every rater labels every item.
Cohen's kappa
and
Fleiss' kappa
would require you to either drop items with
missing data
or impute values before computation.
Let's now compute pairwise
Cohen's kappa
for all three
annotator
pairs to show how agreement varies across pairs.
In
[
17
]:
Code
# Compute pairwise Cohen's kappa for all annotator pairs
pair_labels
=
[
"
A vs B
"
,
"
A vs C
"
,
"
B vs C
"
]
pair_kappas
=
[]
pair_p_o
=
[]
pair_p_e
=
[]
for
r1
,
r2
in
[(
0
,
1
),
(
0
,
2
),
(
1
,
2
)]:
kappa_val
,
po
,
pe
=
cohens_kappa_manual
(
annotations
[:,
r1
],
annotations
[:,
r2
],
categories
)
pair_kappas
.
append
(
kappa_val
)
pair_p_o
.
append
(
po
)
pair_p_e
.
append
(
pe
)
Out
[
18
]:
Console
A vs B: kappa=0.492  (P_o=0.700, P_e=0.410)
A vs C: kappa=0.844  (P_o=0.900, P_e=0.360)
B vs C: kappa=0.355  (P_o=0.600, P_e=0.380)
Out
[
19
]:
Visualization
Pairwise Cohen's kappa values for all three annotator combinations. The A vs C pair shows the highest agreement among binary comparisons, while A vs B shows the lowest. The variation across pairs illustrates why aggregating over raters with Fleiss kappa or Krippendorff alpha provides a more stable summary when you have more than two annotators.
Handling Disagreement
Link Copied
High
inter-annotator agreement
validates our annotation scheme, but what happens when agreement is low? Disagreement is not always noise. Sometimes it signals ambiguous examples, underspecified guidelines, or subjective phenomena. Understanding and handling disagreement appropriately is as important as measuring it.
Adjudication and Majority Voting
Link Copied
The simplest approach to resolving disagreement is
adjudication
: a third expert reviews cases where raters disagree and determines the "correct"
label
. This works well for objective tasks with clear gold standards (such as
syntactic parsing
or coreference resolution) but risks imposing artificial certainty on subjective phenomena. When a quality rater says a response is "helpful" and another says it is "not helpful,"
adjudication
forces a binary choice that erases real ambiguity.
For multi-rater scenarios,
majority voting
selects the most common
label
. With two raters, this requires a tie-breaker rule.
Majority voting
preserves the most likely interpretation but discards information about uncertainty. If two annotators rate sentiment as Positive and Neutral while a third says Negative,
majority voting
yields Positive, but the disagreement suggests this might be a borderline case that a model should approach with calibrated uncertainty rather than confident classification.
Soft Labels and Probabilistic Targets
Link Copied
Rather than forcing hard choices, we can preserve disagreement as
soft labels
. If three annotators
label
an item as [Positive, Positive, Neutral], the soft
label
becomes a probability distribution:
P
(
Positive
)
=
0.67
P(\text{Positive}) = 0.67
,
P
(
Neutral
)
=
0.33
P(\text{Neutral}) = 0.33
.
Training models on
soft labels
rather than hard majority votes captures the nuance of borderline cases. Research on
label smoothing
and distribution matching has shown that models trained with soft targets can produce better-calibrated predictions. As we discussed in
Part XXXVII: Alignment and RLHF
, reward models are often trained on preference probabilities derived from multiple human judgments rather than binary choices. This approach acknowledges that some comparisons are close calls and that a model should assign similar scores to the competing responses.
The degree of annotation disagreement can itself be used as a signal. Items where annotators consistently disagree might indicate that the underlying construct is inherently ambiguous, or that the item sits at a
decision boundary
in the feature space. Both interpretations are informative for model design: the first suggests we should collect more annotations or refine the task definition, the second suggests the model should be allowed to output uncertainty.
Modeling Uncertainty
Link Copied
Low agreement items might deserve different treatment during training. Items with high
annotator
disagreement can be:
Weighted down in the loss function to reduce their influence on learned representations
Excluded from training if disagreement exceeds a threshold, keeping only high-quality signal
Flagged for guideline refinement when systematic disagreement patterns emerge
Treated as belonging to a separate "ambiguous" class, giving the model an explicit way to express uncertainty
In evaluation, disagreement-aware metrics report both performance on high-agreement items (where labels are reliable) and performance on the full dataset. A model that performs well only on unambiguous items might be exploiting superficial features rather than understanding the task. Similarly, a
benchmark
where 30% of items have majority-vote accuracy below 60% among human raters should not be treated as having a clean gold standard.
Guideline Iteration
Link Copied
Persistent disagreement often indicates guideline deficiencies. When annotators systematically disagree on entity boundaries in
NER
or on whether a statement constitutes a "
hallucination
," the annotation guidelines need clarification.
Iterative annotation
, where initial rounds inform guideline refinement, typically improves kappa scores in subsequent rounds.
However, be cautious of over-fitting guidelines to specific annotators. If you refine guidelines until two particular annotators agree, you may have simply matched the idiosyncrasies of those two people, not improved generalizability. Ideal guideline development involves diverse annotators, multiple annotation rounds, and explicit documentation of edge cases so that future annotators can apply the same standards.
A practical workflow for high-quality annotation projects looks like this. First, annotate a small pilot batch (100-200 items) and measure kappa. Second, analyze disagreement patterns to identify which item types, which category distinctions, or which
annotator
pairs are most problematic. Third, update guidelines to address specific sources of confusion. Fourth, annotate a second pilot batch and measure kappa again. Only once kappa exceeds your threshold should you proceed with the full dataset. This iterative approach front-loads cost but dramatically reduces the risk of discovering systematic quality problems after annotating tens of thousands of items.
Limitations and Impact
Link Copied
Chance-corrected agreement coefficients, while needed tools in the NLP practitioner's toolkit, suffer from well-documented paradoxes and limitations. Understanding these issues is not just academic: they determine which coefficient you should choose for a given task and how you should report and interpret your results.
The Prevalence Problem
Link Copied
When class distributions are highly skewed, kappa coefficients can be surprisingly low even with high
raw agreement
. Consider a medical diagnosis task where 95% of cases are "healthy." Two doctors might agree on 90% of cases (both saying healthy) but disagree on the 5% who are sick.
Raw agreement
is 90%, but if they randomly guessed healthy 95% of the time,
chance agreement
would be:
P
e
=
0.95
2
+
0.05
2
=
0.9025
+
0.0025
=
0.905
\begin{aligned}
P_e &= 0.95^2 + 0.05^2 \\
&= 0.9025 + 0.0025 \\
&= 0.905
\end{aligned}
The kappa would be:
κ
=
0.90
−
0.905
1
−
0.905
=
−
0.005
0.095
≈
−
0.05
\begin{aligned}
\kappa &= \frac{0.90 - 0.905}{1 - 0.905} \\
&= \frac{-0.005}{0.095} \\
&\approx -0.05
\end{aligned}
This result suggests negative agreement despite 90% accuracy. The paradox arises because
chance agreement
is already 90.5% given the
class imbalance
, leaving essentially no room for improvement. The kappa denominator
1
−
P
e
=
0.095
1 - P_e = 0.095
amplifies any noise in the numerator.
The implication for NLP practice is significant. For
sequence labeling
tasks like
NER
, where most tokens are "outside" entities, kappa values will routinely look poor even for high-quality annotators. This
prevalence paradox
means kappa is unreliable for heavily imbalanced datasets. Some researchers recommend reporting both
raw agreement
and
prevalence
-adjusted bias-adjusted kappa (
PABAK
), though this metric loses the chance-correction interpretation. Others recommend reporting agreement separately for each class (macro-averaged kappa per category) to identify which specific categories are problematic.
Out
[
20
]:
Visualization
Illustration of the prevalence paradox: as positive-class prevalence increases from 0.5 to 0.95, Cohen''s kappa (red, left axis) declines sharply even when raw observed agreement is held constant at 90 percent. The blue dashed line (right axis) shows how chance agreement ($P_e$) rises simultaneously, squeezing the denominator of the kappa formula. When $P_e$ approaches $P_o$, kappa approaches zero or becomes negative despite high raw accuracy.
The Bias Problem
Link Copied
Cohen's kappa
assumes fixed marginals for each rater. When raters have different base rates (one is more lenient than another), kappa paradoxically decreases compared to
Scott's pi
, which pools marginals. Byrt, Bishop, and Carlin (1993) formalized this as the "bias" component of kappa's limitations: if rater A uses "positive" 80% of the time but rater B uses it 40% of the time, the pooled marginal approach assumes an intermediate rate, while
Cohen's kappa
computes
chance agreement
using these divergent marginals separately, creating a lower expected agreement.
Fleiss' kappa
and
Krippendorff's alpha
use pooled marginals, effectively treating rater differences as noise to be averaged out. This makes them more stable but less sensitive to systematic rater biases. The choice between coefficients depends on whether you view rater differences as meaningful signal (
annotator
A is systematically more strict) or
measurement error
(raters should be interchangeable). In practice, when two specific experts consistently differ in their labeling tendencies,
Cohen's kappa
better captures the challenge of reconciling their perspectives.
Limits of Categorical Agreement
Link Copied
Standard kappa statistics assume categorical data. Modern NLP increasingly uses continuous ratings (quality scores from 1-5) or rankings (preference pairs). While
Krippendorff's alpha
handles ordinal and interval scales through
distance weighting
, the interpretation becomes complex. A disagreement between ratings of 1 and 2 on a 5-point scale might mean something different than 4 vs 5, even if the numerical difference is identical: the bottom of the scale might be harder to distinguish perceptually than the middle.
For
preference evaluation
, which we will cover in the next chapter, we often use ranking agreement metrics like Kendall's
τ
\tau
or the
Bradley-Terry model
discussed in
Part XXXVII: Alignment and RLHF
. These capture the relative nature of preferences better than categorical agreement. A rater who consistently ranks response A above response B agrees with another rater who does the same, even if they would assign different absolute quality scores to each response.
Agreement vs. Validity
Link Copied
High
inter-annotator agreement
does not guarantee validity. Annotators might agree consistently while being consistently wrong relative to some objective standard, or they might agree on superficial features while missing the deeper linguistic phenomenon we care about. Agreement validates the reproducibility of the measurement, not the correctness of the construct.
This distinction matters when using human judgments as training data for LLMs. In
Part XXXVI: Instruction Tuning
, we saw that instruction-following datasets rely on human judgments of response quality. High IAA ensures consistency in those judgments, but if the annotators share systematic biases (cultural, temporal, or ideological), the resulting model inherits those biases. A group of annotators who all come from the same demographic background might agree strongly with each other while being unrepresentative of the broader population the model serves. We will explore bias measurement and mitigation in
Part LVIII: Bias and Fairness
.
The appropriate framework is to view IAA as necessary but not sufficient for dataset quality. You need agreement to ensure the labels are consistent, and you need validity studies (correlation with external criteria, expert review, or task performance) to ensure the labels measure what you intend.
Practical Thresholds
Link Copied
Despite the Landis and Koch benchmarks, context determines what constitutes "good" agreement. For objective tasks like part-of-speech tagging on news text,
κ
>
0.8
\kappa > 0.8
is achievable and expected. For subjective tasks like sentiment analysis of tweets or assessing whether an LLM response "shows empathy,"
κ
=
0.6
\kappa = 0.6
might represent excellent agreement given the inherent ambiguity.
Some practitioners use
κ
=
0.67
\kappa = 0.67
as a minimum threshold for reliable data, while
κ
>
0.8
\kappa > 0.8
indicates data suitable for algorithmic training without additional review. Values below 0.4 suggest the annotation scheme needs substantial revision before proceeding to large-scale labeling. These are starting points, not rules: always justify your threshold relative to your task requirements and your downstream use case.
When reporting IAA in a paper or technical report, always include the
raw agreement
P
o
P_o
alongside the chance-corrected coefficient, note the number of raters and items, report how
missing data
was handled if applicable, and indicate which specific variant of each metric you computed (standard vs
weighted kappa
, nominal vs ordinal alpha). This transparency allows readers to assess the quality of the annotation even if they would have chosen different thresholds.
Summary
Link Copied
Inter-annotator agreement
turns the vague notion of "
label
quality" into quantifiable, comparable statistics that can be tracked across annotation rounds, compared across datasets, and used to make principled decisions about when data is ready for use. We have examined three complementary approaches, each suited to different annotation scenarios:
Cohen's kappa
measures agreement between two specific raters with potentially different biases, which makes it ideal for validating a primary
annotator
against an expert reviewer or for measuring consistency between two automated systems. It preserves rater-specific marginal distributions and is the standard choice when rater identity matters.
Fleiss' kappa
generalizes to any number of raters treated as interchangeable samples from a population, suitable for
crowdsourcing
scenarios where you care about the pool as a whole rather than individual workers. It uses pooled marginals and equals
Scott's pi
in the two-rater case.
Krippendorff's alpha
provides the most general framework, handling
missing data
, varying numbers of raters per item, and different measurement scales through configurable distance metrics. It is the preferred choice for complex annotation schemes with incomplete data or ordinal ratings.
All three coefficients share the
chance-correction framework
, comparing observed agreement against expected random agreement. This correction prevents inflated scores on imbalanced datasets but introduces sensitivity to
prevalence
and marginal distributions. The
prevalence paradox
and the bias problem are the most common pitfalls in practice, and both can lead to misleading conclusions if you report kappa values without understanding what drives them.
When agreement is low, we have options beyond simple
majority voting
.
Soft labels
preserve the uncertainty inherent in borderline cases. Iterative guideline refinement addresses systematic disagreement by clarifying ambiguous decision boundaries. Disagreement-weighted training reduces the influence of unreliable labels. The appropriate strategy depends on whether disagreement represents noise to be eliminated or signal to be preserved.
As we move toward evaluation methodologies that use LLMs as judges, the principles of chance-corrected agreement remain central. Validating an automated judge requires measuring its agreement with human judgments using the same statistical rigor we apply to human annotators. The next chapter on
Preference Evaluation
will explore how these agreement metrics apply specifically to the pairwise and ranking judgments that drive modern alignment techniques like
RLHF
and
DPO
, and how to design
preference annotation
pipelines that achieve both high IAA and valid coverage of the preference space.
Quiz
Link Copied
Ready to test your understanding? Take this quick quiz to
reinforce
what you've learned about
inter-annotator agreement
and chance-corrected
reliability
coefficients.
Comments
No comments yet. Be the first to share your thoughts!
Reference
Citation details
Cite or share this article.
BIBTEX
Academic
Copy
@misc{brenndoerfer2026cohenfleiss,
  author = {Michael Brenndoerfer},
  title = {Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation},
  year = {2026},
  url = {https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability},
  organization = {mbrenndoerfer.com},
  note = {Accessed: 2026-09-13}
}
Show other formats
APA · MLA · Chicago · Harvard · Simple
APA
Academic
Copy
Michael Brenndoerfer (2026). Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation. Retrieved from https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability
MLA
Academic
Copy
Michael Brenndoerfer. "Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation." 2026. Web. September 13, 2026. <https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability>.
CHICAGO
Academic
Copy
Michael Brenndoerfer. "Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation." Accessed September 13, 2026. https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability.
HARVARD
Academic
Copy
Michael Brenndoerfer (2026) 'Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation'. Available at: https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability (Accessed: September 13, 2026).
Simple
Basic
Copy
Michael Brenndoerfer (2026). Cohen, Fleiss & Krippendorff: IAA Metrics & Implementation. https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability
DIRECT LINK
URL
Copy
https://mbrenndoerfer.com/writing/inter-annotator-agreement-kappa-alpha-reliability
About the author
Continue with the full handbook
This chapter is part of Language AI Handbook. Use the handbook page to browse the complete table of contents and continue reading in sequence.
Explore Language AI Handbook
Related content
Newsletter
Stay up to date
Get articles, book updates, and news delivered to your inbox.
Subscribe
No spam, unsubscribe anytime.
or
Join the community
Sign in to remove popups, track your reading progress, and join the discussion.
Join the community
Join the community
Continue reading
Back to
Language AI Handbook
Previous Chapter
Human Evaluation Design
Next Chapter
Preference Evaluation
Author
Michael Brenndoerfer
Editorial note
All opinions expressed here are my own and do not reflect the views of my employer.
Michael currently works as an Associate Director at EQT Partners in Singapore, leading AI and data initiatives across private capital investments.
With a background spanning private equity, management consulting, and software engineering, he focuses on building practical analytics solutions and helping teams work more effectively with data. He has contributed research to AI conferences and enjoys exploring applications of machine learning and natural language processing.
Explore
About
Publications
Books
Connect
Contact
Newsletter
Related content
Evaluation Prompt Engineering: Designing Reliable LLM Judges
Mar 12, 2026
•
59
min read
Data, Analytics & AI
Software Engineering
Design reliable LLM judge prompts using explicit criteria, few-shot examples, and chain-of-thought formatting to maximize evaluation accuracy.
Read more
Position Bias in LLM Judges: Measurement and Mitigation
Mar 11, 2026
•
46
min read
Data, Analytics & AI
Software Engineering
Explains how position bias, verbosity bias, and sycophancy distort LLM evaluation. Measure swap consistency, detect length effects.
Read more
LLM-as-Judge: Scalable AI Evaluation with Language Models
Mar 10, 2026
•
55
min read
Data, Analytics & AI
Software Engineering
Build LLM-as-Judge evaluation pipelines: prompt design, judge model selection, calibration against human annotations, and bias mitigation.
Read more
LLM Preference Evaluation: Pairwise Comparisons and Elo
Mar 9, 2026
•
59
min read
Machine Learning
Language AI Handbook
Evaluate language models with pairwise comparisons and Elo ratings, including preference aggregation, confidence intervals, bias, and significance tests.
Read more
All writing