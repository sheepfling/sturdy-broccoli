# RPR Type Normalization Notes

Use this page when you need one answer to two questions:

- where do the 2010 and 2025 parser paths actually differ in this repo?
- what should RPR publish differently so generic HLA tooling does not need
  family-labeled datatype aliases?

## Parser Split

The repo does not maintain separate XML datatype parsers for `2010` and `2025`.

Current structure:

- shared OMT parser and datatype model:
  - `packages/hla-rti-core/src/hla/fom/__init__.py`
- 2025 semantic validator:
  - `packages/hla-rti-core/src/hla/fom/validation.py`
- 2010 conformance assessment:
  - consumed through the shared `hla.fom` catalog and repo verification flows

Practical meaning:

- both edition lanes load the same XML into the same repo-native datatype
  catalog
- the parser is where source-dialect normalization belongs
- edition-specific differences should primarily live in validation rules,
  schema selection, and runtime/binding behavior

## Current RPR Handling

Published RPR packets in the exercised SISO corpus use source labels such as:

- `RPRnullTerminatedArray`
- `RPRlengthlessArray`
- `RPRpaddingTo32Array`
- `RPRpaddingTo64Array`

The parser currently absorbs those labels and maps them into canonical internal
structural kinds:

- `RPRnullTerminatedArray` -> `null-terminated-array`
- `RPRlengthlessArray` -> `lengthless-array`
- `RPRpaddingTo32Array` -> `padding-to-32-bit-boundary-array`
- `RPRpaddingTo64Array` -> `padding-to-64-bit-boundary-array`

The original XML label is preserved as `source_encoding` only for:

- traceability
- round-trip serialization
- standards-facing audit/reporting

The runtime datatype engine should branch on canonical semantics, not on RPR
family names.

## Suggested RPR Type Changes

These are the changes we would want in a future cleaner RPR publication so the
repo would not need family-labeled datatype aliases at parse time.

### Arrays

1. `RPRnullTerminatedArray`

- current intent:
  - array terminated by a sentinel `0x00`
- suggested standards change:
  - define a generic null-terminated array encoding in the standard encoding
    vocabulary, or explicitly define this as a standard structural pattern
    rather than an RPR-branded label

2. `RPRlengthlessArray`

- current intent:
  - repeated elements with no inline count field; length derived from enclosing
    context or message extent
- suggested standards change:
  - define this as a generic “externally bounded array” structural form, or
    restate the field as standard `HLAfixedArray` / `HLAvariableArray` when the
    bound can be made explicit

3. `RPRpaddingTo32Array`

- current intent:
  - zero to three octets used only to reach the next 32-bit boundary
- suggested standards change:
  - treat this as generic alignment padding, not as an array datatype with RPR
    branding
  - if the standard does not support explicit alignment metadata, document it
    as a structural padding rule attached to enclosing records

4. `RPRpaddingTo64Array`

- current intent:
  - zero to seven octets used only to reach the next 64-bit boundary
- suggested standards change:
  - same as `RPRpaddingTo32Array`: generic alignment rule, not family-labeled
    datatype vocabulary

### Variant Records

1. `RPRextendedVariantRecord`

- current intent:
  - variant-record-like structure with RPR-specific extension semantics
- suggested standards change:
  - map this onto a generic variant record capability, ideally using standard
    OMT naming rather than RPR-family branding
  - if the semantics truly exceed plain `HLAvariantRecord`, document the delta
    as a generic extension concept instead of an RPR-specific one

## What RPR Could Publish Instead

The clean long-term shape would be:

- standard names where standard names are sufficient:
  - `HLAfixedArray`
  - `HLAvariableArray`
  - `HLAfixedRecord`
  - `HLAvariantRecord`
- generic extension names where the standard needs more vocabulary:
  - null-terminated array
  - externally bounded / lengthless array
  - alignment padding
  - extendable variant record

The key point is not that every construct must collapse into today's standard
names. The key point is that the names should describe generic structure, not
family ownership.

## Repo Guidance

When adding support for more RPR packets:

- parser edge may accept RPR-family labels
- shared datatype engine should normalize them immediately
- 2010 and 2025 report surfaces should call out the source label separately
- new RPR dialect pressure belongs in `docs/rpr_siso_feedback_log.md`

## Related Files

- `packages/hla-rti-core/src/hla/fom/__init__.py`
- `packages/hla-rti-core/src/hla/fom/validation.py`
- `docs/rpr_siso_feedback_log.md`
- `docs/fom_reading_map.md`
