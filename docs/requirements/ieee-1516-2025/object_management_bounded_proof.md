# Object Management Bounded Proof

Source: IEEE 1516.1-2025 object-management service rows and the repo's current
object-exchange, routing, and advisory proof families.

This note records the repo's current requirement-facing object-management claim
as a bounded proof statement for the main `hla-backend-python1516-2025` runtime
lane. It covers service-by-service runtime traceability for the 32
object-management service rows together with the direct and hosted proof
families for object exchange, deletion and local-known-state cleanup,
attribute-value-update routing, advisory/update-rate behavior, transportation
policy state, and directed interaction routing. It does not claim final
clause-by-clause 2025 conformance or exhaustive cross-binding behavior
equivalence.

## Service Families

| Family | Rows | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- | --- |
| Name reservation and basic object exchange | `HLA2025-FI-SVC-051`, `HLA2025-FI-SVC-052`, `HLA2025-FI-SVC-053`, `HLA2025-FI-SVC-054`, `HLA2025-FI-SVC-055`, `HLA2025-FI-SVC-056`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-058`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-061`, `HLA2025-FI-SVC-062` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for single and multi-name reservation or release, plain object registration and discovery, attribute update/reflect flows, and basic interaction send/receive behavior on the direct and hosted `python1516_2025` routes. |
| Directed interaction routing | `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py` | Closed as bounded runtime proof for directed interaction send/receive, selective directed routing, timestamped directed delivery, and hosted FedPro callback decode of directed-interaction semantics. |
| Deletion and local-known-state lifecycle | `HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-066`, `HLA2025-FI-SVC-067` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for delete/remove/local-delete control, orphan/timed remove flows, subscriber known-state rollback, and stale remove cleanup after restore or disconnect. |
| Scope and attribute-value-update routing | `HLA2025-FI-SVC-068`, `HLA2025-FI-SVC-069`, `HLA2025-FI-SVC-070`, `HLA2025-FI-SVC-071` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for attributesInScope/attributesOutOfScope advisories, class-wide and instance requestAttributeValueUpdate routing, provideAttributeValueUpdate callbacks, owner-only routing, and disconnected-owner suppression. |
| Update-rate and advisory callbacks | `HLA2025-FI-SVC-072`, `HLA2025-FI-SVC-073` | `tests/scenarios/test_object_management_backend_matrix.py`, `tests/test_rti1516_2025_python1516_2025_runtime.py`, `packages/hla-verification/src/hla/verification/scenario_update_advisory.py` | Closed as bounded runtime proof for turnUpdatesOn/off advisories, object-scope relevance transitions, update-rate routing, and advisory behavior over the main `python1516_2025` runtime lane. |
| Transportation query and policy state | `HLA2025-FI-SVC-074`, `HLA2025-FI-SVC-075`, `HLA2025-FI-SVC-076`, `HLA2025-FI-SVC-077`, `HLA2025-FI-SVC-078`, `HLA2025-FI-SVC-079`, `HLA2025-FI-SVC-080`, `HLA2025-FI-SVC-081`, `HLA2025-FI-SVC-082` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/transport/test_grpc_transport_2025.py` | Closed as bounded runtime proof for attribute and interaction transportation-type change requests, confirmation/query/report callbacks, rejection paths, default transportation control, and restore persistence of transportation or order policy state. |

## Object-Management Closure Notes

- The direct and hosted proof families cover executable runtime routing rather
  than only parser or API-surface evidence: later discoveries, reflections,
  interactions, advisories, removes, and transportation callbacks change based
  on the object-management state established at runtime.
- Directed-interaction and directed-DDM proof remains part of the current
  object-management working surface because those paths are already routed
  through the main `hla-backend-python1516-2025` runtime and replayed over hosted
  FedPro.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for
  these object-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
