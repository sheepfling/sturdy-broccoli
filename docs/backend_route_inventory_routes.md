# Backend Route Inventory: Routes

Exhaustive inventory of the RTI backends, bridge routes, and transport routes
currently present in this workspace.

Use this page to answer:

- which runtime families exist at all
- which named backend strings map to them
- whether Python talks to them directly, through `jpype`, through `py4j`, or
  through a remote transport
- which paths are backed by current automated evidence

Legend:

- `direct`: no extra remote transport hop from the Python caller
- `remote`: Python talks to a transport host over `grpc` or `rest`
- `baseline-only`: not a normal backend name; used only to separate upstream vs patched evidence
- `green`: current route has automated evidence for its intended scope
- `partial`: route exists and has some automated evidence, but important semantics or scenarios are still missing
- `install-dependent`: route exists but needs a local vendor install not currently evidenced here

Exhaustive Route Table:

| Runtime family | Baseline | Backend name(s) | Python/Java route | Transport | Status | Evidence anchors | Notes |
|---|---|---|---|---|---|---|---|
| Python RTI | n/a | `python`, `in-memory`, `python-in-memory` | direct Python | direct | green | [test_python_backend_support_services.py](../tests/backends/test_python_backend_support_services.py), [test_python_backend_federation_extended.py](../tests/backends/test_python_backend_federation_extended.py), [test_python_backend_object_ownership_extended.py](../tests/backends/test_python_backend_object_ownership_extended.py), [test_python_backend_time_ddm_extended.py](../tests/backends/test_python_backend_time_ddm_extended.py), [`./tools/two-federate`](../tools/two-federate) | strongest reference path |
| Python RTI hosted | n/a | `create_rti_ambassador("python1516e", transport={"kind": "grpc", ...})` | direct Python | `grpc` | green | [test_grpc_transport_python_server.py](../tests/transport/test_grpc_transport_python_server.py) | remote callback polling via evoke APIs |
| Python RTI hosted | n/a | `create_rti_ambassador("python1516e", transport={"kind": "rest", ...})` | direct Python | `rest` / `http-json` | partial | [test_rest_transport.py](../tests/transport/test_rest_transport.py) | transport route is real; scenario breadth is narrower than local Python RTI |
| Python RTI 2025 | n/a | `python1516_2025`, `python-1516-2025`, `python-1516-2025` | direct Python | direct | green | [test_rti1516_2025_python1516_2025_runtime.py](../tests/test_rti1516_2025_python1516_2025_runtime.py), [test_2025_finish_line_snapshot.py](../tests/requirements/test_2025_finish_line_snapshot.py), [test_2025_route_parity_matrix.py](../tests/requirements/test_2025_route_parity_matrix.py) | main full `rti1516_2025` implementation lane in `hla-backend-python1516-2025`; `test_rti1516_2025_python1516_2025_runtime.py` is the main in-process `python1516_2025` proof suite; `hla-backend-shim` remains compatibility-wrapper/import-level support rather than a separate RTI |
| Python RTI 2025 hosted | n/a | `start_2025_grpc_server(...)`, `GrpcTransport(..., schema="rti1516_2025")`, `create_rti_ambassador("python1516_2025", transport={"kind": "grpc", ...})` | direct Python | `grpc` | green | [test_grpc_transport_2025.py](../tests/transport/test_grpc_transport_2025.py), [test_hla_factory_composition.py](../tests/test_hla_factory_composition.py), [test_2025_route_parity_matrix.py](../tests/requirements/test_2025_route_parity_matrix.py), [2025_requirements_finish_line.md](plans/2025_requirements_finish_line.md) | hosted FedPro route over the main full `hla-backend-python1516-2025` runtime; bounded runtime slice, not a separate RTI family; remaining hosted proof is transport-seam evidence over `hla-backend-python1516-2025`, not alternate runtime ownership; factory-level `create_rti_ambassador("python1516_2025", transport=...)` now resolves onto the main `python1516_2025` lane rather than a wrapper-owned route |
| Java shim | n/a | `java-shim-jpype`, `shim-jpype` | `jpype` | direct | partial | [test_java_profile_backend_matrix.py](../tests/vendors/test_java_profile_backend_matrix.py), [test_java_shim_backends.py](../tests/backends/test_java_shim_backends.py) | bridge-proof route, not a vendor RTI |
| Java shim | n/a | `java-shim-py4j`, `shim-py4j` | `py4j` | direct | partial | [test_java_profile_backend_matrix.py](../tests/vendors/test_java_profile_backend_matrix.py), [test_java_shim_backends.py](../tests/backends/test_java_shim_backends.py) | bridge-proof route, not a vendor RTI |
| CERTI | patched | `certi`, `certi-native`, `native-certi` | direct helper/native facade | `subprocess-line` | partial | [tests/vendors/README.md](../tests/vendors/README.md), [test_real_vendor_runtime_smoke.py](../tests/vendors/test_real_vendor_runtime_smoke.py), [`./tools/vendor-green`](../tools/vendor-green) | sync and basic ownership are green; current shared timed-exchange path fails on missing `changeAttributeOrderType` |
| CERTI | patched | `certi-native` | native CERTI helper/runtime path | `subprocess-line` | partial | [tests/vendors/README.md](../tests/vendors/README.md), [test_certi_backend_callbacks.py](../tests/backends/test_certi_backend_callbacks.py) | native runtime route |
| CERTI hosted | patched | `create_rti_ambassador("certi", transport={"kind": "grpc", ...})` | direct helper/native facade | `grpc` | partial | [test_grpc_transport_certi_server.py](../tests/transport/test_grpc_transport_certi_server.py), [test_certi_backend_transport.py](../tests/backends/test_certi_backend_transport.py), [`./tools/vendor-green certi-patched`](../tools/vendor-green) | required baseline promotes the gRPC exchange test; gRPC synchronization and ownership remain probe-only |
| CERTI hosted | patched | `create_rti_ambassador("certi", transport={"kind": "rest", ...})` | direct helper/native facade | `rest` / `http-json` | partial | [test_certi_backend_transport.py](../tests/backends/test_certi_backend_transport.py), [rest_transport_host.py](../packages/hla-transport-rest/src/hla/transports/rest/rest_transport_host.py) | route exists; explicit end-to-end scenario proof is thinner than gRPC |
| CERTI | upstream | no separate backend name | baseline-only | n/a | partial | [`./tools/vendor-green`](../tools/vendor-green), [tests/vendors/README.md](../tests/vendors/README.md), [certi_runtime_limitations.md](../packages/hla-backend-certi/docs/certi_runtime_limitations.md) | selected only via `HLA2010_CERTI_UPSTREAM_*`; used for attribution against patched CERTI |
| Pitch pRTI | vendor runtime | `pitch-jpype`, `java-pitch-jpype` | `jpype` | direct | green | [test_pitch_real_backend_matrix.py](../tests/vendors/test_pitch_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](../tests/vendors/test_real_vendor_runtime_smoke.py) | Docker-backed CRC/FedPro route is the current stable path |
| Pitch pRTI | vendor runtime | `pitch-py4j`, `java-pitch-py4j` | `py4j` | direct | green | [test_pitch_real_backend_matrix.py](../tests/vendors/test_pitch_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](../tests/vendors/test_real_vendor_runtime_smoke.py) | Docker-backed CRC/FedPro route is the current stable path |
| Portico | vendor runtime | `portico`, `portico-jpype`, `java-portico-jpype` | `jpype` | direct | install-dependent | [rti1516e.py](../packages/hla-rti-core/src/hla/runtime/rti1516e.py), [real_rti_portico.py](../packages/hla-vendor-portico/src/hla/vendors/portico/real_rti_portico.py) | runtime discovery/wiring exists; no current local real-runtime evidence in this workspace |
| Portico | vendor runtime | `portico-py4j`, `java-portico-py4j` | `py4j` | direct | install-dependent | [rti1516e.py](../packages/hla-rti-core/src/hla/runtime/rti1516e.py), [real_rti_portico.py](../packages/hla-vendor-portico/src/hla/vendors/portico/real_rti_portico.py) | runtime discovery/wiring exists; no current local real-runtime evidence in this workspace |

Use this page when you want the route table itself.
