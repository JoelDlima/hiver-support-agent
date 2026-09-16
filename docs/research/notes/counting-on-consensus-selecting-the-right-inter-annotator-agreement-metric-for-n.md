---
title: 'Counting on Consensus: Selecting the Right Inter-annotator Agreement Metric
  for NLP Annotation and Evaluation'
id: counting-on-consensus-selecting-the-right-inter-annotator-agreement-metric-for-n
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:17.769251Z'
source: https://arxiv.org/html/2603.06865
source_domain: arxiv.org
fetched_at: '2026-09-15T02:28:17.764547Z'
fetch_provider: builtin
status: draft
type: note
tier: institutional
content_type: paper
deprecated: false
---

Counting on Consensus: Selecting the Right Inter-annotator Agreement Metric for NLP Annotation and Evaluation
Title:
Content selection saved. Describe the issue below:
Description:
arXiv is now an independent nonprofit!
Learn more
×
License: CC BY 4.0
arXiv:2603.06865v2 [cs.CL] 01 Apr 2026
Counting on Consensus: Selecting the Right Inter-annotator Agreement Metric for NLP Annotation and Evaluation
Abstract
Human annotation remains the foundation of reliable and interpretable data in Natural Language Processing (NLP). As annotation and evaluation tasks continue to expand, from categorical labelling to segmentation, subjective judgment, and continuous rating, measuring agreement between annotators has become increasingly more complex. This paper outlines how inter-annotator agreement (IAA) has been conceptualised and applied across NLP and related disciplines, describing the assumptions and limitations of common approaches. We organise agreement measures by task type and discuss how factors such as label imbalance and missing data influence reliability estimates. In addition, we highlight best practices for clear and transparent reporting, including the use of confidence intervals and the analysis of disagreement patterns. The paper aims to serve as a guide for selecting and interpreting agreement measures, promoting more consistent and reproducible human annotation and evaluation in NLP.
Keywords:
inter-annotator agreement, annotation reliability, reproducibility, human evaluation
Joseph James
Department of Computer Science, The University of Sheffield
Sheffield, United Kingdom
jhfjames1@sheffield.ac.uk
Abstract content
1.  Introduction
Creating high-quality annotated data and ensuring reliable human evaluation are central to NLP, and the consistency of human judgments determines the validity of datasets and evaluations. IAA measures this consistency by quantifying the extent to which multiple annotators or evaluators apply the same labels to the same items. High IAA suggests clear guidelines and a reproducible results from texts or model outputs to human judgments, whereas low IAA can indicate under-specified instructions, insufficient training, or subjectivity in the task being evaluated
Hallgren (2012)
. However, relying on raw agreement alone can overestimate reliability, motivating the use of chance-corrected and task-appropriate statistics
Hayes and Krippendorff (2007)
;
Kohen (1960)
. The diversity of NLP tasks, from simple categorical labelling to span-based extraction, segmentation, and pairwise preferences, makes selecting the right agreement metric challenging. Recent work has highlighted how metric choice and distance functions affect interpretability and robustness for complex annotation tasks
Braylan et al. (2022)
, and evaluation studies document substantial variability in human criteria and correlations with automatic metrics
Chhun et al. (2022)
. This highlights the need to match the agreement coefficient to the annotation design and to clarify what construct the metric is intended to capture
Chhun et al. (2022)
.
Another concern is the reporting practices. Point estimates without uncertainty overstate precision and reduce comparability. Methodological guidance recommends reporting confidence intervals, describing the rater design, and accounting for missing data and label prevalence, all of which affect interpretation of the results
Hallgren (2012)
;
Hayes and Krippendorff (2007)
. These considerations extend to human evaluation of model outputs, where pairwise preference studies reveal inconsistency under common setups and call for better design and meta-evaluation
Ghosh et al. (2024)
. Similar work shows that evaluator biases and inconsistencies can influence conclusions about system quality, meaning careful design is required to obtain reliable human judgments
Bavaresco et al. (2025)
;
Liu et al. (2024)
;
Balloccu et al. (2024)
;
Tam et al. (2024)
. Finally, disagreement is not merely “noise”, modelling annotator or evaluator identities and perspectives can improve downstream learning and preserve legitimate variation in judgments, rather than collapsing it during aggregation
Deng et al. (2023)
.
This paper offers an overview of how IAA can be measured in NLP. It reviews commonly used approaches across different settings, describing how their underlying assumptions affect interpretation and comparability. In addition, it outlines methodological considerations for reporting, including how to account for data imbalance, missing annotations, and uncertainty in agreement estimates. The aim is to help researchers select measures that align with their task and interpret them appropriately in context. By treating agreement not as an afterthought but as a key component, this work seeks to support more transparent and reproducible practices in NLP.
2.  Categorical data
For tasks where each item is assigned a category, agreement can be measured in two main ways: by directly calculating the proportion of matching labels between annotators, or by using chance-corrected coefficients that adjust for agreement expected by random chance.
2.1.  Percentage Agreement
Percentage agreement (
P
o
P_{o}
) is the simplest and most direct measure of inter-annotator reliability. It represents the proportion of items for which annotators assign the same label and is defined as the number of agreed items divided by the total number of items. However, because it does not account for agreement that could occur by chance,
P
o
P_{o}
can overestimate reliability, especially when the categories are imbalanced. Despite this, it remains a useful baseline metric, particularly in exploratory or crowdsourced annotation studies. This measure provides an intuitive view of overall consistency and is often reported alongside chance-corrected statistics
Mohammad et al. (2018)
.
2.2.  Bennett, Alpert, and Goldstein’s S
Bennett, Alpert, and Goldstein’s
S
S
coefficient provides a simple chance-corrected alternative to raw percentage agreement
BENNETT et al. (1954)
. It assumes that all categories are equally likely and is defined as
S
=
1
−
k
⁡
(
1
−
P
o
)
k
−
1
,
S=1-\frac{k(1-P_{o})}{k-1},
where
k
k
is the number of possible categories. The
S
S
statistic adjusts for the probability of random agreement under the assumption of uniform category prevalence. However, it does not account for differences in annotator bias or imbalanced label distributions, which limits its suitability. Although rarely used in research, it is historically significant as one of the earliest attempts to correct for chance agreement metrics.
2.3.  Cohen’s Kappa
Cohen’s
κ
\kappa
Cohen (1960)
is one of the earliest and most commonly used IAA measures for categorisation tasks. It applies when two annotators label the same set of items.
κ
\kappa
compares the observed agreement
P
o
P_{o}
between the two annotators to the agreement expected by chance
P
e
P_{e}
, and is defined as
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
,
\kappa=\frac{P_{o}-P_{e}}{1-P_{e}},
where
P
o
P_{o}
is the proportion of items the annotators agreed on, and
P
e
P_{e}
is the proportion expected to agree by random chance (based on each annotator’s labelling distribution). By subtracting
P
e
P_{e}
,
κ
\kappa
corrects for random guessing. For example, if both annotators heavily favour one category, they might agree often simply by coincidence;
κ
\kappa
will reduce the score to account for this.
κ
\kappa
ranges from 1 (perfect agreement) down to 0 (no better than chance) or even negative (systematic disagreement). Cohen’s paper introduced
κ
\kappa
precisely to handle such situations where raw agreement is misleading.
2.4.  Fleiss’ Kappa
Fleiss’
κ
\kappa
Fleiss (1971)
generalises Cohen’s
κ
\kappa
to multiple annotators. It handles any number of annotators assigning nominal categories to a common set of items. Conceptually, Fleiss’
κ
\kappa
also compares observed agreement to chance agreement, but it aggregates agreement across all annotators rather than comparing them pairwise. For each item
i
i
, the observed agreement among
N
N
annotators is computed as
P
i
=
1
N
⁡
(
N
−
1
)
​
∑
j
=
1
k
n
i
​
j
​
(
n
i
​
j
−
1
)
,
P_{i}=\frac{1}{N(N-1)}\sum_{j=1}^{k}n_{ij}(n_{ij}-1),
where
n
i
​
j
n_{ij}
is the number of annotators who assigned item
i
i
to category
j
j
. The mean observed agreement across all
N
N
items is then
P
¯
=
1
N
​
∑
i
=
1
N
P
i
.
\bar{P}=\frac{1}{N}\sum_{i=1}^{N}P_{i}.
The expected agreement
P
e
P_{e}
is derived from the overall category proportions, and the final
κ
\kappa
is computed in the same way as Cohen’s equation. Fleiss’
κ
\kappa
assumes that each item receives the same number of annotations and can be sensitive to class imbalance or uneven marginal distributions. It is equivalent to Scott’s
π
\pi
Scott (1955)
under the condition that each item has the same number of annotations.
2.5.  Weighted Kappa
Weighted kappa
Cohen (1968)
extends Cohen’s
κ
\kappa
to ordinal scales by assigning partial credit to near agreements. Instead of treating all disagreements equally, it applies a weighting function that penalises larger differences more heavily. The two most common weighting schemes are
linear
, where weights decrease proportionally with distance, and
quadratic
, where distant disagreements are penalised more strongly. Weighted
κ
\kappa
is particularly useful for rating tasks on Likert or ordinal scales, as it captures both the direction and magnitude of disagreement between annotators.
2.6.  Krippendorff’s Alpha
Krippendorff’s
α
\alpha
Krippendorff (2013)
is a versatile agreement metric that works for various data types (nominal, ordinal, interval, etc.), any number of annotators, and can handle missing data.
α
\alpha
is popular in content analysis and increasingly in NLP because of this flexibility. It calculates agreement by focusing on disagreements:
α
=
1
−
D
o
D
e
,
\alpha=1-\frac{D_{o}}{D_{e}},
where
D
o
D_{o}
is the observed disagreement and
D
e
D_{e}
is the expected disagreement under chance. For nominal data, disagreement is usually defined as 0 if two labels are the same and 1 if different; for ordinal or interval data, a different distance function (e.g., squared difference) can be used. A major advantage of
α
\alpha
is handling missing data. Notably, for nominal two-annotator cases with no missing values,
α
\alpha
is mathematically equivalent to Cohen’s
κ
\kappa
; for multiple annotators it relates closely to Fleiss’
κ
\kappa
. Researchers have used Krippendorff’s
α
\alpha
in NLP annotation of discourse or subjective content, where not all annotators label everything or where an ordinal scale needs to be handled appropriately.
2.7.  Gwet’s AC1/AC2
Gwet’s AC1/AC2
Gwet (2001)
are more recent chance-corrected agreement measures proposed to address some limitations of
κ
\kappa
in situations of high agreement or highly skewed class distributions (often called the “
κ
\kappa
paradox” where
κ
\kappa
can be low despite high observed agreement, or vice versa). Gwet’s AC1 (for nominal) and AC2 (for ordinal, with weights) use an alternative formula for expected agreement that tends to be more stable when classes are imbalanced or when annotators have bias. Recent NLP studies with extreme class imbalance have reported AC1 alongside
κ
\kappa
to provide a more nuanced view of agreement
Chhun et al. (2024)
.
3.  Structured annotations
Not all annotation tasks involve assigning a single label to an item. In many NLP tasks, annotators mark segments of text, which introduces alignment issues. Examples include named entity recognition (NER), where annotators highlight spans corresponding to entities, or text segmentation, where annotators divide a document into segments (e.g., topic boundaries or dialogue turns).
3.1.  Span-Based Annotations
For span labelling tasks, a common approach is to treat one annotator’s annotations as a
predicted
set of spans and another’s as the
gold
set, then compute precision, recall, and F
1
score between them. This pairwise F
1
(or the Dice coefficient) measures overlap agreement, it rewards the annotators for each entity span they both identified exactly and penalises cases where one annotator found an entity that the other missed or where their span boundaries differ. In practice, F
1
is calculated on a per-span basis (exact matches).
3.2.  Text Segmentation
When the task is to segment a text into contiguous units (e.g., dividing an article into sections), annotators are placing boundaries in text. Two popular metrics for segmentation agreement are:
•
P
k
P_{k}
Beeferman et al. (1999)
: Slides a fixed-size window through the text and checks if the segmentations agree on whether there is a boundary between two points.
•
WindowDiff
Pevzner and Hearst (2002b)
: Similar to
P
k
P_{k}
, but it penalizes near-misses less harshly.
Producing a score between 0 and 1, where 0 indicates perfect agreement. If annotators’ segment boundaries are slightly shifted, WindowDiff is more forgiving than
P
k
P_{k}
.
These metrics have been widely used in discourse and dialogue segmentation studies. For example,
Scaiano and Inkpen (2012)
applied them to evaluate segment boundaries in multi-party conversation, highlighting how boundary-based agreement can reveal both annotator consistency and the inherent ambiguity of conversational structure. Building on these approaches,
Fournier and Inkpen (2012)
introduced Segmentation Similarity, a generalised framework that unifies and extends
P
k
P_{k}
and WindowDiff by accounting for partial matches and variable boundary tolerance.
3.3.  Unitising Tasks
In some tasks, annotators not only mark segments of text but also decide the number and positions of those segments, so-called unitising annotations. For example, in discourse analysis, annotators might break a conversation into discourse units and label each unit with a discourse function.
One metric is the holistic gamma (
γ
\gamma
) measure
Mathet et al. (2015)
, which is designed for complex unitising tasks. Gamma treats the problem as a combination of segmentation and categorisation by finding an optimal alignment between units marked by different annotators and computing chance-corrected agreement. It accounts for both positional discrepancies (differences in unit boundaries) and categorical discrepancies (differences in labels).
3.4.  Boundary Edit Distance
Boundary Edit Distance
Fournier (2013)
is a generalised measure of segmentation agreement that quantifies the minimal number of edits required to transform one annotator’s segmentation into another’s. It accounts for insertions, deletions, and near misses of boundaries, producing a flexible score that can handle varying degrees of segmentation granularity. Compared with WindowDiff or
γ
\gamma
, Boundary Edit Distance is often considered a more robust alternative for tasks such as discourse or dialogue segmentation, where partial overlaps and fuzzy boundaries are common.
4.  Continuous data
Certain tasks require continuous or interval-scale outputs rather than discrete categories. Examples include grading the fluency or coherence of text, or scoring emotional intensity on a numeric scale
Abercrombie et al. (2023)
;
Wong and Paritosh (2022)
. In such cases, the goal is to assess how consistently annotators assign scores along a continuous scale, rather than whether they select the same label. Measures of association or reliability for continuous data estimate how much of the variance in ratings reflects systematic differences between items rather than random noise or rater bias.
4.1.  Intraclass Correlation Coefficient
The Intraclass Correlation Coefficient (ICC) is the most widely used reliability measure for continuous tasks. It quantifies the proportion of total variance in ratings that is attributable to true differences between items, relative to variance introduced by differences among raters or random error. Although well established in psychology and medicine, ICC is less frequently reported in NLP, where continuous annotation is often treated as ordinal or categorical.
Several ICC variants exist, distinguished by their model assumptions and by whether they estimate the consistency of individual ratings or the generalisability of aggregated ratings across multiple annotators. Following the framework introduced by
Shrout and Fleiss (1979)
and expanded by
McGraw and Wong (1996a)
, the most common variants are:
•
ICC(1,1)
: One-way random effect, single measurement. Used when each item is rated by a different random set of raters.
•
ICC(1,k)
: One-way random effect, average measurement. It reflects the reliability of the mean rating when each item is rated by
k
k
raters.
•
ICC(2,1)
: Two-way random effect, single measurement (absolute agreement). Here, both items and raters are considered random samples from larger populations.
•
ICC(2,k)
: Two-way random effect, average measurement. It measures the reliability of the average rating from
k
k
raters.
•
ICC(3,1)
: Two-way mixed effect, single measurement (consistency). The raters are fixed (i.e., the particular raters are the only ones of interest) and the focus is on consistency rather than absolute agreement.
•
ICC(3,k)
: Two-way mixed effect, average measurement. It reflects the reliability of the average of
k
k
fixed raters.
In the two-way models, the difference between ICC(2,*) and ICC(3,*) lies in the treatment of the raters: in ICC(2,*) the raters are assumed to be randomly selected from a larger population, while in ICC(3,*) the raters are considered the only raters of interest (i.e., fixed). The choice between a single measurement (e.g., ICC(2,1)) and an average measurement (e.g., ICC(2,k)) depends on whether the study is concerned with the reliability of an individual rater’s score or the aggregated score across raters. Selecting the appropriate ICC variant is essential for accurately assessing the reliability of annotations.
4.2.  Cronbach’s Alpha
Cronbach’s
α
\alpha
Cronbach (1951)
is a measure of internal consistency that quantifies how closely related a set of ratings or items are as a group. It is mathematically equivalent to certain forms of the Intraclass Correlation Coefficient (ICC), specifically when the same raters assess each item under a one-way random-effects model. In annotation contexts, a high
α
\alpha
suggests that annotators are applying the scale consistently across items. However, like ICC, its interpretation depends on model assumptions about rater and item effects, and it does not distinguish between consistency and absolute agreement.
4.3.  Concordance Correlation Coefficient
The Concordance Correlation Coefficient (CCC)
Lawrence and Lin (1989)
assesses how well two sets of continuous ratings agree in both precision and accuracy. Unlike standard correlation coefficients, which measure only the strength of association, CCC also captures deviation from the identity line, that is, how close annotators’ scores are to perfect concordance. It combines Pearson’s correlation with a term penalising mean and scale differences between annotators. CCC has been widely used in affective computing and emotion intensity annotation, where it provides a more stringent criterion for agreement than correlation alone.
4.4.  Correlation-Based Measures
Correlation coefficients assess the degree to which annotators produce similar rating patterns across items. They are useful for measuring consistency rather than absolute agreement.
For ordinal or ranked judgments, non-parametric correlation coefficients such as Spearman’s
ρ
\rho
Spearman (1904)
and Kendall’s
τ
\tau
Kendall (1938)
evaluate whether annotators preserve the same ordering of items, without assuming equal intervals between ranks. These measures are commonly used in human–model correlation studies, system ranking tasks, and as proxies for IAA when judgments are relative rather than absolute.
For continuous scores, Pearson’s correlation coefficient (
r
r
)
Pearson (1895)
measures the strength and direction of the linear relationship between annotators’ ratings. However, correlation alone does not indicate absolute agreement: two annotators may be perfectly correlated yet systematically offset in their scores. Therefore, correlation-based metrics should be interpreted as indicators of association rather than reliability in the strict sense.
5.  Metric Selection and Interpretation
Selecting an appropriate IAA metric depends on the data type, number of annotators, and whether chance correction or missing data handling is essential. Table
1
summarises commonly used metrics, outlining their key properties and limitations to support informed metric selection and interpretation.
Metric
Data Type
Missing Data?
Number of Annotators?
Chance-Corrected?
Sensitive to Imbalance?
Limitations
Percentage Agreement
Nominal
–
Pairwise
–
High
Overestimates reliability.
Bennett’s S
Nominal
–
Two or more
✓
–
Assumes uniform label distribution.
Cohen’s
κ
\kappa
Nominal
–
Two only
✓
High
Unstable when class frequencies or rater biases differ.
Fleiss’
κ
\kappa
Nominal
–
Three or more
✓
High
Requires equal numbers of ratings per item.
Krippendorff’s
α
\alpha
Nominal / Ordinal / Interval / Ratio
✓
Two or more
✓
Moderate
Complex computation; interpretation can vary by distance metric.
Gwet’s AC1/AC2
Nominal / Ordinal
✓
Two or more
✓
Low
Less common in literature; parameter selection affects results.
Weighted
κ
\kappa
Ordinal
–
Two only
✓
High
Requires careful choice of weighting scheme.
ICC
Continuous / Interval
✓
Two or more
✓
Moderate
Sensitive to model choice and assumes normality.
Cronbach’s
α
\alpha
Continuous / Interval
✓
Two or more
✓
–
Assumes unidimensionality; may overestimate reliability.
CCC
Continuous
–
Two only
✓
Low
Sensitive to outliers; conflates accuracy and precision.
F
1
/ Dice
Span-based / Structured
–
Pairwise
–
Task-dependent
Sensitive to boundary mismatches.
P
k
/ WindowDiff
Segmentation
–
Pairwise
–
–
Results dependent on window size.
Gamma (
γ
\gamma
)
Unitising / Structured
✓
Two or more
✓
Moderate
Computationally intensive; conceptually complex.
Boundary Edit Distance
Segmentation
–
Pairwise
–
Task-dependent
Robust to near-misses; interpretation depends on tolerance.
Table 1:
Overview of IAA metrics with key properties and limitations.
5.1.  Interpretation of Agreement Scores
The qualitative interpretation of IAA scores varies across research domains and metric families. For
κ
\kappa
-type coefficients such as Cohen’s, Fleiss’, and Krippendorff’s
α
\alpha
, conventions often follow the scale introduced by
Landis and Koch (1977)
and later refined by
Viera et al. (2005)
and
McHugh (2012)
. These frameworks associate numerical ranges with descriptive categories such as “poor,” “fair,” “moderate,” “substantial,” and “almost perfect,” though their thresholds are not universally accepted.
For reliability coefficients such as the ICC and Cronbach’s
α
\alpha
, psychometric and medical research typically applies more conservative standards, often considering values above 0.75 to indicate strong reliability
Koo and Li (2016)
. Correlation-based measures, including Pearson’s
r
r
, Spearman’s
ρ
\rho
, and Kendall’s
τ
\tau
, follow broadly similar conventions, distinguishing weak, moderate, and strong associations without fixed numeric boundaries.
Structured and segmentation-based metrics such as F
1
, Boundary Similarity, Edit Distance, WindowDiff, P
k
, and
γ
\gamma
lack standard interpretive scales. Their scores depend heavily on task setup, annotation granularity, and tolerance for partial matches, making relative rather than absolute comparisons more informative.
Recent work has raised broader concerns about how IAA scores are interpreted and reported.
Wong et al. (2021)
argue that fixed interpretive thresholds are overly rigid for complex or subjective tasks and propose replication-based benchmarks in place of universal cutoffs.
Klie et al. (2024)
similarly show that many dataset papers report kappa-type coefficients without accounting for class imbalance, sample size, or annotator expertise, and call for greater transparency in reporting. Other studies highlight structural limitations:
Stefanovitch and Piskorski (2023)
find that traditional metrics often fail in multilingual or cross-domain settings, while
Li et al. (2024a)
demonstrate that categorical interpretive conventions do not directly transfer to structured or sequence-labelling tasks, where agreement is inherently lower due to hierarchical or contextual complexity.
Building on these critiques,
Richie et al. (2022)
emphasise that IAA should not be treated as a hard performance ceiling for machine learning systems, recommending instead the weighting or calibration of annotators rather than assuming uniform reliability.
Wong and Paritosh (2022)
introduce the
k
k
-rater reliability framework to quantify agreement across aggregated annotations, capturing stability that single-rater metrics often underestimate. Expanding this perspective,
Klie et al. (2024)
provide a meta-analysis of 591 NLP datasets, revealing inconsistent quality control and advocating for standardised, transparent reporting of annotation design and error estimation.
Each agreement metric is based on different underlying assumptions about how to measure consistency between annotators. Some account for chance agreement, while others measure overlap or correlation directly. Because of these differences, agreement scores are not always comparable across metrics and must be interpreted in relation to the task and data. Results can also be affected by factors such as class imbalance, the number of annotators, and annotation granularity. Agreement should therefore be understood as a context-dependent indicator of reliability rather than an absolute measure of annotation quality.
5.2.  Reliability vs. Validity
Reporting confidence intervals alongside IAA metrics is essential, as they indicate the range within which the true value of a metric is likely to lie and quantify uncertainty in its estimation. Narrow intervals suggest high precision, while wider intervals reflect greater variability or instability
McHugh (2012)
. Confidence intervals also enable more meaningful comparisons of agreement across tasks or groups by showing whether apparent differences are statistically significant or could arise from sampling variability
Reichenheim (2004)
.
Although both p-values and confidence intervals support statistical inference, they serve different roles. A p-value assesses whether the observed agreement differs significantly from chance but provides no information about precision or effect magnitude. In contrast, a confidence interval conveys the range of plausible values for the agreement estimate, directly expressing its uncertainty. In IAA reporting, p-values can indicate significance, but confidence intervals offer a clearer sense of how stable and reliable the estimate is.
Inter-annotator agreement demonstrates reliability, the consistency with which annotators apply a scheme, but it does not establish validity. As
Artstein and Poesio (2008)
note, high IAA only confirms that annotators are consistent, not that they are measuring the intended construct correctly. High agreement can arise even from oversimplified or biased guidelines, while low agreement may reflect genuine ambiguity or interpretive diversity rather than poor data quality
(
Plank, 2022
)
.
Researchers should therefore report reliability measures alongside evidence of validity, such as examples of ambiguous cases or comparisons to external references. Treating reliability and validity as complementary dimensions moves the field beyond numeric agreement scores and toward more interpretable and grounded evaluation practices
(
Howcroft et al., 2020
)
. Achieving both requires clear task definitions, empirical grounding, and iterative refinement through pilot studies, adjudication, and expert feedback to distinguish methodological uncertainty from genuine subjectivity.
5.3.  The Role of Disagreement
Disagreement among annotators is a common feature of both annotation and evaluation in NLP. Rather than treating all divergence as noise, it can reveal task ambiguity, underspecified guidelines, or variation in rater preferences. Prior work identifies multiple sources of disagreement, including genuine linguistic ambiguity, inconsistent criteria, and contextual or interface effects that influence decision-making
Reidsma and Carletta (2008)
;
Fleisig et al. (2023)
;
Xu et al. (2024)
. These findings caution against interpreting low agreement as evidence of poor data quality.
Recent research increasingly views disagreement as informative rather than erroneous. Retaining label distributions or “soft labels” allows ambiguity to be represented explicitly, while measures of label dispersion indicate where annotators diverge
Rodríguez-Barroso et al. (2024)
;
Fleisig et al. (2023)
. Rater-aware models extend this approach by learning annotator representations, disentangling systematic bias from item difficulty, and improving both aggregation and downstream robustness
Fleisig et al. (2023)
. Together, these methods treat disagreement as a meaningful signal about data, tasks, and annotator populations.
Practically, researchers are encouraged to report both agreement coefficients and measures of label dispersion, to analyse systematic disagreement across classes or subgroups, and to document annotation design factors such as training, and interface settings
Xu et al. (2024)
;
Sandri et al. (2023)
. In subjective or interpretive tasks, preserving disagreement may be preferable to enforcing a single
ground truth
, as it better reflects population diversity and produces models that are more robust and representative
Rodríguez-Barroso et al. (2024)
;
Sandri et al. (2023)
;
Wan et al. (2023)
.
5.4.  Effects of Pay and Time Pressure
Payment and time constraints influence both the quality of annotations and the behaviour of annotators. Early work showed that non-expert annotations can be valuable after aggregation, but quality varies with incentives and task design
Snow et al. (2008)
. Flat-rate payment schemes are common yet often inequitable, as completion times vary widely, leading to very low effective wages for slower or more careful annotators and incentivising speed over accuracy
Salminen et al. (2023)
. Performance-based or bonus systems can improve outcomes by promoting accuracy-oriented behaviour, though their effectiveness depends on task difficulty and the clarity of evaluation criteria
Rogstadius et al. (2011)
. Ethical analyses note that focusing solely on pay neglects broader issues of autonomy and bias, emphasising the need for transparency and worker agency
Shmueli et al. (2021)
. From a motivation perspective, excessive reliance on extrinsic rewards can displace intrinsic motives such as curiosity, though clear feedback and transparent incentive structures can help counteract this effect.
Time constraints have comparable consequences. Tight deadlines promote heuristic or superficial judgments and reduce exploration under uncertainty, potentially inflating agreement for the wrong reasons
Wu et al. (2022)
. Conversely, strict viewing-time limits reduce both performance and satisfaction, while extended sessions without breaks cause fatigue and increase variance in responses
Lim et al. (2024)
;
Schlicher et al. (2021)
. Annotation difficulty also affects completion time, making uniform per-item pay problematic when item complexity varies
Wei et al. (2018)
. In practice, payment and timing protocols should prioritise accuracy over throughput: establish fair hourly rates based on observed completion times, define transparent evaluation criteria, avoid excessive time caps, and adjust compensation for more complex items. These design principles, reported alongside agreement statistics, support both reproducibility and ethical evaluation
Shmueli et al. (2021)
.
5.5.  Human–Model Comparison
Large Language Models (LLMs) are now used not only as systems to be evaluated but also as evaluators, producing judgments of fluency, coherence, or factuality that were once the exclusive domain of human annotators. This shift challenges the long-held assumption that human agreement represents the upper bound of evaluation quality. Recent studies demonstrate that model-based evaluation can equal or even exceed human reliability on several text quality dimensions
(
Gilardi et al., 2023
)
. As a result, human annotations can no longer serve as an unquestioned gold standard when models are expected to complement or surpass human performance.
Surveys have shown that the emergence of LLM-based evaluation has reshaped the methodological landscape of NLP
(
Li et al., 2024b
;
Gu et al., 2024
;
Chang et al., 2024
;
Laskar et al., 2024
)
. These reviews highlight that while models often display higher internal consistency than human raters, they also risk reproducing systematic biases or calibration errors. Conversely, human disagreement can reflect genuine ambiguity or contextual sensitivity that models fail to capture. Rather than replacing human judgment, model-based evaluators should be benchmarked against diverse human perspectives and assessed for alignment with multiple criteria rather than correlation with a single reference set. Finally,
Bojić et al. (2025)
compare human annotators and several LLMs across sentiment, political leaning, emotional intensity, and sarcasm detection, finding that models often match human reliability on structured tasks but still underperform on nuanced or affective judgments, highlighting the continued value of human evaluation.
5.6.  Annotator Expertise and Domain Knowledge
Annotator experience and subject-matter knowledge strongly affect both annotation quality and reliability. In knowledge-intensive domains such as legal text, domain experts are often essential, as they can apply specialised concepts consistently and resolve ambiguities that non-experts may misinterpret
Yang et al. (2019)
. Even among experts, however, variability persists, as shown in medical imaging and other high-stakes tasks, reflecting the inherent complexity of annotation in such settings
Yang et al. (2023)
. For general tasks such as sentiment analysis or entity tagging, aggregated non-expert labels can achieve high reliability
Zlabinger et al. (2020)
;
Snow et al. (2008)
. Training and calibration also play a key role: novice annotators typically introduce higher variance, but consistency improves through structured feedback, curated examples, and repeated exposure
Huang et al. (2020)
;
Zlabinger et al. (2020)
.
Expertise, however, extends beyond factual knowledge to include interpretive perspective. Homogeneous expert groups may achieve high agreement but risk amplifying shared biases and overlooking alternative viewpoints. Mixed-expertise or crowdsourced settings tend to be noisier but are valuable for subjective or contested phenomena such as offensiveness, subjectivity, or inference, where disagreement may reflect genuine diversity rather than error
Mehta and Srikumar (2023)
;
Snow et al. (2008)
. Accordingly, documenting annotator backgrounds, training procedures, and recruitment strategies is critical for contextualising agreement scores and assessing generalisability. Transparent reporting of such information supports both reproducibility and ethical accountability in annotation research
Wang et al. (2013)
.
Cultural and linguistic background also shapes annotation behaviour.
Hershcovich et al. (2022)
emphasise that NLP must account for cultural as well as linguistic variation, since interpretations of meaning and social norms differ across communities.
Lee et al. (2024)
report large cross-country differences in English hate-speech labels, and
Pang et al. (2023)
find similar variation across cultural groups in human-labelling tasks. Together, these studies show that annotation reflects cultural perspective as much as linguistic competence and highlight the importance of documenting annotator backgrounds and considering cross-cultural diversity in dataset design.
6.  Conclusion
IAA is fundamental to ensuring the reliability and reproducibility of annotated data in NLP, but its value depends on more than just reporting a number. Reliable evaluation requires aligning the agreement measure with the task and rater design, clearly communicating underlying assumptions, and reporting uncertainty to reflect the limits of precision. Equally important is examining patterns of disagreement to understand whether they reflect ambiguity, bias, or inconsistency. Treating IAA as an integral part of the methodological process can lead to more transparent and interpretable annotation and evaluation practices.
7.  Limitations
This paper aims to provide an accessible overview of IAA measures used across different types of NLP annotation and evaluation tasks. As such, it focuses on breadth rather than depth, outlining commonly applied metrics and their practical implications. Readers seeking detailed mathematical descriptions or domain-specific adaptations are encouraged to explore the primary literature cited throughout this paper. Practitioners are additionally advised to carefully plan their annotation task before committing to a specific metric.
While we have aimed to cover a wide range of IAA metrics, it is possible that certain tasks or niche metrics have been omitted. Areas such as multimodal annotation, interactive evaluation, and subjective phenomena like humour or creativity may require approaches beyond those discussed in this paper.
Acknowledgements
Joseph James is supported by the Centre for Doctoral Training in Speech and Language Technologies (SLT) and their Applications funded by UK Research and Innovation [grant number EP/S023062/1].
8.  Bibliographical References
Abercrombie
et al.
(2023)
G. Abercrombie, V. Rieser, and D. Hovy
Consistency is key: disentangling label variation in natural language processing with intra-annotator agreement
.
arXiv preprint arXiv:2301.10684
.
Cited by:
§4
.
Altman (1990)
D. G. Altman
Practical statistics for medical research
.
Chapman and Hall/CRC
.
Artstein and Poesio (2008)
R. Artstein and M. Poesio
Inter-coder agreement for computational linguistics
.
Computational linguistics
34
(
4
),
pp. 555–596
.
Cited by:
§5.2
.
S. Balloccu, A. Belz, R. Huidrom, E. Reiter, J. Sedoc, and C. Thomson (Eds.) (2024)
S. Balloccu, A. Belz, R. Huidrom, E. Reiter, J. Sedoc, and C. Thomson (Eds.)
Proceedings of the fourth workshop on human evaluation of nlp systems (humeval) @ lrec-coling 2024
.
ELRA and ICCL
,
Torino, Italia
.
External Links:
Link
Cited by:
§1
.
Bavaresco
et al.
(2025)
A. Bavaresco, R. Bernardi, L. Bertolazzi, D. Elliott, R. Fernández, A. Gatt, E. Ghaleb, M. Giulianelli, M. Hanna, A. Koller, A. Martins, P. Mondorf, V. Neplenbroek, S. Pezzelle, B. Plank, D. Schlangen, A. Suglia, A. K. Surikuchi, E. Takmaz, and A. Testoni
LLMs instead of human judges? a large scale empirical study across 20 NLP evaluation tasks
.
In
Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)
,
W. Che, J. Nabende, E. Shutova, and M. T. Pilehvar (Eds.)
,
Vienna, Austria
,
pp. 238–255
.
External Links:
Link
,
Document
,
ISBN 979-8-89176-252-7
Cited by:
§1
.
Beeferman
et al.
(1999)
D. Beeferman, A. Berger, and J. Lafferty
Statistical models for text segmentation
.
Machine learning
34
(
1
),
pp. 177–210
.
Cited by:
1st item
.
BENNETT
et al.
(1954)
E. M. BENNETT, R. ALPERT, and A. C. GOLDSTEIN
Communications through limited-response questioning*
.
Public Opinion Quarterly
18
(
3
),
pp. 303–308
.
External Links:
ISSN 0033-362X
,
Document
,
Link
,
https://academic.oup.com/poq/article-pdf/18/3/303/5384778/18-3-303.pdf
Cited by:
§2.2
.
Bojić
et al.
(2025)
L. Bojić, O. Zagovora, A. Zelenkauskaite, V. Vuković, M. Čabarkapa, S. Veseljević Jerković, and A. Jovančević
Comparing large language models and human annotators in latent content analysis of sentiment, political leaning, emotional intensity and sarcasm
.
Scientific reports
15
(
1
),
pp. 11477
.
Cited by:
§5.5
.
Braylan
et al.
(2022)
A. Braylan, O. Alonso, and M. Lease
Measuring annotator agreement generally across complex structured, multi-object, and free-text annotation tasks
.
In
Proceedings of the ACM Web Conference 2022
,
pp. 1720–1730
.
Cited by:
§1
.
Chang
et al.
(2024)
Y. Chang, X. Wang, J. Wang, Y. Wu, L. Yang, K. Zhu, H. Chen, X. Yi, C. Wang, Y. Wang,
et al.
A survey on evaluation of large language models
.
ACM transactions on intelligent systems and technology
15
(
3
),
pp. 1–45
.
Cited by:
§5.5
.
Chhun
et al.
(2022)
C. Chhun, P. Colombo, F. M. Suchanek, and C. Clavel
Of human criteria and automatic metrics: a benchmark of the evaluation of story generation
.
In
Proceedings of the 29th International Conference on Computational Linguistics
,
N. Calzolari, C. Huang, H. Kim, J. Pustejovsky, L. Wanner, K. Choi, P. Ryu, H. Chen, L. Donatelli, H. Ji, S. Kurohashi, P. Paggio, N. Xue, S. Kim, Y. Hahm, Z. He, T. K. Lee, E. Santus, F. Bond, and S. Na (Eds.)
,
Gyeongju, Republic of Korea
,
pp. 5794–5836
.
External Links:
Link
Cited by:
§1
.
Chhun
et al.
(2024)
C. Chhun, F. M. Suchanek, and C. Clavel
Do language models enjoy their own stories? prompting large language models for automatic story evaluation
.
Transactions of the Association for Computational Linguistics
12
,
pp. 1122–1142
.
External Links:
Link
,
Document
Cited by:
§2.7
.
Cohen (1960)
J. Cohen
A coefficient of agreement for nominal scales
.
Educational and Psychological Measurement
20
(
1
),
pp. 37–46
.
Cited by:
§2.3
.
Cohen (1968)
J. Cohen
Weighted kappa: nominal scale agreement provision for scaled disagreement or partial credit.
.
Psychological bulletin
70
(
4
),
pp. 213
.
Cited by:
§2.5
.
Cronbach (1951)
L. J. Cronbach
Coefficient alpha and the internal structure of tests
.
psychometrika
16
(
3
),
pp. 297–334
.
Cited by:
§4.2
.
Deng
et al.
(2023)
N. Deng, X. Zhang, S. Liu, W. Wu, L. Wang, and R. Mihalcea
You are what you annotate: towards better models through annotator representations
.
In
Findings of the Association for Computational Linguistics: EMNLP 2023
,
H. Bouamor, J. Pino, and K. Bali (Eds.)
,
Singapore
,
pp. 12475–12498
.
External Links:
Link
,
Document
Cited by:
§1
.
Fleisig
et al.
(2023)
E. Fleisig, R. Abebe, and D. Klein
When the majority is wrong: modeling annotator disagreement for subjective tasks
.
arXiv preprint arXiv:2305.06626
.
Cited by:
§5.3
,
§5.3
.
Fleiss (1971)
J. L. Fleiss
Measuring nominal scale agreement among many raters
.
Psychological Bulletin
76
(
5
),
pp. 378–382
.
Cited by:
§2.4
.
Fournier and Inkpen (2012)
C. Fournier and D. Inkpen
Segmentation similarity and agreement
.
In
Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies
,
E. Fosler-Lussier, E. Riloff, and S. Bangalore (Eds.)
,
Montréal, Canada
,
pp. 152–161
.
External Links:
Link
Cited by:
§3.2
.
Fournier (2013)
C. Fournier
Evaluating text segmentation using boundary edit distance
.
In
Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
,
pp. 1702–1712
.
Cited by:
§3.4
.
Ghosh
et al.
(2024)
S. Ghosh, T. Srinivasan, and S. Swayamdipta
Compare without despair: reliable preference evaluation with generation separability
.
In
Findings of the Association for Computational Linguistics: EMNLP 2024
,
Y. Al-Onaizan, M. Bansal, and Y. Chen (Eds.)
,
Miami, Florida, USA
,
pp. 12787–12805
.
External Links:
Link
,
Document
Cited by:
§1
.
Gilardi
et al.
(2023)
F. Gilardi, M. Alizadeh, and M. Kubli
ChatGPT outperforms crowd workers for text-annotation tasks
.
Proceedings of the National Academy of Sciences
120
(
30
),
pp. e2305016120
.
Cited by:
§5.5
.
Gu
et al.
(2024)
J. Gu, X. Jiang, Z. Shi, H. Tan, X. Zhai, C. Xu, W. Li, Y. Shen, S. Ma, H. Liu,
et al.
A survey on llm-as-a-judge
.
arXiv preprint arXiv:2411.15594
.
Cited by:
§5.5
.
Gwet (2001)
K. Gwet
Handbook of inter-rater reliability
.
Gaithersburg, MD: STATAXIS Publishing Company
,
pp. 223–246
.
Cited by:
§2.7
.
Hallgren (2012)
K. A. Hallgren
Computing inter-rater reliability for observational data: an overview and tutorial
.
Tutorials in quantitative methods for psychology
8
(
1
),
pp. 23
.
Cited by:
§1
,
§1
.
Hayes and Krippendorff (2007)
A. F. Hayes and K. Krippendorff
Answering the call for a standard reliability measure for coding data
.
Communication methods and measures
1
(
1
),
pp. 77–89
.
Cited by:
§1
,
§1
.
Hershcovich
et al.
(2022)
D. Hershcovich, S. Frank, H. Lent, M. de Lhoneux, M. Abdou, S. Brandl, E. Bugliarello, L. Cabello Piqueras, I. Chalkidis, R. Cui, C. Fierro, K. Margatina, P. Rust, and A. Søgaard
Challenges and strategies in cross-cultural NLP
.
In
Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
,
S. Muresan, P. Nakov, and A. Villavicencio (Eds.)
,
Dublin, Ireland
,
pp. 6997–7013
.
External Links:
Link
,
Document
Cited by:
§5.6
.
Howcroft
et al.
(2020)
D. M. Howcroft, A. Belz, M. Clinciu, D. Gkatzia, S. A. Hasan, S. Mahamood, S. Mille, E. van Miltenburg, S. Santhanam, and V. Rieser
Twenty years of confusion in human evaluation: NLG needs evaluation sheets and standardised definitions
.
In
Proceedings of the 13th International Conference on Natural Language Generation
,
B. Davis, Y. Graham, J. Kelleher, and Y. Sripada (Eds.)
,
Dublin, Ireland
,
pp. 169–182
.
External Links:
Link
,
Document
Cited by:
§5.2
.
Huang
et al.
(2020)
T. Huang, C. Huang, C. C. Ding, Y. Hsu, and C. L. Giles
Coda-19: using a non-expert crowd to annotate research aspects on 10,000+ abstracts in the covid-19 open research dataset
.
arXiv preprint arXiv:2005.02367
.
Cited by:
§5.6
.
Kendall (1938)
M. G. Kendall
A new measure of rank correlation
.
Biometrika
30
(
1-2
),
pp. 81–93
.
Cited by:
§4.4
.
Klie
et al.
(2024)
J. Klie, R. E. d. Castilho, and I. Gurevych
Analyzing dataset annotation quality management in the wild
.
Computational Linguistics
50
(
3
),
pp. 817–866
.
Cited by:
§5.1
,
§5.1
.
Kohen (1960)
J. Kohen
A coefficient of agreement for nominal scale
.
Educ Psychol Meas
20
,
pp. 37–46
.
Cited by:
§1
.
Koo and Li (2016)
T. K. Koo and M. Y. Li
A guideline of selecting and reporting intraclass correlation coefficients for reliability research
.
Journal of chiropractic medicine
15
(
2
),
pp. 155–163
.
Cited by:
§5.1
.
Krippendorff (2013)
K. Krippendorff
Content analysis: an introduction to its methodology
.
3rd edition
,
SAGE Publications
.
Cited by:
§2.6
.
Landis and Koch (1977)
J. R. Landis and G. G. Koch
The measurement of observer agreement for categorical data
.
biometrics
,
pp. 159–174
.
Cited by:
§5.1
.
Laskar
et al.
(2024)
M. T. R. Laskar, S. Alqahtani, M. S. Bari, M. Rahman, M. A. M. Khan, H. Khan, I. Jahan, A. Bhuiyan, C. W. Tan, M. R. Parvez, E. Hoque, S. Joty, and J. Huang
A systematic survey and critical review on evaluating large language models: challenges, limitations, and recommendations
.
In
Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing
,
Y. Al-Onaizan, M. Bansal, and Y. Chen (Eds.)
,
Miami, Florida, USA
,
pp. 13785–13816
.
External Links:
Link
,
Document
Cited by:
§5.5
.
Lawrence and Lin (1989)
I. Lawrence and K. Lin
A concordance correlation coefficient to evaluate reproducibility
.
Biometrics
,
pp. 255–268
.
Cited by:
§4.3
.
Lee
et al.
(2024)
N. Lee, C. Jung, J. Myung, J. Jin, J. Camacho-Collados, J. Kim, and A. Oh
Exploring cross-cultural differences in English hate speech annotations: from dataset construction to analysis
.
In
Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)
,
K. Duh, H. Gomez, and S. Bethard (Eds.)
,
Mexico City, Mexico
,
pp. 4205–4224
.
External Links:
Link
,
Document
Cited by:
§5.6
.
Li
et al.
(2024a)
D. Li, C. Rose, A. Yuan, and C. Zhou
Estimating agreement by chance for sequence annotation
.
In
Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
,
L. Ku, A. Martins, and V. Srikumar (Eds.)
,
Bangkok, Thailand
,
pp. 5085–5097
.
External Links:
Link
,
Document
Cited by:
§5.1
.
Li
et al.
(2024b)
H. Li, Q. Dong, J. Chen, H. Su, Y. Zhou, Q. Ai, Z. Ye, and Y. Liu
Llms-as-judges: a comprehensive survey on llm-based evaluation methods
.
arXiv preprint arXiv:2412.05579
.
Cited by:
§5.5
.
Lim
et al.
(2024)
G. Lim, S. Larson, Y. Huang, and K. Leach
Towards fair pay and equal work: imposing view time limits in crowdsourced image classification
.
arXiv preprint arXiv:2412.00260
.
Cited by:
§5.4
.
Liu
et al.
(2024)
Y. Liu, H. Zhou, Z. Guo, E. Shareghi, I. Vulić, A. Korhonen, and N. Collier
Aligning with human judgement: the role of pairwise preference in large language model evaluators
.
arXiv preprint arXiv:2403.16950
.
Cited by:
§1
.
Mathet
et al.
(2015)
Y. Mathet, A. Widlöcher, and J. Métivier
The unified and holistic method gamma for inter-annotator agreement measure and alignment
.
Computational Linguistics
41
(
3
),
pp. 437–479
.
Cited by:
§3.3
.
McGraw and Wong (1996a)
K. O. McGraw and S. P. Wong
Forming inferences about some intraclass correlation coefficients.
.
Psychological methods
1
(
1
),
pp. 30
.
Cited by:
§4.1
.
McGraw and Wong (1996b)
K. O. McGraw and S. P. Wong
Forming inferences about some intraclass correlation coefficients
.
Psychological Methods
1
(
1
),
pp. 30–46
.
McHugh (2012)
M. L. McHugh
Interrater reliability: the kappa statistic
.
Biochemia medica
22
(
3
),
pp. 276–282
.
Cited by:
§5.1
,
§5.2
.
Mehta and Srikumar (2023)
M. Mehta and V. Srikumar
Verifying annotation agreement without multiple experts: a case study with Gujarati SNACS
.
In
Findings of the Association for Computational Linguistics: ACL 2023
,
A. Rogers, J. Boyd-Graber, and N. Okazaki (Eds.)
,
Toronto, Canada
,
pp. 10941–10958
.
External Links:
Link
,
Document
Cited by:
§5.6
.
Mohammad
et al.
(2018)
S. Mohammad, F. Bravo-Marquez, M. Salameh, and S. Kiritchenko
SemEval-2018 task 1: affect in tweets
.
In
Proceedings of the 12th International Workshop on Semantic Evaluation
,
M. Apidianaki, S. M. Mohammad, J. May, E. Shutova, S. Bethard, and M. Carpuat (Eds.)
,
New Orleans, Louisiana
,
pp. 1–17
.
External Links:
Link
,
Document
Cited by:
§2.1
.
Pang
et al.
(2023)
R. Y. Pang, J. Cenatempo, F. Graham, B. Kuehn, M. Whisenant, P. Botchway, K. Stone Perez, and A. Koenecke
Auditing cross-cultural consistency of human-annotated labels for recommendation systems
.
In
Proceedings of the 2023 ACM Conference on Fairness, Accountability, and Transparency
,
pp. 1531–1552
.
Cited by:
§5.6
.
Pearson (1895)
K. Pearson
VII. note on regression and inheritance in the case of two parents
.
proceedings of the royal society of London
58
(
347-352
),
pp. 240–242
.
Cited by:
§4.4
.
Pevzner and Hearst (2002a)
L. Pevzner and M. Hearst
A critique and improvement of the p
k
{}_{k}
metric for text segmentation
.
In
Proceedings of the 40th Annual Meeting on Association for Computational Linguistics (ACL)
,
pp. 27–36
.
Pevzner and Hearst (2002b)
L. Pevzner and M. A. Hearst
A critique and improvement of an evaluation metric for text segmentation
.
Computational Linguistics
28
(
1
),
pp. 19–36
.
Cited by:
2nd item
.
Plank (2022)
B. Plank
The “problem” of human label variation: on ground truth in data, modeling and evaluation
.
In
Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing
,
Y. Goldberg, Z. Kozareva, and Y. Zhang (Eds.)
,
Abu Dhabi, United Arab Emirates
,
pp. 10671–10682
.
External Links:
Link
,
Document
Cited by:
§5.2
.
Reichenheim (2004)
M. E. Reichenheim
Confidence intervals for the kappa statistic
.
The Stata Journal
4
(
4
),
pp. 421–428
.
Cited by:
§5.2
.
Reidsma and Carletta (2008)
D. Reidsma and J. Carletta
Reliability measurement without limits
.
Computational Linguistics
34
(
3
),
pp. 319–326
.
Cited by:
§5.3
.
Richie
et al.
(2022)
R. Richie, S. Grover, and F. (. Tsui
Inter-annotator agreement is not the ceiling of machine learning performance: evidence from a comprehensive set of simulations
.
In
Proceedings of the 21st Workshop on Biomedical Language Processing
,
D. Demner-Fushman, K. B. Cohen, S. Ananiadou, and J. Tsujii (Eds.)
,
Dublin, Ireland
,
pp. 275–284
.
External Links:
Link
,
Document
Cited by:
§5.1
.
Rodríguez-Barroso
et al.
(2024)
N. Rodríguez-Barroso, E. M. Cámara, J. C. Collados, M. V. Luzón, and F. Herrera
Federated learning for exploiting annotators’ disagreements in natural language processing
.
Transactions of the Association for Computational Linguistics
12
,
pp. 630–648
.
External Links:
Link
,
Document
Cited by:
§5.3
,
§5.3
.
Rogstadius
et al.
(2011)
J. Rogstadius, V. Kostakos, A. Kittur, B. Smus, J. Laredo, and M. Vukovic
An assessment of intrinsic and extrinsic motivation on task performance in crowdsourcing markets
.
In
Proceedings of the international AAAI conference on web and social media
,
Vol.
5
,
pp. 321–328
.
Cited by:
§5.4
.
Salminen
et al.
(2023)
J. Salminen, A. M. S. Kamel, S. Jung, M. Mustak, and B. J. Jansen
Fair compensation of crowdsourcing work: the problem of flat rates
.
Behaviour & Information Technology
42
(
16
),
pp. 2871–2892
.
Cited by:
§5.4
.
Sandri
et al.
(2023)
M. Sandri, E. Leonardelli, S. Tonelli, and E. Jezek
Why don’t you do it right? analysing annotators’ disagreement in subjective tasks
.
In
Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics
,
A. Vlachos and I. Augenstein (Eds.)
,
Dubrovnik, Croatia
,
pp. 2428–2441
.
External Links:
Link
,
Document
Cited by:
§5.3
.
Scaiano and Inkpen (2012)
M. Scaiano and D. Inkpen
Getting more from segmentation evaluation
.
In
Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies
,
E. Fosler-Lussier, E. Riloff, and S. Bangalore (Eds.)
,
Montréal, Canada
,
pp. 362–366
.
External Links:
Link
Cited by:
§3.2
.
Schlicher
et al.
(2021)
K. D. Schlicher, J. Schulte, M. Reimann, and G. W. Maier
Flexible, self-determined… and unhealthy? an empirical study on somatic health among crowdworkers
.
Frontiers in Psychology
12
,
pp. 724966
.
Cited by:
§5.4
.
Scott (1955)
W. A. Scott
Reliability of content analysis: the case of nominal scale coding
.
Public opinion quarterly
,
pp. 321–325
.
Cited by:
§2.4
.
Shmueli
et al.
(2021)
B. Shmueli, J. Fell, S. Ray, and L. Ku
Beyond fair pay: ethical implications of NLP crowdsourcing
.
In
Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies
,
K. Toutanova, A. Rumshisky, L. Zettlemoyer, D. Hakkani-Tur, I. Beltagy, S. Bethard, R. Cotterell, T. Chakraborty, and Y. Zhou (Eds.)
,
Online
,
pp. 3758–3769
.
External Links:
Link
,
Document
Cited by:
§5.4
,
§5.4
.
Shrout and Fleiss (1979)
P. E. Shrout and J. L. Fleiss
Intraclass correlations: uses in assessing rater reliability.
.
Psychological bulletin
86
(
2
),
pp. 420
.
Cited by:
§4.1
.
Snow
et al.
(2008)
R. Snow, B. O’Connor, D. Jurafsky, and A. Ng
Cheap and fast – but is it good? evaluating non-expert annotations for natural language tasks
.
In
Proceedings of the 2008 Conference on Empirical Methods in Natural Language Processing
,
M. Lapata and H. T. Ng (Eds.)
,
Honolulu, Hawaii
,
pp. 254–263
.
External Links:
Link
Cited by:
§5.4
,
§5.6
,
§5.6
.
Spearman (1904)
C. Spearman
The proof and measurement of association between two things
.
The American Journal of Psychology
15
(
1
),
pp. 72–101
.
External Links:
ISSN 00029556
,
Link
Cited by:
§4.4
.
Stefanovitch and Piskorski (2023)
N. Stefanovitch and J. Piskorski
Holistic inter-annotator agreement and corpus coherence estimation in a large-scale multilingual annotation campaign
.
In
Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing
,
H. Bouamor, J. Pino, and K. Bali (Eds.)
,
Singapore
,
pp. 71–86
.
External Links:
Link
,
Document
Cited by:
§5.1
.
Tam
et al.
(2024)
T. Y. C. Tam, S. Sivarajkumar, S. Kapoor, A. V. Stolyar, K. Polanska, K. R. McCarthy, H. Osterhoudt, X. Wu, S. Visweswaran, S. Fu,
et al.
A framework for human evaluation of large language models in healthcare derived from literature review
.
NPJ digital medicine
7
(
1
),
pp. 258
.
Cited by:
§1
.
Viera
et al.
(2005)
A. J. Viera J. M. Garrett
et al.
Understanding interobserver agreement: the kappa statistic
.
Fam med
37
(
5
),
pp. 360–363
.
Cited by:
§5.1
.
Wan
et al.
(2023)
R. Wan, J. Kim, and D. Kang
Everyone’s voice matters: quantifying annotation disagreement using demographic information
.
In
Proceedings of the AAAI Conference on Artificial Intelligence
,
Vol.
37
,
pp. 14523–14530
.
Cited by:
§5.3
.
Wang
et al.
(2013)
A. Wang, C. D. V. Hoang, and M. Kan
Perspectives on crowdsourcing annotations for natural language processing
.
Language resources and evaluation
47
(
1
),
pp. 9–31
.
Cited by:
§5.6
.
Wei
et al.
(2018)
Q. Wei, A. Franklin, T. Cohen, and H. Xu
Clinical text annotation–what factors are associated with the cost of time?
.
In
AMIA Annual Symposium Proceedings
,
Vol.
2018
,
pp. 1552
.
Cited by:
§5.4
.
Wong
et al.
(2021)
K. Wong, P. Paritosh, and L. Aroyo
Cross-replication reliability - an empirical approach to interpreting inter-rater reliability
.
In
Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers)
,
C. Zong, F. Xia, W. Li, and R. Navigli (Eds.)
,
Online
,
pp. 7053–7065
.
External Links:
Link
,
Document
Cited by:
§5.1
.
Wong and Paritosh (2022)
K. Wong and P. Paritosh
K-Rater Reliability: The correct unit of reliability for aggregated human annotations
.
In
Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)
,
S. Muresan, P. Nakov, and A. Villavicencio (Eds.)
,
Dublin, Ireland
,
pp. 378–384
.
External Links:
Link
,
Document
Cited by:
§4
,
§5.1
.
Wu
et al.
(2022)
C. M. Wu, E. Schulz, T. J. Pleskac, and M. Speekenbrink
Time pressure changes how people explore and respond to uncertainty
.
Scientific reports
12
(
1
),
pp. 4122
.
Cited by:
§5.4
.
Xu
et al.
(2024)
J. Xu, M. Theune, and D. Braun
Leveraging annotator disagreement for text classification
.
In
Proceedings of the 7th International Conference on Natural Language and Speech Processing (ICNLSP 2024)
,
M. Abbas and A. A. Freihat (Eds.)
,
Trento
,
pp. 1–10
.
External Links:
Link
Cited by:
§5.3
,
§5.3
.
Yang
et al.
(2023)
F. Yang, G. Zamzmi, S. Angara, S. Rajaraman, A. Aquilina, Z. Xue, S. Jaeger, E. Papagiannakis, and S. K. Antani
Assessing inter-annotator agreement for medical image segmentation
.
IEEE Access
11
,
pp. 21300–21312
.
Cited by:
§5.6
.
Yang
et al.
(2019)
Y. Yang, O. Agarwal, C. Tar, B. C. Wallace, and A. Nenkova
Predicting annotation difficulty to improve task routing and model performance for biomedical information extraction
.
arXiv preprint arXiv:1905.07791
.
Cited by:
§5.6
.
Zlabinger
et al.
(2020)
M. Zlabinger, M. Sabou, S. Hofstätter, M. Sertkan, and A. Hanbury
DEXA: supporting non-expert annotators with dynamic examples from experts
.
In
Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval
,
pp. 2109–2112
.
Cited by:
§5.6
.
*