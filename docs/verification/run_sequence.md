# Verification Run Sequence

This page is the canonical easy-run sequence for the repo.

Use it when you want the whole lifecycle in one order:

1. install
2. compilation
3. lint / type annotations
4. unit tests
5. integration smoke
6. integration tests
7. compliance matrices
8. full backend matrixed compliance
9. other evidence-producing checks

Canonical command:

```bash
./tools/python verify
```

Canonical order of the underlying steps:

1. `scripts/ci/install_python.sh`
2. `scripts/ci/lint.sh`
3. `scripts/ci/pyright.sh`
4. `scripts/ci/test.sh`
5. `scripts/ci/vendor_runtime_smoke.sh matrix`
6. `scripts/run_two_federate_suite.py`
7. `scripts/ci/target_radar_backend_matrix.sh --backend python --backend java-shim-jpype --backend java-shim-py4j`
8. `scripts/ci/target_radar_proof.sh`
9. `scripts/ci/section8_backend_matrix_gate.sh`
10. `scripts/ci/vendor_runtime_smoke.sh all`

What each stage means:

- install: create or refresh the Python environment
- compilation: syntax and lint gate, including generated-doc checks
- lint / type annotations: scoped static typing plus import discipline
- unit tests: the normal pytest suite
- integration smoke: CERTI/Pitch runtime smoke coverage
- integration tests: composite two-federate artifact generation, now including
  the trial-safe time-window future-exclusion and restore-state proof legs
- compliance matrices: Section 8 compliance artifact generation
- full backend matrixed compliance: the broad vendor/runtime smoke matrix
- other evidence-producing checks: the target/radar matrix over the core trio and the proof packet

When you want only the narrow Pitch-safe two-federate vendor probes rather than
the whole vendor matrix, use:

- `./tools/pitch time-window-probe`
- `./tools/pitch time-window-restore-state-probe`

Those commands add bounded vendor credence for the two-federate 2025
future-exclusion and restore-state routes. They do not replace the direct
`python2025` proof lane or the hosted `python-2025-fedpro-grpc` replay.

Use this page when you want the sequence without chasing individual wrapper
names.
