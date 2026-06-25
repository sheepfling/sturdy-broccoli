# Pitch Behavior Matrix

This is the shortest single source of truth for Pitch behavior in this repo.

Use it when you need to answer:

- which Pitch routes are real vendor-runtime evidence
- which Pitch routes are bounded adapter evidence only
- which slices are expected to pass
- which slices are expected to remain vendor-divergent or blocked
- where the exact evidence note or operator command lives

For the explicit Python-baseline comparison and classification policy, also
read [pitch_vs_python_baseline.md](pitch_vs_python_baseline.md).

## Route Classes

| Route | Runtime class | Claim class | Default use |
| --- | --- | --- | --- |
| `pitch-jpype` | real Pitch 2010 vendor runtime | real vendor evidence | compare real Java bridge behavior |
| `pitch-py4j` | real Pitch 2010 vendor runtime | real vendor evidence | compare real Java bridge behavior |
| `pitch-202x-jpype` | repo adapter over Python 2025 backend | bounded behavior discovery only | discover the vendor-specific `202X` surface without claiming IEEE 2025 conformance |
| `pitch-202x-py4j` | repo adapter over Python 2025 backend | bounded behavior discovery only | discover the vendor-specific `202X` surface without claiming IEEE 2025 conformance |

## Route Boundaries

### Real Pitch 2010

`pitch-jpype` and `pitch-py4j` count as real vendor-runtime evidence.

They can support:

- vendor smoke
- vendor verification
- real-runtime FOM smoke
- bounded SISO micro parity
- bounded Pitch-safe time-window probes

They do not automatically imply:

- blanket parity with the Python RTI
- blanket parity between `jpype` and `py4j`
- any IEEE 1516.1-2025 claim

### Pitch 202X adapter routes

`pitch-202x-jpype` and `pitch-202x-py4j` are explicit adapter routes.

They prove:

- the bundled Pitch jars expose a live vendor-specific `hla.rti1516_202X` surface
- the repo can route that surface through explicit adapter lanes
- bounded example/FOM and micro-scenario behavior discovery can succeed through those routes

They do not prove:

- native Pitch `202X` vendor-runtime behavior
- IEEE 1516.1-2025 conformance

See:

- [evidence/pitch_202x_probe_2026-06-23.md](evidence/pitch_202x_probe_2026-06-23.md)
- [evidence/pitch_202x_surface_audit_2026-06-23.md](evidence/pitch_202x_surface_audit_2026-06-23.md)

## Expected Passes

### Real Pitch 2010 expected-pass slices

| Slice | Expected state | Operator path | Evidence |
| --- | --- | --- | --- |
| exchange smoke | pass | `./tools/pitch smoke` | vendor smoke lane plus `tests/vendors/test_real_vendor_runtime_smoke.py::test_pitch_java_real_exchange_smoke` |
| bounded SISO micro parity over `link16`, `rpr`, `space` | pass | `./tools/pitch 202x-micro-certify` | `artifacts/pitch_202x_micro_certification/` |
| Pitch-safe time-window future exclusion | candidate-review pass | `./tools/pitch time-window-probe` | [evidence/pitch_time_window_candidate_review_2026-06-24.md](evidence/pitch_time_window_candidate_review_2026-06-24.md) |
| Pitch-safe time-window restore-state | candidate-review pass | `./tools/pitch time-window-restore-state-probe` | [evidence/pitch_time_window_candidate_review_2026-06-24.md](evidence/pitch_time_window_candidate_review_2026-06-24.md) |
| real-runtime FOM smoke on `repo-cross-target-radar`, `link16-rpr2-integrated`, `rpr3-merged-informative-1516-2010` | pass | `./tools/pitch fom-smoke` | [evidence/pitch_fom_smoke_failures_2026-06-24.md](evidence/pitch_fom_smoke_failures_2026-06-24.md) |

### Bounded Pitch 202X expected-pass slices

| Slice | Expected state | Operator path | Evidence |
| --- | --- | --- | --- |
| `202X` Java surface discovery | pass | `./tools/pitch 202x-certify` and Java discover routes | [evidence/pitch_202x_probe_2026-06-23.md](evidence/pitch_202x_probe_2026-06-23.md) |
| bounded SISO micro parity over `link16`, `rpr`, `space` | pass | `./tools/pitch 202x-micro-certify` | `artifacts/pitch_202x_micro_certification/` |
| adapter-backed FOM smoke on `repo-2010-demo`, `repo-cross-target-radar`, `link16-rpr2-integrated`, `rpr3-merged-informative-1516-2010` | pass | `./tools/pitch fom-smoke --kind pitch-202x-jpype --kind pitch-202x-py4j` | [evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md](evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md) |

