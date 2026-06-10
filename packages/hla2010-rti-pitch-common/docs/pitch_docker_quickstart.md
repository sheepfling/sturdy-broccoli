# Pitch Docker Quickstart

This is the easiest supported path for running the certified HLA 1516-2010
Pitch RTI in this repo.

For the full Pitch decision tree, including Docker vs JPype vs Py4J and the
known quirks, see:

- [Pitch Decision Tree](pitch_decision_tree.md)

## One-time setup

Fastest path:

```bash
./scripts/pitch_docker_easy.sh preflight
./scripts/pitch_docker_easy.sh all
```

That runs:

- install
- smoke
- verify

`./scripts/pitch_docker_easy.sh preflight` also persists the default preflight artifact and normalized
status reports under:

- `analysis/preflight_artifacts/`
- `analysis/vendor_runtime_ci_state/` on dedicated vendor CI jobs
- `analysis/vendor_runtime_status/`
- `analysis/vendor_parity_artifacts/`

If you want the staged flow:

```bash
./scripts/pitch_docker_easy.sh install
```

What that does:

- discovers the bundled Pitch runtime under `third_party/pitch/PITCH-prti1516e-manual`
- seeds a persistent Pitch `user.home`
- builds the Docker image used for CRC + FedPro

## Start Pitch

```bash
./scripts/pitch_docker_easy.sh start
```

That starts one named container:

- container: `hla2010-pitch-crc`
- CRC: `127.0.0.1:8989`
- FedPro: `127.0.0.1:15164`

## Smoke test

```bash
./scripts/pitch_docker_easy.sh smoke
```

That dispatches to the strict shared vendor lane for the Pitch smoke slice.

## Full real Pitch matrix

```bash
./scripts/pitch_docker_easy.sh verify
```

That dispatches to the strict shared vendor lane for the Pitch verify slice.

## Day-to-day commands

```bash
./scripts/pitch_docker_easy.sh status
./scripts/pitch_docker_easy.sh logs
./scripts/pitch_docker_easy.sh stop
./scripts/pitch_docker_easy.sh restart
./scripts/pitch_docker_easy.sh doctor
./scripts/pitch_docker_easy.sh save-restore
./scripts/pitch_docker_easy.sh save-restore-probe
./scripts/pitch_docker_easy.sh ddm
./scripts/pitch_docker_easy.sh ddm-probe
./scripts/pitch_docker_easy.sh all
```

## Zero-thinking vendor smoke

If you just want the standard vendor smoke wrapper, this now works with
repo-local Pitch defaults:

```bash
./scripts/pitch_docker_easy.sh smoke
./scripts/pitch_docker_easy.sh verify
./scripts/pitch_docker_easy.sh all
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
./scripts/pitch_docker_easy.sh preflight
./scripts/pitch_docker_easy.sh doctor
./scripts/pitch_docker_easy.sh logs
```

Common causes:

- Docker Desktop is not running
- the Pitch runtime bundle is missing from `third_party/pitch/PITCH-prti1516e-manual`
- another process is already bound to `8989` or `15164`

If you prefer the explicit script path, `./scripts/pitch_docker_easy.sh` is a thin alias for
`./scripts/pitch_docker_easy.sh`.
