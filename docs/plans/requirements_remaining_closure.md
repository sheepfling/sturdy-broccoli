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

## Requirements Matrix Shape

Use one matrix model for both editions:

- `shards` are the executable ownership units
- `views` are overlapping requirement-oriented or audit-oriented cuts
- every runnable check belongs to at least one canonical shard
- requirement rows may map to multiple shards when proof spans more than one lane
- views must never replace shard ownership for CI or repo-green
- the canonical requirement status is not the same thing as backend resolution
- keep backend results in separate columns or companion artifacts such as
  `python_runtime_disposition`, `pitch_runtime_disposition`, `certi_runtime_disposition`,
  route-parity ledgers, or vendor gap profiles
- do not overload one `status` cell to mean both requirement closure and
  backend-by-backend support

Treat this as the preferred column shape for closure tracking tables, proof
notes, or generated rollups:

| Column | Meaning |
| --- | --- |
| `Edition` | `2010` or `2025` |
| `Requirement family` | clause, capability family, or grouped worklist bucket |
| `Requirement IDs` | exact requirement IDs or grouped row identifiers being closed |
| `Canonical status` | `planned`, `partial`, `mapped`, `covered`, `duplicate/umbrella`, or `retired/legacy-only` |
| `Backend resolution` | separate backend-specific result columns or a linked backend-resolution artifact |
| `Primary shard` | the first canonical runnable shard that owns the proof |
| `Widen to` | broader shard or lane only when the requirement claim crosses that boundary |
| `View tags` | overlapping audit cuts such as `ownership`, `transport`, `setup-preflight`, `save-restore`, `omt`, or `finish-line` |
| `Primary command` | stable operator command for the owning shard |
| `Evidence artifact` | exact doc, ledger, JSON, CSV, or proof note to update |
| `Notes / boundary` | honest scope note when the evidence is bounded rather than full-surface |

Practical rules:

1. if a thing needs a stable command and pass/fail meaning, model it as a shard
2. if a thing overlaps multiple shards and mostly answers audit questions, model it as a view
3. keep shard names stable for juniors, CI, and restart docs
4. let view tags overlap freely, but do not let them redefine repo-green
5. when a row changes canonical status, record the exact shard command that justified the change
6. when backend support differs, spell it out in backend-specific columns instead of compressing it into one status word

Recommended starter `view tags` for this repo:

- `2010-core`
- `2025-core`
- `transport`
- `setup-preflight`
- `java-shim`
- `cpp-shim`
- `ownership`
- `time`
- `save-restore`
- `fom-omt`
- `scenarios`
- `finish-line`

Example shape:

