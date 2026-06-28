# IEEE 1516-2025 Requirements And Traceability

Use this page when the question is:

- what is the repo's 2025 requirement source surface?
- where do the 2025 requirement ledgers, proof notes, and traceability packets live?
- where should someone start reading 2025 requirements-facing material?

Start here, then continue into:

1. [`../../../requirements/2025/README.md`](../../../requirements/2025/README.md)
2. [`../../verification/README.md`](../../verification/README.md)
3. [`../../spec_reading_map.md`](../../spec_reading_map.md)
4. one bounded proof note or 2025 source packet from the family you care about

Use this reading rule:

- this README is the human-facing front door for the 2025 requirement surface
- `requirements/2025/README.md` is the collected source-side inventory
- `verification/README.md` explains where executable or generated proof artifacts live
- `spec_reading_map.md` tells you which proof note or requirement packet to read first for a concrete standards question

This directory is the first structured extraction tranche for the 2025 HLA
family:

- IEEE 1516-2025, Framework and Rules
- IEEE 1516.1-2025, Federate Interface Specification
- IEEE 1516.2-2025, Object Model Template Specification

The extraction stance is intentionally conservative. `shall` is the primary
normative marker and drives mandatory backlog entries first. `should`, `may`,
and `can` are retained as advisory, permission, or descriptive notes in later
passes.

Source anchors for modal terms:

| Source | Clause | Page |
| --- | ---: | ---: |
| IEEE 1516-2025 | 1.3 | 11 |
| IEEE 1516.1-2025 | 1.3 | 16 |
| IEEE 1516.2-2025 | 1.3 | 12 |

## Edition Inventory

The 2025 requirement surface is intentionally collected through the source-side
2025 view at [`../../../requirements/2025/README.md`](../../../requirements/2025/README.md).
That edition inventory covers:

- merge/source-trace and strict-doc reports
- 2025-vs-2010 differential packets
- depth-expansion packets
- harmonization, review, and closure packets

## Practical Flow

Use this order:

1. open the 2025 source-side inventory
2. pick one requirement packet, bounded proof note, or closure ledger
3. open `verification/README.md` when you need the proof packet or executable evidence side

## Basic Execution Rules

Use this section when the question is whether the 2025 requirement surface
already covers the basic federation-execution state rules:

- this is the canonical 2025 "have we joined yet?" rule family for
  execution-affecting calls

- connect before RTI interaction
- create and destroy federation execution preconditions
- joined versus not-joined execution-member guards
- plain object registration rejected until the caller has joined
- delete, local-delete, update, interaction, query, and region-gated DDM
  services rejected until the caller has joined
- concretely, `Update Attribute Values`, `Send Interaction`,
  `Request Attribute Value Update`, `Query Attribute Transportation Type`,
  `Send Interaction With Regions`, and
  `Request Attribute Value Update With Regions` all stay inside that
  joined-state guard family
- after resign, those execution-affecting services continue to reject the
  caller as no longer joined, including delete/local-delete plus the
  region-gated DDM send and request-update variants
- destroy rejected while federates are still joined
- after destroy succeeds, later destroy or join attempts against that missing
  federation reject with `FederationExecutionDoesNotExist`
- federation membership listing and reporting
- resign and disconnect cleanup after membership changes

Primary owner surfaces:

- `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`
  for the grouped 2025 service disposition rows
- [`../execution_membership_rules.md`](../execution_membership_rules.md) for
  one cross-edition index covering join, destroy, update, delete, query, and
  region-gated not-joined rules
- [`federation_management_bounded_proof.md`](federation_management_bounded_proof.md)
  for the bounded proof note covering connect, create, destroy, join,
  membership, resign, disconnect, synchronization, and save/restore families
- [`object_management_bounded_proof.md`](object_management_bounded_proof.md)
  for the bounded proof note covering not-joined rejection on update,
  interaction, transportation-query, and attribute-value-update services
- [`ddm_bounded_proof.md`](ddm_bounded_proof.md) for the bounded proof note
  covering not-joined rejection on region-gated send and request-update paths
- `executable_tests/hla_2025_executable_test_requirements_v3.csv` for the
  executable requirement rows such as
  `HLA2025-FI-004-XT-REQ-CONNECT_BEFORE_RTI_INTERACTION`,
  `HLA2025-FI-SVC-005`, `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-010`, and
  `HLA2025-FI-SVC-011`

