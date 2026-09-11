"""Hiver support demo — VirginTrains primary, AppleSupport kept (no server needed, direct src.agent import)."""
import importlib
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, r"C:\Hiver")

import streamlit as st

from src.agent import AppleAgent
from src import brands as brands_mod

MAX_CHARS = 2000

BRAND_LABELS = {
    "virgin": "VirginTrains (primary)",
    "apple": "AppleSupport (v1 evidence)",
}

BRAND_PLACEHOLDERS = {
    "virgin": "e.g. my train from Euston was delayed 45 mins, how do I claim Delay Repay?",
    "apple": "e.g. my iphone battery drains fast after ios 11 update",
}

BRAND_EXAMPLES = {
    "virgin": "my train was delayed, I want to claim delay repay",
    "apple": "my iphone battery drains fast after ios 11 update",
}


def _brand_label(b: str) -> str:
    return BRAND_LABELS.get(b, b)


def _intents_for_brand(brand: str) -> list:
    try:
        mod_name = brands_mod.get_intent_module_name(brand)
        mod = importlib.import_module(mod_name)
        intents = list(getattr(mod, "INTENTS", []))
        if intents:
            return intents
    except Exception:
        pass
    return []


def _make_retriever_for_brand(brand: str):
    """Load per-brand TF-IDF index read-only; None on any failure (fail-closed)."""
    try:
        for index_dir in brands_mod.get_index_candidates(brand):
            try:
                p = Path(index_dir)
                vec_p = p / "tfidf_vectorizer.pkl"
                nn_p = p / "nn_index.pkl"
                ids_p = p / "doc_ids.csv"
                if not (vec_p.exists() and nn_p.exists() and ids_p.exists()):
                    continue
                import joblib
                import pandas as pd
                vec = joblib.load(vec_p)
                nn = joblib.load(nn_p)
                ids = pd.read_csv(ids_p)
                doc_ids = ids["tweet_id"].astype(str).tolist() if "tweet_id" in ids.columns else ids.iloc[:, -1].astype(str).tolist()
                kb_name = "virgin_kb.csv" if brand == "virgin" else "apple_kb.csv"
                kb_path = Path(r"C:\Hiver\data\processed") / kb_name
                lookup: dict = {}
                try:
                    if kb_path.exists():
                        kb = pd.read_csv(kb_path, usecols=["tweet_id", "text", "clean"])
                        lookup = {str(r.tweet_id): (r.text, r.clean) for r in kb.itertuples()}
                except Exception:
                    lookup = {}

                class _BrandRetriever:
                    def __init__(self, _vec, _nn, _doc_ids, _lookup):
                        self.vec = _vec
                        self.nn = _nn
                        self.doc_ids = _doc_ids
                        self.lookup = _lookup

                    def query(self, text: str, k: int = 5):
                        Xq = self.vec.transform([(text or "").lower()])
                        dist, idx = self.nn.kneighbors(Xq, n_neighbors=min(k, len(self.doc_ids)))
                        out = []
                        for d, j in zip(dist[0], idx[0]):
                            tid = self.doc_ids[j]
                            raw, clean = self.lookup.get(tid, ("", ""))
                            out.append({"tweet_id": tid, "distance": float(d),
                                        "score": float(1 - d), "text": raw, "clean": clean})
                        return out

                return _BrandRetriever(vec, nn, doc_ids, lookup)
            except Exception:
                continue
    except Exception:
        pass
    if brand == "apple":
        try:
            from src.retriever import Retriever
            return Retriever()
        except Exception:
            return None
    return None


st.set_page_config(page_title="Hiver support demo — VirginTrains primary", layout="centered")
st.title("Hiver — support demo (VirginTrains primary, Apple kept)")
st.caption("Brand-agnostic: classify → draft → escalate. Direct agent call (no server). Keyless default; Groq drafts fail-closed to template.")

brand = st.selectbox(
    "Brand",
    options=["virgin", "apple"],
    index=0,
    format_func=_brand_label,
    help="VirginTrains is primary; AppleSupport kept as v1 evidence + transfer proof.",
)

try:
    cfg = brands_mod.get_brand_config(brand)
    st.caption(f"{_brand_label(brand)} — {cfg.get('description', '')}")
except Exception:
    pass

intents = _intents_for_brand(brand)
if intents:
    with st.expander(f"Intents for {_brand_label(brand)} ({len(intents)})"):
        st.write(", ".join(f"`{i}`" for i in intents))

placeholder = BRAND_PLACEHOLDERS.get(brand, "Type a customer support message...")


@st.cache_resource
def get_agent_for_brand(b: str):
    try:
        retr = _make_retriever_for_brand(b)
    except Exception:
        retr = None
    try:
        return AppleAgent(retr, brand=b)
    except Exception:
        return AppleAgent(None, brand=b)


agent = get_agent_for_brand(brand)
text = st.text_area("Customer message", height=120, max_chars=MAX_CHARS,
                    placeholder=placeholder)
run = st.button("Predict", type="primary")

if run:
    if not text or not text.strip():
        st.warning("Empty input — agent will escalate as unresolvable. Type a message to try again.")
    try:
        with st.spinner("Running agent..."):
            t0 = time.perf_counter()
            r = agent.handle(text[:MAX_CHARS], brand)
            wall_ms = round((time.perf_counter() - t0) * 1000, 1)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Intent", r.intent)
        c2.metric("Confidence", f"{r.intent_confidence:.3f}")
        c3.metric("Decision", r.decision)
        sig = r.escalate_signals or {}
        draft_path = sig.get("draft_path", "template")
        c4.metric("Draft path", draft_path)
        groq_reason = sig.get("groq_reason", "")
        reason_line = f"**Reason:** `{r.escalate_reason}`  |  **Latency:** {r.latency_ms} ms (wall {wall_ms} ms)  |  **Brand:** `{sig.get('brand', brand)}`  |  **Draft path:** `{draft_path}`"
        if groq_reason:
            reason_line += f"  |  **Groq:** `{groq_reason}`"
        else:
            reason_line += "  |  **Groq:** `no-key → template`"
        st.write(reason_line)
        # Confidence honesty: weak-label ceiling + threshold context (no fake precision).
        if r.intent_confidence < 0.45:
            st.caption("Low confidence (<0.45) → auto-escalates as unresolvable. Add journey + date/time detail or DM booking ref.")
        elif r.intent_confidence < 0.70 and r.intent in ("delay_claim", "ticket_change_refund", "fare_ticketing", "purchase_billing_service"):
            st.caption("Money intent below 0.70 → escalated for human review (no auto-refund).")
        st.subheader("Draft reply")
        st.write(r.draft_reply)
        st.write("**Grounding passage IDs:**", r.grounding_passage_ids or ["(none — will escalate)"])
        with st.expander("Signals / debug"):
            st.json({"brand": sig.get("brand", brand), "draft_path": draft_path,
                     "groq_reason": groq_reason or "no-key",
                     "escalate_signals": r.escalate_signals,
                     "unsupported_claims": r.unsupported_claims})
        if r.decision == "escalate":
            st.info(f"Escalated ({r.escalate_reason}). In prod this routes to a human with intent + passages.")
    except Exception as e:
        st.error(f"Agent failed: {e}")
        with st.expander("Traceback"):
            st.code(traceback.format_exc()[:2000])
