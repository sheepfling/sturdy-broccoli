# Architecture notes

The main repository pattern is:

`facade -> domain modules/mixins -> shared state/engine -> factories/registries -> optional transport/runtime adapters`

That pattern exists to keep HLA service behavior reviewable by domain while still allowing multiple runtime and transport paths behind the same ambassador surface.

## Facades

- `hla2010/rti.py`: top-level backend and transport selection facade.
- `hla2010/backends/python/backend.py`: package facade for the pure-Python backend.
- `hla2010/backends/python/`: canonical Python backend implementation package.
- `hla2010/real_rti.py`: runtime discovery compatibility facade.

## Domain Modules And Mixins

- `hla2010/backends/python/declaration.py`
- `hla2010/backends/python/object.py`
- `hla2010/backends/python/object_delivery.py`
- `hla2010/backends/python/mom.py`
- `hla2010/backends/python/mom_actions.py`
- `hla2010/backends/python/mom_reporting.py`
- `hla2010/backends/python/ownership.py`
- `hla2010/backends/python/time.py`
- `hla2010/backends/python/time_queue.py`
- `hla2010/backends/python/time_services.py`
- `hla2010/backends/python/ddm.py`
- `hla2010/backends/python/federation.py`
- `hla2010/backends/python/federation_lifecycle.py`
- `hla2010/backends/python/federation_sync.py`

These modules isolate standard HLA service families so review can happen at the service-domain level instead of inside a single backend god module.

The current Python pattern is:

- domain root module: public mixin/composition seam for that service family
- focused internal submodules: dense mechanics split by responsibility
- shared support: `state.py`, `engine.py`, `reporting.py`

Examples:

- object management: `object.py` + `object_delivery.py`
- MOM: `mom.py` + `mom_actions.py` + `mom_reporting.py`
- time management: `time.py` + `time_queue.py` + `time_services.py`
- federation management: `federation.py` + `federation_lifecycle.py` + `federation_sync.py`

## Shared State And Engine

- `hla2010/backends/python/state.py`: backend data model, queue state, MOM/reporting flags, save/restore snapshots, and typed support values.
- `hla2010/backends/python/engine.py`: shared in-memory handle registry, FOM bootstrap, class/interaction lookup, and federation object model support.
- `hla2010/backends/python/reporting.py`: service-report file support.

This layer contains reusable backend mechanics that should not be duplicated across individual service-domain modules.

## Testing Pattern

The testing package mirrors the same structure where feasible:

- compatibility facade: `scenarios.py`, `java_shim.py`, `two_federate_suite.py`
- domain/scenario roots: `scenario_exchange.py`, `scenario_sync.py`, `scenario_ownership.py`
- focused support modules: `scenario_support.py`, `java_shim_types.py`, `java_shim_backend.py`, `java_shim_factory.py`
- suite coordinator plus helpers: `two_federate_suite_runner.py`, `two_federate_suite_scenarios.py`, `two_federate_suite_pairs.py`, `two_federate_suite_writers.py`

The goal is the same as production code: keep scenario orchestration separate from dense helper mechanics and artifact writing.

## Factories And Registries

- `hla2010/backends/python/factory.py`: pure-Python backend constructors.
- `hla2010/rti.py`: `register_backend_factory(...)` and `register_transport_factory(...)`.
- `hla2010/backends/certi/__init__.py`: CERTI backend and transport factory surface.

The rule is that new backend kinds or transport kinds should register themselves instead of extending a central switchboard.

## Optional Transport And Runtime Adapters

- `hla2010/backends/transport.py`: typed transport request/response boundary.
- `hla2010/backends/rest_transport`: JSON-over-HTTP transport package with a checked-in client adapter around the OpenAPI envelope.
- `hla2010/backends/grpc_transport`: gRPC transport package with checked-in protobuf schema and Python stubs.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema for generated clients.
- `hla2010/backends/certi/transport.py` and `hla2010/backends/certi/service_adapter.py`: explicit CERTI transport/service split.
- `hla2010/backends/jpype/runtime.py`, `adapter.py`, and `factory.py`: JPype-backed Java RTI family.
- `hla2010/backends/py4j/runtime.py`, `adapter.py`, and `factory.py`: Py4J-backed Java RTI family.
- `hla2010/backends/certi_java/runtime.py`, `adapter.py`, and `factory.py`: Java-profile CERTI family over the real native CERTI path.
- `hla2010/real_rti_certi.py`, `hla2010/real_rti_pitch.py`, `hla2010/real_rti_portico.py`, `hla2010/real_rti_process.py`: runtime discovery and process-launch helpers.

