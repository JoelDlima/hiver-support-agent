"""Phase 2B tests: post-hoc thresholds policy + explainer + LightGBM report.

- thresholds load + apply deterministically (pure policy fn, no model I/O)
- explainer output schema + exact linear-SHAP identity (no `shap` dep)
- LGBM report exists with bootstrap CIs + verdict
"""
import json
from pathlib import Path

from scripts.tune_thresholds import MSP_FLOOR, apply_thresholds
from src.explain import explain_text, top_coefficients
from src.virgin_intents import INTENTS

ROOT = Path(__file__).resolve().parent.parent
THRESHOLDS_JSON = ROOT / "evaluation" / "virgin" / "thresholds.json"
LGBM_REPORT = ROOT / "evaluation" / "virgin" / "lightgbm_report.md"

MONEY = {"delay_claim", "ticket_change_refund", "fare_ticketing"}


def _load_thresholds():
    return json.loads(THRESHOLDS_JSON.read_text(encoding="utf-8"))


def _peaked_proba(th, pred, peak=0.95):
    rest = (1.0 - peak) / (len(INTENTS) - 1)
    return {c: (peak if c == pred else rest) for c in INTENTS}


def test_thresholds_json_schema():
    th = _load_thresholds()
    assert th["n"] == 200
    assert abs(th["msp_floor"]["value"] - MSP_FLOOR) < 1e-12
    assert abs(th["msp_floor"]["value"] - 0.45) < 1e-12
    assert set(th["money_intents"]) == MONEY
    assert set(th["per_intent"]) == set(INTENTS)
    for intent, d in th["per_intent"].items():
        assert 0.0 < d["threshold"] < 1.0, intent
        for k in ("precision", "recall", "f1", "support", "roc_auc",
                  "average_precision", "rule", "money_tuned"):
            assert k in d, (intent, k)
        assert d["money_tuned"] == (intent in MONEY)


def test_thresholds_apply_deterministic():
    th = _load_thresholds()
    # Accept: peaked above floor + above the delay_claim operating point.
    good = _peaked_proba(th, "delay_claim")
    r1 = apply_thresholds("delay_claim", good, th)
    r2 = apply_thresholds("delay_claim", good, th)
    r3 = apply_thresholds("delay_claim", dict(good), th)
    assert r1 == r2 == r3
    assert r1["action"] == "accept" and r1["reason"] == "above_operating_point"
    # Abstain: everything below the MSP floor.
    flat = {c: 1.0 / len(INTENTS) for c in INTENTS}
    r = apply_thresholds("other_out_of_scope", flat, th)
    assert r["action"] == "abstain" and r["reason"] == "below_msp_floor"
    # Abstain: above floor but below the per-intent operating point.
    thr = th["per_intent"]["fare_ticketing"]["threshold"]
    assert thr > MSP_FLOOR  # guard: this case needs thr above the floor
    peak = (MSP_FLOOR + thr) / 2.0
    mid = _peaked_proba(th, "fare_ticketing", peak=peak)
    r = apply_thresholds("fare_ticketing", mid, th)
    assert r["action"] == "abstain" and r["reason"] == "below_operating_point"


def test_explainer_schema_and_exactness():
    e = explain_text("my train was delayed, I want to claim compensation",
                     top_k=5)
    for k in ("text", "predicted_intent", "predicted_proba", "target_intent",
              "target_proba", "all_proba", "logit", "base_value", "background",
              "contributions", "top_positive", "top_negative", "global",
              "exactness"):
        assert k in e, k
    assert e["predicted_intent"] in INTENTS
    assert abs(sum(e["all_proba"].values()) - 1.0) < 1e-6
    assert e["exactness"]["abs_err"] < 1e-9  # base + sum(phi) == logit exactly
    phis = [c["phi"] for c in e["contributions"]]
    assert phis == sorted(phis, reverse=True)
    assert len(e["top_positive"]) <= 5 and len(e["top_negative"]) <= 5
    assert e["background"]["n"] == 200
    for c in e["contributions"]:
        assert set(c) == {"feature", "tfidf", "mean_tfidf", "weight", "phi"}
    # Target override path keeps the identity too.
    e2 = explain_text("packed train, refund please",
                      intent="ticket_change_refund", top_k=5)
    assert e2["target_intent"] == "ticket_change_refund"
    assert e2["exactness"]["abs_err"] < 1e-9


def test_top_coefficients_shape():
    t = top_coefficients("delay_claim", k=7)
    assert t["intent"] == "delay_claim"
    assert len(t["top_positive"]) == 7 and len(t["top_negative"]) == 7
    pos = [d["weight"] for d in t["top_positive"]]
    assert pos == sorted(pos, reverse=True)
    assert all(d["weight"] > 0 for d in t["top_positive"])
    try:
        top_coefficients("not_an_intent")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for unknown intent")


def test_lightgbm_report_exists_with_ci():
    assert LGBM_REPORT.exists(), "run scripts/train_lightgbm_arm.py first"
    md = LGBM_REPORT.read_text(encoding="utf-8")
    assert "95% CI" in md
    assert "macro-F1" in md and "best_iteration" in md
    assert ("Verdict: NO-SHIP" in md) or ("Verdict: SHIP" in md)
    assert "lightgbm" in md.lower()
