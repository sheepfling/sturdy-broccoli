# Pitch FOM Smoke Comparison

Date: `2026-06-24`

Related generated packet:
- `artifacts/pitch_fom_smoke_compare/pitch_fom_smoke_compare_summary.json`
- `artifacts/pitch_fom_smoke_compare/pitch_fom_smoke_compare_report.md`

Front door:
- `./tools/pitch fom-smoke`
- `./tools/pitch fom-smoke-compare`

## Summary

The side-by-side comparison is useful because it separates:

- real Pitch 2010 vendor-runtime behavior
- explicit `pitch-202x-*` adapter behavior over the repo Python `2025` backend

Current comparison result:

- green on both lanes:
  - `repo-cross-target-radar`
  - `link16-rpr2-integrated`
  - `rpr3-merged-informative-1516-2010`
- real-Pitch-only failure:
  - `repo-2010-demo`
- shared failure across both lanes:
  - `space-fom-core`

## Why this matters

This is the fastest way to explain two different kinds of failure:

- `repo-2010-demo`:
  - the failure is specific to the real Pitch vendor-runtime lane
  - the same packet is green through the `pitch-202x-*` adapter wrappers
- `space-fom-core`:
  - the failure survives even through the explicit `pitch-202x-*` adapter lane
  - treat that as a broader family or lookup quirk, not just a narrow 2010
    bridge parse issue

## Learning value

This packet is also a compact FOM-learning surface:

- it shows which example packets behave like clean federation roots
- it shows which packets are integration families rather than standalone XMLs
- it shows how runtime evidence can differ from parser-only or adapter-backed
  evidence
