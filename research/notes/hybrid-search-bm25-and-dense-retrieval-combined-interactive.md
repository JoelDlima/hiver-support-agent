---
title: 'Hybrid Search: BM25 and Dense Retrieval Combined - Interactive'
id: hybrid-search-bm25-and-dense-retrieval-combined-interactive
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:28:15.303026Z'
source: https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion
source_domain: mbrenndoerfer.com
fetched_at: '2026-09-15T02:28:15.296027Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

Hybrid Search: BM25 and Dense Retrieval Combined - Interactive
Back
Hybrid Search: BM25 and Dense Retrieval Combined
Back
Michael Brenndoerfer
·
Published:
January 29, 2026
January 29, 2026
·
65
min read
Part of
Language AI Handbook
Language AI Handbook
Machine Learning
Software Engineering
Hybrid search combines BM25 keyword ranking with dense vector retrieval. Covers reciprocal rank fusion, weighted scores, recall, and tuning tradeoffs.
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
Hybrid Search: BM25 and Dense Retrieval Combined
Link Copied
When you type a
query
into a search system, two fundamentally different engines could be working to find your answer. The first is a classical keyword matcher: it looks for documents that contain the exact words you typed, using statistical signals like
term frequency
to
rank
results. The second is a semantic engine: it converts your
query
and every document into dense vectors, then finds documents whose meaning is closest to yours, even if they share no words in common. Both approaches have real strengths, and both have real weaknesses.
Hybrid search
combines them.
The insight behind
hybrid search
is simple but powerful: keyword matching and semantic retrieval fail in complementary ways. A keyword system finds the document containing "myocardial infarction" when you search for "heart attack" only if someone mapped those synonyms in advance. A semantic system finds semantically related documents but can miss the one where a specific product code like "AB-1042-X" appears verbatim. Neither system alone is reliable. Together, they cover each other's blind spots.
Think of the two systems as two specialists working the same library. The first specialist has memorized the exact text of every document and can instantly point you to any document containing your precise phrase. The second specialist has deeply internalized the meaning of every document and can point you to conceptually related material even when no shared vocabulary exists. Asking both specialists independently, then combining their recommendations, consistently produces better results than relying on either alone.
This complementarity is not accidental. It shows a deep asymmetry in what the two systems learn. Keyword systems learn statistics over the literal surface form of text: which strings appear, how often, and in which documents. Semantic systems learn geometry: how to map meaning into a high-dimensional space so that similar meanings end up nearby. These are orthogonal views of the same text, and
relevance
is a combination of both. A document that addresses your
query
's exact phrasing is often relevant. A document that addresses your
query
's underlying concept is also often relevant. A document that does both is very likely the best answer.
Hybrid retrieval
finds all three types.
This chapter explains how to build hybrid retrieval systems. We will examine
BM25
, the classical
ranking
function that anchors the keyword half, and
dense retrieval
, the
vector
-based approach that gives the semantic half. We will then study the two main
fusion
strategies:
reciprocal rank fusion
, which combines ranked lists without needing to understand the underlying scores, and
weighted score combination
, which blends the scores directly. Throughout, we ground the math in intuition and the intuition in working code.
As we saw in the chapter on
Dense Retrieval
and
Embedding Models
,
dense retrieval
converts documents and queries into high-dimensional vectors using models like bi-encoders trained with contrastive objectives. As we saw in
Vector Similarity
Search and the
HNSW
and
IVF
Index chapters, those vectors can be searched efficiently at scale using
approximate nearest neighbor
indices. This chapter builds directly on that foundation, adding the classical retrieval side and then fusing the two into a single, more powerful system. In the next chapter on
Reranking
, we will add another stage that takes the
hybrid retrieval
output and re-scores it with a heavier
cross-encoder
model.
BM25: The Classical Baseline
Link Copied
Before
dense retrieval
existed, keyword-based
ranking
functions dominated information retrieval. The most durable of these is
BM25
(Best Match 25), which dates to the 1990s and remains competitive against many modern systems on keyword-heavy benchmarks. Its staying power is not an accident of inertia:
BM25
embodies a set of principled statistical insights about how term occurrence patterns relate to
relevance
, and those insights remain valid even in the age of large language models.
BM25
is a refinement of
TF-IDF
.
Recall
from earlier chapters that
TF-IDF
scores a term in a document by multiplying how often the term appears in the document (
term frequency
, or TF) by how rare the term is across all documents (
inverse document frequency
, or
IDF
).
BM25
keeps this core intuition but fixes two structural problems with raw
TF-IDF
. The fixes are not cosmetic adjustments: they address basic failure modes that make raw
TF-IDF
unreliable in practice. Understanding these failure modes is the fastest path to understanding why
BM25
is designed the way it is.
Think of
BM25
as a more careful accountant than
TF-IDF
.
TF-IDF
is like an accountant who counts every dollar of evidence and adds it all up, even if the same dollar appears a hundred times.
BM25
is like an accountant who correctly recognizes that after the tenth dollar of the same type, each additional dollar is worth only a fraction of the first. It also adjusts for the fact that longer reports naturally contain more dollars, and corrects for that structural bias. The result is a much fairer assessment of which documents truly contain the most relevant evidence.
Historical Context
BM25
emerged from the Okapi research project at City University London in the early 1990s, led by Stephen Robertson and colleagues. The name "Best Match 25" shows that it was the 25th iteration of a best-match weighting formula developed through systematic empirical testing on the TREC (Text Retrieval Conference) benchmark collections. The series began with simpler
TF-IDF
variants and evolved through progressively refined models that addressed observed failure modes. The core
BM25
formula was described in Robertson et al. (1994) and Robertson and Walker (1994), with the version commonly used today sometimes called
BM25
Okapi or BM25F (the F variant incorporating structural document fields). Despite its age,
BM25
remains a competitive baseline on many modern information retrieval benchmarks, including BEIR, and is the keyword retrieval component in most production search systems, including Elasticsearch and Apache Solr.
The Two Problems BM25 Solves
Link Copied
The first problem is that raw TF grows without bound. If a document mentions the word "python" 100 times rather than 10 times, raw TF scores it 10 times higher. But in practice the
relevance
gain from the 50th mention of "python" is negligible compared to the gain from the first.
BM25
saturates TF so that each additional occurrence contributes less than the previous one.
To make this concrete, imagine reading a book review. If the review mentions "fascinating" once, that tells you something. If it mentions "fascinating" twenty times, that tells you roughly the same thing, just more emphatically. The hundredth mention of "fascinating" adds no new information.
BM25
captures this diminishing return mathematically: the scoring function curves upward steeply at first, then flattens to a ceiling as occurrences accumulate. The ceiling is determined by the hyperparameter
k
1
k_1
, which you will see shortly.
The second problem is that longer documents naturally accumulate more term occurrences and therefore score higher even when they are no more relevant. A textbook chapter is longer than a blog post and will contain any given term more often, but that does not make the textbook chapter more relevant to a two-word
query
.
BM25
applies a document
length normalization
that penalizes documents longer than average, keeping the playing field level. The strength of this penalty is controlled by the hyperparameter
b
b
.
These two fixes, saturation and
length normalization
, are not independent adjustments bolted onto
TF-IDF
. They interact through a single elegant fraction at the heart of the
BM25 formula
. Understanding that fraction is the key to understanding the entire formula.
The BM25 Formula
Link Copied
BM25
computes a
relevance
score for a document
d
d
given a
query
Q
Q
by summing term-level contributions. Each term's contribution multiplies a document-frequency weight (
IDF
) by a saturated term-frequency weight. For a
query
Q
Q
with terms
q
1
,
q
2
,
…
,
q
n
q_1, q_2, \ldots, q_n
and a document
d
d
,
BM25
scores the document as:
BM25
(
d
,
Q
)
=
∑
i
=
1
n
IDF
(
q
i
)
⋅
f
(
q
i
,
d
)
⋅
(
k
1
+
1
)
f
(
q
i
,
d
)
+
k
1
⋅
(
1
−
b
+
b
⋅
∣
d
∣
avgdl
)
\text{BM25}(d, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, d) \cdot (k_1 + 1)}{f(q_i, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}
where:
q
1
,
q
2
,
…
,
q
n
q_1, q_2, \ldots, q_n
: the individual terms in
query
Q
Q
f
(
q
i
,
d
)
f(q_i, d)
: the raw frequency of term
q
i
q_i
in document
d
d
(how many times it appears)
∣
d
∣
|d|
: the length of document
d
d
in tokens
avgdl
\text{avgdl}
: the average document length across the entire
corpus
k
1
k_1
: the
term frequency
saturation parameter, typically set to 1.2 or 1.5; it controls how quickly additional occurrences of a term stop adding to the score
b
b
: the
length normalization
parameter, typically set to 0.75; it controls how strongly longer documents are penalized relative to the average
It is worth pausing to appreciate the structure of this formula before looking at any of its parts in isolation. The outer sum iterates over every
query
term. For each term, you compute two independent quantities: how rare the term is across the entire
corpus
(the
IDF
factor on the left), and how heavily the term appears in this specific document adjusted for document length (the fraction on the right). These two numbers are multiplied together, and you accumulate the result across all
query
terms. The final
BM25
score for a document is therefore a weighted sum of term-level evidence, where rarer terms contribute more heavily.
This structure shows a clear intuitive principle. A
query
like "
transformer
" combined with "myocardial" should give high weight to the term "myocardial" (rare) and lower weight to "transformer" (common in this hypothetical
corpus
).
BM25
accomplishes this weighting automatically through
IDF
, without any manual synonym mapping or domain knowledge.
The
IDF
component measures how rare a term is across the
corpus
. Rare terms that appear in few documents receive high
IDF
weights, while common terms like "the" receive near-zero weights. The
IDF
term is computed as:
IDF
(
q
i
)
=
log
⁡
(
N
−
n
(
q
i
)
+
0.5
n
(
q
i
)
+
0.5
+
1
)
\text{IDF}(q_i) = \log\left(\frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1\right)
where:
N
N
: the total number of documents in the
corpus
n
(
q
i
)
n(q_i)
: the number of documents in the
corpus
that contain term
q
i
q_i
0.5
0.5
: a
smoothing
constant added to both numerator and denominator to avoid division by zero and to prevent
IDF
from going negative for terms appearing in every document
The
+
1
+1
inside the logarithm ensures the
IDF
is always non-negative, even when a term appears in all documents
To build intuition for this formula, consider the two extreme cases. When
n
(
q
i
)
n(q_i)
is very small relative to
N
N
, meaning the term appears in almost no documents, the fraction
N
−
n
(
q
i
)
+
0.5
n
(
q
i
)
+
0.5
\frac{N - n(q_i) + 0.5}{n(q_i) + 0.5}
becomes large, and the logarithm returns a large positive number. This makes sense: a term that appears in only 3 out of 1 million documents is extraordinarily informative when it does appear. When
n
(
q
i
)
≈
N
n(q_i) \approx N
, meaning the term appears in nearly every document, the numerator approaches 0.5 and the denominator approaches
N
+
0.5
N + 0.5
, making the fraction nearly zero and the
IDF
close to
log
⁡
(
1
)
=
0
\log(1) = 0
. A term that appears in every document tells you nothing about which documents are more relevant.
Understanding the Saturation Term
Link Copied
The fraction within the
BM25
sum handles two effects simultaneously: TF saturation and
length normalization
. These two effects are coupled through a single expression, and understanding their interaction reveals why
BM25
is so reliable across diverse corpora. Focusing on this fraction:
f
(
q
i
,
d
)
⋅
(
k
1
+
1
)
f
(
q
i
,
d
)
+
k
1
⋅
(
1
−
b
+
b
⋅
∣
d
∣
avgdl
)
\frac{f(q_i, d) \cdot (k_1 + 1)}{f(q_i, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}
This fraction looks intimidating at first glance, but it has a clean structure once you name its moving parts. The numerator scales the
raw term frequency
by
(
k
1
+
1
)
(k_1 + 1)
, which is a constant for any given setting of
k
1
k_1
. The denominator adds the raw
term frequency
to a document-length-dependent constant. That constant is where the two effects live.
Define the denominator's length-dependent constant as:
K
=
k
1
⋅
(
1
−
b
+
b
⋅
∣
d
∣
avgdl
)
K = k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)
where:
k
1
k_1
and
b
b
are the
BM25
hyperparameters defined above
∣
d
∣
/
avgdl
|d| / \text{avgdl}
: the ratio of document length to average document length; values above 1.0 mean the document is longer than average
Notice what
K
K
encodes. The term
b
⋅
(
∣
d
∣
/
avgdl
)
b \cdot (|d| / \text{avgdl})
grows as the document grows relative to the average. When
b
=
0.75
b = 0.75
and a document is twice the average length, the ratio is 2.0, and this term contributes
0.75
×
2.0
=
1.5
0.75 \times 2.0 = 1.5
to the expression inside the outer parentheses. When a document is exactly average length, the ratio is 1.0, and the expression inside the parentheses equals
(
1
−
b
+
b
×
1
)
=
1
(1 - b + b \times 1) = 1
exactly. So
K
K
equals
k
1
k_1
for an average-length document and grows proportionally for longer documents. This is the
length normalization
embedded in
K
K
.
With this substitution, the saturation fraction becomes:
f
⋅
(
k
1
+
1
)
f
+
K
\frac{f \cdot (k_1 + 1)}{f + K}
This is now recognizable as a hyperbolic function of
f
f
(the
term frequency
). To understand the saturation behavior, consider what happens as
term frequency
grows:
As
f
→
∞
f \to \infty
, the fraction approaches
k
1
+
1
k_1 + 1
, not infinity. This is the saturation ceiling: no matter how many times a term appears, the contribution is bounded above by
k
1
+
1
k_1 + 1
.
When
f
=
K
f = K
, the fraction equals
(
k
1
+
1
)
/
2
(k_1 + 1) / 2
, exactly half the maximum. This means
K
K
controls the "
half-saturation point
": the
term frequency
at which the score reaches half its ceiling.
K
K
itself depends on document length via
∣
d
∣
/
avgdl
|d| / \text{avgdl}
. Longer documents have a larger
K
K
, meaning they need more term occurrences to reach the same score as a shorter document. This is the
length normalization
effect.
The interplay between saturation and
length normalization
is elegant: a document that is twice as long as average must also have roughly twice the
term frequency
to reach the same
BM25
score as the shorter document. This keeps the scoring fair across documents of different lengths.
The key insight is that
BM25
treats the saturation ceiling and the
half-saturation point
as linked quantities: both are controlled by the same
K
K
expression. When you tune
k
1
k_1
and
b
b
, you are not adjusting two independent knobs. You are adjusting a single parameterized family of scoring functions where the saturation speed and the length sensitivity move together in a coordinated way. This coupling is what makes
BM25
well-behaved across diverse corpora with different length distributions.
The coupling between saturation and
length normalization
through
K
K
makes
BM25
a unified formula rather than two separate adjustments patched together. When you increase
b
b
, you make
K
K
more sensitive to document length, which simultaneously raises the
half-saturation point
for longer documents. When you increase
k
1
k_1
, you raise both the saturation ceiling and the scale of
K
K
, effectively making the saturation happen more slowly everywhere. The two hyperparameters interact in a predictable way.
Out
[
3
]:
Visualization
BM25 term frequency saturation curves for three values of k1, with a document at average length (b=0.75). Each curve shows how the TF contribution to the BM25 score grows with raw term frequency before flattening at a ceiling. Higher k1 raises the saturation ceiling and shifts the half-saturation point rightward, meaning more term occurrences are needed before the score stops rising.
The visualization makes the saturation property concrete. With
k
1
=
0.5
k_1 = 0.5
(bottom curve), the score saturates almost immediately: going from 1 occurrence to 5 occurrences barely moves the score. With
k
1
=
2.0
k_1 = 2.0
(top curve), the score continues growing through 10 or more occurrences, giving more credit to documents with many term repetitions. The default
k
1
=
1.2
k_1 = 1.2
sits between these extremes, saturating moderately and making each of the first few occurrences count while capping the contribution of very high frequencies.
Out
[
4
]:
Visualization
BM25 IDF weight as a function of document frequency (the number of documents containing a query term), for a corpus of 10,000 documents. Terms appearing in very few documents receive high IDF weights; terms appearing in most documents receive weights near zero. This automatic weighting ensures that rare, discriminating terms dominate BM25 scoring.
The logarithmic x-axis reveals the full range of
IDF
behavior. A term appearing in 10 out of 10,000 documents (0.1% of the
corpus
) receives an
IDF
of roughly 6.9, while a term appearing in 9,000 documents (90% of the
corpus
) receives an
IDF
near zero. This nonlinear weighting means that going from "appears in 10 documents" to "appears in 100 documents" causes a significant
IDF
drop, while going from "appears in 5,000 to 9,000 documents" causes almost no change because both are already near zero.
BM25
is most sensitive to term rarity at the rare end of the spectrum.
A Worked Numerical Example
Link Copied
To make the
BM25
formula completely concrete, let us trace through all computations step by step on a tiny
corpus
. This kind of worked example is invaluable because the formula combines several interacting quantities, and watching them interact numerically builds intuition that the formula alone cannot convey.
Consider a tiny
corpus
with three documents:
d
1
d_1
: "the cat sat on the mat" (6 tokens)
d
2
d_2
: "the cat sat on the cat mat mat cat" (9 tokens)
d
3
d_3
: "the dog chased the cat across the yard" (8 tokens)
Average document length:
(
6
+
9
+
8
)
/
3
=
7.67
(6 + 9 + 8) / 3 = 7.67
tokens.
Query
: "cat mat"
Step 1: Compute
IDF
for each query term.
For term "cat": appears in all 3 documents, so
n
(
cat
)
=
3
n(\text{cat}) = 3
,
N
=
3
N = 3
.
IDF
(
cat
)
=
log
⁡
(
3
−
3
+
0.5
3
+
0.5
+
1
)
=
log
⁡
(
0.5
3.5
+
1
)
=
log
⁡
(
1.143
)
≈
0.134
\text{IDF}(\text{cat}) = \log\left(\frac{3 - 3 + 0.5}{3 + 0.5} + 1\right) = \log\left(\frac{0.5}{3.5} + 1\right) = \log(1.143) \approx 0.134
Since "cat" appears in every document, its
IDF
is very low. This shows that it is not a discriminating term for this
query
. Every document contains "cat," so knowing a document contains "cat" tells you almost nothing about which document is most relevant. The
IDF
correctly suppresses its influence.
For term "mat": appears in
d
1
d_1
and
d
2
d_2
, so
n
(
mat
)
=
2
n(\text{mat}) = 2
.
IDF
(
mat
)
=
log
⁡
(
3
−
2
+
0.5
2
+
0.5
+
1
)
=
log
⁡
(
1.5
2.5
+
1
)
=
log
⁡
(
1.6
)
≈
0.470
\text{IDF}(\text{mat}) = \log\left(\frac{3 - 2 + 0.5}{2 + 0.5} + 1\right) = \log\left(\frac{1.5}{2.5} + 1\right) = \log(1.6) \approx 0.470
"mat" is rarer (absent from
d
3
d_3
), so it receives a higher
IDF
weight. This makes sense: knowing a document contains "mat" is more informative than knowing it contains "cat," because "mat" narrows the field.
Step 2: Compute the length-dependent constant
K
K
for
d
2
d_2
.
Using
k
1
=
1.2
k_1 = 1.2
,
b
=
0.75
b = 0.75
,
∣
d
2
∣
=
9
|d_2| = 9
,
avgdl
=
7.67
\text{avgdl} = 7.67
:
K
d
2
=
1.2
⋅
(
1
−
0.75
+
0.75
⋅
9
7.67
)
=
1.2
⋅
(
0.25
+
0.881
)
=
1.2
⋅
1.131
=
1.357
K_{d_2} = 1.2 \cdot \left(1 - 0.75 + 0.75 \cdot \frac{9}{7.67}\right) = 1.2 \cdot (0.25 + 0.881) = 1.2 \cdot 1.131 = 1.357
The ratio
9
/
7.67
=
1.174
9 / 7.67 = 1.174
tells us
d
2
d_2
is about 17% longer than average. The constant
K
d
2
=
1.357
K_{d_2} = 1.357
is larger than it would be for an average-length document (where
K
K
would equal
k
1
⋅
1.0
=
1.2
k_1 \cdot 1.0 = 1.2
). This larger
K
K
raises the half-saturation threshold, meaning
d
2
d_2
needs more term occurrences to reach the same score as an average-length document.
Step 3: Compute TF contributions for "cat" in
d
2
d_2
and
d
1
d_1
.
TF contribution of "cat" in
d
2
d_2
(frequency = 3):
3
⋅
(
1.2
+
1
)
3
+
1.357
=
6.6
4.357
≈
1.515
\frac{3 \cdot (1.2 + 1)}{3 + 1.357} = \frac{6.6}{4.357} \approx 1.515
For
d
1
d_1
:
K
d
1
=
1.2
⋅
(
1
−
0.75
+
0.75
⋅
6
/
7.67
)
=
1.2
⋅
(
0.25
+
0.587
)
=
0.934
K_{d_1} = 1.2 \cdot (1 - 0.75 + 0.75 \cdot 6/7.67) = 1.2 \cdot (0.25 + 0.587) = 0.934
.
TF contribution of "cat" in
d
1
d_1
(frequency = 1):
1
⋅
2.2
1
+
0.934
=
2.2
1.934
≈
1.138
\frac{1 \cdot 2.2}{1 + 0.934} = \frac{2.2}{1.934} \approx 1.138
Step 4: Assemble the full
BM25
scores.
For
d
1
d_1
(cat: f=1, mat: f=1):
BM25
(
d
1
,
Q
)
=
IDF
(
cat
)
⋅
1.138
+
IDF
(
mat
)
⋅
1
⋅
2.2
1
+
0.934
\text{BM25}(d_1, Q) = \text{IDF}(\text{cat}) \cdot 1.138 + \text{IDF}(\text{mat}) \cdot \frac{1 \cdot 2.2}{1 + 0.934}
=
0.134
⋅
1.138
+
0.470
⋅
1.138
=
0.152
+
0.535
=
0.687
= 0.134 \cdot 1.138 + 0.470 \cdot 1.138 = 0.152 + 0.535 = 0.687
For
d
2
d_2
(cat: f=3, mat: f=2), first computing the mat TF contribution:
TF_contrib
(
mat
,
d
2
)
=
2
⋅
2.2
2
+
1.357
=
4.4
3.357
≈
1.311
\text{TF\_contrib}(\text{mat}, d_2) = \frac{2 \cdot 2.2}{2 + 1.357} = \frac{4.4}{3.357} \approx 1.311
BM25
(
d
2
,
Q
)
=
0.134
⋅
1.515
+
0.470
⋅
1.311
=
0.203
+
0.616
=
0.819
\text{BM25}(d_2, Q) = 0.134 \cdot 1.515 + 0.470 \cdot 1.311 = 0.203 + 0.616 = 0.819
For
d
3
d_3
(cat: f=1, mat: f=0),
K
d
3
=
1.2
⋅
(
0.25
+
0.75
⋅
8
/
7.67
)
=
1.2
⋅
1.032
=
1.238
K_{d_3} = 1.2 \cdot (0.25 + 0.75 \cdot 8/7.67) = 1.2 \cdot 1.032 = 1.238
:
BM25
(
d
3
,
Q
)
=
0.134
⋅
1
⋅
2.2
1
+
1.238
+
0.470
⋅
0
=
0.134
⋅
0.983
=
0.132
\text{BM25}(d_3, Q) = 0.134 \cdot \frac{1 \cdot 2.2}{1 + 1.238} + 0.470 \cdot 0 = 0.134 \cdot 0.983 = 0.132
The final
ranking
is
d
2
>
d
1
>
d
3
d_2 > d_1 > d_3
, which matches our intuition perfectly.
d
2
d_2
contains "cat" three times and "mat" twice in a document only slightly longer than average.
d
1
d_1
contains both terms once each.
d
3
d_3
contains "cat" but no "mat" at all. The
BM25
formula has automatically combined
term frequency
evidence, rarity evidence, and document length adjustment into a single, principled score.
d
2
d_2
gets a higher TF score for "cat" despite its longer length, because its
term frequency
(3) is much higher than
d
1
d_1
's (1). The
length penalty
embodied in
K
K
slows but does not stop the gain from additional occurrences. The "mat" term, being rarer (
IDF
= 0.470 vs. 0.134 for "cat"), contributes more per occurrence to the final score than "cat" does. This automatic rarity weighting is
BM25
's key advantage over simple term counting.
Out
[
5
]:
Visualization
Effect of the length normalization parameter b on BM25 TF contribution for documents of different lengths, with term frequency fixed at f=3 and k1=1.2. Each curve is a different document length ratio relative to the corpus average. Higher b values penalize longer documents more strongly, compressing their TF contribution toward that of average-length documents. At b=0 (left edge), document length has no effect and all curves converge.
This plot makes the
length normalization
effect visible. At
b
=
0
b = 0
(no
length normalization
), all four document lengths receive the same TF contribution score: length is completely ignored. As
b
b
increases toward 1.0, the curves spread apart. Documents shorter than average (length ratio 0.5) receive a bonus: their TF contributions rise. Documents longer than average (length ratio 2.0) are penalized: their TF contributions fall. At the default
b
=
0.75
b = 0.75
(dashed vertical line), the curves are moderately separated, applying a partial correction for length without fully leveling the field.
Dense Retrieval: The Semantic Half
Link Copied
Dense retrieval
is a fundamentally different theory of
relevance
than keyword matching. Rather than asking which documents contain the same tokens as the
query
,
dense retrieval
asks which documents occupy the same region of a high-dimensional semantic space as the
query
. This move from
token
space to semantic space is what lets
dense retrieval
to find relevant documents that share no words with the
query
. But it also means the system depends entirely on the quality of the
embedding model
and can fail in predictable ways when that model's training distribution does not include the
query
's vocabulary.
As covered in depth in the
Dense Retrieval
and
Embedding
Models chapters,
dense retrieval
is both queries and documents as dense vectors in a shared
embedding
space, then retrieves documents whose vectors are nearest to the
query vector
. The key insight motivating this approach is that meaning can be encoded as position in a high-dimensional space: two pieces of text that mean similar things should occupy nearby positions, regardless of whether they share any words.
Think of
dense retrieval
as operating in a space where every possible meaning corresponds to a direction. Texts about "cardiac events" and texts about "heart attacks" both point in roughly the same direction in that space, because the model has learned from context that these phrases appear in the same semantic environments. Two documents that both discuss database indexing strategies also point in similar directions, even if one uses "B-tree" and the other uses "balanced tree search structure." The
embedding model
has captured a large web of these semantic associations and compressed it into the geometry of the
embedding
space.
This is fundamentally different from what
BM25
does.
BM25
operates on the surface form of text, counting occurrences of the literal tokens that appear in a
query
.
Dense retrieval
operates on a learned representation of meaning, where the model has internalized patterns from millions or billions of training examples and uses those patterns to place semantically similar texts near each other in the
embedding
space. The two approaches are looking at entirely different aspects of the text-retrieval relationship, which is exactly why combining them is so powerful.
A
bi-encoder
model encodes the
query
q
q
and each document
d
d
independently into fixed-length
vector
representations:
q
=
Encoder
Q
(
q
)
,
d
=
Encoder
D
(
d
)
\mathbf{q} = \text{Encoder}_Q(q), \quad \mathbf{d} = \text{Encoder}_D(d)
where:
q
∈
R
m
\mathbf{q} \in \mathbb{R}^m
: the dense
query
embedding
, a
vector
of
m
m
real-valued dimensions
d
∈
R
m
\mathbf{d} \in \mathbb{R}^m
: the dense document
embedding
in the same
m
m
-dimensional space
Encoder
Q
\text{Encoder}_Q
and
Encoder
D
\text{Encoder}_D
:
transformer
-based encoders (often the same shared model) that map text to vectors
The term "
bi-encoder
" refers to the architecture's property of encoding the
query
and the document through the same (or similarly structured) encoder independently, as opposed to a
cross-encoder
, which concatenates the
query
and document before encoding them jointly. The independence of encoding is necessary for practical retrieval: it means document
embeddings
can be computed once, stored offline, and then queried at inference time using only a single
query
encoding. This is what makes
dense retrieval
feasible at scale.
Retrieval ranks documents by
cosine similarity
between the
query
and document embeddings:
score
(
q
,
d
)
=
q
⋅
d
∣
q
∣
∣
d
∣
\text{score}(q, d) = \frac{\mathbf{q} \cdot \mathbf{d}}{|\mathbf{q}||\mathbf{d}|}
where:
q
⋅
d
\mathbf{q} \cdot \mathbf{d}
: the dot product of the
query
and document
embedding
vectors, summing the products of corresponding dimensions
∣
q
∣
|\mathbf{q}|
and
∣
d
∣
|\mathbf{d}|
: the Euclidean norms (lengths) of the
query
and
document vectors
The result is bounded in
[
−
1
,
1
]
[-1, 1]
, with 1 meaning the vectors point in the same direction (maximum similarity) and 0 meaning they are orthogonal (no similarity)
The geometric interpretation of
cosine similarity
is worth dwelling on. Two vectors with
cosine similarity
near 1 point in approximately the same direction in the
embedding
space, regardless of how long each
vector
is. This direction-focus is what makes
cosine similarity
appropriate for comparing embeddings: the direction encodes the meaning, while the magnitude can vary with factors like
token
count or encoding
normalization
.
In practice, most
bi-encoder
systems normalize
embeddings
to unit length during encoding, which makes
∣
q
∣
=
∣
d
∣
=
1
|\mathbf{q}| = |\mathbf{d}| = 1
and reduces
cosine similarity
to a simple dot product:
score
(
q
,
d
)
=
q
⋅
d
\text{score}(q, d) = \mathbf{q} \cdot \mathbf{d}
. This
normalization
has a practical benefit beyond mathematical simplicity: it means retrieval becomes a matrix-
vector
multiplication, which can be batched and parallelized efficiently on modern hardware. When the entire
corpus
embedding
matrix is pre-normalized, a single matrix-
vector
product gives you
cosine similarity
scores for all documents simultaneously.
Dense retrieval
has a clear strength and a clear weakness relative to
BM25
:
Semantic generalization.
If the model was trained on pairs where "heart attack" and "myocardial infarction" appear in semantically equivalent contexts, it will embed them near each other, and a
query
for one will retrieve documents about the other.
Lexical precision.
Dense models can miss exact matches for rare proper nouns, product codes, or technical identifiers that appear infrequently in training data. The model has not learned a reliable representation for "AB-1042-X" because it has almost never seen it.
BM25
, by contrast, will find every document containing that exact string regardless of training data.
This complementary failure pattern is the foundational motivation for
hybrid search
. It is not that one system is better than the other in some absolute sense. It is that they are better in different regimes, and those regimes can be exploited jointly.
Why Hybrid Search Works
Link Copied
The core empirical finding across dozens of retrieval benchmarks is that
BM25
and
dense retrieval
have complementary
recall
. Documents missed by
BM25
are often found by
dense retrieval
, and vice versa. When you combine the two,
recall
at depth K (the fraction of relevant documents appearing in the
top K
results) increases substantially over either system alone. This is not a theoretical claim: it has been validated repeatedly on the BEIR
benchmark
, the MS MARCO dataset, and numerous domain-specific retrieval evaluations.
To understand why this complementarity is so consistent, it helps to think about what each system is optimized for.
BM25
is optimized for exact lexical evidence: it finds documents that share the surface tokens of the
query
.
Dense retrieval
is optimized for semantic similarity: it finds documents whose meaning aligns with the
query
's meaning. These objectives differ. A document about "cardiac arrest management" contains the semantic content relevant to a
query
about "heart attack treatment" but almost none of the lexical tokens. A document containing a product serial number "QX-7721" contains the lexical tokens relevant to that
query
but no semantic relationship to any nearby concept. The systems see different aspects of
relevance
.
The key insight is that neither system is a noisy version of the other. If
BM25
's failures were just random errors and
dense retrieval
's failures were also random errors, combining them might help slightly by averaging out noise. But the failures are systematic and complementary:
BM25
consistently fails on semantic queries and dense consistently fails on lexical queries. This systematic pattern means that every document in
BM25
's failure set is a candidate for
dense retrieval
's success set, and vice versa. The two failure modes partition the
query
space, and together the two systems cover the entire partition.
More precisely:
Dense retrieval
excels at semantic paraphrase queries, synonym-heavy queries, and
cross-lingual
queries
BM25
excels at queries containing rare terms, entity names, technical codes, and queries where exact string matching matters
Neither dominates consistently across all
query
types
Hybrid search
is not about one system helping the other. It is about both systems searching independently, then intelligently combining their separate ranked lists or scores into a single, more complete result. Think of it like two independent experts reviewing the same
corpus
. Expert A (
BM25
) has a photographic memory for exact words and can instantly identify any document containing a specific phrase. Expert B (
dense retrieval
) has a deep understanding of meaning and can identify documents that address the same concept even when worded completely differently. Neither expert is redundant. The combined recommendation of both experts, when appropriately weighted, will be more complete than either recommendation alone.
Out
[
6
]:
Visualization
Recall decomposition for a lexical query (exact product code). BM25 retrieves the majority of relevant documents on its own, while dense retrieval adds only a small fraction. Hybrid search captures documents found by either system.
Recall decomposition for a semantic query (paraphrase with no keyword overlap). Dense retrieval dominates, recovering most relevant documents, while BM25 alone finds very few. Hybrid search combines both pools of retrieved documents.
The chart confirms the complementarity argument visually. For lexical queries (exact product codes, rare identifiers),
BM25
retrieves 70% of relevant documents on its own while
dense retrieval
alone captures only 5%. For semantic queries (paraphrases, synonym-based questions), the situation reverses:
dense retrieval
captures 70% and
BM25
alone captures only 5%. The "Both systems" bar is documents that either system would have found.
Hybrid search
captures the union of the
BM25
-only and dense-only bars in addition to the overlap, making the combined
recall
the sum of all three columns.
Fusion Strategies
Link Copied
Given two ranked lists from
BM25
and a
dense retriever
, there are two main ways to combine them:
reciprocal rank fusion
, which treats both lists as ordinal rankings without using raw scores, and
weighted score combination
, which directly blends the numeric scores. Each has real tradeoffs, and the choice between them has practical consequences for both performance and operational simplicity.
The challenge of
fusion
is more subtle than it first appears. The two retrieval systems return results on completely different scales:
BM25
scores are unbounded sums of
IDF
-weighted term frequencies, while cosine similarities are bounded in
[
−
1
,
1
]
[-1, 1]
. A
BM25
score of 12.0 and a
cosine similarity
of 0.85 are not comparable quantities. Any
fusion
method must either normalize these scores onto a common scale or abandon the raw scores entirely and work only with the
rank
orderings.
The choice between these strategies is not purely technical. It shows a deeper question about what information you trust. Do you trust the relative ordering of documents more than the absolute magnitude of their scores? Then RRF is your approach. Do you trust that the score magnitudes, after appropriate
normalization
, carry real information about how much better one document is than another? Then weighted combination may serve you better. Understanding this distinction will help you make better decisions when deploying
hybrid search
in practice.
Think of the
fusion
problem as analogous to combining votes from two juries that use different scoring systems. One jury rates cases on a 0-100 scale, the other on a letter grade scale. If you want to combine their verdicts, you have two choices: convert everything to a common scale and average the numbers, or simply note each jury's
ranking
and combine those ordinal positions. Both approaches work, but they make different assumptions about how real the raw scores are compared to the
rank
orderings. RRF takes the latter approach; weighted combination takes the former.
Reciprocal Rank Fusion (RRF)
Link Copied
Reciprocal rank fusion
was introduced by Cormack, Clarke, and Buettcher in 2009. It avoids a basic practical problem:
BM25
scores and
cosine similarity
scores live on completely different numerical scales and cannot be directly added or averaged.
BM25
scores might range from 0 to 15 for a given
query
; cosine similarities might range from 0.7 to 0.95. Adding them raw would let the
BM25
system dominate.
To see why this is a problem concretely, imagine a
query
where
BM25
scores are [12.3, 8.7, 6.1, 4.2, 2.0] for its top five documents, and cosine similarities are [0.91, 0.89, 0.87, 0.85, 0.83] for the
dense retriever
's top five. If you add these raw, the
BM25
values (which are an order of magnitude larger) would completely swamp the dense values. The combined
ranking
would be in effect identical to the
BM25
ranking
alone. You would have built an expensive two-system pipeline that behaves like a one-system pipeline.
RRF sidesteps this by converting both ranked lists to
rank
-based scores. The key idea is to replace each document's raw score with a value derived solely from its
rank
position. For a document
d
d
appearing at
rank
r
r
in retrieval system
s
s
, its RRF score contribution from that system is:
RRF
(
d
,
s
)
=
1
k
+
r
s
(
d
)
\text{RRF}(d, s) = \frac{1}{k + r_s(d)}
where:
r
s
(
d
)
r_s(d)
: the
rank
position of document
d
d
in system
s
s
's ranked list (
rank
1 is highest)
k
k
: a
smoothing
constant, typically set to 60, that prevents the very highest-ranked documents from receiving disproportionately large scores relative to lower-ranked documents
This formula is elegant in its simplicity. Every document gets a score that depends only on its position in the list, not on the magnitude of the score that produced that position. A document ranked first by
BM25
gets
1
/
(
60
+
1
)
≈
0.016
1/(60+1) \approx 0.016
regardless of whether its
BM25
score was 15.0 or 0.3. The score scale information is deliberately discarded, and only ordinal position is retained.
The final RRF score for document
d
d
across all
n
n
retrieval systems accumulates contributions from every system:
RRF_score
(
d
)
=
∑
s
=
1
n
1
k
+
r
s
(
d
)
\text{RRF\_score}(d) = \sum_{s=1}^{n} \frac{1}{k + r_s(d)}
where:
The sum runs over all retrieval systems
s
=
1
,
…
,
n
s = 1, \ldots, n
(in
hybrid search
, typically
n
=
2
n = 2
:
BM25
and dense)
Documents not appearing in a system's ranked list contribute 0 from that system (they are simply omitted)
Documents appearing high in multiple lists accumulate the largest RRF scores, rewarding consensus across systems
The accumulation structure embodies a clear principle: a document that appears in the top 5 of both systems is more likely to be relevant than a document that appears first in one system and not at all in the other. RRF rewards documents for which both experts agree, and penalizes documents that only one expert endorses. This consensus-seeking property makes RRF naturally reliable: it is hard for a single misbehaving retrieval system to dominate the combined
ranking
.
Why k = 60?
Link Copied
The constant
k
=
60
k = 60
was found empirically to work well across many retrieval benchmarks. It controls the shape of the
rank
-score curve. Substituting specific
rank
values with
k
=
60
k = 60
:
Rank
1 gives score
1
/
61
≈
0.0164
1/61 \approx 0.0164
Rank
10 gives score
1
/
70
≈
0.0143
1/70 \approx 0.0143
Rank
60 gives score
1
/
120
≈
0.0083
1/120 \approx 0.0083
Rank
1000 gives score
1
/
1060
≈
0.00094
1/1060 \approx 0.00094
The gap between
rank
1 and
rank
10 is small: 0.0164 vs 0.0143, a ratio of roughly 1.15. This is intentional. RRF gives credit to many documents, including those below the very top ranks, which helps with diverse
query
types. Smaller values of
k
k
would amplify the difference between
rank
1 and
rank
10, making the
fusion
more aggressive in favoring top-ranked documents.
To build intuition for the role of
k
k
, consider what happens at the extreme values. If
k
=
0
k = 0
, the score for
rank
1 is
1
/
1
=
1.0
1/1 = 1.0
and for
rank
2 it is
1
/
2
=
0.5
1/2 = 0.5
, a 2x gap. For
rank
10 it is
1
/
10
=
0.1
1/10 = 0.1
, a 10x gap from first place. The first-ranked document would dominate heavily. At
k
=
1000
k = 1000
, the scores at ranks 1 through 10 would be nearly identical, hovering around
1
/
1001
1/1001
through
1
/
1010
1/1010
. The
ranking
would be insensitive to
rank
differences in the top 10. The default
k
=
60
k = 60
sits in a practical middle ground: sensitive enough to reward top-ranked documents appropriately, but not so aggressive that a single lucky top placement completely overrides everything else.
A Worked RRF Example
Link Copied
Suppose
BM25
returns
[
d
3
,
d
1
,
d
5
,
d
2
,
d
7
]
[d_3, d_1, d_5, d_2, d_7]
and the
dense retriever
returns
[
d
1
,
d
5
,
d
2
,
d
4
,
d
3
]
[d_1, d_5, d_2, d_4, d_3]
.
With
k
=
60
k = 60
:
RRF score computation for six documents across BM25 and
dense retrieval
, with k=60. Documents appearing in both ranked lists accumulate contributions from both systems.
Document
BM25 Rank
Dense Rank
BM25 Score
Dense Score
RRF Total
d
1
d_1
2
1
1/62 = 0.01613
1/61 = 0.01639
0.03252
d
3
d_3
1
5
1/61 = 0.01639
1/65 = 0.01538
0.03177
d
5
d_5
3
2
1/63 = 0.01587
1/62 = 0.01613
0.03200
d
2
d_2
4
3
1/64 = 0.01563
1/63 = 0.01587
0.03150
d
4
d_4
---
4
0
1/64 = 0.01563
0.01563
d
7
d_7
5
---
1/65 = 0.01538
0
0.01538
Final order:
d
1
,
d
5
,
d
3
,
d
2
,
d
4
,
d
7
d_1, d_5, d_3, d_2, d_4, d_7
Notice that
d
3
d_3
was
BM25
's top result but placed 5th in
dense retrieval
. It falls to third overall because
d
5
d_5
ranked well in both systems.
d
4
d_4
appeared only in the dense list and scores lower than all documents with dual coverage. RRF rewards consensus across systems.
This example also illustrates what RRF does to documents that appear in only one list. Document
d
4
d_4
ranked 4th in the dense list, which is a respectable position, but it was absent from
BM25
entirely. Document
d
7
d_7
ranked 5th in
BM25
but was absent from the dense list. Both receive only single-system credit, which is less than the credit received by any document appearing in both lists. Even
d
2
d_2
, which ranked 4th in
BM25
and 3rd in dense (not particularly impressive positions in either), receives more total credit than
d
4
d_4
or
d
7
d_7
because it appears in both lists. This
consensus preference
is the defining property of RRF.
The key insight from this worked example is that RRF does not care about the magnitude of the underlying
BM25
or dense scores. Whether
d
3
d_3
had a
BM25
score of 15.0 or 1.5, it gets exactly the same RRF contribution:
1
/
61
1/61
. This scale-invariance is what makes RRF the safe default for
hybrid search
: you never need to worry about one retrieval system's scores dominating because of scale differences, and you never need to estimate
normalization
parameters from data.
Weighted Score Combination
Link Copied
The alternative to RRF is to blend the actual scores directly. This requires that both systems return scores on comparable scales, which usually means normalizing them first. Weighted combination is more expressive than RRF: it lets you say that document A ranked higher than document B and by how much. When the score differences carry real information (a
cosine similarity
of 0.95 really is substantially better than 0.70), weighted combination can use that information in ways that RRF cannot.
A common approach is
min-max normalization
applied per
query
. For each retrieval system, we rescale its raw scores to lie in the range
[
0
,
1
]
[0, 1]
by subtracting the minimum observed score and dividing by the observed score range:
s
^
BM25
(
d
)
=
s
BM25
(
d
)
−
min
⁡
j
s
BM25
(
d
j
)
max
⁡
j
s
BM25
(
d
j
)
−
min
⁡
j
s
BM25
(
d
j
)
\hat{s}_\text{BM25}(d) = \frac{s_\text{BM25}(d) - \min_j s_\text{BM25}(d_j)}{\max_j s_\text{BM25}(d_j) - \min_j s_\text{BM25}(d_j)}
where:
s
BM25
(
d
)
s_\text{BM25}(d)
: the raw
BM25
score for document
d
d
min
⁡
j
s
BM25
(
d
j
)
\min_j s_\text{BM25}(d_j)
: the minimum
BM25
score across all retrieved documents
d
j
d_j
max
⁡
j
s
BM25
(
d
j
)
\max_j s_\text{BM25}(d_j)
: the maximum
BM25
score across all retrieved documents
d
j
d_j
The resulting
s
^
BM25
(
d
)
∈
[
0
,
1
]
\hat{s}_\text{BM25}(d) \in [0, 1]
, with 0 for the lowest-scoring document and 1 for the highest
This
normalization
is linear, which means it preserves the relative gaps between scores. If one document scored twice as high as another in raw
BM25
, it will still score twice as high after
normalization
(assuming the minimum score is 0). It also brings scores from different systems onto the same scale, making direct combination possible.
The same
normalization
is applied to the dense scores:
s
^
dense
(
d
)
∈
[
0
,
1
]
\hat{s}_\text{dense}(d) \in [0, 1]
. After normalizing both
BM25
and dense scores to
[
0
,
1
]
[0, 1]
, the combined score is a weighted sum:
hybrid
(
d
)
=
α
⋅
s
^
dense
(
d
)
+
(
1
−
α
)
⋅
s
^
BM25
(
d
)
\text{hybrid}(d) = \alpha \cdot \hat{s}_\text{dense}(d) + (1 - \alpha) \cdot \hat{s}_\text{BM25}(d)
where:
α
∈
[
0
,
1
]
\alpha \in [0, 1]
: a mixing hyperparameter controlling how much weight the
dense retrieval
score receives
1
−
α
1 - \alpha
: the complementary weight assigned to the
BM25
score
Setting
α
=
1
\alpha = 1
gives pure
dense retrieval
; setting
α
=
0
\alpha = 0
gives pure
BM25
; values around
0.5
0.5
to
0.7
0.7
often work well on mixed
query
benchmarks
The mixing parameter
α
\alpha
is the key lever for domain adaptation in weighted
fusion
. It lets you express a prior belief about how much to trust each retrieval modality. On a
corpus
of scientific literature where users frequently search by exact paper titles, author names, or technical acronyms, you might set
α
=
0.3
\alpha = 0.3
, giving 70% weight to
BM25
. On a customer-facing search system for a
knowledge base
where users ask open-ended questions in natural language, you might set
α
=
0.7
\alpha = 0.7
, giving 70% weight to
dense retrieval
. The ability to express this prior numerically, and to tune it empirically on labeled data, is the main advantage of weighted combination over RRF.
Advantages and Disadvantages
Link Copied
Weighted combination allows more precise tuning when you have
query
-level signals. If you know a
query
is lexical (an exact product name), you might increase
1
−
α
1 - \alpha
. If you know a
query
is semantic (a conceptual question), you might increase
α
\alpha
. Systems that classify
query
type before retrieval can dynamically set
α
\alpha
.
The downside is sensitivity to
normalization
.
Min-max normalization
is affected by
outliers
: if one document has an extremely high
BM25
score, it compresses all other scores toward zero. A single highly-matching document (for instance, one that contains every
query
term many times in a short document) can push all other documents' normalized scores close to zero, effectively neutralizing the contribution of
BM25
for that
query
. Less outlier-sensitive alternatives include score clipping before
normalization
or using
rank
-based sigmoid
normalization
. In contrast, RRF is entirely immune to outliers because it only uses ordinal position.
Reciprocal Rank Fusion vs. Weighted Combination
RRF is reliable to score scale differences and requires no tuning of the
k
k
parameter in practice (60 works broadly well). Weighted combination requires careful
normalization
and
α
\alpha
tuning but allows
query
-adaptive weighting. For most production systems, RRF is the safer default; weighted combination is useful when you have a labeled validation set to tune
α
\alpha
.
Ensemble and Learn-to-Rank Extensions
Link Copied
Beyond these two basic strategies, more advanced
fusion
methods exist. Learn-to-
rank
approaches train a lightweight model on top of retrieval features (
BM25
score, dense score, document length,
query
length) to predict
relevance
. These require labeled training data but can outperform fixed
fusion
weights materially on specialized domains.
The intuition behind
learn-to-rank fusion
is that different features matter differently for different
query
types. A
logistic regression
or gradient boosted tree trained on
relevance
labels can learn that
BM25
score is highly predictive for short, specific queries but dense score is more predictive for long, natural language questions. No fixed
α
\alpha
can capture this
query
-type-conditional behavior, but a learned model can.
Convex combination with
cross-validation
, where
α
\alpha
is tuned on held-out queries and their
relevance
judgments, is a practical middle ground that does not require full learn-to-
rank
infrastructure. If you have even a few hundred labeled
query
-document pairs from your domain, a cross-validated
α
\alpha
sweep over a grid of values (say, 0.0, 0.1, 0.2, ..., 1.0) typically takes seconds and often yields a real improvement over the default
α
=
0.5
\alpha = 0.5
.
Code Implementation
Link Copied
Let us build a
hybrid search
system step by step. We will use the
rank_bm25
library for the
BM25
half and
sentence-transformers
for the dense half, then implement both RRF and weighted
fusion
.
First, install the required libraries.
In
[
7
]:
Code
import
subprocess
subprocess
.
run
(
[
"
uv
"
,
"
pip
"
,
"
install
"
,
"
rank-bm25
"
,
"
sentence-transformers
"
,
"
--quiet
"
],
check
=
True
,
)
Setting Up the Corpus
Link Copied
We define a small
corpus
of documents that tests both semantic and lexical retrieval. Some queries will favor
BM25
(exact term matches), others will favor
dense retrieval
(semantic similarity).
In
[
8
]:
Code
# A small corpus illustrating different retrieval scenarios
corpus
=
[
"
Machine learning models require large amounts of training data to generalize well.
"
,
"
Deep neural networks have transformed computer vision with convolutional architectures.
"
,
"
Natural language processing lets computers to understand and generate human text.
"
,
"
The transformer architecture uses self-attention to model long-range dependencies.
"
,
"
BERT pre-training uses masked language modeling to learn bidirectional representations.
"
,
"
Retrieval-augmented generation combines search with language model generation.
"
,
"
BM25 is a probabilistic ranking function widely used in information retrieval.
"
,
"
Vector databases store high-dimensional embeddings for approximate nearest neighbor search.
"
,
"
Fine-tuning adapts a pre-trained model to a specific downstream task.
"
,
"
Product ID AB-1042-X failed quality inspection due to dimensional tolerances.
"
,
]
doc_ids
=
list
(
range
(
len
(
corpus
)))
corpus_size
=
len
(
corpus
)
Out
[
9
]:
Console
Corpus size: 10 documents
The
corpus
deliberately mixes conceptual machine learning documents with one highly specific product record (document 9). This makes possible us show
BM25
's strength on exact lexical matches and
dense retrieval
's strength on semantic paraphrase queries.
BM25 Retrieval
Link Copied
We
tokenize
the
corpus
and build a
BM25
index using
rank_bm25
.
In
[
10
]:
Code
from
rank_bm25
import
BM25Okapi
# Tokenize corpus: lowercase and split on whitespace
tokenized_corpus
=
[
doc
.
lower
().
split
()
for
doc
in
corpus
]
bm25
=
BM25Okapi
(
tokenized_corpus
)
vocab_size
=
len
(
set
(
tok
for
doc
in
tokenized_corpus
for
tok
in
doc
))
Out
[
11
]:
Console
BM25 index built.
Vocabulary size: 88 unique tokens
BM25Okapi
implements the standard
BM25
variant with default parameters
k
1
=
1.5
k_1 = 1.5
and
b
=
0.75
b = 0.75
. We use simple
whitespace tokenization
here; production systems would apply stemming and stopword removal for better coverage.
Now we write a
BM25
retrieval function that returns ranked document indices with their scores.
In
[
12
]:
Code
def
bm25_search
(
query
:
str
,
top_k
:
int
=
5
):
"""
Return top_k documents ranked by BM25 score.
"""
tokens
=
query
.
lower
().
split
()
scores
=
bm25
.
get_scores
(
tokens
)
ranked_indices
=
np
.
argsort
(
scores
)[::
-
1
][:
top_k
]
return
[(
int
(
idx
),
float
(
scores
[
idx
]))
for
idx
in
ranked_indices
]
Dense Retrieval
Link Copied
We encode the
corpus
with a sentence-
transformer
model. In production systems you would pre-compute and store these
embeddings
, but here we compute them inline to keep the code self-contained.
In
[
13
]:
Code
from
sentence_transformers
import
SentenceTransformer
model
=
SentenceTransformer
(
"
all-MiniLM-L6-v2
"
)
# Encode all documents at once (efficient batch encoding)
corpus_embeddings
=
model
.
encode
(
corpus
,
normalize_embeddings
=
True
,
show_progress_bar
=
False
)
embeddings_shape
=
corpus_embeddings
.
shape
Out
[
14
]:
Console
Corpus embeddings shape: (10, 384)
The model produces 384-dimensional normalized
embeddings
for each document. Because the embeddings are L2-normalized, dot product and
cosine similarity
are equivalent, which makes retrieval a simple matrix-
vector
multiplication.
In
[
15
]:
Code
def
dense_search
(
query
:
str
,
top_k
:
int
=
5
):
"""
Return top_k documents ranked by cosine similarity.
"""
query_embedding
=
model
.
encode
(
query
,
normalize_embeddings
=
True
)
# Since embeddings are L2-normalized, dot product equals cosine similarity
scores
=
np
.
dot
(
corpus_embeddings
,
query_embedding
)
ranked_indices
=
np
.
argsort
(
scores
)[::
-
1
][:
top_k
]
return
[(
int
(
idx
),
float
(
scores
[
idx
]))
for
idx
in
ranked_indices
]
Reciprocal Rank Fusion
Link Copied
We now implement RRF. It takes multiple ranked lists, each as a list of
(doc_id, score)
tuples, and combines them.
In
[
16
]:
Code
def
reciprocal_rank_fusion
(
ranked_lists
:
list
,
k
:
int
=
60
,
top_k
:
int
=
5
):
"""
Combine multiple ranked lists using Reciprocal Rank Fusion.
Args:
ranked_lists: List of [(doc_id, score), ...] sorted by descending score
k: Smoothing constant (default 60)
top_k: Number of results to return
Returns:
List of (doc_id, rrf_score) sorted by descending RRF score
"""
rrf_scores
=
{}
for
ranked_list
in
ranked_lists
:
for
rank
,
(
doc_id
,
_score
)
in
enumerate
(
ranked_list
,
start
=
1
):
rrf_scores
[
doc_id
]
=
rrf_scores
.
get
(
doc_id
,
0.0
)
+
1.0
/
(
k
+
rank
)
sorted_docs
=
sorted
(
rrf_scores
.
items
(),
key
=
lambda
x
:
x
[
1
],
reverse
=
True
)
return
sorted_docs
[:
top_k
]
Weighted Score Combination
Link Copied
For weighted
fusion
, we normalize scores and apply a mixing weight
α
\alpha
.
In
[
17
]:
Code
def
normalize_scores
(
ranked_list
:
list
)
->
dict
:
"""
Min-max normalize scores from a ranked list. Returns {doc_id: normalized_score}.
"""
if
not
ranked_list
:
return
{}
scores
=
[
score
for
_
,
score
in
ranked_list
]
min_score
=
min
(
scores
)
max_score
=
max
(
scores
)
score_range
=
max_score
-
min_score
if
score_range
==
0
:
return
{
doc_id
:
1.0
for
doc_id
,
_
in
ranked_list
}
return
{
doc_id
:
(
score
-
min_score
)
/
score_range
for
doc_id
,
score
in
ranked_list
}
def
weighted_fusion
(
bm25_results
:
list
,
dense_results
:
list
,
alpha
:
float
=
0.5
,
top_k
:
int
=
5
):
"""
Combine BM25 and dense retrieval results using weighted score combination.
Args:
bm25_results: [(doc_id, bm25_score), ...]
dense_results: [(doc_id, dense_score), ...]
alpha: Weight for dense scores (1 - alpha goes to BM25)
top_k: Number of results to return
Returns:
List of (doc_id, combined_score) sorted by descending combined score
"""
bm25_norm
=
normalize_scores
(
bm25_results
)
dense_norm
=
normalize_scores
(
dense_results
)
# Collect all unique doc IDs
all_doc_ids
=
set
(
bm25_norm
.
keys
())
|
set
(
dense_norm
.
keys
())
combined
=
{}
for
doc_id
in
all_doc_ids
:
b_score
=
bm25_norm
.
get
(
doc_id
,
0.0
)
d_score
=
dense_norm
.
get
(
doc_id
,
0.0
)
combined
[
doc_id
]
=
alpha
*
d_score
+
(
1
-
alpha
)
*
b_score
sorted_docs
=
sorted
(
combined
.
items
(),
key
=
lambda
x
:
x
[
1
],
reverse
=
True
)
return
sorted_docs
[:
top_k
]
Running Hybrid Search
Link Copied
Let us test all three retrieval modes on two contrasting queries: one semantic, one lexical.
In
[
18
]:
Code
def
display_results
(
results
:
list
,
label
:
str
):
"""
Pretty-print retrieval results.
"""
print
(
f
"
\n{
'
=
'
*
60
}
"
)
print
(
f
"
{
label
}
"
)
print
(
f
"
{
'
=
'
*
60
}
"
)
for
rank
,
(
doc_id
,
score
)
in
enumerate
(
results
,
start
=
1
):
snippet
=
corpus
[
doc_id
][:
75
]
+
(
"
...
"
if
len
(
corpus
[
doc_id
])
>
75
else
""
)
print
(
f
"
{
rank
}
. [doc
{
doc_id
}
] (score:
{
score
:.4f
}
)"
)
print
(
f
"
{
snippet
}
"
)
In
[
19
]:
Code
TOP_K
=
5
# Query 1: Semantic: no exact keyword overlap expected with best answer
semantic_query
=
"
how do language models learn to stand for text meaning
"
bm25_r1
=
bm25_search
(
semantic_query
,
top_k
=
TOP_K
)
dense_r1
=
dense_search
(
semantic_query
,
top_k
=
TOP_K
)
rrf_r1
=
reciprocal_rank_fusion
([
bm25_r1
,
dense_r1
],
top_k
=
TOP_K
)
wf_r1
=
weighted_fusion
(
bm25_r1
,
dense_r1
,
alpha
=
0.6
,
top_k
=
TOP_K
)
Out
[
20
]:
Console
============================================================
  BM25: 'how do language models learn to stand for text meaning'
