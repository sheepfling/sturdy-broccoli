# hla-fom-proto2025-time-mgmt-test docs

This package owns the Proto2025 TimeMgmtTest internal showcase runner and related
package-specific support.

Key owned surfaces:

- `hla.foms.proto2025_time_mgmt_test._internal`: repo-internal TimeMgmtTest showcase
  runner.
- package-owned showcase support reused by the repo-internal combined Proto2025 showcase orchestration layer.
- `tests/test_fom_proto2025_time_mgmt_test_split_package.py`: split-package guard
  coverage for the installable TimeMgmtTest showcase package.

This package does not own RTI backend implementations, generic shared
verification-harness scenarios, or the shared Proto2025 2025 XML resource bundle.

If you want the package entrypoint and usage story, read
[`../README.md`](../README.md).
