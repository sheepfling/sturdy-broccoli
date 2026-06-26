# Requirements Execution Queue

Use this page when the question is:

- what should we close first?
- which still-open buckets are cheapest to resolve honestly?
- what sequence gives the shortest truthful path to a finished requirements surface?

This queue is derived from
[`requirements_gap_register.md`](requirements_gap_register.md).

Reading rule:

- use this queue for ordering
- use `requirements_gap_register.md` for the exact owner doc, owner companion,
  and artifact-update contract before changing a bucket

## Queue Rules

Use this prioritization logic:

1. close direct `planned` rows before broad `partial` families
2. prefer buckets with one clear owner doc and one narrow shard
3. prefer buckets that collapse multiple open rows or remove ambiguity from the
   final claim
4. prefer low-risk final-claim hygiene work early when it removes ambiguity
   without inventing broader runtime claims
5. delay broad bounded-claim redesign unless it blocks a concrete stronger claim

## Phase 1: Cheapest Truthful Wins

There are no active queue entries at this phase.
The prior 2025 umbrella and retired-row final-claim normalization work is now
settled into maintained owner notes.

## Phase 2: Large Partial Family Tightening

These are where the remaining truthful-closeout gap is largest on the 2010 side.

| Priority | Bucket | Why now | First command | Owner pair |
| --- | --- | --- | --- | --- |

## Phase 3: Broad Bounded-Claim Decisions

There are no active queue entries at this phase.
The current bounded claim surfaces are already in their intended closeout
state; reopen them only if the repo deliberately broadens claim scope.

## Phase 4: Residual Final-Claim Hygiene

There are no active queue entries at this phase.
Residual hygiene now lives in the maintained owner notes below and should be
revisited only if later proof work materially changes child claims.

## Cheapest Win Candidates

If the goal is immediate visible progress with minimal scope risk, start by
checking whether any generated report, owner doc, or row-level ledger has gone
stale relative to the maintained boundary surfaces below.

## Dependency Notes

- do not spend time expanding 2025 bounded route/binding claims before the
  final-claim boundary docs are stable
- treat the 2010 mixed-backend clause rows as already honest bounded-owner
  surfaces unless new backend evidence reopens them
- route/binding claim expansion should happen only after the repo decides
  whether a broader than bounded claim is actually wanted

## Maintained Boundaries

These are not active queue entries, but they remain important canonical
boundary surfaces:

