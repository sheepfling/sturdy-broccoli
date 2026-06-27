# Requirements Gap Register

Use this page when the question is:

- what exact proof is still missing for each open requirement bucket?
- which shard should close it first?
- what specific exit condition would let us mark the bucket finished?

This is the operational companion to
[`requirements_completion_audit.md`](requirements_completion_audit.md).

## How To Read This

Each row below is an actively open bucket.
Settled bounded owner notes that already have their intended final reading
should stay out of this table unless a deliberate scope expansion or evidence
change reopens them.

- `Owner doc` names the human-facing canonical reading for the open bucket
- `Owner companion` names the source ledger, backend-resolution companion, or
  row-level harmonization artifact that must stay aligned with that owner doc
- `Current evidence` names the strongest current proof shape already present
- `Missing proof to close` names the exact remaining gap
- `Exit condition` states what must become true before the bucket can move out
  of the open set

Do not promote a bucket just because nearby implementation exists.
Promote it only when the exit condition is actually proven.

Keep these roles separate:

- use the owner doc to explain the bounded or still-open claim honestly
- use the owner companion to carry canonical row state or backend-resolution
  detail
- update both when the bucket changes materially

## 2010 Gap Register

There are no active `2010` open buckets in this register.

The focused `2010` backend-compliance packet now has `0` `partial` rows.
Maintained boundary notes and backend-resolution companions still exist, but
they are no longer packet-open partials.

The `2010` backend-compliance packet no longer carries any `planned`
inventory rows.
The former OMT placeholder rows are not treated as active open buckets in this
register because they are now classified explicitly in
[`2010_python_rti_bounded_family_execution_worklist.md`](2010_python_rti_bounded_family_execution_worklist.md)
as:

- `20` `pass` OMT/XML area rows
- `3` `implemented-slice` OMT/XML execution witnesses
- `0` remaining OMT/XML area partial placeholders

Use that worklist when the question is whether to tighten those bounded rows
further.
Use this gap register only when one of those classes becomes an actively opened
closeout bucket with a specific owner doc, owner companion, and exit
condition.

Scope-expansion candidates and recent decisions under the current honest-`100%`
program:

| Bucket | Owner doc | Owner companion | Current evidence | Missing proof to close | Exit condition |
| --- | --- | --- | --- | --- | --- |
| 2010 mixed-backend priority rows | `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md` | `requirements/2010/hla1516_1_priority_backend_resolution.csv` plus `requirements/2010/traceability_matrix.csv` | Canonical owner rows are closed and backend-resolution truth is explicit | materially broader cross-backend evidence only if the repo wants a parity claim beyond the current owner surface | owner rows stay `pass` while backend-resolution truth remains explicit in the companion ledger |

Latest investigated decision:

- on `2026-06-27`, the `2010 mixed-backend priority rows` bucket was re-audited
  and kept as an explicit bounded/backend-resolution surface
- the current owner doc, backend-resolution ledger, traceability rows, and
  targeted owning shard commands all support that reading
- the canonical rows are now already closed for the repo-supported claim, so
  the remaining work would only be broader cross-backend parity expansion
- treat this bucket as maintained boundary documentation unless later backend
  evidence materially changes the mixed-backend dispositions or leadership
  explicitly wants a narrower Python-only claim
- on `2026-06-26`, the `2010 CAP-SUP bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard command all support that reading
- the current tail remains a uniform bounded `43 PRE`, `43 EXC`, and
  `43 EXC_API` negative-envelope family
- no narrower direct claim was identified that would preserve the current
  Clause 10 row meanings without adding new exhaustive per-service
  negative-matrix proof
- treat this bucket as maintained boundary documentation unless future
  per-service negative-matrix evidence materially changes the bounded family
  disposition or leadership explicitly funds that tighter proof scope
- on `2026-06-26`, the `2010 CAP-DM bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard commands all support that reading
- the current tail remains a stable bounded `12 PRE`, `12 EXC`, and
  `14 EXC_API` Clause 5 family envelope
