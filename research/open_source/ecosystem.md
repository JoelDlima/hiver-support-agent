# Open-Source Ecosystem — AppleSupport Agent (CPU-only, <15min repro)
**Agent 7 — OPEN-SOURCE ECOSYSTEM | Date: 2026-09-10 | Scope: C:\Hiver**
**Constraints:** Python 3.12, CPU-only, no GPU servers, no K8s, no managed vector DB. Full train→serve→demo must finish in <15 min on a laptop.

## 1. Web research (10 queries, Sep 2026)

| # | Query | Key finding for AppleSupport |
|---|-------|------------------------------|
| 1 | scikit-learn TF-IDF+LogReg text classification 2026 best practice | `Pipeline([TfidfVectorizer, LogisticRegression])` remains the standard sparse-text baseline. Use `solver=lbfgs`, `class_weight=balanced` if skewed, `max_iter=1000`. Handles sparse matrices natively. Ref: scikit-learn 1.9 docs, 20-newsgroups example. |
| 2 | sentence-transformers MiniLM all-MiniLM-L6-v2 CPU inference 2026 | `all-MiniLM-L6-v2`: 384-dim, ~90 MB, ~750 q/s on CPU, 5× faster than mpnet with good quality. CPU-friendly via PyTorch / ONNX / OpenVINO backends. Apache-2.0. |
| 3 | FAISS-cpu vs sklearn NN small dataset 2026 | FAISS wins at 100M+ vectors / strict p95. For <100k threads (our case), `sklearn.neighbors.NearestNeighbors` (ball_tree/brute, cosine) is sufficient, zero extra infra. `faiss-cpu` (PyPI, C++/BLAS only) is the optional step-up, still CPU-only. |
| 4 | FastAPI CPU-only text classification serving best practice 2026 | Serve sklearn (sync `def` endpoints — FastAPI runs them in threadpool), load model once at startup, Pydantic schemas, `uvicorn` single process. Avoid `async` for CPU-bound predict. |
| 5 | Streamlit vs Gradio demo UI 2026 | Gradio = fastest ML-function demo + auto API + `ChatInterface`; Streamlit = better for dashboards/dataframes/layout. Either is <5 min. Recommend **Streamlit primary** (thread triage dashboard), Gradio optional. CLI fallback if UI install fails. |
| 6 | pytest ML testing 2026 | `tests/` outside `src/`, `conftest.py` fixtures, `--strict-markers`, `parametrize`, `Arrange-Act-Assert`. `pytest` + `pytest-cov` standard. |
| 7 | SQLite threads index metadata storage 2026 | Python stdlib `sqlite3`, zero-install. One connection per thread (`check_same_thread=False` + lock, or per-thread connect), `WAL` mode, `CREATE INDEX` on thread/product/label cols. GIL released during SQLite C calls. |
| 8 | joblib vs pickle sklearn persistence 2026 | sklearn docs: `joblib.dump/load` preferred for estimators with NumPy arrays (efficient, memmap). Both are pickle-based — never load untrusted files. `skops` only if untrusted sharing needed. |
| 9 | Python 3.12 scikit-learn pandas CPU-only install 2026 | Python ≥3.11 required for sklearn 1.9; Python 3.12 has full win_amd64/arm64 + manylinux wheels for numpy/scipy/pandas/sklearn. CPU-only wheels install in ~1–2 min. CSC Mar-2026 ref env: py3.12 + sklearn 1.8.0 + pandas 2.3.3 + scipy 1.17.1. |
| 10 | pandas preprocessing + sklearn Pipeline 2026 | `pandas` for CSV ingest/clean/split; hand homogeneous numeric/sparse arrays to sklearn via `Pipeline` / `ColumnTransformer`; `set_output(transform="pandas")` for debuggability. Keep text path as `TfidfVectorizer` inside the Pipeline to prevent leakage. |

## 2. Recommended minimal stack (pinned, CPU-only)

**Runtime:** Python 3.12.x (verified 3.12.10 on this box).

**Core (required, <5 min install from wheels):**
- `numpy==1.26.4`, `scipy==1.14.1`, `pandas==2.2.3`
- `scikit-learn==1.7.1` — `TfidfVectorizer + LogisticRegression` Pipeline (primary classifier + `NearestNeighbors` retrieval baseline)
- `joblib==1.4.2` — Pipeline persistence (`models/*.joblib`)

