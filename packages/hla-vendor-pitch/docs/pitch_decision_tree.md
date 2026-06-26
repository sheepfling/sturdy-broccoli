# Pitch Decision Tree

This is the single-page guide for Pitch in this repo.

If you need the canonical new-machine Docker-backed setup walkthrough, start
with [`../../../docs/pitch_docker_first_run.md`](../../../docs/pitch_docker_first_run.md).

Use it when you need to decide:

- how to install Pitch
- how to run it
- which interface to use
- whether to use `jpype`, `py4j`, or Docker
- what the known compliance quirks are

## Default Recommendation

If you just want to run the certified Pitch path in the least painful way, use:

```bash
./tools/bootstrap pitch
./tools/pitch all
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
./tools/pitch install
./tools/pitch start
./tools/pitch smoke
./tools/pitch verify
```

Or just:

```bash
./tools/pitch all
```

### Use `jpype` or `py4j` if you are debugging bridge behavior

Choose `pitch-jpype` or `pitch-py4j` when you want to inspect how the Python
adapter talks to the Java bridge.

These are for diagnostics and comparison, not the default operator path.

Use them when you need to answer:

- does the Java bridge itself behave differently?
- is the behavior changing between JPype and Py4J?
- is the runtime issue in the bridge or in Pitch itself?

Pitch also ships a vendor-specific Java `202X` surface in the bundled jars.
That surface is currently discoverable and auditable, but it is not yet wired
as a promoted backend lane because the bridge stack is still 2010-shaped.
Use the evidence notes when you need that distinction:

- [`pitch_behavior_matrix.md`](pitch_behavior_matrix.md)
- [`pitch_vs_python_baseline.md`](pitch_vs_python_baseline.md)
- [`evidence/pitch_202x_probe_2026-06-23.md`](evidence/pitch_202x_probe_2026-06-23.md)
- [`evidence/pitch_202x_surface_audit_2026-06-23.md`](evidence/pitch_202x_surface_audit_2026-06-23.md)
- [`evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md`](evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md)
- [`evidence/pitch_fom_smoke_failures_2026-06-24.md`](evidence/pitch_fom_smoke_failures_2026-06-24.md)
- [`evidence/pitch_fom_smoke_comparison_2026-06-24.md`](evidence/pitch_fom_smoke_comparison_2026-06-24.md)
- [`evidence/pitch_time_window_candidate_review_2026-06-24.md`](evidence/pitch_time_window_candidate_review_2026-06-24.md)

## Install / Build / Run / Connect

### Install

`./tools/bootstrap pitch`

What it does:

- installs the editable Python package
- builds the Pitch Docker image
- does not require host Java for the Docker path

### Build

`./tools/pitch install`

This:

- discovers the bundled Pitch runtime under `third_party/pitch/PITCH-prti1516e-manual`
- seeds a persistent Pitch `user.home`
- builds the Docker image used for CRC + FedPro

### Run