- no narrower direct claim was identified that would preserve the current
  Clause 5 row meanings without adding new isolated per-row precondition or
  negative-path proof
- treat this bucket as maintained boundary documentation unless future Clause 5
  witnesses materially change the bounded family disposition or leadership
  explicitly funds that tighter proof scope
- on `2026-06-26`, the `2010 CAP-TM bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard command all support that reading
- the current tail remains a stable bounded `19 PRE`, `19 EXC`, `19 EXC_API`,
  and `1 OVW` Clause 8 family envelope
- no narrower direct claim was identified that would preserve the current
  Clause 8 row meanings without adding new isolated per-row negative or
  overview-decomposition proof
- treat this bucket as maintained boundary documentation unless future
  isolated Clause 8 witnesses materially change the bounded family disposition
  or leadership explicitly funds that tighter proof scope
- on `2026-06-26`, the `2010 CAP-FM bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard commands all support that reading
- the current tail remains a stable bounded `43 ARG`, `23 EFF`, `17 CB_ORD`,
  `15 EXC`, and `11` residual Clause 4 family envelope
- no narrower direct claim was identified that would preserve the current
  Clause 4 row meanings without adding new row-level decomposition or direct
  runtime connection-loss callback proof
- treat this bucket as maintained boundary documentation unless future Clause 4
  decomposition or direct fault-surface witnesses materially change the
  bounded family disposition or leadership explicitly funds that tighter proof
  scope
