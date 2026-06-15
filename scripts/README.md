# Scripts

Repo-local entrypoints are organized the same way as the docs:

`entrypoint -> family -> command -> evidence`

Start here:

- [../README.md](../README.md): operator-facing install and smoke entry point
- [../docs/README.md](../docs/README.md): documentation index
- [../docs/python_environment.md](../docs/python_environment.md): Python bootstrap, `.venv`, extras, and install order
- [../docs/documentation_hierarchy.md](../docs/documentation_hierarchy.md): canonical doc hierarchy
- [../java_shims/README.md](../java_shims/README.md): Java bridge verification-fixture contract
- `./tools/lint`: canonical local lint and doc-link verification flow

The `scripts/` tree is implementation and CI plumbing, not the primary
human-facing operator surface.

Supported human-facing entrypoints live under `tools/` for vendor/runtime work:

- `./tools/bootstrap` canonical workspace bootstrap and doctor flow
- `./tools/python` canonical Python / repo-green verification flow
- `./tools/certi-easy` canonical CERTI install, doctor, build, run, smoke/compare, and best-effort verify flow
- `./tools/pitch` canonical Pitch Docker-backed install, start, strict smoke/verify, best-effort smoke/verify, and support flow
- `./tools/vendor-green` canonical strict vendor-runtime verification flow
- `./tools/vendor-state` canonical vendor preflight classification and CI-state flow
- `./tools/vendor-parity` canonical backend parity artifact flow
- `./tools/compliance` canonical compliance packet generation and backend-discovery flow
- `./tools/vendor-probe-review` canonical repeated-run probe review and promotion-review artifact flow
- `./tools/vendor-edge` canonical vendor edge matrix flow
- `./tools/rti-options` canonical generated RTI route/options matrix flow
- `./tools/fom-overview` canonical merged FOM/MIM overview artifact flow
- `./tools/package-deps` canonical split-package dependency tree flow
- `./tools/section8-gate` canonical Section 8 backend-matrix gate
- `./tools/target-radar` canonical target/radar proof and backend-matrix artifact flow
- `./tools/lint` canonical local lint, link, and generated-doc hygiene flow
- `./tools/two-federate` canonical generic two-federate artifact flow
- `./tools/test` canonical direct pytest wrapper

Repo setup entrypoints that still live under `scripts/`:

- `scripts/bootstrap_profile.sh` profile-based setup implementation behind `./tools/bootstrap`
- `scripts/bootstrap_python.sh` split-package bootstrap implementation called by `./tools/bootstrap python`

Normal setup order:

1. `./tools/bootstrap python`
2. `source .venv/bin/activate`
3. run a pure-Python smoke path
4. only then move on to CERTI, Pitch, JPype, or Py4J work

The repository root is not an installable Python distribution. Python setup
installs the split packages in editable mode, starting with
`packages/hla2010-spec`. Do not use root `pip install -e .` and do not add
workspace source roots through `.pth` or `sys.path` injection.

Python scripts assume the split packages are already importable. Run
`./tools/bootstrap python` or install the package roots in editable mode
before invoking Python scripts directly; scripts do not mutate `sys.path` or
bootstrap imports themselves. If you run a script without that environment, it
should fail plainly with a normal import error.

Repo-aware Python scripts use the current working directory as the default
project root. Run them from the repository root, or pass `--project-root PATH`
for scripts that read or write repository artifacts from another directory.

Operator guide links:

- [../packages/hla2010-rti-certi/docs/certi_section8_runbook.md](../packages/hla2010-rti-certi/docs/certi_section8_runbook.md): CERTI operator runbook
- [../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md](../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md): Pitch selection and troubleshooting
- [../docs/preflight_artifacts.md](../docs/preflight_artifacts.md): JSON preflight artifacts and inspection examples
- `./tools/certi-easy preflight [--json] [--json-file FILE]`: CERTI readiness check before install or smoke
- `./tools/pitch preflight [--json] [--json-file FILE]`: Pitch Docker readiness check before install or run
- `./tools/vendor-state classify --lane repo-green|vendor-green [--vendor certi|pitch] [--json]`: classify preflight artifacts into ready vs blocked vs broken states
- `./tools/vendor-state ci-state --profile ...`: validate dedicated CI runtime env/path state before vendor-green execution
- `scripts/ci/write_vendor_runtime_job_summary.py`: CI helper that renders normalized vendor runtime status into GitHub-job-friendly Markdown
- `scripts/check_vendor_runner_template_drift.py`: CI helper that verifies the runner provisioning template, validator profiles, and workflow env contracts stay aligned
- `scripts/ci/vendor_runtime_smoke.sh`: implementation wrapper behind the vendor-runtime lane; it runs mandatory vendor preflight first, writes standard JSON artifacts under `analysis/preflight_artifacts/`, and can still classify/skip blocked vendor runs even when the repo virtualenv has not been activated yet
- `./tools/python verify`: canonical Python / repo-green wrapper around the default full verification lane
- `./tools/vendor-green [profile]`: strict vendor-runtime gate for dedicated real-runtime runners; under CI it self-validates the dedicated runner contract before trying the runtime lane
- `scripts/ci/vendor_probe_stability.sh`: repeated probe implementation used by the promotion-review flow; under CI it validates the dedicated runner contract once before collecting repeated-run evidence and disables redundant per-attempt revalidation inside the loop
- `./tools/vendor-probe-review <profile> [repeat-count]`: canonical repeated-run probe review wrapper over the promotion path
- `./tools/vendor-probe-review promotion-review`: canonical promotion-review artifact generator
- `./tools/vendor-edge [time-query|negotiated-ownership|save-restore|ddm|all]`: canonical high-value vendor edge packet refresh

CI lane rule:

- use `./tools/python verify` for the default repo-green lane
- use `./tools/vendor-green [profile]` for dedicated real-runtime runners
- treat `scripts/ci/vendor_runtime_smoke.sh` as the shared implementation
  behind the vendor-green lane, not as the preferred top-level CI contract

Copy-paste preflight artifact flow:

```bash
mkdir -p analysis/preflight_artifacts

./tools/certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
python3 -m json.tool analysis/preflight_artifacts/certi-preflight.json

./tools/pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
python3 -m json.tool analysis/preflight_artifacts/pitch-preflight.json
```

Both preflight entrypoints also accept `--json` for machine-readable output.
The canonical `./tools/certi-easy preflight` and `./tools/pitch preflight` commands now also persist the
default JSON artifact plus normalized runtime-status/parity
reports even when no explicit `--json-file` is provided.
The vendor smoke wrapper writes the same JSON artifacts by default before it
decides whether to run or skip a vendor profile.

Compatibility aliases that remain for implementation and migration support:

- `./scripts/certi_easy.sh`
- `./scripts/pitch_docker_easy.sh`

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
- `ci/vendor_runtime_smoke.sh`: CERTI and Pitch runtime smoke matrix with mandatory preflight and artifact emission
- `ci/vendor_green.sh`: strict vendor-runtime gate for dedicated real-runtime runners

### Pitch Runtime

- `check_pitch_preflight.sh`: Docker and bundled Pitch readiness probe
- `setup_pitch_state.sh`: persistent Pitch `user.home`
- `run_pitch_local.sh`: launch extracted Pitch runtime
- `pitch_docker_easy.sh`: compatibility alias behind the top-level `./tools/pitch` operator flow
- `run_pitch_docker_crc.sh`: Docker-backed Pitch CRC runner
- `accept_pitch_dialog.sh`: acceptance dialog helper

### Evidence and Analysis

- `run_two_federate_suite.py`: composite two-federate artifact packet through the repo-level workspace wrapper, including vendor launcher injection when vendor packages are installed
- `run_target_radar_backend_matrix.py`: target/radar backend diagnostic packet
- `run_target_radar_proof.py`: target/radar proof packet
- `generate_fom_overview.py`: merged FOM/MIM tree and matrix overview packet, with optional interactive HTML output via `--html`
- `generate_compliance_artifacts.py`: compliance and requirements packet
- `update_rti_options_matrix.py`: generated backend-alias section for `docs/rti_options_and_test_matrix.md`
- `generate_imported_packet_requirements_docs.py`: packet-style markdown views from the imported canonical v1.0 requirements catalog
- `generate_imported_packet_backlog.py`: repo-native implementation backlog views derived from the harmonized requirements ledgers and imported packet
- `discover_backend_compliance.py`: one-command backend/spec compliance discovery over the generated packet
- `report_test_requirement_markers.py`: CSV report of explicit pytest requirement markers, defaulting to the backend modules currently carrying Clause 4 through Clause 10 markers
- `diagnose_pitch_exchange.py`: Pitch exchange diagnostics
- `diagnose_pitch_negotiated_ownership.py`: Pitch negotiated-ownership diagnostics

