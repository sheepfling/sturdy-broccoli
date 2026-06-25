# Pitch vs Python RTI Baseline

Use this page when the question is not just "does Pitch run?" but:

- what should match the repo's Python RTI baseline
- what currently diverges from that baseline
- which slices are still bounded probes rather than promoted parity claims

This page is intentionally current-state and operator-facing. Historical dated
notes stay in `docs/evidence/` and `packages/hla-vendor-pitch/docs/evidence/`.

## Baseline Rule

The Python RTI is the executable baseline for behavior authoring in this repo.

That means:

- new scenario semantics are usually authored and stabilized first against the
  Python RTI
- Pitch is then compared against that already-defined behavior
- a Python-green result does not automatically become a Pitch requirement
- a Pitch failure is only a repo regression when the repo currently defends
  that slice as `expected-pass` for Pitch

For the main Python proof lanes, use:

- `./tools/python verify`
- `./tools/python verify-main-2025`
- `./tools/python verify-routes-2025`

For the current Pitch operator and evidence lanes, use:

- `./tools/pitch smoke`
- `./tools/pitch verify`
- `./tools/pitch fom-smoke`
- `./tools/pitch fom-smoke-compare`
- `./tools/pitch 202x-micro-certify`

## Comparison Contract

Treat Python as the semantic baseline and Pitch as external vendor evidence for
the overlap that has actually been proven.

Use these classifications:

| Classification | Meaning |
| --- | --- |
| `expected-pass` | Python behavior is part of the defended Pitch overlap and should currently pass on the stated Pitch routes |
| `vendor-divergent` | Python behavior is understood, but Pitch currently behaves differently with concrete vendor evidence |
| `known-gap` | Python behavior exists, but Pitch is not yet promoted for that slice |
| `blocked` | the lane is not yet executable or not yet cleanly classifiable |

If a slice is not listed as `expected-pass`, do not treat a Pitch miss as
evidence that the Python baseline is wrong.

## Current Overlap Against Python

## Requirement-Facing Anchors

The comparison below is intentionally requirement-facing, but only where the
repo already has a defended anchor. Use these references to connect the Pitch
story back to the generated 2010 matrix and the bounded 2025 proof notes.

### 2010 requirement anchors for real Pitch 2010 overlap

| Slice | Requirement-facing anchors | Source |
| --- | --- | --- |
| synchronization | `HLA1516.1-FM-4.11-001`, `HLA1516.1-FM-4.12-001`, `HLA1516.1-FM-4.13-001`, `HLA1516.1-FM-4.14-001`, `HLA1516.1-FM-4.15-001` | `docs/backend_conformance_matrix.md` |
| save/restore lifecycle currently proven on real Pitch | `HLA1516.1-FM-4.16-001` through `HLA1516.1-FM-4.32-001` | `docs/backend_conformance_matrix.md` |
| basic ownership overlap that is currently promoted | `HLA1516.1-OWN-7.5-001`, `HLA1516.1-OWN-7.7-001`, `HLA1516.1-OWN-7.8-001`, `HLA1516.1-OWN-7.12-001`, `HLA1516.1-OWN-7.13-001` | `tests/verification/test_requirements_ledger_v013.py`, `docs/backend_conformance_matrix.md` |

### 2010 requirement anchors for known real Pitch divergence

| Slice | Requirement-facing anchors | Source |
| --- | --- | --- |
| negotiated ownership continuation | `HLA1516.1-OWN-7.8-001`, `HLA1516.1-OWN-7.11-001`, `HLA1516.1-OWN-7.13-001`, `HLA1516.1-OWN-7.15-001`, `HLA1516.1-OWN-7.16-001` | `docs/backend_conformance_matrix.md`, [evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md](evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md) |

### 2025 bounded proof anchors used for Pitch credence only

These are not claims that real Pitch 2010 is a native 2025 runtime.
They are the bounded 2025 proof ladders where Pitch currently supplies narrow
external credence for a subset of the Python-baseline behavior.

| Slice | Bounded proof anchors | Source |
| --- | --- | --- |
| time-window future exclusion | `time-window-future-exclusion` | `docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md` |
| time-window restore-state rollback | `time-window-save-restore-window-state` | `docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md` |
| SISO micro parity over `link16`, `rpr`, `space` | shared bounded scenario credence, not clause-by-clause parity | [evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md](evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md) |

### `expected-pass`

These are the Python-baseline slices that the repo currently defends as proven
for real Pitch 2010 vendor routes:

