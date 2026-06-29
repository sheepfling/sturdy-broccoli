# HLA 1516-2025 requirement harmonization packet

This directory carries generated 2025 harmonization projections derived from
the 691-row requirement-depth expansion in `../depth/` plus the canonical
requirement and backend-resolution catalogs.

Canonical rule:

- the primary 2025 requirement truth is `../canonical_requirements.json`
- the matching canonical CSV export is `../canonical_requirements.csv`
- the primary backend and route companion truth is `../backend_resolution.json`
- the matching canonical CSV export is `../backend_resolution.csv`
- this directory is a generated or review-facing projection layer over those
  canonical edition surfaces, not the first truth surface to read

The files remain reviewable harmonization artifacts rather than blanket
conformance claims. They are synchronized downstream projections, and any row
promotion to `covered` must already be reflected in the canonical requirement
catalog with direct repo evidence and executable anchors reconciled:

- `hla_2025_requirement_disposition_ledger.csv` and `.json`: generated
  row-shaped closeout projection with disposition, priority, closure wave,
  binding/source trace fields, evidence path suggestions, closure tasks, and
  promotion rules.
- `hla_2025_fi_binding_surface_matrix.csv`: FI service rows with Java, C++,
  and FedPro official surface accounting.
- `hla_2025_harmonization_worklist.csv`: grouped execution waves by area,
  service group, canonical disposition, `python_runtime_resolution`,
  `java_cpp_binding_resolution`, `hosted_fedpro_resolution`,
  `pitch_202x_resolution`, and backend-resolution references.
- `hla_2025_pitch_202x_group_resolution.csv`: generated grouped companion
  projection for the Pitch proto HLA 4 / `202X` backend-resolution field.
- `hla_2025_pitch_202x_row_resolution.csv`: generated row-level companion
  projection for the same Pitch proto HLA 4 / `202X` backend-resolution
  reading across all 691 harmonization rows.
- `hla_2025_review_queue.csv`: sorted row queue for implementation and evidence
  review.
- `hla_2025_requirement_coverage_rollup.json`: machine-readable counts by
  disposition, priority, area, closure wave, and FI binding surface status.
- `hla_2025_requirement_coverage_closure_report.md`: human-readable summary and
  promotion guardrails.
- `source_manifest.json`: source file checksums for the imported packet.

Rows move to `covered` only after repo evidence anchors, executable tests or
fixtures, and unsupported-boundary decisions where applicable are recorded.

Verification rule:

- `../canonical_requirements.json` is the only row-level requirement
  truth for this packet
- treat `../canonical_requirements.json` and `../canonical_requirements.csv`
  as the same row-level requirement truth surface in two encodings; they are
  the only row-level requirement truth for this packet
- `../backend_resolution.json` is the only backend- and route-resolution
  truth for this packet
- treat `../backend_resolution.json` and `../backend_resolution.csv` as the
  same backend- and route-resolution truth surface in two encodings; they are
  the only backend- and route-resolution truth for this packet
- treat every file in this directory as a downstream grouped, row-shaped, or
  review-sequencing projection over those canonical surfaces

Reading rule for the grouped worklist:

- `canonical_disposition` answers whether the grouped requirement bucket is
  still `planned`, `partial`, `covered`, `duplicate/umbrella`, or
  `retired/legacy-only`
- backend-specific support stays in the explicit backend-resolution columns and
  linked owner artifacts such as the FI binding surface matrix, harmonization
  ledger, or bounded proof notes
- when a vendor uses alternate branding such as Pitch proto HLA 4 / `202X`,
  record that in the backend-resolution notes or linked owner docs rather than
  inferring parity from the vendor package name alone
- `pitch_202x_resolution` is the grouped field for that vendor-branded surface;
  it records support, boundedness, or non-applicability without changing the
  canonical requirement disposition
- `hla_2025_pitch_202x_row_resolution.csv` carries the same split at row level:
  FI rows are only bounded overlap notes, callback rows stay umbrella-owned,
  SOM/FOM usage rows stay mirrored-FI cross-checks, and OMT/framework/legacy
  rows stay explicitly non-owning for Pitch runtime claims
- the current concrete packet for that field is
  `artifacts/pitch_202x_micro_certification/` plus
  `packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md`
- the canonical owner doc for that field is
  `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`

Current grouped worklist state:

- `10 covered`
- `2 duplicate/umbrella`
- `1 retired/legacy-only`

Practical reading rule:

- start from `../canonical_requirements.json` for exact row-level canonical
  status, owner doc, shard, command, and evidence references
- start from `../backend_resolution.json` when backend or route support differs
  from canonical requirement status
- do not treat this grouped packet as an open backlog of missing runtime proof
- treat it as a synchronized grouped projection over the canonical requirement
  catalog and backend-resolution companion
- when the repo still is not “done,” the blocker is now usually one of:
  - row-level bounded supported-scope language
  - umbrella-row final-claim hygiene
  - retired/legacy-only exclusion discipline
  - bounded route/binding claims that should not be widened without stronger proof