============================================================
  1. [doc 4] (score: 3.0653)
     BERT pre-training uses masked language modeling to learn bidirectional repr...
  2. [doc 0] (score: 2.1108)
     Machine learning models require large amounts of training data to generaliz...
  3. [doc 7] (score: 1.8541)
     Vector databases store high-dimensional embeddings for approximate nearest ...
  4. [doc 2] (score: 1.1594)
     Natural language processing lets computers to understand and generate human...
  5. [doc 5] (score: 0.8408)
     Retrieval-augmented generation combines search with language model generati...

============================================================
  Dense: 'how do language models learn to stand for text meaning'
============================================================
  1. [doc 4] (score: 0.4868)
     BERT pre-training uses masked language modeling to learn bidirectional repr...
  2. [doc 5] (score: 0.4779)
     Retrieval-augmented generation combines search with language model generati...
  3. [doc 2] (score: 0.4726)
     Natural language processing lets computers to understand and generate human...
  4. [doc 8] (score: 0.3273)
     Fine-tuning adapts a pre-trained model to a specific downstream task.
  5. [doc 0] (score: 0.3144)
     Machine learning models require large amounts of training data to generaliz...

============================================================
  RRF Hybrid: 'how do language models learn to stand for text meaning'
============================================================
  1. [doc 4] (score: 0.0328)
     BERT pre-training uses masked language modeling to learn bidirectional repr...
  2. [doc 0] (score: 0.0315)
     Machine learning models require large amounts of training data to generaliz...
  3. [doc 5] (score: 0.0315)
     Retrieval-augmented generation combines search with language model generati...
  4. [doc 2] (score: 0.0315)
     Natural language processing lets computers to understand and generate human...
  5. [doc 7] (score: 0.0159)
     Vector databases store high-dimensional embeddings for approximate nearest ...

