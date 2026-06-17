# HLA 2025 executable test requirements expansion

Input: `hla_2025_requirements_capabilities_tests_expanded.csv`

Output: `hla_2025_executable_test_requirements_v3.csv`

This file expands the extracted checklist/requirement rows into concrete executable test requirements. Each row includes:

- a stable `executable_test_id`
- the parent requirement ID
- scenario/fixture/precondition/action/assertion fields
- positive, negative, callback, validator, merge, trace, and report-schema test kinds
- target routes and evidence artifact paths
- suggested pytest and CLI entry points

## Counts

- Source checklist rows: 398
- Executable test requirement rows: 1117

## Top test kinds

- `surface_contract`: 196
- `trace_evidence`: 196
- `validator_negative_fixture`: 158
- `validator_positive_fixture`: 158
- `negative_or_illegal_state`: 149
- `positive_behavior`: 149
- `callback_positive`: 47
- `evidence_or_traceability`: 44
- `merge_behavior`: 18
- `matrix_guard`: 1
- `ledger_guard`: 1

## Notes

This is an executable-test backlog, not a claim that all tests already exist. The next engineering step is to turn the suggested pytest candidates into parameterized tests and wire them to route-specific evidence reports.
