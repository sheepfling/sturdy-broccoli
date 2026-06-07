# Scripts

This directory holds the repo-local entrypoints for setting up and validating
the IEEE 1516.1-2010 workspace, including the vendored CERTI tree.

Core workflow:

- `../certi-easy` the simplest operator entrypoint for pristine and patched
  CERTI: install, doctor, build, run, smoke, and compare
- `bootstrap_python.sh` create or refresh the local Python virtualenv and
  install editable project dependencies
- `rebuild_certi.sh` configure, build, and install the repo-local CERTI source
  tree into `CERTI-build/` and `CERTI-install/`
- `rebuild_certi_upstream.sh` clone, build, and install a pristine upstream
  CERTI baseline from GitHub into `CERTI-upstream-source/`,
  `CERTI-upstream-build/`, and `CERTI-upstream-install/`
- `bootstrap_all.sh` run both of the above in sequence
- `check_certi_preflight.py` report whether the local host/session can actually
  run the real CERTI matrix or whether it will skip, including loopback socket
  permission failures
- `run_certi_local.sh` launch `rtig` or `rtia` against the repo-local CERTI
  install
- `setup_pitch_state.sh` seed and then preserve a persistent Pitch `user.home`
  under the repo-managed local-state root so the free-runtime acceptance dialog
  is not reintroduced on every launch
- `run_pitch_local.sh` launch the extracted Pitch runtime if present
- `setup_local_git_remote.sh` create or refresh a local bare Git remote under
  the repo-managed local-state root and attach it as a named remote
- `run_two_federate_suite.py` execute the composite two-federate suite and emit
  JSON, CSV, Markdown, and SVG artifacts under `analysis/`, including the
  profile matrix and callback timeline packet
- `generate_compliance_artifacts.py` emit the spec-traceability packet under
  `analysis/compliance/`, including service/requirement ledgers, section
  summaries, public-class mapping inventory, rows lacking exact
  requirement-level executable evidence, and the dedicated Section 8
  backend matrix

Quality gates:

- `ci/install_python.sh` install the local QA environment used by CI and local reruns
- `ci/lint.sh` run the repo lint/syntax gate
- `ci/check_generated_docs.sh` verify the generated backend alias inventory is in sync with `rti.py`
- `ci/lint_backlog.sh` report the broader Ruff backlog without making it a required gate
- `ci/lint_strict.sh` run an opt-in stricter Ruff gate, including `E501`, with temporary excludes for the largest legacy/generated files
- `ci/test.sh` run pytest for the full suite or for selected paths
- `ci/seed_suite.sh` run the default CI quality gate locally
- `ci/section8_backend_matrix_gate.sh` run the dedicated cross-backend
  Section 8 matrix and regenerate the backend-specific Section 8 compliance
  artifacts in one step
- `ci/vendor_runtime_smoke.sh` run the CERTI or Pitch vendor runtime profiles
  or the combined real-profile matrix

CERTI baseline attribution:

- Use `HLA2010_CERTI_UPSTREAM_PREFIX` for pristine/original CERTI evidence.
- Run `rebuild_certi_upstream.sh` to fetch that baseline from
  `https://github.com/etopzone/CERTI.git` unless you already have a pristine
  local install.
- Use `HLA2010_CERTI_PATCHED_PREFIX` for an explicit patched CERTI install, or
  the repo-local `CERTI-install/` from `rebuild_certi.sh` for the normal patched
  baseline.
- The `certi-upstream` selector never falls back to repo-local `CERTI-build/`
  libraries. Set `HLA2010_CERTI_UPSTREAM_BUILD_ROOT` only when the upstream
  baseline intentionally needs its own build overlay.

Recommended CERTI commands:

- `./certi-easy install`
  bootstrap Python, build patched CERTI, and clone/build pristine upstream
  CERTI in one shot
- `./certi-easy doctor`
  print the important paths and tell you whether real CERTI smoke can run in
  the current host/session
- `./certi-easy smoke compare`
  run the promoted upstream-vs-patched compare slice
- `./certi-easy run patched rtig -v 0`
  launch the patched local `rtig`
- `./certi-easy run upstream rtig -v 0`
  launch the pristine upstream `rtig`

Lower-level CERTI commands:

- `./scripts/rebuild_certi.sh`
  builds the repo-local vendored/patched CERTI baseline
- `./scripts/rebuild_certi_upstream.sh`
  clones and builds the pristine upstream CERTI baseline
- `./scripts/ci/vendor_runtime_smoke.sh certi-patched`
  runs the patched/runtime smoke and full patched CERTI matrix
- `./scripts/ci/vendor_runtime_smoke.sh certi-upstream`
  runs the upstream-only baseline probe
- `./scripts/ci/vendor_runtime_smoke.sh certi-compare`
  runs the promoted time-management baseline, negotiated-ownership baseline,
  and release-request `deny` / `confirm` / `ifwanted` branch probes against
  both upstream and patched CERTI for direct attribution
- `python3 -m pytest -q tests/time/test_section8_backend_matrix.py`
  runs the dedicated cross-backend Section 8 suite across the Python
  reference backend and the hosted Python REST/gRPC paths
- `./scripts/ci/section8_backend_matrix_gate.sh`
  runs that Section 8 suite and refreshes
  `analysis/compliance/section8_backend_matrix.*`

The helper scripts default their generated downloads, caches, and local
runtime state to `/private/tmp/hla-2010` so the iCloud-synced workspace stays
clean. That includes Pitch state and the default service-report sink used by
the Python RTI backend.

The GitHub workflows are intentionally thin wrappers around these scripts. If a
quality gate changes, update the script first and let CI call through to it.
