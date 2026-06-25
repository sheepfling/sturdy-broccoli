# Verification Run Sequence

This page is the canonical easy-run sequence for the repo.

Use it when you want the whole lifecycle in one order:

1. install
2. compilation
3. lint / type annotations
4. unit shards
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

1. `scripts/validate_test_surface_manifest.py`
2. `scripts/ci/install_python.sh`
3. `scripts/ci/lint.sh`
4. `scripts/ci/pyright.sh`
5. `./tools/test-surface run repo-green-units`
6. `scripts/ci/vendor_runtime_smoke.py matrix`
7. `scripts/run_two_federate_suite.py`
8. `scripts/ci/target_radar_backend_matrix.sh --backend python1516e --backend java-shim-jpype --backend java-shim-py4j`
9. `scripts/ci/target_radar_proof.sh`
10. `scripts/ci/section8_backend_matrix_gate.sh`
11. `scripts/ci/vendor_runtime_smoke.py all`

What each stage means:

- install: create or refresh the Python environment
- manifest validation: confirm the named test-surface lanes and shard wiring are structurally sound before any broader lane runs
- compilation: syntax and lint gate, including generated-doc checks
- lint / type annotations: scoped static typing plus import discipline
- unit shards: named repo-owned unit chunks composed through `repo-green-units`, so shard order changes live in the manifest rather than CI code
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
`python1516_2025` proof lane or the hosted `python1516_2025-fedpro-grpc` replay.

Use this page when you want the sequence without chasing individual wrapper
names.
