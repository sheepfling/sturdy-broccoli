# hla2010-python

This archive is a clean seed for the Python HLA 1516.1-2010 workstream. It contains the current Python package source, Java bridge adapter source, pure-Python RTI source, vendored CERTI source, examples, tests, helper scripts, FOM/MIM XML resources, and the user-supplied IEEE reference/source documents.

It intentionally does **not** include generated verification packets, generated analysis matrices, historical scaffold ZIPs, prior run summaries, pytest caches, built Java `.jar` files, or other transient assets. Those should be regenerated from source when needed.

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

Additional repo-local material promoted from `INBOX`:

- `docs/plans/` 2010 workspace planning and foundation notes
- `docs/backend_capability_matrix.md` backend support status across Python, Java shims, CERTI, and Pitch
- `docs/backend_conformance_matrix.md` clause-level backend parity and conformance status across Python, CERTI, and future Pitch
- `docs/certi_spec_traceability.md` clause-level real CERTI parity and evidence notes for sync and ownership services
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

To bootstrap everything needed for local CERTI work as well:

```bash
./scripts/bootstrap_all.sh
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
./scripts/ci/test.sh
./scripts/ci/seed_suite.sh
./scripts/ci/vendor_runtime_smoke.sh certi
./scripts/ci/vendor_runtime_smoke.sh pitch
```

By default `bootstrap_python.sh` installs the `qa` extras. Override that with
`HLA2010_BOOTSTRAP_EXTRAS=...` if you want a narrower environment.

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
./scripts/rebuild_certi.sh
./scripts/run_certi_local.sh rtig --help
python3 -c "from hla2010.rti import create_rti_ambassador; rti=create_rti_ambassador('pitch-jpype'); print(rti.getHLAversion()); rti.close()"
python3 -c "from hla2010.rti import create_rti_ambassador; rti=create_rti_ambassador('certi'); print(rti.getHLAversion()); rti.close()"
```

The `pitch-jpype` path currently discovers the extracted runtime from:

- `HLA2010_PITCH_HOME`, if set
- `third_party/pitch/PITCH-prti1516e-manual`, if present

For Pitch specifically, the runtime layer now checks the local CRC license state
through the bundled `LicenseActivator` class before attempting the real smoke
path. If no local licenses are present, the backend fails fast with a clear
message instead of timing out on the CRC socket.

The `CERTI` launcher currently discovers the install prefix from:

- `HLA2010_CERTI_PREFIX`, if set
- `CERTI-install`, if present in this repository
- `./scripts/rebuild_certi.sh` will populate the local `CERTI-build/` and
  `CERTI-install/` trees from `CERTI/`

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
HLA2010_ENABLE_REAL_RTI_SMOKE=1 python -m pytest -q tests/test_real_vendor_runtime_smoke.py
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
