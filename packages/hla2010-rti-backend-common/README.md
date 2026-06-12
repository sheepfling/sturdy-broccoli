# hla2010-rti-backend-common

Shared backend conversion support package for `hla2010-spec`.

This package owns backend-neutral conversion helpers such as native handle
registries, backend value conversion policy, and Java handle-type inference.
Import the canonical implementation from `hla2010_rti_backend_common`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_backend_common_split_package.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
