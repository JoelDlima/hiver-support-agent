---
title: TimeSeriesSplit — scikit-learn 1.9.1 documentation
id: timeseriessplit-scikit-learn-191-documentation
tags:
- hiver-support-agent-audit-6d951f
- locus-leakage-safe-temporal-split-vs-random-stratified-split
created: '2026-09-15T02:39:16.984577Z'
source: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
source_domain: scikit-learn.org
fetched_at: '2026-09-15T02:39:16.983516Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

TimeSeriesSplit — scikit-learn 1.9.1 documentation
Skip to main content
Back to top
Ctrl
+
K
System Settings
Light
Dark
GitHub
Choose version
Collapse Sidebar
Expand Sidebar
TimeSeriesSplit
#
class
sklearn.model_selection.
TimeSeriesSplit
(
n_splits
=
5
,
*
,
max_train_size
=
None
,
test_size
=
None
,
gap
=
0
)
[source]
#
Time Series cross-validator.
Provides train/test indices to split time-ordered data, where other
cross-validation methods are inappropriate, as they would lead to training
on future data and evaluating on past data.
To ensure comparable metrics across folds, samples must be equally spaced.
Once this condition is met, each test set covers the same time duration,
while the train set size accumulates data from previous splits.
This cross-validation object is a variation of
KFold
.
In the k-th split, it returns the first k folds as the train set and the
(k+1)-th fold as the test set.
Note that, unlike standard cross-validation methods, successive
training sets are supersets of those that come before them.
Read more in the
User Guide
.
For visualisation of cross-validation behaviour and
comparison between common scikit-learn split methods
refer to
Visualizing cross-validation behavior in scikit-learn
Added in version 0.18.
Parameters
:
n_splits
int, default=5
Number of splits. Must be at least 2.
Changed in version 0.22:
n_splits
default value changed from 3 to 5.
max_train_size
int, default=None
Maximum size for a single training set.
test_size
int, default=None
Used to limit the size of the test set. Defaults to
n_samples
//
(n_splits
+
1)
, which is the maximum allowed value
with
gap=0
.
Added in version 0.24.
gap
int, default=0
Number of samples to exclude from the end of each train set before
the test set.
Added in version 0.24.
Notes
The training set has size
i
*
n_samples
//
(n_splits
+
1)
+
n_samples
%
(n_splits
+
1)
in the
i
th split,
with a test set of size
n_samples//(n_splits
+
1)
by default,
where
n_samples
is the number of samples. Note that this
formula is only valid when
test_size
and
max_train_size
are
left to their default values.
Examples
>>>
import
numpy
as
np
>>>
from
sklearn.model_selection
import
TimeSeriesSplit
>>>
X
=
np
.
array
([[
1
,
2
],
[
3
,
4
],
[
1
,
2
],
[
3
,
4
],
[
1
,
2
],
[
3
,
4
]])
>>>
y
=
np
.
array
([
1
,
2
,
3
,
4
,
5
,
6
])
>>>
tscv
=
TimeSeriesSplit
()
>>>
print
(
tscv
)
TimeSeriesSplit(gap=0, max_train_size=None, n_splits=5, test_size=None)
>>>
for
i
,
(
train_index
,
test_index
)
in
enumerate
(
tscv
.
split
(
X
)):
...
print
(
f
"Fold
{
i
}
:"
)
...
print
(
f
"  Train: index=
{
train_index
}
"
)
...
print
(
f
"  Test:  index=
{
test_index
}
"
)
Fold 0:
Train: index=[0]
Test:  index=[1]
Fold 1:
Train: index=[0 1]
Test:  index=[2]
Fold 2:
Train: index=[0 1 2]
Test:  index=[3]
Fold 3:
Train: index=[0 1 2 3]
Test:  index=[4]
Fold 4:
Train: index=[0 1 2 3 4]
Test:  index=[5]
>>>
# Fix test_size to 2 with 12 samples
>>>
X
=
np
.
random
.
randn
(
12
,
2
)
>>>
y
=
np
.
random
.
randint
(
0
,
2
,
12
)
>>>
tscv
=
TimeSeriesSplit
(
n_splits
=
3
,
test_size
=
2
)
>>>
for
i
,
(
train_index
,
test_index
)
in
enumerate
(
tscv
.
split
(
X
)):
...
print
(
f
"Fold
{
i
}
:"
)
...
print
(
f
"  Train: index=
{
train_index
}
"
)
...
print
(
f
"  Test:  index=
{
test_index
}
"
)
Fold 0:
Train: index=[0 1 2 3 4 5]
Test:  index=[6 7]
Fold 1:
Train: index=[0 1 2 3 4 5 6 7]
Test:  index=[8 9]
Fold 2:
Train: index=[0 1 2 3 4 5 6 7 8 9]
Test:  index=[10 11]
>>>
# Add in a 2 period gap
>>>
tscv
=
TimeSeriesSplit
(
n_splits
=
3
,
test_size
=
2
,
gap
=
2
)
>>>
for
i
,
(
train_index
,
test_index
)
in
enumerate
(
tscv
.
split
(
X
)):
...
print
(
f
"Fold
{
i
}
:"
)
...
print
(
f
"  Train: index=
{
train_index
}
"
)
...
print
(
f
"  Test:  index=
{
test_index
}
"
)
Fold 0:
Train: index=[0 1 2 3]
Test:  index=[6 7]
Fold 1:
Train: index=[0 1 2 3 4 5]
Test:  index=[8 9]
Fold 2:
Train: index=[0 1 2 3 4 5 6 7]
Test:  index=[10 11]
For a more extended example see
Time-related feature engineering
.
get_metadata_routing
(
)
[source]
#
Get metadata routing of this object.
Please check
User Guide
on how the routing
mechanism works.
Returns
:
routing
MetadataRequest
A
MetadataRequest
encapsulating
routing information.
get_n_splits
(
X
=
None
,
y
=
None
,
groups
=
None
)
[source]
#
Returns the number of splitting iterations as set with the
n_splits
param
when instantiating the cross-validator.
Parameters
:
X
array-like of shape (n_samples, n_features), default=None
Always ignored, exists for API compatibility.
y
array-like of shape (n_samples,), default=None
Always ignored, exists for API compatibility.
groups
array-like of shape (n_samples,), default=None
Always ignored, exists for API compatibility.
Returns
:
n_splits
int
Returns the number of splitting iterations in the cross-validator.
split
(
X
,
y
=
None
,
groups
=
None
)
[source]
#
Generate indices to split data into training and test set.
Parameters
:
X
array-like of shape (n_samples, n_features)
Training data, where
n_samples
is the number of samples
and
n_features
is the number of features.
y
array-like of shape (n_samples,), default=None
Always ignored, exists for API compatibility.
groups
array-like of shape (n_samples,), default=None
Always ignored, exists for API compatibility.
Yields
:
train
ndarray
The training set indices for that split.
test
ndarray
The testing set indices for that split.
Gallery examples
#
Time-related feature engineering
Time-related feature engineering
Lagged features for time series forecasting
Lagged features for time series forecasting
Features in Histogram Gradient Boosting Trees
Features in Histogram Gradient Boosting Trees
L1-based models for Sparse Signals
L1-based models for Sparse Signals
Visualizing cross-validation behavior in scikit-learn
Visualizing cross-validation behavior in scikit-learn
On this page
scikit-learn is
financially supported
by Probabl and other
        institutions.
Enterprise-grade solutions and services