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
The focused `2010` packet is now owner-clean and has no remaining `partial`
rows.

## Phase 2: Large Partial Family Tightening

There are no active queue entries at this phase.
The current 2010 family-level partial surfaces are already in their intended
closeout state.
## Latest Investigated No-Convert Result

The `2025 framework umbrella slice` (`HLA2025-FR-001` through
`HLA2025-FR-010`) was re-audited on `2026-06-26`.

Result:

- keep it as an umbrella boundary
- do not spend the next closeout slice trying to relabel it as direct
  `covered`

Why:

1. the linked FI, OMT, traceability, scenario, ownership, and time rows
   already own the real child proof
2. current framework owner docs already express the narrow honest reading for
   these rules without creating a second proof bucket
3. no narrower direct claim was identified that would avoid double-counting
   the child proof

Use the framework owner doc as maintained boundary documentation and advance to
`P1` / `P2` above for the next actual closeout move.

The `2025 callback-control umbrella slice` (`HLA2025-FI-CB-002` through
`HLA2025-FI-CB-004`) was re-audited on `2026-06-26`.

Result:

- keep it as an umbrella boundary
- do not spend the next closeout slice trying to relabel it as direct `covered`

Why:

1. `HLA2025-FI-SVC-193` through `HLA2025-FI-SVC-196` already own the direct FI
   service semantics
2. current runtime, backend, scenario, and transport tests already exercise
   the same callback-control behavior as child-row evidence
3. no narrower direct claim was identified that would avoid double-counting the
   child proof

Use the callback-control owner doc as maintained boundary documentation and
advance to `P1` / `P2` above for the next actual closeout move.

The `2010 mixed-backend priority rows` bucket was also re-audited on
`2026-06-27`.

Result:

- keep the canonical rows `pass`
- keep the backend split in
  `requirements/2010/hla1516_1_priority_backend_resolution.csv`
- do not spend the next closeout slice trying to broaden those cross-backend
  rows into false backend parity claims

Why:

1. the current owner rows are already closed for the repo-supported claim
2. Python proof is strong, but the mixed-backend dispositions remain real and
   material
3. backend-resolution truth still belongs in the companion ledger rather than
   in one overloaded status cell
4. the owner doc already expresses the honest final reading for the current
   evidence

The owning shard commands were rerun on `2026-06-26` and are green again after
fixing a hosted transport connect-overload bug in
`packages/hla-transport-common/src/hla/transports/common/hosted_server.py`.

The `2025 FedPro protocol umbrella slice` (`HLA2025-BIND-FEDPRO-001`) was also
re-audited on `2026-06-26`.

Result:

- keep it as an umbrella boundary
- do not spend the next closeout slice trying to relabel it as direct
  `covered`

Why:

1. `HLA2025-BND-003` already owns the bounded hosted FedPro/protobuf child
   surface
2. the current owner docs already express the real claim as bounded hosted
   request/response/callback parity over `hla-backend-python1516-2025`
3. current transport and route-parity evidence already prove the real wire
   surface without creating a second RTI implementation claim
4. no narrower direct claim was identified that would avoid restating the
   bounded hosted-route child proof

Use the hosted-route owner docs as maintained boundary documentation and
advance to `P1` / `P2` above for the next actual closeout move.

The `2025 directed-interaction callback umbrella slice`
(`HLA2025-FI-CB-007`) was also re-audited on `2026-06-26`.

Result:

- keep it as an umbrella boundary
- do not spend the next closeout slice trying to relabel it as direct
  `covered`

Why:

