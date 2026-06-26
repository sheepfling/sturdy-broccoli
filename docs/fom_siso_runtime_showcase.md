# SISO FOM Runtime Showcase

Use this when you need actual federate-backed micro-scenarios for the most
salient SISO families rather than only validation and round-trip artifacts.

## Front Door

- `./tools/fom-siso-runtime-showcase`
- `./tools/fom-siso-runtime-launcher`
- `./tools/fom-siso-runtime-observer`

Generated artifacts land under:

- `artifacts/siso_runtime_showcase/siso_runtime_showcase_summary.json`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_scenarios.csv`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_backend_matrix.csv`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_manifest.json`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_listener_index.json`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_listener_index.html`
- `artifacts/siso_runtime_showcase/siso_runtime_showcase_report.md`
- `artifacts/siso_runtime_showcase/listener/<scenario>/listener_trace.ndjson`
- `artifacts/siso_runtime_showcase/listener/<scenario>/listener_summary.json`
- `artifacts/siso_runtime_showcase/listener/<scenario>/listener_report.html`

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

## Listener Federate

Each runtime row now treats the last observer as an explicit listener federate.

That listener does three jobs:

- subscribes to the scenario's object and interaction traffic
- records callback-level timeline events during execution
- emits operator-facing artifacts that show:
  - loaded FOM modules
  - participant roster and roles
  - lifecycle progress phases
  - discovered objects, reflected updates, and received interactions
  - basic runtime statistics

The important boundary is that this is still a real federate in the scenario,
not a post-hoc parser over the final summary.

The two main listener outputs are:

- `listener_trace.ndjson`
  - append-friendly event stream for phase changes, object registration/update
    operations, and listener callback traffic
- `listener_report.html`
  - compact runtime dashboard for one scenario

Use the listener index HTML when you want the shortest front door for "what ran
and where is the per-scenario live-view packet?".

## Live Observer Server

If you need a watchable live session instead of a post-run packet, use:

- `./tools/fom-siso-runtime-observer`
- optional auto-start: `./tools/fom-siso-runtime-observer --provider siso-runtime --scenario link16-rpr2-integrated-2010-micro-2`

That tool:

- exposes a scenario catalog and start/stop control plane
- can launch:
  - SISO runtime showcase rows
  - the workspace `two-federate` suite
  - the `target-radar` proof lane
- exposes local JSON state at `/api/state`
- exposes the stable normalized event schema at `/api/schema`
- exposes the scenario catalog at `/api/catalog`
- exposes start and stop control endpoints at `/api/control/start` and `/api/control/stop`
- exposes append-only callback events at `/api/events`
- exposes a live SSE stream at `/events`
- serves a local HTML dashboard at `/`

This is the first concrete route toward a manager-facing "watch the federation"
surface without forcing the RTI-facing federates themselves to become a web
stack.

Current telemetry boundary:

- `SISO runtime` rows have true live callback/event streaming because the
  listener federate writes normalized timeline events
- `two-federate` now emits live phase plus callback events through the shared
  suite timeline recorder
- `target-radar` now emits live phase plus target/radar/track progression
  events during execution

The observer page now also exposes simple scenario option controls:

- backend override
- `target_radar_steps` for the `two-federate` and `target-radar` lanes

The page is now framed as a generic federation subscriber:

- normalized event families:
  - `object.discovered`
  - `object.updated`
  - `interaction.received`
  - `scenario.phase`
  - `scenario.operation`
- stable contract:
  - checked-in schema: [`reference/runtime_observer_event_schema.json`](reference/runtime_observer_event_schema.json)
  - notes: [`reference/runtime_observer_event_schema.md`](reference/runtime_observer_event_schema.md)
- generic inspectors:
  - object inspector
  - interaction inspector
- generic filtering:
  - family filter
  - class filter
  - event-type filter
- optional semantic panels layered on top:
  - Target/Radar
  - RPR
  - Link 16

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
