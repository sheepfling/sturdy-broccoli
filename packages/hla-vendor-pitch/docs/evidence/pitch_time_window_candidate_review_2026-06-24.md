# Pitch Time-Window Candidate Review

Date: `2026-06-24`

Artifact source:
- `artifacts/vendor_probe_promotion_review/vendor_probe_promotion_review_summary.json`
- `artifacts/vendor_probe_stability/pitch-time-window-probe/vendor_probe_stability_summary.json`
- `artifacts/vendor_probe_stability/pitch-time-window-restore-state-probe/vendor_probe_stability_summary.json`

## Summary

Both current Pitch-safe time-window probes regenerated as `candidate-review`
with repeated-run stability evidence present.

Profiles:
- `pitch-time-window-probe`
- `pitch-time-window-restore-state-probe`

Observed repeated-run result for both:
- repeat count: `5`
- success count: `5`
- failure count: `0`
- semantic stability: `true`
- semantic outcome totals: `xfailed=10`, `xpassed=0`

## Decision

Promote both probes to documented candidate-review status now.

That means:
- keep them as bounded vendor-credence probes
- stop describing them as unstable or inconclusive
- do not yet promote them to broad clause-level parity proof

## Why this is the right boundary

What the artifacts prove:
- the current Docker-backed Pitch route reruns these probes consistently
- the outcome signature is stable across all five attempts
- the earlier `xpass` anomaly is not present in the latest rerun set

What the artifacts do not prove:
- full Clause 8 parity
- full save/restore parity
- general promotion beyond the narrow documented Target/Radar time-window slice

## Operator wording

Use this wording when explaining the state:

- the two Pitch-safe time-window probes are now repeated-run stable and have
  been promoted to candidate-review evidence
- they are still intentionally bounded probes, not a full clause-level
  promotion