============================================================
  Weighted (alpha=0.6) Hybrid: 'how do language models learn to stand for text meaning'
============================================================
  1. [doc 4] (score: 1.0000)
     BERT pre-training uses masked language modeling to learn bidirectional repr...
  2. [doc 2] (score: 0.6077)
     Natural language processing lets computers to understand and generate human...
  3. [doc 5] (score: 0.5690)
     Retrieval-augmented generation combines search with language model generati...
  4. [doc 0] (score: 0.2284)
     Machine learning models require large amounts of training data to generaliz...
  5. [doc 7] (score: 0.1822)
     Vector databases store high-dimensional embeddings for approximate nearest ...
In
[
21
]:
Code
# Query 2: Lexical: exact product code that dense retrieval may miss
lexical_query
=
"
AB-1042-X quality inspection
"
bm25_r2
=
bm25_search
(
lexical_query
,
top_k
=
TOP_K
)
dense_r2
=
dense_search
(
lexical_query
,
top_k
=
TOP_K
)
rrf_r2
=
reciprocal_rank_fusion
([
bm25_r2
,
dense_r2
],
top_k
=
TOP_K
)
wf_r2
=
weighted_fusion
(
bm25_r2
,
dense_r2
,
alpha
=
0.6
,
top_k
=
TOP_K
)
Out
[
22
]:
Console
============================================================
  BM25: 'AB-1042-X quality inspection'
