# Backend Route Inventory

Exhaustive inventory of the RTI backends, bridge routes, transport routes, and
named runtime baselines currently present in this workspace.

This is document `1/4` in the backend documentation set:

1. [backend_route_inventory.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/backend_route_inventory.md): exhaustive route inventory and evidence anchors
2. [rti_options_and_test_matrix.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/rti_options_and_test_matrix.md): option inventory and recommended test matrix
3. [backend_capability_matrix.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/backend_capability_matrix.md): feature-capability coverage by backend
4. [backend_conformance_matrix.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/backend_conformance_matrix.md): clause-level conformance snapshot

## Scope

Use this file to answer:

- which runtime families exist at all
- which named backend strings map to them
- whether Python talks to them directly, through `jpype`, through `py4j`, or through a remote transport
- which paths are backed by current automated evidence
- where named CERTI baselines matter

Legend:

- `direct`: no extra remote transport hop from the Python caller
- `remote`: Python talks to a transport host over `grpc` or `rest`
- `baseline-only`: not a normal backend name; used only to separate upstream vs patched evidence
- `green`: current route has automated evidence for its intended scope
- `partial`: route exists and has some automated evidence, but important semantics or scenarios are still missing
- `install-dependent`: route exists but needs a local vendor install not currently evidenced here

## Exhaustive Route Table

| Runtime family | Baseline | Backend name(s) | Python/Java route | Transport | Status | Evidence anchors | Notes |
|---|---|---|---|---|---|---|---|
| Python RTI | n/a | `python`, `in-memory`, `python-in-memory` | direct Python | direct | green | [test_python_backend_extended_services.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_python_backend_extended_services.py), [run_two_federate_suite.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/run_two_federate_suite.py) | strongest reference path |
| Python RTI hosted | n/a | `create_rti_ambassador("python", transport={"kind": "grpc", ...})` | direct Python | `grpc` | green | [test_grpc_transport_python_server.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/transport/test_grpc_transport_python_server.py) | remote callback polling via evoke APIs |
| Python RTI hosted | n/a | `create_rti_ambassador("python", transport={"kind": "rest", ...})` | direct Python | `rest` / `http-json` | partial | [test_rest_transport.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/transport/test_rest_transport.py) | transport route is real; scenario breadth is narrower than local Python RTI |
| Java shim | n/a | `java-shim-jpype`, `shim-jpype` | `jpype` | direct | partial | [test_java_profile_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_java_profile_backend_matrix.py), [test_java_shim_backends.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_java_shim_backends.py) | bridge-proof route, not a vendor RTI |
| Java shim | n/a | `java-shim-py4j`, `shim-py4j` | `py4j` | direct | partial | [test_java_profile_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_java_profile_backend_matrix.py), [test_java_shim_backends.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_java_shim_backends.py) | bridge-proof route, not a vendor RTI |
| CERTI | patched | `certi`, `certi-native`, `native-certi` | direct helper/native facade | `subprocess-line` | partial | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_certi_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_real_vendor_runtime_smoke.py), [vendor_runtime_smoke.sh](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/vendor_runtime_smoke.sh) | sync and basic ownership are green; current shared timed-exchange path fails on missing `changeAttributeOrderType` |
| CERTI | patched | `certi-jpype`, `java-certi-jpype` | `jpype` facade over CERTI helper/native path | `subprocess-line` | partial | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_certi_java_profile_callbacks.py) | facade parity route |
| CERTI | patched | `certi-py4j`, `java-certi-py4j` | `py4j` facade over CERTI helper/native path | `subprocess-line` | partial | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_certi_java_profile_callbacks.py) | facade parity route |
| CERTI hosted | patched | `create_rti_ambassador("certi", transport={"kind": "grpc", ...})` | direct helper/native facade | `grpc` | partial | [test_grpc_transport_certi_server.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/transport/test_grpc_transport_certi_server.py), [test_certi_backend_transport.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_certi_backend_transport.py) | real remote route exists; scenario breadth is narrower than the local CERTI matrix |
| CERTI hosted | patched | `create_rti_ambassador("certi", transport={"kind": "rest", ...})` | direct helper/native facade | `rest` / `http-json` | partial | [test_certi_backend_transport.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/backends/test_certi_backend_transport.py), [rest_transport_host.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/hla2010/backends/rest_transport_host.py) | route exists; explicit end-to-end scenario proof is thinner than gRPC |
| CERTI | upstream | no separate backend name | baseline-only | n/a | partial | [vendor_runtime_smoke.sh](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/scripts/ci/vendor_runtime_smoke.sh), [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_runtime_limitations.md) | selected only via `HLA2010_CERTI_UPSTREAM_*`; used for attribution against patched CERTI |
| Pitch pRTI | vendor runtime | `pitch-jpype`, `java-pitch-jpype` | `jpype` | direct | green | [test_pitch_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_pitch_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_real_vendor_runtime_smoke.py) | Docker-backed CRC/FedPro route is the current stable path |
| Pitch pRTI | vendor runtime | `pitch-py4j`, `java-pitch-py4j` | `py4j` | direct | green | [test_pitch_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_pitch_real_backend_matrix.py), [test_real_vendor_runtime_smoke.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/vendors/test_real_vendor_runtime_smoke.py) | Docker-backed CRC/FedPro route is the current stable path |
| Portico | vendor runtime | `portico`, `portico-jpype`, `java-portico-jpype` | `jpype` | direct | install-dependent | [rti.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/hla2010/rti.py), [real_rti_portico.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/hla2010/real_rti_portico.py) | runtime discovery/wiring exists; no current local real-runtime evidence in this workspace |
| Portico | vendor runtime | `portico-py4j`, `java-portico-py4j` | `py4j` | direct | install-dependent | [rti.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/hla2010/rti.py), [real_rti_portico.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/hla2010/real_rti_portico.py) | runtime discovery/wiring exists; no current local real-runtime evidence in this workspace |