- on `2026-06-26`, the `2010 CAP-OM bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard commands all support that reading
- the current tail now remains a stable bounded `10 EFF`, `25 CB_ORD`,
  `17 CB_ORDER`, `6 EXC_API`, `5 EXC`, `6 FED_CB`, and
  `1 OVW` Clause 6 family envelope
- the recent `updateAttributeValues` exception rows and the object-instance
  overload exception row for `requestAttributeValueUpdate` are no longer part
  of that bounded tail
- the `updateAttributeValues` precondition row is also no longer part of that
  bounded tail because the current direct negative-path witnesses now isolate
  the applicable connection, membership, handle-validation, ownership,
  invalid-logical-time, and save/restore guards
- the `reserveObjectInstanceName` precondition row is also no longer part of
  that bounded tail because the current direct negative-path witnesses now
  isolate the applicable connection, membership, and save or restore guards
- the `reserveObjectInstanceName` effect and exception rows are also no longer
  part of that bounded tail because the current direct naming-state and
  negative-path witnesses now isolate the supported reservation
  success-or-failure effect plus the exercised membership, connection, and
  save/restore failures while intentionally excluding unimplemented
  `IllegalName` throwing
- the `registerObjectInstance` precondition row is also no longer part of that
  bounded tail because the current direct negative-path witnesses now isolate
  the applicable connection, membership, duplicate-name, and save or restore
  guards across the exercised overloads
- the `registerObjectInstance` effect and exception rows are also no longer
  part of that bounded tail because the current direct positive and
  negative-path witnesses now isolate object creation plus discovery
  eligibility and the exercised class-definition, strict-publication,
  duplicate-name, membership, connection, and save/restore failures
- the `releaseObjectInstanceName` precondition row is also no longer part of
  that bounded tail because the current direct negative-path witnesses now
  isolate the applicable connection, membership, and save or restore guards
- the `releaseObjectInstanceName` effect and exception rows are also no longer
  part of that bounded tail because the current direct naming-state and
  negative-path witnesses now isolate the supported reservation-release effect
  plus the exercised membership, connection, and save/restore failures while
  intentionally excluding unimplemented `ObjectInstanceNameNotReserved`
  throwing
- the `localDeleteObjectInstance` precondition row is also no longer part of
  that bounded tail because the current direct negative-path witnesses now
  isolate the applicable connection, membership, object-knownness,
  ownership-state, and save/restore guards
- the `localDeleteObjectInstance` effect and exception rows are also no longer
  part of that bounded tail because the current direct lifecycle and
  negative-path witnesses now isolate the supported local-knowledge-only
  effect plus the exercised pending-acquisition, ownership, object-knownness,
  membership, connection, and save/restore failures
- the `deleteObjectInstance` precondition row is also no longer part of that
  bounded tail because the current direct negative-path witnesses now isolate
  the applicable connection, membership, object-knownness, delete-privilege,
  and save or restore guards
- the `deleteObjectInstance` effect and exception rows are also no longer part
  of that bounded tail because the current direct lifecycle and negative-path
  witnesses now isolate the supported known-object removal effect plus the
  exercised privilege, object-knownness, membership, connection, save/restore,
  and invalid-logical-time failures
- the `sendInteraction` precondition row is also no longer part of that
  bounded tail because the current direct negative-path witnesses now isolate
  the applicable connection, membership, publication-state, handle-validation,
  and invalid-logical-time guards across the exercised overloads, while the
  broader save or restore wording stays bounded separately
- the multiple-name reservation and release precondition rows are also no
  longer part of that bounded tail because the current direct negative-path
  witnesses now isolate the applicable connection, membership, and
  save/restore guards
- the `reserveMultipleObjectInstanceName` effect and exception rows are also
  no longer part of that bounded tail because the current direct naming-state
  and negative-path witnesses now isolate the supported coordinated
  reservation effect plus the exercised membership, connection, and
  save/restore failures while intentionally excluding unimplemented
  `IllegalName`, `NameSetWasEmpty`, and `RTIinternalError` throwing
- the `releaseMultipleObjectInstanceName` effect and exception rows are also
  no longer part of that bounded tail because the current direct naming-state
  and negative-path witnesses now isolate the supported reservation-release-set
  effect plus the exercised membership, connection, and save/restore failures
  while intentionally excluding unimplemented
  `ObjectInstanceNameNotReserved` throwing
- the `requestAttributeValueUpdate` precondition row is also no longer part of
  that bounded tail because the current direct negative-path witnesses now
  isolate the applicable connection, membership, handle-validation, and
  save/restore guards across both overloads
- the class-wide `requestAttributeValueUpdate` exception rows are also no
  longer part of that bounded tail because the backend now surfaces the
  imported `ObjectClassNotDefined` failure on the exercised class-wide
  overload
- no narrower direct claim was identified that would preserve the current
  Clause 6 row meanings without adding new isolated per-row callback-order,
  effect-vector, or negative-path proof
- treat this bucket as maintained boundary documentation unless future Clause 6
  witnesses materially change the bounded family disposition or leadership
  explicitly funds that tighter proof scope
- on `2026-06-26`, the `2010 CAP-OWN bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard commands all support that reading
- the current tail remains a stable bounded `8 PRE`, `11 EXC`, and
  `11 EXC_API` Clause 7 family envelope
- no narrower direct claim was identified that would preserve the current
  Clause 7 row meanings without adding new isolated per-row negative-path
  proof
- treat this bucket as maintained boundary documentation unless future Clause 7
  negative-path witnesses materially change the bounded family disposition or
  leadership explicitly funds that tighter proof scope
- on `2026-06-26`, the `2010 CAP-DDM bounded family` was also re-audited and
  kept as an explicit bounded family surface
- the current owner doc, reconciliation companion, reconciliation verifier,
  and owning shard commands all support that reading
- the current tail now remains a stable bounded `6 EXC` and `10 EXC_API`
  Clause 9 family envelope
- no narrower direct claim was identified that would preserve the current
  Clause 9 row meanings without adding new isolated per-row negative-path
  proof
- treat this bucket as maintained boundary documentation unless future Clause 9
  negative-path witnesses materially change the bounded family disposition or
  leadership explicitly funds that tighter proof scope
