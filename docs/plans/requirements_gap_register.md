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

The remaining `2010` `partial` rows are now all owned by explicit bounded
family notes or backend-resolution companions.
Those rows stay out of the active gap table unless a deliberate scope expansion
or new evidence change reopens them.

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
