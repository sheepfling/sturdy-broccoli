# IEEE 1516-2025 Requirements Backlog

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

## Files

- `requirements.json`: machine-readable tranche registry.
- `framework_rules.md`: Framework and Rules requirements, including Rules 1-10.
- `federate_interface.md`: Federate Interface service, conformance, callback, FDD, exception, and time requirements.
- `omt.md`: OMT/FOM naming, DIF, component, identification, conformance, and merge requirements.
- `traceability_matrix.md`: initial requirement-to-project-lane and primary-`python1516_2025` runtime plus binding/hosted-route scenario mapping.
- `fom_backed_scenario_bounded_proof.md`: bounded requirement-facing note for the tracked Proto2025 and Target/Radar example/FOM-backed scenario suite over the main `python1516_2025` lanes.
- `federation_management_bounded_proof.md`: bounded requirement-facing proof note for federation lifecycle, synchronization, and save/restore control families over the main `python1516_2025` lane plus hosted replay.
- `python2025_direct_bounded_proof.md`: bounded requirement-facing proof note for the direct `python1516_2025` main-surface runtime lane over `hla-backend-python2025`.
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
- `python2025_exclusion_boundaries.md`: explicit exclusion map for legacy aliases, Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope OMT extension semantics around the main `python1516_2025` claim.
- `callback_bounded_proof.md`: bounded requirement-facing proof note for callback-delivery families, callback-control hygiene, and direct-versus-hosted callback surface boundaries over the main `python1516_2025` runtime.
- `callback_binding_deltas.md`: bounded requirement-facing note for callback/configuration/binding delta rows.
- `omt_xs_any_extension_tolerance.md`: bounded requirement-facing note for OMT `xs:any` extension preservation and schema-tolerant round-trip behavior.
- `executable_tests/`: imported v3 executable-test backlog with 1117 candidate test rows.
- `encoding_auth_work_packet/`: imported encoding/auth requirements, vectors, schemas, smoke FOM, and contract-test skeletons.
- `../../../requirements/2025/depth/`: imported 691-row requirement-depth expansion used as a harmonization candidate for FI service, SOM/FOM service usage, OMT component/schema, validator-negative, framework, binding/configuration, and retired/replacement rows.
- `../../../requirements/2025/harmonization/`: imported provisional disposition layer over the 691-row depth packet, including FI binding surface accounting, worklist, review queue, coverage rollup, and promotion guardrails.

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
  time-management bounded proof notes over `hla-backend-python2025`
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
`hla-backend-python2025` runtime layout rather than against the thin public
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
