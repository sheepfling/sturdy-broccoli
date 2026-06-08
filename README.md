# hla2010-python

This archive is a clean seed for the Python HLA 1516.1-2010 workstream. It contains the current Python package source, Java bridge adapter source, pure-Python RTI source, vendored CERTI source, examples, tests, helper scripts, FOM/MIM XML resources, and the user-supplied IEEE reference/source documents.

It intentionally does **not** include generated verification packets, generated analysis matrices, generated source-code artifacts, historical scaffold ZIPs, prior run summaries, pytest caches, built Java `.jar` files, or other transient assets. Those should be regenerated from source when needed.

## Layout

```text
hla2010/              Python package source
examples/             runnable examples, including Target/Radar
tests/                pytest tests and smoke coverage
tools/                spec-analysis and download helper scripts
java_shims/           Java shim source used for bridge validation; no built jar included
CERTI/                vendored CERTI source tree for the 2010 runtime path
CERTI-build/          symlinked local CERTI build tree created by ./scripts/rebuild_certi.sh
CERTI-install/        symlinked local CERTI install tree created by ./scripts/rebuild_certi.sh
specs/ieee-1516-2010/ user-supplied IEEE PDFs and source ZIPs
docs/                 clean project notes for the repo seed
```

For the package-level backend/API organization, see
[`docs/package_layout.md`](docs/package_layout.md).

For the seeded requirement sources and ID registry, start with
[`requirements/README.md`](requirements/README.md).

For the canonical documentation hierarchy, start with
[`docs/README.md`](docs/README.md) and
[`docs/documentation_hierarchy.md`](docs/documentation_hierarchy.md).

For the script hierarchy and operator entrypoints, see
[`scripts/README.md`](scripts/README.md).

For the full documented lifecycle sequence, see
[`docs/verification/run_sequence.md`](docs/verification/run_sequence.md).

The boundary is intentional:

- `hla2010/` is the installable package.
- `examples/` contains runnable entrypoints and example-only assets.
- shared scenario code belongs in `hla2010/scenarios/`, not in `examples/`.

The documentation follows the same rule:

- `README.md` is the operator entry point.
- `docs/README.md` is the document index.
- `docs/documentation_hierarchy.md` explains the parallel story used by the
  rest of `docs/`.

If you want the shortest install path, use the new profile dispatcher:

```bash
./bootstrap python
./bootstrap certi
./bootstrap pitch
./bootstrap all
```

Those profiles are intentionally lighter than the vendor-specific compare
wrappers:

- `python` installs the editable package plus lean test deps and does not
  require Java.
- `certi` installs Python and builds the repo-local CERTI runtime.
- `pitch` installs Python and builds the Pitch Docker image.
- `all` installs Python, CERTI, and Pitch.

If you want the broader lint/typecheck extras instead of the lean test extras,
set `HLA2010_BOOTSTRAP_EXTRAS=qa` before running `./bootstrap ...`.

Additional repo-local material promoted from `INBOX`:

- `docs/plans/` 2010 workspace planning and foundation notes
- `docs/backend_capability_matrix.md` backend support status across Python, Java shims, CERTI, and Pitch
- `docs/backend_conformance_matrix.md` clause-level backend parity and conformance status across Python, CERTI, and future Pitch
- `docs/certi_spec_traceability.md` clause-level real CERTI parity and evidence notes for sync and ownership services
- `docs/certi_runtime_limitations.md` known CERTI runtime shortfalls and patched-vs-upstream baseline policy
- `docs/certi_negotiated_ownership_findings.md` source-level investigation notes for CERTI negotiated ownership limitations
- `docs/evidence/` unpacked verification evidence packets
- `docs/reference/hla-2010-specs.zip` original PDF-only reference drop
- `third_party/pitch/` Pitch pRTI / Visual OMT installer bundle
- `archives/` retained source-drop and verification ZIP archives
- `scripts/bootstrap_python.sh` local Python environment bootstrap
- `scripts/rebuild_certi.sh` local CERTI configure/build/install
- `scripts/bootstrap_all.sh` combined Python and CERTI bootstrap
- `scripts/setup_local_state.sh` one-shot setup for symlinked local caches and
  build trees
