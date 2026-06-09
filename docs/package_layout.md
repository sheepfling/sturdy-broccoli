# Package Layout

The repository separates public API definitions, backend abstractions, concrete
RTI implementations, transport adapters, and verification assets.

This is a monorepo workspace with multiple installable package roots. The
stable import surface is the `src/hla2010/` package, while concrete backend
and support implementations live in package-owned directories under
`packages/*/src`. The root distribution aggregates those roots for editable
checkout workflows and keeps compatibility facades for legacy imports. The
top-level `hla2010/` directory is now a narrow shim area rather than the main
package root.

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
- `packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/`: shared backend conversion, native handle registries, and type inference helpers.
- `packages/hla2010-rti-java-common/src/hla2010_rti_java_common/`: shared Java bridge support, overload resolution, callback dispatching, and Java-side value conversion.
- `packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/`: shared vendor-runtime process lifecycle and loopback TCP helpers.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema.
- `packages/hla2010-rti-transport-grpc/src/hla2010_rti_transport_grpc/`: canonical gRPC transport infrastructure with `.proto` schema, checked-in Python stubs, client adapter, and hosted server helpers.
- `packages/hla2010-rti-transport-rest/src/hla2010_rti_transport_rest/`: canonical REST transport infrastructure with the OpenAPI-aligned Python client adapter and hosted server runtime.

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
- `src/hla2010/backends/certi/`, `src/hla2010/backends/certi_java/`, `src/hla2010/backends/jpype/`, and `src/hla2010/backends/py4j/`: compatibility facades for the split backend packages.

Java transport stubs generated from the RTI REST or gRPC transport contracts are not checked in and are currently out of scope. Java integration in this repo is through the backend families above, not through generated transport bindings.

The legacy `src/hla2010/backends/grpc_transport/`, `src/hla2010/backends/rest_transport/`, and `src/hla2010/backends/rest_transport_host.py` modules are compatibility facades over the split transport packages.

## Backend Factories

- `src/hla2010/rti.py`: top-level backend plugin descriptor, entry point discovery, and transport registry.
- `packages/hla2010-rti-python/src/hla2010_rti_python/factory.py`: pure-Python backend factories.
- `packages/hla2010-rti-python/src/hla2010_rti_python/plugin.py`: pure-Python backend plugin descriptor.
- `src/hla2010/backends/java_plugins.py`: compatibility exports for split Java-family plugin descriptors.
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/plugin.py`: CERTI backend plugin descriptors.
- `src/hla2010/backends/certi/__init__.py`: CERTI backend and transport factories.

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

Import isolation for the installable `packages/*` trees is enforced by
[`tests/test_package_import_isolation.py`](../tests/test_package_import_isolation.py).
That test rejects direct imports from `hla2010.testing.*` and any sibling
package-root import outside the explicit allowlist for each family.

During the transition, this repository keeps in-tree fallback plugin discovery
so editable/source checkouts work even before the package is physically split.

## Runtime Discovery

- `src/hla2010/real_rti.py`: compatibility facade.
- `src/hla2010/real_rti_certi.py`, `src/hla2010/real_rti_pitch.py`, `src/hla2010/real_rti_portico.py`: compatibility facades for split vendor runtime discovery packages.
- `src/hla2010/real_rti_process.py`: compatibility facade for split process and TCP listener helpers.

## Verification And Scenarios

- `src/hla2010/testing/`: reusable scenario and artifact-producing test helpers.
- `src/hla2010/testing/scenario_support.py`, `scenario_exchange.py`, `scenario_sync.py`, `scenario_ownership.py`, `scenario_basic.py`: scenario-family split beneath the compatibility facade `src/hla2010/testing/scenarios.py`.
- `src/hla2010/testing/java_shim_types.py`, `java_shim_backend.py`, `java_shim_kernel.py`, `java_shim_factory.py`: Java-shaped shim split beneath the compatibility facade `src/hla2010/testing/java_shim.py`.
- `src/hla2010/testing/two_federate_suite_runner.py`: suite coordinator.
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/`: canonical generic suite pairs, configs, scenario bodies, packet types, summary/timeline shaping, and writer helpers.
- `packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/testing/two_federate_suite_profiles.py`: target/radar-owned profile policy for the composite suite.
- `packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/scenarios/`: canonical Target/Radar scenario implementation and FOM helper entrypoints.
- `src/hla2010/scenarios/`: compatibility facades plus reusable domain scenarios that are safe to import from both tests and example entrypoints.
- `examples/`: runnable scripts and example-only assets. Nothing under `examples/` is part of the installable `hla2010` package.
- `examples/<scenario>/`: scenario-local scratch or notes only. Canonical reusable assets such as FOM XML live under their owning package roots.
- `src/hla2010/verification.py` and `src/hla2010/conformance.py`: evidence and requirements-ledger support.

`src/hla2010/testing/` is repo-internal support code, not public runtime API. The
wheel excludes it so the installable package stays focused on the runtime
surface rather than on packet generation and test helpers.

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

## Example Boundary Rules

Keep example entrypoints thin:

- parse CLI arguments
- construct a backend or scenario factory
- call into `hla2010.scenarios.*` or another reusable package module
- load reusable data or FOM assets from an owning package root, not from a
  duplicate copy under `examples/`

Keep reusable scenario logic out of `examples/` so tests can import the same
code without depending on a script layout.
