# Pitch transportation subset vendor divergence note

Date: `2026-06-11`

Scope:
- Vendor: `Pitch pRTI Free 5.5.10 build 9905`
- Runtime modes exercised by the shared matrix wrappers:
  - `pitch-jpype`
  - `pitch-py4j`
- Clause family:
  - `HLA1516.1-OM-6.1.10-001`
  - `HLA1516.1-OM-6.23-001`
  - `HLA1516.1-OM-6.24-001`
  - `HLA1516.1-OM-6.25-001`
  - `HLA1516.1-OM-6.26-001`
  - `HLA1516.1-OM-6.27-001`
  - `HLA1516.1-OM-6.28-001`
  - `HLA1516.1-OM-6.29-001`
  - `HLA1516.1-OM-6.30-001`

## Summary

Pitch is promotable for the shared reliable/best-effort transportation subset, including:
- explicit attribute transportation-type changes
- explicit interaction transportation-type changes
- transportation query and report callbacks
- rejection behavior for invalid or non-owner calls
- save/restore persistence for the supported overrides

These rows remain `vendor-divergent` because the standard-language family speaks for the full transportation semantic space, while the backend surface exercised here only models the portable `HLAreliable` / `HLAbestEffort` subset.

## Shared evidence already in repo

The shared harness scenarios that execute the supported subset are:
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_scenario`
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_rejection_scenario`
- `packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario`

The thin backend wrappers are:
- `tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix`
- `tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_rejection_matrix`
- `tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_rejection_matrix`
- `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix`

## Why the rows stay vendor-divergent

The shared scenarios prove that Pitch handles the supported reliable/best-effort profile correctly. They do not prove that Pitch exposes arbitrary transportation-type semantics beyond that subset, and the repo does not model any broader portable transport family for this backend.

Because the extracted Clause 6 rows explicitly speak for the full transportation semantic space rather than only the supported subset, promoting them to `verified` would overclaim backend behavior. The correct generated disposition remains `vendor-divergent` until the backend surface or vendor evidence demonstrates broader transportation semantics.