- on `2026-06-26`, the `2010 CAP-XML / CAP-OMT bounded family` was also
  re-audited and kept as an explicit bounded family surface
- the current owner doc, reconciliation companions, reconciliation verifiers,
  and owning shard command all support that reading
- the current XML tail remains a stable bounded `274 XML_ELEM`, `89 XML_TYPE`,
  and `1 CLAUSE12_13_DETAIL` envelope
- the current OMT tail remains a stable bounded `2` Annex B normalization-row
  envelope
- no narrower direct claim was identified that would preserve the current XML
  and OMT row meanings without adding new one-row-per-element, one-row-per-
  type, or stronger executable normalization proof
- treat this bucket as maintained boundary documentation unless future XML atom
  witnesses or stronger runtime normalization proof materially change the
  bounded family disposition or leadership explicitly funds that tighter proof
  scope

Settled but still useful reference:

- `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`
  plus `requirements/2010/hla1516_1_priority_backend_resolution.csv` remain
  the canonical place to read the three 2010 mixed-backend clause rows.
  They are intentionally bounded `partial` rows, but not active open buckets in
  this register unless future backend evidence reopens them.
- `docs/requirements/ieee-1516-2010/federation_management_bounded_family.md`
  plus `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` remain the
  canonical place to read the `CAP-FM` partial family. It is intentionally
  bounded at the current harmonization and granularity limits, but not an
  active open bucket in this register unless future row-level decomposition or
  stronger proof scope reopens it.
- `docs/requirements/ieee-1516-2010/support_services_bounded_family.md` plus
  `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` remain the
  canonical place to read the `CAP-SUP` partial family. It is intentionally
  bounded at the current negative-path granularity limits, but not an active
  open bucket in this register unless future per-service exhaustive negative
  matrices or stronger proof scope reopen it.
- `docs/requirements/ieee-1516-2010/object_management_bounded_family.md` plus
  `requirements/2010/hla1516_1_om_detailed_reconciliation.csv` remain the
  canonical place to read the `CAP-OM` partial family. It is intentionally
  bounded at the current callback-order, negative-envelope, effect-vector, and
  supported-subset limits, but not an active open bucket in this register
  unless future isolated witnesses or stronger proof scope reopen it.
- `docs/requirements/ieee-1516-2010/time_management_bounded_family.md` plus
  `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv` remain the
  canonical place to read the `CAP-TM` partial family. It is intentionally
  bounded at the current precondition-envelope, exception-envelope, and
  overview-granularity limits, but not an active open bucket in this register
  unless future isolated witnesses or stronger proof scope reopen it.
- `docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md`
  plus `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv` remain the
  canonical place to read the `CAP-DM` partial family. It is intentionally
  bounded at the current precondition-envelope and exception-envelope limits,
  but not an active open bucket in this register unless future isolated
  witnesses or stronger proof scope reopen it.
- `docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md`
  plus `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv` remain
  the canonical place to read the `CAP-DDM` partial family. It is intentionally
  bounded at the current precondition-envelope and exception-envelope limits,
  but not an active open bucket in this register unless future isolated
  witnesses or stronger proof scope reopen it.
- `docs/requirements/ieee-1516-2010/ownership_management_bounded_family.md`
  plus `requirements/2010/hla1516_1_own_detailed_reconciliation.csv` remain
  the canonical place to read the `CAP-OWN` partial family. It is intentionally
  bounded at the current precondition-envelope and exception-envelope limits,
  but not an active open bucket in this register unless future isolated
  witnesses or stronger proof scope reopen it.
