# Plans

This family holds the active roadmap items for the HLA 2010 project.

Canonical order:

1. foundation plan
2. parity or extraction plan
3. validation or closure plan

Internal index:

- [roadmap_index.md](roadmap_index.md)

Current plans:

- [PLN-001_hla_2010_foundation.md](PLN-001_hla_2010_foundation.md)
- [PLN-002_certi_parity_and_runtime_plan.md](PLN-002_certi_parity_and_runtime_plan.md)
- [PLN-003_requirements_authoring_plan.md](PLN-003_requirements_authoring_plan.md)
- [PLN-004_python_rti_100_percent_compliance_plan.md](PLN-004_python_rti_100_percent_compliance_plan.md)
- [PLN-005_requirements_shards_views_and_verification_plan.md](PLN-005_requirements_shards_views_and_verification_plan.md): canonical shard-versus-view model, backend-resolution separation, and verification-flow plan for both editions
- [PLN-006_normalized_requirement_row_model_execution_plan.md](PLN-006_normalized_requirement_row_model_execution_plan.md): shared typed model and canonical projection plan for both editions
- [PLN-007_2010_truth_surface_normalization_plan.md](PLN-007_2010_truth_surface_normalization_plan.md): execution plan for reducing `2010 / 1516e` to one leaf-oriented canonical requirement list plus one backend-resolution companion and demoting old drift surfaces
- [2025_python_rti_100_percent_worklist.md](2025_python_rti_100_percent_worklist.md): concrete 2025 denominator rule plus the exact 46 non-covered rows that block literal `691 / 691 covered`
- [2025_python_rti_umbrella_decomposition_worklist.md](2025_python_rti_umbrella_decomposition_worklist.md): exact child-row, shard-owner, and promotion criteria for the 22 remaining 2025 umbrella rows
- [2010_python_rti_bounded_family_execution_worklist.md](2010_python_rti_bounded_family_execution_worklist.md): exact owner-doc, companion-ledger, shard-owner, and tightening criteria for the remaining bounded 2010 families
- [imported_requirements_backlog_v1_0.md](imported_requirements_backlog_v1_0.md): generated repo-native work queues from the harmonized requirements ledgers
- [requirements_finish_line.md](requirements_finish_line.md): the handoff note for finishing remaining requirement rows without overclaiming
- [requirements_remaining_closure.md](requirements_remaining_closure.md): concrete remaining 2010/2025 proof debt, the canonical shard-versus-view matrix model, and the preferred closeout-table column shape
- [requirements_completion_audit.md](requirements_completion_audit.md): current-state audit of what still blocks an honest full requirements-complete claim
- [requirements_gap_register.md](requirements_gap_register.md): exact missing-proof table for each still-open cross-edition requirement bucket
- [requirements_execution_queue.md](requirements_execution_queue.md): prioritized shard-first queue for closing the still-open requirement buckets
- [../verification/requirement_compliance_exports.md](../verification/requirement_compliance_exports.md): CSV/XLSX export contract for the boss-facing `2010 / 1516e` and `2025 / 1516_2025` backend-compliance packets
- [spec2025_finish_line.md](spec2025_finish_line.md): generated 2025 finish-line summary packet
- [spec2025_finish_line_snapshot.json](spec2025_finish_line_snapshot.json): generated 2025 finish-line machine-readable snapshot
- [spec2025_route_parity_matrix.md](spec2025_route_parity_matrix.md): generated 2025 route-parity markdown view
- [2025_python_rti_backend_audit.md](2025_python_rti_backend_audit.md): generated backend-audit packet for the current 2025 Python RTI lane
- [2025_requirement_by_requirement_audit.md](2025_requirement_by_requirement_audit.md): generated requirement-by-requirement audit packet

Reading rule for closeout work:

1. open the edition requirement front door first, then the canonical requirement catalog and backend-resolution companion
2. use `requirements_completion_audit.md` for the truthful downstream "are we done?" answer
3. use `requirements_remaining_closure.md` for the exact bucket shape and shard/view ownership model
4. use `PLN-005_requirements_shards_views_and_verification_plan.md` when you need the canonical shard-versus-view execution model
5. use `requirements_gap_register.md` and `requirements_execution_queue.md` for the next runnable closeout slices
6. use `requirement_compliance_exports.md` only when you need presentation packets, not canonical requirement ownership

Closeout packets in this directory are downstream reporting and sequencing
surfaces. They do not replace `canonical_requirements.json`,
`backend_resolution.json`, bounded proof notes, or shard-owned executable
evidence as requirement truth.
