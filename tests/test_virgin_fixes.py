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
