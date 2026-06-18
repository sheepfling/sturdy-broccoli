# Proto2025 MessageTest v0.1 Test Plan

| ID | Test | Federates | Procedure | Pass criteria | Evidence |
|---|---|---|---|---|---|
| MT-001 | FOM load and join | FederationManager, TestDesignFederate, TestExecutionFederate | Create federation with `Proto2025_Base.xml` and `Proto2025_MessageTest.xml`; join required federates. | All federates join, publish `FederateHealth`, and emit `FederateReady`. | Health log, join log |
| MT-002 | Publish/subscribe contract | TestDesignFederate, TestExecutionFederate, TestViewFederate | Register one suite, two cases, and three steps. | Subscribers discover each object and receive required attributes. | Discovery trace |
| MT-003 | Stimulus/response path | TestExecutionFederate, SystemUnderTestFederate, TestDatabaseFederate | Send `SendStimulus`; SUT emits `MessageObserved`; execution emits `VerificationResult`. | Correlation ID is preserved and verdict is `Pass`. | Event log, verdict object |
| MT-004 | Attribute update load | TestDesignFederate, TestViewFederate, TestDatabaseFederate | Publish 100 cases and 1,000 steps with state updates. | Recorder sees all objects and no decode errors; view remains alive. | Counter report |
| MT-005 | Timeout negative test | TestExecutionFederate, SystemUnderTestFederate | Configure SUT to suppress one response. | Step fails or becomes inconclusive within `TimeoutNs`. | VerificationStatus |
| MT-006 | Fault injection | FaultInjectionFederate, SystemUnderTestFederate, TestExecutionFederate | Inject drop, delay, corrupt, duplicate, and reorder faults. | Expected mismatches are detected and attributed to fault IDs. | Fault log, verdicts |
| MT-007 | Late-join view/database | TestViewFederate or TestDatabaseFederate joins after suite loaded. | Start late subscriber after MT-002 state exists. | Late joiner discovers current suite/case/step objects and obtains state via update request or configured refresh. | Late-join trace |
| MT-008 | Recorder replay | TestDatabaseFederate, ObserverRecorder | Reconstruct event sequence from run artifact. | Replay order hash matches original. | Replay report |

## Minimum v0.1 run profile

- One `TestSuite` named `EchoProtocolSmoke`.
- Test case A: valid echo request/response.
- Test case B: invalid payload expected to produce rejection.
- Timeout: 100 ms logical time or profile-configured equivalent.
- Required outputs: run manifest, FOM set ID, event log, verdict summary, coverage summary.
