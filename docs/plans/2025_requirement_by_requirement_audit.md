# 2025 Requirement-By-Requirement Audit

This note is the row-level audit companion to the 691-row harmonization ledger in
`requirements/2025/harmonization/`.

For the current umbrella-row execution surface, use
[`2025_python_rti_umbrella_decomposition_worklist.md`](2025_python_rti_umbrella_decomposition_worklist.md).

It answers a narrow question:

Does the repo now have an explicit requirement-by-requirement audit across the
tracked 2025 requirement universe?

## Short Answer

Yes.

The repo now has a row-level requirement-by-requirement disposition audit across
all 691 tracked 2025 rows.

That does not mean all 691 rows are delivered support.

It means every tracked row is now explicitly dispositioned as one of:

- `covered`
- `retired/legacy-only`
- `duplicate/umbrella`

## Current Audit Result

- Total tracked rows: `691`
- Covered rows: `645`
- Unsupported-boundary rows: `0`
- Retired/legacy-only rows: `24`
- Duplicate/umbrella rows: `22`

Area closure is currently:

- Federate Interface service catalog: `covered=196`
- SOM/FOM service-usage requirements: `covered=196`
- OMT component-level conformance: `covered=224`
- OMT validator-negative conformance: `covered=29`
- Framework and Rules: `duplicate/umbrella=10`
- Callback/configuration/binding deltas: `duplicate/umbrella=12`
- Retired / replacement mapping candidates: `retired/legacy-only=24`

## Recommended 100 Percent Metric Rule

Use two separate percentages:

1. `100% dispositioned` across all `691` tracked rows
2. `100% covered` across the active normative non-retired non-umbrella rows

That active denominator is currently:

- `691` total tracked rows
- minus `22` `duplicate/umbrella` rows
- minus `24` `retired/legacy-only` rows
- equals `645` active normative non-retired non-umbrella rows

Current result on that denominator:

- `645 / 645 = 100% covered` on active normative non-retired non-umbrella rows

Do not restate that as `691 / 691 covered`.
The remaining `46` rows are explicit owner-note classes, not hidden gaps.

## What This Audit Proves

The repo no longer lacks a row-level 2025 audit.

More specifically, it proves:

- every tracked 2025 row has an explicit harmonization disposition
- every covered row has a suggested repo evidence path
- no tracked row remains hidden in an implicit unsupported bucket
- framework and delta umbrella rows are kept separate from delivered support
- legacy and retired rows are excluded explicitly instead of being silently mixed
  into coverage claims

This closes the missing-audit gap.

It also strengthens the bounded main-implementation claim for
`hla-backend-python1516-2025`: the repo now has a row-level ledger behind the
current Python 2025 RTI lane rather than only broad slice summaries, while
`hla-backend-shim` stays in a compatibility-wrapper role instead of becoming a
second implementation owner.

Read that backend-resolution split explicitly:

- `hla-backend-python1516-2025` remains the primary direct 2025 runtime owner
- Java and C++ standard-shim routes remain wrapper-only capability surfaces
  over that runtime lane, not alternate RTI owners
- hosted FedPro evidence remains a bounded route surface over the same runtime
  lane, not a second 2025 implementation owner
- any Pitch proto HLA 4 / `202X` overlap remains explicit vendor-resolution
  context rather than inferred closure of the grouped 2025 rows

For the `22` remaining `duplicate/umbrella` rows, this audit now has an
explicit child-owner and shard-owner companion:

- framework umbrella rows remain owned by
  [`../requirements/ieee-1516-2025/framework_rules.md`](../requirements/ieee-1516-2025/framework_rules.md)
- callback/configuration/binding umbrella rows remain owned by
  [`../requirements/ieee-1516-2025/callback_binding_deltas.md`](../requirements/ieee-1516-2025/callback_binding_deltas.md)
- exact child-row links, primary shard owners, and direct-promotion criteria
  now live in
  [`2025_python_rti_umbrella_decomposition_worklist.md`](2025_python_rti_umbrella_decomposition_worklist.md)
- canonical shard ownership terms live in
  [`../verification/shard_registry.md`](../verification/shard_registry.md)

## What This Audit Does Not Prove

This is still not a full unconditional 2025 conformance pass.

The row-level audit remains bounded because:

- `24` rows are retired or legacy-only exclusions
- `22` rows are umbrella normalization rows rather than direct one-row
  conformance assertions
- many covered rows still inherit bounded supported-scope language from broader
  executable slices instead of standalone exhaustive clause-by-clause proof
