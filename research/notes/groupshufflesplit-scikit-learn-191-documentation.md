---
title: GroupShuffleSplit — scikit-learn 1.9.1 documentation
id: groupshufflesplit-scikit-learn-191-documentation
tags:
- hiver-support-agent-audit-6d951f
- locus-leakage-safe-temporal-split-vs-random-stratified-split
created: '2026-09-15T02:39:08.738075Z'
source: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html
source_domain: scikit-learn.org
fetched_at: '2026-09-15T02:39:08.738075Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

GroupShuffleSplit — scikit-learn 1.9.1 documentation
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
GroupShuffleSplit
#
class
sklearn.model_selection.
GroupShuffleSplit
(
n_splits
=
5
,
*
,
test_size
=
None
,
train_size
=
None
,
random_state
=
None
)
[source]
#
Shuffle-Group(s)-Out cross-validation iterator.
Provides randomized train/test indices to split data according to a
third-party provided group. This group information can be used to encode
arbitrary domain-specific groupings of the samples as integers.
For instance the groups could be the year of collection of the samples
and thus allow for cross-validation against time-based splits.
The difference between
LeavePGroupsOut
and
GroupShuffleSplit
is that
the former generates splits using all subsets of size
p
unique groups,
whereas
GroupShuffleSplit
generates a user-determined number of random
test splits, each with a user-determined fraction of unique groups.
For example, a less computationally intensive alternative to
LeavePGroupsOut(p=10)
would be
GroupShuffleSplit(test_size=10,
n_splits=100)
.
Contrary to other cross-validation strategies, the random splits
do not guarantee that test sets across all folds will be mutually exclusive,
and might include overlapping samples. However, this is still very likely for
sizeable datasets.
Note: The parameters
test_size
and
train_size
refer to groups, and
not to samples as in
ShuffleSplit
.
Read more in the
User Guide
.
For visualisation of cross-validation behaviour and
comparison between common scikit-learn split methods
refer to
Visualizing cross-validation behavior in scikit-learn
Parameters
:
n_splits
int, default=5
Number of re-shuffling & splitting iterations.
test_size
float, int, default=None
If float, should be between 0.0 and 1.0 and represent the proportion
of groups to include in the test split (rounded up). If int,
represents the absolute number of test groups. If None, the value is
set to the complement of the train size. If
train_size
is also None,
it will be set to 0.2.
train_size
float or int, default=None
If float, should be between 0.0 and 1.0 and represent the
proportion of the groups to include in the train split. If
int, represents the absolute number of train groups. If None,
the value is automatically set to the complement of the test size.
random_state
int, RandomState instance or None, default=None
Controls the randomness of the training and testing indices produced.
Pass an int for reproducible output across multiple function calls.
See
Glossary
.
See also
ShuffleSplit
Shuffles samples to create independent test/train sets.
LeavePGroupsOut
Train set leaves out all possible subsets of
p
groups.
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
GroupShuffleSplit
>>>
X
=
np
.
ones
(
shape
=
(
8
,
2
))
>>>
y
=
np
.
ones
(
shape
=
(
8
,
1
))
>>>
groups
=
np
.
array
([
1
,
1
,
2
,
2
,
2
,
3
,
3
,
3
])
>>>
print
(
groups
.
shape
)
(8,)
>>>
gss
=
GroupShuffleSplit
(
n_splits
=
2
,
train_size
=
.7
,
random_state
=
42
)
>>>
gss
.
get_n_splits
()
2
>>>
print
(
gss
)
GroupShuffleSplit(n_splits=2, random_state=42, test_size=None, train_size=0.7)
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
gss
.
split
(
X
,
y
,
groups
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
, group=
{
groups
[
train_index
]
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
, group=
{
groups
[
test_index
]
}
"
)
Fold 0:
Train: index=[2 3 4 5 6 7], group=[2 2 2 3 3 3]
Test:  index=[0 1], group=[1 1]
Fold 1:
Train: index=[0 1 5 6 7], group=[1 1 3 3 3]
Test:  index=[2 3 4], group=[2 2 2]
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
set_split_request
(
*
,
groups
:
bool
|
None
|
str
=
'$UNCHANGED$'
)
→
GroupShuffleSplit
[source]
#
Configure whether metadata should be requested to be passed to the
split
method.
Note that this method is only relevant when this estimator is used as a
sub-estimator within a
meta-estimator
and metadata routing is enabled
with
enable_metadata_routing=True
(see
sklearn.set_config
).
Please check the
User Guide
on how the routing
mechanism works.
The options for each parameter are:
True
: metadata is requested, and passed to
split
if provided. The request is ignored if metadata is not provided.
False
: metadata is not requested and the meta-estimator will not pass it to
split
.
None
: metadata is not requested, and the meta-estimator will raise an error if the user provides it.
str
: metadata should be passed to the meta-estimator with this given alias instead of the original name.
The default (
sklearn.utils.metadata_routing.UNCHANGED
) retains the
existing request. This allows you to change the request for some
parameters and not others.
Added in version 1.3.
Parameters
:
groups
str, True, False, or None,                     default=sklearn.utils.metadata_routing.UNCHANGED
Metadata routing for
groups
parameter in
split
.
Returns
:
self
object
The updated object.
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
The target variable for supervised learning problems.
groups
array-like of shape (n_samples,)
Group labels for the samples used while splitting the dataset into
train/test set.
Yields
:
train
ndarray
The training set indices for that split.
test
ndarray
The testing set indices for that split.
Notes
Randomized CV splitters may return different results for each call of
split. You can make the results identical by setting
random_state
to an integer.
Gallery examples
#
Visualizing cross-validation behavior in scikit-learn
Visualizing cross-validation behavior in scikit-learn
On this page
scikit-learn is
financially supported
by Probabl and other
        institutions.
Enterprise-grade solutions and services