- `scripts/local_state.sh` shared helper that keeps generated state in
  `/private/tmp/hla-2010` and replaces repo-local build/cache directories with
  symlinks

## Quick start

```bash
./scripts/bootstrap_python.sh
./scripts/ci/seed_suite.sh
python examples/target_radar_simulation.py --backend python --steps 5
```

To bootstrap everything needed for local CERTI work as well, use the easy path
first:

```bash
./certi-easy preflight
./certi-easy install
./certi-easy doctor
./certi-easy smoke compare
```

That is the primary CERTI operator contract in this repo:

- patched local CERTI built and installed
- pristine upstream CERTI cloned, built, and installed
- one command to compare the two runtimes on the promoted real smoke slices

Lower-level CERTI scripts such as `scripts/rebuild_certi.sh`,
`scripts/rebuild_certi_upstream.sh`, and
`scripts/ci/vendor_runtime_smoke.sh` remain available for targeted debugging
and matrix work, but they are secondary operator entrypoints.

For the one-page CERTI operator runbook, see
[`docs/certi_section8_runbook.md`](docs/certi_section8_runbook.md).

For the preflight JSON options-file workflow and inspection examples, see
[`docs/preflight_artifacts.md`](docs/preflight_artifacts.md). The shortest
copy-paste path is:

```bash
mkdir -p analysis/preflight_artifacts

./certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
python3 -m json.tool analysis/preflight_artifacts/certi-preflight.json

./pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
python3 -m json.tool analysis/preflight_artifacts/pitch-preflight.json
```

Optional Java bridge packages can be installed with:

```bash
pip install -e '.[jpype]'
pip install -e '.[py4j]'
```

## Local quality gates

The repo CI is intentionally built from thin shell wrappers so local reruns and
GitHub Actions use the same entrypoints.

```bash
./scripts/ci/install_python.sh
./scripts/ci/lint.sh
./scripts/ci/lint_backlog.sh
./scripts/ci/lint_strict.sh
./scripts/ci/test.sh
./scripts/ci/seed_suite.sh
./scripts/ci/vendor_runtime_smoke.sh certi
./scripts/ci/vendor_runtime_smoke.sh pitch
./scripts/ci/vendor_edge_matrix.sh
./scripts/run_two_federate_suite.py
./scripts/generate_compliance_artifacts.py
```

By default `bootstrap_python.sh` installs the `qa` extras. Override that with
`HLA2010_BOOTSTRAP_EXTRAS=...` if you want a narrower environment.

`lint.sh` is the required gate. `lint_backlog.sh` reports the broader Ruff
cleanup backlog so it can be burned down incrementally without blocking every
change. `lint_strict.sh` is the opt-in next-step gate; it adds `E501` while
temporarily excluding the largest legacy/generated files that still need a
separate cleanup pass.

`generate_compliance_artifacts.py` emits the current conformance packet under
`analysis/compliance/`, including:

- service conformance JSON/CSV
- requirements ledger JSON/CSV
- whole-spec requirements matrix JSON/CSV
- verification assets JSON
- verification traceability CSV
- section-by-section compliance summary
- public class `1:1` vs adapted inventory
- rows that still lack exact requirement-level executable evidence

For a junior operator, start with these two files after regeneration:

- `analysis/compliance/verification_assets.json`: named verification slices and their evidence
- `analysis/compliance/verification_traceability.csv`: flat section-to-asset map for clause review
- `analysis/compliance/supported_subset_policy.md`: broad-spec versus supported-subset policy split for defended partials
- `analysis/compliance/defended_partials_index.md`: review-facing index of broad partial rows and the narrower supported-subset passes that defend them

Then use:

- `analysis/compliance/requirements_matrix_2010.csv`: one flat matrix spanning section areas, service requirements, and cross-cutting verification slices
- `analysis/compliance/extracted_requirements_clause5_6.md`: Clause 5/6 packet split into broad-spec and supported-subset rows
- `analysis/compliance/extracted_requirements_clause7_9.md`: Clause 7/9 packet split the same way, ready as those extracted rows are promoted