Representative 2025 requirement rows for this rule set:

- `HLA2025-FI-004-XT-REQ-CONNECT_BEFORE_RTI_INTERACTION` for the direct
  connect-before-service guard
- `HLA2025-FI-SVC-005` for destroy preconditions and joined-federate
  rejection
- `HLA2025-FI-SVC-008` for federation membership listing and reporting
- `HLA2025-FI-SVC-010` for join preconditions and membership entry
- `HLA2025-FI-SVC-011` for resign preconditions and membership exit cleanup
- `HLA2025-FI-SVC-051` for `Reserve Object Instance Name` joined-state gating
  on the shared backend proof path
- `HLA2025-FI-SVC-057` for `Register Object Instance` joined-state gating on
  the shared backend proof path
- `HLA2025-FI-SVC-065` for `Delete Object Instance` execution-member gating
- `HLA2025-FI-SVC-067` for `Local Delete Object Instance`
  execution-member gating
- `HLA2025-FI-SVC-059` for `Update Attribute Values` execution-member gating
- `HLA2025-FI-SVC-061` for `Send Interaction` execution-member gating
- `HLA2025-FI-SVC-070` for `Request Attribute Value Update`
  execution-member gating
- `HLA2025-FI-SVC-077` for `Query Attribute Transportation Type`
  execution-member gating
- `HLA2025-FI-SVC-136` for `Send Interaction With Regions`
  execution-member gating on the DDM surface
- `HLA2025-FI-SVC-137` for `Request Attribute Value Update With Regions`
  execution-member gating on the DDM surface

The main execution-state guard exceptions are already part of that ownership
surface:

- `NotConnected`
- `FederateNotExecutionMember`
- `FederatesCurrentlyJoined`
- `FederationExecutionDoesNotExist`

