# Package Layout

The repository separates public API definitions, backend abstractions, concrete
RTI implementations, transport adapters, and verification assets.

For the stricter rule table about what may import what, use
[`import_boundary_rules.md`](import_boundary_rules.md).

For the machine-derived installable package dependency graph, use
[`package_dependency_tree.md`](package_dependency_tree.md).

This is a monorepo workspace with multiple installable package roots. The
repository root is tooling-only: it keeps pytest, Ruff, and Pyright
configuration, but it is not a Python distribution. The architectural root is
`hla2010-spec`, whose package manifest owns `src/hla2010/`. Concrete backend
and support implementations live in package-owned directories under
`packages/*/src`.

Do not use `pip install -e .` at the repository root. Install the split
packages directly, starting with `packages/hla2010-spec`, or use
`./scripts/bootstrap_python.sh` to install the editable workspace package set.

For packages whose split status is `implementation-moved`, the owning package's
`pyproject.toml` should declare only package-owned `source_roots`. Files under
`src/hla2010/` may re-export or forward to those packages, but they are not
counted as owned implementation roots anymore. For `hla2010-spec`,
`src/hla2010/` is the owned implementation root.

## Core API

- `src/hla2010/spec/`: standalone clean Python spec package.
- `src/hla2010/spec_inventory.py`: plain-text method-name inventory used by the clean spec layer.
- `src/hla2010/spec_sources.py`: readable Java/C++ source references used in the clean spec docstrings.
- `src/hla2010/runtime_api.py`: explicit runtime-facing Pythonic convenience layer over the spec contract.
- `src/hla2010/api.py`: compatibility shim that re-exports the runtime layer.
- `src/hla2010/_spec_impl.py`: internal implementation module behind `hla2010.spec`.
- `src/hla2010/handles.py`, `src/hla2010/types.py`, `src/hla2010/enums.py`, `src/hla2010/time.py`: shared HLA value types.
- `src/hla2010/raw_api.py`: source-derived API scaffold.

## Backend Abstractions

- `src/hla2010/backends/base.py`: backend interface, invocation envelope, and delegating ambassador.
- `src/hla2010/backends/transport.py`: typed transport request/response boundary.
- `packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/`: shared backend conversion, native handle registries, type inference helpers, and backend-neutral invocation resolution.
- `packages/hla2010-rti-java-common/src/hla2010_rti_java_common/`: shared Java bridge support, callback dispatching, return-type helpers, and Java-side value conversion.
- `packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/`: shared vendor-runtime process lifecycle and loopback TCP helpers.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema.
- `packages/hla2010-rti-transport-common/src/hla2010_rti_transport_common/`: shared hosted transport request-processing helpers used by multiple wire protocols.
- `packages/hla2010-rti-transport-grpc/src/hla2010_rti_transport_grpc/`: canonical gRPC transport infrastructure with `.proto` schema, checked-in Python stubs, client adapter, and hosted server helpers.
- `packages/hla2010-rti-transport-rest/src/hla2010_rti_transport_rest/`: canonical REST transport infrastructure with the OpenAPI-aligned Python client adapter and hosted server runtime.
- `src/hla2010/transport_codecs.py`: backend-neutral transport codec helpers shared by hosted transport layers.

Transport packages are not backend families. They are the wire layer beneath a
backend-neutral ambassador surface.

## Concrete Backends

- `packages/hla2010-rti-python/src/hla2010_rti_python/`: canonical pure in-memory RTI backend implementation package.
- `src/hla2010/backends/python/`: compatibility facades for the split Python backend.
- `packages/hla2010-rti-python/src/hla2010_rti_python/state.py`, `engine.py`, `reporting.py`: shared backend state, handle registry, and service-report support.
- `packages/hla2010-rti-python/src/hla2010_rti_python/federation.py`, `federation_lifecycle.py`, `federation_sync.py`: federation lifecycle and synchronization services.
- `packages/hla2010-rti-python/src/hla2010_rti_python/object.py`, `object_delivery.py`: object update/delete, interaction delivery, and transport callbacks.
- `packages/hla2010-rti-python/src/hla2010_rti_python/mom.py`, `mom_actions.py`, `mom_reporting.py`: MOM dispatch/decoding and MOM/service-report emission.
- `packages/hla2010-rti-python/src/hla2010_rti_python/time.py`, `time_queue.py`, `time_services.py`: queue/grant mechanics and public time-service/validation submodules.
- `packages/hla2010-rti-python/src/hla2010_rti_python/save_restore.py`, `callbacks.py`, `declaration.py`, `ownership.py`, `ddm.py`: remaining focused Python backend service domains.
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/`: CERTI runtime, transport, service adapter, and Java-profile CERTI backend package.
- `packages/hla2010-rti-pitch-common/src/hla2010_rti_pitch_common/`: shared Pitch runtime discovery and process-launch helpers.
- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/` and `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/`: generic Java RTI bridge packages through JPype and Py4J.
- `packages/hla2010-rti-pitch-jpype/src/hla2010_rti_pitch_jpype/` and `packages/hla2010-rti-pitch-py4j/src/hla2010_rti_pitch_py4j/`: Pitch-specific plugin descriptors and compatibility exports for the generic Java bridge packages.
- `packages/hla2010-rti-portico/src/hla2010_rti_portico/`: Portico runtime discovery and JPype/Py4J plugin descriptors.
- `packages/hla2010-rti-certi/docs/`, `packages/hla2010-rti-pitch-common/docs/`, and `packages/hla2010-rti-portico/docs/`: vendor-owned runbooks, findings, and package-local operational notes.
Java transport stubs generated from the RTI REST or gRPC transport contracts are not checked in and are currently out of scope. Java integration in this repo is through the backend families above, not through generated transport bindings.

