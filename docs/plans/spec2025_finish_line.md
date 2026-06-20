# IEEE 1516-2025 Requirements Finish Line

This inventory is deliberately conservative. It records implemented slices, partial slices, and planned work without using HLA conformance language.

## Current Scale

- Initial curated registry rows: 28
- Imported executable-test rows: 1117
- Imported requirement-depth rows: 691
- Imported provisional disposition rows: 691
- Completion-backlog rows: 33
- High-priority rows still open: 0

## Closeout Readiness

- Implemented evidence slices: 73
- Route parity partial rows: 0
- Route parity missing rows: 0
- Ready for slice closeout: True
- Ready for full completion claim: False
- Assessment: Executable slice coverage, route parity, FI per-service runtime traceability, and bounded working-RTI milestone evidence are in strong shape for the current 2025 lane, and the repo now has a row-level requirement-by-requirement disposition audit across the full 2025 universe, but the remaining unsupported, umbrella, cross-binding, and bounded-route limits still block a complete 2025 claim or a permanent promotion decision over a future shim-versus-dedicated-RTI split.

Conformance blockers:

- The repo now has a row-level requirement-by-requirement disposition audit across all 2025 rows, but that audit still contains unsupported, retired, and umbrella rows rather than an all-covered conformance pass.
- Many implemented-slice rows outside the FI service catalog still aggregate multiple requirements under bounded supported-scope language rather than proving every requirement individually.
- Java and C++ standard-route evidence remains artifact-gated/runtime-capability evidence, not a full cross-binding behavior-conformance pass.
- The hosted FedPro route is verified as a runtime slice, but its own supported-scope rows explicitly stop short of full RTI semantics and full MOM action/request conformance.
- OMT component and validator coverage still mixes supported-subset proof with explicit unsupported-boundary rows, so those areas are not yet represented as an unconditional requirement-by-requirement conformance pass.
- Unsupported-boundary and legacy-only rows remain explicit exclusions rather than delivered support, so overall completion cannot be promoted to an unconditional 2025 conformance claim.

## Pytest Anchor Audit

- Anchored requirements: 711
- Assessment: Repo-native HLA2025 requirement markers now provide direct pytest-function anchors for the supported working-surface claim, complementing the broader evidence-slice ledgers.

## Unanchored Requirement Audit

- Unanchored ledger requirements: 0
- Assessment: All FI, delta, binding, and OMT proof-ledger rows now have direct pytest-function anchors, so the broader evidence-slice ledgers and direct requirement markers are aligned.

## FI Service Proof Audit

- Service rows: 196
- Ready for per-service runtime traceability claim: True
- Ready for full FI service conformance claim: False
- Assessment: All 196 Federate Interface service catalog rows now map to explicit runtime evidence rows, but many services are still proven through clustered slice evidence rather than isolated one-service final conformance tests.

FI service family counts:

- callback_control: 4
- ddm: 12
- declaration_management: 12
- federation_management: 17
- name_reservation: 6
- object_class_relevance: 4
- object_management: 26
- ownership_management: 18
- save_restore: 17
- support_services: 55
- time_management: 25

## Delta Requirement Proof Audit

- Delta rows: 20
- Ready for delta traceability claim: True
- Ready for full delta conformance claim: False
- Assessment: All modified, new, and retired common delta rows now map to explicit evidence slices, but several are still proven through grouped behavioral slices or retirement mappings rather than isolated final SHALL tests.

- modified-existing: 10
- new-2025-requirement: 7
- retired-mapped-2010: 3

## Binding Requirement Proof Audit

- Binding rows: 3
- Ready for binding traceability claim: True
- Ready for full binding conformance claim: False
- Assessment: All three binding rows now have explicit slice and route-parity proof records, but Java/C++ remain artifact/runtime-capability bounded and FedPro remains a hosted runtime slice rather than full conformance.

## OMT Requirement Proof Audit

- OMT rows: 454
- Ready for OMT traceability claim: True
- Ready for full OMT conformance claim: False
- Assessment: All OMT-related rows are now explicit requirement records, with supported-subset proof separated from unsupported-boundary proof. This closes the traceability gap without pretending the unsupported OMT boundaries are delivered support.

## Callback Proof Audit

- Callback rows: 55
- Helper-backed callbacks: 55
- Focused executable callbacks: 55
- Ready for callback surface traceability claim: True
- Ready for callback-by-callback working-surface claim: True
- Assessment: The repo now has an explicit callback-by-callback ledger through the FederateAmbassador conformance matrix, and all 55 callback rows are helper-backed with focused executable evidence. This closes the callback-ledger gap, but it still does not by itself prove exhaustive cross-binding callback signature/ordering parity or a full callback conformance claim.

Callback verification status counts:

- focused-executable-tests: 55

## Callback Route Parity Audit

- Callback rows: 55
- Hosted/direct route-backed callbacks: 55
- Callback-helper-only rows: 0
- Ready for full Python-lane callback route parity claim: True
- Ready for exhaustive cross-binding callback parity claim: False
- Assessment: The callback ledger is now fully route-backed across the current Python 2025 lanes, so every callback row has hosted/direct executable evidence in addition to the helper-backed working-surface proof. The repo still does not yet prove exhaustive callback-by-callback signature and ordering equivalence across every binding.

## Support-Service Proof Audit

- Support-service rows: 62
- Focused executable rows: 62
- Rows with known gaps: 61
- Complete negative-path rows: 61
- Partial negative-path rows: 0
- Metadata-mapped negative-path rows: 0
- Ready for support-service traceability claim: True
- Ready for support-service full conformance claim: False
- Assessment: The repo now has an explicit support-service ledger through the RTIambassador conformance matrix, and all 62 support-service rows have focused executable evidence. Negative-path coverage is now complete for all 61 actionable support-service rows, with the remaining row marked not-applicable because it declares no actionable RTI exception surface. Support services are no longer the main blocker; cross-binding evidence remains weaker than the Python routes.

Support-service verification status counts:

- focused-executable-tests: 62

Support-service negative-path status counts:

- complete: 61
- not-applicable: 1

## Python RTI Milestone Audit

- Audit status: bounded-python-rti-milestones
- Routes: python-2025-inprocess, python-2025-fedpro-grpc
- Milestones per route: 6
- Assessment: Both Python 2025 routes now have explicit milestone gates for working-surface breadth, FOM-backed scenario execution, message routing, time sync, GALT/LITS query evidence, and lookahead handling. The time milestones now explicitly include Target/Radar future-exclusion, output-delivery, consumer-order, pipeline, receive-order poison, save/restore window-state, save/restore output resume, save/restore pipeline resume, and time-window proof, but the last four remain bounded-evidence milestones rather than blanket correctness claims.

## Requirement-By-Requirement Audit

- Audit status: row-level-requirement-disposition-audit-captured
- Row count: 691
- Ready for row-level audit claim: True
- Ready for full 2025 conformance claim: False
- Rows with complete review metadata: 691
- Covered rows with evidence paths: 564
- Unsupported rows with explicit boundary flag: 81
- Assessment: The repo now has an explicit row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows: every row is reviewed, dispositioned, and linked either to repo evidence, an explicit unsupported boundary, a retired exclusion, or an umbrella normalization role. That closes the missing-audit gap without turning the result into an unconditional all-covered conformance pass.

Requirement-by-requirement blockers:

- 81 rows are explicit unsupported-boundary decisions rather than delivered support.
- 24 rows are retired/legacy-only exclusions rather than active 2025 support.
- 22 rows remain duplicate/umbrella normalization aids rather than one-row conformance assertions.
- Many covered rows still inherit bounded supported-scope language from slice-level evidence rather than standalone exhaustive clause-by-clause proof.

Requirement-by-requirement area closure:

- fi_service_catalog: covered=196
- som_fom_service_usage: covered=196
- omt_component_conformance: covered=143, unsupported-boundary=81
- omt_validator_negative_conformance: covered=29
- framework_rules: duplicate/umbrella=10
- callback_configuration_binding_deltas: duplicate/umbrella=12
- retired_replacement_mapping_candidates: retired/legacy-only=24

## Completion Claim Audit

- Claim shape: bounded-working-surface-with-explicit-boundaries
- Ready for supported-boundary statement: True
- Ready for full 2025 conformance claim: False
- Assessment: The repo can now make a defensible supported-boundary statement: the claimed working surface is backed by explicit requirement ledgers, the backlog is closed at the tracked 2025 delta level, and unsupported or legacy-only areas are named rather than hidden. This is still short of a full 2025 conformance claim.

Requirement universe:

- Total rows: 691
- Covered rows: 564
- Unsupported-boundary rows: 81
- Retired/legacy-only rows: 24
- Duplicate/umbrella rows: 22

Full-claim blockers:

### python-2025-inprocess

- Milestone count: 6
- All milestone parity-covered: True
- Assessment: The route clears the tracked milestone gates as a bounded Python 2025 working surface.

