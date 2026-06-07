# Package Layout

The repository separates public API definitions, backend abstractions, concrete
RTI implementations, transport adapters, and verification assets.

## Core API

- `hla2010/api.py`: public RTI and Federate Ambassador protocols.
- `hla2010/handles.py`, `hla2010/types.py`, `hla2010/enums.py`, `hla2010/time.py`: shared HLA value types.
- `hla2010/raw_api.py`: source-derived API scaffold.

## Backend Abstractions

- `hla2010/backends/base.py`: backend interface, invocation envelope, and delegating ambassador.
- `hla2010/backends/transport.py`: typed transport request/response boundary.
- `hla2010/backends/conversion.py` and `hla2010/backends/java_common.py`: cross-backend value conversion.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema.
- `hla2010/backends/grpc_transport/`: gRPC transport package with `.proto` schema, generated-compatible Python stubs, client adapter, and hosted server helpers.
- `hla2010/backends/rest_transport/`: REST transport package with OpenAPI-aligned Python client adapter and transport runtime.

## Concrete Backends

- `hla2010/backends/python/`: canonical pure in-memory RTI backend implementation package.
- `hla2010/backends/python/backend.py`: package facade for the concrete Python backend class.
- `hla2010/backends/python/state.py`, `engine.py`, `reporting.py`: shared backend state, handle registry, and service-report support.
- `hla2010/backends/python/federation.py`: federation domain root.
- `hla2010/backends/python/federation_lifecycle.py`, `federation_sync.py`: lifecycle/join-resign and synchronization-point submodules.
- `hla2010/backends/python/object.py`: object domain root.
- `hla2010/backends/python/object_delivery.py`: object update/delete, interaction delivery, and transport callbacks.
- `hla2010/backends/python/mom.py`: MOM domain root.
- `hla2010/backends/python/mom_actions.py`, `mom_reporting.py`: MOM dispatch/decoding and MOM/service-report emission submodules.
- `hla2010/backends/python/time.py`: time-management domain root.
- `hla2010/backends/python/time_queue.py`, `time_services.py`: queue/grant mechanics and public time-service/validation submodules.
- `hla2010/backends/python/save_restore.py`, `callbacks.py`, `declaration.py`, `ownership.py`, `ddm.py`: remaining focused Python backend service domains.
- `hla2010/backends/certi/`: CERTI service adapter and transport package.
- `hla2010/backends/jpype/`, `hla2010/backends/py4j/`, and `hla2010/backends/certi_java/`: Java-facing backend families with explicit `runtime`, `adapter`, and `factory` modules.

Java transport stubs generated from the RTI REST or gRPC transport contracts are not checked in and are currently out of scope. Java integration in this repo is through the backend families above, not through generated transport bindings.

## Backend Factories

- `hla2010/rti.py`: top-level backend and transport registries.
- `hla2010/backends/python/factory.py`: pure-Python backend factories.
- `hla2010/backends/certi/__init__.py`: CERTI backend and transport factories.

## Runtime Discovery

- `hla2010/real_rti.py`: compatibility facade.
- `hla2010/real_rti_certi.py`, `hla2010/real_rti_pitch.py`, `hla2010/real_rti_portico.py`: vendor-family runtime discovery and launch.
- `hla2010/real_rti_process.py`: process and TCP listener helpers.

## Verification And Scenarios

- `hla2010/testing/`: reusable scenario and artifact-producing test helpers.
- `hla2010/testing/scenario_support.py`, `scenario_exchange.py`, `scenario_sync.py`, `scenario_ownership.py`, `scenario_basic.py`: scenario-family split beneath the compatibility facade `hla2010/testing/scenarios.py`.
- `hla2010/testing/java_shim_types.py`, `java_shim_backend.py`, `java_shim_kernel.py`, `java_shim_factory.py`: Java-shaped shim split beneath the compatibility facade `hla2010/testing/java_shim.py`.
- `hla2010/testing/two_federate_suite.py`: two-federate suite compatibility facade.
- `hla2010/testing/two_federate_suite_runner.py`: suite coordinator.
- `hla2010/testing/two_federate_suite_scenarios.py`: embedded suite scenario bodies such as save/restore and DDM.
- `hla2010/testing/two_federate_suite_pairs.py`, `two_federate_suite_configs.py`, `two_federate_suite_profiles.py`, `two_federate_suite_summary.py`, `two_federate_suite_timeline.py`, `two_federate_suite_writers.py`: pair construction, profile selection, summary/timeline shaping, and artifact writing.
- `hla2010/scenarios/`: reusable domain scenarios that are safe to import from both tests and example entrypoints.
- `examples/`: runnable scripts and example-only assets. Nothing under `examples/` is part of the installable `hla2010` package.
- `examples/<scenario>/`: example-specific static assets such as FOM XML or notes for that scenario.
- `hla2010/verification.py` and `hla2010/conformance.py`: evidence and requirements-ledger support.

Legacy flat backend shim modules have been removed. New code should import from
the canonical package implementations instead.

## Example Boundary Rules

Keep example entrypoints thin:

- parse CLI arguments
- construct a backend or scenario factory
- call into `hla2010.scenarios.*` or another reusable package module

Keep reusable scenario logic out of `examples/` so tests can import the same
code without depending on a script layout.
