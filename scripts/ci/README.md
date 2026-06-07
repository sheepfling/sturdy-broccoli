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
- `full_sequence.sh`: install-to-compliance lifecycle sequence, including type annotations
- `seed_suite.sh`: default local seed suite
- `vendor_runtime_smoke.sh`: CERTI and Pitch smoke/profile runner
- `section8_backend_matrix_gate.sh`: Section 8 cross-backend matrix gate
- `target_radar_backend_matrix.sh`: target/radar backend matrix gate
- `target_radar_proof.sh`: target/radar proof packet gate

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
