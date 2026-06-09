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
| Python RTI | n/a | `python`, `in-memory`, `python-in-memory` | direct Python | direct | green | [test_python_backend_extended_services.py](tests/backends/test_python_backend_support_services.py", "tests/backends/test_python_backend_federation_extended.py", "tests/backends/test_python_backend_object_ownership_extended.py", "tests/backends/test_python_backend_time_ddm_extended.py), [run_two_federate_suite.py](scripts/run_two_federate_suite.py) | strongest reference path |
| Python RTI hosted | n/a | `create_rti_ambassador("python", transport={"kind": "grpc", ...})` | direct Python | `grpc` | green | [test_grpc_transport_python_server.py](tests/transport/test_grpc_transport_python_server.py) | remote callback polling via evoke APIs |
| Python RTI hosted | n/a | `create_rti_ambassador("python", transport={"kind": "rest", ...})` | direct Python | `rest` / `http-json` | partial | [test_rest_transport.py](tests/transport/test_rest_transport.py) | transport route is real; scenario breadth is narrower than local Python RTI |
| Java shim | n/a | `java-shim-jpype`, `shim-jpype` | `jpype` | direct | partial | [test_java_profile_backend_matrix.py](tests/vendors/test_java_profile_backend_matrix.py), [test_java_shim_backends.py](tests/backends/test_java_shim_backends.py) | bridge-proof route, not a vendor RTI |
| Java shim | n/a | `java-shim-py4j`, `shim-py4j` | `py4j` | direct | partial | [test_java_profile_backend_matrix.py](tests/vendors/test_java_profile_backend_matrix.py), [test_java_shim_backends.py](tests/backends/test_java_shim_backends.py) | bridge-proof route, not a vendor RTI |
| CERTI | patched | `certi`, `certi-native`, `native-certi` | direct helper/native facade | `subprocess-line` | partial | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](tests/vendors/test_real_vendor_runtime_smoke.py), [vendor_runtime_smoke.sh](scripts/ci/vendor_runtime_smoke.sh) | sync and basic ownership are green; current shared timed-exchange path fails on missing `changeAttributeOrderType` |
| CERTI | patched | `certi-jpype`, `java-certi-jpype` | `jpype` facade over CERTI helper/native path | `subprocess-line` | partial | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) | facade parity route |
| CERTI | patched | `certi-py4j`, `java-certi-py4j` | `py4j` facade over CERTI helper/native path | `subprocess-line` | partial | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) | facade parity route |
| CERTI hosted | patched | `create_rti_ambassador("certi", transport={"kind": "grpc", ...})` | direct helper/native facade | `grpc` | partial | [test_grpc_transport_certi_server.py](tests/transport/test_grpc_transport_certi_server.py), [test_certi_backend_transport.py](tests/backends/test_certi_backend_transport.py) | real remote route exists; scenario breadth is narrower than the local CERTI matrix |
| CERTI hosted | patched | `create_rti_ambassador("certi", transport={"kind": "rest", ...})` | direct helper/native facade | `rest` / `http-json` | partial | [test_certi_backend_transport.py](tests/backends/test_certi_backend_transport.py), [rest_transport_host.py](hla2010/backends/rest_transport_host.py) | route exists; explicit end-to-end scenario proof is thinner than gRPC |
| CERTI | upstream | no separate backend name | baseline-only | n/a | partial | [vendor_runtime_smoke.sh](scripts/ci/vendor_runtime_smoke.sh), [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](../packages/hla2010-rti-certi/docs/certi_runtime_limitations.md) | selected only via `HLA2010_CERTI_UPSTREAM_*`; used for attribution against patched CERTI |
| Pitch pRTI | vendor runtime | `pitch-jpype`, `java-pitch-jpype` | `jpype` | direct | green | [test_pitch_real_backend_matrix.py](tests/vendors/test_pitch_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](tests/vendors/test_real_vendor_runtime_smoke.py) | Docker-backed CRC/FedPro route is the current stable path |
| Pitch pRTI | vendor runtime | `pitch-py4j`, `java-pitch-py4j` | `py4j` | direct | green | [test_pitch_real_backend_matrix.py](tests/vendors/test_pitch_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](tests/vendors/test_real_vendor_runtime_smoke.py) | Docker-backed CRC/FedPro route is the current stable path |
| Portico | vendor runtime | `portico`, `portico-jpype`, `java-portico-jpype` | `jpype` | direct | install-dependent | [rti.py](hla2010/rti.py), [real_rti_portico.py](hla2010/real_rti_portico.py) | runtime discovery/wiring exists; no current local real-runtime evidence in this workspace |
| Portico | vendor runtime | `portico-py4j`, `java-portico-py4j` | `py4j` | direct | install-dependent | [rti.py](hla2010/rti.py), [real_rti_portico.py](hla2010/real_rti_portico.py) | runtime discovery/wiring exists; no current local real-runtime evidence in this workspace |

Use this page when you want the route table itself.