1. `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, and `HLA2025-BND-003` already
   own the directed send/receive and bounded hosted-route child proof
2. current runtime, transport, and route-parity evidence already exercise the
   same directed callback semantics as child-row evidence
3. no narrower direct claim was identified that would avoid restating the
   child proof

Use the callback/configuration/binding owner doc as maintained boundary
documentation and advance to `P1` / `P2` above for the next actual closeout
move.

The `2025 configuration/auth umbrella slice` (`HLA2025-FI-CFG-001`,
`HLA2025-FI-AUTH-001`) was also re-audited on `2026-06-26`.

Result:

- keep it as an umbrella boundary
- do not spend the next closeout slice trying to relabel it as direct
  `covered`

Why:

1. `HLA2025-FI-005`, `HLA2025-MOD-001`, and `HLA2025-BND-003` already own the
   connect/auth/configuration child semantics
2. current runtime, factory-composition, and transport evidence already
   exercise the same callback-model, credentials, and connect-shape behavior
   as child-row evidence
3. no narrower direct claim was identified that would avoid restating the
   child proof

Use the callback/configuration/binding owner doc as maintained boundary
documentation and advance to `P1` / `P2` above for the next actual closeout
move.

The `2025 Java/C++ binding umbrella slice` (`HLA2025-BIND-JAVA-CPP-001`) was
also re-audited on `2026-06-26`.

Result:

- keep it as an umbrella boundary
- do not spend the next closeout slice trying to relabel it as direct
  `covered`

Why:

1. `HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, and
   `HLA2025-FI-004` already own the binding-capability and wrapper-surface
   child proof
2. current standard-shim artifact tests, route-parity checks, and shim-route
   evidence already exercise the same bounded Java/C++ adapter/runtime story
   as child-row evidence
3. no narrower direct claim was identified that would avoid restating the
   child proof

Use the callback/configuration/binding owner doc as maintained boundary
documentation and advance to `P1` / `P2` above for the next actual closeout
move.

The `2010 CAP-SUP bounded family` was also re-audited on `2026-06-27`.

Result:

- keep it as a bounded family surface
- do not spend the next closeout slice trying to relabel it as direct support

Why:

1. the current owner doc and reconciliation companion already express the
   intended bounded Clause 10 reading
2. the owning support-service shard is green
3. the remaining tail is still a uniform bounded `43 PRE`, `43 EXC`, and
   `43 EXC_API` envelope rather than a set of isolated direct per-service
   witnesses
4. the owner ledger and Clause 10 companion now state those bounded envelopes
   explicitly at the row-note level instead of relying on one generic
   residual explanation
5. no narrower direct claim was identified that would preserve the current row
   meanings without adding new exhaustive per-service negative-matrix proof

Use the support-services owner docs as maintained bounded documentation and
advance to `P1` / `P2` above for the next actual closeout move.

The `2010 CAP-TM bounded family` was also re-audited on `2026-06-27`.

Result:

- keep it as a bounded family surface
- do not spend the next closeout slice trying to relabel it as direct support

Why:

1. the current owner doc and reconciliation companion already express the
   intended bounded Clause 8 reading
2. the owning time-management shard is green
3. the remaining tail is still a stable bounded `19 PRE`, `19 EXC`,
   `19 EXC_API`, and `1 OVW` envelope rather than a set of isolated direct
   per-row witnesses
4. the owner ledger and Clause 8 companion now state those bounded envelopes
   explicitly at the row-note level instead of relying on one generic
   residual explanation
5. no narrower direct claim was identified that would preserve the current row
   meanings without adding new isolated negative or overview-decomposition
   proof

Use the time-management owner docs as maintained bounded documentation and
advance to `P1` / `P2` above for the next actual closeout move.

The `2010 CAP-FM bounded family` was also re-audited on `2026-06-27`.

Result:

- keep it as a bounded family surface
- do not spend the next closeout slice trying to relabel it as direct support

Why:

1. the current owner doc and reconciliation companion already express the
   intended bounded Clause 4 reading
2. the owning federation-management shards are green
3. the remaining tail is now a stable bounded `43 ARG`, `17 CB_ORD`,
   `4 EFF`, `4 EXC`, and `11` residual envelope rather than a set of isolated
   direct per-row witnesses
4. no narrower direct claim was identified that would preserve the current row
   meanings without adding new row-level decomposition or direct runtime
   connection-loss callback proof

