---
title: '[2210.13265] Toward improved inference for Krippendorff’s Alpha agreement
  coefficient'
id: 221013265-toward-improved-inference-for-krippendorffs-alpha-agreement-coefficien
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:47:47.344388Z'
source: https://ar5iv.labs.arxiv.org/html/2210.13265
source_domain: ar5iv.labs.arxiv.org
fetched_at: '2026-09-15T02:47:47.342383Z'
fetch_provider: builtin
status: draft
type: note
tier: institutional
content_type: paper
deprecated: false
---

[2210.13265] Toward improved inference for Krippendorff’s Alpha agreement coefficient
Toward improved inference for Krippendorff’s Alpha agreement coefficient
John Hughes
Affiliation:
Lehigh University
Affiliation:
Bethlehem, PA, USA 18015
Abstract
In this article I recommend a better point estimator for Krippendorff’s Alpha agreement coefficient, and develop a jackknife variance estimator that leads to much better interval estimation than does the customary bootstrap procedure or an alternative bootstrap procedure. Having developed the new methodology, I analyze nominal data previously analyzed by Krippendorff, and two experimentally observed datasets: (1) ordinal data from an imaging study of congenital diaphragmatic hernia, and (2) United States Environmental Protection Agency air pollution data for the Philadelphia, Pennsylvania area. The latter two applications are novel. The proposed methodology is now supported in version 2.0 of my open source R package,
krippendorffsalpha
, which supports common and user-defined distance functions, and can accommodate any number of units, any number of coders, and missingness. Interval computation can be parallelized.
1
Introduction
Krippendorff’s
α
\alpha
(
Hayes and Krippendorff, 2007
)
is a well-known methodology for statistically assessing agreement. Although
α
\alpha
is non-parametric, the customary
α
\alpha
estimator is motivated by an estimator of the intraclass correlation coefficient in the one-way mixed-effects analysis of variance (ANOVA) model
(
Ravishanker et al., 2021
)
, a much studied fully parametric model. In this article I leverage
α
\alpha
’s connection with the one-way mixed-effects ANOVA model to explore the customary approach to inference for Krippendorff’s
α
\alpha
, finding that both the point estimator and interval estimation have substantial drawbacks for smaller, yet realistic, sample sizes. Then I consider a better point estimator; and propose a jackknife variance estimator
(
Hinkley, 1977
)
that yields interval estimates having very nearly their desired coverage rates, even in unfavorable conditions. I evaluate the various procedures not only formally but also by way of extensive and realistic simulation studies. Finally, I analyze data previously analyzed by Krippendorff and others, along with two experimentally observed datasets: (1) radiologist-assigned grades in an imaging study of congenital diaphragmatic hernia (CDH), and (2) United States Environmental Protection Agency (EPA) PM
2.5
data from seven geographically dispersed air sensors in or near Philadelphia, Pennsylvania.
2
Measuring agreement
An inter-coder agreement coefficient—which takes a value in the unit interval, with 0 indicating no agreement and 1 indicating perfect agreement—is a statistical measure of the extent to which two or more coders agree regarding the same units of analysis. The agreement problem has a long history and is important in many fields of inquiry, and numerous agreement statistics have been proposed.
The earliest agreement coefficients were
S
S
(
Bennett et al., 1954
)
,
π
\pi
(
Scott, 1955
)
, and
κ
\kappa
(
Cohen, 1960
)
.
Bennett et al., 1954
proposed the
S
S
score as a measure of the extent to which two methods of communication provide identical information.
Scott, 1955
proposed the
π
\pi
coefficient for measuring agreement between two coders.
Cohen, 1960
criticized
π
\pi
and proposed the
κ
\kappa
coefficient as an alternative to
π
\pi
—although
Smeeton, 1985
noted that Francis Galton mentioned a
κ
\kappa
-like statistic in his 1892 book,
Finger Prints
.
Fleiss, 1971
proposed multi-
κ
\kappa
, a generalization of Scott’s
π
\pi
for measuring agreement among more than two coders.
Conger, 1980
and
Davies and Fleiss, 1982
likewise generalized
κ
\kappa
to the multi-coder setting. Other generalizations of
κ
\kappa
, e.g., weighted
κ
\kappa
(
Cohen, 1968
)
, have also been proposed. The
κ
\kappa
coefficient and its generalizations can fairly be said to dominate the field and are still widely used despite their well-known shortcomings
(
Feinstein and Cicchetti, 1990
;
Cicchetti and Feinstein, 1990
)
.
Other oft-used measures of agreement are Gwet’s
A
​
C
1
AC_{1}
and
A
​
C
2
AC_{2}
(
Gwet, 2008
)
and Krippendorff’s
α
\alpha
(
Hayes and Krippendorff, 2007
)
, the latter of which is the subject of this article. An even newer agreement methodology is Sklar’s
ω
\omega
(
Hughes, 2022
)
, a parametric Gaussian copula-based framework. For more comprehensive reviews of the literature on agreement, I refer the interested reader to the article by
Banerjee et al., 1999
, the article by
Artstein and Poesio, 2008
, and the book by
Gwet, 2014
.
3
A motivating example
To fix ideas, let us consider an example dataset that was previously analyzed by
Krippendorff, 2013
. The dataset, which comprises 41 nominal codes assigned to a dozen units of analysis by four coders, is shown below. The dots represent missing values.
c
1
c_{1}
c
2
c_{2}
c
3
c_{3}
c
4
c_{4}
u
1
u_{1}
1
1
∙
\bullet
1
u
2
u_{2}
2
2
3
2
u
3
u_{3}
3
3
3
3
u
4
u_{4}
3
3
3
3
u
5
u_{5}
2
2
2
2
u
6
u_{6}
1
2
3
4
u
7
u_{7}
4
4
4
4
u
8
u_{8}
1
1
2
1
u
9
u_{9}
2
2
2
2
u
10
u_{10}
∙
\bullet
5
5
5
u
11
u_{11}
∙
\bullet
∙
\bullet
1
1
u
12
u_{12}
∙
\bullet
3
∙
\bullet
∙
\bullet
Figure 1:
Nominal scores previously analyzed by Krippendorff, for twelve units and four coders. The dots represent missing values.
Because this dataset is small and the codes are nominal, it is easy to hypothesize by inspection that agreement is high. Indeed, eight of the units exhibit perfect agreement, and two of the remaining units exhibit near-perfect agreement. The only unit about which the coders evidently disagreed is unit 6. And of course the final unit carries no information regarding agreement. These facts taken together suggest that an estimated agreement coefficient for these data should not be too far from 1, unless the estimator in question is strongly influenced by the disagreement over unit 6.
Before analyzing these data I should mention that I will interpret results according to the agreement scale given in Table
1
(
Landis and Koch, 1977
)
. Although this scale is well-established, agreement scales remain a subject of debate
(
Taber, 2018
)
, and so the following scale—indeed, any agreement scale—should be applied circumspectly.
Table 1:
Guidelines for interpreting values of an agreement coefficient.
Range of Agreement
Interpretation
α
≤
0.2
\phantom{0.2<\;}\alpha\leq 0.2
Slight Agreement
0.2
<
α
≤
0.4
0.2<\alpha\leq 0.4
Fair Agreement
0.4
<
α
≤
0.6
0.4<\alpha\leq 0.6
Moderate Agreement
0.6
<
α
≤
0.8
0.6<\alpha\leq 0.8
Substantial Agreement
α
>
0.8
\phantom{0.2<\;}\alpha>0.8
Near-Perfect Agreement
Applying the customary Krippendorff’s
α
\alpha
methodology to these data, with the discrete metric
d
2
(
x
,
y
)
=
1
{
x
≠
y
}
d^{2}(x,y)=1\{x\neq y\}
as the distance function, yields point estimate
α
^
=
0.743
\hat{\alpha}=0.743
and 95% confidence interval
(
0.459
,
1.000
)
(0.459,1.000)
. This estimate of
α
\alpha
indicates substantial agreement, and the interval suggests that these data are consistent with agreement ranging from fair to perfect. If one repeats the analysis having removed unit 6, the point estimate changes to
0.857
0.857
, and the interval becomes
(
0.679
,
1.000
)
(0.679,1.000)
. Thus we see that unit 6 was (perhaps unduly) influential since the new results indicate near-perfect agreement (point estimate) and at least substantial agreement (interval estimate).
I will return to these data in Section
9
, where I will apply my proposed methodology and compare those results to these.
4
The customary Krippendorff’s
α
\alpha
methodology
Hughes, 2021a
showed that Krippendorff’s
α
\alpha
finds its origin in the well-known one-way mixed-effects ANOVA model. In this section I will review
Hughes, 2021a
’ demonstration, and then elaborate on it for the purposes of this article.
4.1
Krippendorff’s
α
\alpha
and the one-way mixed-effects ANOVA model
The one-way mixed-effects ANOVA model is given by
Y
i
​
j
=
μ
+
τ
i
+
ε
i
​
j
,
(
i
=
1
,
2
,
…
,
a
)
​
(
j
=
1
,
2
,
…
,
n
i
)
Y_{ij}=\mu+\tau_{i}+\varepsilon_{ij},\;\;\;\;(i=1,2,\dots,a)\;(j=1,2,\dots,n_{i})
where
•
Y
i
​
j
Y_{ij}
is the
j
j
th score (of
n
i
n_{i}
scores) for the
i
i
th unit (of
a
a
units of analysis);
•
μ
∈
ℝ
\mu\in\mathbb{R}
is the population mean score;
•
τ
i
∼
ind
Normal
​
(
0
,
σ
τ
2
)
\tau_{i}\stackrel{{\scriptstyle\text{ind}}}{{\sim}}\textsc{Normal}(0,\sigma_{\tau}^{2})
are random unit effects such that
σ
τ
2
≥
0
\sigma_{\tau}^{2}\geq 0
;
•
ε
i
​
j
∼
ind
Normal
​
(
0
,
σ
ε
2
)
\varepsilon_{ij}\stackrel{{\scriptstyle\text{ind}}}{{\sim}}\textsc{Normal}(0,\sigma_{\varepsilon}^{2})
are errors such that
σ
ϵ
2
>
0
\sigma_{\epsilon}^{2}>0
; and
•
the unit effects are independent of the errors.
Since the scores for the
i
i
th unit share the unit effect
τ
i
\tau_{i}
, said scores are dependent. Specifically, for
j
≠
j
′
j\neq j^{\prime}
,
cov
​
(
Y
i
​
j
,
Y
i
​
j
′
)
=
σ
τ
2
\text{cov}(Y_{ij},Y_{ij^{\prime}})=\sigma_{\tau}^{2}
, and
α
\displaystyle\alpha
=
cor
​
(
Y
i
​
j
,
Y
i
​
j
′
)
=
σ
τ
2
σ
τ
2
+
σ
ε
2
.
\displaystyle=\text{cor}(Y_{ij},Y_{ij^{\prime}})=\frac{\sigma_{\tau}^{2}}{\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}}.
(1)
This correlation among the scores for a given unit is usually called the intraclass correlation coefficient (ICC). I denote the ICC as ‘
α
\alpha
’ precisely because the ICC is the population parameter for Krippendorff’s
α
\alpha
when the data conform to the one-way mixed-effects ANOVA model. To reveal this connection it suffices to show that Krippendorff’s estimator, which I denote as
α
^
\hat{\alpha}
, is an estimator of
α
\alpha
.
First, note that
α
\alpha
can be written as
α
=
1
−
σ
ε
2
σ
τ
2
+
σ
ε
2
.
\alpha=1-\frac{\sigma_{\varepsilon}^{2}}{\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}}.
This suggests the estimator
α
^
=
1
−
σ
ε
2
^
σ
τ
2
+
σ
ε
2
^
,
\hat{\alpha}=1-\frac{\widehat{\sigma_{\varepsilon}^{2}}}{\widehat{\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}}},
which we can completely specify by identifying estimators
σ
ε
2
^
\widehat{\sigma_{\varepsilon}^{2}}
and
σ
τ
2
+
σ
ε
2
^
\widehat{\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}}
. For the one-way mixed-effects ANOVA model, the customary estimator of the error variance
σ
ε
2
\sigma_{\varepsilon}^{2}
is the so called mean squared error (
M
​
S
​
E
MSE
):
σ
ε
2
^
=
M
​
S
​
E
=
S
​
S
​
E
N
−
a
=
∑
i
=
1
a
∑
j
=
1
n
i
(
Y
i
​
j
−
Y
¯
i
∙
)
2
N
−
a
,
\widehat{\sigma_{\varepsilon}^{2}}=MSE=\frac{SSE}{N-a}=\frac{\sum_{i=1}^{a}\sum_{j=1}^{n_{i}}(Y_{ij}-\bar{Y}_{i\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}})^{2}}{N-a},
where
S
​
S
​
E
SSE
denotes the error sum of squares,
N
=
∑
i
n
i
N=\sum_{i}n_{i}
is the total sample size, and
Y
¯
i
∙
\bar{Y}_{i\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}}
is the sample mean for the
i
i
th unit.
M
​
S
​
E
MSE
is both the method of moments (MoM) estimator and the maximum likelihood estimator of the error variance for the balanced design (i.e., when
n
i
=
n
n_{i}=n
for all
i
i
). For the unbalanced design,
M
​
S
​
E
MSE
is once again the MoM estimator of
σ
ε
2
\sigma_{\varepsilon}^{2}
, but the maximum likelihood estimator of
σ
ε
2
\sigma_{\varepsilon}^{2}
is not available in closed form. For both designs
M
​
S
​
E
MSE
is unbiased for
σ
ε
2
\sigma_{\varepsilon}^{2}
.
Now, to estimate the total variance
σ
τ
2
+
σ
ε
2
\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}
, Krippendorff uses
σ
τ
2
+
σ
ε
2
^
=
M
​
S
​
T
c
=
S
​
S
​
T
c
N
−
1
=
∑
i
=
1
a
∑
j
=
1
n
i
(
Y
i
​
j
−
Y
¯
∙
∙
)
2
N
−
1
,
\widehat{\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}}=MST_{c}=\frac{SST_{c}}{N-1}=\frac{\sum_{i=1}^{a}\sum_{j=1}^{n_{i}}(Y_{ij}-\bar{Y}_{\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}})^{2}}{N-1},
where
S
​
S
​
T
c
SST_{c}
denotes the corrected (for the population mean) total sum of squares and
Y
¯
∙
∙
\bar{Y}_{\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}}
denotes the mean for the entire sample. This estimator seems quite natural given that
𝔼
​
M
​
S
​
T
c
=
N
−
∑
i
n
i
2
N
N
−
1
​
σ
τ
2
+
σ
ε
2
≈
σ
τ
2
+
σ
ε
2
,
\mathbb{E}MST_{c}=\frac{N-\frac{\sum_{i}n_{i}^{2}}{N}}{N-1}\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2}\approx\sigma_{\tau}^{2}+\sigma_{\varepsilon}^{2},
with equality only when
σ
τ
2
=
0
\sigma_{\tau}^{2}=0
(or
n
i
=
1
n_{i}=1
for all
i
i
, which makes no sense). In any case, we arrive at Krippendorff’s point estimator:
α
^
\displaystyle\hat{\alpha}
=
1
−
M
​
S
​
E
M
​
S
​
T
c
.
\displaystyle=1-\frac{MSE}{MST_{c}}.
(2)
This estimator is the customary estimator for Krippendorff’s
α
\alpha
when squared Euclidean distance
d
2
​
(
x
,
y
)
=
(
x
−
y
)
2
d^{2}(x,y)=(x-y)^{2}
is employed as the measure of discrepancy.
Hughes, 2021a
showed how this form of
α
^
\hat{\alpha}
can give rise to the non-parametric form of Krippendorff’s
α
\alpha
, which is incidentally a modified multi-response permutation procedure
(
Mielke and Berry, 2007
)
. The non-parametric form of
α
\alpha
simply makes
d
2
d^{2}
a parameter whose value is chosen by the practitioner based on the type of outcomes to be analyzed—e.g., the discrete metric
d
2
(
x
,
y
)
=
1
{
x
≠
y
}
d^{2}(x,y)=1\{x\neq y\}
for nominal observations, distance function
d
2
​
(
x
,
y
)
=
{
(
x
−
y
)
/
(
x
+
y
)
}
2
d^{2}(x,y)=\{(x-y)/(x+y)\}^{2}
for ratio observations, etc.
It is important to note that
α
\alpha
is an agreement coefficient for all types of outcomes and suitable distance functions
d
2
d^{2}
. However,
α
\alpha
is not a well-defined population parameter for every sensible choice of
d
2
d^{2}
. For example, when the observations are categorical and the discrete metric is used,
α
^
\hat{\alpha}
is surely an estimator of agreement, but the population parameter that
α
^
\hat{\alpha}
estimates cannot be described precisely. This reminds one of the
g
g
factor
(
Warne and Burningham, 2019
)
, a construct that has been defined operationally as that which is measured by various cognitive tests.
4.2
Bias of the customary point estimator
Note that
M
​
S
​
T
c
MST_{c}
is biased downward, and the magnitude of the bias grows as the (average) number of coders increases (for fixed
N
N
). This implies that
α
^
\hat{\alpha}
, which already has a negative bias, becomes much more biased as the shape of the data matrix goes from tall to square to short (
→
\to
→
\to
). This is shown in Figure
2
, where the simulated outcomes were Gaussian and three balanced designs were used: (1) 16 units and 4 coders, (2) 8 units and 8 coders, and (3) 4 units and 16 coders.
16
×
4
16\times 4
8
×
8
8\times 8
4
×
16
4\times 16
Figure 2:
The raw bias (top row) and percent bias (bottom row) for the customary Krippendorff’s
α
\alpha
point estimator.
We see that, as the aspect ratio of the data matrix increases from
1
/
4
1/4
to 1 to 4, the percent bias increases dramatically. For the
16
×
4
16\times 4
data matrix the maximum percent bias is nearly 10%. The maximum percent bias then increases to approximately 15% and 30% for the square and short matrices, respectively. This unappealing behavior can be remedied (Section
5
).
4.3
Coverage rates of the customary interval estimator
The customary approach to interval estimation for Krippendorff’s
α
\alpha
employs a bootstrapping procedure
(
Krippendorff, 2016
)
that seems intuitive but struggles to perform well. The bootstrap sample is produced by computing
α
^
k
∗
=
1
−
M
​
S
​
E
k
∗
M
​
S
​
T
c
\hat{\alpha}_{k}^{*}=1-\frac{MSE_{k}^{*}}{MST_{c}}
for
k
=
1
,
…
,
b
k=1,\dots,b
, where
b
b
is the desired bootstrap sample size;
M
​
S
​
E
k
∗
MSE_{k}^{*}
is
M
​
S
​
E
MSE
computed for a data matrix that was created by resampling, with replacement, the rows of the observed data matrix; and
M
​
S
​
T
c
MST_{c}
is the total mean square for the observed data matrix. Given the resulting bootstrap sample
α
^
1
∗
,
…
,
α
^
b
∗
\hat{\alpha}_{1}^{*},\dots,\hat{\alpha}_{b}^{*}
, one estimates a confidence interval for
α
\alpha
by computing the appropriate quantiles of the bootstrap sample
(
Efron, 1982
)
. That is, we compute a
(
1
−
δ
)
​
100
%
(1-\delta)100\%
interval as
(
L
=
α
^
(
δ
/
2
)
∗
,
U
=
α
^
(
1
−
δ
/
2
)
∗
)
,
(L=\hat{\alpha}_{(\delta/2)}^{*},\;U=\hat{\alpha}_{(1-\delta/2)}^{*}),
where
δ
∈
(
0
,
1
)
\delta\in(0,1)
is the desired significance level. Note that the percentile method is used here because the distribution of
α
^
\hat{\alpha}
tends to be skewed, especially as
α
\alpha
approaches 0 or 1.
The rationale for this method of interval estimation is two-fold. First, the resampling procedure leaves the rows intact to avoid breaking the dependence we aim to measure. Resampling the whole dataset would lead to much-inflated bootstrap estimates of
σ
ϵ
2
\sigma_{\epsilon}^{2}
, which would lead to a badly negatively biased bootstrap sample of
α
^
k
∗
\hat{\alpha}_{k}^{*}
. Second,
M
​
S
​
T
c
MST_{c}
is held fixed because the total sum of squares is invariant to permutation of the data.
It turns out that both of these arguments are incorrect. The second argument—that
M
​
S
​
T
c
MST_{c}
should be held fixed—has the most deleterious effect on interval coverage rates. Of course it is true that
M
​
S
​
T
c
MST_{c}
is invariant to permutation of the dataset, but that is irrelevant. What is relevant is that
M
​
S
​
E
/
M
​
S
​
T
c
MSE/MST_{c}
is a ratio of estimators. Thus holding
M
​
S
​
T
c
MST_{c}
fixed while using resampled data matrices to produce
M
​
S
​
E
1
∗
,
…
,
M
​
S
​
E
b
∗
MSE_{1}^{*},\dots,MSE_{b}^{*}
yields bootstrapped ratios
M
​
S
​
E
k
∗
/
M
​
S
​
T
c
MSE_{k}^{*}/MST_{c}
that are severely under-dispersed relative to the estimator
M
​
S
​
E
/
M
​
S
​
T
c
MSE/MST_{c}
. This is not surprising since failing to account for the variability of
M
​
S
​
T
c
MST_{c}
as well as the variability of
M
​
S
​
E
MSE
is analogous to erroneously assuming that a Student’s
t
t
distributed statistic is standard Gaussian. For smaller samples this, along with the bias of
α
^
\hat{\alpha}
, leads to confidence intervals that have abysmal coverage rates for nearly all values of
α
\alpha
.
The plots in Figure
3
show coverage rates for 95% intervals that were computed using the methodology just described. Once again I include plots for tall, square, and short matrices such that
N
=
a
​
n
N=an
remains constant at 64. We see that the customary interval estimation method performs well for small values of
α
\alpha
, but as
α
\alpha
increases, performance degrades very rapidly and is generally unacceptable.
16
×
4
16\times 4
8
×
8
8\times 8
4
×
16
4\times 16
Figure 3:
Empirical coverage rates of 95% intervals computed using the customary Krippendorff’s
α
\alpha
point estimator and bootstrap procedure.
4.4
Attempting to salvage bootstrap inference for
α
\alpha
As I implied in the preceding section, we should consider producing a bootstrap sample
α
^
1
∗
,
…
,
α
^
b
∗
\hat{\alpha}_{1}^{*},\dots,\hat{\alpha}_{b}^{*}
by resampling the rows of the data matrix with replacement and computing
α
^
k
∗
=
1
−
M
​
S
​
E
k
∗
(
M
​
S
​
T
c
)
k
∗
\hat{\alpha}_{k}^{*}=1-\frac{MSE_{k}^{*}}{(MST_{c})_{k}^{*}}
for each of
b
b
resampled datasets. This would allow us to account for both sources of variation in
α
^
=
1
−
M
​
S
​
E
/
M
​
S
​
T
c
\hat{\alpha}=1-MSE/MST_{c}
.
While this more principled approach does very much improve coverage rates relative to the customary method, said rates are still much too low overall. This is attributable to the simple fact that, for data matrices having a small number of rows, resampling the rows with replacement tends to introduce so much redundancy, i.e., so many duplicate rows, that the apparent variation in the resampled dataset is much smaller than the variation of the original data. This once again leads to rather under-dispersed bootstrap samples, which leads to optimistic confidence intervals.
The plots in Figure
4
show coverage rates for 95% intervals that were computed using the improved bootstrap procedure just described. This figure, too, includes plots for tall, square, and short matrices such that
N
=
a
​
n
N=an
remains constant at 64. The improved bootstrap method performs much better overall than the customary method, yet coverage rates remain much too low.
16
×
4
16\times 4
8
×
8
8\times 8
4
×
16
4\times 16
Figure 4:
Empirical coverage rates of 95% intervals computed using the customary Krippendorff’s
α
\alpha
point estimator and the improved bootstrap procedure.
5
Alternative point estimators for
α
\alpha
The one-way mixed-effects ANOVA model, although apparently simple as a data-generating mechanism, has inspired a rich literature because the model is rather complicated as a data-analytic tool. In this section I describe five alternative estimators of
α
\alpha
found in the literature. I compare the five estimators to one another and to
α
^
\hat{\alpha}
by way of an extensive simulation study. Since the five estimators have been considered in some depth and detail elsewhere, I will keep my presentation brief.
Having chosen a suitable point estimator from among the six considered, I develop a corresponding interval estimation method that performs quite well, even for smaller and/or shorter data matrices. The proposed method also performs well computationally for smaller datasets, when the method is needed most.
5.1
The maximum likelihood estimator
The maximum likelihood estimator (MLE) of
α
\alpha
is available in closed form for the balanced model but not for the unbalanced model. In the balanced case we have
α
̊
\displaystyle\mathring{\alpha}
=
(
1
−
1
/
a
)
​
M
​
S
​
A
−
M
​
S
​
E
(
1
−
1
/
a
)
​
M
​
S
​
A
+
(
n
−
1
)
​
M
​
S
​
E
,
\displaystyle=\frac{(1-1/a)MSA-MSE}{(1-1/a)MSA+(n-1)MSE},
(3)
where
M
​
S
​
A
=
S
​
S
​
A
a
−
1
=
∑
i
=
1
a
n
i
(
Y
¯
i
∙
−
Y
¯
∙
∙
)
2
a
−
1
MSA=\frac{SSA}{a-1}=\frac{\sum_{i=1}^{a}n_{i}(\bar{Y}_{i\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}}-\bar{Y}_{\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}})^{2}}{a-1}
is the “treatment” mean square. The above estimator can be obtained by appealing to the invariance of maximum likelihood estimators and substituting the MLEs
σ
τ
2
̊
=
{
(
1
−
1
/
a
)
​
M
​
S
​
A
−
M
​
S
​
E
}
/
n
\mathring{\sigma_{\tau}^{2}}=\{(1-1/a)MSA-MSE\}/n
and
σ
ε
2
̊
=
M
​
S
​
E
\mathring{\sigma_{\varepsilon}^{2}}=MSE
for
σ
τ
2
\sigma_{\tau}^{2}
and
σ
ε
2
\sigma_{\varepsilon}^{2}
in (
1
). For Gaussian unit effects and errors, the estimator (
3
) is the MLE for
α
\alpha
if and only if
σ
τ
2
̊
\mathring{\sigma_{\tau}^{2}}
is the MLE for
σ
τ
2
\sigma_{\tau}^{2}
, which requires that
σ
τ
2
̊
\mathring{\sigma_{\tau}^{2}}
be non-negative. When
α
̊
\mathring{\alpha}
is the MLE of
α
\alpha
, the estimator is not the ratio of unbiased estimators, nor is the MLE itself unbiased. But of course
α
̊
\mathring{\alpha}
possesses the attractive properties of MLEs, namely, consistency, statistical efficiency, and asymptotic normality.
5.2
The analytical estimator
The most commonly used estimator of
α
\alpha
, which is sometimes called the analytical estimator, is given by
α
~
\displaystyle\tilde{\alpha}
=
σ
τ
2
~
σ
τ
2
~
+
σ
ε
2
~
=
M
​
S
​
A
−
M
​
S
​
E
M
​
S
​
A
+
(
n
−
1
)
​
M
​
S
​
E
,
\displaystyle=\frac{\tilde{\sigma_{\tau}^{2}}}{\tilde{\sigma_{\tau}^{2}}+\tilde{\sigma_{\varepsilon}^{2}}}=\frac{MSA-MSE}{MSA+(n-1)MSE},
(4)
where
M
​
S
​
E
MSE
is unbiased for
σ
ε
2
\sigma_{\varepsilon}^{2}
and
(
M
​
S
​
A
−
M
​
S
​
E
)
/
n
(MSA-MSE)/n
is unbiased for
σ
τ
2
\sigma_{\tau}^{2}
. This is for a balanced model. The corresponding estimator for the unbalanced model is
M
​
S
​
A
−
M
​
S
​
E
M
​
S
​
A
+
(
n
∗
−
1
)
​
M
​
S
​
E
,
\frac{MSA-MSE}{MSA+(n^{*}-1)MSE},
where
n
∗
=
N
−
1
N
​
∑
i
=
1
a
n
i
2
a
−
1
n^{*}=\frac{N-\frac{1}{N}\sum_{i=1}^{a}n_{i}^{2}}{a-1}
is the average number of codes per unit of analysis. These are clearly plug-in MoM estimators since
σ
τ
2
~
\tilde{\sigma_{\tau}^{2}}
and
σ
ε
2
~
\tilde{\sigma_{\varepsilon}^{2}}
are MoM estimators and
α
~
\tilde{\alpha}
is obtained by plugging these estimators into (
1
).
Although the form of
α
~
\tilde{\alpha}
given in (
4
) is intuitive because it mirrors (
1
), it will soon prove useful to have
α
~
\tilde{\alpha}
expressed as
α
~
=
M
​
S
​
A
/
M
​
S
​
E
−
1
M
​
S
​
A
/
M
​
S
​
E
+
n
−
1
.
\tilde{\alpha}=\frac{MSA/MSE-1}{MSA/MSE+n-1}.
Some investigators have referred to
M
​
S
​
A
/
M
​
S
​
E
MSA/MSE
as the variance ratio statistic, where the variance ratio in question is
γ
=
σ
τ
2
/
σ
ϵ
2
\gamma=\sigma_{\tau}^{2}/\sigma_{\epsilon}^{2}
. But
M
​
S
​
A
/
M
​
S
​
E
MSA/MSE
is not an estimator of
γ
\gamma
. Rather,
M
​
S
​
A
/
M
​
S
​
E
MSA/MSE
is an (positively biased) estimator of
θ
=
n
​
γ
+
1
\theta=n\gamma+1
. The relationships among
α
\alpha
,
γ
\gamma
, and
θ
\theta
can be written as
α
=
θ
−
1
θ
+
n
−
1
=
(
n
​
γ
+
1
)
−
1
(
n
​
γ
+
1
)
+
n
−
1
=
n
​
γ
n
​
γ
+
n
=
γ
γ
+
1
.
\alpha=\frac{\theta-1}{\theta+n-1}=\frac{(n\gamma+1)-1}{(n\gamma+1)+n-1}=\frac{n\gamma}{n\gamma+n}=\frac{\gamma}{\gamma+1}.
5.3
A variant of the analytical estimator
The estimator that is the focus of this section is a variant of the analytical estimator. This variant was introduced by
Atenafu et al., 2012
for the express purpose of producing a reduced-bias estimator of
α
\alpha
(see next section).
Atenafu et al., 2012
present their variant (for a balanced design) as
#
�
\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\displaystyle\alpha\hfil
=
#
�
γ
1
+
#
�
γ
,
\displaystyle=\frac{\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}}{1+\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}},
where
#
�
γ
=
{
N
−
a
−
2
}
​
S
​
S
​
A
/
S
​
S
​
E
−
(
a
−
1
)
n
⁡
(
a
−
1
)
\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}=\frac{\{N-a-2\}SSA/SSE-(a-1)}{n(a-1)}
is an unbiased estimator of the variance ratio
γ
\gamma
. To see how
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
is a variant of
α
~
\tilde{\alpha}
, observe that
Atenafu et al., 2012
estimate
θ
\theta
(unbiasedly) as
#
�
θ
=
n
​
#
�
γ
+
1
=
M
​
S
​
A
S
​
S
​
E
/
(
N
−
a
−
2
)
,
\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\theta\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\theta\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\theta\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\theta\hfil$\crcr}}}=n\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}+1=\frac{MSA}{SSE/(N-a-2)},
in contrast to
θ
~
=
M
​
S
​
A
M
​
S
​
E
=
M
​
S
​
A
S
​
S
​
E
/
(
N
−
a
)
\tilde{\theta}=\frac{MSA}{MSE}=\frac{MSA}{SSE/(N-a)}
for the analytical estimator.
Clearly,
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
θ
\hfil\textstyle\theta\hfil
is strictly smaller than
θ
~
\tilde{\theta}
, which implies that
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
is strictly smaller than
α
~
\tilde{\alpha}
. Thus, since
α
~
\tilde{\alpha}
is negatively biased,
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
exacerbates the bias of
α
~
\tilde{\alpha}
, and so
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
is not a compelling estimator of
α
\alpha
in its own right.
Atenafu et al., 2012
simply use
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
as a starting point in their effort to formulate an estimator of
α
\alpha
that has a smaller bias than the analytical estimator
α
~
\tilde{\alpha}
.
Because characterization of
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
’s bias employs second-order Taylor approximations of
log
⁡
#
�
γ
\log\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}
and
log
⁡
(
1
+
#
�
γ
)
\log(1+\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}})
, the bias correction relies on the variance of
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
γ
\hfil\textstyle\gamma\hfil
, which is equal to
(
Atenafu et al., 2012
)
𝕍
​
#
�
γ
=
N
−
a
−
2
n
2
​
(
a
−
1
)
​
{
a
+
1
N
−
a
−
4
−
a
−
1
N
−
a
−
2
}
​
(
n
​
γ
+
1
)
2
.
\displaystyle\mathbb{V}\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}=\frac{N-a-2}{n^{2}(a-1)}\left\{\frac{a+1}{N-a-4}-\frac{a-1}{N-a-2}\right\}(n\gamma+1)^{2}.
One must estimate this variance since it is a function of
γ
\gamma
.
Atenafu et al., 2012
recommend the plug-in estimator that replaces
θ
=
n
​
γ
+
1
\theta=n\gamma+1
in (
5.3
) with
#
�
θ
=
n
​
#
�
γ
+
1
\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\theta\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\theta\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\theta\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\theta\hfil$\crcr}}}=n\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}+1
. Of course another possibility is to substitute
θ
~
=
M
​
S
​
A
/
M
​
S
​
E
\tilde{\theta}=MSA/MSE
for
θ
\theta
.
5.4
A bias-corrected estimator
Atenafu et al., 2012
characterized the bias of
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
α
\hfil\textstyle\alpha\hfil
and proposed two bias-corrected estimators, which I will denote as
#
�
α
bc1
\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\alpha\hfil$\crcr}}}_{\text{bc1}}
and
#
�
α
bc2
\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\alpha\hfil$\crcr}}}_{\text{bc2}}
. To reveal the bias, first write second-order Taylor approximations of
log
⁡
#
�
γ
\log\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}
and
log
⁡
(
1
+
#
�
γ
)
\log(1+\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}})
as
log
⁡
#
�
γ
≈
log
⁡
γ
+
1
γ
​
(
#
�
γ
−
γ
)
−
1
2
​
γ
2
​
(
#
�
γ
−
γ
)
2
\log\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}\approx\log\gamma+\frac{1}{\gamma}(\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}-\gamma)-\frac{1}{2\gamma^{2}}(\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}-\gamma)^{2}
and
log
⁡
(
#
�
γ
+
1
)
≈
log
⁡
(
γ
+
1
)
+
1
γ
+
1
​
(
#
�
γ
−
γ
)
−
1
2
​
(
γ
+
1
)
2
​
(
#
�
γ
−
γ
)
2
\log(\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}+1)\approx\log(\gamma+1)+\frac{1}{\gamma+1}(\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}-\gamma)-\frac{1}{2(\gamma+1)^{2}}(\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}-\gamma)^{2}
for
γ
\gamma
near
#
�
\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr
γ
\hfil\textstyle\gamma\hfil
. This implies that
𝔼
⁡
(
log
⁡
#
�
α
−
log
⁡
α
)
≈
−
1
2
​
{
1
γ
2
−
1
(
γ
+
1
)
2
}
​
𝕍
​
#
�
γ
.
\mathbb{E}(\log\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\alpha\hfil$\crcr}}}-\log\alpha)\approx-\frac{1}{2}\left\{\frac{1}{\gamma^{2}}-\frac{1}{(\gamma+1)^{2}}\right\}\mathbb{V}\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}.
Then produce a bias-corrected estimator of
log
⁡
α
\log\alpha
as
#
�
log
α
bc
=
log
⁡
#
�
α
+
1
2
​
{
1
#
�
γ
2
−
1
(
#
�
γ
+
1
)
2
}
​
𝕍
^
​
#
�
γ
.
\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\log\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\log\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\log\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\log\alpha\hfil$\crcr}}}_{\text{bc}}=\log\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\alpha\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\alpha\hfil$\crcr}}}+\frac{1}{2}\left\{\frac{1}{\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}^{\,2}}-\frac{1}{(\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}+1)^{2}}\right\}\widehat{\mathbb{V}}\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}.
Here
𝕍
^
​
#
�
γ
\widehat{\mathbb{V}}\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}
is an estimator of
𝕍
​
#
�
γ
\mathbb{V}\mathchoice{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\displaystyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\displaystyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\displaystyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\textstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\textstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\textstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptstyle\gamma\hfil$\crcr}}}{\vbox{\halign{#\cr\kern-0.7pt\cr$\mkern 2.0mu\scriptscriptstyle\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraitd}$}}{{}\hbox{$\textstyle{\montraitd}$}}{{}\hbox{$\scriptstyle{\montraitd}$}}{{}\hbox{$\scriptscriptstyle{\montraitd}$}}}\mkern-1.5mu\leaders{\hbox{$\scriptscriptstyle\mkern 0.0mu\mathrel{\mathchoice{{}\hbox{$\displaystyle{\montraita}$}}{{}\hbox{$\textstyle{\montraita}$}}{{}\hbox{$\scriptstyle{\montraita}$}}{{}\hbox{$\scriptscriptstyle{\montraita}$}}}\mkern 0.0mu$}}{\hfill}\mkern-1.5mu\fldr$\crcr\kern-0.3pt\cr$\hfil\scriptscriptstyle\gamma\hfil$\crcr}}}
. Finally, map back to the original scale to obtain
α
→
bc1
\displaystyle\vec{\alpha}_{\text{bc1}}
=
α
→
​
exp
⁡
[
1
2
​
{
1
γ
→
2
−
1
(
γ
→
+
1
)
2
}
​
𝕍
^
​
γ
→
]
.
\displaystyle=\vec{\alpha}\exp\left[\frac{1}{2}\left\{\frac{1}{\vec{\gamma}^{\,2}}-\frac{1}{(\vec{\gamma}+1)^{2}}\right\}\widehat{\mathbb{V}}\vec{\gamma}\right].
(37)
We can already see that this estimator will tend to perform poorly when agreement is low. This is because the dilation factor in (
37
) goes to
∞
\infty
as
γ
\gamma
goes to 0. When the sample size is smaller and agreement is low,
α
→
bc1
\vec{\alpha}_{\text{bc1}}
is even challenging to evaluate by simulation because the estimator can take any value in
ℝ
∪
{
−
∞
,
∞
}
\mathbb{R}\cup\{-\infty,\infty\}
and has very heavy tails. Since this estimator’s drawbacks do not vanish until the sample size is large, I will not consider
α
→
bc1
\vec{\alpha}_{\text{bc1}}
further.
5.5
A second bias-corrected estimator
Atenafu et al., 2012
noted the above mentioned deficiency of
α
→
bc1
\vec{\alpha}_{\text{bc1}}
and recommended an alternative estimator (based on Taylor expansion of
1
−
α
1-\alpha
) in the case of small
γ
\gamma
. Said alternative is given by
α
→
bc2
\displaystyle\vec{\alpha}_{\text{bc2}}
=
1
−
(
1
−
α
→
)
​
exp
⁡
{
−
1
2
​
(
γ
→
+
1
)
2
​
𝕍
^
​
γ
→
}
.
\displaystyle=1-(1-\vec{\alpha})\exp\left\{-\frac{1}{2(\vec{\gamma}+1)^{2}}\widehat{\mathbb{V}}\vec{\gamma}\right\}.
(38)
The sensible contraction factor for
α
→
bc2
\vec{\alpha}_{\text{bc2}}
allows
α
→
bc2
\vec{\alpha}_{\text{bc2}}
to perform much better than
α
→
bc1
\vec{\alpha}_{\text{bc1}}
for small values of
γ
\gamma
.
5.6
Choosing the best point estimator
I compared the five point estimators to one another by way of an extensive simulation study. Specifically, for each value of
α
\alpha
in a fine grid with step size 0.01, I simulated 1,000,000 datasets and computed each of the five estimates for each dataset. Graphical results for percent bias and mean squared error are shown in Figure
5
.
16
×
4
16\times 4
8
×
8
8\times 8
4
×
16
4\times 16
Figure 5:
Percent bias and mean squared error for the five point estimators.
The contest is clearly between the analytical estimator and the second bias-corrected estimator of
Atenafu et al., 2012
. For tall datasets, the analytical estimator performs about as well as the bias-corrected estimator for
α
\alpha
values between approximately 0.2 and 1. As
α
\alpha
descends toward 0, the analytical estimator exhibits less and less bias relative to the bias-corrected estimator. The two estimators are nearly indistinguishable with respect to mean squared error.
For the square-matrix scenario, the bias-corrected estimator exhibits less bias than the analytical estimator over nearly the entire interval, although the difference is small. And once again the estimators’ mean squared errors are close for all values of
α
\alpha
.
For the short-matrix scenario, the bias-corrected estimator offers substantially less bias than the analytical estimator. As for mean squared error, we can see a noticeable, but not too large, difference in this scenario. For small to moderate agreement the analytical estimator is more accurate. For moderate to strong agreement the bias-corrected estimator is more accurate.
In summary, the analytical estimator is better for tall data matrices, the two estimators perform comparably for square matrices, and the bias-corrected estimator is better for short matrices. Either the analytical estimator or the bias-corrected estimator is a better choice than the customary estimator, the MLE, or the analytical variant proposed by
Atenafu et al., 2012
. Of course these differences in performance disappear as the sample size grows large. For smaller sample sizes, though, making an educated choice can have a meaningful impact on the quality of inference.
6
Jackknife-based interval estimation for the analytical point estimator
Whether one chooses the analytical estimator or the bias-corrected estimator, it is desirable to obtain confidence intervals having the desired rates of coverage. Above I argued and verified by simulation that bootstrapping based on resampling the rows of the data matrix yields unacceptably low coverage rates. In this section I will develop an effective jackknife method for interval estimation that can be applied to either estimator. I will present the method for
α
~
\tilde{\alpha}
.
The jackknife variance estimator for
α
~
\tilde{\alpha}
is based on
log
⁡
(
M
​
S
​
A
/
M
​
S
​
E
)
=
log
⁡
(
θ
~
)
\log(MSA/MSE)=\log(\tilde{\theta})
because log-transforming
M
​
S
​
A
/
M
​
S
​
E
MSA/MSE
normalizes the estimator and stabilizes its variance. This permits one to compute a good-performing Student’s
t
t
-based confidence interval for
log
⁡
(
θ
)
\log(\theta)
, the endpoints of which are then transformed to the scale of
α
\alpha
using
α
=
(
θ
−
1
)
/
(
θ
+
n
−
1
)
\alpha=(\theta-1)/(\theta+n-1)
.
Let
η
=
log
⁡
(
θ
)
\eta=\log(\theta)
. Then compute
a
a
pseudovalues
η
˙
i
=
a
​
η
~
−
(
a
−
1
)
​
η
−
i
,
\dot{\eta}_{i}=a\tilde{\eta}-(a-1)\eta_{-i},
where
η
~
=
log
⁡
(
θ
~
)
\tilde{\eta}=\log(\tilde{\theta})
and
η
−
i
\eta_{-i}
is equal to the analytical estimate of
η
\eta
for the data matrix with row
i
i
left out. Then the jackknife estimator of variance is
V
jack
=
S
2
/
a
V_{\text{jack}}=S^{2}/a
, where
S
2
S^{2}
is the sample variance of the pseudovalues:
S
2
=
∑
i
=
1
a
(
η
˙
i
−
1
a
​
∑
i
=
1
a
η
˙
i
)
2
a
−
1
.
S^{2}=\frac{\sum_{i=1}^{a}(\dot{\eta}_{i}-\frac{1}{a}\sum_{i=1}^{a}\dot{\eta}_{i})^{2}}{a-1}.
The statistic
T
=
η
~
−
η
V
jack
T=\frac{\tilde{\eta}-\eta}{\sqrt{V_{\text{jack}}}}
is approximately
t
t
distributed, and so an estimated
(
1
−
δ
)
​
100
%
(1-\delta)100\%
confidence interval for
η
\eta
is given by
(
L
η
=
η
~
−
t
ν
1
−
δ
/
2
​
V
jack
,
U
η
=
η
~
+
t
ν
1
−
δ
/
2
​
V
jack
)
,
(L_{\eta}=\tilde{\eta}-t_{\nu}^{1-\delta/2}\sqrt{V_{\text{jack}}},\;U_{\eta}=\tilde{\eta}+t_{\nu}^{1-\delta/2}\sqrt{V_{\text{jack}}}),
where
t
ν
1
−
δ
/
2
t_{\nu}^{1-\delta/2}
denotes the
1
−
δ
/
2
1-\delta/2
quantile of Students’s
t
t
distribution with
ν
\nu
degrees of freedom. The corresponding interval for
α
\alpha
is
(
L
=
exp
⁡
(
L
η
)
−
1
exp
⁡
(
L
η
)
+
n
−
1
,
U
=
exp
⁡
(
U
η
)
−
1
exp
⁡
(
U
η
)
+
n
−
1
)
.
\left(L=\frac{\exp(L_{\eta})-1}{\exp(L_{\eta})+n-1},\;U=\frac{\exp(U_{\eta})-1}{\exp(U_{\eta})+n-1}\right).
Given that
S
2
S^{2}
is the sample variance for a sample of size
a
a
, one might suspect that
ν
=
a
−
1
\nu=a-1
. Alas,
ν
\nu
is complicated and so must be estimated or simply set to
a
−
1
a-1
. I investigated the double-jackknife estimation approach recommended by
Hinkley, 1977
, wherein
ν
\nu
is estimated as
ν
~
=
2
​
V
jack
2
K
,
\tilde{\nu}=\frac{2V_{\text{jack}}^{2}}{K},
where
K
=
∑
i
=
1
a
(
η
˙
−
1
a
​
∑
i
=
1
a
η
˙
i
)
4
a
⁡
(
a
−
1
)
​
(
a
−
2
)
2
−
a
​
V
jack
2
(
a
−
2
)
2
,
K=\frac{\sum_{i=1}^{a}(\dot{\eta}-\frac{1}{a}\sum_{i=1}^{a}\dot{\eta}_{i})^{4}}{a(a-1)(a-2)^{2}}-\frac{aV_{\text{jack}}^{2}}{(a-2)^{2}},
but found that using
ν
~
\tilde{\nu}
does not improve on using
a
−
1
a-1
in this setting because
ν
~
\tilde{\nu}
is too variable for smaller samples. Luckily, assuming
a
−
1
a-1
degrees of freedom yields coverage rates close to
(
1
−
δ
)
​
100
%
(1-\delta)100\%
because
ν
\nu
is approximately equal to
a
−
1
a-1
for small values of
a
a
, and then
ν
\nu
and
a
a
diverge in a complicated way as
a
a
increases.
Simulation results are shown in Figure
6
. Each panel shows coverage rates for the customary point estimator
α
^
\hat{\alpha}
with the improved bootstrap procedure described in Section
4.4
, the analytical estimator
α
~
\tilde{\alpha}
with improved bootstrap, and the analytical estimator with jackknife variance estimation. We see that the coverage rates are very close to 95% for the latter method while the first two methods yield poor coverage rates.
16
×
4
16\times 4
8
×
8
8\times 8
4
×
16
4\times 16
Figure 6:
Coverage rates of 95% intervals for the customary Krippendorff’s
α
\alpha
estimator with improved bootstrap procedure (blue, dotted), the analytical estimator with improved bootstrap procedure (green, dash-dot), the analytical estimator with jackknife variance estimation (pink, dashed).
7
Computing issues
The time complexities of the four approaches to interval estimation are given in Table
2
, where
b
b
is the bootstrap sample size,
a
a
is the number of units, and
n
n
is the number of coders. These rates are for the general, i.e., nonparametric, version of Krippendorff’s
α
\alpha
, which is arrived at by applying the identity
∑
i
=
1
m
(
x
i
−
x
¯
∙
)
2
=
1
2
​
m
​
∑
i
=
1
m
∑
j
=
1
m
(
x
i
−
x
j
)
2
\sum_{i=1}^{m}(x_{i}-\bar{x}_{\text{\raisebox{1.0pt}{\scalebox{.6}{$\bullet$}}}})^{2}=\frac{1}{2m}\sum_{i=1}^{m}\sum_{j=1}^{m}(x_{i}-x_{j})^{2}
to the usual definitions of
S
​
S
​
E
SSE
and
S
​
S
​
T
c
SST_{c}
and then allowing for other (perhaps even user-defined) distance functions in addition to squared Euclidean distance
d
2
​
(
x
i
,
x
j
)
=
(
x
i
−
x
j
)
2
d^{2}(x_{i},x_{j})=(x_{i}-x_{j})^{2}
(
Hughes, 2021a
)
.
We see that the jackknife procedure’s growth rate is cubic in
a
a
while the other procedures have quadratic running times. These fast growth rates can make analyses of larger datasets quite burdensome or even infeasible. This is a minor problem, though, since for large datasets even the customary bootstrap procedure provides high-quality inference. Still, it is desirable to carefully consider how one might speed computation of
S
​
S
​
T
c
SST_{c}
, which is
Θ
⁡
(
a
2
​
n
2
)
\Theta(a^{2}n^{2})
and must be computed
b
b
times for the improved bootstrap procedure and
a
a
times for the jackknife method.
Table 2:
Running times for the four approaches to interval estimation.
Method
Time Complexity
α
^
\hat{\alpha}
with customary bootstrap
Θ
⁡
(
a
2
​
n
2
)
\Theta(a^{2}n^{2})
α
^
\hat{\alpha}
with improved bootstrap
Θ
⁡
(
b
​
a
2
​
n
2
)
\Theta(ba^{2}n^{2})
α
~
\tilde{\alpha}
with improved bootstrap
Θ
⁡
(
b
​
a
2
​
n
2
)
\Theta(ba^{2}n^{2})
α
~
\tilde{\alpha}
with jackknife variance estimation
Θ
⁡
(
a
3
​
n
2
)
\Theta(a^{3}n^{2})
To see why computation of
S
​
S
​
T
c
SST_{c}
is onerous in the general case, consider the nonparametric version of
S
​
S
​
T
c
SST_{c}
:
S
​
S
​
T
c
=
1
2
​
a
​
n
​
∑
i
=
1
a
∑
j
=
1
n
∑
k
=
1
a
∑
l
=
1
n
d
2
​
(
Y
i
​
j
,
Y
k
​
l
)
,
SST_{c}=\frac{1}{2an}\sum_{i=1}^{a}\sum_{j=1}^{n}\sum_{k=1}^{a}\sum_{l=1}^{n}d^{2}(Y_{ij},Y_{kl}),
where
d
2
d^{2}
is the chosen distance function. Clearly, this entails computing the distance between every pair of outcomes in the dataset. This computational load can be eased considerably by storing the distances in an
a
​
n
×
a
​
n
an\times an
lookup table during the first pass over the data, and then using the lookup table to compute
(
S
​
S
​
T
c
)
k
∗
​
(
k
=
1
,
…
,
b
)
(SST_{c})_{k}^{*}\;\;(k=1,\dots,b)
for the bootstrap or
(
S
​
S
​
T
c
)
−
i
​
(
i
=
1
,
…
,
a
)
(SST_{c})_{-i}\;\;(i=1,\dots,a)
for the jackknife. Employing a lookup table can be hundreds of times faster than computing
S
​
S
​
T
c
SST_{c}
from scratch during each iteration.
8
Additional analyses of simulated data
In addition to carrying out the simulation experiments already described, I investigated by simulation the behaviors of the customary and analytical estimators when (1) the outcomes were Gaussian and the design was unbalanced (20% missing at random), (2) the outcomes were continuous but the unit effects were Student’s
t
t
distributed with four degrees of freedom, and (3) when the outcomes were categorical.
For the unbalanced Gaussian scenario and the
t
t
scenario,
α
\alpha
is still a well-defined population parameter, and so I was able to measure bias, mean squared error, and coverage rates, as above. I have omitted those results because they are quite similar to the results I presented above for Gaussian unit effects in a balanced design.
Investigating the behavior of
α
^
\hat{\alpha}
and
α
~
\tilde{\alpha}
for categorical outcomes is a rather different matter since the population parameter cannot be defined precisely. This poses two challenges. First, since
α
\alpha
does not belong to a known probability model, one must choose a probability model to serve as a sort of proxy. Second, only estimation and variance can be appraised due to the mismatch between the proxy probability model and the unknown true probability model.
A sensible proxy model from which to simulate categorical outcomes is the direct Gaussian copula model with compound symmetry dependence structure and categorical marginal distribution
(
Xue-Kun Song, 2000
;
Hughes, 2021b
)
. The generative form of this model is given by
𝒁
\displaystyle\boldsymbol{Z}
∼
Normal
​
{
𝟎
,
𝛀
⁡
(
α
)
}
\displaystyle\;\sim\;\textsc{Normal}\{\boldsymbol{0},\mathbf{\Omega}(\alpha)\}
U
i
​
j
\displaystyle U_{ij}
=
Φ
(
Z
i
​
j
)
(
i
=
1
,
…
,
a
;
j
=
1
,
…
,
n
)
\displaystyle\;=\;\Phi(Z_{ij})\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;(i=1,\dots,a;\;j=1,\dots,n)
Y
i
​
j
\displaystyle Y_{ij}
=
F
−
1
​
(
U
i
​
j
∣
𝝅
)
,
\displaystyle\;=\;F^{-1}(U_{ij}\mid\boldsymbol{\pi}),
where
𝛀
\mathbf{\Omega}
is block diagonal with each
n
×
n
n\times n
block having compound symmetry structure
𝛀
i
=
1
2
…
n
1
(
1
α
…
α
)
2
α
1
…
α
⋱
n
α
α
…
1
,
\mathbf{\Omega}_{i}=\bordermatrix{&1&2&\dots&n\cr 1&1&\alpha&\dots&\alpha\cr 2&\alpha&1&\dots&\alpha\cr\vdots&\vdots&\vdots&\ddots&\vdots\cr n&\alpha&\alpha&\dots&1},
Φ
\Phi
is the standard Gaussian cdf, and
F
−
1
(
⋅
∣
𝝅
)
F^{-1}(\cdot\mid\boldsymbol{\pi})
is the quantile function for the categorical distribution having probabilities
𝝅
=
(
π
1
,
…
,
π
p
)
′
\boldsymbol{\pi}=(\pi_{1},\dots,\pi_{p})^{\prime}
. Here
𝑼
=
(
U
11
,
…
,
U
a
​
n
)
′
\boldsymbol{U}=(U_{11},\dots,U_{an})^{\prime}
is a realization of the Gaussian copula indexed by
𝛀
\mathbf{\Omega}
, which is to say that the
U
i
​
j
U_{ij}
are marginally standard uniform and exhibit the Gaussian correlation structure defined by
𝛀
\mathbf{\Omega}
. Since
U
i
​
j
U_{ij}
is standard uniform, applying the inverse probability integral transform to
U
i
​
j
U_{ij}
in the final stage produces outcome
Y
i
​
j
Y_{ij}
having the desired categorical marginal distribution
F
(
⋅
∣
𝝅
)
F(\cdot\mid\boldsymbol{\pi})
.
I chose
p
=
3
p=3
and
𝝅
=
(
0.5
,
0.2
,
0.3
)
′
\boldsymbol{\pi}=(0.5,0.2,0.3)^{\prime}
(a challenging scenario), and once again used a fine grid of
α
\alpha
values. Results are shown in Figure
7
, where results for the Gaussian scenario are included for comparison. We see that the relative behaviors of the two estimators are broadly similar for nominal data and Gaussian data, which suggests that my proposed methodology may substantially improve upon the customary methodology for all kinds of data.
16
×
4
16\times 4
8
×
8
8\times 8
4
×
16
4\times 16
Categorical
Gaussian
Categorical
Gaussian
Figure 7:
Estimation and variance of the customary and analytical estimators, for categorical outcomes.
9
Application to experimentally observed data
9.1
Re-analysis of Krippendorff’s categorical data
Re-analysis of Krippendorff’s nominal data using my proposed methodology yielded
α
~
=
0.756
\tilde{\alpha}=0.756
and
α
∈
(
0.228
,
0.951
)
\alpha\in(0.228,0.951)
. Leaving out row 6 gives
α
~
=
0.866
\tilde{\alpha}=0.866
and
α
∈
(
0.370
,
0.981
)
\alpha\in(0.370,0.981)
. All results for this dataset are collected in Table
3
.
Each width ratio is the ratio of the length of the jackknife interval to the length of the customary bootstrap interval. We see that the jackknife intervals are much wider than the bootstrap intervals, as expected.
The execution times in Table
3
(as well as in Table
5
and Table
6
) were obtained on a 3.6 GHz 10-core Intel Core i9 CPU, with both interval estimation methods parallelized over eight cores, and a bootstrap sample size of 2,000 for the customary procedure.
Estimate
95% Confidence Interval
Width Ratio
Execution Time
α
^
=
0.743
\hat{\alpha}=0.743
α
∈
(
0.459
,
1.000
)
\alpha\in(0.459,1.000)
1.34
<
1
<1
s
α
~
=
0.756
\tilde{\alpha}=0.756
α
∈
(
0.228
,
0.951
)
\alpha\in(0.228,0.951)
2 s
α
^
−
6
=
0.857
\hat{\alpha}_{-6}=0.857
α
∈
(
0.679
,
1.000
)
\alpha\in(0.679,1.000)
1.90
<
1
<1
s
α
~
−
6
=
0.866
\tilde{\alpha}_{-6}=0.866
α
∈
(
0.370
,
0.981
)
\alpha\in(0.370,0.981)
2 s
Table 3:
Results from applying the customary and improved methodologies to Krippendorff’s nominal data.
9.2
Analyses of CDH data
The data for this example, some of which are shown in Figure
8
, are liver-herniation scores (in
{
1
,
…
,
5
}
\{1,\dots,5\}
) assigned by two coders (radiologists) to magnetic resonance images (MRI) of the liver in a study pertaining to congenital diaphragmatic hernia (CDH)
(
Longoni et al., 2020
)
, in which a hole in the diaphragm permits abdominal organs to enter the chest. The five grades are described in Table
4
.
u
1
u_{1}
u
2
u_{2}
u
3
u_{3}
u
4
u_{4}
u
5
u_{5}
…
\dots
u
43
u_{43}
u
44
u_{44}
u
45
u_{45}
u
46
u_{46}
u
47
u_{47}
c
11
c_{11}
2
4
4
4
4
…
\dots
2
1
2
1
1
c
12
c_{12}
2
4
5
4
4
…
\dots
2
1
2
1
1
c
21
c_{21}
3
5
5
5
4
…
\dots
2
2
2
1
1
c
22
c_{22}
3
5
5
4
4
…
\dots
2
2
2
1
1
Figure 8:
Ordinal scores for MR images of the liver. Each coder scored each unit twice.
Grade
Description
1
No herniation of liver into the fetal chest
2
Less than half of the ipsilateral thorax is occupied by the fetal liver
3
Greater than half of the thorax is occupied by the fetal liver
4
The liver dome reaches the thoracic apex
5
The liver dome not only reaches the thoracic apex but also extends
across the thoracic midline
Table 4:
Liver herniation grades for the CDH study.
Each coder scored each of the 47 images twice, and so we are interested in assessing both intra-coder and inter-coder agreement. The results are shown in Table
5
. We see that both intra-coder and inter-coder agreement are very nearly perfect. The jackknife interval widths are once again substantially wider than the bootstrap intervals because the jackknife approach properly accounts for uncertainty. And the running times are comparable for the two methods because the dataset is on the small side.
Estimate
95% Confidence Interval
Width Ratio
Execution Time
Radiologist 1
α
^
=
0.979
\hat{\alpha}=0.979
α
∈
(
0.950
,
1.000
)
\alpha\in(0.950,1.000)
1.42
2 s
α
~
=
0.979
\tilde{\alpha}=0.979
α
∈
(
0.923
,
0.994
)
\alpha\in(0.923,0.994)
2 s
Radiologist 2
α
^
=
0.987
\hat{\alpha}=0.987
α
∈
(
0.968
,
1.000
)
\alpha\in(0.968,1.000)
2.56
2 s
α
~
=
0.987
\tilde{\alpha}=0.987
α
∈
(
0.916
,
0.998
)
\alpha\in(0.916,0.998)
2 s
Both
α
^
=
0.965
\hat{\alpha}=0.965
α
∈
(
0.944
,
0.984
)
\alpha\in(0.944,0.984)
1.25
2 s
α
~
=
0.966
\tilde{\alpha}=0.966
α
∈
(
0.933
,
0.983
)
\alpha\in(0.933,0.983)
2 s
Table 5:
Results from applying the customary and improved methodologies to the liver data.
9.3
Analyses of PM
2.5
data
I created the PM
2.5
dataset from data collected during 2021 by the EPA (
https://tinyurl.com/2p93czeh
) via seven monitors in or near Philadelphia, Pennsylvania (see Figure
9
). Specifically, the data matrix comprises exactly 365 rows, one row for each day of 2021. The row corresponding to a given day comprises that day’s mean PM
2.5
concentrations (in micrograms per cubic meter) for the seven monitors. An image plot of the dataset is shown in Figure
10
. We see extensive missingness for monitors 2 and 3, yet the dataset is large (1,937 measurements) and dense (76%). The horizontal streaking in the image plot suggests that an analysis of these data will reveal considerable spatial agreement among the seven monitors.
Figure 9:
The locations of the seven air quality monitors that generated the PM
2.5
data. I used the EPA’s interactive map to create this image.
Figure 10:
The 2021 PM
2.5
data for Philadelphia, PA.
My analysis yielded the results shown in Table
6
. Since this dataset is quite large, it is not surprising that the customary method and my proposed method produced nearly identical results. (Although the jackknife interval is 31% wider than the bootstrap interval, both intervals are narrow.) Nor is it surprising that the execution times were six seconds and nearly two minutes, respectively: for a dataset so large, the cubic time complexity of the jackknife procedure begins to show itself conspicuously. In this respect it is fortunate that the customary methodology yields high-quality inference for large datasets.
Estimate
95% Confidence Interval
Width Ratio
Execution Time
α
^
=
0.859
\hat{\alpha}=0.859
α
∈
(
0.841
,
0.875
)
\alpha\in(0.841,0.875)
1.31
6 s
α
~
=
0.859
\tilde{\alpha}=0.859
α
∈
(
0.835
,
0.880
)
\alpha\in(0.835,0.880)
1 min 53 s
Table 6:
Results from applying the customary and improved methodologies to the Philadelphia PM
2.5
data.
These results suggest that a single air quality monitor may suffice for the study region, which could save taxpayer dollars that are currently being spent to purchase, install, and maintain the monitors. Perhaps further analyses of this sort for other cities would lead to similar conclusions and possibly more savings. And one can imagine how these and similar data could be used to measure agreement patterns not only for a whole year but also within a given year (by season, for example) or across years.
10
Discussion
In this article I revealed inferential challenges faced by the customary methodology for Krippendorff’s
α
\alpha
agreement measure. Specifically, the customary point estimator is biased downward, and the bias increases in magnitude rather substantially as the number of coders increases. The customary procedure for interval estimation is also wanting, typically yielding unacceptably low coverage rates for smaller samples.
I then investigated a number of candidate point estimators, and ultimately chose the so called analytical estimator owing to that estimator’s bias and mean squared error profiles. I employed the analytical estimator to develop a jackknife approach to interval estimation. Although potentially burdensome computationally, the jackknife procedure produces confidence intervals having very nearly the nominal coverage rates.
In the final section of the paper I compared and contrasted the customary methodology and my proposed methodology as applied to three experimentally observed datasets. The first dataset was previously analyzed by Krippendorff. The latter two datasets—which pertain to an imaging study in congenital diaphragmatic hernia and the spatial pattern of PM
2.5
concentrations in and near Philadelphia, Pennsylvania—represent novel applications of Krippendorff’s
α
\alpha
.
Author contributions
John Hughes conceived the project, performed all simulations and data analyses, created the PM
2.5
dataset, and wrote the manuscript.
Acknowledgments
I thank Hyunok Choi for helpful discussions regarding air quality monitoring.
References
Artstein and Poesio,  (2008)
Artstein, R. and Poesio, M. (2008).
Inter-coder agreement for computational linguistics.
Computational Linguistics
, 34(4):555–596.
Atenafu et al.,  (2012)
Atenafu, E. G., Hamid, J. S., To, T., Willan, A. R., M Feldman, B., and Beyene,
J. (2012).
Bias-corrected estimator for intraclass correlation coefficient in
the balanced one-way random effects model.
BMC Medical Research Methodology
, 12(1):126.
Banerjee et al.,  (1999)
Banerjee, M., Capozzoli, M., McSweeney, L., and Sinha, D. (1999).
Beyond kappa: A review of interrater agreement measures.
Canadian Journal of Statistics
, 27(1):3–23.
Bennett et al.,  (1954)
Bennett, E. M., Alpert, R., and Goldstein, A. C. (1954).
Communications through limited-response questioning.
Public Opinion Quarterly
, 18(3):303–308.
Cicchetti and Feinstein,  (1990)
Cicchetti, D. V. and Feinstein, A. R. (1990).
High agreement but low kappa: II. resolving the paradoxes.
Journal of Clinical Epidemiology
, 43(6):551–558.
Cohen,  (1960)
Cohen, J. (1960).
A coefficient of agreement for nominal scales.
Educational and Psychological Measurement
, 20(1):37–46.
Cohen,  (1968)
Cohen, J. (1968).
Weighed kappa: Nominal scale agreement with provision for scaled
disagreement or partial credit.
Psychological Bulletin
, 70(4):213–220.
Conger,  (1980)
Conger, A. J. (1980).
Integration and generalization of kappas for multiple raters.
Psychological Bulletin
, 88(2):322.
Davies and Fleiss,  (1982)
Davies, M. and Fleiss, J. L. (1982).
Measuring agreement for multinomial data.
Biometrics
, pages 1047–1051.
Efron,  (1982)
Efron, B. (1982).
The Jackknife, the Bootstrap and Other Resampling Plans
.
Society for Industrial and Applied Mathematics.
Feinstein and Cicchetti,  (1990)
Feinstein, A. R. and Cicchetti, D. V. (1990).
High agreement but low kappa: I. the problems of two paradoxes.
Journal of Clinical Epidemiology
, 43(6):543–549.
Fleiss,  (1971)
Fleiss, J. L. (1971).
Measuring nominal scale agreement among many raters.
Psychological Bulletin
, 76(5):378.
Gwet,  (2008)
Gwet, K. L. (2008).
Computing inter-rater reliability and its variance in the presence of
high agreement.
British Journal of Mathematical and Statistical Psychology
,
61(1):29–48.
Gwet,  (2014)
Gwet, K. L. (2014).
Handbook of Inter-Rater Reliability: The Definitive Guide to
Measuring the Extent of Agreement Among Raters
.
Advanced Analytics, LLC, Gaithersburg, MD, 4th edition.
Hayes and Krippendorff,  (2007)
Hayes, A. F. and Krippendorff, K. (2007).
Answering the call for a standard reliability measure for coding
data.
Communication Methods and Measures
, 1(1):77–89.
Hinkley,  (1977)
Hinkley, D. (1977).
Jackknife confidence limits using Student t approximations.
Biometrika
, 64(1):21–28.
(17)
Hughes, J. (2021a).
krippendorffsalpha: An R package for measuring agreement using
Krippendorff’s Alpha coefficient.
The R Journal
, 13(1):413–425.
(18)
Hughes, J. (2021b).
On the occasional exactness of the distributional transform
approximation for direct Gaussian copula models with discrete margins.
Statistics & Probability Letters
, 177:109159.
Hughes,  (2022)
Hughes, J. (2022).
Sklar’s Omega: A Gaussian copula-based framework for assessing
agreement.
Statistics and Computing
, 32(3):46.
Krippendorff,  (2013)
Krippendorff, K. (2013).
Computing Krippendorff’s alpha-reliability.
Technical report, University of Pennsylvania.
Krippendorff,  (2016)
Krippendorff, K. (2016).
Bootstrapping distributions for Krippendorff’s Alpha.
Technical report, University of Pennsylvania.
Landis and Koch,  (1977)
Landis, J. R. and Koch, G. G. (1977).
The measurement of observer agreement for categorical data.
Biometrics
, pages 159–174.
Longoni et al.,  (2020)
Longoni, M., Pober, B. R., and High, F. A. (2020).
Congenital diaphragmatic hernia overview.
GeneReviews®[Internet]
.
Mielke and Berry,  (2007)
Mielke, P. W. and Berry, K. J. (2007).
Permutation Methods: A Distance Function Approach
.
Springer Series in Statistics. Springer, New York, 2nd edition.
Ravishanker et al.,  (2021)
Ravishanker, N., Chi, Z., and Dey, D. K. (2021).
A First Course in Linear Model Theory
.
Chapman and Hall/CRC.
Scott,  (1955)
Scott, W. A. (1955).
Reliability of content analysis: The case of nominal scale coding.
Public Opinion Quarterly
, 19:321–325.
Smeeton,  (1985)
Smeeton, N. C. (1985).
Early history of the kappa statistic.
Biometrics
, 41(3):795–795.
Taber,  (2018)
Taber, K. S. (2018).
The use of Cronbach’s alpha when developing and reporting research
instruments in science education.
Research in Science Education
, 48(6):1273–1296.
Warne and Burningham,  (2019)
Warne, R. T. and Burningham, C. (2019).
Spearman’s g found in 31 non-Western nations: Strong evidence
that g is a universal phenomenon.
Psychological Bulletin
, 145(3):237.
Xue-Kun Song,  (2000)
Xue-Kun Song, P. (2000).
Multivariate dispersion models generated from Gaussian copula.
Scandinavian Journal of Statistics
, 27(2):305–320.
◄
Feeling
lucky?
Conversion
report
Report
an issue
View original
on arXiv
►