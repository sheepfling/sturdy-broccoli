# RPR SISO Feedback Log

Use this document as the standing issues and complaints log for the RPR family
so concerns can be routed back to SISO instead of being normalized into repo
code as if they were uncontroversial.

Companion design note:

- [`rpr_type_normalization_notes.md`](rpr_type_normalization_notes.md)

This is not a bug list for our implementation.

It is the standards-facing log for:

- confusing or underspecified RPR constructs
- source naming that leaks family branding into generic tooling pressure
- edition-shape ambiguities
- interoperability pain points discovered while exercising the SISO packets

## Scope

In scope:

- RPR 2.0 material used through the Link 16 integrated family
- RPR 3.0 Annex A normative family
- RPR 3.0 merged informative 1516-2010 packet
- adjacent RPR-derived structures that affect generic FOM tooling

Out of scope:

- ordinary repo bugs with no standards implication
- vendor runtime failures unless they point to an RPR source-model problem
- Space FOM and other SISO family issues unless they are directly tied to RPR

## How To Use This Log

For each item, capture:

- `id`
- `status`: `open` | `sent-to-siso` | `answered` | `closed-local-workaround`
- `severity`: `low` | `medium` | `high`
- `area`: `naming` | `encoding` | `edition` | `load-order` | `runtime` | `documentation`
- `affected sources`
- `complaint`
- `why this is a standards-facing issue`
- `local repo handling`
- `desired SISO clarification or change`

The rule is:

- log the complaint here first
- keep code changes generic where possible
- do not let repeated workarounds silently redefine the standard boundary

## Open Items

### RPR-001

- status: `open`
- severity: `high`
- area: `encoding`
- affected sources:
  - `RPR-Base_v2.0.xml`
  - `RPR-Base_v3.0.xml`
  - merged RPR 3.0 informative 1516-2010 packet
- complaint:
  - RPR user tags rely on family-labeled array or record encoding conventions
    such as `RPRnullTerminatedArray`, `RPRlengthlessArray`, and
    `RPRUserDefinedTag`.
- why this is a standards-facing issue:
  - these constructs are legal in the exercised RPR packets, but their naming
    pushes family-specific vocabulary directly into generic datatype tooling.
  - this creates avoidable friction for parsers and validators that otherwise
    operate on structural OMT categories.
- local repo handling:
  - generic internal canonicalization now maps source labels to generic array
    encoding kinds such as `null-terminated-array` and `lengthless-array`.
  - original source labels are preserved as source metadata, not control flow.
- desired SISO clarification or change:
  - clarify whether these encodings are intended as family-local aliases over
    generic OMT patterns.
  - publish recommended generic semantics for implementers so tooling does not
    need to branch on RPR branding.
  - preferred direction in this repo:
    - null-terminated arrays should be described generically
    - lengthless arrays should be described generically
    - alignment padding should not be modeled as RPR-family array names

### RPR-001A

- status: `open`
- severity: `high`
- area: `naming`
- affected sources:
  - `RPRnullTerminatedArray`
  - `RPRlengthlessArray`
  - `RPRpaddingTo32Array`
  - `RPRpaddingTo64Array`
  - `RPRextendedVariantRecord`
- complaint:
  - RPR uses family-owned datatype names for structural concepts that should be
    generic implementation vocabulary.
- why this is a standards-facing issue:
  - the problem is not only support burden. The naming itself pushes
    implementers toward family-name branching in generic OMT code.
- local repo handling:
  - parser-side canonicalization converts source labels into generic internal
    structural kinds while preserving the original source name for reporting and
    round-trip output.
- desired SISO clarification or change:
  - publish datatype names that describe generic structure rather than RPR
    family ownership.
  - see [`rpr_type_normalization_notes.md`](rpr_type_normalization_notes.md)
    for the concrete substitutions we recommend.

### RPR-002

- status: `open`
- severity: `high`
- area: `documentation`
- affected sources:
  - `RPRUserDefinedTag` in RPR 2.0 and RPR 3.0 sources
- complaint:
  - user-supplied tags are runtime-critical, but the practical encoding shape
    is not obvious from casual inspection and is easy for implementers to get
    wrong.
- why this is a standards-facing issue:
  - interoperability depends on these bytes being shaped correctly for updates
    and interactions.
  - implementers can mistakenly treat the tag as opaque free text when the
    packet expects a structured encoding.
- local repo handling:
  - repo tests now validate the actual encoded tag forms exercised by RPR 2.0
    and RPR 3.0 runtime scenarios.
- desired SISO clarification or change:
  - provide a shorter implementer-facing explanation and concrete examples for
    RPR tag encoding requirements in both edition-relevant source lanes.

### RPR-003

- status: `open`
- severity: `medium`
- area: `edition`
- affected sources:
  - `rpr3-annex-a-normative`
  - `rpr3-merged-informative-1516-2010`
- complaint:
  - the runtime family requirement "RPR on both editions" does not map to one
    single packet shape; different edition lanes currently need different RPR
    source packets.
- why this is a standards-facing issue:
  - users can reasonably assume "RPR 3.0" names one directly portable runtime
    packet, but the practical exercised sources differ by edition and purpose.
- local repo handling:
  - the runtime showcase is explicit:
    - `2010` uses `rpr3-merged-informative-1516-2010`
    - `2025` uses `rpr3-annex-a-normative`
- desired SISO clarification or change:
  - document the intended edition/runtime portability story more plainly:
    which packets are normative runtime baselines, which are stress artifacts,
    and which are compatibility-oriented merged packets.

### RPR-004

- status: `open`
- severity: `medium`
- area: `load-order`
- affected sources:
  - RPR ordered family packets
  - Link 16 integrated RPR 2.0 family
- complaint:
  - family load order is operationally important but easy to lose once packets
    are copied, merged, or repackaged.
- why this is a standards-facing issue:
  - many user failures will look like parser or RTI bugs when the actual issue
    is family assembly order or missing companion modules.
- local repo handling:
  - repo inventory and showcase tooling preserve ordered-family load sets
    explicitly.
- desired SISO clarification or change:
  - provide a stronger machine-readable or clearly bounded load-order contract
    for modular RPR families and extension slices like the Link 16 integration.

## Closed Or Mitigated Locally

### RPR-LOCAL-001

- status: `closed-local-workaround`
- severity: `medium`
- area: `encoding`
- affected sources:
  - `RPRnullTerminatedArray`
  - `RPRlengthlessArray`
- complaint:
  - generic datatype code should not branch on raw RPR family names.
- why this is a standards-facing issue:
  - branding leakage in the core tooling path makes future interoperability
    work more expensive and less principled.
- local repo handling:
  - resolved by canonical internal encoding kinds plus `source_encoding`
    preservation.
- desired SISO clarification or change:
  - same as `RPR-001`: make the generic structural intent of these encodings
    easier for tool builders to implement without family-name branching.

## Submission Queue

When an item is ready to send to SISO, copy it here with:

- date prepared
- source contact
- exact packet/version references
- minimal repro or concrete example
- requested clarification text

This keeps the repo history distinct from the external standards-feedback trail.
