# 2010 Python RTI Bounded Family Execution Worklist

Use this note when the question is:

- what exactly remains bounded on the `2010 / 1516e` Python RTI side?
- which owner doc, companion ledger, and shard currently own each remaining
  `2010` partial family or mixed-backend boundary?
- what would have to happen to tighten one of those bounded `2010` surfaces
  into narrower direct proof?

This note is the concrete `2010` execution companion to:

- [`PLN-004_python_rti_100_percent_compliance_plan.md`](PLN-004_python_rti_100_percent_compliance_plan.md)
- [`requirements_remaining_closure.md`](requirements_remaining_closure.md)

## Current Truth

There are no remaining direct `2010` `planned` clause-family tightening rows in
the curated bounded-family closeout ledgers.

The broader `2010` backend-compliance packet also no longer contains any
`planned` rows.
The coarse framework, Clause 5, Clause 6, and traceability seed files also no
longer carry stale direct `partial` rows for entries that the packet already
proves as `pass`.
The former OMT-area and schema-conformance placeholders are now settled
explicitly as:

- `20` `pass` OMT/XML area rows
- `3` `implemented-slice` OMT/XML execution witnesses
- `0` remaining OMT/XML area partial placeholders

The remaining `2010` truth shape is already explicit and bounded:

1. mixed-backend priority rows that are now canonical `pass` with explicit
   backend-resolution companions
2. bounded detailed-reconciliation notes where imported-master residual
   families still overstate the exact proof granularity
3. XML and OMT bounded tails where the repo proves parser, schema, and
   round-trip families more strongly than it proves one-row-per-atom witnesses

This is not missing-owner debt.
It is explicit bounded-scope debt.

## Current Packet Snapshot

Use this snapshot when the question is:

- what still remains non-`pass` in the `2010` packet?
- which part is bounded-family debt versus already-settled direct proof?

Current `analysis/compliance/requirements_matrix_2010.csv` totals:

- `931` matrix rows
- `867` `pass`
- `40` `implemented-slice`
- `1` `implemented-smoke`
- `0` `partial`

Interpretation rule:

- there are no remaining `partial` rows in the focused `2010` packet
- there is no remaining hidden `planned` inventory in the `2010` packet
- do not describe the `2010` lane as if every remaining non-`pass` row were
  the same kind of debt

## Execution Rule

For each `2010` bounded bucket, choose one of two paths:

1. keep it bounded
2. tighten it into narrower direct proof

### Keep-Bounded Rule

Keep the bucket bounded when all of these remain true:

1. the current owner doc already explains the honest supported scope
2. the current companion ledger already records the canonical partial reading
3. stronger proof would require materially narrower or broader new work rather
   than a wording fix

### Tighten-To-Direct Rule

Only tighten a bounded bucket when all of these are true:

1. the narrower claim is explicitly named
2. the narrowest owning shard is named
3. the owner doc and companion ledger are updated together
4. the new proof improves the exact bounded row kind rather than only adding
   adjacent evidence

## Common Column Meanings

| Column | Meaning |
| --- | --- |
| `Bucket` | bounded family or mixed-backend surface |
| `Primary owner doc` | canonical human-facing owner note |
| `Primary companion` | canonical CSV or traceability companion |
| `Primary shard now` | narrowest current proof owner |
| `Primary views` | overlapping audit cuts |
| `Stay bounded when` | condition for preserving the current bounded reading |
| `Tighten only if` | minimum condition for narrower direct proof |

## Mixed-Backend Priority Rows

Primary owner:
[`../requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`](../requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md)

