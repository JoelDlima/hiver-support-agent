"""VirginTrains intent taxonomy (Phase 1 V-DATA filled, V-MODEL shim origin).

10 intents from REVAMP_V2_PLAN.md. KEYWORDS are weak-label rules refined from
the 65,346-row Virgin union scan (see research/datasets/virgin_data_quality.md).
TEMPLATES are brand-voice drafts (<=280 chars): acknowledge -> Delay-Repay /
amendment step -> DM booking ref; never invent times/prices.
"""
INTENTS = [
    "delay_claim",
    "ticket_change_refund",
    "timetable_platform",
    "lost_property",
    "complaint_service",
    "fare_ticketing",
    "accessibility_assistance",
    "howto_guidance",
    "support_access_followup",
    "other_out_of_scope",
]

DESCRIPTIONS = {
    # Grounded in 65,346-row Virgin union scan (27,817 outbound / 37,530 mentions;
    # inbound n=37,529, outbound n=27,817). Counts below are inbound/outbound hits.
    "delay_claim": "train delayed/cancelled/late, Delay Repay compensation claim (delay 2602/1757, delayed 1326/534, late 1400/583, cancel 1387/275, delay repay 291/432, compensation 251/357)",
    "ticket_change_refund": "amend Advance ticket, change journey, refund request, admin-fee rules (refund 1224/308, advance 607/342, booking 400/391, booking ref 45/205, off-peak 48/98)",
    "timetable_platform": "departure/arrival times, platform number, live disruption, engineering works (platform 356/59, timetable 50/45; station names NOT keywords — they are slot entities)",
    "lost_property": "item left on train/station, lost-property office, claim process (lost 214/154, left 494/52, left my 58/0, bag 138/16, luggage 97/14, phone 491/44)",
    "complaint_service": "staff conduct, overcrowding, cleanliness, onboard experience incl. seat/first-class/wifi/toilet (complaint 365/390, rude 185/1, seat 2347/872, first class 925/222, wifi 712/259, toilet 373/28)",
    "fare_ticketing": "ticket types, fare price, railcard, penalty fare, collection/machine/office (fare/price/cost/railcard/penalty/season/collect; bare 'ticket' 3900/2025 deliberately NOT a keyword — too generic)",
    "accessibility_assistance": "step-free access, Passenger Assist booking, wheelchair space, priority seat — RARE, oversample (assistance 78/62, wheelchair 27/2, disabled 71/6, ramp 22/0)",
    "howto_guidance": "how do I book, Delay Repay how-to, app guidance, station facilities (how-phrases; distinct from timetable by question shape)",
    "support_access_followup": "DM follow-up, short ack, thanks/closure — matched LAST among content intents so 'delayed 2hrs thanks' stays delay_claim (Thank you 82, Thanks 73, Morning 22, Ok thanks 19, Yes 18)",
    "other_out_of_scope": "vague, non-rail, non-English, unrelated",
}

# Weak-label rules (lowercase substring match; FIRST match wins in INTENTS order
# except support_access_followup, which is checked last despite list position —
# see weak_label() note. Order puts rare/distinctive (lost_property,
# accessibility_assistance) before generic (complaint_service) so they are not stolen.)
KEYWORDS = {
    "delay_claim": ["delay repay", "delayed", "delay", "running late", "arrived late", "late arriving", "cancelled", "canceled", "cancel", "compensation", "repay"],
    "ticket_change_refund": ["refund", "advance ticket", "advance", "amend", "change my ticket", "change my journey", "exchange", "booking ref", "booking reference", "admin fee", "administration fee", "off-peak", "off peak", "super off-peak", "reprint", "reissue", "receipt", "at the station", "duplicate ticket"],
    "timetable_platform": ["next train", "when is", "what platform", "which platform", "leaving at", "arriving at", "due to leave", "first train", "last train", "platform", "timetable", "engineering work", "engineering works", "departure", "arrival", "what time", "running on time", "on time", "still running", "expected at", "due at", "line closure", "bus replacement"],
    "lost_property": ["lost property", "lost my", "lost", "left my", "left on the train", "left on", "luggage", "left my bag", "bag on", "phone on the train"],
    "complaint_service": ["complaint", "rude", "disgusting", "appalling", "overcrowd", "overcrowded", "overcrowding", "packed", "rammed", "crammed", "crush", "crushed", "standing room only", "first class", "seat", "wifi", "toilet", "dirty", "cleanliness", "staff were", "staff was", "no air", "too hot", "too cold", "quiet coach", "quiet carriage"],
    "fare_ticketing": ["railcard", "penalty fare", "penalty", "season ticket", "season", "anytime", "ticket machine", "ticket office", "collect my ticket", "collect your ticket", "mticket", "m-ticket", "e-ticket", "eticket", "fare", "how much", "price of", "cost of", "upgrade"],
    "accessibility_assistance": ["passenger assist", "assistance", "wheelchair", "disabled", "step-free", "step free", "ramp", "accessible", "accessibility", "priority seat", "assistance dog", "blind", "deaf", "mobility"],
    "howto_guidance": ["how do i", "how to", "how can i", "how do you", "where is", "where do i", "can i use", "do you offer", "how does"],
    "support_access_followup": ["dm sent", "sent dm", "sent you a dm", "check dm", "thank you", "thankyou", "thanks", "thank", "thx", "ok thanks", "morning", "evening", "good night", "brilliant", "great service"],
    "other_out_of_scope": [],
}

