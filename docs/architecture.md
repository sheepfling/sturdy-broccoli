# Architecture notes

The main repository pattern is:

`front door -> domain modules/mixins -> shared state/engine -> factories/registries -> optional transport/runtime adapters`

That pattern exists to keep HLA service behavior reviewable by domain while still allowing multiple runtime and transport paths behind the same ambassador surface.

The stricter package dependency rules live in
[`import_boundary_rules.md`](import_boundary_rules.md).

## Facades

- `hla.rti`: neutral spec/backend discovery and ambassador-creation facade.
- `hla.rti1516e`: canonical IEEE 1516.1-2010 Python API package.
- `hla.rti1516_2025`: canonical IEEE 1516.1-2025 Python API package scaffold.

For the primary 2025 Python RTI implementation lane, keep the ownership split explicit:

- `hla-backend-python1516-2025` is the main full Python-owned IEEE 1516.1-2025 RTI implementation package
- `hla-backend-shim` is only an import-level compatibility-wrapper package over that runtime
- Java/C++ 2025 binding routes remain segregated non-Python binding/capability lanes and should not be counted as alternate Python RTIs or as implementation-owner proof for the main Python 2025 lane

These facade modules are package-owned import paths under the shared PEP 420
`hla` namespace. No package owns `src/hla/__init__.py`.

## Domain Modules And Mixins

- `packages/hla-backend-python1516e/src/hla/backends/python1516e/declaration.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/object.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/object_delivery.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/mom.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/mom_actions.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/mom_reporting.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/ownership.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/time.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/time_queue.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/time_services.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/ddm.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/federation.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/federation_lifecycle.py`
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/federation_sync.py`

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

- `packages/hla-backend-python1516e/src/hla/backends/python1516e/state.py`: backend data model, queue state, MOM/reporting flags, save/restore snapshots, and typed support values.
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/engine.py`: shared in-memory handle registry, FOM bootstrap, class/interaction lookup, and federation object model support.
- `packages/hla-backend-python1516e/src/hla/backends/python1516e/reporting.py`: service-report file support.

This layer contains reusable backend mechanics that should not be duplicated across individual service-domain modules.

## Testing Pattern

The testing package mirrors the same structure where feasible:

- canonical generic scenario bodies: `packages/hla-verification/src/hla/verification/scenario_*.py`
- Java-shaped shim support: `packages/hla-bridge-java-common/src/hla.bridges.java.common/java_shim_*.py`
- repo-internal target/radar suite coordinator: `packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py`

The goal is the same as production code: keep scenario orchestration separate from dense helper mechanics and artifact writing.

Compatibility checks that remain in tests are intentional when they assert that
old import paths stay absent or that thin public facades remain narrow. They
should not be mistaken for installable package dependencies.

## Factories And Registries

- `packages/hla-backend-python1516e/src/hla/backends/python1516e/factory.py`: pure-Python backend constructors.
- `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py`: main full Python 2025 backend plugin and discovery surface.
- `packages/hla-backend-shim/src/hla/backends/shim/plugin.py`: retired shim plugin module that now returns no backend plugins and remains only for import compatibility.
- `packages/hla-rti-core/src/hla/rti/`: workspace-facing backend discovery and ambassador-construction helpers.
- `packages/hla-backend-certi/src/hla/backends/certi/certi/plugin.py`: CERTI backend plugin descriptors.

The rule is that new backend kinds or transport kinds should register themselves instead of extending a central switchboard.

## Optional Transport And Runtime Adapters

- `packages/hla-transport-common/src/hla.transports.common/transport.py`: typed transport request/response boundary.
- `packages/hla-backend-common/src/hla/backends/common/conversion.py`: shared backend conversion and native-handle policy.
- `packages/hla-bridge-java-common/src/hla.bridges.java.common/java_common.py`: shared Java bridge-independent adapter policy.
- `packages/hla-rti-core/src/hla.rti/real_rti_process.py`: shared vendor runtime-process lifecycle and loopback TCP policy.
- `packages/hla-transport-common/src/hla.transports.common`: shared hosted transport request-processing and callback polling helpers.
- `packages/hla-transport-rest/src/hla.transports.rest`: package-owned JSON-over-HTTP transport infrastructure with a checked-in client adapter around the OpenAPI envelope.
- `packages/hla-transport-grpc/src/hla.transports.grpc`: package-owned gRPC transport infrastructure with checked-in protobuf schema and Python stubs.
- `docs/openapi/rti_transport.yaml`: formal REST transport schema for generated clients.
- `packages/hla-backend-certi/src/hla/backends/certi/certi/transport.py` and `service_adapter.py`: explicit CERTI transport/service split.
- `packages/hla-bridge-java-jpype/src/hla.bridges.java.jpype/runtime.py`, `adapter.py`, and `factory.py`: JPype-backed Java RTI family.
- `packages/hla-bridge-java-py4j/src/hla.bridges.java.py4j/runtime.py`, `adapter.py`, and `factory.py`: Py4J-backed Java RTI family.
- `packages/hla-backend-certi/src/hla/backends/certi/certi_java/runtime.py`, `adapter.py`, and `factory.py`: Java-profile CERTI family over the real native CERTI path.
- `packages/hla-vendor-pitch/src/hla.vendors.pitch/real_rti_pitch.py`, `packages/hla-vendor-portico/src/hla/vendors/portico/real_rti_portico.py`, and `packages/hla-rti-core/src/hla.rti/real_rti_process.py`: runtime discovery and process-launch helpers.

