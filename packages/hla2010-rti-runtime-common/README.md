# hla2010-rti-runtime-common

Shared vendor-runtime process helper package for `hla2010-spec`.

This package owns the subprocess lifecycle and loopback TCP helper utilities
used by vendor runtime launch code such as CERTI and Pitch, plus the shared
runtime-facing backend factory helpers used by split backend packages.

Use this package when code needs to:

- create RTI ambassadors from installed backend plugins
- discover backend plugins without importing concrete backend packages directly
- manage shared runtime launch or process lifecycle behavior

Import the canonical implementation from `hla2010_rti_runtime_common`.
It does not own human operator entrypoints; those live under `./tools/`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_runtime_common_split_package.py` and
`tests/test_package_boundary.py`.

## Ownership Card

- Edit here for: backend factory selection, plugin discovery, shared process lifecycle support
- Do not edit here for: concrete RTI service semantics, public spec method definitions
- First files to open:
  `src/hla2010_rti_runtime_common/factory.py`,
  `src/hla2010_rti_runtime_common/__init__.py`
- Quick tests:
  `python3 -m pytest tests/test_package_boundary.py tests/test_rti_runtime_common_split_package.py -q`
