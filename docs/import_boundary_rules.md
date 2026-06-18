# Import Boundary Rules

This repository now uses a strict layered package model.

The shared namespace root is `hla`.

No package may own `src/hla/__init__.py`; `hla` is a PEP 420 namespace package.

The package-owned roots are:

- `hla-rti1516e`: `packages/hla-rti1516e/src/hla/rti1516e`
- `hla-rti1516-2025`: `packages/hla-rti1516-2025/src/hla/rti1516_2025`
- `hla-rti-core`: `packages/hla-rti-core/src/hla/rti`, including backend discovery and neutral factory selection
- backend packages: `packages/hla-backend-*/src/hla/backends/...`
- transport packages: `packages/hla-transport-*/src/hla/transports/...`
- bridge/vendor packages: `packages/hla-bridge-*` and `packages/hla-vendor-*`

Do not recreate `hla2010` as a conceptual root. Do not restore `_Spec` aliases
or the removed `hla.rti1516e.spec` facade; canonical standard types are
`hla.rti1516e.RTIambassador`, `hla.rti1516e.FederateAmbassador`,
`hla.rti1516_2025.RTIambassador`, and
`hla.rti1516_2025.FederateAmbassador`.

This repository also has two distinct axes that must stay separate:

- backend family: where HLA service semantics execute
- transport: how a client talks to a backend

Those are not the same thing. A backend is `python`, `certi`, `jpype`, or
`py4j`. A transport is `grpc` or `rest`.

The practical rule is:

`versioned spec API -> shared support or edition backend -> transport/vendor/leaf package`

Not:

- `transport == backend family`
- `python depends on java because the helpers happened to start there`
- `leaf packages depend on whichever backend packages examples happen to use`

## Package Classes

### Spec Roots

- `hla-rti1516e`
- `hla-rti1516-2025`

Owns:

- clean spec surfaces
- shared HLA value types and exceptions
- backend registry contract through `hla-rti-core`
- source-derived overload metadata
- edition-owned source trace and generated/doc-derived API metadata

### Shared Support

- `hla-backend-common`
- `hla-rti-core`
- `hla-transport-common`
- `hla-verification`

Shared support packages may depend only on `hla-rti1516e` and other shared
support packages in the explicitly documented direction below. New 2025 support
must use `hla-rti1516-2025` or `hla-rti-core`, not import through the 2010 spec
package.

### Backend Families

- `hla-backend-inmemory`
- `hla-backend-shim`
- `hla-backend-certi`
- `hla-bridge-java-jpype`
- `hla-bridge-java-py4j`

### Vendor Specializations

- `hla-bridge-java-common`
- `hla-vendor-pitch`
- `hla-vendor-pitch-jpype`
- `hla-vendor-pitch-py4j`
- `hla-vendor-portico`

### Transport

- `hla-transport-common`
- `hla-transport-grpc`
- `hla-transport-rest`

Transport packages own wire protocols and hosted transport adapters. They do
not own backend semantics and must not depend directly on concrete backend
families.

### Leaves

- `hla-fom-target-radar`
- `hla-fom-proto2025-message-test`
- `hla-fom-proto2025-space-lite`
- `hla-fom-proto2025-time-mgmt-test`

Leaf packages own concrete FOM/scenario resources and verification-facing
helpers. They must not depend directly on vendor or backend families.

## Allowed Dependency Story

The approved internal dependency direction is:

