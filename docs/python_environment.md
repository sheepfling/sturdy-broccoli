# Python Environment

This is the canonical setup path for this repository.

If you are a person, an agent, or CI automation, start here before running
examples, tests, or backend tools.

This page covers the shared Python bootstrap contract for both editions. For
the current IEEE 1516.1-2025 runtime lane, the main executable backend remains
`hla-backend-python1516-2025`, while `hla-backend-shim` stays only as a
legacy compatibility shim.

## What You Need First

- Python 3.10 or newer
- `bash`
- `git`

Optional later:

- `jpype1` if you want the JPype bridge paths
- `py4j` if you want the Py4J bridge paths
- Docker if you want the Pitch Docker flow
- a local CERTI build or install if you want the CERTI runtime paths

If you need to inspect the local JDK, `javac`, `jar`, or Java shim artifact state,
use `./tools/java`.

## The Shortest Working Path

From the repository root:

```bash
./tools/bootstrap python
source .venv/bin/activate
python examples/target_radar_simulation.py --backend python1516e --steps 5
```

That is the shortest supported path to a working local Python setup.

For the main 2025 lane after bootstrap, continue with:

- [`python_rti_backend.md`](python_rti_backend.md) for the current runtime
  ownership and wrapper boundary
- [`python_rti_reading_map.md`](python_rti_reading_map.md) for the shortest
  edit path through `hla-backend-python1516-2025`
- [`networked_rti_python.md`](networked_rti_python.md) for the bounded hosted
  `python1516_2025-fedpro-grpc` route

If you want to check the machine and workspace before bootstrapping, run:

```bash
./tools/bootstrap doctor
```

That verifies Python, `.venv`, workspace imports, and optional backend
prerequisites without trying to install anything.

## What The Bootstrap Commands Do

There are two normal entrypoints:

```bash
./tools/bootstrap python
HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python
```

They are related, but not identical:

- `./tools/bootstrap python` is the shortest supported bootstrap entrypoint.
  It defaults to the lean `test` extras.
- `HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python` is the direct way to
  request broader Python extras.

Both commands:

- create or refresh the repo-local virtual environment
- install the split workspace packages in editable mode
- add the selected helper dependencies without installing the repo root as a distribution

## Where The Virtual Environment Lives

The repository-managed virtual environment lives at the repo root:

```bash
source .venv/bin/activate
```

Older local worktrees may still have `.venv` as a symlink from an earlier
layout. That is tolerated, but the supported bootstrap contract is the plain
repo-local `.venv` path.

## Which Extras To Install

Pick the smallest thing that matches your work.

### 1. Basic Python development

```bash
./tools/bootstrap python
```

This gives you:

- editable workspace install
- pytest support

### 2. Full local QA flow

```bash
HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python
```

This adds:

- pytest
- Ruff
- Pyright
- the JPype and Py4J bridge helper dependencies needed by the repo-green split-package suite
- the JPype/Py4J/Portico split package set used by repo-level verification

### 3. Java bridge work

JPype:

```bash
HLA2010_BOOTSTRAP_EXTRAS=jpype ./tools/bootstrap python
```

Py4J:

```bash
HLA2010_BOOTSTRAP_EXTRAS=py4j ./tools/bootstrap python
```

Both:

```bash
HLA2010_BOOTSTRAP_EXTRAS=java ./tools/bootstrap python
```

If you need both bridge dependencies and QA tooling, install them after the
bootstrap. The `qa` bootstrap already installs the repo-green bridge package
set; use the manual command only when you want to add the helper dependencies
to an already-bootstrapped environment without reinstalling split packages:

```bash
source .venv/bin/activate
python -m pip install --no-build-isolation ruff pyright jpype1 py4j
```

## Install Order

Use this order unless you have a specific reason not to.

0. Optionally run `./tools/bootstrap doctor`.
1. Bootstrap Python first.
2. Activate `.venv`.
3. Run a pure-Python example or smoke test.
4. Add bridge extras if you need JPype or Py4J.
5. Only then install or build vendor runtimes such as CERTI or Pitch.

That order matters because the vendor flows assume the Python environment and
repo-local wrappers already work.

## First Commands After Bootstrap

After the Python environment is up:

```bash
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python1516e --steps 5
./tools/two-federate --target-radar-steps 3
./tools/python verify
./tools/test
```

If those commands work, the base environment is healthy.

For IEEE 1516.1-2025 specifically:

- `python1516_2025` is the main in-process RTI lane
- `hla-backend-shim` is a legacy compatibility shim over that runtime
- the hosted gRPC path is a bounded route variant, not a separate RTI family

## Hosted Python gRPC Authorization

The hosted Python gRPC route needs one extra capability beyond the direct
in-process Python backend: the current execution surface must be allowed to
open a loopback TCP listener on `127.0.0.1`.

Check that first with:

```bash
./tools/python verify-routes-preflight
```

Supported interpretation:

- `python-grpc: runnable`: hosted Python gRPC may run here
- `python-grpc: blocked`: the current sandbox or runner policy denied loopback
  sockets

The required permission is local TCP `bind`, `listen` / `accept`, and
`connect` on `127.0.0.1` ephemeral ports.

When you are running through Codex or another managed sandbox, repo changes do
not grant that capability. You must either:

- approve unsandboxed execution for the hosted-route commands in that session
- run the commands on a dedicated runner that already permits loopback sockets

Once authorized, use:

```bash
./tools/python verify-main-2025
./tools/python verify-routes
./tools/python verify-routes-2025
python examples/target_radar_simulation.py --backend python1516e-grpc --steps 5
python examples/target_radar_simulation.py --backend python1516_2025 --steps 5
```

Treat `./tools/python verify-main-2025` as the normal main-surface proof lane
for the real 2025 Python RTI. Use `./tools/python verify-routes-2025` only
when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane.

## Vendor Runtime Order

Once the Python path is working:

### CERTI

```bash
./tools/certi-easy preflight
./tools/certi-easy install
./tools/certi-easy verify-best-effort
./tools/certi-easy smoke compare
```

### Pitch

```bash
./tools/pitch preflight
./tools/pitch install
./tools/pitch smoke
./tools/pitch verify
./tools/pitch verify-best-effort
./tools/vendor-green matrix
```

Do not start with CERTI or Pitch before the Python bootstrap succeeds.

Use `./tools/pitch verify-best-effort` when you need the normalized Pitch
preflight/runtime artifacts on a local or sandboxed machine that cannot satisfy
the strict Docker and loopback prerequisites for `./tools/pitch verify`.

For real runtime proof on an unrestricted local terminal or a dedicated CI
runner, use [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md).

## Repo Layout For Setup Purposes

The setup-relevant parts of this repo are:

- `packages/hla-rti1516e/src/hla/rti1516e/`: `hla.rti1516e`, the IEEE 1516.1-2010 API package
- `packages/hla-rti-core/src/hla/rti/`: `hla.rti`, the cross-version discovery and factory package
- `packages/*/src/`: package-owned backend, transport, bridge, FOM, and support implementations
- `examples/`: runnable entrypoints
- `tools/`: human-facing vendor/runtime operator entrypoints
- `scripts/`: bootstrap, CI, and implementation wrappers
- `tests/`: pytest coverage

The bootstrap scripts install the split workspace package set across those
package roots in editable mode.

## If You Are An Agent

Use this sequence:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
```

Do not assume the environment is already active.
Do not start with vendor runtime flows unless the task explicitly requires them.

## Read Next

1. [`first_run.md`](first_run.md)
2. [`two_federate_quickstart.md`](two_federate_quickstart.md)
3. [`install_matrix.md`](install_matrix.md)
