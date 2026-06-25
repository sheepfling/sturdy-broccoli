# SISO FOM Runtime Showcase

Use this when you need actual federate-backed micro-scenarios for the most
salient SISO families rather than only validation and round-trip artifacts.

## Front Door

- `./tools/fom-siso-runtime-showcase`
- `./tools/fom-siso-runtime-launcher`

Generated artifacts land under:

- `artifacts/siso_runtime_showcase/siso_runtime_showcase_summary.json`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_scenarios.csv`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_backend_matrix.csv`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_manifest.json`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_report.md`

Promote into `analysis/...` only when you want to retain and cite a specific
packet.

## Included Runtime Scenarios

The runtime lane is now a matrix:

- families: `Link 16`, `RPR`, `Space`
- editions: `2010`, `2025`
- topologies: `micro-2`, `squad-5`, `constellation-10`

That yields 18 executable scenarios.

The backend policy for those 18 rows is separate and explicit:

- Python baseline:
  - `2010` rows use `python1516e`
  - `2025` rows use `python1516_2025`
  - all 18 rows are expected to execute here
- Pitch vendor parity:
  - `2010` rows may use `pitch-jpype` or `pitch-py4j` only for `micro-2`
  - `2025` rows may use `pitch-202x-jpype` or `pitch-202x-py4j` only for `micro-2`
  - `squad-5` and `constellation-10` stay Python-only on purpose
- `Pitch 202X` note:
  - this is a bounded vendor-credence lane, not an IEEE `1516.1-2025` conformance claim

Each row is also emitted into an explicit scenario manifest with:

- scenario id
- family and edition
- topology and federate count
- source packet and concrete FOM module names
- participant-role list
- backend eligibility and boundary notes

That manifest is the direct handoff surface for larger federation launchers.

The launcher wrapper now consumes that manifest directly and lets operators
filter by:

- family
- edition
- topology
- explicit scenario id

So the larger showcase lane no longer needs hardcoded scenario selection logic.

Representative examples:

- `link16-rpr2-integrated-2010-micro-2`
  - story: one Link 16 originator publishes `RadioTransmitter` state and sends
    `JTIDSMessageRadioSignal` plus `RTTABRadioSignal` to one observer
- `rpr-runtime-2025-squad-5`
  - story: one bridge owner plus multiple shooters and observers execute a
    `WeaponFire` and `MunitionDetonation` chain
- `space-fom-core-2025-constellation-10`
  - story: one frame authority plus multiple entity producers and observers
    propagate reference-frame and dynamical-entity state across a larger
    constellation

## Why It Exists

This is the runtime companion to the static SISO showcase packet:

- it proves the downloaded families are useful for small executable demos
- it gives us stronger showcase material than parser-only stress packets
- it keeps the stories narrow enough to stay green in normal repo testing
- it now gives us a reusable parity lane for 2-federate vendor checks and
  larger 5- and 10-federate showcase topologies

## Orchestration Model

These scenarios use the repo's explicit local orchestration model:

- startup is direct `connect/create/join`
- callback delivery is explicit `evoke...Callbacks(...)` pumping
- 2010 pair scenarios use one shared in-memory engine
- scenario progress is advanced by bounded callback drains between lifecycle
  phases

Read [`federation_orchestration.md`](federation_orchestration.md) for the
operator-facing explanation of startup sync points, callback processing, and the
difference between multi-federate and actual multi-process orchestration.