- `hla-backend-common` -> `hla-rti1516e`
- `hla-rti-core` -> `hla-rti1516e`, `hla-backend-common`, `hla-transport-common`
- `hla-transport-common` -> `hla-rti1516e`, `hla-backend-common`
- `hla-verification` -> `hla-rti1516e`, `hla-backend-common`, `hla-rti-core`
- `hla-bridge-java-common` -> `hla-rti1516e`, `hla-backend-common`
- `hla-backend-inmemory` -> `hla-rti1516e`, `hla-backend-common`
- `hla-backend-certi` -> `hla-rti1516e`, `hla-bridge-java-common`, `hla-rti-core`, `hla-transport-common`
- `hla-bridge-java-jpype` -> `hla-rti1516e`, `hla-bridge-java-common`
- `hla-bridge-java-py4j` -> `hla-rti1516e`, `hla-bridge-java-common`
- `hla-vendor-pitch` -> `hla-rti1516e`, `hla-bridge-java-common`, `hla-rti-core`
- `hla-vendor-pitch-jpype` -> `hla-rti1516e`, `hla-bridge-java-common`, `hla-vendor-pitch`, `hla-bridge-java-jpype`
- `hla-vendor-pitch-py4j` -> `hla-rti1516e`, `hla-bridge-java-common`, `hla-vendor-pitch`, `hla-bridge-java-py4j`
- `hla-vendor-portico` -> `hla-rti1516e`, `hla-bridge-java-common`, `hla-bridge-java-jpype`, `hla-bridge-java-py4j`
- `hla-transport-grpc` -> `hla-rti1516e`, `hla-backend-common`, `hla-rti-core`, `hla-transport-common`
- `hla-transport-rest` -> `hla-rti1516e`, `hla-backend-common`, `hla-rti-core`, `hla-transport-common`
- `hla-fom-target-radar` -> `hla-rti1516e`, `hla-rti-core`
- `hla-fom-proto2025-message-test` -> `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-backend-inmemory`
- `hla-fom-proto2025-space-lite` -> `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-backend-inmemory`
- `hla-fom-proto2025-time-mgmt-test` -> `hla-rti1516e`, `hla-rti1516-2025`, `hla-backend-common`, `hla-backend-inmemory`

Important consequences:

- `hla-rti1516e` depends on nothing internal
- `hla-backend-inmemory` does not depend on `hla-bridge-java-common`
- `hla-transport-common` does not depend on concrete backend or vendor packages
- transport packages do not depend on `hla-backend-inmemory` or `hla-backend-certi`
- leaf packages do not depend on vendor/backend families

## What Belongs Where

Put code in a backend family package when it:

- implements HLA service behavior
- owns backend-specific state or callback semantics
- exposes backend plugin descriptors

Put code in a shared support package when it:

- is reused across multiple backend families
- is metadata-driven or backend-neutral
- does not define the identity of one concrete backend family

Examples:

- backend-neutral invocation resolution belongs in `hla-backend-common`
- runtime process helpers belong in `hla-rti-core`
- transport request processing and transport selection/coercion belong in `hla-transport-common`

The same rule applies to `hla.rti`: it owns cross-version discovery and
ambassador creation, not version-specific API methods, backend execution, or
transport wire code. Package-owned code should import runtime factory helpers
from `hla.rti` directly.
Do not import plugin contract types, backend registry internals, low-level
transport registration helpers, private helpers, or transport coercion through
that root module from package-owned code.
Put code in a transport package when it:

- serializes or deserializes wire messages
- hosts HTTP or gRPC server entrypoints
- implements a transport client adapter

Put code in a leaf package when it:

- owns a concrete FOM
- owns scenario resources
- owns verification profiles that stay backend-neutral in package metadata

Removed split-package compatibility paths under `src/hla2010/backends/*` must
not be reintroduced.
Package-owned implementation code must import the owning split package module
directly. Removed root compatibility paths such as `hla.rti1516e.java_runtime`
must not be reintroduced.

The declared `tool.hla.package.source_roots` must point only at files under that
package's own `packages/<name>/src/...` tree.

## Enforcement

Installable package-root isolation is enforced by
[tests/test_package_import_isolation.py](../tests/test_package_import_isolation.py).
That test scans the declared `source_roots`, not just `packages/*/src`, so
metadata cannot quietly point at off-package implementation files.

Dependency metadata is enforced by
[tests/test_package_dependency_metadata.py](../tests/test_package_dependency_metadata.py).

Treat these tests as architectural guardrails. If a new sibling-package
dependency is necessary, update this document first and then change the
allowlist deliberately.
