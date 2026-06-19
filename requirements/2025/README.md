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
