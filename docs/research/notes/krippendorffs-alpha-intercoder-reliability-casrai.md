---
title: 'Krippendorff''s Alpha: Intercoder Reliability — CASRAI'
id: krippendorffs-alpha-intercoder-reliability-casrai
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:47:57.728371Z'
source: https://casrai.org/guides/krippendorffs-alpha
source_domain: casrai.org
fetched_at: '2026-09-15T02:47:57.726433Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Krippendorff's Alpha: Intercoder Reliability — CASRAI
Skip to main content
Guide
Research Methods & Statistics
Krippendorff’s Alpha: Calculating Intercoder Reliability
The observed-vs-expected disagreement formula, a worked example with missing data across three coders, Krippendorff’s own 0.667/0.800 benchmarks, a bootstrap confidence-interval method, and software (R, Python, SPSS/SAS/Stata, ReCal).
Written and maintained by
CASRAI Editorial Board
Last updated
29 August 2026
X
LinkedIn
Facebook
Copy link
On this page:
the observed-vs-expected disagreement formula behind Krippendorff’s alpha; how the difference function changes for nominal, ordinal, interval and ratio data; a fully worked example with three coders and one missing rating; why alpha handles that missing cell without deleting the whole unit; getting a confidence interval by bootstrapping; and where to actually compute it.
Krippendorff’s alpha (α) is a chance-corrected intercoder-reliability coefficient built to do three things Cohen’s kappa cannot: accept
any number of coders
, accept a rating matrix with
missing data
instead of forcing listwise deletion, and apply to
any level of measurement
— nominal, ordinal, interval or ratio — using one consistent formula. This page assumes you already know you want alpha rather than kappa, Fleiss’ kappa or an ICC, and goes straight to how to actually compute it and interpret the result. For the full decision between coefficients — including exactly when alpha is the right call over kappa — see CASRAI’s guide to
choosing an inter-rater reliability coefficient
; this page deliberately doesn’t repeat that selection logic.
The formula: agreement built from disagreement
Unlike kappa, which is built from
agreement
, alpha is built from
disagreement
and then flipped:
α = 1 − (D
o
/ D
e
)
where D
o
is the observed disagreement among coders and D
e
is the disagreement expected if coders assigned categories at random, given the actual distribution of categories used. α = 1 means perfect agreement; α = 0 means agreement no better than chance; negative values mean coders disagreed more than chance would predict, usually a sign of a coding-scheme or training problem.
Both quantities are computed from a
coincidence matrix
rather than directly from the raw rating matrix. For every unit with two or more coded values, every ordered pair of those values is added to the matrix with weight 1/(m
u
− 1), where m
u
is the number of coders who rated that unit. That weighting is what makes the whole system work with a variable number of ratings per unit: a unit two coders rated contributes exactly as much total weight to the matrix as a unit five coders rated, just distributed across fewer pairs. A unit only one coder reached, or that nobody reached, contributes nothing — it is dropped automatically rather than forcing the rest of that coder’s work to be discarded, which is exactly what listwise deletion does under Cohen’s or Fleiss’ kappa.
Once the coincidence matrix is built, observed disagreement sums the off-diagonal cells weighted by a
difference function
δ², and expected disagreement does the same using the matrix’s category marginals instead of the cell counts themselves — the “what would disagreement look like if these same category totals were paired up at random” quantity.
The difference function is what makes alpha work across data types
Everything above is generic. The one thing that changes by level of measurement is δ², and swapping it is the entire mechanism that lets one formula span all four data types:
Level of measurement
Difference function δ²(c,k)
What it does
Nominal
0 if c = k, else 1
Any disagreement counts the same — there is no notion of “close.”
Ordinal
Based on the cumulative frequency of categories between c and k
A disagreement spanning several ranks counts for more than an adjacent-category disagreement, without assuming the ranks are evenly spaced.
Interval
(c − k)²
Squared numeric distance — the same penalty shape as quadratic weighted kappa or an ICC.
Ratio
((c − k) / (c + k))²
Squared
relative
distance, appropriate when zero is a true zero and the scale has no fixed unit.
This is also why alpha is the default in mixed-methods and multi-variable coding projects: a single reliability run can apply the nominal function to a theme code, the interval function to a numeric rating, and the ordinal function to a severity scale, each computed correctly, rather than requiring a different coefficient and a different assumption for every variable.
Worked example: three coders, missing data, nominal categories
The illustration below uses hypothetical data — six units coded “yes”/”no” by up to three coders, with one coder missing one unit — chosen because the arithmetic is checkable by hand and small enough to show every step. It is not drawn from any real study.
Unit
Coder A
Coder B
Coder C
1
Yes
Yes
Yes
2
Yes
Yes
No
3
No
No
No
4
Yes
No
— not coded —
5
No
No
No
6
Yes
Yes
Yes
Step 1 — count pairable values.
Units 1, 2, 3, 5 and 6 have three coders each (m
u
= 3); unit 4 has two (m
u
= 2), since coder C never reached it. Total pairable values n = 3+3+3+2+3+3 = 17. Unit 4 is not dropped — it still contributes its one pairable comparison between coders A and B, at full weight 1/(2−1) = 1 instead of the 1/(3−1) = 0.5 a three-coder unit uses.
Step 2 — build the coincidence matrix.
Working through each unit’s ordered coder pairs at the weight above and summing gives:
Yes
No
Row total
Yes
7
2
9
No
2
6
8
The matrix is symmetric by construction, and its row/column totals (9 “yes”, 8 “no”) match a direct count of every value in the table — a useful sanity check on any real coincidence matrix you build by hand or in software.
Step 3 — observed and expected disagreement.
Nominal δ² is 1 for every off-diagonal cell, so:
D
o
= (1/n) × (o
Yes,No
+ o
No,Yes
) = (1/17) × (2 + 2) = 4/17 ≈ 0.235
D
e
= (1/(n(n−1))) × (n
Yes
·n
No
+ n
No
·n
Yes
) = (1/(17×16)) × (9×8 + 8×9) = 144/272 = 9/17 ≈ 0.529
Step 4 — alpha.
α = 1 − D
o
/D
e
= 1 − (4/17)/(9/17) = 1 − 4/9 = 5/9 ≈
0.556
.
By Krippendorff’s own benchmarks (below), 0.556 falls short of even the tentative-conclusions band — a realistic outcome for a six-unit toy example, and a reminder that alpha, like every reliability coefficient, needs a real sample size before the number means anything.
Reading the number
Krippendorff’s own convention, distinct from and stricter than the Landis & Koch kappa bands: rely on data at α ≥ 0.800; draw only tentative conclusions for α between 0.667 and 0.800; discard data below 0.667. These remain conventions rather than derived thresholds, but Krippendorff states the rationale explicitly — the 0.667 floor is where he judges the risk of drawing a wrong substantive conclusion from the coded data becomes unacceptable for exploratory work, and 0.800 is what he considers the bar for high-stakes use. Set your own threshold in the coding protocol before you look at the result, and report the confidence interval alongside the point estimate (see below) — a single decimal without an interval overstates the precision small reliability samples actually support.
Getting a confidence interval: bootstrap it
Alpha has no simple closed-form standard error once the rating matrix has missing data or a variable number of coders per unit, which is the normal case in real coding projects. The standard solution, following Hayes and Krippendorff’s own recommendation, is a nonparametric bootstrap:
Resample units, not individual ratings, with replacement
from your original set of
N
units, drawing a new sample of size
N
each time. Resampling whole units keeps each unit’s own pattern of missingness and its full set of coder values intact, which is what preserves the reliability data’s actual structure rather than inventing ratings that were never made.
Rebuild the coincidence matrix and recompute alpha
on the resampled set.
Repeat
, typically 2,000–10,000 times.
Take the 2.5th and 97.5th percentiles
of the resulting distribution of alpha values as the 95% confidence interval. If the bootstrap distribution is noticeably skewed, a bias-corrected-and-accelerated (BCa) interval is preferable to the plain percentile method.
Report the interval, not just the point estimate — an α of 0.71 with a bootstrap CI of 0.58–0.84 straddles both Krippendorff’s bands, which is a materially different finding than 0.71 with a CI of 0.68–0.74.
Computing it without doing the arithmetic by hand
R
— the
irr
package’s
kripp.alpha()
function computes alpha directly from a coders-by-units matrix, with a
method
argument for
"nominal"
,
"ordinal"
,
"interval"
or
"ratio"
; missing cells are simply left
NA
in the input matrix.
Python
— the
krippendorff
package on PyPI implements the same coincidence-matrix algorithm and accepts the same four difference-function options.
SPSS, SAS and Stata
— none of the three has a built-in alpha command; Hayes and Krippendorff’s own
KALPHA
macro (published alongside the coefficient’s standard reference paper) is the standard way to compute it in any of the three, and includes bootstrap confidence intervals as a built-in option.
ReCal
— a free browser-based reliability calculator, widely used in content-analysis coursework, that reports alpha alongside Cohen’s/Fleiss’ kappa and percent agreement from a pasted or uploaded rating matrix, without requiring any of the above installed.
Whichever tool you use, confirm which difference function it applied and how it treated missing cells before trusting the output — the defaults are not identical across packages, and a silently wrong level of measurement produces a plausible-looking but incorrect number.
What to report
The
coefficient and the difference function used
— “Krippendorff’s alpha (nominal)”, not “alpha” alone.
The
point estimate and a bootstrapped 95% confidence interval
.
The
number of coders, whether the same coders rated every unit, and how much of the rating matrix was missing
— alpha tolerates missingness, but a reader still needs to know how much there was.
The
total number of units and pairable values
(
n
in the formula above), since a high alpha on very few units carries little weight.
The
threshold you pre-specified
, ideally Krippendorff’s own 0.667/0.800 bands stated as the convention they are, or a study-specific bar justified by what the coded data will be used for.
The
software and version
used to compute it.
The
reliability reporting checklist (GRRAS)
referenced on CASRAI’s coefficient-selection guide applies to alpha exactly as it does to kappa and the ICC.
Krippendorff’s alpha vs. Cronbach’s alpha
The shared name is a source of real confusion and the two measure entirely different things. Krippendorff’s alpha is an
intercoder reliability
statistic — whether independent coders assign the same category or score to the same unit.
Cronbach’s alpha
is an
internal consistency
statistic — whether the items of a multi-item scale, answered by a single respondent in one sitting, correlate with each other. A study can report a high Cronbach’s alpha for its survey instrument and a low Krippendorff’s alpha for the coders who scored open-ended responses to that same survey; the two numbers answer unrelated questions and neither substitutes for the other.
Frequently asked questions
Do I need to remove units with missing coder ratings before computing alpha?
No — this is the coefficient’s central practical advantage over Cohen’s or Fleiss’ kappa. A unit with at least two coded values contributes to the coincidence matrix automatically, weighted by how many coders actually reached it. Only a unit with zero or one coded value is excluded, because a single rating produces no pair to compare.
Can I use Krippendorff’s alpha with only two coders and no missing data?
Yes. In that special case alpha and Cohen’s kappa are computed from the same underlying agreement information and will generally track closely, though they are not numerically identical because their expected-disagreement terms are built differently. There is no reason not to use alpha in the two-coder, complete-data case; the reverse — using kappa once you have three coders or missing data — is where the real limitation is.
What sample size do I need for a stable alpha?
There is no single rule; it depends on the number of categories, how skewed their prevalence is, and the width of confidence interval your use case can tolerate. Because alpha has no simple closed-form standard error, the practical way to check stability is to run the bootstrap above and look at how wide the resulting interval actually is, rather than relying on a fixed rule of thumb for the number of units to double-code.
Why is my alpha lower than the percent agreement looks like it should produce?
Chance correction. Like kappa, alpha subtracts out the disagreement rate coders would produce by chance given the categories’ actual prevalence, so a coding scheme where one category dominates will pull alpha down relative to raw agreement — the same underlying phenomenon documented for kappa’s prevalence paradox. Reporting the coincidence-matrix marginals alongside alpha lets a reader see whether that is what happened.
Is Krippendorff’s alpha always the better choice over Cohen’s kappa?
No — it is the better choice specifically when you have more than two coders, an incomplete rating matrix, or want one coefficient applied consistently across variables measured at different levels. If you have exactly two coders, a complete matrix, and nominal or ordinal data, Cohen’s or weighted kappa is the more widely recognised reporting convention in most fields and is a reasonable default. See CASRAI’s full
coefficient-selection guide
for the complete decision logic.
This guide sits in CASRAI’s
research methods
cluster. For the coding workflow alpha typically supports, see
content analysis
and
coding qualitative interview data
; for the underlying measurement-theory background, see
reliability in research measurement
and
levels of measurement
.
Follow CASRAI
Research-administration guidance, standards updates and independent tool reviews.
LinkedIn
X
Instagram
Facebook
Ask CASRAI · free to try
Ask about Krippendorff’s Alpha: Calculating Intercoder Reliability
Ask your first
2
questions free below. Subscribers get
150
a day for $
29
a month.
Ask CASRAI answers research-administration questions and cites the passages behind every claim. When our sources don't cover a question, it says so.
Answers draw on CASRAI's guides and dictionary plus the federal and funder documents we index: Federal Register, Grants.gov, Regulations.gov and UKRI.
Works on this site and inside
Claude, Cursor and the AI tools you already use
.
Ask your first question free
Subscribe — $
29
/month
See what it covers →
Already subscribed? Sign in
Everything CASRAI publishes — this page, the dictionary, the guides and the news — stays free to read, with no account and no card.
Referenced across the research world
View CASRAI adoption →