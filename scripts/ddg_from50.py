"""Resume DDG from #50 onwards (1-based). Incremental save, slow, UA rotation. Writes inside the repo root only."""
import re, time, random
from pathlib import Path
from datetime import date
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import html as ihtml

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "research" / "ddg_120_results.md"
LOG = ROOT / "docs" / "research_log.md"
TODAY = date.today().isoformat()

# Full 120 list (same as ddg_120.py) — we resume at index 49 (query #50)
QUERIES = [
("T1-problem", "AppleSupport Twitter common issues iOS 11 battery"),
("T1-problem", "Twitter customer support intent taxonomy categories"),
("T1-problem", "AppleSupport DM triage workflow send DM look into"),
("T1-problem", "customer support escalation policy auto handle vs human"),
("T1-problem", "iPhone X launch support issues November 2017"),
("T1-problem", "iOS 11 autocorrect bug I A box support complaints"),
("T1-problem", "Twitter support response time benchmark median minutes"),
("T1-problem", "Apple Genius Bar appointment workflow checkcoverage"),
("T1-problem", "customer support containment vs resolution metric pitfall"),
("T1-problem", "Twitter thread conversation intent drift message level"),
("T1-problem", "Apple ID locked out activation lock support flow"),
("T1-problem", "non-English customer support handling policy escalate"),
("T2-competitors", "customer support on twitter github AppleSupport bot"),
("T2-competitors", "Intercom Fin AI resolution rate hallucination rate"),
("T2-competitors", "Zendesk AI support agent architecture retrieval"),
("T2-competitors", "LangGraph customer support multi-agent github"),
("T2-competitors", "Twitter support RAG chatbot FAISS GPT-4 precision"),
("T2-competitors", "tweet intent classifier DistilBERT github"),
("T2-competitors", "support tweet classifier out-of-scope recall collapse"),
("T2-competitors", "Ada support chatbot grounding citations validation"),
("T2-competitors", "Decagon AI support agent evaluation metrics"),
("T2-competitors", "Sierra AI customer support accuracy benchmark"),
("T2-competitors", "Cresta support handoff packet warm transfer"),
("T2-competitors", "Forethought support triage escalation confidence"),
("T3-models", "DistilBERT tweet classification accuracy benchmark"),
("T3-models", "DeBERTa-v3-small text classification license MIT"),
("T3-models", "all-MiniLM-L6-v2 embedding license dimensions 384"),
("T3-models", "e5-small-v2 vs MiniLM MTEB score"),
("T3-models", "bge-reranker-base vs v2-m3 RAG rerank"),
("T3-models", "gpt-4o-mini pricing structured output json_schema 2026"),
("T3-models", "Claude Haiku pricing latency 2026 Anthropic"),
("T3-models", "Llama 3.1 8B license commercial use Meta"),
("T3-models", "Mistral 7B license Apache 2.0"),
("T3-models", "Gemma 2 terms of use license Google"),
("T3-models", "TF-IDF LogisticRegression tweet baseline accuracy"),
("T3-models", "SetFit few-shot intent classification Banking77 8 shots"),
("T4-retrieval", "BM25 vs dense retrieval short tweets benchmark"),
("T4-retrieval", "hybrid search RRF reciprocal rank fusion 2025"),
("T4-retrieval", "FAISS latest release version 2026 Facebook"),
("T4-retrieval", "Chroma vector database release 2026 status"),
("T4-retrieval", "LanceDB version status 2026"),
("T4-retrieval", "pgvector vs FAISS small corpus 100k docs"),
("T4-retrieval", "Elasticsearch dense vector hybrid search status"),
("T4-retrieval", "tweet chunking RAG single tweet atomic chunk"),
("T4-retrieval", "query expansion HyDE retrieval improvement"),
("T4-retrieval", "cross-encoder reranking RAG precision gain"),
("T4-retrieval", "RAGAS faithfulness correctness metric definition"),
("T4-retrieval", "recall at k vs answer correctness RAG evaluation"),
("T5-orchestration", "LangChain LangGraph v1.0 status 2026"),
("T5-orchestration", "LlamaIndex workflows status 2026"),
("T5-orchestration", "PydanticAI version status 2026"),
("T5-orchestration", "OpenAI Agents SDK structured output status"),
("T5-orchestration", "CrewAI production limitations scaling"),
("T5-orchestration", "Microsoft Agent Framework GA 2026"),
("T5-orchestration", "Google ADK agent development kit version"),
("T5-orchestration", "DSPy GEPA prompt optimization status"),
("T5-orchestration", "deterministic workflow vs AI agent reliability Anthropic"),
("T5-orchestration", "MCP model context protocol version 2026"),
("T5-orchestration", "Pydantic structured output validation LLM JSON schema"),
("T5-orchestration", "function calling tool use error compounding multi-step"),
("T6-data", "thoughtvector customer-support-on-twitter dataset columns license"),
("T6-data", "AppleSupport reply volume Twitter dataset count"),
("T6-data", "Twitter text preprocessing URL mention emoji hashtag"),
("T6-data", "duplicate detection canned responses customer support"),
("T6-data", "thread reconstruction response_tweet_id in_response_to"),
("T6-data", "time split vs random split temporal leakage ML"),
("T6-data", "class imbalance intent classification handling weights"),
("T6-data", "Banking77 dataset 77 intents train test split"),
("T6-data", "weak supervision keyword labeling noise accuracy"),
("T6-data", "data quality missing values duplicates outliers report"),
("T6-data", "iOS 11 2017 support era cutoff iPhone 8"),
("T6-data", "synthetic PII redaction evaluation data privacy"),
("T7-opensource", "scikit-learn LogisticRegression multi_class removed version"),
("T7-opensource", "FastAPI stateless scaling workers uvicorn throughput"),
("T7-opensource", "Streamlit FastAPI demo integration requests"),
("T7-opensource", "SQLite WAL concurrent read limit scaling"),
("T7-opensource", "joblib model persistence serving sklearn"),
("T7-opensource", "pytest FastAPI TestClient example"),
("T7-opensource", "sentence-transformers MiniLM CPU offline fallback"),
("T7-opensource", "faiss-cpu vs sklearn NearestNeighbors 100k latency"),
("T7-opensource", "slowapi rate limiting FastAPI decorator"),
("T7-opensource", "httpx async testing FastAPI client"),
("T7-opensource", "Docker python slim non-root HEALTHCHECK best practice"),
("T7-opensource", "LRU cache per worker hit rate in-memory"),
("T8-academic", "Banking77 BERT accuracy SOTA benchmark"),
("T8-academic", "few-shot intent classification SetFit 8 shots accuracy"),
("T8-academic", "retrieve exemplars few-shot RAG cost accuracy Loukas"),
("T8-academic", "twitter-roberta emoji hashtag handling preprocessing"),
("T8-academic", "knowledge graph RAG MRR improvement faithfulness"),
("T8-academic", "ARES RAG evaluation thresholds calibration"),
("T8-academic", "LLM as judge bias position verbosity length"),
("T8-academic", "Cohen kappa vs correlation judge agreement metric"),
("T8-academic", "CODS COMAD message level intent drift dialogue"),
("T8-academic", "FRANQ factual vs faithful distinction RAG"),
("T8-academic", "Evidence Override retrieval failure generation ignores context"),
("T8-academic", "Papers With Code intent classification leaderboard Banking77"),
("T9-evalsec", "intent classification macro F1 per intent confusion matrix sklearn"),
("T9-evalsec", "escalation precision recall threshold tuning support"),
("T9-evalsec", "BLEU ROUGE BERTScore support reply correlation factuality"),
("T9-evalsec", "LLM judge rubric groundedness actionability brand voice"),
("T9-evalsec", "prompt injection support chatbot attack success rate"),
("T9-evalsec", "PII redaction pre-egress evaluation data synthetic"),
("T9-evalsec", "OWASP LLM Top 10 prompt injection 2025"),
("T9-evalsec", "adversarial testing empty huge malformed input chatbot"),
("T9-evalsec", "judge human agreement weighted kappa 60 samples"),
("T9-evalsec", "safety fail recall account security customer support"),
("T9-evalsec", "paraphrase consistency evaluation chatbot robustness"),
("T9-evalsec", "jailbreak refusal rate frozen test set support"),
("T10-production", "FastAPI workers cores throughput benchmark uvicorn"),
("T10-production", "SQLite FTS5 read-only scaling limit"),
("T10-production", "Docker compose replicas load balancing FastAPI"),
("T10-production", "structured logging request ID FastAPI middleware"),
("T10-production", "rate limiting 30 per minute IP FastAPI slowapi"),
("T10-production", "small model vs LLM API cost per request 2026"),
("T10-production", "CPU inference latency p50 p95 measurement numpy percentile"),
("T10-production", "ANN index FAISS annoy scaling trigger threshold"),
("T10-production", "Redis cache vs in-memory LRU per worker FastAPI"),
("T10-production", "health check ready check Kubernetes probe FastAPI"),
("T10-production", "model routing cache hit latency optimization"),
("T10-production", "support agent cost 100 1000 10000 users estimate hosting"),
]

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]
TAG_RE = re.compile(r"<[^>]+>")
A_RE = re.compile(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)
LITE_RE = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)

