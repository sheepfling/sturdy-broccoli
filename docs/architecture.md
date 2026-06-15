# Architecture notes

The main repository pattern is:

`front door -> domain modules/mixins -> shared state/engine -> factories/registries -> optional transport/runtime adapters`

That pattern exists to keep HLA service behavior reviewable by domain while still allowing multiple runtime and transport paths behind the same ambassador surface.

The stricter package dependency rules live in
[`import_boundary_rules.md`](import_boundary_rules.md).

## Facades

- `hla2010/rti.py`: temporary top-level backend discovery and ambassador-creation compatibility facade.
- `hla2010/runtime_api.py` and `hla2010/api.py`: root runtime-facing compatibility layer over the clean spec contracts.

These facade modules are workspace-stable import paths. They are not counted as
package-owned implementation roots for packages marked `implementation-moved`.

## Domain Modules And Mixins

- `packages/hla2010-rti-python/src/hla2010_rti_python/declaration.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/object.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/object_delivery.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/mom.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/mom_actions.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/mom_reporting.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/ownership.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/time.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/time_queue.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/time_services.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/ddm.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/federation.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/federation_lifecycle.py`
- `packages/hla2010-rti-python/src/hla2010_rti_python/federation_sync.py`

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

- `packages/hla2010-rti-python/src/hla2010_rti_python/state.py`: backend data model, queue state, MOM/reporting flags, save/restore snapshots, and typed support values.
- `packages/hla2010-rti-python/src/hla2010_rti_python/engine.py`: shared in-memory handle registry, FOM bootstrap, class/interaction lookup, and federation object model support.
- `packages/hla2010-rti-python/src/hla2010_rti_python/reporting.py`: service-report file support.

This layer contains reusable backend mechanics that should not be duplicated across individual service-domain modules.

## Testing Pattern

The testing package mirrors the same structure where feasible:

- canonical generic scenario bodies: `packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_*.py`
- Java-shaped shim support: `packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_shim_*.py`
- repo-internal target/radar suite coordinator: `src/hla2010_repo_internal/verification/two_federate_suite_runner.py`

The goal is the same as production code: keep scenario orchestration separate from dense helper mechanics and artifact writing.

Compatibility imports that remain in tests are intentional when they verify
migration aliases or workspace-facade behavior. They should not be mistaken for
installable package dependencies.

## Factories And Registries

- `packages/hla2010-rti-python/src/hla2010_rti_python/factory.py`: pure-Python backend constructors.
- `hla2010/rti.py`: workspace-facing backend discovery and ambassador-construction helpers.
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/plugin.py`: CERTI backend plugin descriptors.

The rule is that new backend kinds or transport kinds should register themselves instead of extending a central switchboard.

## Optional Transport And Runtime Adapters

- `packages/hla2010-rti-transport-common/src/hla2010_rti_transport_common/transport.py`: typed transport request/response boundary.
- `packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/conversion.py`: shared backend conversion and native-handle policy.
- `packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_common.py`: shared Java bridge-independent adapter policy.
- `packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/real_rti_process.py`: shared vendor runtime-process lifecycle and loopback TCP policy.
- `packages/hla2010-rti-transport-common/src/hla2010_rti_transport_common`: shared hosted transport request-processing and callback polling helpers.
- `packages/hla2010-rti-transport-rest/src/hla2010_rti_transport_rest`: package-owned JSON-over-HTTP transport infrastructure with a checked-in client adapter around the OpenAPI envelope.
- `packages/hla2010-rti-transport-grpc/src/hla2010_rti_transport_grpc`: package-owned gRPC transport infrastructure with checked-in protobuf schema and Python stubs.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema for generated clients.
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/transport.py` and `service_adapter.py`: explicit CERTI transport/service split.
- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py`, `adapter.py`, and `factory.py`: JPype-backed Java RTI family.
- `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py`, `adapter.py`, and `factory.py`: Py4J-backed Java RTI family.
- `packages/hla2010-rti-pitch-common/src/hla2010_rti_pitch_common/real_rti_pitch.py`, `packages/hla2010-rti-portico/src/hla2010_rti_portico/real_rti_portico.py`, and `packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/real_rti_process.py`: runtime discovery and process-launch helpers.

The development goal is that a federate written against `hla2010` runs against the same ambassador API whether the backend is pure Python, CERTI-backed, JPype-backed, or Py4J-backed. REST and gRPC are transport options underneath that backend-neutral surface, not separate application APIs.

The remaining documented root facade is intentionally narrow: `hla2010.rti`
stays as a temporary root-facing backend discovery and ambassador-creation
compatibility surface, while shared adapter primitives and plugin contracts
live only in `hla2010_rti_backend_common`.

### Transport Artifact Policy

- gRPC is the only transport with checked-in generated client/server Python artifacts today:
  - `rti_transport.proto`
  - `rti_transport_pb2.py`
  - `rti_transport_pb2_grpc.py`
- REST has a formal OpenAPI schema plus a checked-in Python adapter layer, but the repo does not currently check in OpenAPI-generated Python client code.
- Java transport stubs for this RTI transport are currently out of scope. The Java-facing integration path in this repo is JPype and Py4J for Java RTIs, not generated REST or gRPC transport bindings.

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

- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py`: owns `JPypeConfig` and `JPypeBridge`.
- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/adapter.py`: owns `JPypeRTIBackend`.
- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/factory.py`: owns `create_jpype_backend(...)` and `rti_ambassador(...)`.

Use this family for in-process JVM access where Python talks directly to vendor Java RTI objects through JPype.

### Py4J Family

- `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py`: owns `Py4JConfig`, `Py4JBridge`, and the callback proxy type.
- `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/adapter.py`: owns `Py4JRTIBackend`.
- `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/factory.py`: owns `create_py4j_backend(...)` and `rti_ambassador(...)`.

Use this family when the Java RTI lives in another JVM process or when vendor deployment prefers gateway isolation.

## Current Remote Callback Contract

The current remote proving paths use unary request/response calls plus explicit callback polling through `evokeCallback` and `evokeMultipleCallbacks`.

- This is the current contract of record for remote callback delivery.
- The server may buffer multiple RTI callbacks and drain them across repeated polling requests.
- This keeps the remote path aligned with the existing HLA callback model and with the CERTI helper contract already used in the repo.

Server-streaming or bidi-streaming gRPC remains a possible future contract, but it is not the current one. The immediate goal is clause-level parity over the existing polling model before widening the wire protocol again.
