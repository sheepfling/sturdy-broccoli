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
- `harmonization/`: imported provisional disposition layer over the depth packet,
  with row-level disposition, FI binding surface accounting, review queue,
  execution worklist, coverage rollup, and promotion guardrails

Use this folder when you want to point at "all of the 2025 reqts" or the 2025
source-trace/data block without mixing it into the 2010 requirements ledgers.
The 2010 corpus and mappings live in [`../2010/`](../2010/).

## Canonical 2025 Inventory

Treat this as the single source-side list for the 2025 edition:

- `README.md`: edition front door for the 2025 source-side surface
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
- `harmonization/hla_2025_fi_binding_surface_matrix.csv`: FI binding surface matrix
- `harmonization/hla_2025_harmonization_worklist.csv`: grouped harmonization worklist
- `harmonization/hla_2025_requirement_coverage_closure_report.md`: human-readable closure report
- `harmonization/hla_2025_requirement_coverage_rollup.json`: machine-readable coverage rollup
- `harmonization/hla_2025_requirement_disposition_ledger.csv`: row-level disposition ledger
- `harmonization/hla_2025_requirement_disposition_ledger.json`: JSON form of the disposition ledger
- `harmonization/hla_2025_review_queue.csv`: sorted review queue
- `harmonization/source_manifest.json`: harmonization source manifest

Ignore duplicate ` 2.*` copies when reading the edition surface. They are not
the canonical files.

## Reading Order

Use this order:

1. `requirement_completion_backlog.csv` for the editable closeout view
2. `differentials/` when you need 2025-vs-2010 change shape
3. `depth/` when you need expanded source-derived rows
4. `harmonization/` when you need reviewed dispositions and closure status

Initial executable implementation work is tracked against the differential
packets. The first 2025-native Python RTI slice covers federation execution
listing and federation member discovery in the `shim` backend while preserving
explicit failures for unsupported services.

The `depth/` packet is an import/harmonization candidate, not direct evidence
that all rows are implemented. Use it to split broad 2025 umbrella rows into
reviewable service, schema, validator, and migration-mapping rows before
promoting any claim in the completion backlog or finish-line report.

The `harmonization/` packet is the next review layer. It assigns row-level
dispositions and closure tasks to the depth rows, and may promote rows to
`covered` once concrete repo evidence and executable test or fixture anchors are
reconciled into the packet.
