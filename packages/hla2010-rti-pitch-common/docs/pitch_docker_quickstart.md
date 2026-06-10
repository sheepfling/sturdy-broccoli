# Pitch Docker Quickstart

This is the easiest supported path for running the certified HLA 1516-2010
Pitch RTI in this repo.

For the full Pitch decision tree, including Docker vs JPype vs Py4J and the
known quirks, see:

- [Pitch Decision Tree](pitch_decision_tree.md)

## One-time setup

Fastest path:

```bash
./tools/pitch preflight
./tools/pitch all
```

That runs:

- install
- smoke
- verify

`./tools/pitch preflight` also persists the default preflight artifact and normalized
status reports under:

- `analysis/preflight_artifacts/`
- `analysis/vendor_runtime_ci_state/` on dedicated vendor CI jobs
- `analysis/vendor_runtime_status/`
- `analysis/vendor_parity_artifacts/`

If you want the staged flow:

```bash
./tools/pitch install
```

What that does:

- discovers the bundled Pitch runtime under `third_party/pitch/PITCH-prti1516e-manual`
- seeds a persistent Pitch `user.home`
- builds the Docker image used for CRC + FedPro

## Start Pitch

```bash
./tools/pitch start
```

That starts one named container:

- container: `hla2010-pitch-crc`
- CRC: `127.0.0.1:8989`
- FedPro: `127.0.0.1:15164`

## Smoke test

```bash
./tools/pitch smoke
```

That dispatches to the strict shared vendor lane for the Pitch smoke slice.

## Full real Pitch matrix

```bash
./tools/pitch verify
```

That dispatches to the strict shared vendor lane for the Pitch verify slice.

## Day-to-day commands

```bash
./tools/pitch status
./tools/pitch logs
./tools/pitch stop
./tools/pitch restart
./tools/pitch doctor
./tools/pitch save-restore
./tools/pitch save-restore-probe
./tools/pitch ddm
./tools/pitch ddm-probe
./tools/pitch all
```

## Zero-thinking vendor smoke

If you just want the standard vendor smoke wrapper, this now works with
repo-local Pitch defaults:

```bash
./tools/pitch smoke
./tools/pitch verify
./tools/pitch all
```

Use `./scripts/ci/vendor_green.sh ...` only when you specifically need the
shared CI wrapper surface.

## Dedicated CI Runner Contract

The supported dedicated runner state for Pitch is explicit and Docker-backed:

- `HLA2010_PITCH_HOME`
- `HLA2010_PITCH_USER_HOME`
- Docker daemon reachable
- required ports available or already owned by the managed container

Required runtime marker:

- `HLA2010_PITCH_HOME/lib/prtifull.jar`

Validate that runner state directly with:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile pitch --json
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile matrix --json
```

Those checks emit:

- `analysis/vendor_runtime_ci_state/pitch/vendor_runtime_ci_state_summary.json`
- `analysis/vendor_runtime_ci_state/pitch/vendor_runtime_ci_state_report.md`

## If it fails

Use:

```bash
./tools/pitch preflight
./tools/pitch doctor
./tools/pitch logs
```

Common causes:

- Docker Desktop is not running
- the Pitch runtime bundle is missing from `third_party/pitch/PITCH-prti1516e-manual`
- another process is already bound to `8989` or `15164`

The implementation shim remains `./scripts/pitch_docker_easy.sh`, but the
supported operator path is `./tools/pitch`.
