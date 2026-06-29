# Callback Bounded Proof

Source: IEEE 1516.1-2025 callback rows, the repo's callback proof families,
and the current direct-lane plus hosted FedPro callback evidence.

This note records the repo's current requirement-facing callback claim as a
bounded proof statement for the main `hla-backend-python1516-2025` runtime lane. It
separates the current callback surface into named proof families so the repo's
bounded callback-delivery claim is explicit instead of only living in the
route-summary artifacts or the more general callback-model explainer.

## Current Proof Families

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded evidence scope, not canonical requirement
disposition.

| Family | Evidence anchors | Bounded claim reading |
| --- | --- | --- |
| Declaration relevance and interest advisories | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for `startRegistrationForObjectClass`, `stopRegistrationForObjectClass`, `turnInteractionsOn`, and `turnInteractionsOff` callback delivery across the direct `python1516_2025` lane plus hosted FedPro replay. |
| Federation sync, save/restore, and reporting callbacks | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for synchronization registration/announce flow, `federationSynchronized`, save/restore lifecycle callbacks, connection-lost teardown, and federation reporting callbacks. |
| Object discovery, delivery, and removal | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for `discoverObjectInstance`, `reflectAttributeValues`, `receiveInteraction`, `provideAttributeValueUpdate`, and `removeObjectInstance` delivery across plain, timed, restore, and requester-only routing paths. |
| Object advisory, transport, and name-reservation callbacks | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for scope advisories, update-rate advisories, transport change/query callbacks, and single/multiple object-instance name reservation callback flows. |
| Supplemental callback context and region metadata | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for callback-context preservation, including producing-federate context and sent-region metadata on the direct lane plus hosted FedPro delivery surface. |
| Ownership negotiation and query callbacks | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_ownership_management_backend_matrix.py` | Closed as bounded runtime proof for ownership assumption, release, divestiture confirmation, acquisition notification, unavailable/query callbacks, and restore recovery of in-flight ownership state. |
| Time grant, regulation, and retraction callbacks | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Closed as bounded runtime proof for time-regulation/time-constrained enable callbacks, `timeAdvanceGrant` progression, and `requestRetraction` delivery across the direct lane plus hosted FedPro time-window or queued-TSO replay. |
| Callback control and backlog hygiene | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for `disableCallbacks`, `enableCallbacks`, callback-drain ordering, and reconnect-safe stale-backlog cleanup on the hosted seam. |

## Owner Row Scope

- This note is intentionally a cross-family bounded callback evidence surface
  over linked child rows, not a single contiguous clause owner like the
  service-family notes.
- The most direct callback-control owner rows carried here are
  `HLA2025-FI-SVC-193`, `HLA2025-FI-SVC-194`, `HLA2025-FI-SVC-195`, and
  `HLA2025-FI-SVC-196`.
- The remaining callback families stay owned by their linked child federation,
  declaration, object, ownership, time, and binding rows rather than becoming
  standalone callback-owned service closure just because this note groups their
  delivery evidence together.
- Read this note as the bounded callback-delivery evidence owner for linked
  child rows plus callback-control services, not as a license to relabel every
  touched child service row as callback closure.

## Callback Closure Notes

- The maintained focused rerun view for callback and support-service behavior is
  `./tools/test-focus run python-2025-mom-callbacks`.
- The direct aggregate proof lane is `./tools/python verify-main-2025`, and
  the paired hosted replay lane is `./tools/python verify-routes-2025`.
- The direct executable owner behind these callback proof families is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner
  for this bounded callback claim.
- The hosted `python1516_2025-fedpro-grpc` route replays every current callback
  proof family above, but it remains a bounded hosted route over
  `hla-backend-python1516-2025`, not a second RTI implementation lane.
- The strongest current proof for raw callback-control semantics and inline
  callback behavior remains the direct `python1516_2025` lane; the hosted route is
  still primarily a transport-seam and callback-polling proof surface.
- The REST-hosted Python route is not currently promoted as an owner for these
  2025 callback proof families. The current checked-in REST evidence covers the
  hosted transport seam, 2025 execution-membership control, and selected
  lifecycle/control-flow witnesses, but not a family-by-family 2025 callback
  replay claim.

## Bounded Reading

- This note makes the current callback surface auditable as a named
  requirement-facing family instead of leaving it only as a callback ledger,
  route-parity count, or general backend behavior explainer.
- It does not claim exhaustive callback-by-callback signature equivalence,
  exhaustive callback ordering equivalence across every binding, or blanket
  cross-binding callback conformance beyond the current Python lanes.
- Java and C++ bindings remain cross-binding and artifact/runtime-capability
  evidence over the same `python1516_2025` runtime lane rather than independent
  callback conformance owners.
- Hosted FedPro remains transport-seam evidence over `hla-backend-python1516-2025`
  rather than a second full callback semantics owner.