For the human-readable policy on why some broad rows intentionally remain
partial while narrower subset rows pass, see
[`docs/supported_subset_policy.md`](docs/supported_subset_policy.md).

If you want a readable FOM/MIM visualization instead of raw XML, use:

```bash
python3 scripts/generate_fom_overview.py TargetRadarFOMmodule.xml --html
```

That emits a merged tree-and-matrix overview under `analysis/fom_overview/`.

## Full Verification Sequence

When you want the single easy-run path that exercises install, compilation,
lint/type annotations, unit tests, integration smoke, integration tests,
compliance matrices, and the documented backend evidence checks, use:

```bash
./scripts/ci/full_sequence.sh
```

The runbook at [`docs/verification/run_sequence.md`](docs/verification/run_sequence.md)
describes the exact order and what each stage means.

The sequence is designed to be practical for local reruns:

- the Python, CERTI, and Pitch smoke gates are included where available
- known partial vendor areas are treated as skips rather than hidden failures
- the target/radar matrix uses the core three-backend subset in the default
  sequence so the documented path stays reasonably quick and reproducible

## Two-federate evidence

The repo now includes one streamlined composite two-federate suite that emits
structured artifacts and a visual summary:

```bash
./scripts/run_two_federate_suite.py
```

Default outputs land under `analysis/two_federate_suite/`:

- `two_federate_suite_summary.json`
- `two_federate_track_reports.csv`
- `two_federate_callbacks.csv`
- `two_federate_suite_report.md`
- `two_federate_suite_summary.svg`
- `two_federate_suite_timeline.svg`

That suite now emits a python primary profile plus optional CERTI and Pitch
profiles when those runtimes are available. The packet includes a profile
matrix and a callback-order timeline for the python profile.

The python profile exercises, end to end:

- object discovery and attribute reflection
- interaction delivery
- timestamped/time-managed exchange
- federation synchronization
- unconditional ownership transfer
- negotiated ownership cancellation and reacquisition
- save/restore
- DDM region filtering
- a realistic target/radar object plus track-report scenario

For a target/radar-only backend diagnostic packet, use:

```bash
./scripts/run_target_radar_backend_matrix.py
```

That runner writes JSON, CSV, Markdown, and SVG artifacts under
`analysis/target_radar_backend_matrix/` and marks each backend as passed,
skipped, or failed with an explicit reason.

For a proof packet with the backend matrix plus the detailed simulation trace
and visuals, use:

```bash
./scripts/run_target_radar_proof.py
```

That runner writes JSON, CSV, Markdown, and SVG artifacts under
`analysis/target_radar_proof/`, including the truth-target timeline, RCS query
events, track reports, and a trajectory plot. It also writes PNG plots for the
backend matrix, event timeline, truth-vs-track trajectory, and the RCS exchange
between the radar and target. The CI
`target-radar-proof` job uploads that whole directory as a downloadable GitHub
Actions artifact. For the simplest rerun path, use:

```bash
./scripts/ci/target_radar_proof.sh
```

For the highest-value vendor edge slice, which reruns CERTI compare plus the
Pitch matrix and refreshes the compliance packet, use:

```bash
./scripts/ci/vendor_edge_matrix.sh
```

You can also run the focused subprofiles directly:

```bash
./scripts/ci/vendor_edge_matrix.sh time-query
./scripts/ci/vendor_edge_matrix.sh negotiated-ownership
```

## Local Git remote

To attach a local bare remote for offline pushes, use:

```bash
./scripts/setup_local_git_remote.sh
git remote -v
```

The default remote name is `local`, and the bare repository is created under
the repo-managed local-state root in `/private/tmp/hla-2010/git-remotes/`.

## Local RTI wiring

The repo now includes initial runtime wiring for two real RTI targets:

- `Pitch pRTI`
  exposed through the existing Java adapter layer as `pitch-jpype` and
  `pitch-py4j` backend kinds
- `CERTI`
  exposed as a native smoke backend kind `certi` plus the local launcher
  `scripts/run_certi_local.sh`

