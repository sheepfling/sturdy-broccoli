# Ownership Management Bounded Proof

Source: IEEE 1516.1-2025 ownership-management service rows and the repo's
current ownership proof families.

This note records the repo's current requirement-facing ownership-management
claim as a bounded proof statement for the main `hla-backend-python1516-2025`
runtime lane. It covers service-by-service runtime traceability for the 18
ownership-management service rows together with the direct-lane and hosted
FedPro replay proof families for divestiture, confirmation, release,
acquisition, cancellation, query visibility, resign-time policy, and restore
rollback. It does not claim
final clause-by-clause 2025 conformance or exhaustive cross-binding behavior
equivalence.

## Service Families

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded evidence scope, not canonical requirement
disposition.

| Family | Rows | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- |
| Divestiture and confirmation flows | `HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-084`, `HLA2025-FI-SVC-086`, `HLA2025-FI-SVC-087`, `HLA2025-FI-SVC-095` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/transport/test_rest_transport.py` | Closed as bounded runtime proof for unconditional and negotiated divestiture, requestDivestitureConfirmation, confirmDivestiture, cancel-negotiated-offer handling, and hosted replay of the same ownership state transitions over FedPro plus the REST-hosted Python route. |
| Release and if-wanted flows | `HLA2025-FI-SVC-092`, `HLA2025-FI-SVC-093`, `HLA2025-FI-SVC-094` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/transport/test_rest_transport.py` | Closed as bounded runtime proof for requestAttributeOwnershipRelease, attributeOwnershipReleaseDenied, and divestiture-if-wanted transfer behavior on the direct `python1516_2025` lane plus hosted FedPro replay and the REST-hosted Python route. |
| Acquisition, assumption, and notification | `HLA2025-FI-SVC-085`, `HLA2025-FI-SVC-088`, `HLA2025-FI-SVC-089` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/transport/test_rest_transport.py` | Closed as bounded runtime proof for requestAttributeOwnershipAssumption, explicit acquisition requests, and ownership acquisition notification delivery across the direct lane, hosted FedPro replay, and the REST-hosted Python route. |
| Acquisition availability and cancellation | `HLA2025-FI-SVC-090`, `HLA2025-FI-SVC-091`, `HLA2025-FI-SVC-096`, `HLA2025-FI-SVC-097` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/transport/test_rest_transport.py` | Closed as bounded runtime proof for attributeOwnershipAcquisitionIfAvailable, unavailable callbacks, acquisition cancellation, and cancel-confirmation flows across the direct lane, hosted FedPro replay, and the REST-hosted Python route. |
| Query visibility | `HLA2025-FI-SVC-098`, `HLA2025-FI-SVC-099` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/transport/test_rest_transport.py` | Closed as bounded runtime proof for queryAttributeOwnership, ownership-information callback outcomes, and isAttributeOwnedByFederate checks across the direct lane, hosted FedPro replay, and the REST-hosted Python route. |
| Resign policies | `HLA2025-FI-SVC-100` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for resign-time ownership policy behavior on the direct lane plus hosted FedPro replay; the REST-hosted Python route is not yet promoted to this narrower resign-policy claim. |

## Owner Row Scope

- The canonical ownership-management owner rows carried by this note are the
  Clause 7 service rows `HLA2025-FI-SVC-083` through `HLA2025-FI-SVC-100`.
- Save/restore rollback of in-flight ownership state is intentionally part of
  the bounded evidence reading here, but `HLA2025-FI-005` remains a linked
  helper row rather than a canonical ownership-service owner row.
- Read this note as the bounded ownership proof owner for the Clause 7 rows
  plus explicit rollback links, not as a license to relabel broader
  save/restore owner rows as ownership closure.

## Ownership Closure Notes

- The maintained focused rerun view for this bounded family is
  `./tools/test-focus run python-2025-ownership`.
- The direct aggregate proof lane is `./tools/python verify-main-2025`, and
  the paired hosted replay lane is `./tools/python verify-routes-2025`.
- The direct-lane and hosted FedPro replay proof families also cover
  save/restore rollback of inflight ownership negotiation state and
  cross-federate owner-visibility recovery, so the ownership working surface is
  not limited to the happy-path transfer calls.
- The REST-hosted Python route now extends the transfer, release, acquisition,
  cancellation, and query-visibility families above, but the narrower
  resign-time ownership policy claim remains direct-lane plus hosted FedPro
  until a dedicated REST resign-policy witness is added.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for
  these ownership-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
