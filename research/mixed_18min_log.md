
## 17:46:03 [normal-search] thoughtvector customer-support-on-twitter dataset columns license
- finding: Kaggle 3M tweets cols tweet_id author_id inbound created_at text response_ids; PII masked; HF mirrors 945k/794k; cc-by-nc-sa-4.0

## 17:46:54 [ddg-firefoxUA:challenged_or_error] AppleSupport reply volume Twitter dataset count
- (blocked; fallback to normal search later)

## 17:47:01 [normal-search] Twitter text preprocessing URL mention emoji hashtag
- finding: tweet-preprocessor OPT.URL MENTION HASHTAG EMOJI; keep hashtag word drop symbol; URL to token; emoji 1624 list

## 17:47:29 [ddg-fetch-provider] duplicate detection canned responses customer support tweets
- finding: DDG html via provider transport-error (bot-block); fallback to normal search; no invented finding

## 17:48:11 [ddg-firefoxUA:challenged_or_error] duplicate detection canned responses customer support
- (blocked; fallback to normal search later)

## 17:48:18 [normal-search] thread reconstruction response_tweet_id in_response_to conversation_id
- finding: conversation_id + referenced_tweets chain; recursive CTE depth; voson tcn_threads; PHEME script

## 17:49:24 [ddg-firefoxUA:challenged_or_error] time split vs random split temporal leakage machine learning
- (blocked; fallback to normal search later)

## 17:49:31 [normal-search] time split vs random split temporal leakage
- finding: random inflates MCC 1.1-6.5x; strict temporal cutoff needed; Wild-Time 20pct drop OOD

## 17:50:38 [ddg-firefoxUA:challenged_or_error] class imbalance intent classification handling weights
- (blocked; fallback to normal search later)

## 17:50:43 [normal-search] class imbalance intent classification ROS vs cost-sensitive
- finding: ROS outperforms RUS in text; two-stage freeze-encoder retrain-classifier; SMOTE cost-of-transfer high-dim

## 17:51:46 [ddg-firefoxUA:challenged_or_error] Banking77 dataset 77 intents train test split
- (blocked; fallback to normal search later)

## 17:52:09 [normal-search] Banking77 13k 77 intents train 10003 test 3080
- finding: BERT 93.6 full 85 10-shot; overlapping labels; trimmed +4.5pct to 92.4; cc-by-4.0

## 17:53:12 [ddg-firefoxUA:challenged_or_error] weak supervision keyword labeling noise accuracy
- (blocked; fallback to normal search later)

## 17:53:18 [normal-search] weak supervision Snorkel labeling functions data programming
- finding: LFs noisy conflicting; generative model denoises; 2.8x faster 45.5pct gain; within 3.6pct of hand labels

## 17:54:21 [ddg-firefoxUA:challenged_or_error] scikit-learn LogisticRegression multi_class removed version
- (blocked; fallback to normal search later)

## 17:54:27 [normal-search] sklearn LogReg multi_class removed 1.8 penalty l1_ratio
- finding: issue 31781 PR 31795: deprecated 1.5 removed 1.8; penalty string deprecated 1.8

## 17:55:29 [ddg-firefoxUA:challenged_or_error] FastAPI stateless scaling workers uvicorn throughput
- (blocked; fallback to normal search later)

## 17:55:35 [normal-search] FastAPI uvicorn workers throughput def vs async threadpool
- finding: def runs in threadpool; workers=cores; Uvicorn HTTP1.1 +15pct vs Hypercorn; TechEmpower FastAPI top Python

## 17:56:32 [ddg-firefoxUA:challenged_or_error] Streamlit FastAPI demo integration requests
- (blocked; fallback to normal search later)

## 17:56:39 [normal-search] Streamlit FastAPI demo requests direct import
- finding: frontend/backend split; requests pattern; direct import avoids server for demo

## 17:57:36 [ddg-firefoxUA:challenged_or_error] SQLite WAL concurrent read limit scaling
- (blocked; fallback to normal search later)

## 17:58:00 [normal-search] SQLite WAL read concurrency checkpoint starvation
- finding: readers dont block writers; 1 writer; checkpoint at 1000 pages; starvation if long readers; same-host shm

## 17:58:06 [normal-search] Banking77 BERT 93.66 full 85.19 10-shot overlapping
- finding: Casanueva dual encoders; Ying 1428 label errors trimmed 92.4; prefix-tuning 82.76

## 17:59:17 [ddg-firefoxUA:challenged_or_error] LLM as judge bias position verbosity length
- (blocked; fallback to normal search later)

## 17:59:24 [normal-search] LLM judge position bias RS PC PF metrics
- finding: RS over 0.95 top judges; PC PF vary by task; verbosity weak; swap-consistency needed; kappa not correlation

## 18:00:29 [ddg-firefoxUA:challenged_or_error] prompt injection support chatbot attack success rate
- (blocked; fallback to normal search later)

## 18:00:37 [normal-search] prompt injection OWASP LLM01 direct indirect support chatbot
- finding: direct ignore-guidelines query-private-data; indirect hidden webpage exfil; RAG fine-tune dont fully mitigate; delimit + filter + HITL

## 18:01:43 [ddg-firefoxUA:challenged_or_error] OWASP LLM Top 10 prompt injection 2025
- (blocked; fallback to normal search later)