Use the federation-management owner docs as maintained bounded documentation
and advance to `P1` / `P2` above for the next actual closeout move.

The `2010 CAP-OWN bounded family` was also re-audited on `2026-06-27`.

Result:

- keep it as a fully mapped closeout surface
- do not spend the next closeout slice trying to reintroduce broader Clause 7
  exception universes without new witnesses

Why:

1. the current owner doc and reconciliation companion now express the intended
   fully mapped Clause 7 closeout reading
2. the owning ownership shards are green
3. the former Clause 7 tail has been converted into isolated direct guard
   claims for PRE, EXC, and EXC_API rows
4. future work should widen those rows only by adding stronger isolated
   negative-path proof

Use the ownership-management owner docs as maintained closeout documentation
and advance to `P1` / `P2` above for the next actual closeout move.

The `2010 CAP-DDM bounded family` was also re-audited on `2026-06-26`.

Result:

- keep it as a bounded family surface
- do not spend the next closeout slice trying to relabel it as direct support

Why:

1. the current owner doc and reconciliation companion already express the
   intended bounded Clause 9 reading
2. the owning DDM shards are green
3. the remaining tail is now a stable bounded `6 EXC` and `10 EXC_API`
   envelope rather than a set of isolated direct per-row witnesses
4. no narrower direct claim was identified that would preserve the current row
   meanings without adding new isolated negative-path proof

Use the data-distribution owner docs as maintained bounded documentation and
advance to `P1` / `P2` above for the next actual closeout move.

The `2010 CAP-XML / CAP-OMT bounded family` was also re-audited on
`2026-06-27`.

Result:

- keep it as a bounded family surface
- do not spend the next closeout slice trying to relabel it as direct support

Why:

1. the current owner doc and reconciliation companions already express the
   intended bounded XML schema-family and Annex B normalization reading
2. the owning parser, validator, MOM-catalog, and round-trip shards are green
3. the remaining XML tail is still a stable bounded `274 XML_ELEM`,
   `89 XML_TYPE`, and `1 CLAUSE12_13_DETAIL` envelope
4. the remaining OMT tail is still a stable bounded `2` normalization-row
   envelope
5. the reader-facing owner surfaces now keep the XML and OMT ledgers canonical
   while retaining `hla1516_2_omt_xml_detailed_reconciliation.csv` only as a
   legacy bridge artifact
6. no narrower direct claim was identified that would preserve the current row
   meanings without adding one-row-per-element, one-row-per-type, or stronger
   executable normalization proof

Use the OMT/XML owner docs as maintained bounded documentation. After this
decision, there are no remaining 2010 family-level tightening buckets; only
revisit-only mixed-backend priority rows remain if backend truth changes.

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
stale relative to the maintained boundary surfaces below, then run `P1`
only if backend truth has actually changed.

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
| 2010 CAP-DM bounded family | the owner doc and reconciliation ledger now express the intended fully mapped closeout reading; rerun only if future work tries to widen the narrowed Clause 5 guard claims materially | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/backends/test_python_backend_time_ddm_extended.py` | `declaration_management_bounded_family.md` plus `hla1516_1_dm_detailed_reconciliation.csv` |
| 2010 CAP-DDM bounded family | the owner doc and reconciliation ledger already express the intended bounded supported-scope reading; rerun only if precondition-envelope scope or exception-envelope scope materially changes | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_compliance_slice_v011.py` | `data_distribution_management_bounded_family.md` plus `hla1516_1_ddm_detailed_reconciliation.csv` |
| 2010 CAP-OWN bounded family | the owner doc and reconciliation ledger now express the intended fully mapped closeout reading; rerun only if future work tries to widen the narrowed Clause 7 guard claims materially | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/scenarios/test_ownership_management_backend_matrix.py` | `ownership_management_bounded_family.md` plus `hla1516_1_own_detailed_reconciliation.csv` |
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
