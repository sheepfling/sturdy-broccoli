# Pitch 202X Adapter FOM Smoke

Date: `2026-06-24`

Artifact source:
- `artifacts/pitch_fom_smoke_202x_adapters/pitch_fom_smoke_summary.json`
- `artifacts/pitch_fom_smoke_202x_adapters/pitch_fom_smoke_report.md`

Scope:
- command: `./tools/pitch fom-smoke --kind pitch-202x-jpype --kind pitch-202x-py4j`
- routes exercised:
  - `pitch-202x-jpype`
  - `pitch-202x-py4j`

## Requirement-Facing Anchors

These adapter-backed rows are still bounded route evidence, not native vendor
2025 conformance rows.

Use the nearest existing anchors instead:

- `repo-2010-demo` contrast with the real Pitch runtime still speaks to the
  `createFederationExecution` (`§4.5`) / `joinFederationExecution` (`§4.9`)
  parse surface because the real vendor runtime is where `ErrorReadingFDD`
  occurs
- `space-fom-core` still lands on `getInteractionClassHandle` (`§10.15`) with
  `NameNotFound`

Current traceability boundary:

- this note explains bounded adapter contrast against the Python RTI baseline
- it does not create a new dedicated generated requirement row for the
  `pitch-202x-*` FOM packet lane

## Claim boundary

These are explicit adapter-backed results.

They exercise the checked-in `pitch-202x-*` routes over the repo Python `2025`
backend while preserving Pitch runtime discovery metadata.

They do **not** prove native Pitch `202X` vendor-runtime behavior.

## Summary

Current adapter result:
- total rows: `10`
- lookup-green rows: `8`
- failed rows: `2`

Green on both adapter routes:
- `repo-2010-demo`
- `repo-cross-target-radar`
- `link16-rpr2-integrated`
- `rpr3-merged-informative-1516-2010`

Failed on both adapter routes:
- `space-fom-core`

## Important contrast with the real 2010 Pitch runtime lane

Compared with `./tools/pitch fom-smoke` on `pitch-jpype` and `pitch-py4j`:

- `repo-2010-demo` is green here
- `repo-2010-demo` fails on the real vendor-runtime lane with `ErrorReadingFDD`
- `space-fom-core` still fails here and also fails on the real vendor-runtime lane

That means:
- the demo parse failure is specific to the real vendor-runtime Pitch path
- the Space FOM interaction lookup gap survives even when the explicit
  `pitch-202x-*` adapters wrap the repo `2025` backend

## Remaining adapter failure

Packet:
- `space-fom-core`

Observed failure type on both routes:
- `NameNotFound`

Observed captured message:
- `HLAinteractionRoot.ReferenceFrameAnnouncement`

Operator explanation:
- even through the explicit `pitch-202x-*` adapter routes, the current probe
  still cannot resolve `ReferenceFrameAnnouncement` in the Space FOM family

Nearest requirement-facing anchor:
- `§10.15` `getInteractionClassHandle`
- explicit exception surface:
  - `NameNotFound`