- `docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md` plus
  `requirements/2010/hla1516_xml_detailed_reconciliation.csv`,
  `requirements/2010/hla1516_2_omt_detailed_reconciliation.csv`, and
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv` remain the
  canonical place to read the `CAP-XML` and narrow `CAP-OMT` partial tails.
  They are intentionally bounded at the current XML atom-granularity and Annex
  B normalization-semantics limits, but not an active open bucket in this
  register unless future row-level witnesses or stronger runtime normalization
  scope reopen them.

## 2025 Gap Register

There are no active `2025` open buckets in this register.

The remaining `2025` rows that are not plain `covered` runtime claims are now
all owned by explicit umbrella, exclusion, backend-resolution, route-bounded,
or tolerance-only owner notes.
Those rows stay out of the active gap table unless a deliberate scope expansion
or evidence change reopens them.

Maintained optional scope-expansion candidates under the current honest-`100%`
program:

| Bucket | Owner doc | Owner companion | Current evidence | Missing proof to close | Exit condition |
| --- | --- | --- | --- | --- | --- |
| 2025 callback-control umbrella slice (`HLA2025-FI-CB-002` through `HLA2025-FI-CB-004`) | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv` | child FI service rows and direct runtime tests already carry explicit EVOKED, queue-drain, and enable/disable callback evidence | narrower standalone callback-control claims that do more than summarize the child rows and are explicitly tied to their narrowest shard owners | the umbrella rows are either intentionally left as non-standalone with the current child-owner map, or replaced by narrower direct callback-control claims with explicit executable anchors and owner-doc updates |
| 2025 directed-interaction callback umbrella slice (`HLA2025-FI-CB-007`) | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus route-parity artifacts and `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv` | child directed-interaction FI rows, direct runtime tests, and hosted FedPro route-parity evidence already carry explicit directed callback semantics | narrower standalone directed-interaction callback-parameterization claims that do more than summarize the child rows and are explicitly tied to their narrowest shard owners | the umbrella row is either intentionally left as non-standalone with the current child-owner map, or replaced by a narrower direct directed-callback claim with explicit executable anchors and owner-doc updates |
| 2025 configuration/auth umbrella slice (`HLA2025-FI-CFG-001`, `HLA2025-FI-AUTH-001`) | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv` | child connect rows, factory composition tests, and hosted FedPro request-shape evidence already carry explicit configuration-result and credentials behavior | narrower standalone configuration-result or authorization-credentials claims that do more than summarize the child connect rows and are explicitly tied to their narrowest shard owners | the umbrella rows are either intentionally left as non-standalone with the current child-owner map, or replaced by narrower direct connect-auth/config claims with explicit executable anchors and owner-doc updates |
| 2025 Java/C++ binding umbrella slice (`HLA2025-BIND-JAVA-CPP-001`) | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus route-parity artifacts, shim-route evidence packets, and `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv` | child binding rows, standard-shim artifact tests, and shim-route traces already carry explicit Java/C++ wrapper-capability evidence | narrower standalone Java/C++ binding-capability claims that do more than summarize the child rows and are explicitly tied to their narrowest shard owners | the umbrella row is either intentionally left as non-standalone with the current child-owner map, or replaced by a narrower direct binding-capability claim with explicit executable anchors and owner-doc updates |
| 2025 FedPro protocol umbrella slice (`HLA2025-BIND-FEDPRO-001`) | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` | `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` plus route-parity artifacts and `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv` | hosted-route parity, protocol assets, and route matrix evidence already exist | narrower direct protocol-capability claims that separate transport adaptation proof from broad umbrella wording | the current bounded hosted-route reading is either preserved explicitly, or replaced by narrower direct FedPro protocol-capability claims with explicit proto/callback/error-mapping evidence |

Latest investigated decision:

- on `2026-06-26`, the `2025 framework umbrella rows` were re-audited and
  kept as an explicit umbrella boundary
- current framework owner docs, child-row maps, traceability anchors, and
  runtime/scenario evidence already carry the real child-proof semantics
- no narrower standalone framework claim was identified that would avoid
  double-counting existing child proof
- treat that slice as maintained boundary documentation unless later work adds
  genuinely narrower direct framework child claims
