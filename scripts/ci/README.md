# CI Wrappers

The `scripts/ci/` directory is a thin wrapper family around the same checks
used by local reruns and GitHub Actions.

The rule is simple:

`entrypoint -> check family -> evidence`

## Families

### Install

- `install_python.sh`: create or refresh the local Python environment used by the quality gates

### Lint / Typecheck

- `lint.sh`: required lint and syntax gate
- `lint_backlog.sh`: non-blocking Ruff backlog report
- `lint_strict.sh`: opt-in stricter Ruff gate
- `pyright.sh`: scoped static typing gate

### Test / Smoke

- `test.sh`: pytest wrapper for the selected test set
- `time.sh`: dedicated HLA 1516.1-2010 time-management suite gate
- `full_sequence.sh`: full verification sequence, including type annotations
- `repo_green.sh`: explicit repo-green wrapper around `full_sequence.sh`
- `seed_suite.sh`: default local seed suite
- `vendor_runtime_smoke.sh`: CERTI and Pitch smoke/profile runner with mandatory preflight and default JSON artifact emission
- `vendor_green.sh`: strict vendor-runtime gate for dedicated real-runtime runners
- `section8_backend_matrix_gate.sh`: Section 8 cross-backend matrix gate
- `target_radar_backend_matrix.sh`: target/radar backend matrix gate
- `target_radar_proof.sh`: target/radar proof packet gate

## Repo Green vs Vendor Green

- `full_sequence.sh` stays repo-green friendly: blocked vendor prerequisites
  short-circuit cleanly after preflight instead of failing late inside pytest.
- `repo_green.sh` is the named operator/CI entrypoint for that repo-green lane.
- `vendor_green.sh` is the strict real-runtime path: it sets
  `HLA2010_VENDOR_PREFLIGHT_STRICT=1` and fails immediately when CERTI or Pitch
  prerequisites are missing or blocked.
- `.github/workflows/ci.yml` now reflects that split directly:
  `repo-green` runs `./scripts/ci/repo_green.sh`, while the vendor-runtime jobs
  run `./scripts/ci/vendor_green.sh ...`.

### Docs / Generated Artifacts

- `check_generated_docs.sh`: verify generated backend alias inventory

## Help Convention

Every wrapper should support a small help summary:

- what family it belongs to
- what the default command does
- what artifact or evidence it updates

That keeps the CI wrappers easy to read for juniors and keeps the repo’s
automation story parallel with the docs story.

When in doubt, a CI wrapper should be a thin `bash` or `python` dispatcher
that delegates to one underlying script or test family rather than
re-implementing the workflow inline.