- Best-attempt Python RTI 2025 working surface: bounded-working-slice (In-process Python 2025 is a best-attempt bounded working surface across the tracked runtime scenario set, not a full requirement-by-requirement conformance claim.)
- Tracked example and FOM-backed scenario execution: covered-scenario-slice (The in-process route executes the tracked repo example/FOM-backed scenarios, including object exchange, FOM showcase, and save/restore rollback paths.)
- Message exchange and routing: covered-routing-slice (The in-process route sends, receives, discovers, reflects, directs, and DDM-filters the tracked message flows end to end.)
- Time synchronization and advance flow: covered-time-advance-slice (The in-process route exercises regulation/constrained enablement, time advance, flush queue, timestamped delivery, retraction, restore rollback of logical time, and restore recovery of saved lookahead plus time/switch control state.)
- GALT and LITS behavior: bounded-query-evidence (The in-process route has executable GALT/LITS query evidence inside the logical-time slice and the Target/Radar future-exclusion proof, with the integrated lookahead-processing-window gauntlet proving the combined closure/output/consumer-order/pipeline ladder on the actual 2025 shim, plus save/restore evidence that dirty lookahead changes are rolled back while a pre-save queued TSO is still redelivered after restore.)
- Lookahead handling and windows: bounded-lookahead-evidence (The in-process route exercises lookahead query/modify behavior, queued timestamped delivery, the integrated Target/Radar lookahead-processing-window gauntlet, and the time-window core, output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, save-restore lookahead rollback with queued-TSO redelivery, save-restore-output-resume, and save-restore-pipeline-resume proofs.)

### python-2025-fedpro-grpc

- Milestone count: 6
- All milestone parity-covered: True
- Assessment: The route clears the tracked milestone gates as a bounded Python 2025 working surface.

- Best-attempt Python RTI 2025 working surface: bounded-working-slice (Hosted FedPro Python 2025 is a best-attempt bounded working surface across the tracked runtime scenario set, not a full RTI semantics or MOM action-request conformance claim.)
- Tracked example and FOM-backed scenario execution: covered-scenario-slice (The hosted FedPro route executes the tracked FOM-backed runtime scenarios used by the current object, MOM, and save/restore route tests.)
- Message exchange and routing: covered-routing-slice (The hosted FedPro route sends, receives, discovers, reflects, directs, and DDM-filters the tracked message flows over the typed transport surface.)
- Time synchronization and advance flow: covered-time-advance-slice (The hosted FedPro route exercises regulation/constrained enablement, async delivery control, advance/grant flow, queued TSO delivery, retraction, restore rollback of logical time, and restore recovery of saved lookahead plus time/switch control state.)
- GALT and LITS behavior: bounded-query-evidence (The hosted FedPro route has executable GALT/LITS query evidence inside the hosted time-management slice, including queued-TSO GALT/LITS divergence after a live lookahead change, the hosted Target/Radar proof-ladder replay, restore rollback of dirty lookahead with pre-save queued TSO redelivered after restore, and the Target/Radar future-exclusion proof.)
- Lookahead handling and windows: bounded-lookahead-evidence (The hosted FedPro route exercises lookahead queries together with advance/grant, queued timestamped delivery, the hosted Target/Radar proof-ladder replay, and the Target/Radar output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, save-restore lookahead rollback with queued-TSO redelivery, save-restore-output-resume, and save-restore-pipeline-resume proofs.)

- Covered rows are mixed with explicit unsupported-boundary and retired/legacy-only rows in the 2025 universe, so the delivered statement must stay bounded.
- Java and C++ binding rows remain artifact/runtime-capability evidence rather than exhaustive behavior-conformance proof.
- The hosted FedPro route remains a bounded runtime slice and not a full RTI semantics/MOM action-request conformance pass.
- Duplicate/umbrella rows remain normalization aids rather than direct one-row conformance assertions.

## Supported Boundary Statement

- Status: supported-boundary-statement
- Ready: True
- Statement: The Python-centered 2025 RTI surface is validated as a bounded working surface across federation management, object management, time management, support services, callbacks, OMT handling, and binding routes, with explicit unsupported, legacy-only, and artifact-gated boundaries recorded in the repo.

Supported scope:

- Python 2025 in-process runtime behavior is executable and parity-covered across the tracked scenario set.
- Hosted FedPro 2025 transport behavior is executable as a bounded runtime slice with explicit route parity coverage.
- FI service requirements are traced across all 196 catalog rows.
- Common delta rows, binding rows, and OMT-related rows are all represented by explicit requirement ledgers.

Explicit boundaries:

- Unsupported OMT component rows remain unsupported-boundary entries rather than delivered support.
- Retired or legacy-only rows remain excluded from the supported 2025 working surface.
- Java and C++ bindings remain artifact/runtime-capability bounded rather than full behavior-conformance proof.
- FedPro remains a hosted runtime slice rather than a full RTI semantics/MOM action-request conformance pass.

## Implementation Concentration Audit

- Audit status: implementation-concentration-captured
- Implemented slices: 73
- Shim backend implementation path: packages/hla-backend-shim/src/hla/backends/shim/backend.py
- Shim backend-backed slices: 42
- Shim backend slice share: 0.575
- 2025 spec-package-backed slices: 12
- Transport-backed slices: 11
- Semantic concentration is material: True
- Assessment: The current 2025 lane is substantively executable, but the implementation proof is materially concentrated in hla-backend-shim/backend.py. That concentration does not by itself force a split, because spec-package and transport-layer evidence also exist, but it is a real architectural pressure signal to monitor as more 2025 behavior lands.
- Extraction pressure boundary: A future dedicated 2025 backend becomes more compelling if new runtime semantics keep accumulating primarily in the shim backend implementation instead of moving into cleaner reusable runtime modules.

Top evidence anchors:

- 52: tests/transport/test_grpc_transport_2025.py
- 49: tests/test_rti1516_2025_spec_and_shim.py
- 42: packages/hla-backend-shim/src/hla/backends/shim/backend.py
- 9: tests/test_rti1516_2025_validation.py
- 9: tests/requirements/test_2025_tail_backlog_evidence.py
- 9: packages/hla-rti1516e/src/hla/rti1516e/fom.py
- 7: packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py
- 7: tests/scenarios/test_object_management_backend_matrix.py
- 6: packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py
- 6: tests/factories/test_fom_omt_parsing.py

## Slice Aggregation Pressure Audit

- Audit status: slice-aggregation-pressure-captured
- Implemented slices: 69
- Aggregated slices >=10 requirements: 9
- Aggregated slices >=10 requirements and shim-backed: 3
- Aggregated slices >=20 requirements: 6
- Aggregated slices >=20 requirements and shim-backed: 2
- Assessment: Most implemented 2025 slices are not huge aggregations, but a small set of large slices still carry a lot of requirement mass. The main runtime pressure points are the shim-backed ddm-default-attribute-policy, save-restore-lifecycle, and directed-interaction-boundary slices, which are credible next decomposition targets if the repo needs tighter requirement-level proof or a cleaner backend seam.
- Next decomposition boundary: If deeper proof is needed, start by splitting the largest shim-backed slices into narrower service- or behavior-family audits before extracting a dedicated 2025 backend.

Largest implemented slices:

- 2025-service-utilization-crosscheck: 196 requirements (shim-backed: False)
- 2025-omt-extended-supported-subset: 109 requirements (shim-backed: False)
- 2025-omt-schema-constraint-validation: 29 requirements (shim-backed: False)
- 2025-ddm-default-attribute-policy: 23 requirements (shim-backed: True)
- 2025-omt-component-metadata-roundtrip: 22 requirements (shim-backed: False)
- 2025-save-restore-lifecycle: 20 requirements (shim-backed: True)
- 2025-standard-route-runtime-capability: 15 requirements (shim-backed: False)
- 2025-omt-switch-and-transport-subset: 12 requirements (shim-backed: False)
- 2025-directed-interaction-boundary: 11 requirements (shim-backed: True)
- 2025-support-federate-and-object-identity-lookups: 9 requirements (shim-backed: True)

Largest shim-backed aggregated slices:

- 2025-ddm-default-attribute-policy: 23 requirements
- 2025-save-restore-lifecycle: 20 requirements
- 2025-directed-interaction-boundary: 11 requirements

## Save/Restore Decomposition Audit

- Audit status: save-restore-decomposition-captured
- Slice id: 2025-save-restore-lifecycle
- Requirement count: 20
- Proof families: 5
- Direct-backed families: 5
- Hosted-backed families: 5
- Assessment: The save/restore slice is no longer just one broad working-surface claim. Its current evidence already separates into lifecycle control, shared rollback scenarios, routing/policy rollback, ownership rollback, and time-window/time-state rollback, with both direct and hosted anchors across every family.
- Next split boundary: If this slice needs further tightening, split it first by these proof families before extracting save/restore runtime semantics into a dedicated 2025 backend.

### save-restore/lifecycle-control

- Focus: save/restore request, initiate, completion, failure, abort, and precondition control flow
- Direct test count: 4
- Hosted test count: 4

### save-restore/shared-scenario-rollback

