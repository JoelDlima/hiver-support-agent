---
title: PolyAI/banking77 · Datasets at Hugging Face
id: polyaibanking77-datasets-at-hugging-face
tags:
- hiver-support-agent-audit-6d951f
created: '2026-09-15T02:30:32.149702Z'
source: https://huggingface.co/datasets/PolyAI/banking77
source_domain: huggingface.co
fetched_at: '2026-09-15T02:30:32.148700Z'
fetch_provider: builtin
status: draft
type: note
tier: unknown
content_type: unknown
deprecated: false
---

PolyAI/banking77 · Datasets at Hugging Face
Dataset Viewer
The dataset viewer is not available for this dataset.
Cannot get the config names for the dataset.
Error code:   ConfigNamesError
Exception:    RuntimeError
Message:      Dataset scripts are no longer supported, but found banking77.py
Traceback:    Traceback (most recent call last):
                File "/src/services/worker/src/worker/job_runners/dataset/config_names.py", line 67, in compute_config_names_response
                  config_names = get_dataset_config_names(
                      path=dataset,
                      token=hf_token,
                  )
                File "/usr/local/lib/python3.14/site-packages/datasets/inspect.py", line 161, in get_dataset_config_names
                  dataset_module = dataset_module_factory(
                      path,
                  ...<4 lines>...
                      **download_kwargs,
                  )
                File "/usr/local/lib/python3.14/site-packages/datasets/load.py", line 1217, in dataset_module_factory
                  raise e1 from None
                File "/usr/local/lib/python3.14/site-packages/datasets/load.py", line 1177, in dataset_module_factory
                  raise RuntimeError(f"Dataset scripts are no longer supported, but found {filename}")
              RuntimeError: Dataset scripts are no longer supported, but found banking77.py
