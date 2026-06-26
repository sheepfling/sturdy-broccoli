# Pitch 202X Bounded Comparison

Source: bounded Pitch proto HLA 4 / `202X` adapter-route evidence over the repo
2025 Python RTI lane.

This note records the repo's current requirement-facing reading for the Pitch
proto HLA 4 / `202X` surface. It is the canonical owner doc for grouped
`pitch_202x_resolution` entries in the 2025 harmonization worklist.

It does not promote Pitch into a second 2025 RTI owner.
It does not claim IEEE 1516.1-2025 vendor conformance.
It records the narrow current evidence the repo actually has.

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`
- companion grouped artifact:
  `requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`
- companion row-level artifact:
  `requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv`
- primary command: `./tools/pitch 202x-micro-certify`
- typical view tags: `2025-core`, `transport`, `java-shim`, `finish-line`

## Final Claim Rule

- this doc is a backend-resolution note, not a second 2025 RTI-owner claim
- vendor proto HLA 4 / `202X` branding does not by itself prove IEEE
  1516.1-2025 closure for the repo or for any grouped FI family
- count current Pitch evidence only as the bounded adapter-route comparison that
  the committed micro-certification packet actually proves
- only widen a Pitch-related grouped row when a narrower explicit vendor packet
  closes that exact requirement surface

Default final stance:

- this bucket is already in its intended final repo-owned state as a bounded
  backend-resolution owner surface
- no additional proof is required to keep Pitch proto HLA 4 / `202X` out of
  canonical 2025 requirement status and out of full vendor-conformance claims
- future work is optional and should happen only if the repo deliberately opens
  a broader vendor-runtime comparison or certification program with its own
  bounded claim and tests

## Current Evidence Packet

Use these files together:

- `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_summary.json`
- `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_comparison.csv`
- `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md`
- `packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md`

Current bounded reading from the committed packet:

- certification state: `bounded-vendor-comparison`
- current concrete `2025` families: `link16`, `rpr`, `space`
- current concrete adapter routes:
  `pitch-202x-jpype`, `pitch-202x-py4j`
- current interpretation:
  bounded adapter-route behavior discovery over the repo Python 2025 runtime,
  not a native vendor 2025 conformance packet

## Current Covered Micro Families

| Family | Bridge | Current packet result | Current bounded reading |
| --- | --- | --- | --- |
| `link16` | `jpype`, `py4j` | `passed` | bounded adapter-route parity over the committed `link16-rpr2-integrated` micro packet |
| `rpr` | `jpype`, `py4j` | `passed` | bounded adapter-route parity over the committed `rpr3-annex-a-normative` micro packet |
| `space` | `jpype`, `py4j` | `passed` | bounded adapter-route parity over the committed `space-fom-core` micro packet |

## Grouped 2025 Reading

Use this rule when reading grouped `pitch_202x_resolution` fields:

| Group family | Current bounded reading |
| --- | --- |
| FI service catalog rows marked `covered` | some Pitch 202X overlap may exist, but the current committed evidence packet is still narrower than clause-complete FI service conformance |
| FI service catalog rows marked `partial` | keep the grouped row `partial` unless a narrower Pitch 202X proof packet closes the exact service family |
| FI service catalog rows marked `planned` | do not infer support from jar or namespace naming alone; no grouped Pitch 202X closure exists yet |
| callback/configuration/binding delta umbrellas | interpret through child FI rows plus the bounded Pitch 202X packet, never as standalone closure |
| OMT, service-usage, framework, and legacy buckets | not Pitch 202X runtime-owner buckets unless a future dedicated vendor packet is added |

## Row-Level Reading

When the grouped table is too coarse, read
`requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv` with
these meanings:

| Row resolution | Meaning |
| --- | --- |
| `bounded-fi-overlap-only` | the row is FI-facing and Pitch may traverse it through bounded adapter bridges, but the current packet does not prove clause-complete parity for that exact service row |
| `umbrella-only-child-fi-owned` | callback or binding umbrella row; resolve through child FI rows and the owner doc |
| `mirrored-fi-cross-check-only` | SOM/FOM usage row; resolve through the mirrored FI owner row rather than this row |
| `not-a-pitch-runtime-owner` | OMT parser, validator, import, or export row; not a Pitch runtime claim |
| `framework-umbrella-child-owned` | framework umbrella row; resolve through linked child FI or OMT rows |
| `legacy-only-no-active-pitch-claim` | retired or replacement-mapping row; not an active Pitch behavior-support claim |

## Boundary Notes

- Pitch may label the Java-facing surface as proto HLA 4 / `202X` in jar and
  namespace naming.
- That vendor label is backend-resolution terminology only.
- `pitch-202x-jpype` and `pitch-202x-py4j` are bounded adapter routes over
  `hla-backend-python1516-2025`.
- `hla-backend-shim` remains a compatibility wrapper and is not a runtime owner
  for this bounded Pitch 202X reading.
- Java bridge packages and `hla-backend-cpp-shim` remain wrapper/binding
  surfaces over the main Python 2025 runtime rather than alternate 2025 RTIs.
- Hosted FedPro is a bounded transport/runtime slice over
  `hla-backend-python1516-2025`; it is not a second RTI implementation lane for
  this bounded Pitch comparison.
- The real vendor-runtime anchor in the current packet remains `pitch-jpype`
  and `pitch-py4j` on the `2010` side of the comparison.
- The current packet does not prove:
  - clause-complete Federate Interface conformance
  - native vendor 2025 semantics
  - broad OMT/service-usage/validator closure
  - full transport or callback parity outside the committed micro families

## Exit Condition

Treat this bucket as closed for current closeout purposes when all of these are
true:

1. the grouped and row-level `pitch_202x_resolution` artifacts remain anchored
   to this owner doc
2. the final claim language keeps Pitch proto HLA 4 / `202X` explicit as a
   bounded backend-resolution reading rather than canonical requirement status
   or vendor-conformance proof
3. no generated packet, audit note, or grouped worklist reclassifies the
   current bounded comparison into a broader vendor-runtime conformance claim

Only reopen this bucket if the repo intentionally starts a broader Pitch 202X
vendor-runtime comparison or certification program.

## Reading Order

1. this note
2. `requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`
3. `requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv`
4. `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md`
5. `packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md`
