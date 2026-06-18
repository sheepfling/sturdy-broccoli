# Proto2025 TimeMgmtTest v0.1 Test Plan

| ID | Test | Federates | Procedure | Pass criteria | Evidence |
|---|---|---|---|---|---|
| TM-001 | RO delivery baseline | ROProducer, EventDrivenConsumer, TimeObserver | Emit 10,000 receive-order events. | Reliable profile receives all events; best-effort losses are counted and not hidden. | Event counts |
| TM-002 | TSO monotonic order | TSOProducer, EventDrivenConsumer | Send timestamped events out of wall-clock order. | Consumer observes non-decreasing logical timestamps. | OrderingReport |
| TM-003 | Simultaneous timestamp batch | TSOProducer, EventDrivenConsumer, TimeObserver | Emit 100 events with same timestamp and explicit `TieBreaker`. | Deterministic order hash matches expected tie-breaker order. | Order hash report |
| TM-004 | TAR time-step cycle | TimeSteppedProducer, TimeObserver | Request fixed time advances over 100 ticks. | Grants are monotonic; no callback violates requested/granted time policy. | TimeAdvanceReport |
| TM-005 | NER event-driven cycle | EventDrivenConsumer, TSOProducer | Consumer advances to next event or requested time. | Grants match next-event expectations and events are processed once. | NER trace |
| TM-006 | Positive lookahead progress | Four time-managed federates | Run with lookahead > 0 and cross-traffic. | No deadlock; grants progress until pattern complete. | Progress timeline |
| TM-007 | Zero-lookahead edge | ZeroLookaheadFederate, TimeObserver | Configure same-time event behavior. | Feature is supported correctly or explicitly reported unsupported. | Capability report |
| TM-008 | Past event protection | FaultInjectionFederate, EventDrivenConsumer | Attempt to send an event in the receiver's past. | Event is rejected, converted, or reported according to profile; no silent corruption. | ErrorReport, violation report |
| TM-009 | Optimistic probe | ZeroLookahead/OptimisticProbe federate | Probe flush/retract behavior if RTI exposes it. | Capability verified or marked unsupported. | Probe report |
| TM-010 | Deterministic replay | All time-test federates | Repeat same seed and pattern. | Event-order hash and verdicts match previous run. | Replay report |
| TM-011 | Late join during time pattern | LateJoinTimeFederate | Join mid-run and subscribe to time-test state. | Discovery behavior is documented; no invalid callbacks or crashes. | Late-join trace |

## Minimum v0.1 time profile

- Logical time type: `HLAinteger64Time`.
- Base tick: 1,000,000 ns.
- Positive lookahead profile: 1 tick.
- Simultaneous-event batch size: 100.
- Deterministic hash: SHA-256 over `eventId|timestamp|tieBreaker|receiveIndex` rows.