============================================================
  1. [doc 9] (score: 5.5623)
     Product ID AB-1042-X failed quality inspection due to dimensional tolerance...
  2. [doc 8] (score: 0.0000)
     Fine-tuning adapts a pre-trained model to a specific downstream task.
  3. [doc 7] (score: 0.0000)
     Vector databases store high-dimensional embeddings for approximate nearest ...
  4. [doc 6] (score: 0.0000)
     BM25 is a probabilistic ranking function widely used in information retriev...
  5. [doc 5] (score: 0.0000)
     Retrieval-augmented generation combines search with language model generati...

============================================================
  Dense: 'AB-1042-X quality inspection'
============================================================
  1. [doc 9] (score: 0.8179)
     Product ID AB-1042-X failed quality inspection due to dimensional tolerance...
  2. [doc 6] (score: 0.1952)
     BM25 is a probabilistic ranking function widely used in information retriev...
  3. [doc 3] (score: 0.1142)
     The transformer architecture uses self-attention to model long-range depend...
  4. [doc 1] (score: 0.0462)
     Deep neural networks have transformed computer vision with convolutional ar...
  5. [doc 7] (score: 0.0408)
     Vector databases store high-dimensional embeddings for approximate nearest ...

============================================================
  RRF Hybrid: 'AB-1042-X quality inspection'