- Focus: shared two-federate save/restore, object-state rollback, and federate-local rollback
- Direct test count: 4
- Hosted test count: 4

### save-restore/routing-policy-rollback

- Focus: callback policy, transport/order policy, object routing, interaction routing, directed routing, and stale queued callback cleanup
- Direct test count: 6
- Hosted test count: 6

### save-restore/ownership-rollback

- Focus: ownership gauntlets, inflight acquisition/divestiture state, and owner-visibility rollback
- Direct test count: 3
- Hosted test count: 3

### save-restore/time-window-and-time-state-rollback

- Focus: lookahead, queued TSO, time/switch state, open/closed window state, output resume, and pipeline resume
- Direct test count: 5
- Hosted test count: 5


## Directed Interaction Decomposition Audit

- Audit status: directed-interaction-decomposition-captured
- Slice id: 2025-directed-interaction-boundary
- Requirement count: 11
- Proof families: 5
- Direct-backed families: 5
- Hosted-backed families: 5
- Assessment: The directed-interaction slice is no longer just one boundary claim. Its evidence separates into base routing/callback delivery, timestamped delivery and retraction, DDM overlap filtering, selective set and publication isolation, and restore-path routing cleanup, with direct and hosted anchors across all families.
- Next split boundary: If this slice needs further tightening, split it first by these directed-interaction proof families before moving directed-routing semantics into a dedicated 2025 backend.

### directed-interaction/base-routing-and-callback-delivery

- Focus: publish, subscribe, unsubscribe, unpublish, and receiveDirectedInteraction callback delivery
- Direct test count: 2
- Hosted test count: 2

### directed-interaction/timestamped-delivery-and-retraction

- Focus: queued timestamped directed delivery, per-subscriber routing, pre-delivery retract, and target-departure cleanup
- Direct test count: 3
- Hosted test count: 3

### directed-interaction/ddm-overlap-filtering

- Focus: region-overlap filtering for directed interactions and removal of disconnected directed DDM subscribers
- Direct test count: 3
- Hosted test count: 3

### directed-interaction/selective-set-and-publication-isolation

- Focus: selective directed-interaction set unsubscribe/unpublish without collapsing sibling classes or other publishers
- Direct test count: 2
- Hosted test count: 2

### directed-interaction/restore-routing-and-stale-queue-cleanup

- Focus: restore recovers directed DDM subscriber routing and clears stale directed TSO without replaying dirty state
- Direct test count: 2
- Hosted test count: 2


## DDM Default-Policy Decomposition Audit

- Audit status: ddm-default-policy-decomposition-captured
- Slice id: 2025-ddm-default-attribute-policy
- Requirement count: 23
- Proof families: 6
- Direct-backed families: 6
- Hosted-backed families: 6
- Assessment: The DDM/default-policy slice is no longer just one large region-policy bucket. Its evidence separates into lookup/default-policy control, object-region routing and scope advisories, interaction-region routing, directed DDM routing, passive/compat aliases, and DDM restore/disconnect cleanup.
- Next split boundary: If this slice needs further tightening, split it first by these DDM/default-policy proof families before moving region-routing semantics into a dedicated 2025 backend.

### ddm-default-policy/lookup-and-default-policy-control

- Focus: FOM-backed dimension lookup, bounds queries, and default attribute transportation/order policy control
- Direct test count: 1
- Hosted test count: 1

### ddm-default-policy/object-region-routing-and-scope-advisories

- Focus: object reflection filtering through region overlap plus attributesInScope/attributesOutOfScope transitions
- Direct test count: 1
- Hosted test count: 1

### ddm-default-policy/interaction-region-routing

- Focus: region-filtered interaction delivery, sent-region callback context, and plain interaction subscriber cleanup
- Direct test count: 2
- Hosted test count: 2

### ddm-default-policy/directed-ddm-routing

- Focus: directed interaction delivery through object update-region and subscribeInteractionClassWithRegions overlap
- Direct test count: 3
- Hosted test count: 3

### ddm-default-policy/passive-alias-and-compat-scenarios

- Focus: passive region subscription aliases and backend-neutral compat DDM scenarios over the same semantics
- Direct test count: 5
- Hosted test count: 5

### ddm-default-policy/ddm-restore-and-disconnect-cleanup

- Focus: restore and disconnect cleanup for queued DDM delivery and directed DDM subscriber routing state
- Direct test count: 2
- Hosted test count: 2


## Shim Pressure Family Route-Backing Audit

- Audit status: shim-pressure-family-route-backing-captured
- Family count: 16
- Fully route-backed family count: 16
- All families route-backed across current Python lanes: True
- Assessment: The decomposed shim-backed pressure families are not in-process-only claims. Every currently named family across save/restore, directed interaction, and DDM/default-policy has both direct shim proof and hosted FedPro proof, which strengthens the current-lane working-RTI claim.
- Residual boundary: This still does not prove full cross-binding conformance or full requirement-by-requirement closure; it proves that the main shim-backed pressure families are executable across the current Python 2025 lanes.

- 2025-save-restore-lifecycle/lifecycle-control: direct=4, hosted=4, route-backed=True
- 2025-save-restore-lifecycle/shared-scenario-rollback: direct=4, hosted=4, route-backed=True
- 2025-save-restore-lifecycle/routing-policy-rollback: direct=6, hosted=6, route-backed=True
- 2025-save-restore-lifecycle/ownership-rollback: direct=3, hosted=3, route-backed=True
- 2025-save-restore-lifecycle/time-window-and-time-state-rollback: direct=5, hosted=5, route-backed=True
- 2025-directed-interaction-boundary/base-routing-and-callback-delivery: direct=2, hosted=2, route-backed=True
- 2025-directed-interaction-boundary/timestamped-delivery-and-retraction: direct=3, hosted=3, route-backed=True
- 2025-directed-interaction-boundary/ddm-overlap-filtering: direct=3, hosted=3, route-backed=True
- 2025-directed-interaction-boundary/selective-set-and-publication-isolation: direct=2, hosted=2, route-backed=True
- 2025-directed-interaction-boundary/restore-routing-and-stale-queue-cleanup: direct=2, hosted=2, route-backed=True
- 2025-ddm-default-attribute-policy/lookup-and-default-policy-control: direct=1, hosted=1, route-backed=True
- 2025-ddm-default-attribute-policy/object-region-routing-and-scope-advisories: direct=1, hosted=1, route-backed=True
- 2025-ddm-default-attribute-policy/interaction-region-routing: direct=2, hosted=2, route-backed=True
- 2025-ddm-default-attribute-policy/directed-ddm-routing: direct=3, hosted=3, route-backed=True
- 2025-ddm-default-attribute-policy/passive-alias-and-compat-scenarios: direct=5, hosted=5, route-backed=True
- 2025-ddm-default-attribute-policy/ddm-restore-and-disconnect-cleanup: direct=2, hosted=2, route-backed=True

## Shim Pressure Family Asymmetry Audit

- Audit status: shim-pressure-family-asymmetry-captured
- Family count: 16
- Balanced families: 16
- Direct-heavier families: 0
- Hosted-heavier families: 0
- Assessment: The main shim-backed pressure families are route-backed across the current Python lanes and are now symmetric at the named proof-family level. The remaining work is no longer family-count parity; it is deeper behavioral expansion, stronger evidence quality, and architectural judgment about whether the current 2025 lane should remain shim-backed or be extracted into a dedicated backend.
- Next parity boundary: Use the hosted-heavier and direct-heavier family rows as the next executable parity worklist for the current 2025 lane.

- 2025-save-restore-lifecycle/lifecycle-control: balance=balanced, direct=4, hosted=4, delta=0
- 2025-save-restore-lifecycle/shared-scenario-rollback: balance=balanced, direct=4, hosted=4, delta=0
- 2025-save-restore-lifecycle/routing-policy-rollback: balance=balanced, direct=6, hosted=6, delta=0
- 2025-save-restore-lifecycle/ownership-rollback: balance=balanced, direct=3, hosted=3, delta=0
- 2025-save-restore-lifecycle/time-window-and-time-state-rollback: balance=balanced, direct=5, hosted=5, delta=0
- 2025-directed-interaction-boundary/base-routing-and-callback-delivery: balance=balanced, direct=2, hosted=2, delta=0
- 2025-directed-interaction-boundary/timestamped-delivery-and-retraction: balance=balanced, direct=3, hosted=3, delta=0
- 2025-directed-interaction-boundary/ddm-overlap-filtering: balance=balanced, direct=3, hosted=3, delta=0
- 2025-directed-interaction-boundary/selective-set-and-publication-isolation: balance=balanced, direct=2, hosted=2, delta=0
- 2025-directed-interaction-boundary/restore-routing-and-stale-queue-cleanup: balance=balanced, direct=2, hosted=2, delta=0
- 2025-ddm-default-attribute-policy/lookup-and-default-policy-control: balance=balanced, direct=1, hosted=1, delta=0
- 2025-ddm-default-attribute-policy/object-region-routing-and-scope-advisories: balance=balanced, direct=1, hosted=1, delta=0
- 2025-ddm-default-attribute-policy/interaction-region-routing: balance=balanced, direct=2, hosted=2, delta=0
- 2025-ddm-default-attribute-policy/directed-ddm-routing: balance=balanced, direct=3, hosted=3, delta=0
- 2025-ddm-default-attribute-policy/passive-alias-and-compat-scenarios: balance=balanced, direct=5, hosted=5, delta=0
- 2025-ddm-default-attribute-policy/ddm-restore-and-disconnect-cleanup: balance=balanced, direct=2, hosted=2, delta=0

