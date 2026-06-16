# hla-rti-core

Shared vendor-runtime process helper package for `hla-rti1516e`.

This package owns the subprocess lifecycle and loopback TCP helper utilities
used by vendor runtime launch code such as CERTI and Pitch, plus the shared
runtime-facing backend factory helpers used by split backend packages.

Use this package when code needs to:

- create RTI ambassadors from installed backend plugins
- discover backend plugins without importing concrete backend packages directly
- manage shared runtime launch or process lifecycle behavior

Import the canonical implementation from `hla.rti`.
It does not own human operator entrypoints; those live under `./tools/`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_runtime_common_split_package.py` and
`tests/test_package_boundary.py`.