| Slice | Python baseline | Pitch routes | Evidence |
| --- | --- | --- | --- |
| exchange smoke | backend-neutral exchange/runtime smoke | `pitch-jpype`, `pitch-py4j` | vendor smoke lane and `tests/vendors/test_real_vendor_runtime_smoke.py` |
| synchronization | shared federation-management/sync scenarios, requirement-facing on `HLA1516.1-FM-4.11-001` through `HLA1516.1-FM-4.15-001` | `pitch-jpype`, `pitch-py4j` | real Pitch matrix |
| save/restore lifecycle overlap | shared save/restore scenarios, requirement-facing on `HLA1516.1-FM-4.16-001` through `HLA1516.1-FM-4.32-001` | `pitch-jpype`, `pitch-py4j` | real Pitch matrix |
| basic ownership, acquisition-if-available path | shared ownership scenarios, with currently promoted rows including `HLA1516.1-OWN-7.5-001`, `HLA1516.1-OWN-7.7-001`, `HLA1516.1-OWN-7.8-001`, `HLA1516.1-OWN-7.12-001`, `HLA1516.1-OWN-7.13-001` | `pitch-jpype`, `pitch-py4j` | real Pitch matrix |
| bounded SISO micro parity for `link16`, `rpr`, `space` | shared micro scenario against Python-backed semantics | `pitch-jpype`, `pitch-py4j`, `pitch-202x-jpype`, `pitch-202x-py4j` | `artifacts/pitch_202x_micro_certification/`, [evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md](evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md) |
| Pitch-safe time-window future exclusion | Python time-window ladder, bounded via `time-window-future-exclusion` | `pitch-jpype`, `pitch-py4j` | [evidence/pitch_time_window_candidate_review_2026-06-24.md](evidence/pitch_time_window_candidate_review_2026-06-24.md) |
| Pitch-safe time-window restore-state | Python save/restore window ladder, bounded via `time-window-save-restore-window-state` | `pitch-jpype`, `pitch-py4j` | [evidence/pitch_time_window_candidate_review_2026-06-24.md](evidence/pitch_time_window_candidate_review_2026-06-24.md) |
| real-runtime FOM smoke on `repo-cross-target-radar`, `link16-rpr2-integrated`, `rpr3-merged-informative-1516-2010` | shared FOM load/lookup smoke expectations | `pitch-jpype`, `pitch-py4j` | [evidence/pitch_fom_smoke_failures_2026-06-24.md](evidence/pitch_fom_smoke_failures_2026-06-24.md) |

### `vendor-divergent`

These are Python-baseline slices where Pitch currently has explicit contrary
evidence and should not be represented as parity-clean:

| Slice | Python baseline expectation | Pitch status | Evidence |
| --- | --- | --- | --- |
| negotiated ownership | full callback-complete negotiated transfer paths, especially `HLA1516.1-OWN-7.8-001`, `HLA1516.1-OWN-7.11-001`, `HLA1516.1-OWN-7.13-001`, `HLA1516.1-OWN-7.15-001`, `HLA1516.1-OWN-7.16-001` | bridge-divergent and incomplete across `pitch-jpype` / `pitch-py4j` | [evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md](evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md) |
| `repo-2010-demo` FOM family | repo fixture loads in Python lanes | vendor rejects FDD because `HLAdefaultRoutingSpace` lacks datatype | [evidence/pitch_fom_smoke_failures_2026-06-24.md](evidence/pitch_fom_smoke_failures_2026-06-24.md) |
| `space-fom-core` lookup probe | lookup resolves `HLAinteractionRoot.ReferenceFrameAnnouncement` in Python-backed lanes | vendor load proceeds, but interaction lookup fails | [evidence/pitch_fom_smoke_failures_2026-06-24.md](evidence/pitch_fom_smoke_failures_2026-06-24.md), [evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md](evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md) |

### `known-gap`

These are Python-baseline slices that exist and matter, but are not yet
promoted as stable Pitch overlap:

| Slice | Python baseline status | Pitch status |
| --- | --- | --- |
| save/restore beyond the promoted restore-state probe | executable and requirement-facing in Python lanes | probe-only / not parity-promoted |
| DDM | executable in Python lanes | probe-only / not parity-promoted |
| lost-federate | executable in bounded Python-facing fault lanes | probe-only / not parity-promoted |
| broad Target/Radar artifact-rich scenario proof | executable in Python lanes | not promoted as real Pitch parity |

## 2010 vs 202X Interpretation

Keep the route classes separate:

- `pitch-jpype` and `pitch-py4j` are real Pitch 2010 vendor-runtime evidence
- `pitch-202x-jpype` and `pitch-202x-py4j` are bounded adapter routes over the
  repo's Python 2025 backend

That means the `pitch-202x-*` routes can help answer:

- what the vendor-specific `hla.rti1516_202X` Java surface looks like
- whether repo examples can be routed through that surface
- whether bounded FOM and micro-scenario discovery works there

They do not by themselves prove native vendor 2025 semantics.

## Research Workflow

When a Python-green slice is being investigated for Pitch:

1. decide whether the slice belongs in defended overlap or only in probe space
2. run the smallest explicit Pitch lane for that slice
3. classify the result as `expected-pass`, `vendor-divergent`, `known-gap`, or `blocked`
4. record the exact failure mode or pass evidence in a checked-in note
5. update [pitch_behavior_matrix.md](pitch_behavior_matrix.md) if the defended claim changed

## Reading Order

1. [pitch_decision_tree.md](pitch_decision_tree.md)
2. [pitch_behavior_matrix.md](pitch_behavior_matrix.md)
3. this file
4. the exact evidence note for the slice under review

## Historical Source

The earlier dated overlap framing is still useful as provenance:

- [../../../docs/evidence/python_vs_pitch_overlap_2026-06-07.md](../../../docs/evidence/python_vs_pitch_overlap_2026-06-07.md)