## Current Lane Coherence Audit

- Audit status: current-lane-coherence-captured
- Coherence claim: bounded-working-RTI-surface
- Ready for current-lane coherent working-surface claim: True
- Ready for permanent no-split architecture claim: False
- Major pressure slice count: 3
- Shim backend concentration is material: True
- All pressure families route-backed across current Python lanes: True
- Assessment: The current 2025 lane now has a defensible coherence story: its main shim-backed pressure slices are identified, decomposed into named proof families, and all of those families are executable across the current Python 2025 lanes. That is strong evidence for a coherent bounded working RTI surface even though the lane is still materially concentrated in the shim backend implementation.

Residual blockers:

- Implementation concentration in hla-backend-shim/backend.py remains material, so coherence is not the same thing as a permanently settled architecture.
- The repo now has a row-level requirement-by-requirement audit, but it still stops at bounded disposition and supported-scope proof rather than an all-covered conformance pass.
- Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.
- Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or MOM action/request conformance pass.

## Current Lane Working-Surface Statement

- Status: current-lane-working-surface-statement
- Ready: True
- Statement: The current 2025 lane can be promoted as the repo's coherent bounded working Python RTI surface: hla-backend-shim is the live Python 2025 RTI lane, its main shim-backed pressure families are route-backed across the current Python lanes, and the repo has enough evidence to make that bounded working-surface claim without hiding unsupported or legacy-only boundaries.
- Assessment: The repo now has a single explicit statement for the current 2025 lane: promote it as the bounded working Python 2025 RTI surface, keep the architecture seam intact, and continue using the remaining requirement-level and cross-binding blockers to decide whether extraction is ever warranted.

Non-claims:

- This is not a full requirement-by-requirement IEEE 1516.1-2025 conformance claim.
- This is not a permanent no-split architecture decision.
- This does not upgrade Java or C++ bindings into exhaustive behavior-conformance lanes.
- This does not turn the hosted FedPro route into a full RTI semantics or MOM action/request conformance pass.

## Implementation Lane Audit

- Audit status: current-lane-architecture-captured
- Current 2025 backend package: hla-backend-shim
- Current 2025 role: current executable Python 2025 RTI lane
- Current 2025 plugin family: shim
- Current 2025 spec support: rti1516_2025
- Reference 2010 backend package: hla-backend-inmemory
- Reference 2010 role: 2010 pure Python RTI backend
- Dedicated 2025 backend package present: False
- Ready for working-surface promotion: True
- Ready for permanent no-split decision: False
- Clean extraction still optional: True
- Assessment: The repo's current 2025 implementation reality is explicit: hla-backend-shim is the live Python 2025 backend lane, the hosted FedPro route is a route variant over that lane rather than a separate RTI family, and the older pure-Python backend remains the 2010-only inmemory lane.
- Extraction boundary: Keep using the current lane as the executable Python 2025 RTI surface unless future evidence shows that shim adaptation is obscuring core runtime semantics strongly enough to justify extracting a dedicated 2025 backend beside a narrower shim layer.

Python 2025 route variants:

- python-2025-inprocess: in-process-backend-route (separate RTI family: False, all milestone parity-covered: True)
- python-2025-fedpro-grpc: hosted-transport-route (separate RTI family: False, all milestone parity-covered: True)

## Promotion Vs Split Audit

- Decision shape: promote-current-lane-or-split-later-based-on-evidence
- Current lane package: hla-backend-shim
- Current lane role: current executable Python 2025 RTI lane
- Recommendation: promote-current-lane-as-working-surface-and-keep-split-optional
- Ready for working-surface promotion: True
- Ready for permanent no-split decision: False
- Assessment: Current evidence is strong enough to treat hla-backend-shim as the live Python 2025 RTI lane for bounded working-surface claims, including across the main shim-backed pressure families, but not strong enough to make a permanent no-split architectural decision.

Promotion basis:

- The current 2025 lane has green executable runtime coverage in the main in-process suite.
- Both Python 2025 routes clear the tracked bounded working-surface milestones.
- The repo can make a supported-boundary statement over the current 2025 lane without hiding unsupported areas.
- Route parity partial and missing counts are both zero for the tracked 2025 matrix.
- The callback ledger is fully route-backed across the current Python 2025 lanes, eliminating callback-helper-only gaps in the promotion surface.
- The main shim-backed pressure families across save/restore, directed interaction, and DDM/default-policy are all route-backed across the current Python 2025 lanes.

Split triggers:

- Adapter concerns begin to obscure or distort core RTI semantics.
- Callback or route normalization grows more complex than the underlying RTI behavior it wraps.
- New 2025 behavior is materially harder to implement because shim and RTI state management are too tightly mixed.
- The row-level requirement-by-requirement audit cannot be promoted from bounded disposition evidence to cleaner all-covered runtime proof without separating a narrower shim from a dedicated 2025 backend.

Permanent-decision blockers:

- The repo now has a row-level requirement-by-requirement audit, but it is still a bounded disposition audit rather than an all-covered 2025 conformance pass.
- Several implemented slices still aggregate multiple requirements under bounded supported-scope language.
- Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or MOM action/request conformance pass.
- Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.

## Objective Audit

- Surface claim: bounded-working-surface
- Ready for bounded working-surface claim: True
- Ready for full 2025 completion claim: False
- Bounded-ready dimensions: 8 / 8
- Assessment: The repo now supports a bounded working-surface claim across the core runtime dimensions, but that is still weaker than a final 2025 conformance claim because several areas remain slice-bounded or artifact-gated rather than requirement-by-requirement proven.

### Federation Management

- Evidence level: strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: federation_lifecycle, save_restore
- Assessment: Connection, federation catalog control, membership reporting/resign, synchronization barriers, and save/restore behavior are exercised directly through the Python 2025 shim and the hosted FedPro route, with parity scenarios recorded across all tracked routes.

- Residual blocker: The evidence is still slice-oriented rather than service-by-service proof.
- Residual blocker: Standard Java and C++ route coverage remains scenario parity/runtime capability evidence, not exhaustive behavior conformance.

### Object Management

- Evidence level: strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: object_exchange, ownership, ddm
- Assessment: The current repo proves a coherent object-management surface: object and interaction exchange, directed interactions, ownership transfer/query callbacks, DDM overlap filtering, transportation policy changes, and object deletion flows all execute end to end.

- Residual blocker: Requirement aggregation still hides per-service completion detail inside supported-scope slices.
- Residual blocker: FedPro coverage is a hosted runtime slice and does not yet constitute full RTI semantics proof.

### Time Management

- Evidence level: strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: time_management, save_restore
- Assessment: Logical-time factories, regulation/constrained mode transitions, advance-request modes, grants, lookahead/query control, timestamped delivery, retraction, and save/restore rollback are all backed by executable runtime traces.

- Residual blocker: The closeout still aggregates multiple time services into bounded slices instead of final per-requirement proof.
- Residual blocker: Cross-binding runtime evidence is narrower than the Python in-process and hosted FedPro slices.

### Support Services

- Evidence level: strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: support_services
- Assessment: Handle lookup, dimension bounds, default policy control, normalization and switch inquiry/set flows are exercised through the Python runtime and are represented across tracked binding routes. The finish-line now also carries an explicit support-service ledger via the RTIambassador conformance matrix.

- Residual blocker: The support-service ledger is executable and negative-path complete inside the Python routes, but it is still aggregated as a bounded slice rather than a final per-service conformance audit.
- Residual blocker: Java and C++ proof remains capability-oriented rather than a full standard-route behavior pass.

### Ownership Management

- Evidence level: strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: ownership, save_restore
- Assessment: Ownership acquisition, divestiture, release negotiation, query callbacks, resign-time policies, and rollback-sensitive ownership state are all exercised directly through the Python 2025 shim and through shared backend-matrix scenarios.

- Residual blocker: The closeout still groups ownership proof into bounded runtime slices rather than a final clause-by-clause ownership audit.
- Residual blocker: Hosted route parity remains scenario-backed runtime evidence, not a full vendor-equivalent ownership conformance pass.

### Callbacks

- Evidence level: strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: federation_lifecycle, object_exchange, ownership, time_management, save_restore, mom, support_services
- Assessment: Callback delivery is broad and executable across lifecycle, object, ownership, DDM, time, MOM, and support-service flows, including hosted FedPro callback decoding and direct Python ambassador behavior. The finish-line now also carries an explicit callback-by-callback ledger via the FederateAmbassador conformance matrix, and that ledger is fully route-backed across the current Python 2025 lanes.