| Bucket | Primary owner doc | Primary companion | Primary shard now | Primary views | Stay bounded when | Tighten only if |
| --- | --- | --- | --- | --- | --- | --- |
| lost-federate detection and MOM reporting | `mixed_backend_priority_boundaries.md` | `requirements/2010/hla1516_1_priority_backend_resolution.csv` plus `requirements/2010/traceability_matrix.csv` | `unit-scenarios-light` | `2010-core`, `scenarios`, `save-restore` | Python proof remains strong while CERTI, Pitch, or Portico truth still diverges or remains unclassified | broader cross-backend parity proof or an intentionally narrowed Python-only final claim is recorded explicitly |
| automatic resign handling for lost federates | `mixed_backend_priority_boundaries.md` | `requirements/2010/hla1516_1_priority_backend_resolution.csv` plus `requirements/2010/traceability_matrix.csv` | `unit-scenarios-light` | `2010-core`, `scenarios`, `save-restore` | Python proof remains strong while broader backend truth still differs | the exact broader backend claim closes or the row is intentionally narrowed with explicit backend-resolution consequences |
| RO messages shall never become received TSO messages | `mixed_backend_priority_boundaries.md` | `requirements/2010/hla1516_1_priority_backend_resolution.csv` plus `requirements/2010/traceability_matrix.csv` | `unit-python-core` | `2010-core`, `time` | Python and CERTI prove the ordering rule while Pitch remains vendor-divergent or Portico remains unclassified | the exact cross-backend ordering claim closes or the row is intentionally narrowed to a smaller truthful scope |

## Latest Investigated Decision

The mixed-backend priority bucket was re-audited on `2026-06-26` against the
current owner doc, backend-resolution companion, traceability rows, and the
owning shard commands for:

- `HLA1516.1-FM-4.1.5-001`
- `HLA1516.1-FM-4.1.5-002`
- `HLA1516.1-TM-8.1.2-003`

Decision:

- keep these rows as canonical `pass`
- keep their backend split in
  `requirements/2010/hla1516_1_priority_backend_resolution.csv`
- do not promote them to a narrower direct canonical claim yet

Reason:

1. the row text is still intentionally cross-backend, not Python-only
2. Python proof is strong, but the companion ledger still records real mixed
   backend truth:
   - lost-federate rows: `python=verified`, `certi=not-yet-tested`,
     `pitch=blocked`, `portico=classification-required`
   - RO/TSO ordering row: `python=verified`, `certi=verified`,
     `pitch=vendor-divergent`, `portico=classification-required`
3. narrowing the canonical rows now would change the claim surface, not merely
   restate existing evidence
4. the current owner doc already expresses the honest final reading for the
   present evidence

Current evidence reviewed for this decision included:

- `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`
- `requirements/2010/hla1516_1_priority_backend_resolution.csv`
- `requirements/2010/traceability_matrix.csv`
- `analysis/compliance/requirements_matrix_2010.csv`
- `tests/scenarios/test_federation_management_backend_matrix.py`
- `tests/time/test_section8_backend_matrix.py`

Verification note:

- the owning time-row shard initially exposed a hosted transport connect overload bug in
  `packages/hla-transport-common/src/hla/transports/common/hosted_server.py`
- after fixing that connect dispatch, the listed owning shard commands were
  green again

Operational effect:

- mixed-backend priority rows remain a maintained bounded/backend-resolution
  surface
- the active execution queue should advance to the next real tightening bucket
  instead of treating these rows as unresolved wording debt

The `CAP-SUP` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard command for:

- `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`
- `tests/verification/test_sup_detailed_reconciliation.py`
- `python3 -m pytest tests/backends/test_python_backend_support_services.py tests/scenarios/test_support_services_backend_matrix.py`

Decision:

- keep the `CAP-SUP` family as canonical `partial`
- keep its Clause 10 tail recorded as the current bounded `PRE`, `EXC`, and
  `EXC_API` family envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion still shows a uniform bounded tail of
   `43 PRE`, `43 EXC`, and `43 EXC_API` rows
2. the current support-service shard is green, but the remaining packet rows
   still describe broader negative envelopes than the direct witnesses
3. the previously confusing factory-helper rows are no longer part of the live
   Python residual set:
   - `REQ-RTI-SS-10_44-getMessageRetractionHandleFactory`
   - `REQ-RTI-SS-10_44-getRegionHandleFactory`
   - both now read `status=pass` with `python_runtime_disposition=verified` in
     `analysis/compliance/requirements_matrix_2010.csv`
   - that confirms the remaining `CAP-SUP` debt is the broad negative-path
     envelope, not missing positive-path helper coverage
4. no narrower direct claim was identified that would preserve the current
   Clause 10 row meanings without adding new exhaustive per-service
   negative-matrix proof
5. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-SUP` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-DM` instead of continuing
  to treat `CAP-SUP` as unresolved wording debt

The `CAP-DM` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard commands for:

- `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`
- `tests/verification/test_dm_detailed_reconciliation.py`
- `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/backends/test_python_backend_time_ddm_extended.py`

