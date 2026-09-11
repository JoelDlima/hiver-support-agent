"""Virgin failure-fix regression probes (F2/F4a/F6/F7). Fail-closed: exact texts from
evaluation/virgin/FAILURE_TESTS.md must keep current verdicts. Uses VirginRetriever
if the index exists, else agent without retrieval (intent/decision unaffected)."""
from src.agent import AppleAgent


def _agent():
    try:
        from scripts.run_virgin_eval import VirginRetriever
        return AppleAgent(VirginRetriever(), brand="virgin")
    except Exception:
        return AppleAgent(None, brand="virgin")


def test_f2_bare_still_running_is_timetable():
    a = _agent()
    o = a.handle("is the 21:03 train from Euston to Birmingham International still running?",
                 brand="virgin")
    assert o.intent == "timetable_platform", o.intent
    assert o.decision == "auto_handle", (o.decision, o.escalate_reason)
    assert "21:03" not in o.draft_reply  # never invent/confirm times


def test_f4a_packed_is_complaint_and_escalates():
    a = _agent()
    o = a.handle("Wow... this train from Oxford to Stockport is ridiculously packed @VirginTrains",
                 brand="virgin")
    assert o.intent == "complaint_service", o.intent
    assert o.decision == "escalate", (o.decision, o.escalate_reason)


def test_f6_repeat_refund_escalates_money():
    a = _agent()
    o = a.handle("Why have i never recieved my refund on tickets had this problem a few times now. "
                 "Really dissapointing Almost 2 months now ??", brand="virgin")
    assert o.intent == "ticket_change_refund", o.intent
    assert o.decision == "escalate" and o.escalate_reason == "money_review", \
        (o.decision, o.escalate_reason)


def test_f7_receipt_routes_to_refund_and_escalates():
    a = _agent()
    o = a.handle("Hey @VirginTrains - I have lost my open ticket home. Can you reprint at the "
                 "station? I have my receipt", brand="virgin")
    assert o.intent == "ticket_change_refund", o.intent
    assert o.decision == "escalate", (o.decision, o.escalate_reason)


def test_pii_without_human_request_escalates_pii_review():
    a = _agent()
    o = a.handle("my email is jane.doe@example.com, please help with my ticket",
                 brand="virgin")
    assert o.decision == "escalate" and o.escalate_reason == "pii_review", \
        (o.decision, o.escalate_reason)
    assert "jane.doe@example.com" not in o.draft_reply  # templates never echo PII


def test_f3b_callback_number_escalates_pii_review():
    a = _agent()
    o = a.handle("Why dont you call them and get them to call me. Save me some money and time. "
                 "My number is 07403630041", brand="virgin")
    assert o.decision == "escalate" and o.escalate_reason == "pii_review", \
        (o.decision, o.escalate_reason)
    assert "07403630041" not in o.draft_reply


def test_delay_template_states_dr_bands_and_fits_280():
    from src.virgin_intents import TEMPLATES
    t = TEMPLATES["delay_claim"]
    assert "30-59" in t and "booking ref" in t
    assert len(t) <= 280, len(t)
