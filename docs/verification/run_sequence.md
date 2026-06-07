# Verification Run Sequence

This page is the canonical easy-run sequence for the repo.

Use it when you want the whole lifecycle in one order:

1. install
2. compilation
3. unit tests
4. integration smoke
5. integration tests
6. compliance matrices
7. full backend matrixed compliance
8. other evidence-producing checks

Canonical command:

```bash
./scripts/ci/full_sequence.sh
```

Canonical order of the underlying steps:

1. `scripts/ci/install_python.sh`
2. `scripts/ci/lint.sh`
3. `scripts/ci/test.sh`
4. `scripts/ci/vendor_runtime_smoke.sh matrix`
5. `scripts/run_two_federate_suite.py`
6. `scripts/ci/target_radar_backend_matrix.sh`
7. `scripts/ci/target_radar_proof.sh`
8. `scripts/ci/section8_backend_matrix_gate.sh`
9. `scripts/ci/vendor_runtime_smoke.sh all`

What each stage means:

- install: create or refresh the Python environment
- compilation: syntax and lint gate, including generated-doc checks
- unit tests: the normal pytest suite
- integration smoke: CERTI/Pitch runtime smoke coverage
- integration tests: composite two-federate artifact generation
- compliance matrices: Section 8 compliance artifact generation
- full backend matrixed compliance: the broad vendor/runtime smoke matrix
- other evidence-producing checks: target/radar matrices and proof packet

Use this page when you want the sequence without chasing individual wrapper
names.