## Named CERTI Baselines

The backend names do not change between upstream and patched CERTI. The baseline
is selected by environment:

- `certi-patched`
  - `HLA2010_CERTI_PATCHED_PREFIX`
  - `HLA2010_CERTI_PATCHED_BUILD_ROOT`
  - or the repo-local default `HLA2010_CERTI_PREFIX` / `HLA2010_CERTI_BUILD_ROOT`
- `certi-upstream`
  - `HLA2010_CERTI_UPSTREAM_PREFIX`
  - `HLA2010_CERTI_UPSTREAM_BUILD_ROOT`

Primary compare command:

```bash
./scripts/ci/vendor_runtime_smoke.sh certi-compare
```

Use that command when the question is:

- is this behavior a generic CERTI limitation?
- or did the local patched CERTI branch change it?

## Remote RTI Routes

Remote here means the Python caller talks to a transport host over `grpc` or
`rest`; it does not mean a separate vendor-specific distributed runtime API.

Current real remote routes are:

- Python RTI over `grpc`
- Python RTI over `rest`
- CERTI over `grpc`
- CERTI over `rest`

Current callback contract for both remote transports:

- unary request/response transport calls
- callback polling through `evokeCallback` / `evokeMultipleCallbacks`
- no streaming callback channel yet

## Testing Commands

### Patched CERTI

```bash
./scripts/ci/vendor_runtime_smoke.sh certi-patched
```

### Upstream vs patched CERTI attribution

```bash
./scripts/ci/vendor_runtime_smoke.sh certi-compare
```

### Pitch

```bash
./scripts/ci/vendor_runtime_smoke.sh pitch
```

Simplest operator path:

```bash
./scripts/pitch_docker_easy.sh install
./scripts/pitch_docker_easy.sh start
./scripts/pitch_docker_easy.sh smoke
```

Quickstart:

- [pitch_docker_quickstart.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/pitch_docker_quickstart.md)

### Transport-hosted Python RTI

```bash
python3 -m pytest -q tests/transport/test_grpc_transport_python_server.py
python3 -m pytest -q tests/transport/test_rest_transport.py
```

### Transport-hosted CERTI

```bash
python3 -m pytest -q tests/transport/test_grpc_transport_certi_server.py
python3 -m pytest -q tests/backends/test_certi_backend_transport.py
```

## What This Inventory Does Not Claim

- It does not claim Portico is currently verified locally.
- It does not claim Pitch negotiated ownership is promotable.
- It does not claim CERTI currently satisfies the shared timed-exchange path.
- It does not treat `grpc` or `rest` as new RTI families; they are route choices under existing backends.