The repo also includes typed `rest` and `grpc` transport surfaces. Those are
currently exercised as transport choices under the CERTI adapter path, not as
separate RTI backend families. The `grpc` path now also has a transport-hosted
pure-Python RTI proving server for end-to-end exchange coverage, and the `rest`
path now has the same style of transport-hosted pure-Python RTI proving path.

The current remote callback contract is explicit as well: the `rest` and `grpc`
paths use
unary request/response calls plus callback polling through the normal
`evokeCallback` / `evokeMultipleCallbacks` services. Streaming callbacks are a
future option, not the current wire contract.

Practical local commands:

```bash
./certi-easy preflight
./certi-easy install
./certi-easy doctor
./certi-easy smoke patched
./certi-easy smoke upstream
./certi-easy smoke compare
./certi-easy run patched rtig -v 0
./certi-easy run upstream rtig -v 0
python3 -c "from hla2010.rti import create_rti_ambassador; rti=create_rti_ambassador('pitch-jpype'); print(rti.getHLAversion()); rti.close()"
python3 -c "from hla2010.rti import create_rti_ambassador; rti=create_rti_ambassador('certi'); print(rti.getHLAversion()); rti.close()"
```

Smoke-scope note:

- `./certi-easy smoke compare` is intentionally limited to the currently stable
  upstream-vs-patched CERTI slices.
- The patched negotiated-ownership end-to-end baseline is still tracked as a
  targeted matrix gap, not part of the smoke contract.

If you need the deeper time-management and compliance gates:

```bash
python3 -m pytest -q tests/time/test_section8_backend_matrix.py
./scripts/ci/section8_backend_matrix_gate.sh
```

The CERTI preflight reports either `real CERTI runnable` or `real CERTI will skip`
and surfaces the exact blocked prerequisite, including loopback socket-bind
restrictions that prevent `rtig` smoke tests from starting in some sandboxed
sessions.

For the dedicated cross-backend Section 8 time-management suite and the real
CERTI execution procedure, see
[`docs/certi_section8_runbook.md`](docs/certi_section8_runbook.md).

The `pitch-jpype` path currently discovers the extracted runtime from:

- `HLA2010_PITCH_HOME`, if set
- `third_party/pitch/PITCH-prti1516e-manual`, if present

The simplest Docker-backed Pitch flow is now:

```bash
./pitch preflight
./pitch all
```

For the one-page guide that explains Docker vs JPype vs Py4J, see:

- [`docs/pitch_decision_tree.md`](docs/pitch_decision_tree.md)

For JSON preflight artifacts and how to inspect them, see:

- [`docs/preflight_artifacts.md`](docs/preflight_artifacts.md)

If you want the explicit staged flow:

```bash
./pitch preflight
./pitch install
./pitch start
./pitch smoke
```

For the full real Pitch matrix:

```bash
./pitch verify
```

Useful operator commands:

```bash
./pitch status
./pitch logs
./pitch stop
./pitch doctor
```

That wrapper handles:

- runtime discovery from `third_party/pitch/PITCH-prti1516e-manual`
- one-time seeding of persistent Pitch `user.home`
- Docker image build
- container lifecycle
- waiting for CRC `8989` and FedPro `15164`
- the real Pitch smoke and matrix commands
- one-command install + smoke + verify through `./pitch all`

The repo-root `./pitch` alias is just a thin wrapper over
`./scripts/pitch_docker_easy.sh`.

If you want the lower-level pieces directly, to avoid re-accepting the
free-runtime dialog on every restart, seed and reuse a persistent Pitch
`user.home`:

```bash
./scripts/setup_pitch_state.sh
./scripts/run_pitch_local.sh
```

That state is kept under `/private/tmp/hla-2010/pitch-user-home` by default, or
under `HLA2010_PITCH_USER_HOME` if you set it explicitly. The runtime helper
now seeds that home once from the vendor bundle and then preserves the accepted
state instead of re-merging the default bundle state on each launch.

For Pitch specifically, the runtime layer now checks the local CRC license state
through the bundled `LicenseActivator` class before attempting the real smoke
path. If no local licenses are present, the backend fails fast with a clear
message instead of timing out on the CRC socket.

