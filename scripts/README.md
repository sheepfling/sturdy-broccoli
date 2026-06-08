# Scripts

Repo-local entrypoints are organized the same way as the docs:

`entrypoint -> family -> command -> evidence`

Start here:

- [../README.md](../README.md): operator-facing install and smoke entry point
- [../docs/README.md](../docs/README.md): documentation index
- [../docs/documentation_hierarchy.md](../docs/documentation_hierarchy.md): canonical doc hierarchy

Primary operator entrypoints:

- `./bootstrap` profile-based setup for `python`, `certi`, `pitch`, or `all`
- `./certi-easy` CERTI install, doctor, build, run, smoke, and compare flow

Operator guide links:

- [../docs/certi_section8_runbook.md](../docs/certi_section8_runbook.md): CERTI operator runbook
- [../docs/pitch_decision_tree.md](../docs/pitch_decision_tree.md): Pitch selection and troubleshooting
- [../docs/preflight_artifacts.md](../docs/preflight_artifacts.md): JSON preflight artifacts and inspection examples
- `./certi-easy preflight [--json] [--json-file FILE]`: CERTI readiness check before install or smoke
- `./pitch preflight [--json] [--json-file FILE]`: Pitch Docker readiness check before install or run

Copy-paste preflight artifact flow:

```bash
mkdir -p analysis/preflight_artifacts

./certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
python3 -m json.tool analysis/preflight_artifacts/certi-preflight.json

./pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
python3 -m json.tool analysis/preflight_artifacts/pitch-preflight.json
```

Both preflight entrypoints also accept `--json` for machine-readable output.

Script families:

### Bootstrap

- `bootstrap_profile.sh`: profile-based setup dispatcher
- `bootstrap_python.sh`: editable Python environment bootstrap
- `bootstrap_all.sh`: combined Python + CERTI + Pitch bootstrap

### CERTI Runtime

- `check_certi_preflight.sh`: loopback, venv, and CERTI readiness probe
- `rebuild_certi.sh`: patched CERTI build/install
- `rebuild_certi_upstream.sh`: pristine upstream CERTI build/install
- `run_certi_local.sh`: launch local `rtig` / `rtia`
- `check_certi_preflight.py`: host/session readiness probe
- `ci/vendor_runtime_smoke.sh`: CERTI and Pitch runtime smoke matrix

### Pitch Runtime

- `check_pitch_preflight.sh`: Docker and bundled Pitch readiness probe
- `setup_pitch_state.sh`: persistent Pitch `user.home`
- `run_pitch_local.sh`: launch extracted Pitch runtime
- `pitch_docker_easy.sh`: simple Pitch Docker operator flow
- `run_pitch_docker_crc.sh`: Docker-backed Pitch CRC runner
- `accept_pitch_dialog.sh`: acceptance dialog helper

### Evidence and Analysis

- `run_two_federate_suite.py`: composite two-federate artifact packet
- `run_target_radar_backend_matrix.py`: target/radar backend diagnostic packet
- `run_target_radar_proof.py`: target/radar proof packet
- `generate_fom_overview.py`: merged FOM/MIM tree and matrix overview packet, with optional interactive HTML output via `--html`
- `generate_compliance_artifacts.py`: compliance and requirements packet
- `discover_backend_compliance.py`: one-command backend/spec compliance discovery over the generated packet
- `diagnose_pitch_exchange.py`: Pitch exchange diagnostics
- `diagnose_pitch_negotiated_ownership.py`: Pitch negotiated-ownership diagnostics

When `generate_compliance_artifacts.py` finishes, the best operator entrypoints are:

- `analysis/compliance/verification_assets.json`: named verification slices and their evidence
- `analysis/compliance/verification_traceability.csv`: flat clause-to-asset traceability
- `analysis/compliance/requirements_ledger.csv`: requirement-level pass/partial/fail ledger
- `analysis/compliance/requirements_matrix_2010.csv`: whole-spec matrix spanning section areas, service rows, and verification slices
- `analysis/compliance/extracted_requirements_clause5_6.md`: Clause 5/6 packet split into broad-spec and supported-subset rows
- `analysis/compliance/extracted_requirements_clause7_9.md`: Clause 7/9 packet split into broad-spec and supported-subset rows
- `analysis/compliance/supported_subset_policy.md`: explicit supported-subset policy statements for defended partial rows
- `analysis/compliance/defended_partials_index.md`: review-facing index of broad partial rows and the narrower passing subset rows that defend them

For the shortest “what do we know about backend compliance right now?” path:

```bash
python3 scripts/generate_compliance_artifacts.py
python3 scripts/discover_backend_compliance.py --show-backlog
```

Use `--backend BACKEND_ID_OR_FAMILY`, `--section SECTION`, or `--priority PRIORITY` to narrow the backlog view, and `--format json` for machine-readable output.

New generated backlog artifacts:

- `analysis/compliance/vendor_discovery_backlog.json`
- `analysis/compliance/vendor_discovery_backlog.md`

### CI Wrappers

- [ci/README.md](ci/README.md): CI wrapper family index
- `ci/install_python.sh`: local QA environment install
- `ci/full_sequence.sh`: full verification sequence with lint and type annotations
- `ci/lint.sh`: required lint/syntax gate
- `ci/requirements_lint.sh`: canonical imported requirements packet gate
- `ci/lint_backlog.sh`: broader Ruff backlog report
- `ci/lint_strict.sh`: stricter opt-in Ruff gate
- `ci/pyright.sh`: scoped Pyright gate used by the full verification sequence
- `ci/test.sh`: pytest wrapper
- `ci/seed_suite.sh`: default CI quality gate
- `ci/target_radar_backend_matrix.sh`: target/radar backend smoke matrix
- `ci/target_radar_proof.sh`: target/radar proof packet
- `ci/section8_backend_matrix_gate.sh`: cross-backend Section 8 matrix
- `ci/vendor_edge_matrix.sh`: vendor edge slice with `time-query` and `negotiated-ownership` subprofiles
- `ci/check_generated_docs.sh`: generated backend alias inventory sync

### Local State And Repo Plumbing

- `local_state.sh`: shared local-state helper
- `setup_local_state.sh`: create repo-managed symlinked caches/build trees
- `setup_local_git_remote.sh`: local bare Git remote
- `scripts/lib/shell.sh`: shared shell helper library

### Other Helpers

- `run_certi_local.sh`: direct CERTI `rtig` / `rtia` launcher
- `run_pitch_local.sh`: direct Pitch launcher
- `run_pitch_docker_crc.sh`: Docker-backed Pitch CRC launcher
- `run_two_federate_suite.py`: composite suite artifact packet
- `generate_compliance_artifacts.py`: compliance packet generator

## Operating Rules

- Keep generated downloads, caches, and transient runtime state under
  `/private/tmp/hla-2010`.
- Update the shell scripts first, then let CI call through to them.
- Keep the wrappers thin: the scripts should orchestrate, not reimplement the
  backend logic or the evidence generation logic.