## Expected Vendor Divergence Or Known Gaps

| Slice | Current state | Why | Evidence |
| --- | --- | --- | --- |
| negotiated ownership | vendor-divergent | real Pitch bridge behavior is not parity-clean across continuation paths | [evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md](evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md) |
| save/restore | known gap / probe-only | not promoted as stable parity | `./tools/pitch save-restore`, `./tools/pitch save-restore-probe` |
| DDM | known gap / probe-only | not promoted as stable parity | `./tools/pitch ddm`, `./tools/pitch ddm-probe` |
| lost-federate | known gap / probe-only | backend-split fault-injection limitations remain | `./tools/pitch lost-federate`, `./tools/pitch lost-federate-probe` |

## Expected FOM-specific Failures

### Real Pitch 2010 failures

| Family | Expected state | Why | Evidence |
| --- | --- | --- | --- |
| `repo-2010-demo` | fail | Pitch rejects the demo FDD because `HLAdefaultRoutingSpace` has no datatype | [evidence/pitch_fom_smoke_failures_2026-06-24.md](evidence/pitch_fom_smoke_failures_2026-06-24.md) |
| `space-fom-core` lookup probe | fail | current lookup path does not resolve `HLAinteractionRoot.ReferenceFrameAnnouncement` | [evidence/pitch_fom_smoke_failures_2026-06-24.md](evidence/pitch_fom_smoke_failures_2026-06-24.md) |

### Bounded Pitch 202X adapter failures

| Family | Expected state | Why | Evidence |
| --- | --- | --- | --- |
| `space-fom-core` lookup probe | fail | the current adapter-backed probe still cannot resolve `ReferenceFrameAnnouncement` | [evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md](evidence/pitch_202x_adapter_fom_smoke_2026-06-24.md) |

## Important Runtime Behaviors

### Named object registration can require reservation

Pitch real-runtime named object registration should be treated as requiring the reservation-aware helper path, not as a free assumption.

Use the shared registration helper when the scenario supplies explicit object names.

Relevant evidence:

- [pitch_decision_tree.md](pitch_decision_tree.md)
- `packages/hla-verification/src/hla/verification/scenario_support.py`

### Callback delivery can require explicit wait loops

Pitch real-runtime two-federate SISO micro delivery was not reliably proven by a simple bounded callback drain alone.

The passing behavior came from aligning the SISO micro lane with the same explicit callback wait discipline already used by the proven real Pitch exchange smoke:

- wait after registration for discovery callbacks
- wait after attribute update for reflect callbacks
- wait after interaction send for receive callbacks

This was a real Pitch 2010 runtime/bridge behavior issue in the executable lane.
It was not:

- a `pitch-202x-*` 2025 adapter failure
- an XML/FOM decode failure

See:

- [evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md](evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md)

### FedPro session drop/resume messages can appear during successful runs

Successful bounded micro runs can still log FedPro session drop/resume messages while completing green.

Treat those messages as vendor-observable runtime behavior, not automatically as proof the packet failed.

See:

- [evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md](evidence/pitch_siso_micro_delivery_alignment_2026-06-24.md)

## Expected-Failure Research Policy

Yes, Pitch should be evaluated relative to the Python RTI baseline, but not every Python-green slice should be treated as a Pitch regression.

For the current explicit overlap/divergence map, see
[pitch_vs_python_baseline.md](pitch_vs_python_baseline.md).

Use these buckets:

- `expected-pass`
  - the repo currently defends this as working for Pitch
- `vendor-divergent`
  - the repo currently has evidence that Pitch behaves differently here
- `known-gap`
  - the repo intentionally does not promote this slice yet
- `blocked`
  - the lane is not yet executable or not yet classified cleanly

When a Pitch result changes, update:

1. this matrix
2. the exact evidence note
3. the requirement disposition or vendor classification if the change affects the defended claim

## Recommended Operator Reading Order

1. [pitch_decision_tree.md](pitch_decision_tree.md)
2. this file
3. [pitch_vs_python_baseline.md](pitch_vs_python_baseline.md)
4. the exact evidence note for the slice you are touching