`./tools/pitch start`

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
./tools/pitch all
./tools/pitch smoke
./tools/pitch verify
./tools/pitch 202x-certify
./tools/pitch doctor
./tools/pitch fom-smoke
./tools/pitch fom-smoke-compare
./tools/pitch logs
./tools/pitch stop
```

`./tools/pitch doctor` follows the same shape as `./tools/pitch preflight`, but adds the
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

- [`backend_route_inventory.md`](../../../docs/backend_route_inventory.md)

## Known Quirks

### macOS local runtime

The non-Docker local launcher can still involve the vendor acceptance flow and
host GUI behavior on macOS.

The Docker-backed `./tools/pitch` path is the easiest way to avoid that pain.

### Linux Docker host mapping

The Docker launcher adds `host.docker.internal` on Linux so the same `./tools/pitch`
flow works on macOS and Linux.

### Negotiated ownership

Pitch negotiated ownership is currently bridge-divergent:

- `pitch-jpype` and `pitch-py4j` do not produce identical callback histories
- negotiated ownership is **not** promoted as a clean parity row
- treat the vendor bug note as the source of truth:
  - [`pitch_negotiated_ownership_vendor_bug_2026-06-07.md`](evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md)

### Example FOM smoke

The current Docker-backed `./tools/pitch fom-smoke` lane is explicit vendor
evidence for which example FOM families currently load and resolve.

Current real-runtime result:

- green on both bridges:
  - `repo-cross-target-radar`
  - `link16-rpr2-integrated`
  - `rpr3-merged-informative-1516-2010`
- failed on both bridges:
  - `repo-2010-demo`
  - `space-fom-core`

Use the checked-in evidence note for exact failure strings and the operator
explanation:

- [`pitch_fom_smoke_failures_2026-06-24.md`](evidence/pitch_fom_smoke_failures_2026-06-24.md)
- [`pitch_202x_adapter_fom_smoke_2026-06-24.md`](evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md)

If you want the side-by-side packet that compares those two lanes directly, use:

```bash
./tools/pitch fom-smoke-compare
```

That emits:

- `artifacts/pitch_fom_smoke_compare/pitch_fom_smoke_compare_summary.json`
- `artifacts/pitch_fom_smoke_compare/pitch_fom_smoke_compare_report.md`

### SISO micro delivery alignment

The bounded SISO micro comparison lane now passes on:

- real Pitch 2010:
  - `pitch-jpype`
  - `pitch-py4j`
- bounded adapter routes:
  - `pitch-202x-jpype`
  - `pitch-202x-py4j`

Important behavior note:

- the earlier real Pitch 2010 failure was not a `2025` adapter defect and not
  an XML/FOM decode issue
- it was an executable-lane callback wait issue
- the passing result came from using the same explicit callback wait discipline
  as the already-passing real Pitch exchange smoke

Use:

```bash
./tools/pitch 202x-micro-certify
```

See:

- [`pitch_behavior_matrix.md`](pitch_behavior_matrix.md)
- [`pitch_vs_python_baseline.md`](pitch_vs_python_baseline.md)
- [`evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md`](evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md)

### Time-window probe status

The two current Pitch-safe time-window probes have repeated-run stability
evidence and are now documented as `candidate-review`.

That means:

- stable enough to cite as bounded vendor-credence evidence
- not yet broad clause-level parity proof

Use the checked-in note:

- [`pitch_time_window_candidate_review_2026-06-24.md`](evidence/pitch_time_window_candidate_review_2026-06-24.md)

### What is currently promoted

Pitch is currently promoted for:

- exchange/time
- synchronization
- basic ownership

Pitch is currently not promoted for:

- negotiated ownership
- save/restore
- lost-federate handling
- DDM
- target/radar

If you want the narrowest explicit 202X vendor-credence packet for the bundled
Pitch jars, use:

```bash
./tools/pitch 202x-certify
```

That route:

- re-runs Pitch preflight
- refreshes the checked-in `202X` surface audit
- runs the promoted lifecycle/exchange smoke
- runs the two current trial-safe Target/Radar probes:
  - `time-window-probe`
  - `time-window-restore-state-probe`
- emits a combined certification packet under:
  - `analysis/pitch_202x_certification/`

Treat that packet as:

- evidence that the bundled Pitch `202X` surface is real
- evidence for the smallest real-runtime trial-safe example/FOM scenarios
- not an IEEE `2025` conformance claim

If you want explicit adapter-backed FOM behavior evidence for the checked-in
`pitch-202x-*` routes, use:

```bash
./tools/pitch fom-smoke --kind pitch-202x-jpype --kind pitch-202x-py4j
```

Treat that route as:

- proof that the explicit `pitch-202x-*` adapters can exercise the repo FOM
  smoke packets
- not proof of native Pitch `202X` vendor-runtime behavior

The current checked-in adapter evidence is:

- [`pitch_202x_adapter_fom_smoke_2026-06-24.md`](evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md)
- [`pitch_siso_micro_delivery_alignment_2026-06-24.md`](evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md)

If you want the current explicit operator result for the negotiated-ownership
gap, use:

```bash
./tools/pitch negotiated
```

That route preflights first, then emits a machine-readable known-gap profile
instead of pretending the slice is silently missing.

If you want the current explicit operator result for the save/restore gap, use:

```bash
./tools/pitch save-restore
```

That route preflights first, then emits a machine-readable known-gap profile
instead of pretending the slice is silently missing.

If you want the current narrow executable save/restore probe instead, use:

```bash
./tools/pitch save-restore-probe
```

Treat that as a deeper runtime probe, not as a promoted stable parity slice yet.

For the current explicit operator result on the lost-federate gap, use:

```bash
./tools/pitch lost-federate
```

If you want the current narrow executable lost-federate probe instead, use:

```bash
./tools/pitch lost-federate-probe
```

Treat that as a backend-split runtime probe: `pitch-py4j` has a fault-injection
path, while `pitch-jpype` still lacks an isolated per-federate loss trigger.
If you need to experiment with vendor-specific loss detection or session-resume
keys, set `HLA2010_PITCH_LRC_EXTRA_SETTINGS` or
`HLA2010_PITCH_FEDPRO_EXTRA_SETTINGS` to newline- or semicolon-separated
`key=value` entries before launching the probe.

For the current explicit operator result on the DDM gap, use:

```bash
./tools/pitch ddm
```

If you want the current narrow executable DDM probe instead, use:

```bash
./tools/pitch ddm-probe
```

Treat that as a deeper runtime probe, not as a promoted stable parity slice yet.

For the current narrow executable negotiated-ownership probe, use:

```bash
./tools/pitch negotiated-probe
```

Treat that as a deeper runtime probe for the currently bridge-divergent
ownership continuation paths, not as a promoted stable parity slice.

Use "Pitch parity" only for the promoted overlap rows we currently defend.
Negotiated ownership remains bridge-divergent and should not be described as
blanket parity.

## What To Use When Things Break

### First-line checks

```bash
./tools/pitch doctor
./tools/pitch logs
```

For scripts or CI, `./tools/pitch preflight --json` emits machine-readable status
with `environment`, `result`, and per-check records.

For file output and inspection examples, see
[Preflight Artifacts](../../../docs/preflight_artifacts.md).

### Common failure causes

- Docker Desktop is not running
- the Pitch runtime bundle is missing from `third_party/pitch/PITCH-prti1516e-manual`
- another process is already bound to `8989` or `15164`
- the local host session cannot talk to Docker

### If you need the raw bridge diagnostics

Use the supported operator path first:

```bash
./tools/pitch preflight
./tools/pitch verify
```

Use `./tools/vendor-green pitch` only when you are debugging the shared
CI wrapper behavior itself.

Or inspect the negotiated ownership diagnostics:

- [`analysis/pitch_negotiated_ownership_2026-06-07/`](../../../analysis/pitch_negotiated_ownership_2026-06-07/)

## Short Answer

If you are a junior or just want Pitch working, use:

```bash
./tools/bootstrap pitch
./tools/pitch all
```

If you are debugging Java bridge behavior, use `pitch-jpype` and `pitch-py4j`.
