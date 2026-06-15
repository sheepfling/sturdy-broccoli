# RTI Options and Test Matrix

This document is the simplest current map of the `hla-2010` runtime surface.

This is document `2/4` in the backend documentation set.
For the canonical documentation hierarchy, see
[documentation_hierarchy.md](documentation_hierarchy.md).

The four backend docs are intentionally parallel:

1. [backend_route_inventory.md](backend_route_inventory.md): exhaustive route inventory and evidence anchors
2. [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): option inventory and recommended test matrix
3. [backend_capability_matrix.md](backend_capability_matrix.md): feature-capability coverage by backend
4. [backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance snapshot

It separates three concerns that are easy to blur together:

1. RTI runtime family
2. Python/Java interaction model
3. transport surface

The Python federate should only need to care about the backend name passed to
`hla2010_rti_runtime_common.create_rti_ambassador(...)`. Everything below that
line is repo/runtime plumbing. The temporary root workspace facade
`hla2010.rti` exposes the same helper during migration, but package-owned and
new public examples should prefer the split runtime package directly.

For the exhaustive route list, including named CERTI baselines and remote
transport-hosted variants, see
[backend_route_inventory.md](backend_route_inventory.md).

## Mental Model

When you choose an HLA path in this repo, you are really choosing:

1. the RTI implementation
2. how Python talks to that RTI
3. whether there is an extra transport hop between Python and the backend

Those are not the same choice.

Example:

- `certi`
  - RTI runtime: `CERTI`
  - Python/Java interaction: none
  - transport surface: usually none explicit from the caller, but the CERTI
    helper can also be hosted behind `grpc` or `rest`

- `hla2010_rti_runtime_common.create_rti_ambassador("certi", transport={"kind": "grpc", ...})`
  - RTI runtime: `CERTI`
  - Python/Java interaction: none exposed to the caller
  - transport surface: `grpc`

- `hla2010_rti_runtime_common.create_rti_ambassador("python")`
  - RTI runtime: in-memory Python reference RTI
  - Python/Java interaction: none
  - transport surface: none

## RTI Runtime Families

| Runtime family | What it is | Primary backend names | Current status |
|---|---|---|---|
| Python RTI | in-process reference RTI implemented in Python | `python` | strongest reference path for local semantics and clause work |
| Java shim | in-process Java-shaped test shim for bridge validation | `java-shim-jpype`, `java-shim-py4j` | useful for bridge and callback parity, not a vendor RTI |
| CERTI | real vendored 1516.1-2010 RTI in this repo | `certi` | strongest real-runtime path in this workspace |
| Pitch pRTI | real vendor runtime through Java adapters | `pitch-jpype`, `pitch-py4j` | available, but local activation/state constraints still matter |
| Portico | real vendor runtime through Java adapters | `portico-jpype`, `portico-py4j` | wiring exists; use only if a real local Portico install is present |

For CERTI specifically, keep two runtime baselines distinct:

- `certi-patched`: the repo-local vendored/modified CERTI build
- `certi-upstream`: a pristine upstream CERTI install selected only through the
  named upstream environment variables

Use `./tools/certi-easy smoke compare` when the goal is
vendor-vs-local attribution rather than generic CERTI smoke.

## Python/Java Interaction Models

These only matter when the chosen runtime is Java-facing.

| Interaction model | Meaning | Used by |
|---|---|---|
| none | pure Python path | `python`, `certi` |
| `jpype` | Python loads JVM in-process | `jpype`, `pitch-jpype`, `portico-jpype`, `java-shim-jpype` |
| `py4j` | Python talks to a separate JVM gateway process | `py4j`, `pitch-py4j`, `portico-py4j`, `java-shim-py4j` |

## Transport Surfaces

These are transport choices under the backend layer, not separate RTI families.

| Transport kind | Meaning | Typical use |
|---|---|---|
| implicit / none | direct in-process/backend call path | `python`, Java adapters, local `certi` default use |
| `subprocess-line` | line-oriented helper transport | primary local CERTI helper path |
| `grpc` | typed unary request/response remote transport | transport-hosted Python RTI and CERTI-hosted remote path |
| `rest` / `http-json` | typed JSON-over-HTTP remote transport | transport-hosted Python RTI and CERTI-facing transport seam |

Current remote callback contract for both `grpc` and `rest`:

- unary request/response
- callback polling through `evokeCallback` / `evokeMultipleCallbacks`
- no streaming callbacks yet

## Supported Backend Names

These are the backend names currently recognized by
[rti.py](../packages/hla2010-spec/src/hla2010/rti.py).

This section is generated from `create_backend(...)` by
[`./tools/rti-options generate`](../tools/rti-options).

<!-- GENERATED_BACKEND_ALIASES_START -->

### Pure Python

- `in-memory`
- `inmemory`
- `python`
- `python-in-memory`
- `python-inmemory`

### Generic Java Adapter Paths

- `java-jpype`
- `jpype`

- `java-py4j`
- `py4j`

These are only useful when you provide a Java RTI configuration explicitly.

### Pitch

- `java-pitch-jpype`
- `pitch-jpype`

- `java-pitch-py4j`
- `pitch-py4j`

### Portico

- `java-portico-jpype`
- `portico`
- `portico-jpype`

- `java-portico-py4j`
- `portico-py4j`

### CERTI

- `certi`
- `certi-native`
- `native-certi`

- `certi-jpype`
- `java-certi-jpype`

- `certi-py4j`
- `java-certi-py4j`

<!-- GENERATED_BACKEND_ALIASES_END -->

## Recommended Operational View

Use this simpler classification in practice:

| Operational bucket | Backend names |
|---|---|
| Python reference RTI | `python` |
| Java shim bridge proofs | `java-shim-jpype`, `java-shim-py4j` |
| Real CERTI | `certi` |
| Real Pitch | `pitch-jpype`, `pitch-py4j` |
| Real Portico | `portico-jpype`, `portico-py4j` |

That is the easiest level for planning and reporting.

## Test Matrix View

This is the practical matrix to use when deciding what to run.

| Backend family | Bridge model | Transport | Exchange | Timed | Sync | Ownership | Negotiated Ownership | Real runtime |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Python RTI | none | none | yes | yes | yes | yes | yes | no |
| Java shim | JPype | none | yes | partial | yes | yes | partial | no |
| Java shim | Py4J | none | yes | partial | yes | yes | partial | no |
| CERTI | native | subprocess-line | yes | partial | yes | yes | partial | yes |
| CERTI | JPype facade | subprocess-line | yes | partial | yes | yes | partial | yes |
| CERTI | Py4J facade | subprocess-line | yes | partial | yes | yes | partial | yes |
| CERTI hosted | native | `grpc` | yes | yes | yes | yes | not yet explicit | yes |
| CERTI hosted | native | `rest` | seam present | not yet explicit | not yet explicit | not yet explicit | no | yes |
| Python RTI hosted | none | `grpc` | yes | yes | yes | yes | yes | no |
| Python RTI hosted | none | `rest` | yes | yes | not yet explicit | not yet explicit | not yet explicit | no |
| Pitch | JPype | none | yes | yes | yes | yes | bridge-divergent | yes |
| Pitch | Py4J | none | yes | yes | yes | yes | bridge-divergent | yes |
| Portico | JPype | none | install-dependent | install-dependent | install-dependent | install-dependent | no | yes |
| Portico | Py4J | none | install-dependent | install-dependent | install-dependent | install-dependent | no | yes |

Interpretation:

- `yes` means automated coverage exists in this repo now
- `partial` means the shape exists but semantics are narrower than a full vendor RTI
- `not yet explicit` means the surface exists but this exact matrix row is not yet proved by dedicated tests
- `workspace-dependent` means the repo path exists, but the local vendor runtime state determines whether tests can actually run
- `install-dependent` means a valid local Portico installation is required

Current CERTI qualifier:

- the local CERTI synchronization and basic ownership routes are green
- the shared timed-exchange route is currently only `partial` because the
  CERTI backend does not implement `changeAttributeOrderType`

## Primary Test Files By Option

### Python reference RTI

- [test_python_backend_support_services.py](../tests/backends/test_python_backend_support_services.py), [test_python_backend_federation_extended.py](../tests/backends/test_python_backend_federation_extended.py), [test_python_backend_object_ownership_extended.py](../tests/backends/test_python_backend_object_ownership_extended.py), [test_python_backend_time_ddm_extended.py](../tests/backends/test_python_backend_time_ddm_extended.py)

### Java shim bridge proofs

- [test_java_profile_backend_matrix.py](../tests/vendors/test_java_profile_backend_matrix.py)
- [test_java_shim_backends.py](../tests/backends/test_java_shim_backends.py)

### Real CERTI

- [tests/vendors/README.md](../tests/vendors/README.md)
- [test_real_vendor_runtime_smoke.py](../tests/vendors/test_real_vendor_runtime_smoke.py)
- [`./tools/vendor-green`](../tools/vendor-green)

### CERTI behind transport surfaces

- [test_certi_backend_transport.py](../tests/backends/test_certi_backend_transport.py)
- [test_grpc_transport_certi_server.py](../tests/transport/test_grpc_transport_certi_server.py)
- [backend_route_inventory.md](backend_route_inventory.md)

### Python RTI behind transport surfaces

- [test_grpc_transport_python_server.py](../tests/transport/test_grpc_transport_python_server.py)
- [test_rest_transport.py](../tests/transport/test_rest_transport.py)

### Real Pitch

- [test_pitch_real_backend_matrix.py](../tests/vendors/test_pitch_real_backend_matrix.py)
- [test_real_vendor_runtime_smoke.py](../tests/vendors/test_real_vendor_runtime_smoke.py)
- Negotiated ownership is currently bridge-divergent rather than simply absent:
  - `pitch-jpype` and `pitch-py4j` do not fail in the same place
  - `pitch-py4j` gets farther on the owned-attribute release-request branch
  - `pitch-jpype` gets farther on the negotiated-offer branch and shows explicit FedPro session-drop / failed-resume lines
- See:
  - [pitch_negotiated_ownership_vendor_bug_2026-06-07.md](../packages/hla2010-rti-pitch-common/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md)
  - [diagnostic_summary.md](../analysis/pitch_negotiated_ownership_2026-06-07/diagnostic_summary.md)

### Runtime discovery and local install assumptions

- [test_real_rti.py](../tests/runtime/test_real_rti.py)

## Recommended Matrix For Day-To-Day Use

If the goal is a manageable default matrix, use this:

1. `python`
2. `java-shim-jpype`
3. `java-shim-py4j`
4. `certi`
5. `certi` over `grpc`
6. `python` hosted over `grpc`
7. `python` hosted over `rest`
8. `pitch-jpype`
9. `pitch-py4j`

That gives one matrix that covers:

- reference semantics
- both Python/Java bridge models
- real native RTI behavior
- remote transport behavior
- vendor runtime behavior

## What To Avoid Confusing

- CERTI is a native backend in this repo; Java bridge routes are reserved for Java-facing RTIs and test shims.
- `rest` and `grpc` are not separate RTI families; they are transport choices.
- `java-shim-*` is a test backend, not a real RTI.
- `pitch-*` and `portico-*` are runtime families, not transport kinds.

## Maintenance

If backend aliases change in
[rti.py](../packages/hla2010-spec/src/hla2010/rti.py),
rerun:

```bash
    ./tools/rti-options generate
```
