# hla2010-rti-backend-common

Shared backend conversion support package for `hla2010-spec`.

This package owns backend-neutral conversion helpers such as native handle
registries, backend value conversion policy, Java handle-type inference, and
the shared backend adapter contract.

Use this package when logic is:

- shared by multiple backend families
- about backend-neutral conversion or adapter behavior
- not specific to one concrete runtime family

Import the canonical implementation from `hla2010_rti_backend_common`.
It does not own human operator entrypoints; those live under `./tools/`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_backend_common_split_package.py` and
`tests/test_package_boundary.py`.

## Ownership Card

- Edit here for: backend-neutral adapter behavior, shared invocation helpers, conversion policy shared by multiple backend families
- Do not edit here for: single-backend service logic or vendor-runtime launch behavior
- First files to open:
  `src/hla2010_rti_backend_common/base.py`,
  `src/hla2010_rti_backend_common/plugin_api.py`
- Quick tests:
  `python3 -m pytest tests/architecture/test_runtime_adapter_no_magic.py tests/test_package_boundary.py -q`
