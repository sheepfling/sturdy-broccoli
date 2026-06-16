# Package Split Workspace

This directory contains the installable workspace packages for the repo. Some
packages still carry migration metadata, but several already own their runtime
implementation outright.

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

The target dependency direction is:

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
  <- hla-fom-target-radar

hla-bridge-java-jpype + hla-bridge-java-py4j
  <- hla-vendor-portico
```

Rules for the split:

- `hla-rti1516e` owns the abstract API, shared HLA value types, exceptions,
  FOM/MOM helpers needed by federates, and backend plugin contract.
- `hla-backend-common` owns backend-neutral invocation resolution and
  backend support utilities.
- `hla-rti-core` owns runtime-process and loopback support.
- `hla-transport-common` owns transport-neutral hosted request handling.
- RTI packages own one backend family and register through the
  `hla.rti_backends` entry point group.
- `hla-verification` is the only supported public verification package.
- FOM/example packages own concrete resources and scenario helpers, not public testing namespaces.
- Vendor runtime packages own their own runbooks and vendor-specific findings under `packages/<name>/docs/`.
- Transport packages own wire-format clients, hosted servers, and protocol assets for one transport family.
- Backend packages may depend on `hla-rti1516e` plus approved shared support
  layers, but `hla-rti1516e` must not import concrete backends, vendor runtime
  discovery, test shims, or examples.
- Python and Java backend families are intentionally separated.
- Transport packages must not depend directly on concrete backend packages.
- Leaf packages must not depend directly on backend or vendor packages.
- During migration, package ownership moves one family at a time after
  import-boundary tests are in place. A package marked
  `implementation-moved` in its `pyproject.toml` is already the canonical
  implementation root for that family, and its declared `source_roots` should
  point only at files under that package's own `packages/<name>/src/...` tree.

Suggested move order:

1. `hla-backend-inmemory`
2. `hla-backend-certi`
3. `hla-backend-common`
4. `hla-bridge-java-common`
5. `hla-rti-core`
6. `hla-bridge-java-jpype`
7. `hla-bridge-java-py4j`
8. `hla-vendor-pitch`
9. `hla-vendor-pitch-jpype`
10. `hla-vendor-pitch-py4j`
11. `hla-vendor-portico`
12. `hla-transport-grpc`
13. `hla-transport-rest`
14. `hla-verification`
15. `hla-fom-target-radar`
16. trim `hla-rti1516e` to the final core surface

## Read Next

1. [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md)
2. [`../docs/package_layout.md`](../docs/package_layout.md)
3. [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md)
