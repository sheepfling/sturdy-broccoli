# 2010 Object-Management Bounded Family

Use this page when the question is:

- why does the 2010 Clause 6 object-management family still carry `partial`
  rows even though most naming, discovery, update, interaction, delete, and
  transport-subset services are already directly tested?
- which single document owns the remaining `CAP-OM` partial pattern?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-OM` partial rows are already in an explicit bounded family
  state
- the canonical owner ledger stays `partial` for those rows
- the bounded reasons are now structured and reviewable instead of implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/object_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- supporting decomposition seed:
  `requirements/2010/hla1516_1_clause_6_object_management.csv`
- primary shards:
  - `unit-scenarios-light`
  - `unit-python-core` for local callback, naming, and narrow object-routing
    proofs that stay within the local backend lane

## Final Claim Rule

- keep the remaining Clause 6 family rows `partial` when the repo already
  proves the main service surface, signature shape, naming callbacks,
  discovery, reflect and receive paths, delete and local-delete behavior,
  request and update-advisory slices, and the implemented reliable plus
  best-effort transportation subset, but does not yet prove every imported
  packet slice as a one-row exhaustive witness
- do not describe these rows as missing object-management services
- do not describe these rows as unsupported object routing or callback behavior
- do not flatten the family into `mapped` merely because the primary object
  exchange paths are strong
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-OM`
  partial family
- the remaining rows are not waiting on wording cleanup; they are already in
  their intended bounded supported-scope presentation
- the unresolved part is only optional future callback-order isolation,
  multi-effect-vector decomposition, broader negative-envelope isolation, or
  wider-than-supported transport semantics, not ambiguity about whether the
  currently exercised Clause 6 service surface exists
- keep the family rows `partial` in
  `hla1516_1_om_detailed_reconciliation.csv` unless narrower direct proof is
  actually added for the remaining packet slices

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the remaining `EFF`, `CB_ORD`, `CB_ORDER`, `EXC_API`, `EXC`, `PRE`,
   `FED_CB`, or overview rows gain new direct isolated witnesses
2. the repo decides to make a stronger one-row-per-packet Clause 6 claim
3. the current family owner ledger stops being the right canonical location for
   the bounded Clause 6 object-management story

If none of those happen, preserve the current bounded family reading and do not
keep describing `CAP-OM` as vague or structurally unfinished.

## Current Family Shape

The current owner ledger has `391` object-management packet rows:

- `274 mapped`
- `117 partial`

The remaining `117 partial` rows cluster into stable categories:

- `25 EFF`
- `25 CB_ORD`
- `19 EXC_API`
- `17 CB_ORDER`
- `14 EXC`
- `10 PRE`
- `6 FED_CB`
- `1 OVW`

## What The Categories Mean

### State-vector breadth tail

The `25 EFF` rows usually describe a broader postcondition vector than the
current direct proof asserts in one place.

Typical pattern:

- key object-routing, naming, or delete effects are already proven
- the full multi-field state transition is not yet claimed as one exhaustive
  witness

### Callback-order breadth tail

The `25 CB_ORD` and `17 CB_ORDER` rows are mostly callback-order or
callback-model breadth rows.

These are not callback-delivery gaps.
They are rows where:

- the callback is already delivered directly
- the signature is already present
- the broader ordering, timing, or scope envelope remains stated more broadly
  than the currently isolated proof

### Exception and precondition breadth tail

The `19 EXC_API`, `14 EXC`, and `10 PRE` rows usually keep a broader negative
envelope than the current tests isolate directly.

Typical pattern:

- representative not-connected, not-joined, save/restore, invalid-handle, and
  known-object guards are already proven
- the packet row still claims a larger clause-level exception or precondition
  universe than the direct witness currently isolates

### Residual callback and overview tail

The last `7` rows are the small bounded remainder:

- one broad object-scope overview row
- a few callback-delivery or callback-surface rows that still phrase the claim
  more broadly than the current isolated witness

These rows are already explicit enough to review honestly, but they are not yet
standalone exhaustive service proofs.

## Supported-Subset Boundary Inside Clause 6

Part of the current partial tail is intentionally a supported-subset boundary,
not a missing feature.

The clearest example is transportation-type behavior:

- the repo directly proves the implemented `HLAreliable` plus `HLAbestEffort`
  subset
- broad full-semantic transportation rows remain partial where they still claim
  more than that subset

The same bounded reading applies to broader update-rate or scope statements
that still exceed the current repo-native runtime claim.

## What Is Already Proved

The current repo directly proves most of the Clause 6 executable surface,
including:

- object-instance name reservation and release families
- registration, discovery, local-delete, and remove-object flows
- attribute update and interaction routing through declaration and DDM filters
- request-attribute-value-update and update-advisory slices
- attributes-in-scope and attributes-out-of-scope callback slices
- implemented reliable plus best-effort transportation override query, confirm,
  report, and restore-persistence subset
- MOM service-reporting visibility for Clause 6 federate-initiated services

Primary evidence anchors:

- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/backends/test_python_backend_support_services.py`
- `tests/scenarios/test_target_radar_scenario.py`
- `requirements/2010/traceability_matrix.csv`

## Good Reading

Good reading:

- object management is broadly implemented, linked, and strongly tested
- the remaining partial rows describe bounded callback-order, negative-envelope,
  multi-effect-vector, or supported-subset limits
- the family already has a defensible supported-scope reading

Bad reading:

- Clause 6 is mostly unproven
- discovery, reflect, receive, or delete behavior is still speculative
- the partial rows imply missing support for the object-management services
  themselves

## Reading Order

1. `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`
2. `requirements/2010/hla1516_1_clause_6_object_management.csv`
3. `requirements/2010/traceability_matrix.csv`
4. `tests/backends/test_python_backend_time_ddm_extended.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../plans/requirements_gap_register.md`](../../plans/requirements_gap_register.md)
