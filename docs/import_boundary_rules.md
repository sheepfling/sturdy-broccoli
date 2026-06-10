# Import Boundary Rules

This repository has two distinct axes that should stay separate:

- backend family: where HLA service semantics execute
- transport: how a client talks to a backend

Those are not the same thing. A backend is `python`, `certi`, `jpype`, or
`py4j`. A transport is `subprocess-line`, `grpc`, or `rest`.

The practical rule is:

`core API -> backend contract -> backend family -> optional transport`

Not:

`transport == backend family`

## Package Roles

### `src/hla2010/`

Owns the stable import surface:

- spec and runtime-facing API
- shared HLA value types and exceptions
- backend contract and top-level registry
- thin compatibility facades during the split-package transition

Do not put concrete backend implementations here long term.

### Backend family packages

These packages own RTI semantics:

- `hla2010-rti-python`
- `hla2010-rti-certi`
- `hla2010-rti-java-jpype`
- `hla2010-rti-java-py4j`
- vendor specializations such as Pitch and Portico

These packages may depend on:

- `hla2010`
- narrow shared support packages needed for their family

They should not depend sideways on unrelated backend families.

### Common support packages

These packages own reusable mechanics, not backend identity:

- `hla2010-rti-backend-common`
- `hla2010-rti-java-common`
- `hla2010-rti-runtime-common`

They exist so concrete backend packages do not duplicate conversion, Java
bridge, or runtime-process helpers.

### Transport packages

These packages own wire protocols, not HLA semantics:

- `hla2010-rti-transport-common`
- `hla2010-rti-transport-grpc`
- `hla2010-rti-transport-rest`

They may depend on:

- `hla2010`
- a hosted backend family when they expose an in-process test server

They should not define their own backend semantics.

## Current Allowed Dependency Story

The intended dependency direction is:

- `hla2010-rti-python` -> `hla2010`
- `hla2010-rti-certi` -> `hla2010`, `hla2010-rti-java-common`
- `hla2010-rti-java-jpype` -> `hla2010`, `hla2010-rti-java-common`
- `hla2010-rti-java-py4j` -> `hla2010`, `hla2010-rti-java-common`
- `hla2010-rti-pitch-*` -> `hla2010`, Java bridge package, Pitch common
- `hla2010-rti-portico` -> `hla2010`, Java bridge package(s)
- `hla2010-rti-transport-common` -> `hla2010`, narrow shared codec support
- `hla2010-rti-transport-grpc` -> `hla2010`, hosted backend packages, transport-common
- `hla2010-rti-transport-rest` -> `hla2010`, hosted backend packages, transport-common

`hla2010-rti-transport-common` exists specifically so REST and gRPC can share
hosted request-processing logic without one transport package depending on the
other's implementation modules.

## What Belongs Where

Put code in the backend family package when it:

- implements HLA service behavior
- owns backend-specific state or callback semantics
- exposes backend plugin descriptors

Put code in a transport package when it:

- serializes or deserializes wire messages
- hosts HTTP or gRPC server entrypoints
- implements a transport client adapter

Put code in a common package when it:

- is reused across multiple backend families
- does not define the identity of one backend family

Keep `src/hla2010/backends/*` as compatibility facades only.

## Import Enforcement

Installable package-root isolation is enforced by
[tests/test_package_import_isolation.py](../tests/test_package_import_isolation.py).

That test should be treated as an architectural guardrail, not just a lint
check. When a new package needs a sibling-package import, document the reason
here first and then make the allowlist change deliberately.
