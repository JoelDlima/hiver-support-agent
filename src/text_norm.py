"""Text normalization for AppleSupport tweets. CPU-only, no external deps."""
import html
import re
import unicodedata

URL_RE = re.compile(r"https?://\S+|t\.co/\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
WS_RE = re.compile(r"\s+")
EMOJI_HINT_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")

def normalize(text: str, keep_case: bool = False) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)
    t = html.unescape(t)
    t = URL_RE.sub(" <URL> ", t)
    # Keep brand signal but normalize (D7 fix: all supported brands -> <BRAND>, not <USER>)
    t = re.sub(r"@applesupport", " <BRAND> ", t, flags=re.IGNORECASE)
    t = re.sub(r"@virgintrains", " <BRAND> ", t, flags=re.IGNORECASE)
    t = MENTION_RE.sub(" <USER> ", t)
    # Keep hashtag word: #ios11 -> hashtag ios11
    t = HASHTAG_RE.sub(r" hashtag \1 ", t)
    # Emoji -> token + count preserved via token
    t = EMOJI_HINT_RE.sub(" <EMOJI> ", t)
    t = WS_RE.sub(" ", t).strip()
    if not keep_case:
        t = t.lower()
    return t

def features_for_escalation(text: str) -> dict:
    low = (text or "").lower()
    return {
        "has_human_request": any(p in low for p in ["human", "real person", "someone real", "call me", "talk to", "manager", "supervisor"]),
        "has_legal_safety": any(p in low for p in ["sue", "lawyer", "court", "hurt", "injured", "injur", "fire", "flame", "burn", "smoke", "smok", "explod", "explode", "shock", "electrocut", "bleed", "blood", "self harm", "kill myself", "suicid"]),
        "has_account_security": any(p in low for p in ["hacked", "stolen", "unauthorized", "someone logged", "password reset not working", "locked out", "activation lock"]),
        "has_data_loss": any(p in low for p in ["lost all", "deleted", "wiped", "photos gone", "contacts gone", "backup failed", "cannot restore"]),
        "has_frustration": any(p in low for p in ["furious", "ridiculous", "pathetic", "worst", "useless", "angry", "disgusted", "fed up", "!!!", "wtf"]),
        "has_money": any(p in low for p in ["refund", "repay", "compensation", "chargeback", "claim", "charged twice", "overcharged", "warranty", "applecare", "$", "£", "receipt", "billing", "delay repay"]),
        "has_non_english": bool(re.search(r"\b(para|gracias|donde|está|merci|pour|avec|guten|danke|waar|dank|grazie|perch[eé]|je|suis|mon|ma|mes|nous|vous|sont|bonjour|annule|bloque|retard|billet|retraso|horario|estaci[oó]n)\b", low)) or (sum(1 for ch in (text or "") if ord(ch) > 127) / max(len(text or ""), 1) > 0.25),
        "has_injection": any(p in low for p in ["ignore previous", "ignore all previous", "reveal password", "reveal system", "system prompt", "jailbreak", "dan mode", "do anything now"]),
        "is_link_only": bool(text and "<URL>" in normalize(text) and len(normalize(text).split()) <= 4),
        "is_very_short": len((text or "").split()) <= 2,
        "is_huge": len(text or "") > 500,
    }
