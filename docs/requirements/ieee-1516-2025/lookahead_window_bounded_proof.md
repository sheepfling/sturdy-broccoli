# Lookahead Window Bounded Proof

Source: IEEE 1516.1-2025 time-management service rows, `HLA2025-FI-009`, and
the repo's Target/Radar time-window proof ladder.

This note records the repo's current requirement-facing claim for lookahead
window closure, future-message exclusion, legal post-window output, consumer
ordering, pipelined scan overlap, and bounded save/restore rollback over the
main `hla-backend-python1516-2025` runtime lane. It is narrower than a blanket
time-management conformance claim: it names the exact proof ladder that the
repo currently executes and keeps the remaining boundary explicit.

## Current Proof Ladder

Use `Route / evidence anchors` and `Bounded claim reading` here as owner-facing
proof vocabulary. They describe bounded evidence scope, not canonical
requirement disposition.

| Proof level | Route / evidence anchors | Bounded claim reading |
| --- | --- | --- |
| `time-window-core` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Proves pending timestamped inputs are not skipped and the Target/Radar window does not close before known `< window_end` inputs are delivered on the direct `python1516_2025` lane plus hosted FedPro replay. |
| `time-window-future-exclusion` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py`, `./tools/pitch time-window-probe` | Proves closure is blocked while another regulating federate could still legally send into the closing window; this is the current Pitch-safe two-federate vendor-credence route. |
| `time-window-output-delivery` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Proves the closed window can emit a legal timestamped output after closure on the direct lane and hosted FedPro replay. |
| `time-window-consumer-order` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Proves downstream consumers observe the Target/Radar output in timestamp order relative to other timestamped traffic. |
| `time-window-pipeline-two-scans` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Proves one scan can be processed while the next scan is collected, without cross-window contamination. |
| `time-window-receive-order-poison` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Proves receive-order side traffic does not mutate a closed timestamp-managed scan window. |
| `time-window-save-restore-window-state`, `time-window-save-restore-output-resume`, `time-window-save-restore-pipeline-resume` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py`, `./tools/pitch time-window-restore-state-probe` | Proves dirty post-save window state, output state, and pipeline state are rolled back rather than leaking across restore, with the Pitch probe currently limited to the two-federate restore-state leg. |
| `lookahead-processing-window-certified` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Proves the integrated bounded ladder over the live `python1516_2025` RTI lane and hosted FedPro replay: safe closure, future-message exclusion, legal output, consumer ordering, pipeline overlap, and bounded rollback guards. |

## Oracle and Negative-Control Boundary

- The ladder is not only a happy-path scenario bundle. It includes matching
  negative-oracle guards for mismatched LITS boundaries, premature window
  closure, premature output, reversed consumer order, cross-window
  contamination, receive-order mutation of a closed window, and dirty
  post-restore replay.
- That matters because the repo is not simply tuning the scenario to current
  runtime behavior. The proof contract includes routes that must fail if the
  RTI allows a future-message exclusion bug or a closed-window causality leak.
- The direct executable owner behind these proof routes is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner
  for this bounded lookahead-window claim.

## Bounded Reading

- This note makes the current lookahead window proof auditable as a named
  requirement-facing family rather than leaving it only inside generated
  milestone prose.
- It does not promote the current proof ladder into an unconditional
  clause-by-clause 2025 conformance claim for every possible time-policy
  topology.
- Java and C++ bindings remain cross-binding and artifact/runtime-capability
  evidence over the same `python1516_2025` runtime lane rather than independent
  lookahead-proof owners.
- Hosted FedPro replay remains a bounded hosted route over
  `hla-backend-python1516-2025`, not a second RTI implementation lane.
- For vendor credence, Pitch currently contributes only the two-federate
  `time-window-future-exclusion` and
  `time-window-save-restore-window-state` probes. Those narrow probes do not
  replace the broader direct `python1516_2025` plus hosted FedPro replay
  evidence for output, consumer-order, pipeline, or restore-resume behavior.
