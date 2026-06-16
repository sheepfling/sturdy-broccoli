# hla-backend-common docs

This package owns backend-neutral support code used across installable HLA 2010
backend families.

Key owned surfaces:
- `hla.backends.common.base`: core backend abstractions and recording
  helpers.
- `hla.backends.common.conversion`: handle/value conversion and native
  handle registry support.
- `hla.backends.common.plugin_api`: backend and transport plugin/spec
  contracts.
- `hla.backends.common.time_management`: shared time-management helper
  algorithms reused by backend implementations.
- `tests/test_rti_backend_common_split_package.py`: split-package guard
  coverage for backend-common.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable backend-support package boundary.

This package is not itself a backend or operator entrypoint.
