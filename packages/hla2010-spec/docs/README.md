# hla2010-spec docs

This package owns the abstract HLA 2010 spec and core API surface for the
workspace.

Key owned surfaces:
- `src/hla2010`: the abstract spec namespace, core types, handles, enums,
  exceptions, time, FOM/MOM helpers, and API/spec references.
- `hla2010.rti`: only the intentionally narrow temporary root facade needed for
  backend discovery during the split-package migration.
- package metadata and boundary rules proving that concrete backend
  implementations stay outside the root `hla2010` namespace.
- `tests/test_package_split_scaffolds.py`, `tests/test_root_facade_policy.py`,
  `tests/test_namespace_policy.py`, and `tests/test_python_api_spec.py`: guard
  coverage for the root-namespace boundary and the temporary facade contract.

This package must not own concrete RTI backend implementations, vendor runtime
discovery, transport implementations, or repo-internal verification logic.
