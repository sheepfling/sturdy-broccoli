# hla-verification docs

This package owns backend-neutral shared verification scenarios and generic
two-federate suite helpers for the multi-package HLA 2010 workspace.

Key owned surfaces:
- `hla.verification.scenario_*`: shared scenario bodies used by
  backend wrapper tests and compliance artifacts.
- `hla.verification.two_federate_suite_*`: reusable suite pairing,
  summary, timeline, and writer helpers.
- `hla.verification.section8_matrix`: shared Clause 8 time
  management scenario cases.
- `tests/test_verification_harness_split_package.py`: split-package guard
  coverage for the shared harness package.
- `tests/test_backend_wrapper_policy.py`: guard coverage that backend and
  transport runtime suites remain thin wrappers over harness entrypoints.

This package intentionally does not own vendor runtime policy, backend
implementations, or example/FOM-specific operator guidance.
