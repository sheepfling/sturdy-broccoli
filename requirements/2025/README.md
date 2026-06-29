# HLA 1516.1-2025 requirements and traceability

This directory holds the 2025 edition traceability block, separated from the
2010 requirements corpus in `../`.

Contents:

- `MERGE_REPORT.md`: merge summary for the 2025 spec package union
- `NOTICE.md`: attribution and source notice for the generated package
- `SOURCE_TRACE.md`: Java/C++ method-to-Python source trace
- `STRICT_DOC_INVENTORY.json`: machine-readable inventory of the 2025 strict-doc package
- `STRICT_DOC_REPORT.md`: human-readable summary of the strict-doc package build
- `requirement_completion_backlog.csv`: human-editable completion backlog for
  carry-forward cleanup, modified existing-section requirements, new 2025
  surfaces, retired/mapped 2010 rows, binding-specific rows, and verification
  work
- `differentials/`: 2025-vs-2010 surface differential and code reuse disposition
  packets used to seed carry-forward, modified, new, and retired requirements
- `depth/`: imported requirement-depth expansion packet with 691 source-derived
  rows for FI service depth, SOM/FOM service usage, OMT component/schema
  conformance, validator-negative checks, framework rules, binding/configuration
  deltas, and retired/replacement mapping candidates
- `harmonization/`: reconciled disposition layer over the depth packet, with
  generated disposition projections, FI binding surface accounting, grouped
  backend-resolution companions, coverage rollup, and derived review/reporting
  artifacts

Use this folder when you want to point at "all of the 2025 reqts" or the 2025
source-trace/data block without mixing it into the 2010 requirements ledgers.
The 2010 corpus and mappings live in [`../2010/`](../2010/).

## Canonical 2025 Inventory

Treat this as the single source-side list for the 2025 edition:

- `README.md`: edition front door for the 2025 source-side surface
- `canonical_requirements.json`: canonical row-level requirement truth for 2025
- `backend_resolution.json`: canonical backend-resolution companion for 2025
- `MERGE_REPORT.md`: merge summary for the 2025 spec package union
- `NOTICE.md`: attribution and source notice for the generated package
- `SOURCE_TRACE.md`: Java/C++ method-to-Python source trace
- `STRICT_DOC_INVENTORY.json`: machine-readable strict-doc inventory
- `STRICT_DOC_REPORT.md`: human-readable strict-doc report
- `requirement_completion_backlog.csv`: human-editable completion backlog
- `differentials/README.md`: differential-packet entrypoint
- `differentials/HLA_1516_2025_vs_2010_Differential_Set.csv`: 2025-vs-2010 differential set
- `differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv`: code-reuse disposition guide
- `depth/README.md`: depth expansion packet entrypoint
- `depth/hla_2025_requirement_depth_expansion.csv`: normalized depth expansion rows
- `depth/hla_2025_requirement_depth_expansion.json`: JSON form of the depth rows
- `depth/hla_2025_requirement_depth_expansion_summary.json`: depth summary counts
- `depth/source_manifest.json`: depth source manifest
- `harmonization/README.md`: harmonization packet entrypoint
- `harmonization/hla_2025_requirement_disposition_ledger.csv`: generated or legacy row-level disposition projection
- `harmonization/hla_2025_requirement_disposition_ledger.json`: generated JSON projection of the disposition ledger
- `harmonization/hla_2025_requirement_coverage_rollup.json`: machine-readable coverage rollup
- `harmonization/hla_2025_fi_binding_surface_matrix.csv`: FI binding surface matrix
- `harmonization/hla_2025_pitch_202x_group_resolution.csv`: grouped companion ledger for `pitch_202x_resolution`
- `harmonization/hla_2025_pitch_202x_row_resolution.csv`: row-level companion ledger for conservative Pitch proto HLA 4 / `202X` backend-resolution reading across all 691 harmonization rows
- `harmonization/hla_2025_harmonization_worklist.csv`: generated grouped coordination view with separate canonical-status and backend-resolution columns
- `harmonization/hla_2025_requirement_coverage_closure_report.md`: human-readable closure report
- `harmonization/hla_2025_review_queue.csv`: derived review queue, not a canonical requirement ledger
- `harmonization/source_manifest.json`: harmonization source manifest

Ignore duplicate ` 2.*` copies when reading the edition surface. They are not
the canonical files.

## Reading Order

Use this order:

1. `docs/requirements/ieee-1516-2025/README.md` for the human-facing owner map
2. `canonical_requirements.json` when you need exact row-by-row canonical disposition and evidence paths
3. `backend_resolution.json` when backend or route truth differs from canonical status
4. `harmonization/hla_2025_requirement_coverage_rollup.json` when you need grouped counts or denominator math
5. `harmonization/hla_2025_fi_binding_surface_matrix.csv` and `harmonization/hla_2025_pitch_202x_*_resolution.csv` only when you need a generated backend-specific projection
6. `depth/` and `differentials/` only when you need source derivation history or 2025-vs-2010 change shape
7. `requirement_completion_backlog.csv`, `harmonization/hla_2025_harmonization_worklist.csv`, and `harmonization/hla_2025_review_queue.csv` only for editable coordination or review sequencing, not for requirement truth

Initial executable implementation work is tracked against the differential
packets. The first 2025-native Python RTI slice covers federation execution
listing and federation member discovery in the `shim` backend while preserving
explicit failures for unsupported services.

The `depth/` packet is an import/harmonization candidate, not direct evidence
that all rows are implemented. Use it to split broad 2025 umbrella rows into
reviewable service, schema, validator, and migration-mapping rows before
promoting any claim in the canonical requirement catalog or owner docs.

