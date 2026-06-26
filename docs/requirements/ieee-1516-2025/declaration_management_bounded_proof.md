# Declaration Management Bounded Proof

Source: IEEE 1516.1-2025 declaration-management service rows and the repo's
current declaration and basic-exchange proof families.

This note records the repo's current requirement-facing declaration-management
claim as a bounded proof statement for the main `hla-backend-python1516-2025`
runtime lane. It covers service-by-service runtime traceability for the 16
declaration-management service rows together with the direct and hosted proof
families for publication control, subscription control, directed-interaction
declaration, and relevance/advisory callback behavior. It does not claim final
clause-by-clause 2025 conformance or exhaustive cross-binding behavior
equivalence.

## Service Families

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded evidence scope, not canonical requirement
disposition.

| Family | Rows | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- |
| Publication control | `HLA2025-FI-SVC-035`, `HLA2025-FI-SVC-036`, `HLA2025-FI-SVC-037`, `HLA2025-FI-SVC-038`, `HLA2025-FI-SVC-039`, `HLA2025-FI-SVC-040` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py` | Closed as bounded runtime proof for object and interaction publication or unpublication, directed-interaction publication control, declaration gating, and rejection behavior on the direct and hosted `python1516_2025` routes. |
| Subscription control | `HLA2025-FI-SVC-041`, `HLA2025-FI-SVC-042`, `HLA2025-FI-SVC-043`, `HLA2025-FI-SVC-044`, `HLA2025-FI-SVC-045`, `HLA2025-FI-SVC-046` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py` | Closed as bounded runtime proof for object and interaction subscription or unsubscription, directed-interaction subscription isolation, passive/full declaration scenarios, and hosted FedPro replay of the same declaration surfaces. |
| Relevance and advisory callbacks | `HLA2025-FI-SVC-047`, `HLA2025-FI-SVC-048`, `HLA2025-FI-SVC-049`, `HLA2025-FI-SVC-050` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for start/stop registration callbacks, turnInteractionsOn/off advisories, and time-managed declaration-independence behavior across the direct and hosted `python1516_2025` routes. |

## Declaration Closure Notes

- The direct and hosted proof families cover declaration management as an
  executable RTI surface rather than a pure parser or API-signature claim:
  publish/subscribe state changes alter later routing and advisory callbacks in
  the live runtime.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for
  these declaration-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
