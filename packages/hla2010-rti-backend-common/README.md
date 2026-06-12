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
