# Data Distribution Management Bounded Proof

Source: IEEE 1516.1-2025 data-distribution-management service rows and the
repo's current DDM/default-policy proof families.

This note records the repo's current requirement-facing data-distribution-
management claim as a bounded proof statement for the main
`hla-backend-python2025` runtime lane. It covers service-by-service runtime
traceability for the 12 DDM service rows together with the direct and hosted
proof families for region creation and modification, object-region routing,
interaction-region routing, directed DDM overlap filtering, passive alias
paths, and restore/disconnect cleanup. It does not claim final clause-by-
clause 2025 conformance or exhaustive cross-binding behavior equivalence.

## Service Families

| Family | Rows | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- | --- |
| Lookup and default-policy control | `HLA2025-FI-SVC-126`, `HLA2025-FI-SVC-127`, `HLA2025-FI-SVC-130` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/backends/test_python_backend_time_ddm_extended.py`, `tests/scenarios/test_ddm_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for createRegion, commitRegionModifications, associateRegionsForUpdates, FOM-backed dimension lookup, and default order/transport policy control across the direct and hosted `python1516_2025` routes. |
| Object-region routing and scope advisories | `HLA2025-FI-SVC-128`, `HLA2025-FI-SVC-129`, `HLA2025-FI-SVC-131`, `HLA2025-FI-SVC-132`, `HLA2025-FI-SVC-133`, `HLA2025-FI-SVC-137` | `tests/backends/test_python_backend_time_ddm_extended.py`, `tests/scenarios/test_ddm_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/test_rti1516_2025_python2025_runtime.py` | Closed as bounded runtime proof for region deletion, object registration with regions, associate/unassociate flows, subscribe/unsubscribe object-class attributes with regions, requestAttributeValueUpdateWithRegions, and `attributesInScope`/`attributesOutOfScope` transitions. |
| Interaction-region routing | `HLA2025-FI-SVC-134`, `HLA2025-FI-SVC-135` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/backends/test_python_backend_time_ddm_extended.py`, `tests/scenarios/test_ddm_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for subscribe/unsubscribe interaction-class-with-regions behavior, sent-region callback context, and cleanup of plain interaction subscribers sharing the same routing surface. |
| Directed DDM routing | `HLA2025-FI-SVC-136` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/scenarios/test_ddm_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for sendInteractionWithRegions delivery through object update-region and `subscribeInteractionClassWithRegions` overlap, including directed-subscriber filtering and no-delivery cases. |

## DDM Closure Notes

- The direct and hosted proof families also cover passive region-subscription
  aliases plus restore/disconnect cleanup for queued DDM delivery and directed
  DDM subscriber routing state, so the DDM working surface is not limited to
  one-path region happy cases.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python2025`. `hla-backend-shim` is not a runtime owner for
  these data-distribution-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
