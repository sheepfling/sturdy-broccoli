# hla-fom-hlax-message-test docs

This package owns the HLA-X MessageTest internal showcase runner and related
package-specific support.

Key owned surfaces:

- `hla.foms.hlax_message_test._internal`: repo-internal MessageTest showcase
  runner.
- package-owned showcase support reused by the repo-internal combined HLA-X showcase orchestration layer.
- `tests/test_fom_hlax_message_test_split_package.py`: split-package guard
  coverage for the installable MessageTest showcase package.

This package does not own RTI backend implementations, generic shared
verification-harness scenarios, or the shared HLA-X 2025 XML resource bundle.

If you want the package entrypoint and usage story, read
[`../README.md`](../README.md).
