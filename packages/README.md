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

If you only need the shortest package-edit path:

1. use [`../docs/onboarding.md`](../docs/onboarding.md) for the ordered repo path
2. come back here to decide which package owns the change
3. open that package README before reading broader architecture docs

## Reference

For the package architecture docs, read them in this order:

1. [`../docs/package_layout.md`](../docs/package_layout.md): canonical human package hierarchy and family ownership
2. [`../docs/package_hierarchy_and_versioning.md`](../docs/package_hierarchy_and_versioning.md): quick hierarchy tree and current versioning model
3. [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md): generated dependency layers and direct graph
4. [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md): guardrails for allowed dependency directions

Current versioning note:

- every package has its own `project.version`
- the workspace is still effectively lockstep versioned today because internal
  package dependencies are pinned with exact `==` versions
- see [`../docs/package_hierarchy_and_versioning.md`](../docs/package_hierarchy_and_versioning.md) for the precise current status

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
  neutral `hla.rti_backends` entry point group, with
  `hla2010.rti_backends` retained as the 2010 compatibility alias.
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

## Edit Here First

Use these ownership cards when you want to know where a human should safely
start editing without tracing the whole package graph first.

The rule is simple:

- spec contract or FOM model change: start at `hla2010-spec`
- concrete in-memory backend behavior: start at `hla2010-rti-python`
- shared backend adapter behavior: start at `hla2010-rti-backend-common`
- factory selection or runtime helper behavior: start at `hla2010-rti-runtime-common`
- package-owned example or FOM logic: start at `hla2010-fom-*`

## Ownership Cards

Use these cards when you need the shortest safe edit boundary.

### `hla2010-spec`

- Purpose: public spec surface, runtime facade, shared HLA value types, FOM helpers
- Edit here for: public RTI methods, callback contracts, shared exceptions, FOM parsing and merge behavior
- Do not edit here for: concrete backend behavior, vendor runtime launch code, transport adapters
- First files: `packages/hla2010-spec/src/hla2010/spec/__init__.py`, `packages/hla2010-spec/src/hla2010/runtime_api.py`, `packages/hla2010-spec/src/hla2010/fom.py`
- Quick tests: `python3 -m pytest tests/test_python_api_spec.py tests/factories/test_fom_omt_parsing.py -q`
- Package README: [`hla2010-spec/README.md`](hla2010-spec/README.md)

### `hla2010-rti-python`

- Purpose: primary in-memory reference RTI backend
- Edit here for: RTI service implementation, backend state changes, callback delivery, Python-first scenario behavior
- Do not edit here for: public spec contract changes, vendor runtime discovery, Java bridge behavior
- First files: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`, `packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`, `packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py`
- Quick tests: `python3 -m pytest tests/backends/test_python_rti_service_registry.py tests/test_python_api_spec.py -q`
- Package README: [`hla2010-rti-python/README.md`](hla2010-rti-python/README.md)

### `hla2010-rti-backend-common`

- Purpose: shared backend-neutral adapter and conversion support
- Edit here for: behavior shared by more than one backend family, common invocation helpers, backend-neutral time/helper policy
- Do not edit here for: one backend's local service logic or vendor-specific runtime concerns
- First files: `packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/base.py`, `packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/plugin_api.py`
- Quick tests: `python3 -m pytest tests/architecture/test_runtime_adapter_no_magic.py tests/test_package_boundary.py -q`
- Package README: [`hla2010-rti-backend-common/README.md`](hla2010-rti-backend-common/README.md)

### `hla2010-rti-runtime-common`

- Purpose: backend factory selection, plugin discovery, runtime-process helpers
- Edit here for: RTI factory selection flow, backend instantiation helpers, shared process lifecycle support
- Do not edit here for: concrete RTI service semantics or public spec methods
- First files: `packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/factory.py`, `packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/__init__.py`
- Quick tests: `python3 -m pytest tests/test_package_boundary.py tests/test_rti_runtime_common_split_package.py -q`
- Package README: [`hla2010-rti-runtime-common/README.md`](hla2010-rti-runtime-common/README.md)

### `hla2010-fom-*`

- Purpose: package-owned FOM resources and reusable scenario helpers
- Edit here for: new FOM XML, federate helpers, scenario logic, reusable package-backed examples
- Do not edit here for: backend internals, root namespace facades, vendor launch logic
- First files: `packages/hla2010-fom-minimal-demo/README.md`, `packages/hla2010-fom-target-radar/README.md`, `docs/create_federate_and_fom.md`
- Quick path: `./tools/new-fom-package your-demo`
- Quick tests: `python3 -m pytest tests/examples/test_minimal_fom_demo.py tests/examples/test_new_fom_package_scaffold.py -q`

## Read Next

1. [`hla2010-spec/README.md`](hla2010-spec/README.md)
2. [`hla2010-rti-python/README.md`](hla2010-rti-python/README.md)
3. [`../docs/package_layout.md`](../docs/package_layout.md)
4. [`../docs/package_dependency_tree.md`](../docs/package_dependency_tree.md)
5. [`../docs/create_federate_and_fom.md`](../docs/create_federate_and_fom.md)
6. [`../docs/import_boundary_rules.md`](../docs/import_boundary_rules.md)
