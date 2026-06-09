# Package Split Workspace

This directory contains the installable workspace packages for the repo. Some
packages still carry migration metadata, but several already own their runtime
implementation outright. The root `src/hla2010/` package now serves as the
stable API and compatibility layer while backend families move behind these
package-owned source roots.

Before you work in any package subtree, bootstrap the workspace Python
environment from the repo root:

1. `./bootstrap python`
2. `source .venv/bin/activate`
3. run a pure-Python smoke path

The canonical environment and install-order guide is
[`../docs/python_environment.md`](../docs/python_environment.md).

The target dependency direction is:

```text
hla2010-spec
  <- hla2010-rti-python
  <- hla2010-rti-certi
  <- hla2010-rti-backend-common
  <- hla2010-rti-java-common
  <- hla2010-rti-runtime-common
  <- hla2010-rti-java-jpype
  <- hla2010-rti-java-py4j
  <- hla2010-rti-pitch-common
       <- hla2010-rti-pitch-jpype -> hla2010-rti-java-jpype
       <- hla2010-rti-pitch-py4j -> hla2010-rti-java-py4j
  <- hla2010-rti-portico -> hla2010-rti-java-jpype / hla2010-rti-java-py4j
  <- hla2010-verification-harness
  <- hla2010-fom-target-radar
```

Rules for the split:

- `hla2010-spec` owns the abstract API, shared HLA value types, exceptions,
  FOM/MOM helpers needed by federates, and backend plugin contract.
- RTI packages own one backend family and register through the
  `hla2010.rti_backends` entry point group.
- Verification-harness packages own shared repo-internal suite/report helpers.
- FOM/example packages own concrete resources and scenario helpers.
- Vendor runtime packages own their own runbooks and vendor-specific findings under `packages/<name>/docs/`.
- Backend packages may depend on `hla2010-spec`, but `hla2010-spec` must not
  import concrete backends, vendor runtime discovery, test shims, or examples.
- During migration, package ownership moves one family at a time after
  import-boundary tests are in place. A package marked
  `implementation-moved` in its `pyproject.toml` is already the canonical
  implementation root for that family.

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
12. `hla2010-verification-harness`
13. `hla2010-fom-target-radar`
14. trim `hla2010-spec` to the final core surface