| Edition | Requirement family | Requirement IDs | Canonical status | Backend resolution | Primary shard | Widen to | View tags | Primary command | Evidence artifact | Notes / boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025` | FI Ownership group | grouped ownership worklist rows | `planned` | `python=covered`, `Pitch=planned`, `CERTI=not-applicable` in the linked disposition ledger until each backend closes | `unit-python-2025-core` | `python1516_2025-routes` | `2025-core`, `ownership` | `./tools/test-focus run python-2025-ownership` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | widen only when hosted replay matters |
| `2025` | hosted FedPro parity | `HLA2025-BND-003` and route-parity rows | `partial` | backend/route resolution lives in the route-parity and hosted-boundary artifacts, not the canonical status cell | `unit-transport-local` | `python1516_2025-routes` | `transport`, `2025-core`, `finish-line` | `./tools/test-surface run transport` | `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md` | bounded hosted-route parity, not a second RTI |
| `2010` | Clause 10 Support Services | grouped support-family rows | `partial` | `python=verified`; vendor-specific differences stay in `requirements_matrix_2010.*` and backend disposition ledgers | `unit-python-core` | `python1516_2025-main` only if shared runtime code changes | `2010-core`, `setup-preflight` | `python3 -m pytest tests/backends/test_python_backend_support_services.py tests/scenarios/test_support_services_backend_matrix.py` | `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` | keep row `partial` if proof only covers narrower supported scope |

## 2010 Remaining Closure

The `2010` surface is structurally linked and collected.
The remaining `2010` `partial` rows are now all owned by maintained bounded
family notes or backend-resolution companions rather than active closeout
buckets.

Current imported-master status from
[`../../requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`](../../requirements/2010/hla_1516_master_harmonization_index_v1_0.csv):

- `2675 mapped`
- `1328 partial`
- `0 unreconciled`

### 2010 Exact Planned Rows

There are no remaining direct `planned` clause rows in the curated `2010`
source ledgers.

There are also no remaining active `2010` closeout buckets in this note.

The remaining `2010` truth shape is now:

1. maintained bounded mixed-backend rows owned by
   `hla1516_1_priority_backend_resolution.csv` plus
   `mixed_backend_priority_boundaries.md`
2. maintained bounded partial-family notes for `CAP-FM`, `CAP-DM`, `CAP-SUP`,
   `CAP-OM`, `CAP-OWN`, `CAP-TM`, and `CAP-DDM`
3. the maintained bounded `CAP-XML` plus narrow `CAP-OMT` owner note in
   `omt_xml_bounded_family.md`

Exact current reading from the backend-compliance packet:

- `48` `partial` rows total
- `35` `partial` rows where Python is already `verified`
- `0` `partial` rows where Python is still `vendor-divergent`
- `13` `partial` rows where Python is `not-applicable`
- only `3` requirement rows remain as direct mixed-backend clause tails:
  - `HLA1516.1-FM-4.1.5-001`
  - `HLA1516.1-FM-4.1.5-002`
  - `HLA1516.1-TM-8.1.2-003`
- the defended subset packet now also exposes:
  - `9` bounded broad partial parents
  - `23` passing supported-subset child proofs
- current `vendor-divergent` composition:
  - `0` supported-subset policy parents from `curated-clause5-6`
- the framework umbrella owner file
  [`../../requirements/2010/hla1516_framework_detailed_reconciliation.csv`](../../requirements/2010/hla1516_framework_detailed_reconciliation.csv)
  remains part of the canonical 2010 owner map, but its narrowed top-level rows are no longer part of the live Python vendor-divergent residual set

### 2010 Largest Partial Families

These families still carry `partial` rows in the canonical ledgers, but they
are no longer active navigation or ownership gaps:

- `CAP-XML`: `364 partial`
- `CAP-SUP`: `129 partial`
- `CAP-OM`: `98 partial`
- `CAP-FM`: `109 partial`
- `CAP-TM`: `58 partial`
- `CAP-FW`: `41 partial`
- `CAP-OMT`: `2 partial`

Practical reading:

- `planned` means direct proof is still missing
- `partial` means there is already some link or test anchor, but the row still
  overstates what the current proof can honestly defend
- these `2010` partials now live behind explicit bounded owner notes rather
  than in an active open-bucket queue
- use the `policy_parents` export surface when the question is whether a `2010`
  partial row is a defended supported-subset boundary versus an unresolved
  Python execution gap
- use the family owner notes and framework reconciliation companion when the
  question is which `vendor-divergent` rows are still true closeout blockers
  versus already-settled bounded owner surfaces

### 2010 Finish Reading

Use this order:

1. treat the bounded owner notes as the canonical final-state reading for the
   remaining `2010` partial rows
2. reopen a `2010` bucket only if the repo deliberately expands scope with
   narrower direct row proofs or broader backend/runtime semantics

### 2010 Suggested Shards And Views

Use the smallest proof shard or focused view that matches the requirement
family before falling back to a broader lane:

| Requirement family | Owner doc | Owner companion | Primary shard | Primary command | Widen to | View tags | Evidence artifact to update | Notes / boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bounded mixed-backend Federation Management rows | `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md` | `requirements/2010/hla1516_1_priority_backend_resolution.csv` plus `requirements/2010/traceability_matrix.csv` | `unit-scenarios-light` | `python3 -m pytest tests/scenarios/test_federation_management_backend_matrix.py -q -k 'test_python_connection_lost_callback_matrix or test_python_backend_lost_federate_mom_matrix'` | `./tools/test-focus run save-restore-2025` only if future backend evidence or scenario semantics materially change the row | `2010-core`, `scenarios`, `save-restore` | `requirements/2010/hla1516_1_priority_backend_resolution.csv`, `requirements/2010/traceability_matrix.csv`, `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless broader backend parity is intentionally reopened |
| bounded mixed-backend Time Management row | `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md` | `requirements/2010/hla1516_1_priority_backend_resolution.csv` plus `requirements/2010/traceability_matrix.csv` | `unit-python-core` | `python3 -m pytest tests/time/test_section8_backend_matrix.py -q -k test_section8_backend_matrix_order_override_services` | `./tools/test-focus run python-2025-time` only if future backend evidence materially changes the row | `2010-core`, `time` | `requirements/2010/hla1516_1_priority_backend_resolution.csv`, `requirements/2010/traceability_matrix.csv`, `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless broader backend parity is intentionally reopened |
| `CAP-FM` partials | `docs/requirements/ieee-1516-2010/federation_management_bounded_family.md` | `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-scenarios-light` | `python3 -m pytest tests/backends/test_python_backend_federation_extended.py tests/verification/test_requirements_ledger_v013.py` | `./tools/test-surface run scenarios` only if future row-level decomposition or Clause 4 scenario scope materially changes | `2010-core`, `scenarios` | `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/federation_management_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger row-level proof scope is intentionally reopened |
| `CAP-DM` partials | `docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md` | `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-foundation` | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/backends/test_python_backend_time_ddm_extended.py` | `./tools/test-surface run scenarios` only if future precondition-envelope scope, exception-envelope scope, or multi-federate declaration composition materially changes | `2010-core`, `setup-preflight`, `scenarios` | `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger isolated row proof is intentionally reopened |
| `CAP-SUP` partials | `docs/requirements/ieee-1516-2010/support_services_bounded_family.md` | `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-python-core` | `python3 -m pytest tests/backends/test_python_backend_support_services.py tests/scenarios/test_support_services_backend_matrix.py` | `./tools/python verify-main-2025` only if future per-service negative-matrix scope or shared runtime support helpers materially change | `2010-core`, `setup-preflight` | `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/support_services_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger per-service negative-path proof is intentionally reopened |
| `CAP-OM` partials | `docs/requirements/ieee-1516-2010/object_management_bounded_family.md` | `requirements/2010/hla1516_1_om_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-scenarios-light` | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_requirements_ledger_v013.py` | `./tools/test-surface run scenarios` only if future callback-order isolation, effect-vector scope, or supported-transport-subset claims materially change | `2010-core`, `scenarios` | `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/object_management_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger isolated row proof is intentionally reopened |
| `CAP-OWN` partials | `docs/requirements/ieee-1516-2010/ownership_management_bounded_family.md` | `requirements/2010/hla1516_1_own_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-scenarios-light` | `python3 -m pytest tests/backends/test_python_backend_object_ownership_extended.py tests/scenarios/test_ownership_management_backend_matrix.py` | `./tools/test-focus run python-2025-ownership` only if future precondition-envelope scope, exception-envelope scope, or broader ownership gauntlet composition materially changes | `2010-core`, `ownership`, `scenarios` | `requirements/2010/hla1516_1_own_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/ownership_management_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger isolated row proof is intentionally reopened |
| `CAP-TM` partials | `docs/requirements/ieee-1516-2010/time_management_bounded_family.md` | `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-python-core` | `python3 -m pytest tests/time/test_mom_mim_time_v10.py tests/time/test_mom_mim_and_time_semantics_v010.py tests/time/test_mom_mim_time_management_v010.py` | `./tools/test-focus run python-2025-time` only if future precondition-envelope scope, exception-envelope scope, or overview decomposition materially changes | `2010-core`, `time` | `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/time_management_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger isolated row proof is intentionally reopened |
| `CAP-DDM` partials | `docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md` | `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv` plus `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-python-core` | `python3 -m pytest tests/backends/test_python_backend_time_ddm_extended.py tests/verification/test_compliance_slice_v011.py` | `./tools/test-surface run scenarios` only if future precondition-envelope scope, exception-envelope scope, or region-gated routing composition materially changes | `2010-core`, `time`, `scenarios` | `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless stronger isolated row proof is intentionally reopened |
| `CAP-XML` and `CAP-OMT` partials | `docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md` | `requirements/2010/hla1516_xml_detailed_reconciliation.csv` plus `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv` and `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` | `unit-fom-tooling` | `python3 -m pytest tests/factories/test_fom_omt_parsing.py tests/factories/test_fom_validate.py tests/mom/test_mom_catalog_validation_v012.py` | `./tools/test-surface run unit-fom-tooling` for parser/validator/workbench cross-checks | `2010-core`, `fom-omt` | `requirements/2010/hla1516_xml_detailed_reconciliation.csv`, `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`, `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`, `docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md` | maintained bounded owner note, not an active remaining-closeout bucket, unless the repo deliberately expands to one-row-per-atom XML witnesses or stronger runtime normalization semantics |