Decision:

- keep the `CAP-DM` family as canonical `partial`
- keep its Clause 5 tail recorded as the current bounded `PRE`, `EXC`, and
  `EXC_API` envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion still shows a stable bounded tail of
   `12 PRE`, `12 EXC`, and `14 EXC_API` rows
2. the current Clause 5 shards are green, but the remaining packet rows still
   describe broader precondition or exception envelopes than the direct
   declaration witnesses isolate
3. no narrower direct claim was identified that would preserve the current
   Clause 5 row meanings without adding new isolated per-row precondition or
   negative-path proof
4. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-DM` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-TM` instead of continuing
  to treat `CAP-DM` as unresolved wording debt

The `CAP-TM` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard command for:

- `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv`
- `tests/verification/test_tm_detailed_reconciliation.py`
- `python3 -m pytest tests/time/test_mom_mim_time_v10.py tests/time/test_mom_mim_and_time_semantics_v010.py tests/time/test_mom_mim_time_management_v010.py`

Decision:

- keep the `CAP-TM` family as canonical `partial`
- keep its Clause 8 tail recorded as the current bounded `PRE`, `EXC`,
  `EXC_API`, and residual overview envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion still shows a stable bounded tail of
   `19 PRE`, `19 EXC`, `19 EXC_API`, and `1 OVW` row
2. the current time-management shard is green, but the remaining packet rows
   still describe broader precondition, exception, or overview envelopes than
   the direct witnesses isolate
3. no narrower direct claim was identified that would preserve the current
   Clause 8 row meanings without adding new isolated per-row negative or
   overview-decomposition proof
4. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-TM` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-FM` instead of continuing
  to treat `CAP-TM` as unresolved wording debt

The `CAP-FM` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard commands for:

- `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`
- `tests/verification/test_fm_detailed_reconciliation.py`
- `python3 -m pytest tests/backends/test_python_backend_federation_extended.py tests/verification/test_requirements_ledger_v013.py`

Decision:

- keep the `CAP-FM` family as canonical `partial`
- keep its Clause 4 tail recorded as the current bounded `ARG`, `EFF`,
  `CB_ORD`, `EXC`, and residual overview or callback-fault envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion still shows a stable bounded tail of
   `43 ARG`, `17 CB_ORD`, and a much smaller residual tail of bounded effect,
   callback, and exception rows
2. the current federation-management shards are green, but the remaining
   packet rows still describe broader decomposition, callback-order, state
   vector, or connection-loss fault envelopes than the direct witnesses
   isolate
3. no narrower direct claim was identified that would preserve the current
   Clause 4 row meanings without adding new row-level decomposition or direct
   runtime connection-loss callback proof
4. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-FM` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-OM` instead of continuing
  to treat `CAP-FM` as unresolved wording debt

The `CAP-OM` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard commands for:

- `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`
- `tests/verification/test_om_detailed_reconciliation.py`
- `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/backends/test_python_backend_object_ownership_extended.py`

Decision:

- keep the `CAP-OM` family as canonical `partial`
- keep its Clause 6 tail recorded as the current bounded `EFF`, `CB_ORD`,
  `CB_ORDER`, `EXC_API`, `EXC`, `PRE`, `FED_CB`, and `OVW` envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion now shows a stable bounded tail of
   `25 CB_ORD`, `17 CB_ORDER`, and the remaining bounded effect and exception
   tails that still overstate full transport and callback-order breadth
2. the current Clause 6 shards are green, and the family already reflects the
   recent tightening where the `updateAttributeValues` exception rows and the
   object-instance overload exception row for `requestAttributeValueUpdate`
   left the partial tail
3. the remaining class-wide `requestAttributeValueUpdate` exception rows stay
   intentionally bounded because the backend reports
   `InvalidObjectClassHandle` rather than the broader imported
   `ObjectClassNotDefined` wording
4. the current remaining packet rows still describe broader callback-order,
   effect-vector, exception-envelope, or supported-transport-subset claims
   than the direct witnesses isolate
5. no narrower direct claim was identified that would preserve the current
   Clause 6 row meanings without adding new isolated per-row callback-order,
   effect-vector, or negative-path proof
6. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-OM` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-OWN` instead of continuing
  to treat `CAP-OM` as unresolved wording debt

