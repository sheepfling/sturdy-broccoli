# Spec Reading Map

Use this page when the question is:

- where should I start reading standards-facing material?
- how do requirement notes, verification docs, and generated evidence fit together?
- which document should I open first for a claim or proof question?

Do not start with a random proof note.
Start from the claim map, then move toward executable or generated evidence.

## Start Here

Read these in order:

1. [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) or [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)
2. [`verification/README.md`](verification/README.md)
3. one focused proof note or requirement ledger for the family you care about
4. the matching executable or generated evidence doc

## By Question

| If the question is... | Start here | Then read |
| --- | --- | --- |
| where is the 2010 requirement source surface? | [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) | [`../requirements/2010/README.md`](../requirements/2010/README.md), [`verification/README.md`](verification/README.md) |
| what is the canonical 2010 owner for a partial or mixed-backend bucket? | [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) | [`requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`](requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md), [`verification/README.md`](verification/README.md) |
| what does the main 2025 runtime claim? | [`requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md`](requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`verification/time_model_compliance.md`](verification/time_model_compliance.md) |
| where is the main 2025 requirement front door? | [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md) | [`../requirements/2025/README.md`](../requirements/2025/README.md), [`verification/README.md`](verification/README.md) |
| what is the declaration-management proof boundary? | [`requirements/ieee-1516-2025/declaration_management_bounded_proof.md`](requirements/ieee-1516-2025/declaration_management_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`test_surface.md`](test_surface.md) |
| what is the object-management proof boundary? | [`requirements/ieee-1516-2025/object_management_bounded_proof.md`](requirements/ieee-1516-2025/object_management_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`test_surface.md`](test_surface.md) |
| what is the ownership proof boundary? | [`requirements/ieee-1516-2025/ownership_management_bounded_proof.md`](requirements/ieee-1516-2025/ownership_management_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`test_surface.md`](test_surface.md) |
| what is the DDM proof boundary? | [`requirements/ieee-1516-2025/ddm_bounded_proof.md`](requirements/ieee-1516-2025/ddm_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`test_surface.md`](test_surface.md) |
| what is the support-services proof boundary? | [`requirements/ieee-1516-2025/support_services_bounded_proof.md`](requirements/ieee-1516-2025/support_services_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`test_surface.md`](test_surface.md) |
| what is the FOM-backed scenario proof boundary? | [`requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md`](requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md) | [`verification/README.md`](verification/README.md), [`test_surface.md`](test_surface.md) |
| what is the save/restore proof boundary? | [`requirements/ieee-1516-2025/save_restore_bounded_proof.md`](requirements/ieee-1516-2025/save_restore_bounded_proof.md) | [`verification/README.md`](verification/README.md) |
| what is the callback proof boundary? | [`requirements/ieee-1516-2025/callback_bounded_proof.md`](requirements/ieee-1516-2025/callback_bounded_proof.md) | [`verification/callback_model_compliance.md`](verification/callback_model_compliance.md) |
| what is the time/lookahead proof boundary? | [`requirements/ieee-1516-2025/time_management_bounded_proof.md`](requirements/ieee-1516-2025/time_management_bounded_proof.md) | [`verification/time_model_compliance.md`](verification/time_model_compliance.md), [`requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`](requirements/ieee-1516-2025/lookahead_window_bounded_proof.md) |
| what owns the framework umbrella rows? | [`requirements/ieee-1516-2025/framework_rules.md`](requirements/ieee-1516-2025/framework_rules.md) | [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md), [`verification/README.md`](verification/README.md) |
| what owns callback/configuration/binding umbrella rows? | [`requirements/ieee-1516-2025/callback_binding_deltas.md`](requirements/ieee-1516-2025/callback_binding_deltas.md) | [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md), [`verification/README.md`](verification/README.md) |
| what owns binding and hosted-route boundary rows? | [`requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`](requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md) | [`requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md`](requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md), [`plans/spec2025_route_parity_matrix.md`](plans/spec2025_route_parity_matrix.md) |
| what do Java/C++ standard bindings claim? | [`requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md`](requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md) | [`requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`](requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md), [`language_shim_routes.md`](language_shim_routes.md) |
| where is the Pitch proto HLA 4 / `202X` backend-resolution reading? | [`requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`](requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md) | [`../requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`](../requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv), [`../requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv`](../requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv) |
| what owns retired or legacy-only 2025 rows? | [`requirements/ieee-1516-2025/retired_legacy_mapping.md`](requirements/ieee-1516-2025/retired_legacy_mapping.md) | [`requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md), [`verification/README.md`](verification/README.md) |
| what is the OMT `xs:any` boundary? | [`requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md`](requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md) | [`requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md), [`verification/README.md`](verification/README.md) |
| what is explicitly out of scope? | [`requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md) | [`verification/README.md`](verification/README.md) |
| which shard should own a requirement status change? | [`test_surface.md`](test_surface.md) | [`verification/README.md`](verification/README.md), [`plans/requirements_remaining_closure.md`](plans/requirements_remaining_closure.md) |
| what testing lane should I run first? | [`test_surface.md`](test_surface.md) | [`local_verification_commands.md`](local_verification_commands.md), [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md) |
| where do I generate the boss-facing 2010 and 2025 compliance spreadsheets? | [`verification/requirement_compliance_exports.md`](verification/requirement_compliance_exports.md) | [`plans/requirements_completion_audit.md`](plans/requirements_completion_audit.md), [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md), [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md) |

## Practical Rule

- requirements docs explain the claim, boundary, and intended evidence scope
- verification docs explain where executable or generated proof artifacts live
- backend and route docs explain how the runtime or route is wired

## Shard And View Reading Rule

Use shards and views deliberately:

- start from the owning requirement doc when the question is claim or status
- start from [`test_surface.md`](test_surface.md) when the question is which
  runnable shard proves the claim
- use views only for overlap questions such as `transport`, `time`,
  `save-restore`, `java-shim`, `cpp-shim`, `setup-preflight`, or `finish-line`
- do not let a view replace the owning shard or the canonical requirement row

## Backend Resolution Rule

Keep canonical requirement disposition separate from backend support:

- requirement status belongs in the owner row or grouped harmonization ledger
- backend resolution belongs in separate backend columns or a linked
  backend-resolution artifact
- Pitch's vendor-branded proto HLA 4 / `202X` surface is backend-resolution
  terminology, not canonical requirement status
- boss-facing CSV/XLSX packets are generated presentation surfaces, not owner
  ledgers

## Read Next

1. [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)
2. [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md)
3. [`verification/README.md`](verification/README.md)
4. [`test_surface.md`](test_surface.md)
5. [`requirements_trace_one_method.md`](requirements_trace_one_method.md)
