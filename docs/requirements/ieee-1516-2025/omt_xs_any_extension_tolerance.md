# OMT `xs:any` Extension Tolerance

Source: IEEE 1516.2-2025 OMT schema extension points with `xs:any` / `##other`.

This bounded-proof note covers the 45 OMT component rows that permit foreign
namespace extension payloads. The repo evidence supports payload preservation,
schema-tolerant parsing, and serializer round-trip of those foreign XML
fragments. It does not claim arbitrary third-party extension execution
semantics or interpretation as native HLA metadata.

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md`
- owner companion:
  `requirements/2025/canonical_requirements.json`
- backend-resolution companion:
  `requirements/2025/backend_resolution.json`
- primary shard: `unit-fom-tooling`
- widen to: only when a future change deliberately introduces executable
  third-party extension semantics
- typical view tags: `2025-core`, `fom-omt`, `closeout-reporting`

## Final Claim Rule

- these rows are bounded parser or serializer tolerance claims, not arbitrary
  third-party extension execution claims
- count them as foreign-payload preservation, schema-tolerant parse, and
  serializer round-trip evidence only
- do not reinterpret foreign extension payloads as native repo-owned HLA
  metadata or runtime semantics
- only widen these rows beyond tolerance when direct executable semantics
  evidence exists for the exact broader claim

Default final stance:

- this bucket is already in its intended final repo-owned state as a bounded
  OMT extension-tolerance owner surface
- no additional proof is required to keep these rows explicit as payload
  preservation and round-trip tolerance rather than third-party execution
  semantics
- future work is optional and should happen only if the repo deliberately opens
  a broader extension-execution program with its own bounded claim and tests

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
- `requirements/2025/canonical_requirements.json`

## Family Mapping

| Family | Requirement count | Example requirement IDs | Focus |
| --- | ---: | --- | --- |
| `object-model-root-and-identity` | 2 | `HLA2025-OMT-COMP-006`, `HLA2025-OMT-COMP-008` | Foreign extension points around objectModel identity and model-level descriptive metadata. |
| `object-class-and-attribute-extension-points` | 16 | `HLA2025-OMT-COMP-019`, `HLA2025-OMT-COMP-045`, `HLA2025-OMT-COMP-082` | Foreign extension points attached to object classes, attributes, update metadata, and associations. |
| `interaction-class-and-parameter-extension-points` | 8 | `HLA2025-OMT-COMP-102`, `HLA2025-OMT-COMP-110`, `HLA2025-OMT-COMP-134` | Foreign extension points attached to interaction classes, parameters, order metadata, and associations. |
| `datatype-and-encoding-extension-points` | 12 | `HLA2025-OMT-COMP-145`, `HLA2025-OMT-COMP-181`, `HLA2025-OMT-COMP-197` | Foreign extension points attached to datatype, encoding, array, record, and enumerator structures. |
| `container-table-and-reference-extension-points` | 7 | `HLA2025-OMT-COMP-202`, `HLA2025-OMT-COMP-210`, `HLA2025-OMT-COMP-224` | Foreign extension points attached to table containers and top-level reference sections. |

## Full Requirement Ledger

### `object-model-root-and-identity`

`HLA2025-OMT-COMP-006`, `HLA2025-OMT-COMP-008`

### `object-class-and-attribute-extension-points`

`HLA2025-OMT-COMP-019`, `HLA2025-OMT-COMP-021`, `HLA2025-OMT-COMP-027`, `HLA2025-OMT-COMP-035`, `HLA2025-OMT-COMP-039`, `HLA2025-OMT-COMP-045`, `HLA2025-OMT-COMP-047`, `HLA2025-OMT-COMP-056`, `HLA2025-OMT-COMP-057`, `HLA2025-OMT-COMP-059`, `HLA2025-OMT-COMP-067`, `HLA2025-OMT-COMP-068`, `HLA2025-OMT-COMP-070`, `HLA2025-OMT-COMP-077`, `HLA2025-OMT-COMP-081`, `HLA2025-OMT-COMP-082`

### `interaction-class-and-parameter-extension-points`

`HLA2025-OMT-COMP-102`, `HLA2025-OMT-COMP-106`, `HLA2025-OMT-COMP-107`, `HLA2025-OMT-COMP-113`, `HLA2025-OMT-COMP-115`, `HLA2025-OMT-COMP-129`, `HLA2025-OMT-COMP-130`, `HLA2025-OMT-COMP-134`

### `datatype-and-encoding-extension-points`

`HLA2025-OMT-COMP-145`, `HLA2025-OMT-COMP-147`, `HLA2025-OMT-COMP-154`, `HLA2025-OMT-COMP-156`, `HLA2025-OMT-COMP-171`, `HLA2025-OMT-COMP-176`, `HLA2025-OMT-COMP-178`, `HLA2025-OMT-COMP-181`, `HLA2025-OMT-COMP-189`, `HLA2025-OMT-COMP-193`, `HLA2025-OMT-COMP-197`, `HLA2025-OMT-COMP-198`

### `container-table-and-reference-extension-points`

`HLA2025-OMT-COMP-202`, `HLA2025-OMT-COMP-204`, `HLA2025-OMT-COMP-208`, `HLA2025-OMT-COMP-210`, `HLA2025-OMT-COMP-219`, `HLA2025-OMT-COMP-222`, `HLA2025-OMT-COMP-224`

## Reading of the Evidence

- `tests/test_rti1516_2025_validation.py` is the executable anchor for the
  bounded claim. It proves the parser accepts foreign-namespace `xs:any`
  payloads, round-trips them through serialization, and does not collapse them
  into native HLA elements.
- `packages/hla-rti1516e/src/hla/rti1516e/fom.py` is the implementation anchor
  that preserves those foreign XML fragments during parse/serialize handling.
- The canonical requirement catalog records the same bounded claim at
  row granularity, while this note explains why those 45 rows are `covered`
  only as payload-preserving tolerance.

## Explicit Non-Claim

- The repo does not claim that foreign `xs:any` extension payloads become
  repo-native HLA object, interaction, datatype, or runtime semantics.
- The repo does not claim arbitrary third-party extension execution semantics.

## Exit Condition

Treat this bucket as closed for current closeout purposes when all of these are
true:

1. all 45 `xs:any` extension rows remain anchored to this owner doc and the
   canonical row-level requirement catalog
2. the final claim language keeps them explicit as payload-preserving tolerance
   rather than native extension execution semantics
3. no generated packet, audit note, or grouped worklist reclassifies them as
   broad third-party extension behavior claims

Only reopen this bucket if the repo intentionally starts a broader extension
execution or interpretation program.