The legacy `src/hla2010/backends/grpc_transport/` modules are compatibility
facades over the split transport packages.

## Backend Factories

- `src/hla2010/rti.py`: top-level backend plugin descriptor, entry point discovery, and transport registry.
- `packages/hla2010-rti-python/src/hla2010_rti_python/factory.py`: pure-Python backend factories.
- `packages/hla2010-rti-python/src/hla2010_rti_python/plugin.py`: pure-Python backend plugin descriptor.
- `src/hla2010/backends/java_plugins.py`: compatibility exports for split Java-family plugin descriptors.
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/plugin.py`: CERTI backend plugin descriptors.
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/plugin.py`: CERTI backend factories and plugin descriptors.

Installable backend packages register RTI implementations through the
`hla2010.rti_backends` entry point group. Entry points must return an
`hla2010.rti.RTIBackendPlugin` descriptor. The descriptor names the backend,
its aliases, its backend family, and a lazy `create_backend(options)` callable.
Use `hla2010.rti.iter_rti_backend_plugins()` for a deduplicated list of
installed backend plugins, and `hla2010.rti.discover_rti_backends(probe=True)`
when tooling needs to check whether optional vendor runtimes are actually
configured on the local machine.

The intended package split is:

- `hla2010-spec`: clean IEEE 1516.1-2010 spec surface, common HLA value types,
  exceptions, FOM/MOM helpers needed by federates, and the backend adapter
  contract.
- `hla2010-rti-python`: pure in-memory Python RTI backend.
- `hla2010-rti-certi`: CERTI transport/runtime adapter package.
- `hla2010-rti-backend-common`: shared backend conversion support layer.
- `hla2010-rti-java-common`: shared Java RTI support layer.
- `hla2010-rti-runtime-common`: shared vendor-runtime process helper layer.
- `hla2010-rti-transport-common`: shared hosted transport request-processing helpers.
- `hla2010-rti-java-jpype`: generic JPype Java RTI bridge and `jpype` backend plugin.
- `hla2010-rti-java-py4j`: generic Py4J Java RTI bridge and `py4j` backend plugin.
- `hla2010-rti-pitch-common`: shared Pitch runtime discovery and process launch.
- `hla2010-rti-pitch-jpype`: Pitch Java RTI adapter through JPype.
- `hla2010-rti-pitch-py4j`: Pitch Java RTI adapter through Py4J.
- `hla2010-rti-portico`: Portico Java RTI adapters through JPype and Py4J.
- `hla2010-rti-transport-grpc`: gRPC transport adapters and hosted servers.
- `hla2010-rti-transport-rest`: REST transport adapters and hosted servers.
- `hla2010-verification-harness`: shared two-federate packet, timeline, summary, and writer helpers for repo-internal verification.
- `hla2010-fom-target-radar`: concrete target/radar FOM resources and
  target/radar scenario/example package.

## Architecture Table

