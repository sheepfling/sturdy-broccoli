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

If you need the shortest package-failure diagnosis path, use
[`../docs/junior_test_diagnosis_runbook.md`](../docs/junior_test_diagnosis_runbook.md).

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
  <- hla-backend-common <- hla-backend-python1516e
  <- hla-rti-core <- hla-vendor-pitch
  <- hla-rti-core <- hla-backend-certi
  <- hla-transport-common <- hla-transport-grpc
  <- hla-transport-common <- hla-transport-rest
  <- hla-rti-core <- hla-fom-target-radar
  <- hla-backend-common <- hla-backend-python1516e <- hla-fom-proto2025-message-test
  <- hla-backend-common <- hla-backend-python1516e <- hla-fom-proto2025-space-lite
  <- hla-backend-common <- hla-backend-python1516e <- hla-fom-proto2025-time-mgmt-test

hla-rti1516-2025
  <- hla-backend-python1516-2025
  <- hla-backend-shim (deprecated compatibility scaffolding over hla-backend-python1516-2025)
  <- hla-fom-target-radar

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
- `hla-backend-python1516-2025` is the main full Python 2025 RTI backend and the
  main full Python 2025 RTI implementation lane. It registers
  `python1516_2025` for `rti1516_2025`.
- `hla-backend-shim` is deprecated temporary import-compatibility scaffolding.
  Its helper modules should remain wrapper-only compatibility aliases over
  `hla.backends.python1516_2025.*`, without reclaiming public runtime-selection
  ownership from `hla-backend-python1516-2025`, and should be removed after
  migration.
- the bounded hosted 2025 FedPro route is a route variant over
  `hla-backend-python1516-2025`, not a separate Python RTI family.
- Java and C++ 2025 binding lanes are supporting adaptation surfaces; they do
  not count as alternate Python 2025 RTIs.
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

## Package Docs

Use one consistent front-door pattern for package-local documentation:

- `packages/<name>/README.md`: package purpose, ownership, and install-facing
  boundary
- `packages/<name>/docs/README.md`: package-local runbooks, traceability
  notes, and vendor/runtime findings
- `packages/<name>/MIGRATION.md`: retained migration notes when that package
  was split or moved

For `packages/<name>/README.md`, prefer this order:

1. `What This Is`
2. `What This Is Not`
3. `When To Open It`
4. `Key Imports` or `Key Entrypoints`
5. `Related Docs`

That pattern matters more than perfect detail. The goal is that a reader can
tell in under a minute whether a package is:

- a standard surface
- shared support
- a concrete backend
- an integration layer
- or a leaf package

Notable package-local doc families:

- `packages/hla-backend-certi/docs/README.md`
- `packages/hla-vendor-pitch/docs/README.md`
- `packages/hla-vendor-portico/docs/README.md`
- `packages/hla-verification/docs/README.md`

## Package Failure Triage

When a test failure seems package-specific, use this order:

1. identify the failing test file or node
2. identify the implementation file it exercises
3. map that file into the owning `packages/<name>/src/...` tree
4. rerun the smallest useful scope
5. inspect package boundaries and dependencies only if the ownership is still unclear

Useful commands:

```bash
./tools/test tests/test_java_bridge_examples.py
./tools/test tests/test_python_route_examples.py
./tools/test -k java_bridge
./tools/package-deps generate
```

Useful docs:

- [`../docs/junior_test_diagnosis_runbook.md`](../docs/junior_test_diagnosis_runbook.md)
- [`../docs/package_layout.md`](../docs/package_layout.md)
- [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md)
- [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md)

## Read Next

1. [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md)
2. [`../docs/package_layout.md`](../docs/package_layout.md)
3. [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md)