The Docker-backed vendor smoke path is now also simpler:

```bash
./scripts/ci/vendor_runtime_smoke.sh pitch
```

If the repo-local Pitch bundle is present, that wrapper now fills in the obvious
Pitch defaults automatically instead of requiring manual `HLA2010_PITCH_HOME`
and `HLA2010_PITCH_USER_HOME` exports first.

The `CERTI` launcher currently discovers the install prefix from:

- `HLA2010_CERTI_PREFIX`, if set
- `CERTI-install`, if present in this repository
- `./scripts/rebuild_certi.sh` will populate the local `CERTI-build/` and
  `CERTI-install/` trees from `CERTI/`

For conformance attribution, use named CERTI baselines:

- `certi-upstream` is a pristine/original CERTI install selected by
  `HLA2010_CERTI_UPSTREAM_PREFIX` or `HLA2010_CERTI_ORIGINAL_PREFIX`
- `certi-patched` is the repo-local vendored/patched CERTI build, or an
  explicit patched install selected by `HLA2010_CERTI_PATCHED_PREFIX`

The upstream selector intentionally does not fall back to the repo-local
`CERTI-build/` overlay. That keeps original-vendor evidence separate from our
modified CERTI evidence.

Runnable CERTI routes:

```bash
./scripts/rebuild_certi.sh
./scripts/rebuild_certi_upstream.sh
./scripts/ci/vendor_runtime_smoke.sh certi-patched
./scripts/ci/vendor_runtime_smoke.sh certi-upstream
./scripts/ci/vendor_runtime_smoke.sh certi-compare
```

Operational meaning:

- `certi-patched` runs the repo-local vendored CERTI build as the active vendor
  path
- `certi-upstream` runs the pristine upstream baseline only
- `certi-compare` runs both the promoted time-query / `flushQueueRequest`
  baseline slice, the negotiated-ownership baseline slice, and the
  release-request `deny` / `confirm` / `ifwanted` branch slice against both
  baselines so upstream CERTI failures and local CERTI changes stay attributable

Generated local state is symlinked out of the repository by default so it is
kept under `/private/tmp/hla-2010` instead of the cloud-synced workspace. That
includes `.venv`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `build/`,
`analysis/`, `verification/`, `htmlcov/`, `dist/`, `downloads/`,
`CERTI-build/`, `CERTI-install/`, the Pitch local home/cache tree, and the
default service-report sink under `service_reports/`.

## Bootstrap and rebuild

The recommended setup path is:

```bash
./scripts/bootstrap_python.sh
./scripts/rebuild_certi.sh
```

or, for both in sequence:

```bash
./scripts/bootstrap_all.sh
```

## Real runtime smoke

The explicit vendor interoperability smoke tests are opt-in:

```bash
HLA2010_ENABLE_REAL_RTI_SMOKE=1 python -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py
```

Those tests keep the Python federate surface backend-neutral. They only use
`create_rti_ambassador(...)`, `connect_create_join(...)`, and the normal HLA
lifecycle calls; vendor specifics stay inside the backend adapters.

`pitch-jpype` exercises a real Java RTI through JPype. `certi` exercises a real
CERTI RTI through a small native helper linked against CERTI's IEEE 1516.1-2010
C++ library.

## Current implementation focus

The package includes:

- a source-derived HLA-style Python `RTIambassador` and `FederateAmbassador` API surface;
- backend-neutral RTI adapters;
- a pure-Python in-memory RTI for local federations;
- JPype and Py4J Java RTI adapters, including a real Pitch pRTI discovery path;
- a typed transport seam for CERTI-facing subprocess, REST, and gRPC transport choices;
- FOM/MIM loading and table-driven MOM catalog support;
- logical-time and timestamp-order support helpers;
- service-reporting, synchronization, save/restore, DDM, and Target/Radar scenario code.

This is still an **unofficial development/reference RTI**, not a certified production RTI.

## Intake status

The 2026-06-05 `INBOX` promotion inventory is recorded in
`docs/inbox_inventory_2026-06-05.md`.