## 2025 Remaining Closure

The `2025` surface is structurally linked and collected.
The grouped harmonization worklist is now fully dispositioned.
There are no remaining active `2025` closeout buckets in this note.
The remaining `2025` non-plain-covered rows are now maintained through owner
notes for umbrella rows, retired rows, backend-resolution lanes, route-bounded
claims, and tolerance-only boundaries.

Current grouped closure state from
[`../../requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`](../../requirements/2025/harmonization/hla_2025_harmonization_worklist.csv):

- `57 covered`
- `5 duplicate/umbrella`
- `2 retired/legacy-only`
- `0 planned`
- `0 partial`

### 2025 Grouped Result

There are no remaining grouped `planned` or `partial` rows in the committed
2025 harmonization worklist.

That means the grouped owner layer now agrees with the row-level harmonization
ledger for:

- FI service families
- OMT validator-negative families
- OMT component-level conformance families
- SOM/FOM service-usage cross-check families

### 2025 Maintained Boundary Classes

The remaining `2025` non-plain-covered rows are now concentrated in these
classes:

- `duplicate/umbrella`
  - framework umbrella rules
  - callback/configuration/binding delta groups
- `retired/legacy-only`
  - legacy FI API candidates
  - legacy OMT schema candidates
- bounded route/binding claim surfaces
  - hosted FedPro
  - Java/C++ standard bindings
  - Pitch proto HLA 4 / `202X` comparison lane