When `generate_compliance_artifacts.py` finishes, the best operator entrypoints are:

- `analysis/compliance/verification_assets.json`: named verification slices and their evidence
- `analysis/compliance/verification_traceability.csv`: flat clause-to-asset traceability
- `analysis/compliance/requirements_ledger.csv`: requirement-level pass/partial/fail ledger
- `analysis/compliance/requirements_matrix_2010.csv`: whole-spec matrix spanning section areas, service rows, and verification slices
- `analysis/compliance/python_requirement_disposition.md`: generated Python backend requirement disposition packet
- `analysis/compliance/certi_requirement_disposition.md`: generated aggregate CERTI family requirement disposition packet
- `analysis/compliance/certi-native_requirement_disposition.md`: generated explicit CERTI native-runtime requirement disposition packet
- `analysis/compliance/pitch_requirement_disposition.md`: generated aggregate Pitch family requirement disposition packet
- `analysis/compliance/pitch-jpype_requirement_disposition.md`: generated explicit Pitch JPype-profile requirement disposition packet
- `analysis/compliance/pitch-py4j_requirement_disposition.md`: generated explicit Pitch Py4J-profile requirement disposition packet
- `analysis/compliance/portico_requirement_disposition.md`: generated aggregate Portico family requirement disposition packet
- `analysis/compliance/portico-jpype_requirement_disposition.md`: generated explicit Portico JPype-profile requirement disposition packet
- `analysis/compliance/portico-py4j_requirement_disposition.md`: generated explicit Portico Py4J-profile requirement disposition packet
- `analysis/compliance/extracted_requirements_clause5_6.md`: Clause 5/6 packet split into broad-spec and supported-subset rows
- `analysis/compliance/extracted_requirements_clause7_9.md`: Clause 7/9 packet split into broad-spec and supported-subset rows
- `analysis/compliance/supported_subset_policy.md`: explicit supported-subset policy statements for defended partial rows
- `analysis/compliance/defended_partials_index.md`: review-facing index of broad partial rows and the narrower passing subset rows that defend them

For the shortest “what do we know about backend compliance right now?” path:

```bash
./tools/bootstrap python
source .venv/bin/activate
./tools/compliance generate
./tools/compliance discover --show-backlog
```

From outside the repository, pass `--project-root /path/to/hla-2010` to these
commands.

Use `--backend BACKEND_ID_OR_FAMILY`, `--section SECTION`, or `--priority PRIORITY` to narrow the backlog view, and `--format json` for machine-readable output.

New generated backlog artifacts:

- `analysis/compliance/vendor_discovery_backlog.json`
- `analysis/compliance/vendor_discovery_backlog.md`

### CI Wrappers

- [ci/README.md](ci/README.md): CI wrapper family index
- `ci/install_python.sh`: local QA environment install
- `ci/full_sequence.sh`: full verification sequence with lint and type annotations
- `ci/repo_green.sh`: explicit repo-green wrapper around `full_sequence.sh`
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
- `setup_local_state.sh`: create the repo-local vendor runtime/build state layout under `.local/`
- `setup_local_git_remote.sh`: local bare Git remote
- `scripts/lib/shell.sh`: shared shell helper library

### Other Helpers

- `run_certi_local.sh`: direct CERTI `rtig` / `rtia` launcher
- `run_pitch_local.sh`: direct Pitch launcher
- `run_pitch_docker_crc.sh`: Docker-backed Pitch CRC launcher
- `run_two_federate_suite.py`: composite suite artifact packet
- `generate_compliance_artifacts.py`: compliance packet generator
- `ci/check_doc_links.py`: canonical Markdown link integrity checker

## Operating Rules

- Keep generated verification outputs under `analysis/`, and keep transient
  vendor runtime/build state under `.local/`.
- Update the shell scripts first, then let CI call through to them.
- Keep the wrappers thin: the scripts should orchestrate, not reimplement the
  backend logic or the evidence generation logic.
