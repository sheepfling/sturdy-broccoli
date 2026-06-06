# Backend Capability Matrix

Current backend support status for the `hla-2010` working scaffold.

## Scope

This matrix tracks what the Python federate can rely on through the common HLA 1516.1-2010 surface today.

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
| `certi` | yes | yes | yes | yes | yes |
| `certi-jpype` | yes | yes | yes | yes | yes |
| `certi-py4j` | yes | yes | yes | yes | yes |
| `pitch-jpype` | blocked | blocked | blocked | blocked | blocked |

## Transport Surfaces

This repo also has a narrower transport seam under the backend layer. That seam is real, but its current scope is explicit:

| Transport kind | Current role | Automated coverage |
|---|---|---:|
| `subprocess-line` | primary local CERTI transport path | yes |
| `rest` / `http-json` | typed remote transport exercised through the CERTI adapter path and through a transport-hosted pure-Python RTI server | yes |
| `grpc` | typed remote transport exercised through the CERTI adapter path and through a transport-hosted pure-Python RTI server | yes |

These transport kinds are not separate RTI backends today. They are transport choices used under the backend-neutral Python HLA surface, with current coverage centered on the CERTI-facing path.

## Notes

- `java-shim-jpype` and `java-shim-py4j` now support end-to-end multi-federate synchronization and ownership scenarios through the shared in-process Java shim.
- The shared Java shims do not model full vendor-style timestamped delivery semantics. They cover the common backend-neutral exchange contract, but timed-delivery assertions remain a real-RTI concern.
- `certi-jpype` and `certi-py4j` are Java-profile facades over the real native CERTI transport in this workspace. There is no vendor-supplied CERTI Java 2010 RTI artifact here.
- `certi`, `certi-jpype`, and `certi-py4j` are covered by real exchange, timed-exchange, synchronization, and ownership smoke tests.
- `rest` remains a transport seam, not an additional runtime family. It now has a transport-hosted pure-Python RTI proving server and uses the same polling callback contract as gRPC.
- `grpc` now goes one step further: a transport-hosted pure-Python RTI server proves that the existing backend-neutral exchange path can run end to end over the gRPC wire without changing federate code.
- The current remote callback contract is explicit across both `rest` and `grpc`: unary transport requests plus callback polling through `evokeCallback` / `evokeMultipleCallbacks`. Callback streaming is a future design option, not the current contract.
- The negotiated ownership services are now wired for CERTI as well, and the
  patched local runtime can now separate the direct `deny` path from the
  transfer paths. `confirm` and `ifwanted` still share the same CERTI
  release-response implementation. See
  [backend_conformance_matrix.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/backend_conformance_matrix.md)
  for the per-clause status.
- The real CERTI backend now carries the same backend-neutral synchronization and ownership scenario helpers used by the in-process shims, which improves parity between the pure Python RTI and the CERTI-backed Java-profile paths.
- `pitch-jpype` remains fail-fast and skipped because the local Pitch CRC/runtime is not activated.

## Test Coverage

- Shared Java-profile exchange matrix:
  - [test_java_profile_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_java_profile_backend_matrix.py)
- Real CERTI backend matrix:
  - [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py)
- CERTI Java-profile callback forwarding and conversion:
  - [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py)
- Real vendor smoke:
  - [test_real_vendor_runtime_smoke.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_real_vendor_runtime_smoke.py)
- Transport-hosted Python RTI over gRPC:
  - [test_grpc_transport_python_server.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_grpc_transport_python_server.py)
- Transport-hosted Python RTI over REST:
  - [test_rest_transport.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_rest_transport.py)
- CERTI hosted behind the same gRPC contract:
  - [test_grpc_transport_certi_server.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_grpc_transport_certi_server.py)