The `harmonization/` packet is the next reconciliation layer. The canonical
edition truth lives in:

- `canonical_requirements.json`
- `backend_resolution.json`

The older harmonization projections still live in:

- `harmonization/hla_2025_requirement_disposition_ledger.csv`
- `harmonization/hla_2025_requirement_disposition_ledger.json`
- `harmonization/hla_2025_fi_binding_surface_matrix.csv`
- `harmonization/hla_2025_pitch_202x_group_resolution.csv`
- `harmonization/hla_2025_pitch_202x_row_resolution.csv`

The grouped worklist, closure report, and review queue are derived working
surfaces built from the canonical requirement and backend-resolution catalogs
plus the older harmonization projections. They are useful for coordination, but
they are not requirement truth and must not sit in the verification chain.

Current grouped harmonization state:

- `10 covered`
- `2 duplicate/umbrella`
- `1 retired/legacy-only`

Evidence reading by grouped family class:

- the `10 covered` families point directly at executable `tests/` and
  `packages/` anchors in `canonical_requirements.json`
- the `Framework and Rules` umbrella family is intentionally non-standalone:
  its canonical rows resolve through `framework_rules.md`, the generated
  `docs/evidence/spec2025/traceability_matrix.json`, and linked child FI/OMT
  requirement evidence rather than pretending each umbrella row is a separate
  runtime witness
- the `Retired / replacement mapping candidates` family is intentionally an
  exclusion family: its canonical rows resolve through
  `retired_legacy_mapping.md` plus the bounded compatibility marker
  `bounded:migration-compatibility-fixture-if-supported`, not through fake
  direct coverage claims

That means the grouped coordination view is now fully dispositioned.
The remaining 2025 closeout work is no longer stale grouped `planned` or
`partial` buckets. The remaining bounded questions live in:

- explicit umbrella rows that must stay non-standalone
- retired or legacy-only exclusions that must stay explicit
- bounded route/binding claim surfaces that should not be overstated
- row-level supported-scope limits that are intentionally narrower than a
  blanket all-covered IEEE 1516.1-2025 claim

## Final Claim Reading Rule

Use the grouped result carefully:

- grouped `covered` means the grouped bucket has a settled canonical
  disposition
- grouped `duplicate/umbrella` means the bucket is a normalization or parent
  note, not a standalone runtime-proof row
- grouped `retired/legacy-only` means the bucket is an explicit exclusion from
  active 2025 support, not a hidden gap
- backend or route-specific support still belongs in separate
  backend-resolution artifacts or linked owner docs

Do not read the grouped worklist as:

- a blanket all-covered IEEE 1516.1-2025 claim
- proof that every row is a direct executable runtime witness
- proof that hosted FedPro, Java, or C++ are alternate full RTI owners
- a substitute for the canonical requirement catalog, backend-resolution
  companion, or the owner docs under
  `docs/requirements/ieee-1516-2025/`

Current direct-evidence invariant:

- only the `10` framework umbrella rows and `24` retired/legacy-only rows lack
  direct `tests/` or `packages/` anchors in the canonical catalog
- that is intentional and audited
- framework rows must instead carry explicit child-row traceability through
  `docs/evidence/spec2025/traceability_matrix.json`
- retired rows must instead carry explicit exclusion-owner evidence through
  `retired_legacy_mapping.md`

## Canonical Boundary Owners

Use these owner docs when the question is about a bounded or non-claim area
rather than a service row:

| Bucket | Canonical owner doc | Meaning |
| --- | --- | --- |
| framework umbrella rows | `docs/requirements/ieee-1516-2025/framework_rules.md` | umbrella rules stay parent notes, not one-row runtime claims |
| callback/configuration/binding delta umbrellas | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | delta umbrellas stay normalization aids, not standalone proof rows |
| binding and hosted-route boundaries | `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md` | Java/C++ and hosted FedPro stay bounded adaptation or transport evidence over the main runtime |
| Pitch proto HLA 4 / `202X` backend-resolution lane | `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md` | vendor-branded route naming stays a backend-resolution story, not canonical status |
| retired and legacy-only rows | `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md` | retired rows stay explicit exclusions unless a compatibility program is added |
| exclusion perimeter around the main Python lane | `docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md` | collects the current non-claim perimeter around `python1516_2025` |
| OMT `xs:any` extension tolerance | `docs/requirements/ieee-1516-2025/omt.md` | canonical OMT owner surface; use `omt_xs_any_extension_tolerance.md` as the bounded evidence note for foreign extension payload round-trip tolerance rather than arbitrary runtime semantics |

Keep canonical closeout and backend support separate in this source-side
surface:

- use `canonical_requirements.json` for row-level canonical requirement closure
- use `backend_resolution.json` for canonical backend and route resolution
- keep backend or route-specific support in dedicated backend-resolution
  artifacts and linked owner docs
- use the grouped worklist only as a coordination summary over those canonical
  surfaces
- use the worklist `pitch_202x_resolution` field only as a grouped view when
  the vendor-branded proto HLA 4 / `202X` surface needs a high-level summary
- use `harmonization/hla_2025_pitch_202x_row_resolution.csv` when you need the
  same backend-resolution split at per-row granularity rather than grouped
  bucket granularity
- for the current concrete bounded packet behind that field, read
  `artifacts/pitch_202x_micro_certification/` and
  `packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md`
- for the canonical owner doc behind that field, read
  `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`

Reading rule:

1. use this README for the source-side inventory and canonical-source reading order
2. use `docs/requirements/ieee-1516-2025/README.md` for the full human-facing
   owner map
3. open the exact owner doc above before widening to route-parity summaries or
   any generated closeout/reporting surface
