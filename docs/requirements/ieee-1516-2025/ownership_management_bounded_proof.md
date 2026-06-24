# Ownership Management Bounded Proof

Source: IEEE 1516.1-2025 ownership-management service rows and the repo's
current ownership proof families.

This note records the repo's current requirement-facing ownership-management
claim as a bounded proof statement for the main `hla-backend-python1516-2025`
runtime lane. It covers service-by-service runtime traceability for the 18
ownership-management service rows together with the direct and hosted proof
families for divestiture, confirmation, release, acquisition, cancellation,
query visibility, resign-time policy, and restore rollback. It does not claim
final clause-by-clause 2025 conformance or exhaustive cross-binding behavior
equivalence.

## Service Families

| Family | Rows | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- | --- |
| Divestiture and confirmation flows | `HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-084`, `HLA2025-FI-SVC-086`, `HLA2025-FI-SVC-087`, `HLA2025-FI-SVC-095` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for unconditional and negotiated divestiture, requestDivestitureConfirmation, confirmDivestiture, cancel-negotiated-offer handling, and hosted FedPro replay of the same ownership state transitions. |
| Release and if-wanted flows | `HLA2025-FI-SVC-092`, `HLA2025-FI-SVC-093`, `HLA2025-FI-SVC-094` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for requestAttributeOwnershipRelease, attributeOwnershipReleaseDenied, and divestiture-if-wanted transfer behavior on the direct and hosted `python1516_2025` routes. |
| Acquisition, assumption, and notification | `HLA2025-FI-SVC-085`, `HLA2025-FI-SVC-088`, `HLA2025-FI-SVC-089` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for requestAttributeOwnershipAssumption, explicit acquisition requests, and ownership acquisition notification delivery. |
| Acquisition availability and cancellation | `HLA2025-FI-SVC-090`, `HLA2025-FI-SVC-091`, `HLA2025-FI-SVC-096`, `HLA2025-FI-SVC-097` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for attributeOwnershipAcquisitionIfAvailable, unavailable callbacks, acquisition cancellation, and cancel-confirmation flows. |
| Query visibility and resign policies | `HLA2025-FI-SVC-098`, `HLA2025-FI-SVC-099`, `HLA2025-FI-SVC-100` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_ownership_management_backend_matrix.py`, `tests/backends/test_python_backend_object_ownership_extended.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for queryAttributeOwnership, ownership-information callback outcomes, isAttributeOwnedByFederate checks, and resign-time ownership policy behavior. |

## Ownership Closure Notes

- The direct and hosted proof families also cover save/restore rollback of
  inflight ownership negotiation state and cross-federate owner-visibility
  recovery, so the ownership working surface is not limited to the happy-path
  transfer calls.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for
  these ownership-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
