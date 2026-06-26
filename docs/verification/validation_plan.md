# Validation Plan

This plan defines the operational-usefulness work for the Python HLA 1516.1-2010 RTI.

It is intentionally separate from [verification_plan.md](verification_plan.md).

This page is 2010-specific. For the current IEEE 1516.1-2025 Python RTI lane,
do not treat this file as the main operational proof ledger.

Use these 2025 evidence anchors instead:

- [`../python_rti_backend.md`](../python_rti_backend.md)
- [`../verification/time_model_compliance.md`](time_model_compliance.md)
- [`../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)
- [`../plans/2025_python_rti_backend_audit.md`](../plans/2025_python_rti_backend_audit.md)
- [`../plans/spec2025_finish_line.md`](../plans/spec2025_finish_line.md)

Use that exclusion note when you need the explicit non-claim boundary around
the bounded 2025 direct `python1516_2025` lane plus hosted FedPro route
validation story, especially for legacy aliases, Java/C++ bindings, hosted
transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope
OMT extension semantics.

## Goal

Produce defensible evidence that realistic federations can run correctly on `hla2010`, generate useful outputs, and be diagnosed when they fail.

## Validation Questions

Use validation assets to answer:

- can federates discover and interact in a realistic way?
- can time-managed workflows support a meaningful study?
- can observer/monitor federates reconstruct federation behavior?
- can scenario artifacts explain success and failure without reading backend code?

## Scenario Levels

### Level 10A: Basic Federation Validation

Use small realistic studies first.

Current anchor:

- target/radar

Validate:

- truth target motion
- radar discovery
- RCS query/response exchange
- track generation

Primary assets:

- `artifacts/target_radar_proof/*`
- `artifacts/target_radar_backend_matrix/*`

### Level 10B: Multi-Federate Mission Validation

Add richer federations:

- aircraft
- radar
- shooter
- optional monitor

Validate:

- detect
- track
- engage
- state transitions across multiple federates

This should become a new proof-packet family under `analysis/validation/`.

### Level 10C: MOM Observer Validation

Add a federate that subscribes only to MOM.

Validate that it can reconstruct:

- joins
- resigns
- publications
- subscriptions
- ownership transfers
- time state changes
- service calls

This asset is especially valuable because it works both as:

- verification evidence for RTI self-report consistency
- validation evidence for federation observability

### Level 10D: Persistence Validation

Run a scenario through:

- advance
- save
- shutdown
- restore
- continue

Validate:

- scenario continuity
- restored object state
- restored time state
- restored ownership state

### Level 10E: Transport Validation

Run the same scenario packet across:

- Python in-memory
- REST-hosted Python
- gRPC-hosted Python
- Java shim paths

The scenario outputs should stay behaviorally equivalent.

## Validation Evidence Standard

A validation packet should contain:

- machine-readable summary
- raw CSV traces
- human-readable report
- plotted artifacts
- explicit rerun command
- explicit backend/runtime attribution

The target/radar packet is the current model, but future validation packets should avoid decorative status graphics and emphasize actual scenario plots and exchange traces.

## Current Validation Spine

Use these as the first-class validation assets:

- [../README.md](../README.md) for rerun entrypoints
- `examples/target_radar_simulation.py`
- `scripts/run_target_radar_proof.py`
- `scripts/ci/target_radar_proof.sh`
- `artifacts/target_radar_proof/*`
- `artifacts/two_federate_suite/*`

## Highest-Value Missing Validation Assets

1. a MOM observer federation packet
2. a shooter-style multi-federate study
3. save/restore continuation validation
4. transport-neutral scenario comparison packet
5. failure-diagnosis packets that show why a backend is misconfigured

## Acceptance Rule

A validation scenario is only "complete" when:

- the scenario purpose is explicit
- the expected operational behavior is explicit
- the proof packet is rerunnable by an operator
- the packet includes raw traces and plotted outputs
- the packet makes failure diagnosis practical

Validation is not complete just because a scenario returns `passed`.
