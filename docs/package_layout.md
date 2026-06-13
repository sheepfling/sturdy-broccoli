# Package Layout

This page is the installable package-family map for the repo.

Use this page for:

- installable package-family roles
- package-owned source roots
- dependency direction between package families
- deciding where backend, transport, verification, and leaf-package code belongs

Do not use this page for:

- top-level repo directory purpose
- the shortest task-first onboarding path
- backend route maturity, smoke commands, or operator command inventory
- first-edit ownership cards for humans

Those belong to:

- [`workspace_layout.md`](workspace_layout.md)
- [`onboarding.md`](onboarding.md)
- [`backend_route_inventory.md`](backend_route_inventory.md)
- [`../packages/README.md`](../packages/README.md)

For the stricter rule table about what may import what, use
[`import_boundary_rules.md`](import_boundary_rules.md).

For the machine-derived installable package dependency graph, use
[`package_dependency_tree.md`](package_dependency_tree.md).

## Front Door

The repository root is tooling-only. The installable package root is
`packages/`.

- `hla2010-spec` is the architectural root package.
- `packages/hla2010-spec/src/hla2010/` owns the public spec surface, shared HLA
  value types, FOM/MOM helpers needed by federates, and the temporary
  workspace facade `hla2010.rti`.
- Concrete backend, transport, vendor, verification, and scenario
  implementations live in package-owned `packages/<name>/src/...` trees.

Do not use `pip install -e .` at the repository root. Install split packages
directly, or use `./tools/bootstrap python` to install the editable workspace
set.

For packages whose split status is `implementation-moved`, the owning
`pyproject.toml` should declare only package-owned `source_roots`.

## Package Families

### `hla2010-spec`

Owns:

- public RTI spec and callback contracts
- Pythonic runtime convenience layer
- shared HLA value types, exceptions, and time helpers
- FOM/MOM parsing, merge, serialization, and model helpers

Does not own:

- concrete RTI backend behavior
- vendor runtime discovery or launch helpers
- transport clients or hosted servers

Key modules:

- `packages/hla2010-spec/src/hla2010/spec/`
- `packages/hla2010-spec/src/hla2010/runtime_api.py`
- `packages/hla2010-spec/src/hla2010/fom.py`
- `packages/hla2010-spec/src/hla2010/raw_api.py`

### Shared Support Packages

These packages may be imported by multiple backend families but must stay
backend-neutral within their declared scope.

- `hla2010-rti-backend-common`: shared adapter contract, invocation resolution,
  conversion helpers, backend-neutral time helpers
- `hla2010-rti-runtime-common`: backend discovery, factory selection,
  loopback/runtime-process helpers
- `hla2010-rti-transport-common`: transport-neutral hosted request-processing
  helpers
- `hla2010-rti-java-common`: Java bridge support, runtime discovery helpers,
  return-type/value conversion
- `hla2010-verification-harness`: the only supported public verification
  package

### Concrete Backend Packages

These own one backend family each.

- `hla2010-rti-python`: primary in-memory reference RTI backend
- `hla2010-rti-certi`: CERTI backend/runtime adapter package
- `hla2010-rti-java-jpype`: generic JPype Java RTI bridge
- `hla2010-rti-java-py4j`: generic Py4J Java RTI bridge

Vendor-focused backend packages stay separate:

- `hla2010-rti-pitch-common`
- `hla2010-rti-pitch-jpype`
- `hla2010-rti-pitch-py4j`
- `hla2010-rti-portico`

### Transport Packages

These are wire/protocol families, not backend families.

- `hla2010-rti-transport-grpc`
- `hla2010-rti-transport-rest`

They own:

- protocol assets and schemas
- client adapters
- hosted server/runtime helpers

They do not own concrete RTI service semantics.

### Leaf Scenario And FOM Packages

These own concrete FOM resources and reusable scenario helpers.

- `hla2010-fom-target-radar`
- other `hla2010-fom-*` packages created through `./tools/new-fom-package`

Leaf packages must stay reusable and backend-neutral. Example scripts may call
them, but reusable logic should not live under `examples/`.

## Dependency Direction

The intended direction is:

```text
hla2010-spec
  <- shared support packages
  <- backend or transport families
  <- verification or leaf packages
```

More concretely:

- `hla2010-rti-backend-common` may depend on `hla2010-spec`
- `hla2010-rti-runtime-common` may depend on `hla2010-spec`,
  `hla2010-rti-backend-common`, and `hla2010-rti-transport-common`
- `hla2010-rti-java-common` may depend on `hla2010-spec` and
  `hla2010-rti-backend-common`
- concrete backend packages may depend on `hla2010-spec` plus approved shared
  support layers for that backend family
- transport packages may depend on `hla2010-spec`,
  `hla2010-rti-transport-common`, and `hla2010-rti-runtime-common`
- leaf packages may depend on `hla2010-spec`, approved verification helpers,
  and package-neutral runtime helpers

Rules that must stay true:

- `hla2010-spec` must not import concrete backend, vendor, transport, or leaf
  packages
- transport packages must not depend directly on concrete backend packages
- leaf packages must not depend directly on concrete backend or vendor packages
- Python and Java backend families stay separated except through approved shared
  support packages

Import isolation for installable `packages/*` trees is enforced by
[`tests/test_package_import_isolation.py`](../tests/test_package_import_isolation.py).
Dependency metadata is enforced by
[`tests/test_package_dependency_metadata.py`](../tests/test_package_dependency_metadata.py).

## Facades And Factories

`hla2010.rti` remains only as the documented temporary root-facing workspace
facade for backend discovery and ambassador creation.

- Package-owned code should import runtime factory helpers from
  `hla2010_rti_runtime_common` directly.
- Shared plugin contract types should import from
  `hla2010_rti_backend_common`.
- Backend packages register through the `hla2010.rti_backends` entry point
  group.

The root facade must stay narrow. It should not become the place where backend
registries, transport helpers, or package-owned internals flow back into the
spec package.

## Source Discipline

Source checkouts should use editable installs or the explicit pytest
`pythonpath` configuration. Production package code must not:

- mutate `sys.path`
- import `_bootstrap`
- walk package `__path__`
- derive repo roots from `__file__`
- compute `__all__` from `globals()`

Keep example entrypoints thin:

- parse CLI arguments
- construct a backend or scenario factory
- call package-owned reusable logic
- load reusable FOM assets from the owning package, not duplicated files under
  `examples/`

## Read Next

1. [`../packages/README.md`](../packages/README.md)
2. [`import_boundary_rules.md`](import_boundary_rules.md)
3. [`package_dependency_tree.md`](package_dependency_tree.md)
4. [`backend_route_inventory.md`](backend_route_inventory.md)
