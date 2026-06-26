# Save/Restore Bounded Proof

Source: IEEE 1516.1-2025 save/restore service rows, `HLA2025-FI-001`,
`HLA2025-FI-005`, `HLA2025-REQ-002`, and the repo's current save/restore proof
families.

This note records the repo's current requirement-facing save/restore claim as a
bounded proof statement for the main `hla-backend-python1516-2025` runtime lane. It
breaks the current save/restore surface into named proof families so the repo's
bounded rollback claim is explicit instead of only living inside the generated
finish-line bundle or inside the broader federation-management note.

## Current Proof Families

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded evidence scope, not canonical requirement
disposition.

| Family | Rows | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- |
| Lifecycle control | `HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`, `HLA2025-FI-SVC-021`, `HLA2025-FI-SVC-022`, `HLA2025-FI-SVC-023`, `HLA2025-FI-SVC-026`, `HLA2025-FI-SVC-027`, `HLA2025-FI-SVC-028`, `HLA2025-FI-SVC-029`, `HLA2025-FI-SVC-030`, `HLA2025-FI-SVC-031`, `HLA2025-FI-SVC-032` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for request, initiate, begun, complete, failure, abort, and precondition/status control flow for federation save and restore across the direct `python1516_2025` lane and hosted FedPro replay. |
| Shared scenario rollback | `HLA2025-REQ-002` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof that a saved federation returns to the saved baseline rather than preserving dirty post-save state across shared backend-neutral save/restore scenarios. |
| Routing and policy rollback | `HLA2025-FI-SVC-024`, `HLA2025-FI-SVC-025`, `HLA2025-FI-SVC-033`, `HLA2025-FI-SVC-034` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for callback-delivery policy recovery, transport/order policy rollback, object/interaction subscriber-routing rollback, directed DDM rollback, and stale queued callback cleanup after restore. |
| Ownership rollback | `HLA2025-FI-005` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for ownership gauntlets, in-flight acquisition/divestiture rollback, and cross-federate owner-visibility recovery after restore. |
| Time-window and time-state rollback | `HLA2025-FI-001` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for saved lookahead recovery, queued-TSO redelivery, time/switch-control rollback, open/closed time-window recovery, output-resume rollback, and pipeline-resume rollback without dirty replay. |

## Save/Restore Closure Notes

- The direct executable owner behind these proof families is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner
  for this bounded save/restore claim.
- The hosted `python1516_2025-fedpro-grpc` route replays every current proof family
  above, but it remains a bounded hosted route over `hla-backend-python1516-2025`,
  not a second RTI implementation lane.
- The current bounded proof also covers restore-failure, restore-abort,
  participant/status exception control flow, transport/order metadata
  persistence, local-delete object-known-state recovery, and rollback of dirty
  post-save window/output/pipeline state rather than just basic lifecycle
  callbacks.

## Bounded Reading

- This note makes the current save/restore surface auditable as a named
  requirement-facing family instead of leaving it only as one larger aggregate
  slice.
- It does not claim that every save/restore requirement now has its own
  standalone clause-by-clause conformance proof.
- Java and C++ bindings remain cross-binding and artifact/runtime-capability
  evidence over the same `python1516_2025` runtime lane rather than independent
  save/restore conformance owners.
- Hosted FedPro remains transport-seam evidence over `hla-backend-python1516-2025`
  rather than full remote-RTI semantics proof.
