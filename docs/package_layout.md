# Package Layout

The repository separates public API definitions, backend abstractions, concrete
RTI implementations, transport adapters, and verification assets.

For the stricter rule table about what may import what, use
[`import_boundary_rules.md`](import_boundary_rules.md).

For the machine-derived installable package dependency graph, use
[`package_dependency_tree.md`](package_dependency_tree.md).

For the shortest answer to hierarchy plus versioning, use
[`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md).

This is a monorepo workspace with multiple installable package roots. The
repository root is tooling-only: it keeps pytest, Ruff, and Pyright
configuration, but it is not a Python distribution. The architectural namespace
root is `hla`, contributed by PEP 420 namespace packages. The 2010 standard API
is owned by `packages/hla-rti1516e/src/hla/rti1516e/`; cross-version factory and
discovery logic is owned by `packages/hla-rti-core/src/hla/rti/`. Concrete
backend, transport, FOM, and support implementations live in package-owned
directories under `packages/*/src`.

## Front Door

If you are trying to find the supported HLA entry points, start here:

- `packages/hla-rti1516e/src/hla/rti1516e/`: strict IEEE 1516.1-2010 API surface
- `packages/hla-rti1516-2025/src/hla/rti1516_2025/`: strict IEEE 1516.1-2025 API surface
- `packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py`: strict `RTIambassador` protocol
- `packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py`: strict `FederateAmbassador` protocol and no-op callback sink
- `packages/hla-rti-core/src/hla/rti/`: cross-version backend/spec discovery and ambassador creation
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/`: in-memory Python RTI backend
- `packages/hla-backend-python2025/src/hla/backends/python2025/`: main Python RTI backend for IEEE 1516.1-2025
- `packages/hla-backend-shim/src/hla/backends/shim/`: wrapper-only compatibility alias over the main 2025 backend lane
- `packages/hla-transport-grpc/src/hla.transports.grpc/`: hosted gRPC transport surface
- `./tools/target-radar` and `examples/target_radar_simulation.py`: Target/Radar operator/example entrypoints

Do not use `pip install -e .` at the repository root. Install the split
packages directly, starting with `packages/hla-rti1516e`, or use
`./tools/bootstrap python` to install the editable workspace package set.

Each package's `pyproject.toml` should declare only package-owned
`source_roots`. For `hla-rti1516e`,
`packages/hla-rti1516e/src/hla/rti1516e/` is the owned implementation root.

## Core API

- `packages/hla-rti1516e/src/hla/rti1516e/__init__.py`: canonical package root exports for the 2010 API.
- `packages/hla-rti1516-2025/src/hla/rti1516_2025/__init__.py`: canonical package root exports for the 2025 API.
- `packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py`: strict source-shaped RTI protocol.
- `packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py`: strict source-shaped federate callback protocol.
- `packages/hla-rti1516e/src/hla/rti1516e/spec_inventory.py`: plain-text method-name inventory used by the spec layer.
- `packages/hla-rti1516e/src/hla/rti1516e/spec_sources.py`: readable Java/C++ source references.
- `packages/hla-rti1516e/src/hla/rti1516e/spec_refs.py`: clause and service references.
- `packages/hla-rti1516e/src/hla/rti1516e/handles.py`, `datatypes.py`, `logical_time.py`, `enums.py`, `time.py`: HLA value types and runtime value helpers.
- `packages/hla-rti1516e/src/hla/rti1516e/raw_api.py`: source-derived metadata scaffold.

## Backend Abstractions

- `packages/hla-backend-common/src/hla/backends/common/`: shared backend conversion, native handle registries, type inference helpers, backend-neutral invocation resolution, and the canonical shared adapter contract.
- `packages/hla-backend-common/src/hla/backends/common/time_management.py`: backend-neutral logical-time, GALT/LITS, queued-TSO, and grant-decision helpers shared by the Python RTI and repo verification.
- `packages/hla-bridge-java-common/src/hla.bridges.java.common/`: shared Java bridge support, callback dispatching, Java runtime discovery, return-type helpers, and Java-side value conversion.
- `packages/hla-rti-core/src/hla.rti/`: shared vendor-runtime process lifecycle, backend registry, and backend-neutral RTI factory helpers.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema.
- `packages/hla-transport-common/src/hla.transports.common/`: shared hosted transport request-processing helpers used by multiple wire protocols.
- `packages/hla-transport-grpc/src/hla.transports.grpc/`: canonical gRPC transport infrastructure with `.proto` schema, checked-in Python stubs, client adapter, and hosted server helpers.
- `packages/hla-transport-rest/src/hla/transports/rest/`: canonical REST transport infrastructure with the OpenAPI-aligned Python client adapter and hosted server runtime.
- `packages/hla-transport-common/src/hla.transports.common/transport_codecs.py`: backend-neutral transport codec helpers shared by hosted transport layers.

Transport packages are not backend families. They are the wire layer beneath a
backend-neutral ambassador surface.

## Concrete Backends

- `packages/hla-backend-inmemory/src/hla/backends/inmemory/`: canonical pure in-memory RTI backend implementation package.
- `packages/hla-backend-python2025/src/hla/backends/python2025/`: main full Python-owned IEEE 1516.1-2025 RTI implementation package.
- `packages/hla-backend-shim/src/hla/backends/shim/`: maintained compatibility-wrapper package that delegates runtime semantics to `hla-backend-python2025`.
- `packages/hla-backend-python2025/src/hla/backends/python2025/backend.py`, `backend_factory_runtime.py`, `runtime_state.py`, `*_runtime.py`, and `*_surface_mixin.py`: thin public shell plus the focused runtime/state/surface split that now carries the main 2025 RTI implementation.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/state.py`, `engine.py`, `reporting.py`: shared backend state, handle registry, and service-report support.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/federation.py`, `federation_lifecycle.py`, `federation_sync.py`: federation lifecycle and synchronization services.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/object.py`, `object_delivery.py`: object update/delete, interaction delivery, and transport callbacks.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/mom.py`, `mom_actions.py`, `mom_reporting.py`: MOM dispatch/decoding and MOM/service-report emission.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/mom_catalog.py`: Python RTI-owned MOM exposure-model and negative-matrix generation derived from the merged FOM/MIM catalog.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/time.py`, `time_queue.py`, `time_services.py`: queue/grant mechanics and public time-service/validation submodules.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/save_restore.py`, `callbacks.py`, `declaration.py`, `ownership.py`, `ddm.py`: remaining focused Python backend service domains.
- `packages/hla-backend-certi/src/hla/backends/certi/`: CERTI runtime, transport, service adapter, and Java-profile CERTI backend package.
- `packages/hla-vendor-pitch/src/hla.vendors.pitch/`: shared Pitch runtime discovery and process-launch helpers.
- `packages/hla-bridge-java-jpype/src/hla.bridges.java.jpype/` and `packages/hla-bridge-java-py4j/src/hla.bridges.java.py4j/`: generic Java RTI bridge packages through JPype and Py4J.
- `packages/hla-vendor-pitch-jpype/src/hla.vendors.pitch.jpype/` and `packages/hla-vendor-pitch-py4j/src/hla.vendors.pitch.py4j/`: Pitch-specific plugin descriptors and compatibility exports for the generic Java bridge packages.
- `packages/hla-vendor-portico/src/hla/vendors/portico/`: Portico runtime discovery and JPype/Py4J plugin descriptors.
- `packages/hla-backend-certi/docs/`, `packages/hla-vendor-pitch/docs/`, and `packages/hla-vendor-portico/docs/`: vendor-owned runbooks, findings, and package-local operational notes.
Java transport stubs generated from the RTI REST or gRPC transport contracts
are not checked in and are currently out of scope. Java integration in this
repo is through the backend families above, not through generated transport
bindings.

## Backend Factories

- `packages/hla-rti-core/src/hla/rti/`: neutral spec/backend discovery and ambassador factory layer.
- `packages/hla-rti1516e/src/hla/rti1516e/factory.py`: 2010-local factory helper that bakes in `spec="rti1516e"`.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/factory.py`: pure-Python backend factories.
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py`: pure-Python backend plugin descriptor.
- `packages/hla-backend-certi/src/hla/backends/certi/certi/plugin.py`: CERTI backend plugin descriptors.
- `packages/hla-backend-certi/src/hla/backends/certi/certi/plugin.py`: CERTI backend factories and plugin descriptors.

Installable backend packages register RTI implementations through the
`hla.rti_backends` entry point group. Entry points must return an
`hla.backends.common.RTIBackendPlugin` descriptor. The descriptor names the backend,
its aliases, its backend family, and a lazy `create_backend(options)` callable.
Workspace users may call
`hla.rti.discover_backends()` for a deduplicated list of installed
backend plugins, and `hla.rti.discover_backends(probe=True)` when
tooling needs to check whether optional vendor runtimes are actually
configured on the local machine. The root facade intentionally does not own
plugin contract types or low-level transport registration helpers. Package-owned code should import directly
from `hla.rti`, and shared plugin contract types should
import directly from `hla.backends.common`.

The current package set is:

- `hla-rti1516e`: strict IEEE 1516.1-2010 spec surface, common HLA value types,
  exceptions, FOM/MOM helpers needed by federates, and the backend adapter
  contract.
- `hla-rti1516-2025`: strict IEEE 1516.1-2025 spec surface, value types, FOM helpers, and 2025-local factory surface.
- `hla-backend-inmemory`: pure in-memory Python RTI backend.
- `hla-backend-python2025`: main full executable Python RTI backend for IEEE 1516.1-2025.
- `hla-backend-shim`: wrapper-only compatibility alias over `hla-backend-python2025`.
- `hla-backend-certi`: CERTI transport/runtime adapter package.
- `hla-backend-common`: shared backend conversion support layer.
- `hla-bridge-java-common`: shared Java RTI support layer.
- `hla-rti-core`: shared vendor-runtime process helper layer.
- `hla-transport-common`: shared hosted transport request-processing helpers.
- `hla-bridge-java-jpype`: generic JPype Java RTI bridge and `jpype` backend plugin.
- `hla-bridge-java-py4j`: generic Py4J Java RTI bridge and `py4j` backend plugin.
- `hla-vendor-pitch`: shared Pitch runtime discovery and process launch.
- `hla-vendor-pitch-jpype`: Pitch Java RTI adapter through JPype.
- `hla-vendor-pitch-py4j`: Pitch Java RTI adapter through Py4J.
- `hla-vendor-portico`: Portico Java RTI adapters through JPype and Py4J.
- `hla-transport-grpc`: gRPC transport adapters and hosted servers.
- `hla-transport-rest`: REST transport adapters and hosted servers.
- `hla-verification`: shared two-federate packet, timeline, summary, and writer helpers for repo-internal verification.
- `hla-fom-target-radar`: concrete target/radar FOM resources and
  target/radar scenario/example package.
- `hla-fom-proto2025-message-test`: package-owned Proto2025 MessageTest showcase runner.
- `hla-fom-proto2025-space-lite`: package-owned Proto2025 SpaceLite showcase runner.
- `hla-fom-proto2025-time-mgmt-test`: package-owned Proto2025 TimeMgmtTest showcase runner.

## Architecture Table

| Package | Class | May depend on | Must not depend on |
| --- | --- | --- | --- |
| `hla-rti1516e` | root | `-` | all internal packages |
| `hla-rti1516-2025` | root | `-` | all internal packages except shared runtime abstractions |
| `hla-backend-common` | shared | `hla-rti1516e` | backend, vendor, transport, leaf packages |
| `hla-rti-core` | shared | `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-transport-common` | backend, vendor bridge, leaf packages |
| `hla-transport-common` | shared | `hla-rti1516e` | concrete backend, vendor, leaf packages |
| `hla-verification` | shared | `hla-rti1516e`, `hla-backend-common`, `hla-rti-core`, `hla-fom-* showcase leaves` | backend, vendor, transport packages |
| `hla-bridge-java-common` | vendor/common | `hla-rti1516e`, `hla-backend-common` | python backend, transport, leaf packages |
| `hla-backend-inmemory` | backend | `hla-rti1516e`, `hla-backend-common` | java-common, vendor, transport, leaf packages |
| `hla-backend-python2025` | backend | `hla-rti1516-2025`, `hla-backend-common`, `hla-rti-core` | shim backflow, vendor, transport, leaf packages |
| `hla-backend-shim` | compatibility-wrapper | `hla-rti1516-2025`, `hla-rti-core`, `hla-backend-python2025` | any path that would re-own core 2025 runtime semantics, plus vendor, transport, leaf packages |
| `hla-backend-certi` | backend | `hla-rti1516e`, `hla-bridge-java-common`, `hla-rti-core` | python backend, transport, leaf packages |
| `hla-bridge-java-jpype` | backend | `hla-rti1516e`, `hla-bridge-java-common` | python backend, transport, leaf packages |
| `hla-bridge-java-py4j` | backend | `hla-rti1516e`, `hla-bridge-java-common` | python backend, transport, leaf packages |
| `hla-vendor-pitch` | vendor/common | `hla-rti1516e`, `hla-bridge-java-common`, `hla-rti-core` | python backend, transport, leaf packages |
| `hla-vendor-pitch-jpype` | vendor | `hla-rti1516e`, `hla-vendor-pitch`, `hla-bridge-java-jpype` | python backend, transport, leaf packages |
| `hla-vendor-pitch-py4j` | vendor | `hla-rti1516e`, `hla-vendor-pitch`, `hla-bridge-java-py4j` | python backend, transport, leaf packages |
| `hla-vendor-portico` | vendor | `hla-rti1516e`, `hla-bridge-java-common`, `hla-bridge-java-jpype`, `hla-bridge-java-py4j` | python backend, transport, leaf packages |
| `hla-transport-grpc` | transport | `hla-rti1516e`, `hla-transport-common`, `hla-rti-core` | concrete backend and vendor packages |
| `hla-transport-rest` | transport | `hla-rti1516e`, `hla-transport-common`, `hla-rti-core` | concrete backend and vendor packages |
| `hla-fom-target-radar` | leaf | `hla-rti1516e`, `hla-rti1516-2025`, `hla-rti-core` | concrete backend, vendor, transport packages |
| `hla-fom-proto2025-message-test` | leaf | `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-backend-inmemory` | concrete backend, vendor, transport packages |
| `hla-fom-proto2025-space-lite` | leaf | `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-backend-inmemory` | concrete backend, vendor, transport packages |
| `hla-fom-proto2025-time-mgmt-test` | leaf | `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-backend-inmemory` | concrete backend, vendor, transport packages |

Import isolation for the installable `packages/*` trees is enforced by
[`tests/test_package_import_isolation.py`](../tests/test_package_import_isolation.py).
That test rejects direct imports from `hla.rti1516e.testing.*` and any sibling
package-root import outside the explicit allowlist for each family.
Dependency metadata is enforced by
[`tests/test_package_dependency_metadata.py`](../tests/test_package_dependency_metadata.py).

Source checkouts should use editable installs or the explicit pytest
`pythonpath` configuration. Production package code must not mutate
`sys.path`, import `_bootstrap`, walk package `__path__`, derive repository
roots from `__file__`, or compute `__all__` from `globals()`.

Backend plugin contracts now live in
`hla.backends.common.plugin_api`. Runtime factory helpers now live in
`hla.rti`, while `hla.rti1516e.rti` remains a narrow 2010-local helper for
backend discovery and ambassador creation. Package-owned code should import
runtime factory helpers from `hla.rti` directly; registry, transport, and
private helper access must stay in the owning split packages.

Backend base implementation now lives in
`hla.backends.common.base`, and the package root
`hla.backends.common` is the supported import surface for the shared
adapter contract.

Java runtime discovery helpers now live only in
`hla.bridges.java.common.java_runtime` and the `hla.bridges.java.common`
package root.

## Runtime Discovery

- Vendor runtime discovery now imports directly from their owning packages:
  `hla.backends.certi.real_rti_certi`,
  `hla.vendors.pitch.real_rti_pitch`,
  `hla.vendors.portico.real_rti_portico`, and
  `hla.rti.real_rti_process`.

## Verification And Scenarios

- `packages/hla-verification/src/hla/verification/`: canonical generic suite pairs, configs, scenario bodies, packet types, summary/timeline shaping, and writer helpers.
- `packages/hla-verification/src/hla/verification/section8_matrix.py`: public Section 8 backend-matrix scenarios owned by the verification harness.
- `packages/hla-bridge-java-common/src/hla.bridges.java.common/java_shim_*.py`: Java-shaped shim support used by Java-profile backends and repo verification flows.
- `packages/hla-verification/src/hla/verification/repo_internal/verification/`: repo-internal proof packets, backend matrices, vendor reports, and two-federate artifact writers.
- `packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/`: canonical Target/Radar internal scenario implementation and FOM helper entrypoints.
- `examples/`: runnable scripts and example-only assets. Nothing under
  `examples/` is part of the installable `hla` package set.
- `examples/<scenario>/`: scenario-local scratch or notes only. Canonical reusable assets such as FOM XML live under their owning package roots.
Testing is not part of the public `hla` runtime namespace. Repo-only proof and
packet helpers now live under `packages/hla-verification/src/hla/verification/repo_internal/verification/`,
while `hla-verification` is the only supported public verification
package. Scenario imports should target the owning split package directly
rather than a root `hla.rti1516e.scenarios` facade.

The Target/Radar leaf package keeps vendor-specific launch policy and proof
packet assembly out of its installable metadata. Vendor-backed suite profiles
are injected by repo-internal callers rather than imported through the leaf
package.

## Setup Order

For environment setup and install order, use
[`python_environment.md`](python_environment.md). The short version is:

1. bootstrap Python first
2. activate `.venv`
3. run a pure-Python smoke path
4. add bridge extras if needed
5. only then install or build CERTI or Pitch

Legacy flat backend import paths are removed for split Python RTI and gRPC
transport code. Import from canonical split package implementations instead.

Tests may still mention removed paths only to assert that those compatibility
modules no longer import.

## Example Boundary Rules

Keep example entrypoints thin:

- parse CLI arguments
- construct a backend or scenario factory
- call into the owning split package such as
  `hla.foms.target_radar._internal.*` or another reusable package module
- load reusable data or FOM assets from an owning package root, not from a
  duplicate copy under `examples/`

Keep reusable scenario logic out of `examples/` so tests can import the same
code without depending on a script layout.
