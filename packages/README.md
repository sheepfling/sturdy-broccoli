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

## Reference

Architecturally, `hla2010-spec` is the one installable root. The
`packages/hla2010-spec/src/hla2010/` tree is the package-owned spec source root used for stable imports, abstract
core API ownership, and only documented temporary compatibility routing.
The remaining workspace facade is `hla2010.rti`.

The target dependency direction is:

```text
hla2010-spec
  <- hla2010-rti-backend-common
  <- hla2010-rti-runtime-common
  <- hla2010-rti-transport-common
  <- hla2010-verification-harness
  <- hla2010-rti-java-common <- hla2010-rti-java-jpype <- hla2010-rti-pitch-jpype
  <- hla2010-rti-java-common <- hla2010-rti-java-py4j <- hla2010-rti-pitch-py4j
  <- hla2010-rti-backend-common <- hla2010-rti-python
  <- hla2010-rti-runtime-common <- hla2010-rti-pitch-common
  <- hla2010-rti-runtime-common <- hla2010-rti-certi
  <- hla2010-rti-transport-common <- hla2010-rti-transport-grpc
  <- hla2010-rti-transport-common <- hla2010-rti-transport-rest
  <- hla2010-fom-target-radar

hla2010-rti-java-jpype + hla2010-rti-java-py4j
  <- hla2010-rti-portico
```

Rules for the split:

- `hla2010-spec` owns the abstract API, shared HLA value types, exceptions,
  FOM/MOM helpers needed by federates, and backend plugin contract.
- `hla2010-rti-backend-common` owns backend-neutral invocation resolution and
  backend support utilities.
- `hla2010-rti-runtime-common` owns runtime-process and loopback support.
- `hla2010-rti-transport-common` owns transport-neutral hosted request handling.
- RTI packages own one backend family and register through the
  `hla2010.rti_backends` entry point group.
- `hla2010-verification-harness` is the only supported public verification package.
- FOM/example packages own concrete resources and scenario helpers, not public testing namespaces.
- Vendor runtime packages own their own runbooks and vendor-specific findings under `packages/<name>/docs/`.
- Transport packages own wire-format clients, hosted servers, and protocol assets for one transport family.
- Backend packages may depend on `hla2010-spec` plus approved shared support
  layers, but `hla2010-spec` must not import concrete backends, vendor runtime
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

1. `hla2010-rti-python`
2. `hla2010-rti-certi`
3. `hla2010-rti-backend-common`
4. `hla2010-rti-java-common`
5. `hla2010-rti-runtime-common`
6. `hla2010-rti-java-jpype`
7. `hla2010-rti-java-py4j`
8. `hla2010-rti-pitch-common`
9. `hla2010-rti-pitch-jpype`
10. `hla2010-rti-pitch-py4j`
11. `hla2010-rti-portico`
12. `hla2010-rti-transport-grpc`
13. `hla2010-rti-transport-rest`
14. `hla2010-verification-harness`
15. `hla2010-fom-target-radar`
16. trim `hla2010-spec` to the final core surface

## Read Next

1. [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md)
2. [`../docs/package_layout.md`](../docs/package_layout.md)
3. [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md)
