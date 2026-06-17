# Package Split Workspace

This directory contains the installable workspace packages for the repo.

## Start Here

Before you work in any package subtree, bootstrap the workspace Python
environment from the repo root:

1. `./tools/bootstrap python`
2. `source .venv/bin/activate`
3. run a pure-Python smoke path

The canonical environment and install-order guide is
[`../docs/python_environment.md`](../docs/python_environment.md).

For the quickest package hierarchy and versioning answer, use
[`../docs/package_hierarchy_and_versioning.md`](../docs/package_hierarchy_and_versioning.md).

## Reference

`hla` is a PEP 420 namespace package contributed by the installable
distributions in this directory. `hla-rti1516e` owns `hla.rti1516e`,
`hla-rti1516-2025` owns `hla.rti1516_2025`, and `hla-rti-core` owns the
cross-version `hla.rti` discovery and factory layer.

The target dependency direction is edition-aware:

```text
hla-rti1516e
  <- hla-backend-common
  <- hla-rti-core
  <- hla-transport-common
  <- hla-verification
  <- hla-bridge-java-common <- hla-bridge-java-jpype <- hla-vendor-pitch-jpype
  <- hla-bridge-java-common <- hla-bridge-java-py4j <- hla-vendor-pitch-py4j
  <- hla-backend-common <- hla-backend-inmemory
  <- hla-rti-core <- hla-vendor-pitch
  <- hla-rti-core <- hla-backend-certi
  <- hla-transport-common <- hla-transport-grpc
  <- hla-transport-common <- hla-transport-rest
  <- hla-rti-core <- hla-fom-target-radar
  <- hla-backend-common <- hla-backend-inmemory <- hla-fom-hlax-message-test
  <- hla-backend-common <- hla-backend-inmemory <- hla-fom-hlax-space-lite
  <- hla-backend-common <- hla-backend-inmemory <- hla-fom-hlax-time-mgmt-test

hla-rti1516-2025
  <- hla-backend-shim

hla-bridge-java-jpype + hla-bridge-java-py4j
  <- hla-vendor-portico
```

Rules for the split:

- `hla-rti1516e` owns the abstract API, shared HLA value types, exceptions,
  FOM/MOM helpers needed by federates, and backend plugin contract.
- `hla-rti1516-2025` owns the authoritative IEEE 1516.1-2025 Python API
  surface from the supplied strict-doc package. It is a sibling of
  `hla-rti1516e`, not an extension of it.
- `hla-backend-common` owns backend-neutral invocation resolution and
  2010 backend support utilities.
- `hla-rti-core` owns runtime-process support plus cross-version spec/backend
  discovery and selection.
- `hla-backend-shim` is the first 2025 runtime lane. It registers `shim` for
  `rti1516_2025` only.
- `hla-transport-common` owns transport-neutral hosted request handling.
- RTI packages own one backend family and register through the
  `hla.rti_backends` entry point group.
- `hla-verification` is the only supported public verification package.
- FOM/example packages own concrete resources and scenario helpers, not public testing namespaces.
- Vendor runtime packages own their own runbooks and vendor-specific findings under `packages/<name>/docs/`.
- Transport packages own wire-format clients, hosted servers, and protocol assets for one transport family.
- Backend packages may depend on their edition spec package plus approved
  shared support layers, but spec packages must not import concrete backends,
  vendor runtime discovery, test shims, or examples.
- Python and Java backend families are intentionally separated.
- Transport packages must not depend directly on concrete backend packages.
- Leaf packages must not depend directly on backend or vendor packages.
- Package-owned code should stay inside the owning `packages/<name>/src/...`
  tree, and each package's `pyproject.toml` should declare only package-owned
  `source_roots`.

## Read Next

1. [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md)
2. [`../docs/package_layout.md`](../docs/package_layout.md)
3. [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md)
