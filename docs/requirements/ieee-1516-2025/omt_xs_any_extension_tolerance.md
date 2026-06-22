# OMT `xs:any` Extension Tolerance

Source: IEEE 1516.2-2025 OMT schema extension points with `xs:any` / `##other`.

This bounded-proof note covers the 45 OMT component rows that permit foreign
namespace extension payloads. The repo evidence supports payload preservation,
schema-tolerant parsing, and serializer round-trip of those foreign XML
fragments. It does not claim arbitrary third-party extension execution
semantics or interpretation as native HLA metadata.

## Current Bounded Claim

- Foreign-namespace `xs:any` extension elements are accepted at the tracked
  2025 OMT extension points.
- Text, attributes, and nested foreign XML are preserved for parse and
  serialize round-trip.
- Foreign extension payloads remain isolated from native HLA elements and are
  not reinterpreted as repo-native runtime semantics.
- This is parser/serializer tolerance evidence, not a claim to execute
  arbitrary third-party extension semantics.

## Primary Evidence Anchors

- `tests/test_rti1516_2025_validation.py`
- `packages/hla-rti1516e/src/hla/rti1516e/fom.py`
- `docs/plans/spec2025_finish_line.md`

## Family Mapping

| Family | Requirement count | Example requirement IDs | Focus |
| --- | ---: | --- | --- |
| `model-identification-and-top-level-extension-points` | 2 | `HLA2025-OMT-COMP-202`, `HLA2025-OMT-COMP-224` | Foreign extension points around objectModel identity and top-level reference sections. |
| `object-class-and-attribute-extension-points` | 16 | `HLA2025-OMT-COMP-019`, `HLA2025-OMT-COMP-045`, `HLA2025-OMT-COMP-082` | Foreign extension points attached to object classes, attributes, update metadata, dimensions, and associations. |
| `interaction-class-and-parameter-extension-points` | 8 | `HLA2025-OMT-COMP-102`, `HLA2025-OMT-COMP-110`, `HLA2025-OMT-COMP-134` | Foreign extension points attached to interaction classes, parameters, order metadata, and associations. |
| `datatype-and-encoding-extension-points` | 12 | `HLA2025-OMT-COMP-006`, `HLA2025-OMT-COMP-057`, `HLA2025-OMT-COMP-197` | Foreign extension points attached to datatype, encoding, array, fixed-record, variant-record, and enumerator structures. |
| `container-table-and-reference-extension-points` | 7 | `HLA2025-OMT-COMP-008`, `HLA2025-OMT-COMP-035`, `HLA2025-OMT-COMP-223` | Foreign extension points attached to table containers, datatype collections, and reference containers. |

## Reading of the Evidence

- `tests/test_rti1516_2025_validation.py` is the executable anchor for the
  bounded claim. It proves the parser accepts foreign-namespace `xs:any`
  payloads, round-trips them through serialization, and does not collapse them
  into native HLA elements.
- `packages/hla-rti1516e/src/hla/rti1516e/fom.py` is the implementation anchor
  that preserves those foreign XML fragments during parse/serialize handling.
- The finish-line artifacts summarize the same claim at the working-surface
  level, but this note is the requirement-facing explanation for why those 45
  rows are `covered` only as payload-preserving tolerance.

## Explicit Non-Claim

- The repo does not claim that foreign `xs:any` extension payloads become
  repo-native HLA object, interaction, datatype, or runtime semantics.
- The repo does not claim arbitrary third-party extension execution semantics.