Primary executable anchors:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/transport/test_grpc_transport_2025.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/scenarios/test_federation_management_backend_matrix.py`
- `tests/scenarios/test_federation_lifecycle_backend_matrix.py`
- `./tools/test-focus run execution-membership`

Use these anchors first when the question is "have we proved the basic
execution lifecycle rules on the direct lane, hosted 2025 gRPC/FedPro route,
and REST-hosted Python route?" rather than
"which broader grouped or bounded bucket owns the remaining closeout story?".

The intended 2025 state-machine reading is:

- `NotConnected` before connect or after disconnect
- `FederateNotExecutionMember` before join and again after resign
- `FederatesCurrentlyJoined` when destroy is attempted while members are still
  joined
- `FederationExecutionDoesNotExist` after the federation has already been
  destroyed

## Shards And Views

Use the shared matrix model from
[`../../plans/requirements_remaining_closure.md`](../../plans/requirements_remaining_closure.md):

- `shards` are the executable ownership units
- `views` are overlapping audit, harmonization, or finish-line cuts across shards
- every 2025 requirement bucket should have one narrowest primary shard first
- widen to hosted or broader lanes only when the requirement claim actually crosses that boundary

For 2025 work, the usual ownership pattern is:

- source packet or harmonization row in [`../../../requirements/2025/README.md`](../../../requirements/2025/README.md)
- canonical claim or boundary note in one bounded proof note under this directory
- primary proof shard or lane from [`../../test_surface.md`](../../test_surface.md)
- generated or executable proof artifact from [`../../verification/README.md`](../../verification/README.md)

Preferred closure-table columns:

| Column | Meaning |
| --- | --- |
| `Requirement family` | grouped FI, OMT, framework, binding, or harmonization bucket |
| `Requirement IDs` | exact 2025 IDs or grouped worklist rows |
| `Canonical status` | `planned`, `partial`, `covered`, `duplicate/umbrella`, or `retired/legacy-only` |
| `Backend resolution` | separate backend-resolution columns or a linked backend-resolution artifact such as the harmonization ledger, FI binding matrix, hosted-route boundary note, or `pitch_202x_resolution` field for Pitch's vendor-branded proto HLA 4 / `202X` surface |
| `Primary shard` | first canonical owning shard |
| `Widen to` | broader lane only if hosted parity, finish-line, or cross-surface proof is required |
| `View tags` | overlapping audit cuts such as `transport`, `ownership`, `time`, `java-shim`, `cpp-shim`, `setup-preflight`, or `finish-line` |
| `Evidence artifact` | bounded proof note, ledger, packet, JSON, or generated route-parity artifact |
| `Boundary note` | honest supported-scope note when the proof is narrower than the full standard wording |

Practical rule:

- keep 2025 closeout owned by shards
- use views to answer cross-bucket questions such as transport, bindings, setup, or finish-line coverage
- do not let a view replace shard ownership in repo-green, route parity, or requirements status changes
- keep canonical requirement closure separate from backend or route-specific support
- when a vendor labels its surface differently, such as Pitch proto HLA 4 / `202X`,
  treat that as backend-resolution terminology and document it in the linked
  owner artifact rather than folding it into canonical status

Current grouped harmonization result:

- `57 covered`
- `5 duplicate/umbrella`
- `2 retired/legacy-only`

Use that grouped result carefully:

- it means the grouped 2025 worklist is fully dispositioned
- it does not mean every 2025 row is an unconditional all-covered conformance claim
- the remaining blockers are boundary-doc and supported-scope questions such as umbrella rows, retired rows, hosted/binding bounded claims, and other intentionally narrow claim surfaces

## Honest 100 Percent Reading

Use this section when the question is not just "what does the main 2025 lane
prove?" but "what exactly counts as an honest `100%` outcome?"

Current closeout reading:

- all tracked `2025` rows are dispositioned
- the active normative non-retired non-umbrella denominator is currently
  `645` rows
- direct coverage on that active denominator is currently `645 / 645 = 100%`
- the remaining `22` `duplicate/umbrella` rows and `24`
  `retired/legacy-only` rows stay explicit outside that direct-support
  denominator unless the repo deliberately funds broader row-by-row proof or
  compatibility work

Use these owner companions for the current honest `100%` program:

- [`../../plans/PLN-004_python_rti_100_percent_compliance_plan.md`](../../plans/PLN-004_python_rti_100_percent_compliance_plan.md)
- [`../../plans/2025_python_rti_100_percent_worklist.md`](../../plans/2025_python_rti_100_percent_worklist.md)
- [`../../plans/2025_python_rti_umbrella_decomposition_worklist.md`](../../plans/2025_python_rti_umbrella_decomposition_worklist.md)
- [`../../plans/requirements_completion_audit.md`](../../plans/requirements_completion_audit.md)

Reading rule:

1. use this README for the canonical 2025 requirement owner map
2. use `2025_python_rti_100_percent_worklist.md` for the exact non-covered row
   inventory and denominator rule
3. use `2025_python_rti_umbrella_decomposition_worklist.md` only if leadership
   wants literal `691 / 691 covered`
4. use `requirements_completion_audit.md` for the current honest answer to
   whether the broader closeout program is actually finished

Requirement-test rule:

- verify 2025 rows through live evidence anchors and owning proof notes
- do not treat closeout plans, worklists, or finish-line prose as the thing
  being verified
- use [`../../verification/requirements_verification_flow.md`](../../verification/requirements_verification_flow.md)
  as the canonical policy for that split

## Boundary Bucket Owners

Use this index when the question is not "what service row proves this?" but
"which single document owns this boundary or umbrella bucket?"

| Bucket | Canonical owner doc | Primary shard | Typical view tags |
| --- | --- | --- | --- |
| framework umbrella rows | `framework_rules.md` | `unit-python-2025-core` | `2025-core`, `finish-line`, `scenarios` |
| callback/configuration/binding delta umbrellas | `callback_binding_deltas.md` | `unit-shim-tooling` | `2025-core`, `java-shim`, `cpp-shim`, `transport` |
| binding and hosted-route boundary rows | `binding_and_hosted_route_boundaries.md` | `unit-transport-local` | `2025-core`, `transport`, `finish-line` |
| Pitch proto HLA 4 / `202X` backend-resolution lane | `pitch_202x_bounded_comparison.md` | `unit-transport-local` | `2025-core`, `transport`, `java-shim`, `finish-line` |
| legacy-alias and non-claim perimeter around the main runtime lane | `python1516_2025_exclusion_boundaries.md` | `unit-foundation` | `2025-core`, `setup-preflight`, `finish-line` |
| retired and legacy-only mapping rows | `retired_legacy_mapping.md` | `unit-foundation` | `2025-core`, `setup-preflight` |

Reading rule:

1. start with the owner doc above
2. then open the linked bounded proof or harmonization ledger
3. only after that widen to route parity, finish-line, or generated packet artifacts

## Files

- `requirements.json`: machine-readable tranche registry.
- `framework_rules.md`: Framework and Rules requirements, including Rules 1-10.
- `federate_interface.md`: Federate Interface service, conformance, callback, FDD, exception, and time requirements.
- `omt.md`: OMT/FOM naming, DIF, component, identification, conformance, and merge requirements.
- `traceability_matrix.md`: initial requirement-to-project-lane and primary-`python1516_2025` runtime plus binding/hosted-route scenario mapping.
- `fom_backed_scenario_bounded_proof.md`: bounded requirement-facing note for the tracked Proto2025 and Target/Radar example/FOM-backed scenario suite over the main `python1516_2025` lanes.
- `federation_management_bounded_proof.md`: bounded requirement-facing proof note for federation lifecycle, synchronization, and save/restore control families over the main `python1516_2025` lane plus hosted replay.
- `python1516_2025_direct_bounded_proof.md`: bounded requirement-facing proof note for the direct `python1516_2025` main-surface runtime lane over `hla-backend-python1516-2025`.
- `declaration_management_bounded_proof.md`: bounded requirement-facing proof note for publication, subscription, advisory, and name-reservation families.
- `object_management_bounded_proof.md`: bounded requirement-facing proof note for object registration, updates, interactions, routing, and delete/remove families.
- `ownership_management_bounded_proof.md`: bounded requirement-facing proof note for divestiture, acquisition, release, query, and resign-time ownership policies.
- `save_restore_bounded_proof.md`: bounded requirement-facing proof note for save/restore lifecycle control, shared rollback, routing/policy rollback, ownership rollback, and time-window/time-state rollback.
- `ddm_bounded_proof.md`: bounded requirement-facing proof note for region lifecycle, overlap routing, declaration gating, and passive/DDM cleanup families.
- `support_services_bounded_proof.md`: bounded requirement-facing proof note for support-service traceability, handle/name lookup, callback-control, and switch/control inquiry families.
- `time_management_bounded_proof.md`: bounded requirement-facing proof note for time-mode control, grants, GALT/LITS/lookahead observability, and Target/Radar window proofs.
- `lookahead_window_bounded_proof.md`: bounded requirement-facing proof note for the Target/Radar lookahead ladder, including future-exclusion, output ordering, pipeline overlap, negative-oracle guards, and bounded save/restore window rollback.
- `standard_binding_runtime_capability_bounded_proof.md`: bounded requirement-facing proof note for Java/C++ standard-route artifact-gated runtime-capability traces over the main `python1516_2025` runtime.
- `hosted_fedpro_bounded_proof.md`: bounded requirement-facing proof note for the hosted `python1516_2025-fedpro-grpc` transport/runtime slice over the main `python1516_2025` RTI lane.
- `binding_and_hosted_route_boundaries.md`: bounded requirement-facing note for Java, C++, and hosted FedPro binding/route boundaries over the main `python1516_2025` runtime.
- `pitch_202x_bounded_comparison.md`: bounded requirement-facing note for the Pitch proto HLA 4 / `202X` adapter-route comparison packet over the main `python1516_2025` runtime.
- `python1516_2025_exclusion_boundaries.md`: explicit exclusion map for legacy aliases, Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope OMT extension semantics around the main `python1516_2025` claim.
- `callback_bounded_proof.md`: bounded requirement-facing proof note for callback-delivery families, callback-control hygiene, and direct-versus-hosted callback surface boundaries over the main `python1516_2025` runtime.
- `callback_binding_deltas.md`: bounded requirement-facing note for callback/configuration/binding delta rows.
- `omt_xs_any_extension_tolerance.md`: bounded requirement-facing note for OMT `xs:any` extension preservation and schema-tolerant round-trip behavior.
- `executable_tests/`: imported v3 executable-test backlog with 1117 candidate test rows.
- `encoding_auth_work_packet/`: imported encoding/auth requirements, vectors, schemas, smoke FOM, and contract-test skeletons.
- `../../../requirements/2025/depth/`: imported 691-row requirement-depth expansion used as a harmonization candidate for FI service, SOM/FOM service usage, OMT component/schema, validator-negative, framework, binding/configuration, and retired/replacement rows.
- `../../../requirements/2025/harmonization/`: imported provisional disposition layer over the 691-row depth packet, including FI binding surface accounting, grouped and row-level Pitch proto HLA 4 / `202X` backend-resolution ledgers, worklist, review queue, coverage rollup, and promotion guardrails.

## Conformance Language

Do not use `HLA Conforming`, `fully conformant`, or `standards compliant` for
local shims, demos, object models, tools, or route reports unless certified
conformance evidence exists.

Allowed project evidence vocabulary:

| Status | Meaning |
| --- | --- |
| `surface-backed` | Standard surface exists and is traceable to source API or schema. |
| `lifecycle-green` | Connect/create/join/callback-poll/resign/destroy/disconnect lifecycle passes. |
| `adapter-smoke-green` | Adapter loads and handles a scoped smoke path. |
| `core-exchange-green` | FOM-backed object/interaction/time exchange path passes. |
| `trace-green` | Route trace matches expected standard-backed events and artifacts. |
| `full-interface-surface-complete` | All joined-federate services and RTI-initiated callbacks are present in surface accounting. |
| `full-interface-behavior-complete` | All joined-federate services and RTI-initiated callbacks are behavior-tested. |

## Current Technical Lane

The current high-value implementation lane is deeper runtime-proof expansion
over the promoted `python1516_2025` RTI surface. The repo has already moved past the
initial FOM/OMT validation bootstrapping stage and now uses this directory as a
requirement-facing evidence map for:

- federation, object, ownership, DDM, save/restore, MOM, support-service, and
  time-management bounded proof notes over `hla-backend-python1516-2025`
- the tracked example/FOM-backed scenario bounded proof note that makes the
  repo-owned Proto2025 and Target/Radar suite explicit without overclaiming
  every possible FOM composition
- the dedicated direct `python1516_2025` bounded proof note that treats the main
  in-process lane as its own requirement-facing executable surface instead of
  only as architecture prose
- the dedicated hosted FedPro bounded proof plus route-parity evidence that replays those runtime
  families without turning the hosted route into a separate RTI owner
- the dedicated callback bounded proof note that separates callback families
  and callback-control hygiene from the generic callback model explainer and
  from the umbrella callback/binding delta rows
- the dedicated save/restore bounded proof note that separates rollback
  families from the broader federation-management note so restore semantics
  stay auditable as their own bounded runtime family
- the dedicated lookahead-window bounded proof note that breaks the
  Target/Radar closure/output/order/pipeline ladder out of the broader
  time-management family so the bounded certification contract stays auditable
- the dedicated Java/C++ standard binding bounded proof that keeps those lanes as adaptation evidence over the
  same runtime rather than alternate implementation owners
- explicit bounded-extension, legacy-only, and wrapper-only shim boundaries so
  the main 2025 Python RTI claim stays narrow enough to defend
- one explicit exclusion map that gathers the non-claim areas around the main
  `python1516_2025` runtime lane so those boundaries stay auditable outside the
  generated finish-line bundle

For code ownership, read those proof notes against the extracted
`hla-backend-python1516-2025` runtime layout rather than against the thin public
shell alone. The main requirement-backed semantics now live across package-owned
modules such as:

- `backend_factory_runtime.py`
- `runtime_state.py`
- `federation_management_runtime.py`
- `time_management_runtime.py`
- `support_services_runtime.py`
- `*_surface_mixin.py`

That is the implementation lane this requirement index is describing.

FOM/OMT validation still matters inside that lane:

- Framework Rule 1 requires a FOM.
- The Federate Interface requires RTI handling, merging, and rejection of FOM modules.
- The OMT defines valid object model naming, content, validation, and merge behavior.

But it is now one proof family inside the broader 2025 runtime-evidence closeout
rather than the next missing implementation frontier by itself.

## Related Docs

- [`../../../requirements/2025/README.md`](../../../requirements/2025/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
- [`../../plans/PLN-004_python_rti_100_percent_compliance_plan.md`](../../plans/PLN-004_python_rti_100_percent_compliance_plan.md)
- [`../../plans/2025_python_rti_100_percent_worklist.md`](../../plans/2025_python_rti_100_percent_worklist.md)
- [`../../plans/2025_python_rti_umbrella_decomposition_worklist.md`](../../plans/2025_python_rti_umbrella_decomposition_worklist.md)
- [`../../plans/requirements_completion_audit.md`](../../plans/requirements_completion_audit.md)
- [`../../plans/requirements_remaining_closure.md`](../../plans/requirements_remaining_closure.md)
- [`../../test_surface.md`](../../test_surface.md)
- [`../../spec_reading_map.md`](../../spec_reading_map.md)
