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
- `vendor_edge_matrix.sh`: explicit high-value vendor probe packet across time-query, negotiated ownership, save/restore, and DDM slices
- `vendor_probe_stability.sh`: repeated-run probe harness for dedicated runner stability evidence
- `vendor_probe_review.sh`: repeated-run probe wrapper that also writes promotion review and refreshes the parity packet
- `write_vendor_probe_promotion_review.py`: summarize which repeated-run probe slices are actual promotion-review candidates
- `emit_vendor_runtime_reports.sh`: shared post-lane runtime-status and parity artifact emitter
- `write_vendor_runtime_job_summary.py`: render normalized runtime-status artifacts into a GitHub job summary
- `check_vendor_runtime_ci_state.py`: validate dedicated runner runtime env/path state before vendor-green jobs
- `../check_vendor_runner_template_drift.py`: verify the runner provisioning template, validator profiles, and workflow env contracts stay aligned
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
- Both wrappers now emit normalized post-run artifacts:
  - `analysis/vendor_runtime_status/...`
  - `analysis/vendor_parity_artifacts/...`
  even when the underlying lane fails or skips after preflight.
- `.github/workflows/ci.yml` now reflects that split directly:
  it also runs a lightweight `vendor-runner-contract` guard so the runner
  template, validator profiles, and workflow env blocks do not drift apart.
  Specifically:
  `vendor-runner-contract` runs `python3 scripts/check_vendor_runner_template_drift.py`;
  `repo-green` runs `./scripts/ci/repo_green.sh`, while the vendor-runtime jobs
  run `./scripts/ci/vendor_green.sh ...`.

### Docs / Generated Artifacts

- `check_generated_docs.sh`: verify generated backend alias inventory
- `check_doc_links.py`: verify Markdown link integrity and catch repo-root-relative assumptions in docs

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