- Residual blocker: The callback ledger still stops short of exhaustive cross-binding callback signature/ordering equivalence proof.
- Residual blocker: Binding-route callback parity is tracked at the scenario level, not as exhaustive callback signature/ordering proof.

### OMT Handling

- Evidence level: bounded-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: none
- Assessment: The OMT path is well-instrumented for the supported parser/serializer/schema subset and now explicitly records the unsupported boundaries instead of leaving them implicit.

- Residual blocker: OMT evidence includes explicit unsupported boundaries, so this area cannot be promoted to full 2025 conformance.
- Residual blocker: Parser/serializer support is intentionally narrower than the full 2025 schema/component space.

### Binding Routes

- Evidence level: bounded-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: federation_lifecycle, object_exchange, ownership, ddm, time_management, save_restore, mom, support_services
- Assessment: Every tracked 2025 route now has explicit scenario parity rows, and the Python in-process plus hosted FedPro routes provide substantive runtime proof for the working surface.

- Residual blocker: Java and C++ routes are still backed by artifact/runtime-capability traces rather than exhaustive behavior equivalence proof.
- Residual blocker: The hosted FedPro route remains a bounded working slice, not a full RTI conformance route.


## Implemented Evidence Slices

| Slice | Status | Requirements | Evidence |
|---|---|---|---|
| 2025-factory-composition | implemented-slice | HLA2025-REQ-001, HLA2025-FI-003, HLA2025-FI-004 | tests/test_hla_factory_composition.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-auth-connect | implemented-slice | HLA2025-MOD-001, HLA2025-FI-005 | tests/test_rti1516_2025_encoding_auth_contexts.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-fom-validation | implemented-slice | HLA2025-FR-001, HLA2025-OMT-001, HLA2025-OMT-005, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, tests/test_hla_factory_composition.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py |
| 2025-lifecycle-and-members | implemented-slice | HLA2025-FI-005, HLA2025-FI-006, HLA2025-NEW-002, HLA2025-NEW-003 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-time-mode-enable-disable | implemented-slice | HLA2025-FI-SVC-101, HLA2025-FI-SVC-102, HLA2025-FI-SVC-103, HLA2025-FI-SVC-104, HLA2025-FI-SVC-105, HLA2025-FI-SVC-106 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-advance-request-modes | implemented-slice | HLA2025-FI-SVC-107, HLA2025-FI-SVC-108, HLA2025-FI-SVC-109, HLA2025-FI-SVC-110, HLA2025-FI-SVC-111 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-grant-and-async-delivery | implemented-slice | HLA2025-FI-SVC-112, HLA2025-FI-SVC-113, HLA2025-FI-SVC-114, HLA2025-FI-SVC-115 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-query-and-lookahead-control | implemented-slice | HLA2025-FI-SVC-116, HLA2025-FI-SVC-117, HLA2025-FI-SVC-118, HLA2025-FI-SVC-119, HLA2025-FI-SVC-120 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-queries-retraction-and-order | implemented-slice | HLA2025-FI-SVC-121, HLA2025-FI-SVC-122, HLA2025-FI-SVC-123, HLA2025-FI-SVC-124, HLA2025-FI-SVC-125, HLA2025-FR-010, HLA2025-FI-009 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, tests/backends/test_shim_route_trace_evidence.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-lookahead-window-proofs | implemented-slice | HLA2025-FI-SVC-107, HLA2025-FI-SVC-108, HLA2025-FI-SVC-121, HLA2025-FI-SVC-122, HLA2025-FI-SVC-123, HLA2025-MOD-006 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, tests/backends/test_shim_route_trace_evidence.py |
| 2025-save-restore-lifecycle | implemented-slice | HLA2025-FI-SVC-018, HLA2025-FI-SVC-019, HLA2025-FI-SVC-020, HLA2025-FI-SVC-021, HLA2025-FI-SVC-022, HLA2025-FI-SVC-023, HLA2025-FI-SVC-024, HLA2025-FI-SVC-025, HLA2025-FI-SVC-026, HLA2025-FI-SVC-027, HLA2025-FI-SVC-028, HLA2025-FI-SVC-029, HLA2025-FI-SVC-030, HLA2025-FI-SVC-031, HLA2025-FI-SVC-032, HLA2025-FI-SVC-033, HLA2025-FI-SVC-034, HLA2025-FI-001, HLA2025-FI-005, HLA2025-REQ-002 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-fom-showcase | implemented-slice | HLA2025-FR-001, HLA2025-FR-003, HLA2025-FR-004 | tests/scenarios/test_proto2025_fom_showcase.py, packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py |
| 2025-handle-normalization | implemented-slice | HLA2025-NEW-005, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-switch-set-get-model | implemented-slice | HLA2025-MOD-008, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-retired-advisory-switch-enable-disable-mapping | legacy-only | HLA2025-RET-001 | tests/requirements/test_2025_tail_backlog_evidence.py, docs/requirements/ieee-1516-2025/retired_legacy_mapping.md, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-fom-mim-error-taxonomy | implemented-slice | HLA2025-MOD-002, HLA2025-MOD-003, HLA2025-FI-008, HLA2025-OMT-007 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-callback-context-object-delivery | implemented-slice | HLA2025-MOD-004, HLA2025-RET-002, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-callback-context-interaction-delivery | implemented-slice | HLA2025-MOD-004, HLA2025-RET-002, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-directed-interaction-boundary | implemented-slice | HLA2025-MOD-007, HLA2025-NEW-001, HLA2025-FR-003, HLA2025-FR-004, HLA2025-FI-001, HLA2025-FI-SVC-039, HLA2025-FI-SVC-040, HLA2025-FI-SVC-045, HLA2025-FI-SVC-046, HLA2025-FI-SVC-063, HLA2025-FI-SVC-064 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-omt-reference-value-required | implemented-slice | HLA2025-NEW-006, HLA2025-OMT-002, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py |
| 2025-omt-component-metadata-roundtrip | implemented-slice | HLA2025-OMT-COMP-004, HLA2025-OMT-COMP-013, HLA2025-OMT-COMP-030, HLA2025-OMT-COMP-084, HLA2025-OMT-COMP-085, HLA2025-OMT-COMP-087, HLA2025-OMT-COMP-090, HLA2025-OMT-COMP-094, HLA2025-OMT-COMP-140, HLA2025-OMT-COMP-141, HLA2025-OMT-COMP-142, HLA2025-OMT-COMP-143, HLA2025-OMT-COMP-144, HLA2025-OMT-COMP-146, HLA2025-OMT-COMP-150, HLA2025-OMT-COMP-151, HLA2025-OMT-COMP-152, HLA2025-OMT-COMP-190, HLA2025-OMT-COMP-191, HLA2025-OMT-COMP-194, HLA2025-OMT-COMP-195, HLA2025-OMT-COMP-215 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-omt-switch-and-transport-subset | implemented-slice | HLA2025-OMT-COMP-078, HLA2025-OMT-COMP-125, HLA2025-OMT-COMP-157, HLA2025-OMT-COMP-158, HLA2025-OMT-COMP-159, HLA2025-OMT-COMP-160, HLA2025-OMT-COMP-161, HLA2025-OMT-COMP-162, HLA2025-OMT-COMP-163, HLA2025-OMT-COMP-164, HLA2025-OMT-COMP-165, HLA2025-OMT-COMP-167 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-omt-extended-supported-subset | implemented-slice | HLA2025-OMT-COMP-001, HLA2025-OMT-COMP-002, HLA2025-OMT-COMP-003, HLA2025-OMT-COMP-005, HLA2025-OMT-COMP-007, HLA2025-OMT-COMP-009, HLA2025-OMT-COMP-010, HLA2025-OMT-COMP-016, HLA2025-OMT-COMP-020, HLA2025-OMT-COMP-022, HLA2025-OMT-COMP-023, HLA2025-OMT-COMP-024, HLA2025-OMT-COMP-025, HLA2025-OMT-COMP-026, HLA2025-OMT-COMP-028, HLA2025-OMT-COMP-029, HLA2025-OMT-COMP-031, HLA2025-OMT-COMP-032, HLA2025-OMT-COMP-033, HLA2025-OMT-COMP-034, HLA2025-OMT-COMP-036, HLA2025-OMT-COMP-046, HLA2025-OMT-COMP-050, HLA2025-OMT-COMP-051, HLA2025-OMT-COMP-052, HLA2025-OMT-COMP-053, HLA2025-OMT-COMP-054, HLA2025-OMT-COMP-055, HLA2025-OMT-COMP-058, HLA2025-OMT-COMP-060, HLA2025-OMT-COMP-061, HLA2025-OMT-COMP-062, HLA2025-OMT-COMP-063, HLA2025-OMT-COMP-064, HLA2025-OMT-COMP-065, HLA2025-OMT-COMP-066, HLA2025-OMT-COMP-069, HLA2025-OMT-COMP-071, HLA2025-OMT-COMP-072, HLA2025-OMT-COMP-073, HLA2025-OMT-COMP-086, HLA2025-OMT-COMP-088, HLA2025-OMT-COMP-089, HLA2025-OMT-COMP-091, HLA2025-OMT-COMP-092, HLA2025-OMT-COMP-093, HLA2025-OMT-COMP-095, HLA2025-OMT-COMP-096, HLA2025-OMT-COMP-097, HLA2025-OMT-COMP-098, HLA2025-OMT-COMP-099, HLA2025-OMT-COMP-100, HLA2025-OMT-COMP-101, HLA2025-OMT-COMP-103, HLA2025-OMT-COMP-104, HLA2025-OMT-COMP-105, HLA2025-OMT-COMP-108, HLA2025-OMT-COMP-116, HLA2025-OMT-COMP-117, HLA2025-OMT-COMP-118, HLA2025-OMT-COMP-119, HLA2025-OMT-COMP-120, HLA2025-OMT-COMP-121, HLA2025-OMT-COMP-122, HLA2025-OMT-COMP-123, HLA2025-OMT-COMP-124, HLA2025-OMT-COMP-126, HLA2025-OMT-COMP-127, HLA2025-OMT-COMP-128, HLA2025-OMT-COMP-131, HLA2025-OMT-COMP-132, HLA2025-OMT-COMP-135, HLA2025-OMT-COMP-136, HLA2025-OMT-COMP-137, HLA2025-OMT-COMP-138, HLA2025-OMT-COMP-139, HLA2025-OMT-COMP-148, HLA2025-OMT-COMP-149, HLA2025-OMT-COMP-153, HLA2025-OMT-COMP-155, HLA2025-OMT-COMP-172, HLA2025-OMT-COMP-173, HLA2025-OMT-COMP-174, HLA2025-OMT-COMP-175, HLA2025-OMT-COMP-177, HLA2025-OMT-COMP-179, HLA2025-OMT-COMP-180, HLA2025-OMT-COMP-182, HLA2025-OMT-COMP-183, HLA2025-OMT-COMP-184, HLA2025-OMT-COMP-185, HLA2025-OMT-COMP-186, HLA2025-OMT-COMP-187, HLA2025-OMT-COMP-188, HLA2025-OMT-COMP-199, HLA2025-OMT-COMP-203, HLA2025-OMT-COMP-205, HLA2025-OMT-COMP-206, HLA2025-OMT-COMP-209, HLA2025-OMT-COMP-211, HLA2025-OMT-COMP-212, HLA2025-OMT-COMP-213, HLA2025-OMT-COMP-214, HLA2025-OMT-COMP-216, HLA2025-OMT-COMP-217, HLA2025-OMT-COMP-218, HLA2025-OMT-COMP-220, HLA2025-OMT-COMP-221, HLA2025-OMT-COMP-223 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-omt-unsupported-component-boundaries | unsupported-boundary | HLA2025-OMT-COMP-037, HLA2025-OMT-COMP-038, HLA2025-OMT-COMP-039, HLA2025-OMT-COMP-040, HLA2025-OMT-COMP-042, HLA2025-OMT-COMP-043, HLA2025-OMT-COMP-048, HLA2025-OMT-COMP-049, HLA2025-OMT-COMP-074, HLA2025-OMT-COMP-079, HLA2025-OMT-COMP-110, HLA2025-OMT-COMP-111, HLA2025-OMT-COMP-112, HLA2025-OMT-COMP-113, HLA2025-OMT-COMP-145, HLA2025-OMT-COMP-147, HLA2025-OMT-COMP-166, HLA2025-OMT-COMP-168, HLA2025-OMT-COMP-169, HLA2025-OMT-COMP-170, HLA2025-OMT-COMP-192, HLA2025-OMT-COMP-193, HLA2025-OMT-COMP-196, HLA2025-OMT-COMP-197 | tests/factories/test_fom_omt_parsing.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-omt-unmodeled-component-boundaries-expanded | unsupported-boundary | HLA2025-OMT-COMP-006, HLA2025-OMT-COMP-008, HLA2025-OMT-COMP-011, HLA2025-OMT-COMP-012, HLA2025-OMT-COMP-014, HLA2025-OMT-COMP-015, HLA2025-OMT-COMP-017, HLA2025-OMT-COMP-018, HLA2025-OMT-COMP-019, HLA2025-OMT-COMP-021, HLA2025-OMT-COMP-027, HLA2025-OMT-COMP-035, HLA2025-OMT-COMP-041, HLA2025-OMT-COMP-044, HLA2025-OMT-COMP-045, HLA2025-OMT-COMP-047, HLA2025-OMT-COMP-056, HLA2025-OMT-COMP-057, HLA2025-OMT-COMP-059, HLA2025-OMT-COMP-067, HLA2025-OMT-COMP-068, HLA2025-OMT-COMP-070, HLA2025-OMT-COMP-075, HLA2025-OMT-COMP-076, HLA2025-OMT-COMP-077, HLA2025-OMT-COMP-080, HLA2025-OMT-COMP-081, HLA2025-OMT-COMP-082, HLA2025-OMT-COMP-083, HLA2025-OMT-COMP-102, HLA2025-OMT-COMP-106, HLA2025-OMT-COMP-107, HLA2025-OMT-COMP-109, HLA2025-OMT-COMP-114, HLA2025-OMT-COMP-115, HLA2025-OMT-COMP-129, HLA2025-OMT-COMP-130, HLA2025-OMT-COMP-133, HLA2025-OMT-COMP-134, HLA2025-OMT-COMP-154, HLA2025-OMT-COMP-156, HLA2025-OMT-COMP-171, HLA2025-OMT-COMP-176, HLA2025-OMT-COMP-178, HLA2025-OMT-COMP-181, HLA2025-OMT-COMP-189, HLA2025-OMT-COMP-198, HLA2025-OMT-COMP-200, HLA2025-OMT-COMP-201, HLA2025-OMT-COMP-202, HLA2025-OMT-COMP-204, HLA2025-OMT-COMP-207, HLA2025-OMT-COMP-208, HLA2025-OMT-COMP-210, HLA2025-OMT-COMP-219, HLA2025-OMT-COMP-222, HLA2025-OMT-COMP-224 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-carry-forward-cleanup | implemented-slice | HLA2025-BLG-001, HLA2025-BLG-002, HLA2025-REQ-001 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv, requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv, tests/test_rti1516_2025_validation.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-service-utilization-crosscheck | implemented-slice | HLA2025-OMT-SU-001, HLA2025-OMT-SU-002, HLA2025-OMT-SU-003, HLA2025-OMT-SU-004, HLA2025-OMT-SU-005, HLA2025-OMT-SU-006, HLA2025-OMT-SU-007, HLA2025-OMT-SU-008, HLA2025-OMT-SU-009, HLA2025-OMT-SU-010, HLA2025-OMT-SU-011, HLA2025-OMT-SU-012, HLA2025-OMT-SU-013, HLA2025-OMT-SU-014, HLA2025-OMT-SU-015, HLA2025-OMT-SU-016, HLA2025-OMT-SU-017, HLA2025-OMT-SU-018, HLA2025-OMT-SU-019, HLA2025-OMT-SU-020, HLA2025-OMT-SU-021, HLA2025-OMT-SU-022, HLA2025-OMT-SU-023, HLA2025-OMT-SU-024, HLA2025-OMT-SU-025, HLA2025-OMT-SU-026, HLA2025-OMT-SU-027, HLA2025-OMT-SU-028, HLA2025-OMT-SU-029, HLA2025-OMT-SU-030, HLA2025-OMT-SU-031, HLA2025-OMT-SU-032, HLA2025-OMT-SU-033, HLA2025-OMT-SU-034, HLA2025-OMT-SU-035, HLA2025-OMT-SU-036, HLA2025-OMT-SU-037, HLA2025-OMT-SU-038, HLA2025-OMT-SU-039, HLA2025-OMT-SU-040, HLA2025-OMT-SU-041, HLA2025-OMT-SU-042, HLA2025-OMT-SU-043, HLA2025-OMT-SU-044, HLA2025-OMT-SU-045, HLA2025-OMT-SU-046, HLA2025-OMT-SU-047, HLA2025-OMT-SU-048, HLA2025-OMT-SU-049, HLA2025-OMT-SU-050, HLA2025-OMT-SU-051, HLA2025-OMT-SU-052, HLA2025-OMT-SU-053, HLA2025-OMT-SU-054, HLA2025-OMT-SU-055, HLA2025-OMT-SU-056, HLA2025-OMT-SU-057, HLA2025-OMT-SU-058, HLA2025-OMT-SU-059, HLA2025-OMT-SU-060, HLA2025-OMT-SU-061, HLA2025-OMT-SU-062, HLA2025-OMT-SU-063, HLA2025-OMT-SU-064, HLA2025-OMT-SU-065, HLA2025-OMT-SU-066, HLA2025-OMT-SU-067, HLA2025-OMT-SU-068, HLA2025-OMT-SU-069, HLA2025-OMT-SU-070, HLA2025-OMT-SU-071, HLA2025-OMT-SU-072, HLA2025-OMT-SU-073, HLA2025-OMT-SU-074, HLA2025-OMT-SU-075, HLA2025-OMT-SU-076, HLA2025-OMT-SU-077, HLA2025-OMT-SU-078, HLA2025-OMT-SU-079, HLA2025-OMT-SU-080, HLA2025-OMT-SU-081, HLA2025-OMT-SU-082, HLA2025-OMT-SU-083, HLA2025-OMT-SU-084, HLA2025-OMT-SU-085, HLA2025-OMT-SU-086, HLA2025-OMT-SU-087, HLA2025-OMT-SU-088, HLA2025-OMT-SU-089, HLA2025-OMT-SU-090, HLA2025-OMT-SU-091, HLA2025-OMT-SU-092, HLA2025-OMT-SU-093, HLA2025-OMT-SU-094, HLA2025-OMT-SU-095, HLA2025-OMT-SU-096, HLA2025-OMT-SU-097, HLA2025-OMT-SU-098, HLA2025-OMT-SU-099, HLA2025-OMT-SU-100, HLA2025-OMT-SU-101, HLA2025-OMT-SU-102, HLA2025-OMT-SU-103, HLA2025-OMT-SU-104, HLA2025-OMT-SU-105, HLA2025-OMT-SU-106, HLA2025-OMT-SU-107, HLA2025-OMT-SU-108, HLA2025-OMT-SU-109, HLA2025-OMT-SU-110, HLA2025-OMT-SU-111, HLA2025-OMT-SU-112, HLA2025-OMT-SU-113, HLA2025-OMT-SU-114, HLA2025-OMT-SU-115, HLA2025-OMT-SU-116, HLA2025-OMT-SU-117, HLA2025-OMT-SU-118, HLA2025-OMT-SU-119, HLA2025-OMT-SU-120, HLA2025-OMT-SU-121, HLA2025-OMT-SU-122, HLA2025-OMT-SU-123, HLA2025-OMT-SU-124, HLA2025-OMT-SU-125, HLA2025-OMT-SU-126, HLA2025-OMT-SU-127, HLA2025-OMT-SU-128, HLA2025-OMT-SU-129, HLA2025-OMT-SU-130, HLA2025-OMT-SU-131, HLA2025-OMT-SU-132, HLA2025-OMT-SU-133, HLA2025-OMT-SU-134, HLA2025-OMT-SU-135, HLA2025-OMT-SU-136, HLA2025-OMT-SU-137, HLA2025-OMT-SU-138, HLA2025-OMT-SU-139, HLA2025-OMT-SU-140, HLA2025-OMT-SU-141, HLA2025-OMT-SU-142, HLA2025-OMT-SU-143, HLA2025-OMT-SU-144, HLA2025-OMT-SU-145, HLA2025-OMT-SU-146, HLA2025-OMT-SU-147, HLA2025-OMT-SU-148, HLA2025-OMT-SU-149, HLA2025-OMT-SU-150, HLA2025-OMT-SU-151, HLA2025-OMT-SU-152, HLA2025-OMT-SU-153, HLA2025-OMT-SU-154, HLA2025-OMT-SU-155, HLA2025-OMT-SU-156, HLA2025-OMT-SU-157, HLA2025-OMT-SU-158, HLA2025-OMT-SU-159, HLA2025-OMT-SU-160, HLA2025-OMT-SU-161, HLA2025-OMT-SU-162, HLA2025-OMT-SU-163, HLA2025-OMT-SU-164, HLA2025-OMT-SU-165, HLA2025-OMT-SU-166, HLA2025-OMT-SU-167, HLA2025-OMT-SU-168, HLA2025-OMT-SU-169, HLA2025-OMT-SU-170, HLA2025-OMT-SU-171, HLA2025-OMT-SU-172, HLA2025-OMT-SU-173, HLA2025-OMT-SU-174, HLA2025-OMT-SU-175, HLA2025-OMT-SU-176, HLA2025-OMT-SU-177, HLA2025-OMT-SU-178, HLA2025-OMT-SU-179, HLA2025-OMT-SU-180, HLA2025-OMT-SU-181, HLA2025-OMT-SU-182, HLA2025-OMT-SU-183, HLA2025-OMT-SU-184, HLA2025-OMT-SU-185, HLA2025-OMT-SU-186, HLA2025-OMT-SU-187, HLA2025-OMT-SU-188, HLA2025-OMT-SU-189, HLA2025-OMT-SU-190, HLA2025-OMT-SU-191, HLA2025-OMT-SU-192, HLA2025-OMT-SU-193, HLA2025-OMT-SU-194, HLA2025-OMT-SU-195, HLA2025-OMT-SU-196 | tests/factories/test_fom_omt_parsing.py, tests/factories/test_fom_roundtrip.py, tests/requirements/test_2025_tail_backlog_evidence.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-exception-and-logical-time-deltas | implemented-slice | HLA2025-MOD-009, HLA2025-MOD-010, HLA2025-VER-002 | tests/requirements/test_2025_tail_backlog_evidence.py, tests/test_rti1516_2025_validation.py, requirements/2025/STRICT_DOC_INVENTORY.json, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-java-binding-source-trace | implemented-slice | HLA2025-BND-001, HLA2025-FI-003, HLA2025-FI-004 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/STRICT_DOC_INVENTORY.json, requirements/2025/SOURCE_TRACE.md, docs/evidence/java-intake/java-2025-standard-shim-2025-jpype.json, docs/evidence/java-intake/java-2025-standard-shim-2025-py4j.json |
| 2025-cpp-binding-source-trace | implemented-slice | HLA2025-BND-002, HLA2025-FI-003, HLA2025-FI-004 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/SOURCE_TRACE.md, docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json, docs/evidence/cpp-intake/cpp-standard-2025-2025-grpc.json, docs/evidence/shim_routes/cpp-standard-2025.json |
| 2025-standard-route-runtime-capability | implemented-slice | HLA2025-BND-001, HLA2025-BND-002, HLA2025-FR-001, HLA2025-FR-004, HLA2025-FI-001, HLA2025-FI-003, HLA2025-FI-004, HLA2025-FI-005, HLA2025-FI-006, HLA2025-FI-009, HLA2025-MOD-005, HLA2025-MOD-006, HLA2025-MOD-007, HLA2025-NEW-004, HLA2025-NEW-007 | tests/backends/test_standard_shim_artifacts.py, packages/hla-verification/src/hla/verification/shim_route_evidence.py, packages/hla-bridge-java-common/src/hla/bridges/java/common/java_standard_2025.py, packages/hla-backend-cpp-shim/src/hla/backends/cpp_shim/standard.py |
| 2025-fedpro-typed-transport-surface | implemented-slice | HLA2025-BND-003, HLA2025-FI-004 | tests/requirements/test_2025_tail_backlog_evidence.py, tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto |
| 2025-fedpro-hosted-runtime-core | implemented-slice | HLA2025-BND-003, HLA2025-FI-004 | tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-fedpro-hosted-runtime-extended-state | implemented-slice | HLA2025-BND-003, HLA2025-FI-004 | tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-ddm-default-attribute-policy | implemented-slice | HLA2025-MOD-007, HLA2025-NEW-004, HLA2025-FI-001, HLA2025-FI-005, HLA2025-FI-SVC-159, HLA2025-FI-SVC-160, HLA2025-FI-SVC-161, HLA2025-FI-SVC-164, HLA2025-FI-SVC-128, HLA2025-FI-SVC-129, HLA2025-FI-SVC-126, HLA2025-FI-SVC-127, HLA2025-FI-SVC-130, HLA2025-FI-SVC-131, HLA2025-FI-SVC-132, HLA2025-FI-SVC-133, HLA2025-FI-SVC-134, HLA2025-FI-SVC-135, HLA2025-FI-SVC-136, HLA2025-FI-SVC-137, HLA2025-FI-SVC-076, HLA2025-FI-SVC-124, HLA2025-FI-SVC-157 | tests/test_rti1516_2025_spec_and_shim.py, tests/backends/test_python_backend_time_ddm_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-omt-schema-constraint-validation | implemented-slice | HLA2025-OMT-CV-001, HLA2025-OMT-CV-002, HLA2025-OMT-CV-003, HLA2025-OMT-CV-004, HLA2025-OMT-CV-005, HLA2025-OMT-CV-006, HLA2025-OMT-CV-007, HLA2025-OMT-CV-008, HLA2025-OMT-CV-009, HLA2025-OMT-CV-010, HLA2025-OMT-CV-011, HLA2025-OMT-CV-012, HLA2025-OMT-CV-013, HLA2025-OMT-CV-014, HLA2025-OMT-CV-015, HLA2025-OMT-CV-016, HLA2025-OMT-CV-017, HLA2025-OMT-CV-018, HLA2025-OMT-CV-019, HLA2025-OMT-CV-020, HLA2025-OMT-CV-021, HLA2025-OMT-CV-022, HLA2025-OMT-CV-023, HLA2025-OMT-CV-024, HLA2025-OMT-CV-025, HLA2025-OMT-CV-026, HLA2025-OMT-CV-027, HLA2025-OMT-CV-028, HLA2025-OMT-CV-029 | tests/test_rti1516_2025_validation.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py, docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd |
| 2025-basic-object-exchange | implemented-slice | HLA2025-FI-SVC-057, HLA2025-FI-SVC-058, HLA2025-FI-SVC-059, HLA2025-FI-SVC-060, HLA2025-FI-SVC-061, HLA2025-FI-SVC-062, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-object-delete-remove-flows | implemented-slice | HLA2025-FI-SVC-065, HLA2025-FI-SVC-066, HLA2025-FI-SVC-067, HLA2025-FR-003, HLA2025-FR-004, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-object-attribute-update-request-callbacks | implemented-slice | HLA2025-FI-SVC-070, HLA2025-FI-SVC-071, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-object-scope-advisory-callbacks | implemented-slice | HLA2025-FI-SVC-068, HLA2025-FI-SVC-069, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-object-update-rate-advisory-callbacks | implemented-slice | HLA2025-FI-SVC-072, HLA2025-FI-SVC-073, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-object-attribute-transport-callbacks | implemented-slice | HLA2025-FI-SVC-074, HLA2025-FI-SVC-075, HLA2025-FI-SVC-077, HLA2025-FI-SVC-078, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-object-interaction-transport-callbacks | implemented-slice | HLA2025-FI-SVC-079, HLA2025-FI-SVC-080, HLA2025-FI-SVC-081, HLA2025-FI-SVC-082, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-single-name-reservation-services | implemented-slice | HLA2025-FI-SVC-051, HLA2025-FI-SVC-052, HLA2025-FI-SVC-053, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-multi-name-reservation-services | implemented-slice | HLA2025-FI-SVC-054, HLA2025-FI-SVC-055, HLA2025-FI-SVC-056, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-connection-lifecycle-services | implemented-slice | HLA2025-FI-SVC-002, HLA2025-FI-SVC-003 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-connect-and-federation-catalog-services | implemented-slice | HLA2025-FI-SVC-001, HLA2025-FI-SVC-004, HLA2025-FI-SVC-005, HLA2025-FI-SVC-006, HLA2025-FI-SVC-007 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-federate-membership-and-resign-services | implemented-slice | HLA2025-FI-SVC-008, HLA2025-FI-SVC-009, HLA2025-FI-SVC-010, HLA2025-FI-SVC-011, HLA2025-FI-SVC-012 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-synchronization-point-services | implemented-slice | HLA2025-FI-SVC-013, HLA2025-FI-SVC-014, HLA2025-FI-SVC-015, HLA2025-FI-SVC-016, HLA2025-FI-SVC-017 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-declaration-publication-services | implemented-slice | HLA2025-FI-SVC-035, HLA2025-FI-SVC-036, HLA2025-FI-SVC-037, HLA2025-FI-SVC-038, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-declaration-subscription-services | implemented-slice | HLA2025-FI-SVC-041, HLA2025-FI-SVC-042, HLA2025-FI-SVC-043, HLA2025-FI-SVC-044, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-declaration-relevance-advisory-callbacks | implemented-slice | HLA2025-FI-SVC-047, HLA2025-FI-SVC-048, HLA2025-FI-SVC-049, HLA2025-FI-SVC-050 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-federate-and-object-identity-lookups | implemented-slice | HLA2025-FI-SVC-138, HLA2025-FI-SVC-139, HLA2025-FI-SVC-140, HLA2025-FI-SVC-141, HLA2025-FI-SVC-142, HLA2025-FI-SVC-143, HLA2025-FI-SVC-144, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_support_services_backend_matrix.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-attribute-interaction-catalog-lookups | implemented-slice | HLA2025-FI-SVC-145, HLA2025-FI-SVC-146, HLA2025-FI-SVC-149, HLA2025-FI-SVC-150, HLA2025-FI-SVC-151, HLA2025-FI-SVC-152, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_support_services_backend_matrix.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-policy-update-and-transport-lookups | implemented-slice | HLA2025-FI-SVC-147, HLA2025-FI-SVC-148, HLA2025-FI-SVC-153, HLA2025-FI-SVC-154, HLA2025-FI-SVC-155, HLA2025-FI-SVC-156, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_support_services_backend_matrix.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-interaction-dimension-and-range-lookups | implemented-slice | HLA2025-FI-SVC-158, HLA2025-FI-SVC-163, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/backends/test_python_backend_support_services.py, tests/backends/test_python_backend_time_ddm_extended.py, tests/verification/test_spec_traceability_and_extended_python_rti.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-handle-normalization-and-region-introspection | implemented-slice | HLA2025-FI-SVC-162, HLA2025-FI-SVC-165, HLA2025-FI-SVC-166, HLA2025-FI-SVC-167, HLA2025-FI-SVC-168, HLA2025-FI-SVC-169 | tests/test_rti1516_2025_spec_and_shim.py, tests/backends/test_python_backend_time_ddm_extended.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-advisory-and-reporting-state-inquiries | implemented-slice | HLA2025-FI-SVC-170, HLA2025-FI-SVC-172, HLA2025-FI-SVC-174, HLA2025-FI-SVC-176, HLA2025-FI-SVC-178, HLA2025-FI-SVC-182, HLA2025-FI-SVC-184, HLA2025-FI-SVC-186 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-runtime-policy-state-inquiries | implemented-slice | HLA2025-FI-SVC-180, HLA2025-FI-SVC-188, HLA2025-FI-SVC-189, HLA2025-FI-SVC-190, HLA2025-FI-SVC-191, HLA2025-FI-SVC-192 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-advisory-and-reporting-state-controls | implemented-slice | HLA2025-FI-SVC-171, HLA2025-FI-SVC-173, HLA2025-FI-SVC-175, HLA2025-FI-SVC-177, HLA2025-FI-SVC-179, HLA2025-FI-SVC-183, HLA2025-FI-SVC-185, HLA2025-FI-SVC-187 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-support-runtime-policy-state-controls | implemented-slice | HLA2025-FI-SVC-181 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-callback-control-services | implemented-slice | HLA2025-FI-SVC-193, HLA2025-FI-SVC-194, HLA2025-FI-SVC-195, HLA2025-FI-SVC-196 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto |
| 2025-ownership-divestiture-confirmation-flows | implemented-slice | HLA2025-FI-SVC-083, HLA2025-FI-SVC-084, HLA2025-FI-SVC-086, HLA2025-FI-SVC-087, HLA2025-FI-SVC-095, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-ownership-release-and-if-wanted-flows | implemented-slice | HLA2025-FI-SVC-092, HLA2025-FI-SVC-093, HLA2025-FI-SVC-094, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-ownership-acquisition-assumption-flows | implemented-slice | HLA2025-FI-SVC-085, HLA2025-FI-SVC-088, HLA2025-FI-SVC-089, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-ownership-acquisition-availability-cancellation-flows | implemented-slice | HLA2025-FI-SVC-090, HLA2025-FI-SVC-091, HLA2025-FI-SVC-096, HLA2025-FI-SVC-097, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-ownership-query-and-resign-policies | implemented-slice | HLA2025-FI-SVC-098, HLA2025-FI-SVC-099, HLA2025-FI-SVC-100, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-mom-service-report-records | implemented-slice | HLA2025-NEW-007, HLA2025-REQ-002 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, tests/requirements/test_2025_tail_backlog_evidence.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-mom-manager-action-routing | implemented-slice | HLA2025-NEW-007, HLA2025-REQ-002 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-mom-manager-query-and-report-routing | implemented-slice | HLA2025-NEW-007, HLA2025-REQ-002 | tests/test_rti1516_2025_spec_and_shim.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-wsdl-legacy-only | legacy-only | HLA2025-RET-003, HLA2025-BND-003, HLA2025-REQ-002 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv, CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto |
| 2025-verification-anchor-matrix | implemented-slice | HLA2025-VER-001, HLA2025-TRACE-001, HLA2025-TRACE-002 | tests/requirements/test_2025_finish_line_snapshot.py, packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py, requirements/2025/requirement_completion_backlog.csv, docs/requirements/ieee-1516-2025/executable_tests/hla_2025_executable_test_requirements_v3.csv |
| 2025-python-rti-milestone-ledger | implemented-slice | HLA2025-MIL-001, HLA2025-MIL-002, HLA2025-MIL-003, HLA2025-MIL-004, HLA2025-MIL-005, HLA2025-MIL-006 | tests/requirements/test_2025_finish_line_snapshot.py, packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py, packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py, requirements/2025/requirement_completion_backlog.csv |

## Highest-Priority Open Work

| ID | Area | Priority | Status | Verification work |
|---|---|---|---|---|

## Finish Rule

Each remaining row needs a positive test, a negative unsupported-boundary test, or an explicit supported-subset/unsupported-boundary row before it can be counted as closed.

Do not promote `partial` rows by broad wording. Narrow the claim or add the missing positive/negative evidence.
