# hla-rti-core docs

This package owns shared vendor-runtime process and backend-discovery helpers
used by installable runtime-backed RTI packages.

Key owned surfaces:
- `hla.rti.factory`: backend discovery, backend creation,
  and transport registration helpers.
- `hla.rti.real_rti_process`: subprocess lifecycle and
  loopback TCP listener helpers for external runtime launches.
- `tests/test_rti_runtime_common_split_package.py`: split-package guard
  coverage for runtime-common.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable runtime-common boundary.

This package is shared support code, not a backend implementation or operator
entrypoint.
