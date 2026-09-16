---
title: 'GitHub - Vishesh062/customer-support-tweet-classifier: Multi-class text classifier
  for routing customer support tweets. TF-IDF baseline vs fine-tuned DistilBERT, compared
  on 1.5M tweets. Model on Hugging Face. · GitHub'
id: github-vishesh062customer-support-tweet-classifier-multi-class-text-classifier-f
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:48:21.208674Z'
source: https://github.com/Vishesh062/customer-support-tweet-classifier
source_domain: github.com
fetched_at: '2026-09-15T02:48:21.206673Z'
fetch_provider: builtin
status: draft
type: note
tier: ground_truth
content_type: code
deprecated: false
---

GitHub - Vishesh062/customer-support-tweet-classifier: Multi-class text classifier for routing customer support tweets. TF-IDF baseline vs fine-tuned DistilBERT, compared on 1.5M tweets. Model on Hugging Face. · GitHub
Skip to content
You signed in with another tab or window.
Reload
to refresh your session.
You signed out in another tab or window.
Reload
to refresh your session.
You switched accounts on another tab or window.
Reload
to refresh your session.
Dismiss alert
Vishesh062
/
customer-support-tweet-classifier
Public
Notifications
You must be signed in to change notification settings
Fork
0
Star
0
main
Branches
Tags
Go to file
Code
Open more actions menu
Latest commit
History
4 Commits
4 Commits
Folders and files
Name
Name
Last commit message
Last commit date
data
data
images
images
models
models
.gitignore
.gitignore
LICENSE
LICENSE
README.md
README.md
customer_support_classifier.ipynb
customer_support_classifier.ipynb
predict.py
predict.py
requirements.txt
requirements.txt
View all files
Repository files navigation
Customer Support Tweet Classifier
A multi-class text classifier that routes customer support tweets into seven categories (billing, technical, account, delivery, product, support, general). Trained and evaluated on 1.54M labelled tweets from the
Customer Support on Twitter
dataset.
Companion post:
A 1.9 MB Classifier Beat a 269 MB One. Sort Of.
Headline result
Model
Training data
Accuracy
Macro F1
Weighted F1
Size
Training
TF-IDF + Logistic Regression
1,230,274
98.2%
0.973
0.982
1.9 MB
3 min CPU
Fine-tuned DistilBERT
50,000
99.5%
0.991
0.994
269 MB
8 min GPU
DistilBERT wins on every class, but the margin is small (1.3 percentage points of accuracy). The interesting question isn't which model is more accurate — it's whether a 142× larger model is worth that gap in production.
The biggest improvements are on
billing
(+0.051 F1) and
technical
(+0.031 F1) — the exact categories the baseline struggles with most, because they share keywords with the dominant
general
class.
The problem
Brand support teams on Twitter receive thousands of tweets a day that need different routing. Billing complaints go to finance, technical issues to engineering, generic feedback to triage. Manual routing doesn't scale.
I trained two models, compared them properly, and dug into where each one fails.
Dataset
Customer Support on Twitter
, ~2.8M tweets between customers and brand support accounts (Apple, Spotify, Sprint, Verizon, and others). After filtering to inbound (customer) tweets only:
1,537,843 tweets
to label and train on.
The dataset doesn't ship with category labels. I generate them by keyword matching — one labelling function, used identically for both models, with documented ordering rules. The category distribution is heavily imbalanced:
general
is 45% of the data because it's the fallback bucket: anything not matching the keywords for the other six categories ends up here. This matters for interpretation — a model that learns to "predict general unless strong evidence otherwise" can get a misleadingly high accuracy.
Approach
Labels.
Define one function with seven keyword sets. Apply via vectorised
pandas.Series.str.contains
. Order-dependent: billing wins over support when both match, by design.
Baseline.
TF-IDF (20K features, bigrams included,
min_df=5
) into a Logistic Regression with
class_weight='balanced'
and
max_iter=1000
. Trained on the full 1.23M training set.
Advanced model.
Fine-tuned
distilbert-base-uncased
on a 50K stratified subset. Three epochs, learning rate 2e-5, early stopping on macro F1. The same labels and the same test set as the baseline — apples to apples.
Where DistilBERT actually helps
The baseline's biggest confusion patterns:
True class
Predicted as
Cases
billing
general
824
general
billing
559
general
technical
469
billing
support
330
technical
general
324
The actual tweets in these confusion cells explain a lot:
"Hello visa, I'd like to pay my bill. Do you accept apologies?"
— labelled billing (keyword "bill"), baseline predicted general. The sarcasm doesn't help, but a keyword classifier shouldn't be expected to catch it.
"Disgusting service, pathetic management, charging for no reason"
— labelled billing, baseline predicted general. Real billing complaint, language is general-purpose ranting.
"@sprintcare A tower has been down near my home for 2 weeks making my phone inoperable. Sprint doesn't care but expects me to pay my bill"
— about technical issues but ends with a billing mention. The label rule fired on "pay my bill," but the substance is technical.
These are exactly the cases DistilBERT handles better — tweets where the labelling keywords are present but the actual semantic intent is different.
Predictions on novel tweets
Both models agree on every example I tested:
Tweet
Both predicted
"Hey @CompanyX, I've been overcharged on my last bill"
billing (100%)
"Your app keeps crashing every time I try to open it"
technical (99.9%)
"I can't log into my account, the password reset email isn't coming through"
account (100% / 99.9%)
"Where is my package? It's been 2 weeks since I ordered"
delivery (100% / 99.9%)
"The product arrived broken. I want a replacement or refund"
billing (100%)
"Just wanted to say your customer service team has been amazing!"
support (96.2% / 99.9%)
"Is there a deal coming up for Black Friday?"
general (84.9% / 99.9%)
DistilBERT is consistently more confident, but the predictions match. For clean, on-topic tweets, the two models are interchangeable.
Which one would I actually deploy?
For most cases:
the baseline.
It's 1.9 MB, runs CPU-only in milliseconds, trains in three minutes, and gets 98.2% accuracy. The agreement with DistilBERT on real-looking tweets suggests the difference matters most on edge cases like the misclassified examples above.
DistilBERT is the right choice when:
You actually need to handle the edge cases (ambiguous billing/technical phrasing, sarcasm, mixed-intent tweets)
The 1.3-point gain is worth the operational cost (GPU inference or substantially slower CPU, 269 MB checkpoint, more complex serving)
You have downstream applications that benefit from the model's higher confidence calibration
This is the kind of decision a senior data scientist gets paid to make: not "which model is best on the leaderboard" but "which model is best for what we're building."
Known limitations
I'd raise these in an interview before someone else did.
The labels are synthetic.
The classifier is, fundamentally, a keyword detector with extra steps. Real-world deployment needs human-annotated training data — even 5,000 manually labelled examples would produce a more meaningful model than 1.54M keyword-derived ones.
The "general" bucket distorts everything.
It catches everything the keyword function doesn't classify, so it's the largest, most diverse class. Most misclassifications fall into it because that's where the base-rate prior lives.
No semantic understanding in the labels.
A tweet like "the delivery of my new account password isn't arriving" should arguably go to
account
, not
delivery
. The current pipeline can't reason about that.
Single train/test split.
I should have used cross-validation. The numbers above are probably stable but I haven't verified.
What I'd do differently in v2
The thing I actually did differently in this version (vs an earlier coursework attempt):
Defined the labelling function exactly once. The previous version had subtle keyword inconsistencies between baseline and DistilBERT — billing keywords differed by one word, so the two models were trained on slightly different labels. Caught and fixed.
Vectorised the labelling.
pandas.apply
row by row took several minutes;
str.contains
takes seconds.
Used
class_weight='balanced'
on Logistic Regression. The previous version didn't, which is why per-class F1 scores were uneven.
Trained DistilBERT on 50K examples instead of ~2,500. The earlier comparison wasn't fair.
If I were doing v3, I'd add:
Human-annotated labels for a held-out evaluation set, even just 1,000 tweets, to measure how well the synthetic labels match real intent
Hierarchical classification: first general-vs-specific, then specific-vs-specific. Removes the "general dumps everything" problem
Active learning loop: use the baseline to surface low-confidence predictions, manually label those, retrain
Running it
git clone https://github.com/Vishesh062/customer-support-tweet-classifier.git
cd
customer-support-tweet-classifier
pip install -r requirements.txt
The full dataset is ~600 MB and not committed. Download from
Kaggle
, unzip, and place
twcs.csv
in the
data/
folder. A 100-row
data/sample.csv
is included for sanity-checking the loading and labelling without downloading the full dataset.
The notebook (
customer_support_classifier.ipynb
) is designed to run end-to-end on Google Colab with a free T4 GPU. The DistilBERT cell needs the GPU; the baseline cells run on CPU.
Using the trained baseline directly
(without re-training):
python predict.py
"
I've been overcharged on my last bill
"
#
→ billing (100.0%)
python predict.py --top-3
"
Your service is slow and the app keeps crashing
"
#
→ technical    87.4%
#
→ support      9.1%
#
→ general      2.3%
python predict.py --distilbert
"
Where is my package?
"
#
→ delivery (99.9%)
If you'd rather embed the model in your own code:
import
pickle
with
open
(
"models/baseline.pkl"
,
"rb"
)
as
f
:
model
=
pickle
.
load
(
f
)
predictions
=
model
.
predict
([
"I've been overcharged on my last bill"
,
"Your app keeps crashing on startup"
,
])
# → ['billing', 'technical']
Trained DistilBERT model
The DistilBERT model is hosted on Hugging Face Hub at
Vishesh062/customer-support-tweet-classifier
(269 MB — too large for a Git repo). Load it directly:
from
transformers
import
AutoTokenizer
,
AutoModelForSequenceClassification
REPO
=
"Vishesh062/customer-support-tweet-classifier"
tokenizer
=
AutoTokenizer
.
from_pretrained
(
REPO
)
model
=
AutoModelForSequenceClassification
.
from_pretrained
(
REPO
)
The Hugging Face page has a complete inference example including label decoding.
Acknowledgements
Originally a coursework project at Macquarie University. Sourav Kumar Payal contributed to the data exploration and early labelling work. The model selection, analysis, and writeup above are mine.
License
MIT. See
LICENSE
.
About
Multi-class text classifier for routing customer support tweets. TF-IDF baseline vs fine-tuned DistilBERT, compared on 1.5M tweets. Model on Hugging Face.
Resources
Readme
MIT license
Activity
Stars
0
stars
Watchers
0
watching
Forks
0
forks
Report repository
Releases
Packages
Contributors
Languages
You can’t perform that action at this time.