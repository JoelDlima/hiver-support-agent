"""Offline contract tests for the SetFit/MiniLM challenger head (Phase 2A).

 Report-only challenger: these tests pin the artifact contract (loads,
 10-intent taxonomy, abstention-gate monotonicity, latency envelope) without
 touching the TF-IDF baseline, goldens, or headline CSVs. Skip (green) when
 the artifact has not been trained yet (e.g. no model weights on disk).
 """

import time

import numpy as np
import pytest

from src.virgin_intents import INTENTS
from src import setfit_head as sh

ARTIFACT = sh.ARTIFACT_DIR
NEEDS_ARTIFACT = pytest.mark.skipif(
    not ((ARTIFACT / "head_final.joblib").exists()
         and (ARTIFACT / "labels.json").exists()
         and (ARTIFACT / "meta.json").exists()),
    reason="challenger artifact not trained (run scripts/train_setfit_head.py)",
)

# One probe per intent (contract = taxonomy membership, NOT correctness —
# the challenger is report-only and underperforms the baseline; see
# evaluation/virgin/setfit_report.md).
PROBES = [
    "my train was delayed by an hour, how do I claim delay repay compensation",
    "I need a refund and to amend my advance ticket, what is the admin fee",
    "what platform does the next train to Euston leave from",
    "I left my bag on the train, where is lost property",
    "the carriage was packed and rammed, staff were rude, I want to complain",
    "how much is a season ticket and can I use my railcard",
    "I need wheelchair assistance and step-free access at the station",
    "how do I book tickets on the app",
    "thanks, DM sent",
    "what is the meaning of life",
]


@NEEDS_ARTIFACT
def test_artifact_loads_with_10_intent_taxonomy():
    art = sh.load_artifact(ARTIFACT)
    assert art["labels"] == INTENTS
    assert len(art["labels"]) == 10
    assert list(art["head"].classes_) == sorted(INTENTS)
    assert 0.1 <= art["temperature"] <= 5.0


@NEEDS_ARTIFACT
def test_predict_contract_taxonomy_and_proba():
    art = sh.load_artifact(ARTIFACT)
    out = sh.predict(PROBES, art)
    assert len(out["labels"]) == len(PROBES)
    assert set(out["labels"]) <= set(INTENTS)
    p = np.asarray(out["proba"])
    assert p.shape == (len(PROBES), 10)
    np.testing.assert_allclose(p.sum(axis=1), 1.0, atol=1e-5)
    assert bool(((out["confidence_msp"] >= 0) & (out["confidence_msp"] <= 1)).all())
    assert np.isfinite(out["confidence_energy"]).all()
    assert out["latency_ms"] > 0


@NEEDS_ARTIFACT
def test_abstention_gate_behaves_monotonically():
    art = sh.load_artifact(ARTIFACT)
    all_in = sh.predict_with_abstention(PROBES, art, threshold=0.0, mode="msp")
    assert sh.ABSTAIN_LABEL not in all_in  # MSP >= 0 always
    all_out = sh.predict_with_abstention(PROBES, art, threshold=1.0, mode="msp")
    # MSP == 1.0 exactly is measure-zero for a 10-way softmax; allow tolerance
    assert all_out.count(sh.ABSTAIN_LABEL) >= len(PROBES) - 1
    mid_lo = sh.predict_with_abstention(PROBES, art, threshold=0.5, mode="msp")
    mid_hi = sh.predict_with_abstention(PROBES, art, threshold=0.8, mode="msp")
    assert mid_hi.count(sh.ABSTAIN_LABEL) >= mid_lo.count(sh.ABSTAIN_LABEL)
    # energy mode returns valid labels/abstains
    ene = sh.predict_with_abstention(PROBES, art, threshold=0.0, mode="energy")
    assert set(ene) <= set(INTENTS) | {sh.ABSTAIN_LABEL}
    with pytest.raises(ValueError):
        sh.confidence_scores(np.ones((2, 10)) / 10, mode="nope")


@NEEDS_ARTIFACT
def test_latency_measured_and_bounded():
    art = sh.load_artifact(ARTIFACT)
    texts = (PROBES * 2)[:20]
    t0 = time.perf_counter()
    out = sh.predict(texts, art)
    total_ms = (time.perf_counter() - t0) * 1000
    per_text = total_ms / len(texts)
    print(f"\nchallenger latency: total={total_ms:.0f}ms for {len(texts)} "
          f"texts => {per_text:.1f}ms/text (incl. frozen MiniLM encode, CPU)")
    assert per_text < 5000, f"latency regression: {per_text:.1f}ms/text"
    assert out["latency_ms"] > 0
