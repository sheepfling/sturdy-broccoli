# Pitch FOM Smoke Failures

Date: `2026-06-24`

Artifact source:
- `artifacts/pitch_fom_smoke/pitch_fom_smoke_summary.json`
- `artifacts/pitch_fom_smoke/pitch_fom_smoke_report.md`

Scope:
- command: `./tools/pitch fom-smoke`
- real vendor-runtime bridges:
  - `pitch-jpype`
  - `pitch-py4j`

## Requirement-Facing Anchors

These packet failures are requirement-relevant, but they do not yet map to one
clean generated "Pitch FOM family" requirement row.

Use the nearest existing anchors instead:

- `repo-2010-demo` parse failure:
  - closest service anchors are `createFederationExecution` (`§4.5`) and
    `joinFederationExecution` (`§4.9`)
  - `ErrorReadingFDD` is an allowed exception surface on both services; see
    `packages/hla-rti1516e/SOURCE_TRACE.md`
- `space-fom-core` lookup failure:
  - closest service anchor is `getInteractionClassHandle` (`§10.15`)
  - `NameNotFound` is an allowed exception surface there; see
    `packages/hla-rti1516e/SOURCE_TRACE.md`

Current traceability boundary:

- these notes are vendor-divergence evidence for FOM-backed executable packets
- they are not yet dedicated generated requirement rows for those packet IDs
- the Python-owned bounded scenario note remains
  `docs/requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md`

## Summary

The current Pitch real-runtime FOM smoke lane is partially green, but two
families fail on both bridges for concrete vendor-observable reasons.

Green on both bridges:
- `repo-cross-target-radar`
- `link16-rpr2-integrated`
- `rpr3-merged-informative-1516-2010`

Failed on both bridges:
- `repo-2010-demo`
- `space-fom-core`

This is strong enough to treat both failures as explicit vendor evidence, not
as flaky harness noise.

## Failure 1: `repo-2010-demo`

Packet:
- `repo-2010-demo`

Observed failure type on both bridges:
- `ErrorReadingFDD`

Observed vendor message:
- `Invalid FDD: Dimension HLAdefaultRoutingSpace has no datatype`

Bridge-specific captured strings:
- `pitch-jpype`: `<bound method JException.message of ErrorReadingFDD('Invalid FDD: Dimension HLAdefaultRoutingSpace has no datatype (file:/tmp/DemoFOMmodule10987164778126894139.xml)')>`
- `pitch-py4j`: `Invalid FDD: Dimension HLAdefaultRoutingSpace has no datatype (file:/tmp/DemoFOMmodule5623147103415101271.xml)`

Interpretation:
- Pitch rejects the repo demo FOM during federation creation/load.
- The rejection is about the FDD content, not object or interaction lookup.
- Because both bridges fail with the same parser complaint, the bridge is not
  the interesting variable here.

Operator explanation:
- the bundled demo FOM is not currently accepted by Pitch because its
  `HLAdefaultRoutingSpace` dimension is treated as invalid without an explicit
  datatype

Nearest requirement-facing anchors:
- `§4.5` `createFederationExecution`
- `§4.9` `joinFederationExecution`
- explicit exception surface:
  - `ErrorReadingFDD`

## Failure 2: `space-fom-core`

Packet:
- `space-fom-core`

Observed failure type on both bridges:
- `NameNotFound`

Observed vendor message:
- `getInteractionClassHandle HLAinteractionRoot.ReferenceFrameAnnouncement (909149037)`

Bridge-specific captured strings:
- `pitch-jpype`: `<bound method JException.message of NameNotFound('getInteractionClassHandle HLAinteractionRoot.ReferenceFrameAnnouncement (909149037)')>`
- `pitch-py4j`: `getInteractionClassHandle HLAinteractionRoot.ReferenceFrameAnnouncement (909149037)`

Interpretation:
- Pitch accepts the ordered Space FOM family far enough to create and join the
  federation.
- The failure happens later when the probe asks for
  `HLAinteractionRoot.ReferenceFrameAnnouncement`.
- That means this is not a coarse XML parse rejection like `repo-2010-demo`;
  it is a post-load lookup failure against an interaction the probe expects to
  exist.

Operator explanation:
- the current Pitch runtime can load the Space FOM family far enough to start,
  but it does not resolve `ReferenceFrameAnnouncement` through the tested lookup
  path

Nearest requirement-facing anchor:
- `§10.15` `getInteractionClassHandle`
- explicit exception surface:
  - `NameNotFound`

## Claim boundary

These results support the following precise statement:

- Pitch real-runtime FOM smoke currently proves successful load and lookup on
  three families and reproducible vendor failures on two families.

They do not support the broader statement:

- "Pitch generally handles all bundled and SISO example FOM families."