- Java and C++ bindings remain artifact/runtime-capability bounded
- hosted FedPro remains a bounded runtime slice rather than a full RTI
  semantics or MOM action/request conformance pass
- Pitch proto HLA 4 / `202X` comparison material remains vendor-resolution
  context, not proof that the grouped 2025 Python RTI rows have a second
  independent backend owner

Read the umbrella class precisely:

- the `22` umbrella rows are not missing proof-owner rows
- they are explicit parent or normalization rows whose child proof already
  exists
- the remaining decision is whether to leave them outside the direct-support
  denominator or deliberately replace them with narrower direct executable
  claims

## Working Conclusion

The correct statement now is:

- the repo has a real requirement-by-requirement audit across the tracked 2025
  universe
- that audit supports a bounded working-surface claim
- that audit supports `100% covered` on the active normative non-retired
  non-umbrella denominator
- that audit does not by itself justify a full all-covered IEEE 1516.1-2025
  conformance claim
- the remaining question is no longer whether a row-level audit exists, but
  whether enough of the bounded rows can be converted into cleaner standalone
  proof to justify a stronger architecture and conformance claim

Recent movement:

- `HLA2025-OMT-COMP-041` and `HLA2025-OMT-COMP-042` moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-dimension-metadata-roundtrip` parser/serializer proof.
- `HLA2025-OMT-COMP-192` and `HLA2025-OMT-COMP-196` moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-component-metadata-roundtrip` logical-time semantics proof.
- `HLA2025-OMT-COMP-200` and `HLA2025-OMT-COMP-201` moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-switch-and-transport-subset` transportation reliable/semantics
  metadata proof.
- `HLA2025-OMT-COMP-207` moved from an explicit unsupported-boundary row to a
  covered row through the `2025-omt-switch-and-transport-subset` update-rate
  semantics metadata proof.
- `HLA2025-OMT-COMP-011`, `HLA2025-OMT-COMP-012`,
  `HLA2025-OMT-COMP-014`, `HLA2025-OMT-COMP-015`,
  `HLA2025-OMT-COMP-017`, and `HLA2025-OMT-COMP-018` moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-attribute-metadata-roundtrip` proof.
- `HLA2025-OMT-COMP-074`, `HLA2025-OMT-COMP-079`,
  `HLA2025-OMT-COMP-080`, `HLA2025-OMT-COMP-109`,
  `HLA2025-OMT-COMP-114`, and `HLA2025-OMT-COMP-133` moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-class-parameter-metadata-roundtrip` proof.
- `HLA2025-OMT-COMP-166`, `HLA2025-OMT-COMP-168`,
  `HLA2025-OMT-COMP-169`, and `HLA2025-OMT-COMP-170` moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-switch-and-transport-subset` proof for additional 2025 switch
  metadata preservation.
- `HLA2025-OMT-COMP-037`, `HLA2025-OMT-COMP-038`,
  `HLA2025-OMT-COMP-040`, `HLA2025-OMT-COMP-043`, and
  `HLA2025-OMT-COMP-044` moved from explicit unsupported-boundary rows to
  covered rows through the `2025-omt-dimension-metadata-roundtrip` proof for
  2025 dimension input/output metadata preservation.
- `HLA2025-OMT-COMP-083` moved from an explicit unsupported-boundary row to a
  covered row through the `2025-omt-extended-supported-subset` proof for
  keyword taxonomy metadata preservation.
- `HLA2025-OMT-COMP-048`, `HLA2025-OMT-COMP-049`,
  `HLA2025-OMT-COMP-075`, `HLA2025-OMT-COMP-076`,
  `HLA2025-OMT-COMP-110`, `HLA2025-OMT-COMP-111`, and
  `HLA2025-OMT-COMP-112` moved from explicit unsupported-boundary rows to
  covered rows through the `2025-omt-association-metadata-roundtrip` proof for
  object directedInteraction name/sharing and object/interaction dimension
  association metadata preservation.
- The remaining 45 OMT `xs:any` extension-point rows moved from explicit
  unsupported-boundary rows to covered rows through the
  `2025-omt-xs-any-extension-tolerance` proof: the parser accepts foreign
  namespace extension elements, preserves their XML payloads across
  parse/serialize/parse round-trip, and isolates them as non-native metadata
  instead of accidentally interpreting them as standard HLA content.
- Arbitrary third-party extension execution semantics remain outside the
  repo-native runtime semantics claim.