TEMPLATES = {
    "delay_claim": "Sorry your train was delayed. Delay Repay is typically 50% of a single ticket for 30-59 mins, 100% for 60+ (full return for 120+) — keep your ticket. DM us your journey + date + booking ref and we'll guide your claim. <BRAND-KB:delay>",
    "ticket_change_refund": "We can help with your amendment/refund. Check your ticket terms (Advance is restricted). DM us your booking ref + journey and we'll advise next steps. <BRAND-KB:amend>",
    "timetable_platform": "Let's check your service — I won't guess times or platforms here (they change). Check live departures, then DM us your from/to + date/time and we'll look it up. <BRAND-KB:timetable>",
    "lost_property": "Sorry you left something behind. Note the service + car/spot if you can. DM us your journey + item description and we'll point you to lost property. <BRAND-KB:lost>",
    "complaint_service": "Sorry about your experience. Please share what happened (service/date/time) without personal details here. DM us and we'll log it properly. <BRAND-KB:complaint>",
    "fare_ticketing": "We can point you on fares — I won't quote prices here (they vary by time/type). Check ticket type + railcard before travel. DM us your journey + passenger type and we'll explain options (no payment here). <BRAND-KB:fare>",
    "accessibility_assistance": "We can help arrange assistance. Book Passenger Assist ahead where possible. DM us your journey + needs and we'll guide you securely. <BRAND-KB:assist>",
    "howto_guidance": "Happy to guide you. Tell us your journey + date/time and the step you're stuck on, and we'll share steps. <BRAND-KB:howto>",
    "support_access_followup": "Thanks for following up — we got it. If you sent a DM, we'll review there. Otherwise DM us your booking ref + journey and we'll continue. <BRAND-KB:followup>",
    "other_out_of_scope": "Thanks for reaching out. Please DM us your journey + date/time + brief detail so we can point you correctly. Don't share personal info publicly. <BRAND-KB:triage>",
}

# Escalation-prone (money/safety/human review first)
SENSITIVE_INTENTS = {
    "delay_claim",
    "ticket_change_refund",
    "complaint_service",
    "accessibility_assistance",
}

# Overcrowding tokens that force a complaint_service remap when the classifier
# predicts other_out_of_scope with low confidence (F4a fix, 2026-09-11).
# Rationale: this lexicon is human-curated ground truth for overcrowding; when the
# weak-trained LogReg says "other" but is unsure (<0.6) and a crowd token is present,
# trust the lexicon. Narrow by design: only fires on other-predictions, so it can
# never steal delay/refund/timetable cases. Stranded/evacuation/injury are NOT here
# (they escalate via safety addons but are not complaint signals).
CROWD_REMAP_TOKENS = [
    "packed",
    "rammed",
    "crammed",
    "crush",
    "overcrowd",
]

# Rail safety lexicon add-ons (extend base text_norm escalation lexicon).
# NOTE: agent._intent_assets reads THIS list (not brands.py). "crammed" covers the
# dominant complaint phrasing ("crammed into the train"); packed/rammed/crush included.
SAFETY_ADDONS = [
    "overcrowd",
    "overcrowded",
    "overcrowding",
    "packed",
    "rammed",
    "crush",
    "crushed",
    "crushing",
    "crammed",
    "evacuation",
    "evacuate",
    "evacuated",
    "injury",
    "injured",
    "stranded",
    "stampede",
    "derail",
]
