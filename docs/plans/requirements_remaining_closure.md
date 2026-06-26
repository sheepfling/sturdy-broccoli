# Requirements Remaining Closure

Use this page when the question is:

- which requirement areas are still not fully tested or fully closed?
- which remaining rows are merely `partial` versus actually `planned`?
- what should we do next to finish the 2010 and 2025 requirement surfaces honestly?

This is the concrete closeout companion to
[`requirements_finish_line.md`](requirements_finish_line.md).

It does not restate the whole requirement surface.
It only records the remaining proof debt that still blocks a stronger
"finished" claim.

## Authoritative Sources

Use these sources as the truth inputs behind this note:

- `2010` source-side inventory:
  [`../../requirements/2010/README.md`](../../requirements/2010/README.md)
- `2025` source-side inventory:
  [`../../requirements/2025/README.md`](../../requirements/2025/README.md)
- `2010` master harmonization index:
  [`../../requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`](../../requirements/2010/hla_1516_master_harmonization_index_v1_0.csv)
- `2025` completion backlog:
  [`../../requirements/2025/requirement_completion_backlog.csv`](../../requirements/2025/requirement_completion_backlog.csv)
- `2025` harmonization worklist:
  [`../../requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`](../../requirements/2025/harmonization/hla_2025_harmonization_worklist.csv)

## What "Remaining" Means

Use these terms precisely:

- `planned`: no defensible executable proof yet for the claimed row or group
- `partial`: some proof exists, but it is narrower than the full standard wording
- `duplicate/umbrella`: organizational or grouping rows, not standalone proof claims
- `retired/legacy-only`: intentionally excluded from active 2025 support claims

If a row is already `mapped` or `covered`, it does not belong on this page.

## 2010 Remaining Closure

The `2010` surface is structurally linked and collected.
The remaining work is mostly proof closure, not navigation cleanup.

Current imported-master status from
[`../../requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`](../../requirements/2010/hla_1516_master_harmonization_index_v1_0.csv):

- `2675 mapped`
- `1328 partial`
- `0 unreconciled`

### 2010 Exact Planned Rows

These are the direct `planned` rows still visible in the curated `2010` source
files:

1. `HLA1516.1-FM-4.3-MOM-001`
   - file: `hla1516_1_clause_4_fm_service_decomposition.csv`
   - gap: disconnect should leave no active MOM-visible federate session
2. `HLA1516.1-DM-5.1.6-001`
   - file: `hla1516_1_clause_5_declaration_management.csv`
   - gap: update-rate reduction subscription support
3. `HLA1516.1-FM-4.1-005`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: one application participating as multiple joined federates
4. `HLA1516.1-FM-4.1-006`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: one application participating in multiple federation executions
5. `HLA1516.1-FM-4.1.2-002`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: queued-message preservation for save/restore
6. `HLA1516.1-FM-4.1.4.1-002`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: reject invalid FOM/MIM definitions in entirety
7. `HLA1516.1-FM-4.1.5-001`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: lost-federate detection and MOM reporting
8. `HLA1516.1-FM-4.1.5-002`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: automatic resign handling for lost federates
9. `HLA1516.1-TM-8.1.2-003`
   - file: `hla1516_1_priority_clauses_4_8_11.csv`
   - gap: RO messages must never be converted into received TSO messages
10. `HLA1516.1-DM-5.1.6-001`
    - file: `traceability_matrix.csv`
    - gap: traceability row still marked planned because runtime update-rate reduction semantics are not implemented

### 2010 Largest Partial Families

These families are linked into the catalog, but still broader than the current
proof:

- `CAP-API`: `394 partial`
- `CAP-XML`: `364 partial`
- `CAP-SUP`: `129 partial`
- `CAP-OM`: `117 partial`
- `CAP-FM`: `109 partial`
- `CAP-TM`: `58 partial`
- `CAP-DDM`: `46 partial`
- `CAP-FW`: `41 partial`
- `CAP-DM`: `38 partial`
- `CAP-OWN`: `30 partial`
- `CAP-OMT`: `2 partial`

Practical reading:

- `planned` means direct proof is still missing
- `partial` means there is already some link or test anchor, but the row still
  overstates what the current proof can honestly defend

### 2010 Finish Order

Use this order:

1. close the `10` direct `planned` rows first
2. burn down `CAP-FM`, `CAP-SUP`, `CAP-OM`, and `CAP-TM` partial rows next
3. treat `CAP-API` and `CAP-XML` as larger tranche work, not one-off spot fixes

### 2010 Suggested Shards And Slices

Use the smallest proof slice that matches the requirement family before falling
back to a broader lane:

| Remaining area | Owner doc | First slice to run | When to widen | Evidence artifact to update |
| --- | --- | --- | --- | --- |
| direct `planned` Federation Management rows | `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv` | `python3 -m pytest tests/backends/test_python_backend_federation_extended.py tests/scenarios/test_startup_sync_fom_java_translation_v09.py` | widen to `./tools/test-focus run save-restore-2025` only if the gap crosses save/restore or scenario replay semantics | `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv`, `requirements/2010/hla1516_1_priority_clauses_4_8_11.csv`, `requirements/2010/traceability_matrix.csv` |
| direct `planned` Declaration Management row | `requirements/2010/hla1516_1_clause_5_declaration_management.csv` | `python3 -m pytest tests/verification/test_requirements_ledger_v013.py` | widen to `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py` if the row turns into runtime subscription semantics | `requirements/2010/hla1516_1_clause_5_declaration_management.csv`, `requirements/2010/traceability_matrix.csv` |
| `CAP-FM` partials | `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` | `python3 -m pytest tests/backends/test_python_backend_federation_extended.py tests/verification/test_requirements_ledger_v013.py` | widen to `./tools/test-surface run scenarios` when the row depends on scenario composition | `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |
| `CAP-SUP` partials | `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` | `python3 -m pytest tests/backends/test_python_backend_support_services.py tests/scenarios/test_support_services_backend_matrix.py` | widen to `./tools/python verify-main-2025` only when support-service changes touch shared runtime surfaces | `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |
| `CAP-OM` partials | `requirements/2010/hla1516_1_om_detailed_reconciliation.csv` | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_requirements_ledger_v013.py` | widen to `./tools/test-surface run scenarios` when object/message routing behavior is scenario-driven | `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |
| `CAP-TM` partials | `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv` | `python3 -m pytest tests/time/test_mom_mim_time_v10.py tests/time/test_mom_mim_and_time_semantics_v010.py tests/time/test_mom_mim_time_management_v010.py` | widen to `./tools/test-focus run python-2025-time` when the row depends on broader time-window ladders | `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |
| `CAP-OWN` partials | `requirements/2010/hla1516_1_own_detailed_reconciliation.csv` | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/scenarios/test_ownership_management_backend_matrix.py` | widen to `./tools/test-focus run python-2025-ownership` if the requirement spans broader ownership gauntlets | `requirements/2010/hla1516_1_own_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |
| `CAP-API` partials | `requirements/2010/hla1516_1_api_detailed_reconciliation.csv` | `python3 -m pytest tests/verification/test_clause13_conformance_packet.py tests/verification/test_requirements_ledger_v013.py` | widen to `./tools/test-surface run unit-shim-tooling` when the change affects standard Java/C++ route artifacts | `requirements/2010/hla1516_1_api_detailed_reconciliation.csv`, `docs/verification/clause13_conformance_packet.json`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |
| `CAP-XML` and `CAP-OMT` partials | `requirements/2010/hla1516_xml_detailed_reconciliation.csv`, `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv` | `python3 -m pytest tests/factories/test_fom_omt_parsing.py tests/factories/test_fom_validate.py tests/mom/test_mom_catalog_validation_v012.py` | widen to `./tools/test-surface run unit-fom-tooling` for parser/validator/workbench cross-checks | `requirements/2010/hla1516_xml_detailed_reconciliation.csv`, `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` |

## 2025 Remaining Closure

The `2025` surface is structurally linked and collected.
The remaining work is mostly harmonization closure and proof granularity.

Current grouped closure state from
[`../../requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`](../../requirements/2025/harmonization/hla_2025_harmonization_worklist.csv):

- `6 covered`
- `8 planned`
- `43 partial`
- `5 duplicate/umbrella`
- `2 retired/legacy-only`

### 2025 Planned Groups

These groups still need direct proof construction:

1. `Federate Interface service catalog / Data distribution management`
   - `12 rows`
2. `Federate Interface service catalog / Declaration management`
   - `12 rows`
3. `Federate Interface service catalog / Federation management`
   - `24 rows`
4. `Federate Interface service catalog / Object management`
   - `15 rows`
5. `Federate Interface service catalog / Ownership management`
   - `18 rows`
6. `Federate Interface service catalog / Support services`
   - `6 rows`
7. `OMT validator-negative conformance / Schema enumerations and value domains`
   - `15 rows`
8. `OMT validator-negative conformance / Schema identity and reference constraints`
   - `14 rows`

### 2025 Partial Clusters

These groups already have some evidence, but not enough for a stronger claim:

- `Federate Interface service catalog`
  - Federation management: `1 row`
  - Object management: `10 rows`
  - Support services: `22 rows`
  - Time management: `23 rows`
- `OMT component-level conformance`
  - object model identification, switches, reference datatypes, time representation,
    dimensions, attributes, interaction/object structures, synchronization,
    transportation types, update-rate tables, tags, and variant records
- `SOM/FOM service-usage requirements`
  - Federation management: `34 rows`
  - Object management: `32 rows`
  - Support services: `59 rows`
  - Time management: `25 rows`
  - Declaration management: `16 rows`
  - Ownership management: `18 rows`
  - Data distribution management: `12 rows`

### 2025 Non-Standalone Groups

These should not be mistaken for missing runtime behavior until their role is
normalized:

- `duplicate/umbrella`
  - callback/configuration/binding delta groups
  - framework umbrella rules
- `retired/legacy-only`
  - legacy FI API candidates
  - legacy OMT schema candidates

### 2025 Finish Order

Use this order:

1. finish the `planned` FI service groups
2. close the two `planned` OMT validator-negative groups
3. reduce the FI `partial` groups for support, time, and object management
4. close the large SOM/FOM service-usage partial clusters
5. only after that, normalize the `duplicate/umbrella` and `retired/legacy-only` rows into final boundary documents

### 2025 Suggested Shards And Slices

Use these slices when closing the grouped `2025` worklist buckets:

| Remaining area | Owner doc | First slice to run | When to widen | Evidence artifact to update |
| --- | --- | --- | --- | --- |
| FI `planned` Federation / Object / Support / Time groups | `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `./tools/python verify-main-2025` | widen to `./tools/python verify-routes-2025` when the claim includes hosted FedPro parity or route-backed proof | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, bounded proof note under `docs/requirements/ieee-1516-2025/` |
| FI `planned` Ownership group | `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `./tools/test-focus run python-2025-ownership` | widen to `./tools/python verify-routes-2025` when hosted route replay matters | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, `docs/requirements/ieee-1516-2025/ownership_management_bounded_proof.md` |
| FI `planned` DDM and Declaration groups | `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_requirements_ledger_v013.py` | widen to `./tools/python verify-main-2025` when the row needs the broader main-surface proof lane | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, matching bounded proof note |
| OMT validator-negative `planned` groups | `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `python3 -m pytest tests/factories/test_fom_validate.py tests/factories/test_fom_omt_parsing.py` | widen to `./tools/test-surface run unit-fom-tooling` for broader parser/validator/workbench coverage | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, `docs/requirements/ieee-1516-2025/omt.md` or `omt_xs_any_extension_tolerance.md` |
| FI `partial` Support / Time / Object groups | `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `./tools/python verify-main-2025` | widen to `./tools/python verify-routes-2025` when the remaining proof boundary explicitly mentions hosted parity | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, matching bounded proof note |
| SOM/FOM service-usage partial clusters | `requirements/2025/depth/hla_2025_requirement_depth_expansion.csv` | `python3 -m pytest tests/factories/test_fom_omt_parsing.py tests/factories/test_fom_validate.py tests/scenarios/test_startup_sync_fom_java_translation_v09.py` | widen to `./tools/test-surface run unit-fom-tooling` or `./tools/test-surface run scenarios` depending on whether the gap is parser-side or scenario-side | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, source packet under `requirements/2025/depth/` |
| duplicate/umbrella callback-binding groups | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `./tools/test-surface run unit-shim-tooling` | widen to `./tools/python verify-routes-2025` only if the umbrella row is being turned into a route-backed proof claim | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md`, `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` |
| retired/legacy-only groups | `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md` | `python3 -m pytest tests/test_documentation_policy.py tests/verification/test_imported_hla_packet_backlog.py` | widen only if the retired mapping changes generated audits or requirement ledgers | `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md`, `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` |

