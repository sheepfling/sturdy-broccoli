# Pitch Decision Tree

This is the single-page guide for Pitch in this repo.

Use it when you need to decide:

- how to install Pitch
- how to run it
- which interface to use
- whether to use `jpype`, `py4j`, or Docker
- what the known compliance quirks are

## Default Recommendation

If you just want to run the certified Pitch path in the least painful way, use:

```bash
./bootstrap pitch
./pitch all
```

That is the junior-friendly path.

It does:

- Python bootstrap
- Pitch Docker image setup
- Pitch smoke
- Pitch verify

## Which Pitch Path Should I Use?

### Use Docker if you want the stable vendor path

Choose the Docker-backed Pitch flow when you want:

- the simplest install/setup path
- no host Java dependency
- the cleanest operator experience
- the current stable vendor evidence path

Commands:

```bash
./pitch install
./pitch start
./pitch smoke
./pitch verify
```

Or just:

```bash
./pitch all
```

### Use `jpype` or `py4j` if you are debugging bridge behavior

Choose `pitch-jpype` or `pitch-py4j` when you want to inspect how the Python
adapter talks to the Java bridge.

These are for diagnostics and comparison, not the default operator path.

Use them when you need to answer:

- does the Java bridge itself behave differently?
- is the behavior changing between JPype and Py4J?
- is the runtime issue in the bridge or in Pitch itself?

## Install / Build / Run / Connect

### Install

`./bootstrap pitch`

What it does:

- installs the editable Python package
- builds the Pitch Docker image
- does not require host Java for the Docker path

### Build

`./pitch install`

This:

- discovers the bundled Pitch runtime under `third_party/pitch/PITCH-prti1516e-manual`
- seeds a persistent Pitch `user.home`
- builds the Docker image used for CRC + FedPro

### Run

`./pitch start`

This launches the vendor runtime container and waits for:

- CRC on `127.0.0.1:8989`
- FedPro on `127.0.0.1:15164`

### Connect

For the Docker-backed path, the Python tests connect to the local container
through those ports.

For the local launcher path, the Pitch runtime uses the extracted runtime under:

- `HLA2010_PITCH_HOME`
- or `third_party/pitch/PITCH-prti1516e-manual`

## Interface Choices

### Docker operator interface

Use this for most work:

```bash
./pitch all
./pitch smoke
./pitch verify
./pitch doctor
./pitch logs
./pitch stop
```

`./pitch doctor` follows the same shape as `./pitch preflight`, but adds the
resolved runtime paths and container state so the operator can see what the
next step is before doing anything else.

### Java bridge interface

Use this only for bridge debugging:

- `pitch-jpype`
- `pitch-py4j`

These are not the default recommended path for a junior.

## Transport / Protocol Surface

Pitch in this repo is not exposed as a separate remote transport family in the
same way as the Python hosted `grpc` / `rest` routes.

For Pitch, the important transport boundaries are:

- local Docker ports for CRC and FedPro
- local Java bridge invocation through JPype or Py4J

Use the route inventory if you need the full matrix:

- [`backend_route_inventory.md`](backend_route_inventory.md)

## Known Quirks

### macOS local runtime

The non-Docker local launcher can still involve the vendor acceptance flow and
host GUI behavior on macOS.

The Docker-backed `./pitch` path is the easiest way to avoid that pain.

### Linux Docker host mapping

The Docker launcher adds `host.docker.internal` on Linux so the same `./pitch`
flow works on macOS and Linux.

### Negotiated ownership

Pitch negotiated ownership is currently bridge-divergent:

- `pitch-jpype` and `pitch-py4j` do not produce identical callback histories
- negotiated ownership is **not** promoted as a clean parity row
- treat the vendor bug note as the source of truth:
  - [`pitch_negotiated_ownership_vendor_bug_2026-06-07.md`](evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md)

### What is currently promoted

Pitch is currently promoted for:

- exchange/time
- synchronization
- basic ownership

Pitch is currently not promoted for:

- negotiated ownership
- save/restore
- DDM
- target/radar

## What To Use When Things Break

### First-line checks

```bash
./pitch doctor
./pitch logs
```

For scripts or CI, `./pitch preflight --json` emits machine-readable status
with `environment`, `result`, and per-check records.

For file output and inspection examples, see
[Preflight Artifacts](preflight_artifacts.md).

### Common failure causes

- Docker Desktop is not running
- the Pitch runtime bundle is missing from `third_party/pitch/PITCH-prti1516e-manual`
- another process is already bound to `8989` or `15164`
- the local host session cannot talk to Docker

### If you need the raw bridge diagnostics

Use the vendor smoke wrapper:

```bash
./scripts/ci/vendor_runtime_smoke.sh pitch
```

Or inspect the negotiated ownership diagnostics:

- [`analysis/pitch_negotiated_ownership_2026-06-07/`](../analysis/pitch_negotiated_ownership_2026-06-07/)

## Short Answer

If you are a junior or just want Pitch working, use:

```bash
./bootstrap pitch
./pitch all
```

If you are debugging Java bridge behavior, use `pitch-jpype` and `pitch-py4j`.
