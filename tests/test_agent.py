import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.text_norm import normalize
from src import classifier as clf_mod
from src.agent import AppleAgent

def test_normalize():
    assert "<url>" in normalize("see https://t.co/abc hi").lower()
    assert "<brand>" in normalize("@AppleSupport help").lower()

def test_weak_label():
    assert clf_mod.weak_label("my battery drains fast") == "battery_power"
    assert clf_mod.weak_label("forgot apple id password") == "apple_id_icloud"

def test_agent_empty():
    a = AppleAgent(None)
    r = a.handle("")
    assert r.decision == "escalate"

def test_agent_escalate_human():
    a = AppleAgent(None)
    r = a.handle("I want a human now, hacked account")
    assert r.decision == "escalate"
