"""Brand-agnostic agent: classify -> retrieve -> draft (groq then template) -> escalate.

- brand param (default virgin per revamp); brand=apple uses old files.
- Per-brand classifier via brands.py with fallback to weak_label.
- Groq draft tried first (fail-closed to template); path recorded in signals.
- Apple path preserved exactly for backward compat.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict
import importlib
import time
from pathlib import Path

from .text_norm import normalize, features_for_escalation
from .intents import INTENTS as APPLE_INTENTS, TEMPLATES as APPLE_TEMPLATES, SENSITIVE_INTENTS as APPLE_SENSITIVE
from . import classifier as clf_mod
from . import brands as brands_mod

try:
    from . import groq_draft as groq_mod
except Exception:  # pragma: no cover - module always present, import guard for safety
    groq_mod = None


@dataclass
class AgentResult:
    intent: str
    intent_confidence: float
    draft_reply: str
    grounding_passage_ids: List[str]
    decision: str  # auto_handle | escalate
    escalate_reason: str
    escalate_signals: Dict
    latency_ms: float
    unsupported_claims: List[str]


TRIVIAL_CANNED = "Thanks for reaching out — please DM us your device + iOS version and detail so we can help."

_PIPELINE_CACHE: Dict[str, object] = {}


def _intent_assets(brand: str):
    """Return (INTENTS, TEMPLATES, SENSITIVE, KEYWORDS, SAFETY_ADDONS) for brand."""
    b = (brand or brands_mod.DEFAULT_BRAND).lower().strip()
    if b not in brands_mod.BRANDS:
        b = brands_mod.DEFAULT_BRAND
    if b == "apple":
        from .intents import KEYWORDS as _kw
        return APPLE_INTENTS, APPLE_TEMPLATES, APPLE_SENSITIVE, _kw, []
    # virgin (or future brands): dynamic import
    mod_name = brands_mod.get_intent_module_name(b)
    try:
        mod = importlib.import_module(mod_name)
        intents = getattr(mod, "INTENTS", [])
        templates = getattr(mod, "TEMPLATES", {})
        sensitive = set(getattr(mod, "SENSITIVE_INTENTS", set()))
        keywords = getattr(mod, "KEYWORDS", {})
        safety = list(getattr(mod, "SAFETY_ADDONS", []))
        # Fallback to brands.py safety addons if module has none
        if not safety:
            safety = list(brands_mod.get_brand_config(b).get("safety_addons", []))
        return intents, templates, sensitive, keywords, safety
    except Exception:
        # Minimal fallback (should not happen; virgin shim always present)
        return APPLE_INTENTS, APPLE_TEMPLATES, APPLE_SENSITIVE, {}, []


def _weak_label_generic(text: str, keywords: Dict[str, List[str]]) -> str:
    t = normalize(text)
    strong_hits = []
    for intent, kws in (keywords or {}).items():
        for kw in (kws or []):
            if kw and kw in t:
                strong_hits.append((intent, kw))
    if not strong_hits:
        if t.startswith("how") or "how do" in t:
            # Only return howto if that intent exists in this brand
            return "howto_guidance"
        if len(t.split()) <= 3 or "dm" in t or "thank" in t:
            return "support_access_followup"
        return "other_out_of_scope"
    non_follow = [i for i, _ in strong_hits if i != "support_access_followup"]
    if non_follow:
        best = max(strong_hits, key=lambda x: len(x[1]) if x[0] != "support_access_followup" else -1)
        if best[0] == "support_access_followup" and non_follow:
            cands = [(i, k) for i, k in strong_hits if i != "support_access_followup"]
            best = max(cands, key=lambda x: len(x[1]))
        return best[0]
    return strong_hits[0][0]


def _weak_label_for_brand(brand: str, text: str) -> str:
    b = (brand or brands_mod.DEFAULT_BRAND).lower().strip()
    if b == "apple":
        return clf_mod.weak_label(text)
    _, _, _, keywords, _ = _intent_assets(b)
    pred = _weak_label_generic(text, keywords)
    # Ensure pred is in brand intents; else map to other
    intents, _, _, _, _ = _intent_assets(b)
    if pred not in intents:
        # howto/support fallbacks exist in virgin; otherwise other
        if pred in intents:
            return pred
        return "other_out_of_scope" if "other_out_of_scope" in intents else (intents[-1] if intents else "other_out_of_scope")
    return pred


def _predict_for_brand(brand: str, text: str):
    """Try per-brand joblib model(s); fallback to weak_label (conf 0.35)."""
    b = (brand or brands_mod.DEFAULT_BRAND).lower().strip()
    if b not in brands_mod.BRANDS:
        b = brands_mod.DEFAULT_BRAND
    # Cache lookup
    if b in _PIPELINE_CACHE:
        pipe = _PIPELINE_CACHE[b]
        try:
            proba = pipe.predict_proba([text])
            preds = pipe.predict([text])
            return str(preds[0]), float(proba.max())
        except Exception:
            pass
    # Try model files in order
    for mp in brands_mod.get_model_candidates(b):
        try:
            p = Path(mp)
            if not p.exists():
                continue
            import joblib
            obj = joblib.load(p)
            pipe = obj["pipeline"] if isinstance(obj, dict) and "pipeline" in obj else obj
            _PIPELINE_CACHE[b] = pipe
            proba = pipe.predict_proba([text])
            preds = pipe.predict([text])
            return str(preds[0]), float(proba.max())
        except Exception:
            continue
    # Fallback
    return _weak_label_for_brand(b, text), 0.35


def draft_grounded(intent: str, passages: List[Dict], brand: str = "apple") -> tuple[str, List[str], List[str]]:
    _, templates, _, _, _ = _intent_assets(brand)
    fallback = templates.get("other_out_of_scope") or APPLE_TEMPLATES["other_out_of_scope"]
    base = templates.get(intent, fallback)
    # D6 fix: strip internal <BRAND-KB:*> debug tag from user-facing text (kept in code for audit, never shown)
    try:
        import re as _re
        base = _re.sub(r"\s*<BRAND-KB:[^>]*>", "", base).strip()
    except Exception:
        pass
    try:
        ids = [p["tweet_id"] for p in (passages or [])[:3] if isinstance(p, dict) and "tweet_id" in p]
    except Exception:
        ids = []
    return base, ids, []


def decide_escalation(intent: str, conf: float, text: str, passages: List[Dict], brand: str = "apple") -> tuple[str, str, Dict]:
    feats = features_for_escalation(text)
    norm = normalize(text)
    b = (brand or "apple").lower().strip()
    if b not in brands_mod.BRANDS:
        b = "apple"
    _, _, sensitive, _, safety_addons = _intent_assets(b)
    # Brand safety add-ons (rail: overcrowd/evacuation/injury/stranded) -> treat as legal_safety
    low = (text or "").lower()
    addon_hit = False
    try:
        for tok in (safety_addons or []):
            if tok and tok.lower() in low:
                addon_hit = True
                break
    except Exception:
        addon_hit = False
    signals = {
        "intent": intent, "confidence": round(float(conf), 3),
        "policy_hit": bool(feats["has_legal_safety"] or feats["has_account_security"] or addon_hit),
        "human_request": feats["has_human_request"],
        "frustration": feats["has_frustration"],
        "data_loss": feats["has_data_loss"],
        "link_only": feats["is_link_only"],
        "low_conf": bool(conf < 0.45),
        "no_grounding": bool(not passages or (isinstance(passages[0], dict) and passages[0].get("score", 0) < 0.08)),
    }
    if addon_hit:
        signals["safety_addon_hit"] = True
    reason = "none"
    decision = "auto_handle"
    if feats["has_legal_safety"] or addon_hit:
        decision, reason = "escalate", "legal_safety"
    elif feats.get("has_injection"):
        decision, reason = "escalate", "unresolvable"
    elif feats["has_account_security"] or feats["has_data_loss"]:
        decision, reason = "escalate", "account_security"
    elif feats["has_human_request"]:
        decision, reason = "escalate", "human_request"
    elif b == "apple" and feats["has_money"] and intent == "purchase_billing_service" and conf < 0.7:
        decision, reason = "escalate", "money_threshold"
    elif b != "apple" and intent in brands_mod.get_brand_config(b).get("money_intents", set()) and (feats["has_money"] or "£" in (text or "")):
        # Money + explicit money language escalates at ANY confidence: confident
        # money errors (repeat-refund @0.92, F6) cost cash; recall > precision here.
        # Plain delay questions without money words still auto-handle below.
        if any(p in low for p in ["refund", "repay", "compensation", "chargeback", "charged", "overcharg", "£", "$"]):
            decision, reason = "escalate", "money_review"
        elif conf < 0.7:
            decision, reason = "escalate", "money_threshold"
    elif feats.get("has_non_english"):
        decision, reason = "escalate", "unresolvable-language"
    elif signals["low_conf"] or signals["no_grounding"] or feats["is_link_only"]:
        decision, reason = "escalate", "unresolvable"
    elif feats["has_frustration"] and (conf < 0.6 or intent in sensitive):
        decision, reason = "escalate", "complaint_review"
    elif feats["is_huge"]:
        decision, reason = "escalate", "unresolvable"
    return decision, reason, signals


class AppleAgent:
    """Brand-agnostic agent (name kept for backward compat). Default brand=virgin."""

    def __init__(self, retriever=None, brand: str = "virgin"):
        self.retriever = retriever
        b = (brand or brands_mod.DEFAULT_BRAND).lower().strip()
        self.brand = b if b in brands_mod.BRANDS else brands_mod.DEFAULT_BRAND

    def handle(self, text: str, brand: str | None = None) -> AgentResult:
        t0 = time.perf_counter()
        eff = (brand or self.brand or brands_mod.DEFAULT_BRAND).lower().strip()
        if eff not in brands_mod.BRANDS:
            eff = brands_mod.DEFAULT_BRAND
        intents, templates, _, _, _ = _intent_assets(eff)
        other = "other_out_of_scope" if "other_out_of_scope" in intents else (intents[-1] if intents else "other_out_of_scope")
        if not text or not text.strip():
            fallback_tpl = templates.get(other, "Please share a brief description so we can help. DM us if it involves personal info.")
            lat0 = (time.perf_counter() - t0) * 1000
            return AgentResult(other, 0.0, fallback_tpl,
                               [], "escalate", "unresolvable", {"empty": True, "brand": eff, "draft_path": "template"}, 1.0, [])
        t_clf = time.perf_counter()
        try:
            pred, conf = _predict_for_brand(eff, text)
        except Exception:
            pred, conf = _weak_label_for_brand(eff, text), 0.35
        classify_ms = round((time.perf_counter() - t_clf) * 1000, 1)
        # Ensure pred in brand intents
        if pred not in intents:
            pred = other
        # Language gate: non-English -> other (English-only v1, no translate-and-guess)
        try:
            if features_for_escalation(text).get("has_non_english") and pred != other and float(conf) < 0.85:
                pred, conf = other, min(float(conf), 0.4)
        except Exception:
            pass
        t_ret = time.perf_counter()
        passages = []
        if self.retriever is not None:
            try:
                passages = self.retriever.query(text, k=5)
            except Exception:
                passages = []
        retrieve_ms = round((time.perf_counter() - t_ret) * 1000, 1)
        # Try Groq first (fail-closed to template)
        t_draft = time.perf_counter()
        draft = None
        draft_path = "template"
        groq_info = {}
        if groq_mod is not None:
            try:
                g_text, g_info = groq_mod.draft_with_groq(pred, text, passages, eff)
                groq_info = g_info or {}
                if g_text:
                    draft = g_text
                    draft_path = "groq"
            except Exception:
                draft = None
                draft_path = "template"
        if draft is None:
            draft, ids, unsup = draft_grounded(pred, passages, eff)
        else:
            try:
                ids = [p["tweet_id"] for p in (passages or [])[:3] if isinstance(p, dict) and "tweet_id" in p]
            except Exception:
                ids = []
            unsup = []
        decision, reason, signals = decide_escalation(pred, float(conf), text, passages, eff)
        signals["brand"] = eff
        signals["draft_path"] = draft_path
        signals["classify_ms"] = classify_ms
        signals["retrieve_ms"] = retrieve_ms
        signals["draft_ms"] = round((time.perf_counter() - t_draft) * 1000, 1)
        if groq_info and groq_info.get("reason") not in (None, "", "ok"):
            # Keep groq failure reason for audit without secrets
            signals["groq_reason"] = str(groq_info.get("reason"))[:64]
        lat = (time.perf_counter() - t0) * 1000
        return AgentResult(pred, float(conf), draft, ids, decision, reason, signals, round(lat, 1), unsup)


def trivial_baseline(text: str) -> AgentResult:
    return AgentResult("support_access_followup", 0.2, TRIVIAL_CANNED, [], "auto_handle", "none", {"baseline": "trivial"}, 0.5, [])


def keyword_baseline(text: str, retriever=None) -> AgentResult:
    pred = clf_mod.weak_label(text)
    passages = []
    if retriever is not None:
        try:
            passages = retriever.query(text, k=1)
        except Exception:
            pass
    if passages:
        draft = passages[0]["text"][:240] if passages[0]["text"] else APPLE_TEMPLATES.get(pred, TRIVIAL_CANNED)
        ids = [passages[0]["tweet_id"]]
    else:
        draft, ids = APPLE_TEMPLATES.get(pred, TRIVIAL_CANNED), []
    low = (text or "").lower()
    if any(p in low for p in ["human", "sue", "hacked"]):
        return AgentResult(pred, 0.5, draft, ids, "escalate", "human_request", {"baseline": "keyword"}, 1.0, [])
    return AgentResult(pred, 0.5, draft, ids, "auto_handle", "none", {"baseline": "keyword"}, 1.0, [])