| Package | Class | May depend on | Must not depend on |
| --- | --- | --- | --- |
| `hla2010-spec` | root | `-` | all internal packages |
| `hla2010-rti-backend-common` | shared | `hla2010-spec` | backend, vendor, transport, leaf packages |
| `hla2010-rti-runtime-common` | shared | `hla2010-spec` | backend, vendor bridge, transport, leaf packages |
| `hla2010-rti-transport-common` | shared | `hla2010-spec` | concrete backend, vendor, leaf packages |
| `hla2010-verification-harness` | shared | `hla2010-spec` | backend, vendor, transport packages |
| `hla2010-rti-java-common` | vendor/common | `hla2010-spec`, `hla2010-rti-backend-common` | python backend, transport, leaf packages |
| `hla2010-rti-python` | backend | `hla2010-spec`, `hla2010-rti-backend-common` | java-common, vendor, transport, leaf packages |
| `hla2010-rti-certi` | backend | `hla2010-spec`, `hla2010-rti-java-common`, `hla2010-rti-runtime-common` | python backend, transport, leaf packages |
| `hla2010-rti-java-jpype` | backend | `hla2010-spec`, `hla2010-rti-java-common` | python backend, transport, leaf packages |
| `hla2010-rti-java-py4j` | backend | `hla2010-spec`, `hla2010-rti-java-common` | python backend, transport, leaf packages |
| `hla2010-rti-pitch-common` | vendor/common | `hla2010-spec`, `hla2010-rti-runtime-common` | python backend, transport, leaf packages |
| `hla2010-rti-pitch-jpype` | vendor | `hla2010-spec`, `hla2010-rti-pitch-common`, `hla2010-rti-java-jpype` | python backend, transport, leaf packages |
| `hla2010-rti-pitch-py4j` | vendor | `hla2010-spec`, `hla2010-rti-pitch-common`, `hla2010-rti-java-py4j` | python backend, transport, leaf packages |
| `hla2010-rti-portico` | vendor | `hla2010-spec`, `hla2010-rti-java-jpype`, `hla2010-rti-java-py4j` | python backend, transport, leaf packages |
| `hla2010-rti-transport-grpc` | transport | `hla2010-spec`, `hla2010-rti-transport-common` | concrete backend and vendor packages |
| `hla2010-rti-transport-rest` | transport | `hla2010-spec`, `hla2010-rti-transport-common` | concrete backend and vendor packages |
| `hla2010-fom-target-radar` | leaf | `hla2010-spec`, `hla2010-verification-harness` | concrete backend, vendor, transport packages |

Import isolation for the installable `packages/*` trees is enforced by
[`tests/test_package_import_isolation.py`](../tests/test_package_import_isolation.py).
That test rejects direct imports from `hla2010.testing.*` and any sibling
package-root import outside the explicit allowlist for each family.
Dependency metadata is enforced by
[`tests/test_package_dependency_metadata.py`](../tests/test_package_dependency_metadata.py).

Source checkouts should use editable installs or the explicit pytest
`pythonpath` configuration. Production package code must not mutate
`sys.path`, import `_bootstrap`, walk package `__path__`, derive repository
roots from `__file__`, or compute `__all__` from `globals()`.

## Runtime Discovery

- Vendor runtime discovery now imports directly from their owning packages:
  `hla2010_rti_certi.real_rti_certi`,
  `hla2010_rti_pitch_common.real_rti_pitch`,
  `hla2010_rti_portico.real_rti_portico`, and
  `hla2010_rti_runtime_common.real_rti_process`.

## Verification And Scenarios

- `packages/hla2010-verification-harness/src/hla2010_verification_harness/`: canonical generic suite pairs, configs, scenario bodies, packet types, summary/timeline shaping, and writer helpers.
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py`: public Section 8 backend-matrix scenarios owned by the verification harness.
- `packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_shim_*.py`: Java-shaped shim support used by Java-profile backends and repo verification flows.
- `src/hla2010_repo_internal/verification/`: repo-internal proof packets, backend matrices, vendor reports, and two-federate artifact writers.
- `packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/scenarios/`: canonical Target/Radar scenario implementation and FOM helper entrypoints.
- `src/hla2010/scenarios/`: compatibility facades that forward to the split scenario packages for workspace-stable imports.
- `examples/`: runnable scripts and example-only assets. Nothing under `examples/` is part of the installable `hla2010` package.
- `examples/<scenario>/`: scenario-local scratch or notes only. Canonical reusable assets such as FOM XML live under their owning package roots.
- `src/hla2010/verification.py` and `src/hla2010/conformance.py`: evidence and requirements-ledger support.

Testing is not part of the public `hla2010` runtime namespace. Repo-only proof
and packet helpers now live under `src/hla2010_repo_internal/verification/`,
while `hla2010-verification-harness` is the only supported public verification
package.

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

Legacy flat backend import paths are compatibility facades. New code should
import from the canonical split package implementations instead.

Compatibility imports may still appear in tests that explicitly verify migration
aliases, and in a small number of operator/test entrypoints that exercise the
workspace facade on purpose. Those are compatibility checks, not package-graph
ownership.

## Example Boundary Rules

Keep example entrypoints thin:

- parse CLI arguments
- construct a backend or scenario factory
- call into `hla2010.scenarios.*` or another reusable package module
- load reusable data or FOM assets from an owning package root, not from a
  duplicate copy under `examples/`

Keep reusable scenario logic out of `examples/` so tests can import the same
code without depending on a script layout.