**Serving + demo:**
- `fastapi==0.115.12` + `uvicorn[standard]==0.34.0` — `/predict`, `/similar`, `/health` (sync endpoints)
- `streamlit==1.41.1` — triage demo UI (fallback: CLI `python -m src.predict "text"`)
- `httpx==0.28.1`, `python-multipart==0.0.20` — API testing / forms

**Storage (zero-install):**
- SQLite via stdlib `sqlite3` — `data/threads.db` (threads, labels, embeddings pointer/index via `joblib`/npy, FTS optional)

**Testing:**
- `pytest==8.3.5` (+ optional `pytest-cov`)

**Optional (offline-tolerant, install only if network/time allows):**
- `sentence-transformers==3.3.1` + CPU-only `torch` (`--extra-index-url https://download.pytorch.org/whl/cpu`) — `all-MiniLM-L6-v2` embeddings. **Fallback if offline: TF-IDF only.**
- `faiss-cpu==1.10.0` — only if >50k vectors or sklearn NN latency proves too high. Default: `sklearn.neighbors.NearestNeighbors`.

See `C:\Hiver\requirements.txt` (core pinned; optional section commented).

## 3. What was rejected (and why)

| Rejected | Reason |
|----------|--------|
| Kubernetes / Docker-first deploy | Overkill for <15 min laptop repro; `uvicorn` single-process suffices. |
| Managed vector DB (Pinecone/Weaviate/Qdrant-cloud, ES) | External service, auth, cost, network. SQLite + sklearn NN / optional faiss-cpu covers scale. |
| GPU servers / `faiss-gpu` / CUDA torch | Violates CPU-only constraint; 10–50× install size/time. Use `faiss-cpu` + torch CPU index only. |
| Full LLM fine-tuning stack (transformers-train, DeepSpeed, vLLM) | >15 min, GPU-bound. MiniLM inference-only is the ceiling; TF-IDF+LogReg is the default. |
| Gradio as primary (kept optional) | Fine tool, but Streamlit fits thread-triage dashboard better; keep one UI to minimize deps. |
| pandas 3.x / sklearn 1.9.0 / fastapi 0.141 / streamlit 1.63 as pins | Bleeding-edge (mid-2026); choose 2025-H2 stable pins with universal py3.12 wheels for guaranteed <15 min repro. Bump later deliberately. |

## 4. <15 min repro plan

1. `py -3.12 -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt` (~2–5 min, wheels only)
2. `python scripts\make_toy_threads.py` → `data/threads.csv` (+ load into SQLite)
3. `python -m src.train` → `models/tfidf_logreg.joblib` (~1 min)
4. `pytest -q` (~30 s) → `uvicorn src.api:app --port 8000` → `streamlit run frontend/app.py`
5. Offline? Skip optional section — TF-IDF path has zero HF/torch dependency.

## 5. Sources (representative)
- scikit-learn docs: `LogisticRegression`, `NearestNeighbors`, `Pipeline`, 20-newsgroups + grid-search-text examples; `model_persistence.rst` (joblib); install matrix (py≥3.11, win_amd64 cp312 wheels for 1.9.0).
- sentence-transformers docs: pretrained models table (MiniLM 18k/750 q/s GPU/CPU), efficiency (PyTorch/ONNX/OpenVINO backends); HF `all-MiniLM-L6-v2` card (384-dim, Apache-2.0).
- faiss: `faiss-cpu` PyPI (BLAS-only, optional GPU via CUDA), GPU-vs-CPU wiki, 10M-vector 2026 benchmark; Suhas Bhairav FAISS-vs-Annoy (FAISS for 100M+, Annoy/prototype for CPU-small).
- FastAPI: best-practices repo, issues #1679/#5969 (sync endpoints for CPU-bound ML, threadpool/processpool guidance).
- Streamlit vs Gradio 2026: markaicode, evidence.dev, pynions, alijabbary, scored.tools (Gradio=ML demo/ChatInterface, Streamlit=dashboard).
- pytest: pytest docs good-practices, qaskills 2026 (src layout, strict-markers, conftest), scientific-python guide.
- SQLite: sqlite.org threading modes, Python `sqlite3` docs (`check_same_thread`, per-thread connections), index tutorial.
- joblib persistence docs + pythontutorials joblib-vs-pickle; sklearn `model_persistence.rst` (skops for untrusted).
- Python 3.12 env evidence: CSC python-data 3.12 (sklearn 1.8.0/pandas 2.3.3, Mar 2026), `pip index versions` verified pins 2026-09-10.