The development goal is that a federate written against `hla2010` runs against the same ambassador API whether the backend is pure Python, CERTI-backed, JPype-backed, or Py4J-backed. REST and gRPC are transport options underneath that backend-neutral surface, not separate application APIs.

### Transport Artifact Policy

- gRPC is the only transport with checked-in generated client/server Python artifacts today:
  - `rti_transport.proto`
  - `rti_transport_pb2.py`
  - `rti_transport_pb2_grpc.py`
- REST has a formal OpenAPI schema plus a checked-in Python adapter layer, but the repo does not currently check in OpenAPI-generated Python client code.
- Java transport stubs for this RTI transport are currently out of scope. The Java-facing integration path in this repo is JPype, Py4J, and the CERTI Java-profile adapters, not generated REST or gRPC transport bindings.

That split is intentional for now. It keeps one generated-wire example in-tree, keeps the REST contract explicit, and avoids suggesting that Java transport stubs are a supported distribution artifact when they are not part of the current runtime model.

## Java Family Module Rules

Each Java-facing backend family follows the same package split:

- `runtime.py`: bridge mechanics, runtime configuration, Java value conversion, and raw JVM/gateway integration.
- `adapter.py`: backend adapter classes, callback proxies, and backend-specific ambassador-facing glue.
- `factory.py`: backend construction, `BackendInfo` population, and convenience constructors such as `rti_ambassador(...)`.

That split is intended to keep PRs reviewable:

- runtime changes should not silently change HLA service semantics.
- adapter changes should not add runtime discovery or process-launch policy.
- factory changes should assemble objects, not implement bridge behavior.

### JPype Family

- `hla2010/backends/jpype/runtime.py`: owns `JPypeConfig` and `JPypeBridge`.
- `hla2010/backends/jpype/adapter.py`: owns `JPypeRTIBackend`.
- `hla2010/backends/jpype/factory.py`: owns `create_jpype_backend(...)` and `rti_ambassador(...)`.

Use this family for in-process JVM access where Python talks directly to vendor Java RTI objects through JPype.

### Py4J Family

- `hla2010/backends/py4j/runtime.py`: owns `Py4JConfig`, `Py4JBridge`, and the callback proxy type.
- `hla2010/backends/py4j/adapter.py`: owns `Py4JRTIBackend`.
- `hla2010/backends/py4j/factory.py`: owns `create_py4j_backend(...)` and `rti_ambassador(...)`.

Use this family when the Java RTI lives in another JVM process or when vendor deployment prefers gateway isolation.

### CERTI Java-Profile Family

- `hla2010/backends/certi_java/runtime.py`: owns Java-shaped CERTI value conversion helpers.
- `hla2010/backends/certi_java/adapter.py`: owns the CERTI Java callback adapter and Java-shaped RTI shim.
- `hla2010/backends/certi_java/factory.py`: owns `create_certi_java_backend(...)`.

Use this family when the transport side is real native CERTI, but the ambassador path needs to exercise the same Java-bridge profile used by JPype or Py4J backends.

## Current Remote Callback Contract

The current remote proving paths use unary request/response calls plus explicit callback polling through `evokeCallback` and `evokeMultipleCallbacks`.

- This is the current contract of record for remote callback delivery.
- The server may buffer multiple RTI callbacks and drain them across repeated polling requests.
- This keeps the remote path aligned with the existing HLA callback model and with the CERTI helper contract already used in the repo.

Server-streaming or bidi-streaming gRPC remains a possible future contract, but it is not the current one. The immediate goal is clause-level parity over the existing polling model before widening the wire protocol again.
