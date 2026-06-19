# HLA 1516-2025 requirement harmonization packet

This directory carries a provisional disposition layer over the 691-row
requirement-depth expansion in `../depth/`.

The files are review inputs, not implementation-proof claims:

- `hla_2025_requirement_disposition_ledger.csv` and `.json`: row-level
  disposition, priority, closure wave, binding/source trace fields, evidence
  path suggestions, closure tasks, and promotion rules.
- `hla_2025_fi_binding_surface_matrix.csv`: FI service rows with Java, C++,
  and FedPro official surface accounting.
- `hla_2025_harmonization_worklist.csv`: grouped execution waves by area,
  service group, disposition, and priority.
- `hla_2025_review_queue.csv`: sorted row queue for implementation and evidence
  review.
- `hla_2025_requirement_coverage_rollup.json`: machine-readable counts by
  disposition, priority, area, closure wave, and FI binding surface status.
- `hla_2025_requirement_coverage_closure_report.md`: human-readable summary and
  promotion guardrails.
- `source_manifest.json`: source file checksums for the imported packet.

Rows should only move to `covered` after repo evidence anchors, executable tests
or fixtures, and unsupported-boundary decisions are recorded.