- explicit row-level supported-scope limits that remain intentionally narrower
  than a blanket all-covered IEEE 1516.1-2025 claim

Exact current reading:

- row-level non-`covered` denominator outside the active direct-support set:
  - `22` `duplicate/umbrella`
  - `24` `retired/legacy-only`
- grouped non-`covered` buckets:
  - `5` `duplicate/umbrella`
  - `2` `retired/legacy-only`
- these are maintained owner classifications, not missing grouped proof buckets

### 2025 Non-Standalone Groups

These should not be mistaken for missing runtime behavior until their role is
normalized:

- `duplicate/umbrella`
  - framework umbrella rules
  - callback/configuration/binding delta groups
- `retired/legacy-only`
  - legacy FI API candidates
  - legacy OMT schema candidates

### 2025 Finish Reading

Use this order:

1. keep the grouped 2025 worklist synchronized with the row-level ledger
2. read umbrella, retired, route-bounded, backend-resolution, and tolerance
   rows through their canonical owner docs
3. reopen a 2025 bucket only if the repo deliberately broadens claim scope or
   a generated artifact drifts out of sync with the owner docs

### 2025 Suggested Shards And Views

Use these shards and views when maintaining the now-closed grouped `2025`
worklist and finishing the remaining 2025 claim-shape work:

| Requirement family | Owner doc | Owner companion | Primary shard | Primary command | Widen to | View tags | Evidence artifact to update | Notes / boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grouped FI / OMT / SOM-FOM covered buckets | `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json` and the matching bounded proof note | `unit-python-2025-core` or `unit-fom-tooling` by owner row | `./tools/python verify-main-2025` or `python3 -m pytest tests/factories/test_fom_validate.py tests/factories/test_fom_omt_parsing.py` | widen only if a covered row is being broadened beyond its current bounded note | `2025-core`, `finish-line`, `fom-omt`, `scenarios` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`, `requirements/2025/harmonization/hla_2025_requirement_coverage_rollup.json`, matching bounded proof note | grouped closure is done; future edits should keep the grouped owner in sync with the row-level ledger rather than reopening stale partial/planned buckets |
| duplicate/umbrella framework rows | `docs/requirements/ieee-1516-2025/framework_rules.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | `unit-python-2025-core` | `./tools/python verify-main-2025` | `./tools/python verify-routes-2025` only if a framework umbrella row is being turned into hosted-route-backed proof | `2025-core`, `finish-line`, `scenarios` | `docs/requirements/ieee-1516-2025/framework_rules.md`, `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | framework rows remain parent normalization aids unless their child runtime or OMT rows are split into narrower direct claims |
| duplicate/umbrella callback-binding groups | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv` | `unit-shim-tooling` | `./tools/test-surface run unit-shim-tooling` | `./tools/python verify-routes-2025` only if the umbrella row is being turned into a route-backed proof claim | `2025-core`, `java-shim`, `cpp-shim`, `transport` | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md`, `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | umbrella rows stay boundary notes unless deliberately split into narrower executable claims |
| retired/legacy-only groups | `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | `unit-foundation` | `python3 -m pytest tests/test_documentation_policy.py tests/verification/test_imported_hla_packet_backlog.py` | widen only if the retired mapping changes generated audits or requirement ledgers | `2025-core`, `setup-preflight` | `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md`, `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | these are exclusion and mapping rows, not runtime behavior claims |
| binding / hosted-route bounded claims | `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md` | route-parity artifacts plus `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` and `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv` | `unit-transport-local` | `./tools/test-surface run transport` | widen only if the repo intentionally expands bounded adaptation evidence into broader behavior-equivalence claims | `2025-core`, `transport`, `java-shim`, `cpp-shim`, `finish-line` | `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`, route-parity artifacts | keep these as bounded adaptation or hosted-transport evidence unless a stronger broader claim is intentionally proven |
| Pitch proto HLA 4 / `202X` backend-resolution lane | `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md` | `requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv` plus `requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv` and the grouped `pitch_202x_resolution` field in `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | `unit-transport-local` | `./tools/test-surface run transport` | widen only if the repo intentionally expands the bounded comparison into a broader vendor-runtime comparison program | `2025-core`, `transport`, `java-shim`, `finish-line` | `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`, `requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`, `requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv` | keep Pitch as a backend-resolution reading, not canonical requirement status, unless a stronger vendor-runtime comparison scope is intentionally added |

## Recommended Cross-Edition Finish Order

If the goal is the shortest truthful path to "done", use this order:

1. synchronize any stale 2025 audit or closure-report artifacts with the current row-level ledger and owner-doc state
2. final boundary cleanup for `2025` umbrella and retired rows
3. `2010` high-volume partial capability families outside `CAP-FM`, `CAP-SUP`, `CAP-OM`, `CAP-TM`, `CAP-DM`, `CAP-DDM`, and `CAP-OWN`
4. bounded 2025 route/binding claim decisions if broader than bounded claims are wanted

## Shard Rule

For every remaining category above:

1. start with the narrowest listed shard or focused view
2. promote to a broader lane only when the requirement claim itself crosses that boundary
3. when a row moves from `planned` to `partial` or `mapped`, record the exact shard or command that proved it

## Done Criteria

Treat this closeout as finished only when:

1. every remaining `2010` bounded mixed-backend or partial row is either closed or intentionally bounded with explicit proof
2. the grouped `2025` worklist stays fully dispositioned and synchronized with the row-level ledger
3. older generated 2025 closure reports do not silently disagree with the current row-level audit and owner-doc state
4. `partial` or bounded rows in both editions are reduced to intentionally bounded supported-scope claims rather than accidental under-testing
5. the supporting docs and ledgers still pass the documentation and traceability checks

## Related Docs

- [`requirements_finish_line.md`](requirements_finish_line.md)
- [`2025_requirements_finish_line.md`](2025_requirements_finish_line.md)
- [`imported_requirements_backlog_v1_0.md`](imported_requirements_backlog_v1_0.md)
