"""TF-IDF + LogReg intent classifier with weak-label bootstrapping. CPU-only."""
from pathlib import Path
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .text_norm import normalize
from .intents import INTENTS, KEYWORDS

# Repo root resolved from this file's location (portable; no machine-specific prefix).
MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_PATH = MODEL_DIR / "intent_classifier.pkl"

def weak_label(text: str) -> str:
    t = normalize(text)
    # Followup short-ack only if very short and no stronger signal
    strong_hits = []
    for intent, kws in KEYWORDS.items():
        for kw in kws:
            if kw in t:
                strong_hits.append((intent, kw))
    if not strong_hits:
        # howto fallback
        if t.startswith("how") or "how do" in t:
            return "howto_guidance"
        if len(t.split()) <= 3 or "dm" in t or "thank" in t:
            return "support_access_followup"
        return "other_out_of_scope"
    # Prefer non-followup over followup when both hit (e.g. "thanks but battery...")
    non_follow = [i for i, _ in strong_hits if i != "support_access_followup"]
    if non_follow:
        # most specific: longest keyword match
        best = max(strong_hits, key=lambda x: len(x[1]) if x[0] != "support_access_followup" else -1)
        if best[0] == "support_access_followup" and non_follow:
            # pick longest non-followup
            cands = [(i, k) for i, k in strong_hits if i != "support_access_followup"]
            best = max(cands, key=lambda x: len(x[1]))
        return best[0]
    return strong_hits[0][0]

def _preproc(x: str) -> str:
    return normalize(x)

def build_pipeline() -> Pipeline:
    vec = TfidfVectorizer(preprocessor=_preproc, lowercase=False,
                          ngram_range=(1, 2), min_df=3, max_features=30000, sublinear_tf=True)
    clf = LogisticRegression(max_iter=1000, C=2.0)
    return Pipeline([("tfidf", vec), ("clf", clf)])

def train(texts, labels):
    pipe = build_pipeline()
    pipe.fit(texts, labels)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "labels": INTENTS}, MODEL_PATH)
    return pipe

def load():
    obj = joblib.load(MODEL_PATH)
    return obj["pipeline"]

def predict(texts):
    pipe = load()
    proba = pipe.predict_proba(texts)
    preds = pipe.predict(texts)
    conf = proba.max(axis=1)
    return list(zip(preds, conf))
