# Backend Capability Matrix

Current backend support status for the `hla-2010` working scaffold.

This is document `3/4` in the backend documentation set.
For the canonical documentation hierarchy, see
[documentation_hierarchy.md](documentation_hierarchy.md).

The four backend docs are intentionally parallel:

1. [backend_route_inventory.md](backend_route_inventory.md): exhaustive route inventory and evidence anchors
2. [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): option inventory and recommended test matrix
3. [backend_capability_matrix.md](backend_capability_matrix.md): feature-capability coverage by backend
4. [backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance snapshot

## Scope

This matrix tracks what the Python federate can rely on through the common HLA 1516.1-2010 surface today.

Use this file to answer:

- which backend families support which scenario classes
- which transport surfaces are real and currently exercised
- which runtime paths are practical for day-to-day testing
- which harmonized artifact packet records vendor/runtime parity evidence

Use the inventory doc for names and combinations, and use the conformance doc
for clause-level status.

Legend:

- `yes`: implemented and covered by automated tests
- `partial`: implemented for a narrower contract than a full vendor RTI
- `no`: not implemented or currently unavailable
- `blocked`: wiring exists, but runtime cannot be exercised in this workspace

## Matrix

| Backend | Common Exchange | Timed Exchange | Sync Scenario | Ownership Scenario | Real RTI Process |
|---|---|---:|---:|---:|---:|
| `python` | yes | yes | yes | yes | no |
| `java-shim-jpype` | yes | partial | yes | yes | no |
| `java-shim-py4j` | yes | partial | yes | yes | no |
| `certi` | yes | partial | yes | yes | yes |
| `certi-jpype` | yes | partial | yes | yes | yes |
| `certi-py4j` | yes | partial | yes | yes | yes |
| `pitch-jpype` | yes | yes | yes | yes | yes |
| `pitch-py4j` | yes | yes | yes | yes | yes |

## Transport Surfaces

This repo also has a narrower transport seam under the backend layer. That seam is real, but its current scope is explicit:

| Transport kind | Current role | Automated coverage |
|---|---|---:|
| `subprocess-line` | primary local CERTI transport path | yes |
| `rest` / `http-json` | typed remote transport exercised through the CERTI adapter path and through a transport-hosted pure-Python RTI server | yes |
| `grpc` | typed remote transport exercised through the CERTI adapter path and through a transport-hosted pure-Python RTI server | yes |

These transport kinds are not separate RTI backends today. They are transport choices used under the backend-neutral Python HLA surface, with current coverage centered on the CERTI-facing path.

## Verification Features

| Feature | Current role | Automated coverage |
|---|---|---:|
| `vendor-parity-packet` | harmonized packet over vendor smoke commands, matrix tests, findings notes, and optional preflight JSON | yes |

Primary anchors:

- [vendor_parity_artifacts.md](vendor_parity_artifacts.md)
- [test_vendor_parity_artifacts.py](../tests/scenarios/test_vendor_parity_artifacts.py)
- [run_vendor_parity_artifacts.py](../scripts/run_vendor_parity_artifacts.py)

## Notes

- `java-shim-jpype` and `java-shim-py4j` now support end-to-end multi-federate synchronization and ownership scenarios through the shared in-process Java shim.
- The shared Java shims do not model full vendor-style timestamped delivery semantics. They cover the common backend-neutral exchange contract, but timed-delivery assertions remain a real-RTI concern.
- `certi-jpype` and `certi-py4j` are Java-profile facades over the real native CERTI transport in this workspace. There is no vendor-supplied CERTI Java 2010 RTI artifact here.
- `certi`, `certi-jpype`, and `certi-py4j` are covered by real synchronization and ownership smoke tests, but the current shared timed-exchange route is only partial because CERTI does not implement `changeAttributeOrderType`.
- `rest` remains a transport seam, not an additional runtime family. It now has a transport-hosted pure-Python RTI proving server and uses the same polling callback contract as gRPC.
- `grpc` now goes one step further: a transport-hosted pure-Python RTI server proves that the existing backend-neutral exchange path can run end to end over the gRPC wire without changing federate code.
- The current remote callback contract is explicit across both `rest` and `grpc`: unary transport requests plus callback polling through `evokeCallback` / `evokeMultipleCallbacks`. Callback streaming is a future design option, not the current contract.
- Use [backend_route_inventory.md](docs/backend_route_inventory.md) when the distinction between patched CERTI, upstream CERTI, local bridge facades, and remote transport-hosted routes matters.
- The negotiated ownership services are now wired for CERTI as well, and the
  patched local runtime can now separate the direct `deny` path from the
  transfer paths. `confirm` and `ifwanted` still share the same CERTI
  release-response implementation. See
  [backend_conformance_matrix.md](docs/backend_conformance_matrix.md)
  for the per-clause status.
- The real CERTI backend now carries the same backend-neutral synchronization and ownership scenario helpers used by the in-process shims, which improves parity between the pure Python RTI and the CERTI-backed Java-profile paths.
- `pitch-jpype` and `pitch-py4j` now pass the real exchange, timed-exchange, synchronization, and ownership matrix against the Docker-backed Pitch CRC/FedPro route.

## Test Coverage

- Shared Java-profile exchange matrix:
  - [test_java_profile_backend_matrix.py](tests/vendors/test_java_profile_backend_matrix.py)
- Real CERTI backend matrix:
  - [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py)
- CERTI Java-profile callback forwarding and conversion:
  - [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py)
- Real vendor smoke:
  - [test_real_vendor_runtime_smoke.py](tests/vendors/test_real_vendor_runtime_smoke.py)
- Real Pitch backend matrix:
  - [test_pitch_real_backend_matrix.py](tests/vendors/test_pitch_real_backend_matrix.py)
- Transport-hosted Python RTI over gRPC:
  - [test_grpc_transport_python_server.py](tests/transport/test_grpc_transport_python_server.py)
- Transport-hosted Python RTI over REST:
  - [test_rest_transport.py](tests/transport/test_rest_transport.py)
- CERTI hosted behind the same gRPC contract:
  - [test_grpc_transport_certi_server.py](tests/transport/test_grpc_transport_certi_server.py)
