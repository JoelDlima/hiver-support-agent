"""Brand-agnostic config for Hiver revamp (Phase 1 V-MODEL).

- Apple kept as v1 evidence + transfer proof (old files untouched).
- Virgin is primary after revamp (default brand in agent).
- Per-brand: intent module path, classifier model path, index dir,
  sensitive sets, safety lexicon add-ons, Groq model.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models"
INDEX_ROOT = ROOT / "data" / "indexes"

BRANDS = {
    "apple": {
        # Intent taxonomy module (old files)
        "intent_module": "src.intents",
        # Per-brand model path (new convention) + legacy fallback (old file)
        "model_path": str(MODEL_DIR / "intent_apple.pkl"),
        "legacy_model_path": str(MODEL_DIR / "intent_classifier.pkl"),
        # Per-brand index dir (new) + legacy fallback (old flat dir)
        "index_dir": str(INDEX_ROOT / "apple"),
        "legacy_index_dir": str(INDEX_ROOT),
        "sensitive_intents": {"apple_id_icloud", "purchase_billing_service", "hardware_device", "setup_transfer_restore"},
        "money_intents": {"purchase_billing_service"},
        "safety_addons": [],
        "groq_model": "llama-3.3-70b-versatile",
        "max_draft_chars": 280,
        "description": "AppleSupport Twitter (v1 evidence, transfer baseline)",
    },
    "virgin": {
        "intent_module": "src.virgin_intents",
        "model_path": str(MODEL_DIR / "intent_virgin.pkl"),
        "legacy_model_path": None,
        "index_dir": str(INDEX_ROOT / "virgin"),
        "legacy_index_dir": None,
        "sensitive_intents": {"delay_claim", "ticket_change_refund", "complaint_service", "accessibility_assistance"},
        "money_intents": {"delay_claim", "ticket_change_refund", "fare_ticketing"},
        "safety_addons": [
            "overcrowd",
            "overcrowded",
            "overcrowding",
            "packed",
            "rammed",
            "crush",
            "crushed",
            "crushing",
            "evacuation",
            "evacuate",
            "evacuated",
            "injury",
            "injured",
            "stranded",
            "stampede",
            "derail",
        ],
        "groq_model": "llama-3.3-70b-versatile",
        "max_draft_chars": 280,
        "description": "VirginTrains UK rail (primary, Delay Repay + amendment + timetable)",
    },
}

DEFAULT_BRAND = "virgin"


def get_brand_config(brand: str) -> dict:
    """Return brand config; fallback to virgin for unknown/empty."""
    b = (brand or DEFAULT_BRAND).lower().strip()
    if b not in BRANDS:
        b = DEFAULT_BRAND
    return BRANDS[b]


def get_intent_module_name(brand: str) -> str:
    return get_brand_config(brand)["intent_module"]


def get_model_candidates(brand: str) -> list:
    """Ordered model paths to try: per-brand first, then legacy (apple)."""
    cfg = get_brand_config(brand)
    cands = [cfg["model_path"]]
    if cfg.get("legacy_model_path"):
        cands.append(cfg["legacy_model_path"])
    return cands


def get_index_candidates(brand: str) -> list:
    cfg = get_brand_config(brand)
    cands = [cfg["index_dir"]]
    if cfg.get("legacy_index_dir"):
        cands.append(cfg["legacy_index_dir"])
    return cands


def list_brands() -> list:
    return sorted(BRANDS.keys())
