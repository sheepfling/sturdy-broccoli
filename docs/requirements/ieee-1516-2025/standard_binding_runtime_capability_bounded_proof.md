# Standard Binding Runtime-Capability Bounded Proof

Source: IEEE 1516.1-2025 Java and C++ standard binding route evidence.

This note records the repo's current requirement-facing claim for the standard
Java and C++ 2025 binding routes. These routes are real executable
artifact-gated/runtime-capability traces over the main
`hla-backend-python1516-2025` runtime, but they remain bounded binding/adaptation
evidence rather than exhaustive cross-binding behavior-conformance proof.

## Current Bounded Claim

- `java-standard-2025-jpype` and `java-standard-2025-py4j` are Java binding
  routes over `hla-backend-python1516-2025`, not separate 2025 RTI owners.
- `cpp-standard-2025-pybind` and `cpp-standard-2025-grpc` are C++ binding
  routes over `hla-backend-python1516-2025`, not separate 2025 RTI owners.
- Both Java and C++ standard-route families are parity-covered across the
  tracked eight scenario families used by the current finish-line inventory.
- The remaining proof burden on these lanes is exhaustive cross-binding
  behavior equivalence, not missing ownership of core RTI semantics.

## Tracked Standard Binding Scenario Families

Use these parity columns as binding-route evidence scope only. They are not
canonical requirement disposition fields.

| Scenario family | Java route parity status | C++ route parity status | Evidence anchors | Current bounded reading |
| --- | --- | --- | --- | --- |
| `federation_lifecycle` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py`, `docs/evidence/shim_routes/java-standard-2025.json`, `docs/evidence/shim_routes/cpp-standard-2025.json` | Standard routes cover artifact-gated lifecycle connect/create/join/resign/destroy flows and callback polling over the main `python1516_2025` runtime. |
| `object_exchange` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py`, `docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json`, `docs/evidence/shim_routes/route_traces/cpp-standard-2025-pybind.json` | Standard routes cover two-federate publish/subscribe, discovery, reflection, interaction receive, and unsubscribe suppression. |
| `ownership` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py` | Standard routes cover bounded divestiture/acquisition/query callback traces and owner-state visibility over the main runtime lane. |
| `ddm` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py` | Standard routes cover bounded DDM region overlap filtering, rediscovery, and in-region reflection traces. |
| `time_management` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py` | Standard routes cover artifact-gated logical-time traces: selected time factory, regulation/constrained mode, lookahead modification, TAR/FQR grants, and GALT/LITS queries. |
| `save_restore` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py` | Standard routes cover bounded save/restore initiation/status/completion, object rollback, and logical-time rollback traces. |
| `mom` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py` | Standard routes cover bounded MOM service-report callback delivery, MIM/FOM data report, and manager adjust interaction routing traces. |
| `support_services` | `parity-covered` | `parity-covered` | `tests/backends/test_standard_shim_artifacts.py` | Standard routes cover bounded lookup helpers, logical-time factory lookup, transport/order lookups, and 2025 switch round-trip traces. |

## Primary Evidence Anchors

- `tests/backends/test_standard_shim_artifacts.py`
- `docs/evidence/shim_routes/java-standard-2025.json`
- `docs/evidence/shim_routes/cpp-standard-2025.json`
- `docs/evidence/shim_routes/route_traces/java-standard-2025-jpype.json`
- `docs/evidence/shim_routes/route_traces/java-standard-2025-py4j.json`
- `docs/evidence/shim_routes/route_traces/cpp-standard-2025-pybind.json`
- `docs/evidence/shim_routes/route_traces/cpp-standard-2025-grpc.json`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`

## Reading of the Evidence

- The route-parity matrix is the requirement-facing ledger for both standard
  binding families. It records 16 parity-covered rows for `HLA2025-BND-001`
  and 16 parity-covered rows for `HLA2025-BND-002`.
- `tests/backends/test_standard_shim_artifacts.py` is the executable anchor for
  the artifact-gated/runtime-capability claim. It proves the standard Java and
  C++ routes execute bounded lifecycle, object, ownership, DDM, time,
  save/restore, MOM, and support-service traces.
- The shim-route evidence artifacts and route traces are the route-facing
  records that show those standard bindings replay bounded traces over the main
  `python1516_2025` runtime owner.

## Explicit Non-Claim

- The repo does not claim that the Java or C++ standard routes are separate
  2025 RTI implementation families.
- The repo does not claim exhaustive cross-binding behavior equivalence from
  these standard-route traces alone.
- The repo does not use standard binding proof to weaken the architectural
  boundary that keeps `hla-backend-python1516-2025` as the main 2025 Python RTI
  implementation lane and the Java/C++ packages as bounded adaptation surfaces.