The development goal is that a federate written against `hla.rti1516e` or
`hla.rti1516_2025` runs against the same versioned ambassador API whether the
backend is pure Python, CERTI-backed, JPype-backed, or Py4J-backed. REST and
gRPC are transport options underneath that backend-neutral surface, not separate
application APIs.

For IEEE 1516.1-2025 specifically, the main executable Python RTI lane is
`hla-backend-python1516-2025`. `hla-backend-shim` remains only as
compatibility-wrapper/import-level code and should not be treated as the
runtime owner.

The remaining documented version-local facade is intentionally narrow:
`hla.runtime.rti1516e` is the 2010-local backend discovery and ambassador-creation
surface, while shared adapter primitives and plugin contracts live only in
`hla.backends.common`.

### Transport Artifact Policy

- gRPC owns the checked-in 2010 FedPro-style protobuf profile and generated
  client/server Python artifacts today:
  - `proto/rti1516e/fedpro/datatypes.proto`
  - `proto/rti1516e/fedpro/RTIambassador.proto`
  - `proto/rti1516e/fedpro/FederateAmbassador.proto`
  - `proto/rti1516e/fedpro/HLA2010RTITransport.proto`
  - `src/hla/transports/grpc/fedpro2010/*_pb2.py`
  - `src/hla/transports/grpc/fedpro2010/*_pb2_grpc.py`
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

- `packages/hla-bridge-java-jpype/src/hla.bridges.java.jpype/runtime.py`: owns `JPypeConfig` and `JPypeBridge`.
- `packages/hla-bridge-java-jpype/src/hla.bridges.java.jpype/adapter.py`: owns `JPypeRTIBackend`.
- `packages/hla-bridge-java-jpype/src/hla.bridges.java.jpype/factory.py`: owns `create_jpype_backend(...)` and `rti_ambassador(...)`.

Use this family for in-process JVM access where Python talks directly to vendor Java RTI objects through JPype.

### Py4J Family

- `packages/hla-bridge-java-py4j/src/hla.bridges.java.py4j/runtime.py`: owns `Py4JConfig`, `Py4JBridge`, and the callback proxy type.
- `packages/hla-bridge-java-py4j/src/hla.bridges.java.py4j/adapter.py`: owns `Py4JRTIBackend`.
- `packages/hla-bridge-java-py4j/src/hla.bridges.java.py4j/factory.py`: owns `create_py4j_backend(...)` and `rti_ambassador(...)`.

Use this family when the Java RTI lives in another JVM process or when vendor deployment prefers gateway isolation.

### CERTI Java-Profile Family

- `packages/hla-backend-certi/src/hla/backends/certi/certi_java/runtime.py`: owns Java-shaped CERTI value conversion helpers.
- `packages/hla-backend-certi/src/hla/backends/certi/certi_java/adapter.py`: owns the CERTI Java callback adapter and Java-shaped RTI shim.
- `packages/hla-backend-certi/src/hla/backends/certi/certi_java/factory.py`: owns `create_certi_java_backend(...)`.

Use this family when the transport side is real native CERTI, but the ambassador path needs to exercise the same Java-bridge profile used by JPype or Py4J backends.

## Current Remote Callback Contract

The current remote proving paths use unary request/response calls plus explicit callback polling through `evokeCallback` and `evokeMultipleCallbacks`.

- This is the current contract of record for remote callback delivery.
- The server may buffer multiple RTI callbacks and drain them across repeated polling requests.
- This keeps the remote path aligned with the existing HLA callback model and with the CERTI helper contract already used in the repo.

Server-streaming or bidi-streaming gRPC remains a possible future contract, but it is not the current one. The immediate goal is clause-level parity over the existing polling model before widening the wire protocol again.