============================================================
  1. [doc 9] (score: 0.0328)
     Product ID AB-1042-X failed quality inspection due to dimensional tolerance...
  2. [doc 6] (score: 0.0318)
     BM25 is a probabilistic ranking function widely used in information retriev...
  3. [doc 7] (score: 0.0313)
     Vector databases store high-dimensional embeddings for approximate nearest ...
  4. [doc 8] (score: 0.0161)
     Fine-tuning adapts a pre-trained model to a specific downstream task.
  5. [doc 3] (score: 0.0159)
     The transformer architecture uses self-attention to model long-range depend...

============================================================
  Weighted (alpha=0.6) Hybrid: 'AB-1042-X quality inspection'
============================================================
  1. [doc 9] (score: 1.0000)
     Product ID AB-1042-X failed quality inspection due to dimensional tolerance...
  2. [doc 6] (score: 0.1192)
     BM25 is a probabilistic ranking function widely used in information retriev...
  3. [doc 3] (score: 0.0567)
     The transformer architecture uses self-attention to model long-range depend...
  4. [doc 1] (score: 0.0042)
     Deep neural networks have transformed computer vision with convolutional ar...
  5. [doc 5] (score: 0.0000)
     Retrieval-augmented generation combines search with language model generati...
For the semantic
query
,
dense retrieval
ranks the
BERT
document (doc 4) near the top because it understands that "bidirectional representations" relates to "stand for text meaning," even though the words do not overlap.
BM25
ranks it lower because the
query
terms are not present verbatim. For the product code
query
,
BM25
immediately surfaces doc 9, which contains "AB-1042-X" exactly. The hybrid systems inherit the best of both behaviors.
Visualizing Score Distributions and Fusion
Link Copied
Let us visualize how the
BM25
and dense scores distribute across documents for a single
query
, and how RRF flattens the
rank
-score curve compared to raw scores.
Out
[
23
]:
Visualization
BM25 and dense retrieval score distributions for a semantic query across all 10 corpus documents. BM25 scores (normalized for display) reflect term-frequency-weighted IDF sums, while cosine similarities are bounded near 1. The two score scales are incompatible for direct summation, motivating rank-based fusion methods like RRF.
RRF score decay curves for three values of k (10, 60, 120) across the top 50 rank positions. Smaller k creates a steeper drop from rank 1 to rank 2, amplifying top-rank advantages. Larger k flattens the curve, treating many top-ranked documents more equally. The default k=60 gives a practical balance between these extremes.
The left panel shows that
BM25
and dense scores for the same
query
are not directly comparable:
BM25
scores reflect term-frequency-weighted
IDF
sums while cosine similarities are bounded between -1 and 1 with a very different distribution. This is exactly why naive score addition fails. The right panel illustrates the RRF curve for three values of
k
k
: smaller
k
k
creates a steeper drop from
rank
1 to
rank
2 (amplifying top-
rank
advantages), while larger
k
k
flattens the curve (treating many top-ranked documents more equally). The default
k
=
60
k = 60
strikes a practical balance.
Evaluating Hybrid Retrieval Quality
Link Copied
To quantitatively assess
hybrid search
, we compute
Mean Reciprocal Rank
(MRR) and
Recall
@K. We need ground-truth
relevance
judgments. For this example we define them manually.
Mean Reciprocal Rank (MRR)
MRR measures how high in the ranked list the first relevant document appears. For a set of queries
Q
Q
, MRR is defined as:
MRR
=
1
∣
Q
∣
∑
q
∈
Q
1
rank
q
\text{MRR} = \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\text{rank}_q}
where:
∣
Q
∣
|Q|
: the total number of queries in the evaluation set
rank
q
\text{rank}_q
: the
rank
position of the first relevant document for
query
q
q
in the retrieved list
1
/
rank
q
1 / \text{rank}_q
: the reciprocal
rank
for
query
q
q
; this equals 1 when the relevant document is ranked first, 0.5 when it is ranked second, and so on
A perfect system reaches MRR = 1.0, meaning the first relevant document is always ranked first. If no relevant document appears in the retrieved list for a
query
, that
query
contributes 0 to the sum.
MRR is particularly well-suited for tasks where there is a single correct answer or a small set of highly relevant documents, and the user's primary goal is to find any relevant document quickly. If a relevant document is first in the ranked list for 3 out of 4 queries but ranked 2nd for one
query
, MRR =
(
1
+
1
+
1
+
0.5
)
/
4
=
0.875
(1 + 1 + 1 + 0.5) / 4 = 0.875
. This makes the metric intuitive: every drop in
rank
position for the first relevant document is penalized proportionally.
In
[
24
]:
Code
# Ground truth: for each query, which document indices are relevant
ground_truth
=
{
"
how do language models learn to stand for text meaning
"
:
{
4
},
# BERT doc
"
AB-1042-X quality inspection
"
:
{
9
},
# Product ID doc
"
transformer self-attention mechanism
"
:
{
3
},
# Transformer doc
"
approximate nearest neighbor vector search
"
:
{
7
},
# Vector DB doc
}
def
recall_at_k
(
results
:
list
,
relevant_docs
:
set
,
k
:
int
=
5
)
->
float
:
"""
Fraction of relevant docs found in top-k results.
"""
retrieved_ids
=
{
doc_id
for
doc_id
,
_
in
results
[:
k
]}
return
len
(
retrieved_ids
&
relevant_docs
)
/
len
(
relevant_docs
)
def
reciprocal_rank
(
results
:
list
,
relevant_docs
:
set
)
->
float
:
"""
Reciprocal of rank of first relevant document.
"""
for
rank
,
(
doc_id
,
_
)
in
enumerate
(
results
,
start
=
1
):
if
doc_id
in
relevant_docs
:
return
1.0
/
rank
return
0.0
In
[
25
]:
Code
queries
=
list
(
ground_truth
.
keys
())
methods
=
{
"
BM25
"
:
[],
"
Dense
"
:
[],
"
RRF Hybrid
"
:
[],
"
Weighted (a=0.6)
"
:
[]}
for
query
in
queries
:
relevant
=
ground_truth
[
query
]
b_res
=
bm25_search
(
query
,
top_k
=
10
)
d_res
=
dense_search
(
query
,
top_k
=
10
)
r_res
=
reciprocal_rank_fusion
([
b_res
,
d_res
],
top_k
=
10
)
w_res
=
weighted_fusion
(
b_res
,
d_res
,
alpha
=
0.6
,
top_k
=
10
)
for
label
,
results
in
[
(
"
BM25
"
,
b_res
),
(
"
Dense
"
,
d_res
),
(
"
RRF Hybrid
"
,
r_res
),
(
"
Weighted (a=0.6)
"
,
w_res
),
]:
rr
=
reciprocal_rank
(
results
,
relevant
)
r5
=
recall_at_k
(
results
,
relevant
,
k
=
5
)
methods
[
label
].
append
((
rr
,
r5
))
Out
[
26
]:
Console
Method                         MRR   Recall@5
---------------------------------------------
BM25                        1.0000     1.0000
Dense                       1.0000     1.0000
RRF Hybrid                  1.0000     1.0000
Weighted (a=0.6)            1.0000     1.0000
All four methods score perfectly on this ten-document toy
corpus
. That is useful as an implementation sanity check, but it is not a meaningful quality comparison: with one relevant document per
query
and only ten candidates, the task is too easy to expose complementary errors. The figure below therefore uses an explicitly illustrative held-out
benchmark
profile to show the trade-off that a real labeled evaluation should measure. In production, replace these example values with metrics from a representative
query
set.
Visualizing Fusion Performance
Link Copied
Out
[
27
]:
Visualization
Illustrative held-out benchmark profile comparing MRR and Recall@5 across BM25, dense retrieval, RRF hybrid, and weighted fusion (alpha=0.6). The example values show how complementary lexical and semantic evidence can improve both first-relevant-result ranking and top-five coverage. Production systems should replace these values with measurements from their own labeled query set.
Visualizing Alpha Sensitivity in Weighted Fusion
Link Copied
The
alpha parameter
in weighted
fusion
controls the balance between lexical and semantic signals. Because the tiny live
corpus
above saturates, the following sensitivity profile is explicitly illustrative: it shows the common pattern of dense-favored queries improving as alpha rises while
BM25
-favored queries decline. A production system should generate this curve by sweeping alpha on a labeled development set.
In
[
28
]:
Code
# Build an illustrative MRR sensitivity profile as alpha varies from 0 to 1.
alpha_vals
=
np
.
linspace
(
0
,
1
,
41
)
dense_favored_mrr
=
0.56
+
0.31
*
(
1
-
np
.
exp
(
-
2.4
*
alpha_vals
))
/
(
1
-
np
.
exp
(
-
2.4
)
)
bm25_favored_mrr
=
0.89
-
0.29
*
alpha_vals
**
1.35
Out
[
29
]:
Visualization
Illustrative MRR sensitivity profile as the alpha mixing parameter moves from pure BM25 to pure dense retrieval. Dense-favored queries improve as alpha rises, while BM25-favored queries decline. Their crossing region shows why a balanced alpha can be a practical compromise for mixed workloads, but production tuning should use a labeled development set.
The illustrative sensitivity plot reveals the key tuning trade-off.
BM25
-favored queries reach their highest MRR near alpha 0, while dense-favored queries improve as more weight shifts to the dense score. A system serving a mixed workload should therefore tune alpha on a representative sample of labeled queries rather than defaulting to 0.5. If the workload skews toward exact identifiers and lexical lookups, a lower alpha is often safer. If it skews toward paraphrased natural-language questions, a higher alpha may work better.
Key Parameters
Link Copied
The key parameters for building and tuning a
hybrid search
system are:
k1
(
BM25
):
Term frequency
saturation constant, typically 1.2 to 1.5. Higher values allow
term frequency
to contribute more before saturating; lower values saturate faster and give more equal weight to each term occurrence.
b
(
BM25
):
Length normalization
strength, typically 0.75. A value of 1.0 applies full
length normalization
; 0.0 disables it entirely.
k
(RRF):
Smoothing
constant for
reciprocal rank fusion
, typically 60. Larger values flatten the
rank
-score curve, giving more equal credit to documents ranked anywhere in the top list.
alpha
(weighted
fusion
): Mixing weight for dense scores, in
[
0
,
1
]
[0, 1]
. Values near 0.5 to 0.7 often work well on mixed
query
benchmarks; tune on labeled data specific to your domain.
top_k
: Number of candidates to retrieve from each system before
fusion
. Larger values increase
recall
but also increase
fusion
computation time.
Practical Considerations
Link Copied
Implementing
hybrid search
in production requires more thought than the toy examples above suggest. Several practical issues arise at scale that are easy to overlook when prototyping. The gap between a working demonstration and a production-ready system is real, and understanding it before you start will save significant time.
Think of production
hybrid search
as managing two parallel pipelines that must be orchestrated carefully. Each pipeline has its own index, its own serving infrastructure, and its own failure modes. When they run correctly in parallel, the combined system is better than either alone. When one pipeline is slow, misconfigured, or serving stale data, the hybrid output degrades in ways that are harder to debug than single-system failures.
Index Design and Latency
Link Copied
BM25
and
dense retrieval
have fundamentally different index types.
BM25
uses an
inverted index
: a map from each vocabulary term to the list of documents containing it, along with
term frequency
statistics. This index scales well with document count and supports very fast retrieval for short queries through
posting list
intersection.
Dense retrieval
uses an
approximate nearest neighbor
index (
HNSW
,
IVF
, or similar, as discussed in prior chapters) over high-dimensional
embeddings
. Both indices can be queried in milliseconds at
corpus
sizes in the millions, but they must both be queried in parallel for
hybrid search
to avoid doubling latency.
Well-designed
hybrid search
systems issue both queries simultaneously and join the results after both return. If one system is materially slower, it becomes the bottleneck. In practice,
HNSW
indexes on GPU-accelerated hardware are often faster than
BM25
on large corpora, making the
inverted index
the potential bottleneck for very high
query
volumes.
The memory footprint also differs substantially. An
inverted index
for a million-document
corpus
might occupy a few gigabytes, dominated by term-frequency and document-frequency statistics. A dense index storing 768-dimensional float32 embeddings for the same
corpus
occupies
1,000,000
×
768
×
4
=
3.07
1{,}000{,}000 \times 768 \times 4 = 3.07
GB just for the raw vectors, before any index structure overhead. For large corpora, the memory requirements for the dense index are the binding constraint, and strategies like
product quantization
(compressing each
vector
to a smaller representation) become necessary.
Sparse and Dense Index Co-location
Link Copied
Modern
vector database
systems like Elasticsearch (with
vector
search extensions) and Weaviate support
hybrid retrieval
natively, maintaining both an
inverted index
for
BM25
and a
vector
index for
dense retrieval
within a single system. This simplifies operational complexity. Alternatively, you can run Elasticsearch or Apache Solr for
BM25
alongside a separate Faiss or Qdrant instance for
dense retrieval
, but this requires managing two separate services and merging results at the application layer.
The co-location approach has operational advantages: a single system to monitor, a single API to
query
, and a single codebase to maintain. The split-system approach gives more flexibility in choosing the best tool for each retrieval type and can scale each component independently. For teams with strong DevOps infrastructure, the split approach is fine. For teams that want operational simplicity, a system with native
hybrid search
support is strongly preferred.
Domain Adaptation and Weight Tuning
Link Copied
The optimal
α
\alpha
for weighted
fusion
or the choice between RRF and weighted
fusion
depends heavily on the domain and
query
distribution. On technical documentation corpora where users frequently search by exact function names, class names, or error codes, heavier weight toward
BM25
is beneficial. On open-domain
question answering
or customer support corpora where users rephrase common questions differently each time, heavier weight toward
dense retrieval
often wins.
The best practice is to collect a sample of real queries with
relevance
judgments (which documents users clicked, or human-annotated relevant documents) and use those to tune
α
\alpha
via
cross-validation
. Without labeled data, RRF with the default
k
=
60
k = 60
is the safest starting point.
Sparse Encoders as a Third Hybrid Component
Link Copied
A growing trend extends
hybrid search
with sparse learned encoders like
SPLADE
.
SPLADE
uses a
transformer
to produce a
sparse vector
over the full vocabulary, where each dimension is a term's importance weighted by the model's understanding of the
query
or document. Unlike
BM25
, which is purely term-frequency-based,
SPLADE
can expand a
query
"heart attack" to also assign high weight to "myocardial," "cardiac," and "infarction" in its sparse representation. This makes sparse encoders a middle ground between classical
BM25
and dense retrievers: they maintain the sparse, vocabulary-aligned structure that supports efficient
inverted index
retrieval while incorporating semantic understanding.
Think of
SPLADE
as a learned version of
query
expansion: instead of manually writing synonym dictionaries, the model learns from training data which vocabulary dimensions should be activated for which queries and documents. The resulting sparse vectors can be indexed and searched using the same
inverted index
infrastructure as
BM25
, but they capture a much richer notion of term
relevance
. Hybrid systems combining
BM25
,
SPLADE
, and
dense retrieval
can outperform any pairwise combination, though they also increase system complexity and require more index infrastructure.
Limitations and Impact
Link Copied
Hybrid search
is not a free lunch. Combining two retrieval systems doubles the infrastructure: you must maintain two indices, execute two retrieval operations per
query
, and implement
fusion
logic that is correct under all edge cases (empty ranked lists, ties, score
normalization
edge cases). For small-scale applications or corpora with clear lexical structure, a well-tuned
BM25
system alone may outperform a poorly-configured hybrid system. The additional complexity pays off only when the two systems have complementary coverage on your specific
query
distribution.
The latency cost, while often manageable through parallelization, is real. If your retrieval must complete in under 50 milliseconds and your
dense retrieval
alone takes 40 milliseconds, adding
BM25
without careful
parallel execution
will breach latency budgets.
Hybrid search
also shifts the debugging challenge: when results are wrong, it is now unclear whether the failure originates in the
BM25
component, the dense component, or the
fusion
logic. A document that deserved to
rank
first might have ranked 3rd in
BM25
(low
BM25
score) and 3rd in dense (moderate
cosine similarity
), giving it a low combined score even though it was the best match. Diagnosing this requires inspecting both individual system outputs, which adds operational overhead.
Weighted score combination
introduces an additional fragility: the
normalization
is sensitive to the retrieval pool size. If you retrieve top-100 from each system before fusing, the min and max scores used for
normalization
are computed over 100 results. If you change to top-50, the
normalization
range changes, and the same document receives a different normalized score even though nothing else changed. This coupling between retrieval depth and score
normalization
is a subtle source of inconsistency in production systems that switch retrieval depths dynamically. RRF does not have this problem because it uses only
rank
positions.
Despite these challenges,
hybrid search
has become a standard architectural pattern in production
RAG
systems because the
recall
gains are consistent and the tradeoffs are well understood. The BEIR
benchmark
, a heterogeneous collection of information retrieval datasets, has repeatedly shown that no single retrieval method dominates across all domains.
Hybrid search
is the practical response to this fragmentation: rather than betting on one paradigm, you hedge across both. The incremental infrastructure cost is justified by more consistent results across diverse
query
types.
The impact on downstream RAG performance is particularly significant. As we explore in the upcoming
Reranking
chapter, the generator's answer quality depends critically on whether the correct document appears in the retrieved context at all. A failure to retrieve the relevant document cannot be corrected by a better reranker or a more capable generator. By increasing
recall
,
hybrid search
raises the quality ceiling for the entire
RAG pipeline
.
Summary
Link Copied
Hybrid search
combines
BM25
keyword retrieval with dense semantic retrieval to reach better
recall
than either system alone:
BM25
uses saturated
term frequency
,
inverse document frequency
, and document
length normalization
to
rank
documents by keyword
relevance
. Its key hyperparameters
k
1
k_1
and
b
b
control saturation and
length normalization
.
Dense retrieval
encodes queries and documents as dense vectors and ranks by
cosine similarity
. This makes possible semantic generalization across paraphrases and synonyms.
Reciprocal rank fusion (RRF)
combines ranked lists by summing
1
/
(
k
+
r
)
1/(k + r)
contributions per document, bypassing
score scale incompatibility
. The default
k
=
60
k = 60
works broadly well without tuning.
Weighted score combination
normalizes scores to a common range and blends them with a weight
α
\alpha
, letting
query
-adaptive
fusion
but requiring careful
normalization
and hyperparameter tuning.
Both systems excel at different
query
types:
BM25
handles exact-match and rare-term queries;
dense retrieval
handles semantic and paraphrase queries. Their
recall
failures are complementary, which is the core reason
hybrid search
improves over either alone.
In production, both indices should be queried in parallel to avoid latency doubling. Systems like Elasticsearch with
vector
extensions support
hybrid search
natively.
With hybrid retrieval improving
recall
, the next challenge is
precision
: so the top-ranked documents are truly the most relevant ones. The next chapter on
Reranking
addresses exactly this, using
cross-encoder
models that jointly encode
query
and document to produce more accurate
relevance
scores for the candidate set that hybrid retrieval gives.
Quiz
Link Copied
Ready to test your understanding? Take this quick quiz to
reinforce
what you've learned about
hybrid search
.
Hybrid Search Quiz
Question
1
of
8
0
of
8
completed
What does the parameter k1 control in the BM25 formula?
The strength of document length normalization
The number of documents retrieved per query
The saturation ceiling for term frequency contributions
The inverse document frequency smoothing constant
Check Answer
Comments
No comments yet. Be the first to share your thoughts!
Reference
Citation details
Cite or share this article.
BIBTEX
Academic
Copy
@misc{brenndoerfer2026hybridsearch,
  author = {Michael Brenndoerfer},
  title = {Hybrid Search: BM25 and Dense Retrieval Combined},
  year = {2026},
  url = {https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion},
  organization = {mbrenndoerfer.com},
  note = {Accessed: 2026-09-13}
}
Show other formats
APA · MLA · Chicago · Harvard · Simple
APA
Academic
Copy
Michael Brenndoerfer (2026). Hybrid Search: BM25 and Dense Retrieval Combined. Retrieved from https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion
MLA
Academic
Copy
Michael Brenndoerfer. "Hybrid Search: BM25 and Dense Retrieval Combined." 2026. Web. September 13, 2026. <https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion>.
CHICAGO
Academic
Copy
Michael Brenndoerfer. "Hybrid Search: BM25 and Dense Retrieval Combined." Accessed September 13, 2026. https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion.
HARVARD
Academic
Copy
Michael Brenndoerfer (2026) 'Hybrid Search: BM25 and Dense Retrieval Combined'. Available at: https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion (Accessed: September 13, 2026).
Simple
Basic
Copy
Michael Brenndoerfer (2026). Hybrid Search: BM25 and Dense Retrieval Combined. https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion
DIRECT LINK
URL
Copy
https://mbrenndoerfer.com/writing/hybrid-search-bm25-dense-retrieval-fusion
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
Product Quantization: Vector Compression for ANN Search
Next Chapter
Reranking: Cross-Encoders for Precise Information Retrieval
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
RAG Prompt Engineering: Context Placement
Jan 31, 2026
•
53
min read
Machine Learning
Language AI Handbook
Covers RAG prompt engineering with strategic context placement, citation formats, and truncation strategies to improve LLM accuracy and reduce hallucinations.
Read more
Reranking: Cross-Encoders for Precise Information Retrieval
Jan 30, 2026
•
61
min read
Language AI Handbook
Explains how reranking with cross-encoders solves bi-encoder limitations. Topics include two-stage retrieval, training strategies.
Read more
Product Quantization: Vector Compression for ANN Search
Jan 28, 2026
•
62
min read
Data, Analytics & AI
Machine Learning
Explains how Product Quantization compresses embeddings up to 100x using learned codebooks and asymmetric distance computation for scalable vector search.
Read more
IVF Index: Clustering-Based Vector Search & Partitioning
Jan 27, 2026
•
66
min read
Machine Learning
Data, Analytics & AI
Covers IVF indexes for scalable vector search. Topics include clustering-based partitioning, nprobe tuning, and IVF-PQ compression for billion-scale retrieval.
Read more
All writing