# hla2010-rti-runtime-common

Shared vendor-runtime process helper package for `hla2010-spec`.

This package owns the subprocess lifecycle and loopback TCP helper utilities
used by vendor runtime launch code such as CERTI and Pitch.
Import the canonical implementation from `hla2010_rti_runtime_common`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_runtime_common_split_package.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