def clean(s):
    import html as H
    return H.unescape(TAG_RE.sub("", s or "")).strip()[:220]

def ddg(q):
    urls = [f"https://lite.duckduckgo.com/lite/?q={quote_plus(q)}",
            f"https://duckduckgo.com/html/?q={quote_plus(q)}"]
    for u in urls:
        try:
            req = Request(u, headers={"User-Agent": random.choice(UAS)})
            with urlopen(req, timeout=25) as r:
                html = r.read().decode("utf-8", errors="ignore")
            if "challenge" in html.lower() and len(html) < 9000:
                continue
            m = A_RE.findall(html) or LITE_RE.findall(html)
            res = []
            for href, title in m:
                t = clean(title)
                if not t or "duckduckgo" in href.lower() or len(t) < 15:
                    continue
                if href.startswith("//"):
                    href = "https:" + href
                res.append((t, href[:180]))
                if len(res) >= 5:
                    break
            if res:
                return "ok", res
        except Exception:
            continue
    return "challenged_or_error", []

def main(start=50):
    assert len(QUERIES) == 120
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    # header once
    if not OUT_MD.exists():
        OUT_MD.write_text(f"# 120 DuckDuckGo searches — {TODAY}\n\nResumed run: #1-49 done earlier (ok), this file continues #50-120 with slow pacing.\n\n", encoding="utf-8")
    logf = open(LOG, "a", encoding="utf-8")
    logf.write(f"\n## {TODAY} — DDG resume from #{start} (slow, UA rotation, incremental)\n")
    ok = chal = 0
    for idx in range(start - 1, 120):
        n = idx + 1
        track, q = QUERIES[idx]
        status, res = ddg(q)
        if status == "ok":
            ok += 1
            top = "; ".join(t for t, _ in res[:3])[:300]
        else:
            chal += 1
            top = "DDG challenge/empty — cross-check via websearch; no invented finding"
        print(f"[{n}/120] {track} :: {q[:65]} -> {status} ({len(res)})", flush=True)
        with open(OUT_MD, "a", encoding="utf-8") as f:
            f.write(f"## {n}. [{track}] {q}\n- status: {status}\n\n")
            for t, h in res[:5]:
                f.write(f"- {t} — {h}\n")
            if not res:
                f.write("- (no DDG content captured; see websearch cross-checks)\n")
            f.write("\n")
        logf.write(f"- DATE: {TODAY} / QUERY: {q} / SOURCE: DuckDuckGo lite/html ({status}) / KEY FINDING: {top} / RELEVANCE: {track} / IMPACT: status={status}\n")
        logf.flush()
        time.sleep(4 + random.random() * 3)
    logf.close()
    print(f"RESUME DONE ok={ok} challenged={chal}")

if __name__ == "__main__":
    main(start=50)