The `CAP-OWN` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard commands for:

- `requirements/2010/hla1516_1_own_detailed_reconciliation.csv`
- `tests/verification/test_own_detailed_reconciliation.py`
- `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/scenarios/test_ownership_management_backend_matrix.py`

Decision:

- keep the `CAP-OWN` family as canonical `partial`
- keep its Clause 7 tail recorded as the current bounded `PRE`, `EXC`, and
  `EXC_API` envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion still shows a stable bounded tail of
   `8 PRE`, `11 EXC`, and `11 EXC_API` rows
2. the current ownership shards are green, but the remaining packet rows still
   describe broader precondition or exception envelopes than the direct
   witnesses isolate
3. no narrower direct claim was identified that would preserve the current
   Clause 7 row meanings without adding new isolated per-row negative-path
   proof
4. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-OWN` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-DDM` instead of continuing
  to treat `CAP-OWN` as unresolved wording debt

The `CAP-DDM` bounded family was also re-audited on `2026-06-26` against the
current owner doc, reconciliation companion, reconciliation verifier, and the
owning shard commands for:

- `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`
- `tests/verification/test_ddm_detailed_reconciliation.py`
- `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_compliance_slice_v011.py`

Decision:

- keep the `CAP-DDM` family as canonical `partial`
- keep its Clause 9 tail recorded as the current bounded `EXC` and `EXC_API`
  envelope
- do not promote the family to narrower direct support yet

Reason:

1. the reconciliation companion now shows a stable bounded tail of
   `6 EXC` and `10 EXC_API` rows
2. the current DDM shards are green, but the remaining packet rows still
   describe broader precondition or exception envelopes than the direct
   witnesses isolate
3. no narrower direct claim was identified that would preserve the current
   Clause 9 row meanings without adding new isolated per-row negative-path
   proof
4. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-DDM` remains a maintained bounded-family surface
- the active execution queue should advance to `CAP-XML / CAP-OMT` instead of
  continuing to treat `CAP-DDM` as unresolved wording debt

The `CAP-XML / CAP-OMT` bounded family was also re-audited on `2026-06-26`
against the current owner doc, reconciliation companions, reconciliation
verifiers, and the owning shard command for:

- `requirements/2010/hla1516_xml_detailed_reconciliation.csv`
- `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`
- `tests/verification/test_xml_detailed_reconciliation.py`
- `tests/verification/test_omt_detailed_reconciliation.py`
- `python3 -m pytest tests/factories/test_fom_omt_parsing.py tests/factories/test_fom_validate.py tests/mom/test_mom_catalog_validation_v012.py`

Decision:

- keep the `CAP-XML / CAP-OMT` family as canonical `partial`
- keep its XML tail recorded as the current bounded `XML_ELEM`, `XML_TYPE`,
  and narrow schema-source envelope
- keep its OMT tail recorded as the current Annex B normalization boundary
- do not promote the family to narrower direct support yet

Reason:

1. the XML reconciliation companion still shows a stable bounded tail of
   `274 XML_ELEM`, `89 XML_TYPE`, and `1 CLAUSE12_13_DETAIL` row
2. the OMT reconciliation companion still shows a stable bounded tail of `2`
   Annex B normalization rows
3. the current parser, validator, MOM-catalog, and round-trip shards are
   green, but the remaining packet rows still describe atom-level schema or
   normalization semantics beyond the current curated direct witnesses
4. no narrower direct claim was identified that would preserve the current XML
   and OMT row meanings without adding new one-row-per-element, one-row-per-
   type, or stronger executable normalization proof
5. the current owner doc already expresses the honest final reading for the
   present evidence

Operational effect:

- `CAP-XML / CAP-OMT` remains the final maintained bounded-family surface on
  the `2010` lane
- there are no remaining 2010 family-level tightening buckets after this; only
  revisit-only mixed-backend priority rows remain if backend-resolution truth
  changes

## Partial-Family Buckets

| Bucket | Primary owner doc | Primary companion | Primary shard now | Primary views | Stay bounded when | Tighten only if |
| --- | --- | --- | --- | --- | --- | --- |
| `CAP-FM` | `federation_management_bounded_family.md` | `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-scenarios-light` | `2010-core`, `scenarios`, `save-restore` | lifecycle, synchronization, save, and restore are already broadly proven but the remaining `ARG`, `EFF`, `CB_ORD`, `EXC`, and residual packet slices still overstate proof granularity | new direct witnesses close the exact remaining packet-row kinds or the repo deliberately moves to one-row-per-packet Clause 4 claims |
| `CAP-DM` | `declaration_management_bounded_family.md` | `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-foundation` | `2010-core`, `setup-preflight`, `scenarios` | publication, subscription, declaration callbacks, and representative negatives are already strong while the remaining precondition and exception envelope rows still describe broader matrices than the current direct witnesses | new direct per-row declaration witnesses close the remaining `PRE`, `EXC`, or `EXC_API` packet slices |
| `CAP-SUP` | `support_services_bounded_family.md` | `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-python-core` | `2010-core`, `setup-preflight` | support-service presence, signatures, lookup behavior, MOM observability, and representative negative paths are already strong while the remaining negative envelope stays broader than the direct witnesses | new direct per-service negative-matrix witnesses close the remaining `PRE`, `EXC`, and `EXC_API` rows |
| `CAP-OM` | `object_management_bounded_family.md` | `requirements/2010/hla1516_1_om_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-scenarios-light` | `2010-core`, `scenarios` | naming, discovery, update, interaction, delete, and supported transport-subset paths are already strong while the remaining rows still describe broader callback-order, effect-vector, or exception envelopes | new isolated row witnesses close the exact remaining bounded row kinds |
| `CAP-OWN` | `ownership_management_bounded_family.md` | `requirements/2010/hla1516_1_own_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-scenarios-light` | `2010-core`, `ownership`, `scenarios` | divestiture, acquisition, callback, query, and MOM behavior are already strong while the remaining rows still describe broader precondition or exception envelopes | new ownership-specific witnesses close the remaining `PRE`, `EXC`, or `EXC_API` packet slices |
| `CAP-TM` | `time_management_bounded_family.md` | `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-python-core` | `2010-core`, `time` | logical time, lookahead, callback ordering, retraction, and queries are already strong while the remaining rows still describe broader precondition, exception, or overview decomposition scope | new time-specific witnesses close the exact remaining `PRE`, `EXC`, `EXC_API`, or overview rows |
| `CAP-DDM` | `data_distribution_management_bounded_family.md` | `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-python-core` | `2010-core`, `time`, `scenarios` | region lifecycle, overlap routing, DDM-gated routing, and MOM behavior are already strong while the remaining rows still describe broader precondition or exception envelopes | new DDM-specific witnesses close the exact remaining bounded row kinds |
| `CAP-XML` plus `CAP-OMT` tail | `omt_xml_bounded_family.md` | `requirements/2010/hla1516_xml_detailed_reconciliation.csv`, `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`, and `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` | parser, schema, validator, and round-trip families are already strong while the remaining rows still describe one-row-per-atom XML witnesses or Annex B normalization semantics beyond the current direct proof | the repo deliberately adds curated element/type witnesses or stronger runtime normalization semantics and records them row by row |

## Current 2010 Partial Shape

The current bounded-family tails called out by the closeout docs are:

- `CAP-XML`: `364 partial`
- `CAP-SUP`: `129 partial`
- `CAP-OM`: `102 partial`
- `CAP-FM`: `79 partial`
- `CAP-TM`: `58 partial`
- `CAP-FW`: `41 partial`
- `CAP-OMT`: `2 partial`

Treat those counts as current bounded inventory, not as proof that the owner
surfaces are vague or unfinished.

## Current 2010 Planned Inventory

The current `2010` packet now has `0` `planned` rows.

The former OMT placeholder inventory is now settled explicitly instead of
remaining as static matrix planning rows:

### Former OMT/FOM area placeholders now `pass`: `5`

- `REQ-OMT-4_1-object_model_identification`
- `REQ-OMT-4_8-user_supplied_tag_table`
- `REQ-OMT-5-lexicon`
- `REQ-OMT-6-conformance`
- `REQ-OMT-Annex_D-dif`

These packet-level areas now aggregate direct clause-level proof from the
curated `1516.2` reconciliation rows.

### Former OMT/FOM area placeholders now `partial`: `7`

- `REQ-OMT-4_9-synchronization_table`
- `REQ-OMT-4_10-transportation_type_table`
- `REQ-OMT-4_11-update_rate_table`
- `REQ-OMT-4_12-switches_table`
- `REQ-OMT-4_13-datatype_table`
- `REQ-OMT-4_14-notes_table`
- `REQ-OMT-Annex_E-schema`

These rows are no longer planned.
They now reflect the honest bounded status of the underlying clause-level
evidence: direct support exists, but the current family still includes bounded
tails that keep the aggregated area row `partial`.

### Schema-conformance slice now `implemented-slice`: `1`

- `REQ-OMT-SCHEMA-001`

This row is now an explicit executable Annex E schema-family witness rather
than a planning note.

Primary source:

- `analysis/compliance/requirements_matrix_2010.csv`

Likely owner path:

- `docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md`
- `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`
- `requirements/2010/hla1516_xml_detailed_reconciliation.csv`

## Recommended Planned-Row Burn-Down Order

There are no remaining `2010` `planned` rows to burn down.

If leadership wants to tighten the remaining bounded `partial` OMT/XML rows
instead of leaving them as an explicit final owner surface, use this order:

1. tighten the `REQ-OMT-Annex_E-schema` plus `CAP-XML` family only if the repo
   is willing to fund one-row-per-element or one-row-per-type curated witnesses
2. tighten the `REQ-OMT-4_9` through `REQ-OMT-4_14` area rows only if the repo
   wants each currently bounded clause family to move beyond its present
   aggregated `partial` reading

Reason:

- the remaining non-OMT family-summary rows have already been converted into
  explicit bounded `partial` owner claims
- the remaining OMT/XML rows are no longer planned inventory
- the remaining work is about whether to fund narrower direct proof for bounded
  `partial` families, not about hidden planning placeholders

## Recommended Execution Order

If leadership wants the strongest next-step `2010` tightening without
pretending the bounded state is ambiguous, use this order:

1. revisit mixed-backend priority rows only if backend-resolution truth
   materially changes or leadership explicitly wants a narrower Python-only
   claim

Reason:

- mixed-backend rows are the sharpest place where backend-resolution truth
  still blocks broader canonical movement
- support, time, federation management, ownership, and DDM have now been
  re-audited into explicit maintained bounded families
- XML/OMT has now also been re-audited into the final maintained bounded
  family tail, leaving only revisit-only backend-resolution work if later
  vendor truth changes

## Work Rules

When changing any `2010` bounded bucket:

1. update the family or priority companion CSV first
2. update the bounded owner doc second
3. record the narrowest owning shard from
   [`../verification/shard_registry.md`](../verification/shard_registry.md)
4. keep backend divergence in explicit backend-resolution surfaces
5. refresh any affected spreadsheet export or vendor/backend disposition
   artifacts when the Python proof changes their honest status

## Related Docs

- [PLN-004_python_rti_100_percent_compliance_plan.md](PLN-004_python_rti_100_percent_compliance_plan.md)
- [requirements_remaining_closure.md](requirements_remaining_closure.md)
- [requirements_completion_audit.md](requirements_completion_audit.md)
- [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md)
- [../requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md](../requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md)
- [../requirements/ieee-1516-2010/federation_management_bounded_family.md](../requirements/ieee-1516-2010/federation_management_bounded_family.md)
- [../requirements/ieee-1516-2010/declaration_management_bounded_family.md](../requirements/ieee-1516-2010/declaration_management_bounded_family.md)
- [../requirements/ieee-1516-2010/object_management_bounded_family.md](../requirements/ieee-1516-2010/object_management_bounded_family.md)
- [../requirements/ieee-1516-2010/ownership_management_bounded_family.md](../requirements/ieee-1516-2010/ownership_management_bounded_family.md)
- [../requirements/ieee-1516-2010/time_management_bounded_family.md](../requirements/ieee-1516-2010/time_management_bounded_family.md)
- [../requirements/ieee-1516-2010/data_distribution_management_bounded_family.md](../requirements/ieee-1516-2010/data_distribution_management_bounded_family.md)
- [../requirements/ieee-1516-2010/support_services_bounded_family.md](../requirements/ieee-1516-2010/support_services_bounded_family.md)
- [../requirements/ieee-1516-2010/omt_xml_bounded_family.md](../requirements/ieee-1516-2010/omt_xml_bounded_family.md)
- [../verification/shard_registry.md](../verification/shard_registry.md)
