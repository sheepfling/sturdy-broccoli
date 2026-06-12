# Pitch Section 8 time-management vendor divergence note

Date: `2026-06-11`

Scope:
- Vendor: `Pitch pRTI Free 5.5.10 build 9905`
- Runtime modes exercised by the shared matrix wrappers:
  - `pitch-jpype`
  - `pitch-py4j`
- Clause family:
  - `REQ-RTI-TM-8_10-nextMessageRequest`
  - `REQ-RTI-TM-8_11-nextMessageRequestAvailable`
  - `REQ-RTI-TM-8_21-retract`
  - `REQ-FED-TM-8_22-requestRetraction`
  - `HLA1516.1-TM-8.1-001`
  - `HLA1516.1-TM-8.1-002`
  - `HLA1516.1-TM-8.1.1-001`
  - `HLA1516.1-TM-8.1.2-001`
  - `HLA1516.1-TM-8.1.2-002`
  - `HLA1516.1-TM-8.1.2-003`
  - `HLA1516.1-TM-8.1.2-004`
  - `HLA1516.1-TM-8.1.3-002`
  - `HLA1516.1-TM-8.1.3-003`
  - `HLA1516.1-TM-8.1.5-001`
  - `HLA1516.1-TM-8.1.6-001`
  - `HLA1516.1-TM-8.1.7-001`
  - `HLA1516.1-TM-8.10-001`
  - `HLA1516.1-TM-8.21-001`

## Summary

Pitch is promotable for the shared Clause 8 state-service, ordering-query,
order-override, and bounded-query coverage that the harness executes portably.

These rows remain `vendor-divergent` because the real Java bridge routes do not
fully reproduce the shared harness expectation for the narrow next-message and
retraction semantics exercised by the Python parity matrix:
- `nextMessageRequest` does not reproduce the expected grant-plus-release shape
- `nextMessageRequestAvailable` and `retract` do not expose the expected
  Python-level retraction-return semantics in the shared available/retraction
  scenario
- `requestRetraction` does not expose the expected Python-level retraction
  handle callback semantics in the shared callback scenario

## Shared evidence already in repo

The shared harness scenarios covering this family are:
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_ordering_and_query_case`
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_available_and_retraction_case`
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_request_retraction_case`
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_state_services_case`
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_order_override_case`

The thin backend wrappers are:
- `tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries`
- `tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_retraction`
- `tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_request_retraction_callback`
- `tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_services`
- `tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_retraction_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_request_retraction_callback_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_services_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_order_override_services_matrix`

## Why the rows stay vendor-divergent

The generated Clause 8 Pitch disposition is no longer missing or ambiguous:
these rows are explicitly attached to shared harness evidence and remain
`vendor-divergent` only for the narrow real-runtime mismatches above.

Promoting these rows to `verified` would overclaim parity between the shared
Python-oriented Clause 8 matrix semantics and the real Java bridge behavior
that Pitch currently exposes. The correct generated disposition remains
`vendor-divergent` until the Pitch bridges reproduce the shared next-message and
retraction semantics or the requirement slice is narrowed further.
