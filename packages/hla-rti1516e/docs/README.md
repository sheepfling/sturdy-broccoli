# hla-rti1516e docs

This package owns the abstract HLA 2010 spec and core API surface for the
workspace.

Key owned surfaces:
- `packages/hla-rti1516e/src/hla/rti1516e/`: the 2010 API package root, core
  types, handles, enums, exceptions, time, FOM/MOM helpers, and API/spec
  references.
- `hla.rti1516e.rti`: the version-local backend-discovery and ambassador
  creation helper.
- package metadata and boundary rules proving that concrete backend
  implementations stay outside the `hla.rti1516e` API package.
- `tests/test_package_split_scaffolds.py`, `tests/test_root_facade_policy.py`,
  `tests/test_namespace_policy.py`, and `tests/test_python_api_spec.py`: guard
  coverage for the package boundary and API surface contract.

This package must not own concrete RTI backend implementations, vendor runtime
discovery, transport implementations, or repo-internal verification logic.