Need help to make the dataset viewer work? Make sure to review
how to configure the dataset viewer
, and
open a discussion
for direct support.
Dataset Card for BANKING77
Dataset Summary
Dataset composed of online banking queries annotated with their corresponding intents.
BANKING77 dataset provides a very fine-grained set of intents in a banking domain.
It comprises 13,083 customer service queries labeled with 77 intents. 
It focuses on fine-grained single-domain intent detection.
Supported Tasks and Leaderboards
Intent classification, intent detection
Languages
English
Dataset Structure
Data Instances
An example of 'train' looks as follows:
{
  'label': 11, # integer label corresponding to "card_arrival" intent
  'text': 'I am still waiting on my card?'
}
Data Fields
text
: a string feature.
label
: One of classification labels (0-76) corresponding to unique intents.
Intent names are mapped to
label
in the following way:
label
intent (category)
0
activate_my_card
1
age_limit
2
apple_pay_or_google_pay
3
atm_support
4
automatic_top_up
5
balance_not_updated_after_bank_transfer
6
balance_not_updated_after_cheque_or_cash_deposit
7
beneficiary_not_allowed
8
cancel_transfer
9
card_about_to_expire
10
card_acceptance
11
card_arrival
12
card_delivery_estimate
13
card_linking
14
card_not_working
15
card_payment_fee_charged
16
card_payment_not_recognised
17
card_payment_wrong_exchange_rate
18
card_swallowed
19
cash_withdrawal_charge
20
cash_withdrawal_not_recognised
21
change_pin
22
compromised_card
23
contactless_not_working
24
country_support
25
declined_card_payment
26
declined_cash_withdrawal
27
declined_transfer
28
direct_debit_payment_not_recognised
29
disposable_card_limits
30
edit_personal_details
31
exchange_charge
32
exchange_rate
33
exchange_via_app
34
extra_charge_on_statement
35
failed_transfer
36
fiat_currency_support
37
get_disposable_virtual_card
38
get_physical_card
39
getting_spare_card
40
getting_virtual_card
41
lost_or_stolen_card
42
lost_or_stolen_phone
43
order_physical_card
44
passcode_forgotten
45
pending_card_payment
46
pending_cash_withdrawal
47
pending_top_up
48
pending_transfer
49
pin_blocked
50
receiving_money
51
Refund_not_showing_up
52
request_refund
53
reverted_card_payment?
54
supported_cards_and_currencies
55
terminate_account
56
top_up_by_bank_transfer_charge
57
top_up_by_card_charge
58
top_up_by_cash_or_cheque
59
top_up_failed
60
top_up_limits
61
top_up_reverted
62
topping_up_by_card
63
transaction_charged_twice
64
transfer_fee_charged
65
transfer_into_account
66
transfer_not_received_by_recipient
67
transfer_timing
68
unable_to_verify_identity
69
verify_my_identity
70
verify_source_of_funds
71
verify_top_up
72
virtual_card_not_working
73
visa_or_mastercard
74
why_verify_identity
75
wrong_amount_of_cash_received
76
wrong_exchange_rate_for_cash_withdrawal
Data Splits
Dataset statistics
Train
Test
Number of examples
10 003
3 080
Average character length
59.5
54.2
Number of intents
77
77
Number of domains
1
1
Dataset Creation
Curation Rationale
Previous intent detection datasets such as Web Apps, Ask Ubuntu, the Chatbot Corpus or SNIPS are limited to small number of classes (<10), which oversimplifies the intent detection task and does not emulate the true environment of commercial systems. Although there exist large scale
multi-domain
datasets (
HWU64
and
CLINC150
), the examples per each domain may not sufficiently capture the full complexity of each domain as encountered "in the wild". This dataset tries to fill the gap and provides a very fine-grained set of intents in a
single-domain
i.e.
banking
. Its focus on fine-grained single-domain intent detection makes it complementary to the other two multi-domain datasets.
Source Data
Initial Data Collection and Normalization
[More Information Needed]
Who are the source language producers?
[More Information Needed]
Annotations
Annotation process
The dataset does not contain any additional annotations.
Who are the annotators?
[N/A]
Personal and Sensitive Information
[N/A]
Considerations for Using the Data
Social Impact of Dataset
The purpose of this dataset it to help develop better intent detection systems.
Any comprehensive intent detection evaluation should involve both coarser-grained multi-domain datasets and a fine-grained single-domain dataset such as BANKING77.
Discussion of Biases
[More Information Needed]
Other Known Limitations
[More Information Needed]
Additional Information
Dataset Curators
PolyAI
Licensing Information
Creative Commons Attribution 4.0 International
Citation Information
@inproceedings{Casanueva2020,
    author      = {I{\~{n}}igo Casanueva and Tadas Temcinas and Daniela Gerz and Matthew Henderson and Ivan Vulic},
    title       = {Efficient Intent Detection with Dual Sentence Encoders},
    year        = {2020},
    month       = {mar},
    note        = {Data available at https://github.com/PolyAI-LDN/task-specific-datasets},
    url         = {https://arxiv.org/abs/2003.04807},
    booktitle   = {Proceedings of the 2nd Workshop on NLP for ConvAI - ACL 2020}
}
Contributions
Thanks to
@dkajtoch
for adding this dataset.
Copy to bucket
new
Downloads last month
12,933
Homepage:
Github
Repository:
Github
Paper:
ArXiv
Leaderboard:
Leaderboard:
Point of Contact:
Point of Contact:
Total file size:
24.4 kB
Models trained or fine-tuned on
PolyAI/banking77
Zero-Shot Classification
•
0.2B
•
Updated
Aug 13, 2024
•
21.8k
•
•
134
Zero-Shot Classification
•
0.1B
•
Updated
Aug 28, 2024
•
10k
•
•
51
Zero-Shot Classification
•
0.2B
•
Updated
Oct 4, 2024
•
2.67k
•
•
27
Zero-Shot Classification
•
Updated
Jul 4, 2024
•
77
•
3
Text Classification
•
0.1B
•
Updated
25 days ago
•
27
•
1
Text Classification
•
0.2B
•
Updated
25 days ago
•
26
Browse 26 models trained on this dataset
Spaces using
PolyAI/banking77
11
Paper for
PolyAI/banking77
Paper
•
2003.04807
•
Published
Mar 10, 2020
•
2