# R1.2 — Miss audit (FIX_PLAN R1): human-200 intent misses of the FINAL system

Method: frozen `models/intent_virgin.pkl` + the two serving remaps (crowd F4a,
language gate) — exactly the shipped classifier path. Bucket precedence:
ambiguous (boundary pair + lexicon signal) > oos_or_noise > context_dependent
(<=6 words / ack shape) > multi_intent (2+ signal families co-present) >
model_error. Read-only; no goldens or models touched.

| bucket | n | share of misses |
|---|---|---|
| ambiguous | 11 | 0.27 |
| multi_intent | 1 | 0.02 |
| context_dependent | 0 | 0.00 |
| oos_or_noise | 17 | 0.41 |
| model_error | 12 | 0.29 |
| **total misses** | **41** | (acc 0.795) |

## ambiguous (examples)
- human=`delay_claim` pred=`timetable_platform` — “@VirginTrains Yeah thanks for that, forget that I’m now going to be late arriving into Edinburgh. Booked those specific times for a reason. Don’t fly get the tr”
- human=`timetable_platform` pred=`lost_property` — “Does anyone know where the 5:40 from Glasgow is? Apparently @VirginTrains have lost it”

## multi_intent (examples)
- human=`ticket_change_refund` pred=`complaint_service` — “@VirginTrains What is the refund procedure for removal of First Class services?”

## oos_or_noise (examples)
- human=`other_out_of_scope` pred=`timetable_platform` — “@341297 @VirginTrains @59 Sorry about that, what time/service train was this on? ^MS”
- human=`other_out_of_scope` pred=`accessibility_assistance` — “@127472 @VirginTrains You are disabled and have a rail card.  I replied because I got blown up in Afghanistan and lifted my trouser leg up.  At this point I was”

## model_error (examples)
- human=`howto_guidance` pred=`complaint_service` — “@VirginTrains can you tell me which first class menu it will be Manchester to Euston 1915? Also what times are each menu on this route as I travel this route a ”
- human=`howto_guidance` pred=`complaint_service` — “@VirginTrains @123241 @13044 Clicked reserve seating, only to find that trainline don’t warn you. Any help? CS virgintrains couldn’t either. Thanks”

## Reading
- `ambiguous` + `multi_intent` + `context_dependent` are **label/task-shape** costs,
  not model capacity: they need dual-label policy (DECISION_LOG #20) and
  thread-context features (FIX_PLAN R1.3a), not a bigger classifier.
- `oos_or_noise` is the other-detection stage from R1.3b.
- `model_error` is the honest capacity residue — the target for any future
  modeling work after the structural buckets are addressed.

## Reproduce
```powershell
python scripts/r1_miss_audit.py            # real run (read-only)
python scripts/r1_miss_audit.py --selftest # bucket-assignment math check
```
