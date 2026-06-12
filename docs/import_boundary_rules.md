# Import Boundary Rules

This repository now uses a strict layered package model.

The installable root is `hla2010-spec`.

The workspace facade is `src/hla2010/`.

Those are not the same thing:

- `hla2010-spec` owns the architectural root surface
- `src/hla2010/` owns the abstract/core API plus only documented workspace
  compatibility facade: `hla2010.rti`

Do not treat `src/hla2010/` as a second conceptual root.
Do not add new root facades unless they are temporary, documented, and backed
by a migration reason.

This repository also has two distinct axes that must stay separate:

- backend family: where HLA service semantics execute
- transport: how a client talks to a backend

Those are not the same thing. A backend is `python`, `certi`, `jpype`, or
`py4j`. A transport is `grpc` or `rest`.

The practical rule is:

`hla2010-spec -> shared support -> backend family or transport -> leaf package`

Not:

- `transport == backend family`
- `python depends on java because the helpers happened to start there`
- `leaf packages depend on whichever backend packages examples happen to use`

## Package Classes

### Root

- `hla2010-spec`

Owns:

- clean spec surface
- shared HLA value types and exceptions
- backend contract
- backend registry contract
- source-derived overload metadata
- backend-neutral transport codecs exposed through the workspace facade

### Shared Support

- `hla2010-rti-backend-common`
- `hla2010-rti-runtime-common`
- `hla2010-rti-transport-common`
- `hla2010-verification-harness`

Shared support packages may depend only on `hla2010-spec` and other shared
support packages in the explicitly documented direction below.

### Backend Families

- `hla2010-rti-python`
- `hla2010-rti-certi`
- `hla2010-rti-java-jpype`
- `hla2010-rti-java-py4j`

### Vendor Specializations

- `hla2010-rti-java-common`
- `hla2010-rti-pitch-common`
- `hla2010-rti-pitch-jpype`
- `hla2010-rti-pitch-py4j`
- `hla2010-rti-portico`

### Transport

- `hla2010-rti-transport-common`
- `hla2010-rti-transport-grpc`
- `hla2010-rti-transport-rest`

Transport packages own wire protocols and hosted transport adapters. They do
not own backend semantics and must not depend directly on concrete backend
families.

### Leaves

- `hla2010-fom-target-radar`

Leaf packages own concrete FOM/scenario resources and verification-facing
helpers. They must not depend directly on vendor or backend families.

## Allowed Dependency Story

The approved internal dependency direction is:

- `hla2010-rti-backend-common` -> `hla2010-spec`
- `hla2010-rti-runtime-common` -> `hla2010-spec`, `hla2010-rti-backend-common`, `hla2010-rti-transport-common`
- `hla2010-rti-transport-common` -> `hla2010-spec`, `hla2010-rti-backend-common`
- `hla2010-verification-harness` -> `hla2010-spec`, `hla2010-rti-backend-common`, `hla2010-rti-runtime-common`
- `hla2010-rti-java-common` -> `hla2010-spec`, `hla2010-rti-backend-common`
- `hla2010-rti-python` -> `hla2010-spec`, `hla2010-rti-backend-common`
- `hla2010-rti-certi` -> `hla2010-spec`, `hla2010-rti-java-common`, `hla2010-rti-runtime-common`, `hla2010-rti-transport-common`
- `hla2010-rti-java-jpype` -> `hla2010-spec`, `hla2010-rti-java-common`
- `hla2010-rti-java-py4j` -> `hla2010-spec`, `hla2010-rti-java-common`
- `hla2010-rti-pitch-common` -> `hla2010-spec`, `hla2010-rti-java-common`, `hla2010-rti-runtime-common`
- `hla2010-rti-pitch-jpype` -> `hla2010-spec`, `hla2010-rti-java-common`, `hla2010-rti-pitch-common`, `hla2010-rti-java-jpype`
- `hla2010-rti-pitch-py4j` -> `hla2010-spec`, `hla2010-rti-java-common`, `hla2010-rti-pitch-common`, `hla2010-rti-java-py4j`
- `hla2010-rti-portico` -> `hla2010-spec`, `hla2010-rti-java-common`, `hla2010-rti-java-jpype`, `hla2010-rti-java-py4j`
- `hla2010-rti-transport-grpc` -> `hla2010-spec`, `hla2010-rti-backend-common`, `hla2010-rti-runtime-common`, `hla2010-rti-transport-common`
- `hla2010-rti-transport-rest` -> `hla2010-spec`, `hla2010-rti-backend-common`, `hla2010-rti-runtime-common`, `hla2010-rti-transport-common`
- `hla2010-fom-target-radar` -> `hla2010-spec`, `hla2010-verification-harness`, `hla2010-rti-runtime-common`

Important consequences:

- `hla2010-spec` depends on nothing internal
- `hla2010-rti-python` does not depend on `hla2010-rti-java-common`
- `hla2010-rti-transport-common` does not depend on concrete backend or vendor packages
- transport packages do not depend on `hla2010-rti-python` or `hla2010-rti-certi`
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

- backend-neutral invocation resolution belongs in `hla2010-rti-backend-common`
- runtime process helpers belong in `hla2010-rti-runtime-common`
- transport request processing and transport selection/coercion belong in `hla2010-rti-transport-common`

The same rule applies to `hla2010.rti`: it is a temporary documented root
compatibility facade for backend discovery and ambassador creation, not a place to move
package-owned backend logic back into `src/hla2010/`.
Package-owned code should import runtime factory helpers from
`hla2010_rti_runtime_common` directly rather than through `hla2010.rti`.
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
directly. Removed root compatibility paths such as `hla2010.java_runtime`
must not be reintroduced.

For packages marked `implementation-moved`, the declared
`tool.hla2010.package-split.source_roots` must point only at files under that
package's own `packages/<name>/src/...` tree. Compatibility facades under
`src/hla2010/` are workspace migration surface, not package-owned
implementation.

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
