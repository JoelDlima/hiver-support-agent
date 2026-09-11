import json
import os
import sys
import types

sys.path.insert(0, r"C:\Hiver")

from src.agent import AppleAgent
from src import groq_draft as groq_mod
from src import brands as brands_mod
from src import virgin_intents as virgin_mod
from src import intents as apple_mod


def test_groq_no_key_returns_none(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    text, info = groq_mod.draft_with_groq("delay_claim", "my train was delayed", [], "virgin")
    assert text is None
    assert info.get("reason") == "no-key"
    assert "GROQ" not in str(info) or "KEY" not in str(info.get("reason", ""))
    # No secrets leaked in info
    for v in info.values():
        assert "sk-" not in str(v)


def test_virgin_template_path_no_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    a = AppleAgent(None, brand="virgin")
    r = a.handle("my train was delayed, I want to claim delay repay")
    assert r.intent in virgin_mod.INTENTS
    assert r.escalate_signals.get("draft_path") == "template"
    assert r.escalate_signals.get("brand") == "virgin"
    assert "BRAND-KB" not in r.draft_reply
    assert len(r.draft_reply) <= 280


def test_virgin_safety_addon_escalates(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    a = AppleAgent(None, brand="virgin")
    r = a.handle("carriage overcrowded, we were stranded and need evacuation help")
    assert r.decision == "escalate"
    assert r.escalate_reason == "legal_safety"


def test_apple_regression(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    a = AppleAgent(None, brand="apple")
    r = a.handle("my iphone battery drains fast after ios 11 update")
    assert r.intent in apple_mod.INTENTS
    # Classifier model exists for apple legacy path
    assert r.intent == "battery_power"
    assert r.escalate_signals.get("draft_path") == "template"
    assert "BRAND-KB" not in r.draft_reply


def test_brands_config_shape():
    assert set(brands_mod.list_brands()) == {"apple", "virgin"}
    for b in ["apple", "virgin"]:
        cfg = brands_mod.get_brand_config(b)
        assert "intent_module" in cfg and "model_path" in cfg and "index_dir" in cfg
        assert cfg["model_path"].endswith(f"intent_{b}.pkl")
        assert cfg["index_dir"].replace("\\", "/").endswith(f"data/indexes/{b}") or f"indexes/{b}" in cfg["index_dir"].replace("\\", "/")


def _fake_groq_module(draft_payload: str, boom: bool = False):
    """Build a fake `groq` module: either returns draft_payload or raises."""
    mod = types.ModuleType("groq")

    if boom:
        class _BoomCompletions:
            @staticmethod
            def create(**kwargs):
                raise RuntimeError("boom")

        class _BoomChat:
            completions = _BoomCompletions()

        class _BoomClient:
            def __init__(self, *a, **k):
                self.chat = _BoomChat()
        mod.Groq = _BoomClient
        return mod

    class _Msg:
        content = draft_payload

    class _Choice:
        message = _Msg()

    class _Resp:
        choices = [_Choice()]

    class _Completions:
        @staticmethod
        def create(**kwargs):
            return _Resp()

    class _Chat:
        completions = _Completions()

    class _Client:
        def __init__(self, *a, **k):
            self.chat = _Chat()

    mod.Groq = _Client
    return mod


def _fake_openai_module(draft_payload: str, boom: bool = False):
    """Build a fake `openai` module: either returns draft_payload or raises."""
    mod = types.ModuleType("openai")

    if boom:
        class _BoomClient:
            def __init__(self, *a, **k):
                raise RuntimeError("boom")
        mod.OpenAI = _BoomClient
        return mod

    class _Msg:
        content = draft_payload

    class _Choice:
        message = _Msg()

    class _Resp:
        choices = [_Choice()]

    class _Completions:
        @staticmethod
        def create(**kwargs):
            return _Resp()

    class _Chat:
        completions = _Completions()

    class _Client:
        def __init__(self, *a, **k):
            self.chat = _Chat()

    mod.OpenAI = _Client
    return mod


def test_groq_validation_fail_invented_price_time(monkeypatch):
    # Unit-level: invented £ amount + HH:MM absent from sources must fail.
    ok, reason = groq_mod.validate_draft(
        "Sorry for the delay — your refund is \u00a345.20 and the train leaves at 14:30, DM us.",
        "my train was delayed, I want to claim",
        [{"text": "Delay Repay lets you claim if delayed. DM us so we can help.", "clean": ""}],
    )
    assert not ok
    assert reason.startswith("ungrounded-token")
    # Grounded control: same £ token present in inbound passes length/grounding gate.
    ok2, _ = groq_mod.validate_draft(
        "Sorry about the \u00a312 fare issue — DM us so we can help with your claim.",
        "I was charged \u00a312 for my ticket",
        [],
    )
    assert ok2
    # Invented URL must fail even when £/time are clean (live-caught 2026-09-11).
    ok3, reason3 = groq_mod.validate_draft(
        "Sorry about the delay. Claim here: https://t.co/AbDpHCk89z DM us.",
        "my train was delayed, I want to claim",
        [{"text": "Delay Repay lets you claim if delayed. DM us so we can help.", "clean": ""}],
    )
    assert not ok3
    assert reason3.startswith("ungrounded-url")
    # API-level: mocked Groq returning invented £/time must still fail closed to template.
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_fake")
    payload = json.dumps({"draft_reply": "Your compensation is £45.20, train at 14:30, DM us."})
    monkeypatch.setitem(sys.modules, "groq", _fake_groq_module(payload))
    text, info = groq_mod.draft_with_groq(
        "delay_claim", "my train was delayed", [{"text": "Delay Repay info, DM us.", "clean": ""}], "virgin"
    )
    assert text is None
    assert info.get("draft_path") == "template"
    assert str(info.get("reason", "")).startswith("validation-fail")
    for v in info.values():
        assert "gsk_test_fake" not in str(v)


def test_groq_error_to_template(monkeypatch):
    # Transport/API error must fail closed to template (reason error, no secrets).
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_fake")
    monkeypatch.setitem(sys.modules, "groq", _fake_groq_module("", boom=True))
    text, info = groq_mod.draft_with_groq("delay_claim", "my train was delayed", [], "virgin")
    assert text is None
    assert info.get("draft_path") == "template"
    assert info.get("reason") == "error"
    assert info.get("error_type") == "RuntimeError"
    for v in info.values():
        assert "gsk_test_fake" not in str(v)
    # Agent-level stays on template path too.
    a = AppleAgent(None, brand="virgin")
    r = a.handle("my train was delayed, I want to claim delay repay")
    assert r.escalate_signals.get("draft_path") == "template"
    assert len(r.draft_reply) <= 280