- on `2026-06-26`, the `2025 callback-control umbrella slice` was re-audited
  and kept as an explicit umbrella boundary
- current child FI service rows plus runtime and transport tests already carry
  the direct callback semantics
- no narrower standalone callback-control claim was identified that would avoid
  double-counting existing child proof
- treat that slice as maintained boundary documentation unless later work adds
  a genuinely narrower direct callback-control claim
- on `2026-06-26`, the `2025 FedPro protocol umbrella slice` was also
  re-audited and kept as an explicit bounded hosted-route boundary
- current child binding row `HLA2025-BND-003`, hosted-route owner docs, route
  parity artifacts, and transport tests already carry the real protocol-facing
  claim
- no narrower standalone FedPro protocol-capability claim was identified that
  would avoid restating existing bounded route traceability
- treat that slice as maintained boundary documentation unless later work adds
  a genuinely narrower direct protocol-capability claim
- on `2026-06-26`, the `2025 retired/legacy-only rows` were also re-audited
  and kept as an explicit exclusion boundary
- current retired owner docs, harmonization ledgers, grouped worklist rows,
  and finish-line evidence already carry the intended legacy-only reading
- no compatibility or migration mode was identified that would justify
  promoting those rows into active 2025 support claims
- treat that slice as maintained exclusion documentation unless the repo later
  deliberately opens a compatibility or migration program

Settled but still useful reference:

- `docs/requirements/ieee-1516-2025/framework_rules.md` plus
  `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`
  remain the canonical place to read the `duplicate/umbrella` framework rows.
  They are intentionally maintained as non-standalone parent rows, but not
  active open buckets in this register unless future child-claim or ownership
  changes reopen them.
- `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` plus
  `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`
  and `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv`
  remain the canonical place to read the callback/configuration/binding
  `duplicate/umbrella` rows. They are intentionally maintained as
  non-standalone delta or normalization rows, but not active open buckets in
  this register unless future child-claim or ownership changes reopen them.
- `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md` plus
  `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`
  remain the canonical place to read the `retired/legacy-only` rows. They are
  intentionally maintained as explicit exclusions, but not active open buckets
  in this register unless the repo deliberately opens a compatibility or
  migration program.
- `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`
  plus route-parity artifacts,
  `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`, and
  `requirements/2025/harmonization/hla_2025_fi_binding_surface_matrix.csv`
  remain the canonical place to read the binding and hosted-route bounded
  claims. They are intentionally maintained as bounded adaptation or
  transport-route evidence, but not active open buckets in this register
  unless the repo deliberately opens a broader behavior-equivalence program.
- `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md` plus
  `requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`,
  `requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv`,
  and the grouped `pitch_202x_resolution` field in
  `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`
  remain the canonical place to read the Pitch proto HLA 4 / `202X`
  backend-resolution lane. It is intentionally maintained as a bounded
  backend-resolution reading, but not an active open bucket in this register
  unless the repo deliberately opens a broader vendor-runtime comparison or
  certification program.
- `docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md` plus
  `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`
  remain the canonical place to read the OMT `xs:any` extension-tolerance
  boundary. It is intentionally maintained as payload-preserving tolerance
  rather than arbitrary extension-execution semantics, but not an active open
  bucket in this register unless the repo deliberately opens a broader
  extension-execution program.

## Reading Rule

Use this order when closing a bucket:

1. confirm the bucket is still open in
   [`requirements_completion_audit.md`](requirements_completion_audit.md)
2. open the owner doc named here
3. run the narrowest listed shard or command
4. update the listed artifact
5. only then remove the bucket from the audit surfaces

## Related Docs

- [`requirements_execution_queue.md`](requirements_execution_queue.md)
- [`requirements_completion_audit.md`](requirements_completion_audit.md)
- [`requirements_remaining_closure.md`](requirements_remaining_closure.md)
- [`requirements_finish_line.md`](requirements_finish_line.md)
