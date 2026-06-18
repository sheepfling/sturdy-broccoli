# hla-fom-proto2025-space-lite docs

This package owns the Proto2025 SpaceLite internal showcase runner and related
package-specific support.

Key owned surfaces:

- `hla.foms.proto2025_space_lite._internal`: repo-internal SpaceLite showcase
  runner.
- package-owned showcase support reused by the repo-internal combined Proto2025 showcase orchestration layer.
- `tests/test_fom_proto2025_space_lite_split_package.py`: split-package guard
  coverage for the installable SpaceLite showcase package.

This package does not own RTI backend implementations, generic shared
verification-harness scenarios, or the shared Proto2025 2025 XML resource bundle.

If you want the package entrypoint and usage story, read
[`../README.md`](../README.md).