## Recommended Cross-Edition Finish Order

If the goal is the shortest truthful path to "done", use this order:

1. `2010` direct `planned` rows
2. `2025` `planned` FI service groups
3. `2025` `planned` OMT validator-negative groups
4. `2010` high-volume partial capability families
5. `2025` partial FI and SOM/FOM clusters
6. final boundary cleanup for `2025` umbrella and retired rows

## Shard Rule

For every remaining category above:

1. start with the narrowest listed slice
2. promote to a broader lane only when the requirement claim itself crosses that boundary
3. when a row moves from `planned` to `partial` or `mapped`, record the exact shard or command that proved it

## Done Criteria

Treat this closeout as finished only when:

1. every `2010` direct `planned` row is either `mapped` or intentionally bounded with explicit proof
2. every `2025` `planned` worklist group is moved to `covered`, `partial`, or explicit exclusion with real evidence anchors
3. `partial` rows in both editions are reduced to intentionally bounded supported-scope claims rather than accidental under-testing
4. the supporting docs and ledgers still pass the documentation and traceability checks

## Related Docs

- [`requirements_finish_line.md`](requirements_finish_line.md)
- [`2025_requirements_finish_line.md`](2025_requirements_finish_line.md)
- [`imported_requirements_backlog_v1_0.md`](imported_requirements_backlog_v1_0.md)
