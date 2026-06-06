# Scripts

This directory holds the repo-local entrypoints for setting up and validating
the IEEE 1516.1-2010 workspace, including the vendored CERTI tree.

Core workflow:

- `bootstrap_python.sh` create or refresh the local Python virtualenv and
  install editable project dependencies
- `rebuild_certi.sh` configure, build, and install the repo-local CERTI source
  tree into `CERTI-build/` and `CERTI-install/`
- `bootstrap_all.sh` run both of the above in sequence
- `run_certi_local.sh` launch `rtig` or `rtia` against the repo-local CERTI
  install
- `setup_pitch_state.sh` seed and then preserve a persistent Pitch `user.home`
  under the repo-managed local-state root so the free-runtime acceptance dialog
  is not reintroduced on every launch
- `run_pitch_local.sh` launch the extracted Pitch runtime if present
- `setup_local_git_remote.sh` create or refresh a local bare Git remote under
  the repo-managed local-state root and attach it as a named remote
- `run_two_federate_suite.py` execute the composite two-federate suite and emit
  JSON, CSV, Markdown, and SVG artifacts under `analysis/`

Quality gates:

- `ci/install_python.sh` install the local QA environment used by CI and local reruns
- `ci/lint.sh` run the repo lint/syntax gate
- `ci/check_generated_docs.sh` verify the generated backend alias inventory is in sync with `rti.py`
- `ci/lint_backlog.sh` report the broader Ruff backlog without making it a required gate
- `ci/lint_strict.sh` run an opt-in stricter Ruff gate, including `E501`, with temporary excludes for the largest legacy/generated files
- `ci/test.sh` run pytest for the full suite or for selected paths
- `ci/seed_suite.sh` run the default CI quality gate locally
- `ci/vendor_runtime_smoke.sh` run the CERTI or Pitch vendor runtime profiles

The helper scripts default their generated downloads, caches, and local
runtime state to `/private/tmp/hla-2010` so the iCloud-synced workspace stays
clean. That includes Pitch state and the default service-report sink used by
the Python RTI backend.

The GitHub workflows are intentionally thin wrappers around these scripts. If a
quality gate changes, update the script first and let CI call through to it.