| Boundary | Why not queued | Maintenance command | Owner pair |
| --- | --- | --- | --- |
| 2010 lost-federate and TM mixed-backend clause rows | the owner doc and backend-resolution companion already express the intended bounded final reading; rerun only if backend evidence changes | `python3 -m pytest tests/scenarios/test_federation_management_backend_matrix.py -q -k 'test_python_connection_lost_callback_matrix or test_python_backend_lost_federate_mom_matrix'` or `python3 -m pytest tests/time/test_section8_backend_matrix.py -q -k test_section8_backend_matrix_order_override_services` | `mixed_backend_priority_boundaries.md` plus `hla1516_1_priority_backend_resolution.csv` |
| 2010 CAP-FM bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if row-level decomposition or Clause 4 proof scope changes materially | `python3 -m pytest tests/backends/test_python_backend_federation_extended.py tests/verification/test_requirements_ledger_v013.py` | `federation_management_bounded_family.md` plus `hla1516_1_fm_detailed_reconciliation.csv` |
| 2010 CAP-SUP bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if per-service negative-matrix scope or Clause 10 proof scope changes materially | `python3 -m pytest tests/backends/test_python_backend_support_services.py tests/scenarios/test_support_services_backend_matrix.py` | `support_services_bounded_family.md` plus `hla1516_1_sup_detailed_reconciliation.csv` |
| 2010 CAP-OM bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if callback-order isolation, effect-vector scope, negative-envelope scope, or supported-transport-subset claims materially change | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_requirements_ledger_v013.py` | `object_management_bounded_family.md` plus `hla1516_1_om_detailed_reconciliation.csv` |
| 2010 CAP-TM bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if precondition-envelope scope, exception-envelope scope, or overview decomposition materially changes | `python3 -m pytest tests/time/test_mom_mim_time_v10.py tests/time/test_mom_mim_and_time_semantics_v010.py tests/time/test_mom_mim_time_management_v010.py` | `time_management_bounded_family.md` plus `hla1516_1_tm_detailed_reconciliation.csv` |
| 2010 CAP-DM bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if precondition-envelope scope or exception-envelope scope materially changes | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/backends/test_python_backend_time_ddm_extended.py` | `declaration_management_bounded_family.md` plus `hla1516_1_dm_detailed_reconciliation.csv` |
| 2010 CAP-DDM bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if precondition-envelope scope or exception-envelope scope materially changes | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_compliance_slice_v011.py` | `data_distribution_management_bounded_family.md` plus `hla1516_1_ddm_detailed_reconciliation.csv` |
| 2010 CAP-OWN bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if precondition-envelope scope or exception-envelope scope materially changes | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/scenarios/test_ownership_management_backend_matrix.py` | `ownership_management_bounded_family.md` plus `hla1516_1_own_detailed_reconciliation.csv` |
| 2010 CAP-XML / CAP-OMT bounded family | the owner doc and companion ledgers already express the intended bounded schema-family and normalization-semantics reading; rerun only if the repo deliberately expands to one-row-per-atom XML witnesses or stronger runtime normalization semantics | `python3 -m pytest tests/factories/test_fom_omt_parsing.py tests/factories/test_fom_validate.py tests/mom/test_mom_catalog_validation_v012.py` | `omt_xml_bounded_family.md` plus `hla1516_xml_detailed_reconciliation.csv` and `hla1516_2_omt_detailed_reconciliation.csv` |
| 2025 duplicate/umbrella framework rows | the owner doc and row-level disposition ledger already express the intended non-standalone final reading; rerun only if child claims or framework ownership change materially | `./tools/python verify-main-2025` only if child claims change | `framework_rules.md` plus `hla_2025_requirement_disposition_ledger.csv` |
| 2025 duplicate/umbrella callback-binding rows | the owner doc, row-level disposition ledger, and FI binding matrix already express the intended non-standalone final reading; rerun only if child claims or binding ownership change materially | `./tools/test-surface run unit-shim-tooling` only if child claims change | `callback_binding_deltas.md` plus `hla_2025_requirement_disposition_ledger.csv` and `hla_2025_fi_binding_surface_matrix.csv` |
| 2025 retired/legacy-only rows | the owner doc and row-level disposition ledger already express the intended exclusion reading; rerun only if the retired mapping changes or a compatibility program is deliberately added | `python3 -m pytest tests/test_documentation_policy.py tests/verification/test_imported_hla_packet_backlog.py` | `retired_legacy_mapping.md` plus `hla_2025_requirement_disposition_ledger.csv` |
| 2025 binding / hosted-route bounded claims | the owner doc, route-parity artifacts, grouped worklist, and FI binding surfaces already express the intended bounded adaptation and hosted-route reading; rerun only if the repo deliberately opens a broader behavior-equivalence program | `./tools/test-surface run transport` | `binding_and_hosted_route_boundaries.md` plus route-parity artifacts and FI binding surfaces |
| 2025 Pitch proto HLA 4 / `202X` backend-resolution lane | the owner doc plus grouped and row-level Pitch companion ledgers already express the intended bounded backend-resolution reading; rerun only if the repo deliberately opens a broader vendor-runtime comparison or certification program | `./tools/test-surface run transport` | `pitch_202x_bounded_comparison.md` plus `hla_2025_pitch_202x_group_resolution.csv` and `hla_2025_pitch_202x_row_resolution.csv` |
| 2025 OMT `xs:any` extension-tolerance boundary | the owner doc and row-level disposition ledger already express the intended payload-preserving tolerance reading; rerun only if the repo deliberately opens a broader extension-execution program | `python3 -m pytest tests/test_rti1516_2025_validation.py` | `omt_xs_any_extension_tolerance.md` plus `hla_2025_requirement_disposition_ledger.csv` |

## Related Docs

- [`requirements_gap_register.md`](requirements_gap_register.md)
- [`requirements_completion_audit.md`](requirements_completion_audit.md)
- [`requirements_remaining_closure.md`](requirements_remaining_closure.md)
