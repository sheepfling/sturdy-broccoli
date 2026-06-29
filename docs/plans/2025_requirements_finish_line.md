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

- Implemented evidence slices: 80
- Route parity partial rows: 0
- Route parity missing rows: 0
- Ready for slice closeout: True
- Ready for full completion claim: False
- Assessment: Executable slice coverage, route parity, FI per-service runtime traceability, and bounded working-RTI milestone evidence are in strong shape for the primary 2025 Python RTI lane, and the repo now has a row-level requirement-by-requirement disposition audit across the full 2025 universe. The remaining retired, umbrella, cross-binding, bounded-extension, and bounded-route limits still block a complete 2025 claim, but those limits now sit outside the already-green primary python1516_2025 runtime lane: hla-backend-python1516-2025 is the repo's main 2025 Python RTI lane, hla-backend-shim remains a wrapper-only legacy compatibility shim, the hosted FedPro route remains a bounded route surface over that runtime rather than a second implementation lane, and any Pitch proto HLA 4 / 202X overlap remains explicit vendor-resolution context rather than inferred grouped closure.

Conformance blockers:

- The repo now has a row-level requirement-by-requirement disposition audit across all 2025 rows, but that audit still contains retired, umbrella, and bounded-scope rows rather than an unconditional conformance pass; this is a requirement-closeout limit rather than evidence that the main python1516_2025 runtime lane is behaviorally incomplete.
- Many implemented-slice rows outside the FI service catalog still aggregate multiple requirements under bounded supported-scope language rather than proving every requirement individually; that remaining gap is about requirement granularity, not about whether hla-backend-python1516-2025 has the underlying executable behavior.
- Java and C++ standard-route evidence remains artifact-gated/runtime-capability evidence, not a full cross-binding behavior-conformance pass.
- The hosted FedPro route is verified as a runtime slice, but its own supported-scope rows explicitly stop short of full RTI semantics and full cross-binding conformance; the remaining route boundary is a hosted/cross-binding proof limit rather than evidence that the direct python1516_2025 runtime lane lacks those semantics.
- Any Pitch proto HLA 4 / 202X overlap remains explicit vendor-resolution context rather than evidence that the grouped 2025 rows have a second independent backend owner.
- OMT component coverage includes foreign xs:any extension payload preservation, but arbitrary third-party extension execution semantics remain out of scope.
- Legacy-only rows remain explicit exclusions, so overall completion cannot be promoted to an unconditional 2025 conformance claim.

## Closeout Blocker Partition Audit

- Audit status: closeout-blocker-partition-captured
- Closeout blocker count: 7
- Partitioned blocker count: 7
- Direct-runtime incompleteness blocker count: 0
- Boundary-only blocker count: 7
- All current closeout blockers external to main python1516_2025 runtime: True
- Assessment: The broader closeout blockers are now explicitly partitioned too. On the current tree they all describe requirement-granularity, cross-binding, hosted-route, OMT-extension-scope, or legacy-exclusion limits rather than missing core executable behavior in the main hla-backend-python1516-2025 runtime lane.
- Residual boundary: This partition audit clarifies why closeout remains incomplete without treating the main python1516_2025 runtime as behaviorally unfinished.

Partitioned blockers:

- row_level_requirement_closeout_limit: requirement-closeout-boundary, counts_against_main_python2025_runtime_completeness=False (row-level disposition still includes retired, umbrella, and bounded-scope rows rather than an unconditional conformance pass)
- implemented_slice_requirement_granularity_gap: requirement-granularity-boundary, counts_against_main_python2025_runtime_completeness=False (many implemented slices still aggregate multiple requirements under bounded supported-scope language)
- standard_java_cpp_cross_binding_gap: external-binding-boundary, counts_against_main_python2025_runtime_completeness=False (Java/C++ standard-route evidence remains artifact-gated/runtime-capability proof rather than full cross-binding behavior conformance)
- hosted_fedpro_cross_binding_gap: external-hosted-boundary, counts_against_main_python2025_runtime_completeness=False (hosted FedPro supported-scope rows stop short of full RTI semantics and full cross-binding conformance)
- pitch_202x_vendor_context_gap: external-vendor-resolution-boundary, counts_against_main_python2025_runtime_completeness=False (Pitch proto HLA 4 / 202X overlap remains explicit vendor-resolution context rather than a second backend owner for grouped 2025 coverage)
- omt_extension_execution_scope_gap: external-omt-boundary, counts_against_main_python2025_runtime_completeness=False (OMT xs:any coverage preserves foreign extension payloads but leaves arbitrary third-party extension execution semantics out of scope)
- legacy_only_explicit_exclusion: legacy-exclusion-boundary, counts_against_main_python2025_runtime_completeness=False (legacy-only rows remain explicit exclusions from an unconditional 2025 completion claim)

## Pytest Anchor Audit

- Anchored requirements: 731
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
- Assessment: All three binding rows now have explicit slice and route-parity proof records, but Java/C++ remain artifact/runtime-capability bounded and FedPro remains a hosted runtime slice rather than full conformance. Those remaining limits are adapter or transport seam evidence boundaries over the main hla-backend-python1516-2025 runtime, not alternate ownership lanes for core 2025 RTI semantics.

Canonical boundary owner reading order:

1. `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`
2. `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md`
3. `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md`
4. `docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`
5. `docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md`

Use the owner docs above for the boundary narrative, and use the linked grouped or row-level backend-resolution ledgers only for the backend split details:

- `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`
- `requirements/2025/harmonization/hla_2025_pitch_202x_group_resolution.csv`
- `requirements/2025/harmonization/hla_2025_pitch_202x_row_resolution.csv`

## OMT Requirement Proof Audit

- OMT rows: 461
- Ready for OMT traceability claim: False
- Ready for full OMT conformance claim: False
- Assessment: All OMT-related rows are now explicit requirement records with supported-subset proof, including bounded foreign xs:any extension tolerance. This closes the traceability gap without pretending extension payloads are preserved as repo-native runtime semantics.

## Callback Proof Audit

- Callback rows: 55
- Helper-backed callbacks: 55
- Focused executable callbacks: 55
- Ready for callback surface traceability claim: True
- Ready for callback-by-callback working-surface claim: True
- Assessment: The repo now has an explicit callback-by-callback ledger through the FederateAmbassador conformance matrix, and all 55 callback rows are helper-backed with focused executable evidence, including reconnect-safe callback backlog cleanup across disconnect/reconnect on the hosted FedPro seam. This closes the callback-ledger gap, but it still does not by itself prove exhaustive cross-binding callback signature/ordering parity or a full callback conformance claim.

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

- Support-service rows: 64
- Focused executable rows: 64
- Rows with known gaps: 0
- Complete negative-path rows: 61
- Partial negative-path rows: 0
- Metadata-mapped negative-path rows: 0
- Ready for support-service traceability claim: True
- Ready for support-service full conformance claim: True
- Assessment: The repo now has an explicit support-service ledger through the RTIambassador conformance matrix, and all 64 support-service rows have focused executable evidence. Negative-path coverage is now complete for all 61 actionable support-service rows, with the remaining row marked not-applicable because it declares no actionable RTI exception surface. Hosted FedPro support-service replay now also proves reconnect-safe discard of a disconnected peer's disabled callback backlog before later reconnect. That leaves the support-service slice requirement-traceable and focused-executable/negative-path complete inside the Python routes. Cross-binding evidence still remains weaker than the Python routes, but it is no longer the blocker for the bounded Python-lane support-service claim.

Support-service verification status counts:

- focused-executable-tests: 64

Support-service negative-path status counts:

- complete: 61
- not-applicable: 3

## Python RTI Milestone Audit

- Audit status: bounded-python-rti-milestones
- Routes: python1516_2025, python1516_2025-fedpro-grpc
- Milestones per route: 6
- Assessment: Both Python 2025 routes now have explicit milestone gates for working-surface breadth, FOM-backed scenario execution, message routing, time sync, GALT/LITS query evidence, and lookahead handling. The time milestones now explicitly include Target/Radar future-exclusion, output-delivery, consumer-order, pipeline, receive-order poison, save/restore window-state, save/restore output resume, save/restore pipeline resume, and time-window proof, paired with negative-oracle rejection guards, but the last four remain bounded-evidence milestones rather than blanket correctness claims.

## Requirement-By-Requirement Audit

- Audit status: row-level-requirement-disposition-audit-captured
- Row count: 691
- Ready for row-level audit claim: True
- Ready for full 2025 conformance claim: False
- Rows with complete review metadata: 691
- Covered rows with evidence paths: 645
- Unsupported rows with explicit boundary flag: 0
- Assessment: The repo now has an explicit row-level requirement-by-requirement disposition audit across all 691 tracked 2025 rows: every row is reviewed, dispositioned, and linked either to repo evidence, an explicit bounded support claim, a retired exclusion, or an umbrella normalization role. That closes the missing-audit gap without turning the result into an unconditional all-covered conformance pass, and it strengthens the bounded main-implementation claim for hla-backend-python1516-2025 while leaving hla-backend-shim in a wrapper-only compatibility role.

Requirement-by-requirement blockers:

- 24 rows are retired/legacy-only exclusions rather than active 2025 support.
- 22 rows remain duplicate/umbrella normalization aids rather than one-row conformance assertions; those rows are split between framework-rule umbrellas and callback/configuration/binding delta umbrellas.
- OMT xs:any extension-point rows are covered as payload-preserving tolerance, not arbitrary third-party extension execution semantics.
- Many covered rows still inherit bounded supported-scope language from slice-level evidence rather than standalone exhaustive clause-by-clause proof.

Requirement-by-requirement duplicate/umbrella breakdown:

- framework-umbrella: 10 rows (HLA2025-FR-001, HLA2025-FR-002, HLA2025-FR-003, HLA2025-FR-004, HLA2025-FR-005, HLA2025-FR-006, HLA2025-FR-007, HLA2025-FR-008, HLA2025-FR-009, HLA2025-FR-010)
- delta-umbrella: 12 rows (HLA2025-BIND-FEDPRO-001, HLA2025-BIND-JAVA-CPP-001, HLA2025-FI-AUTH-001, HLA2025-FI-CB-001, HLA2025-FI-CB-002, HLA2025-FI-CB-003, HLA2025-FI-CB-004, HLA2025-FI-CB-005, HLA2025-FI-CB-006, HLA2025-FI-CB-007, HLA2025-FI-CB-008, HLA2025-FI-CFG-001)

## Duplicate Umbrella Mapping Audit

- Audit status: duplicate-umbrella-mapping-captured
- Row count: 22
- Framework doc path: docs/requirements/ieee-1516-2025/framework_rules.md
- Delta doc path: docs/requirements/ieee-1516-2025/callback_binding_deltas.md
- Framework row count: 10
- Delta row count: 12
- Ready for duplicate umbrella mapping claim: True
- Assessment: The duplicate/umbrella rows are no longer just grouped by role in the closeout bundle. The repo now has explicit proof-note documents for both framework-rule umbrellas and callback/configuration/binding delta umbrellas, and every umbrella row is anchored to, enumerated by, and child-linked from those notes.
- Residual boundary: This audit improves the traceability of umbrella rows, but it does not change their status into standalone one-row conformance claims.

Duplicate umbrella rows by role:

- framework-umbrella: 10 rows (HLA2025-FR-001, HLA2025-FR-002, HLA2025-FR-003, HLA2025-FR-004, HLA2025-FR-005, HLA2025-FR-006, HLA2025-FR-007, HLA2025-FR-008, HLA2025-FR-009, HLA2025-FR-010)
- delta-umbrella: 12 rows (HLA2025-BIND-FEDPRO-001, HLA2025-BIND-JAVA-CPP-001, HLA2025-FI-AUTH-001, HLA2025-FI-CB-001, HLA2025-FI-CB-002, HLA2025-FI-CB-003, HLA2025-FI-CB-004, HLA2025-FI-CB-005, HLA2025-FI-CB-006, HLA2025-FI-CB-007, HLA2025-FI-CB-008, HLA2025-FI-CFG-001)

## Retired Legacy Mapping Audit

- Audit status: retired-legacy-mapping-captured
- Doc path: docs/requirements/ieee-1516-2025/retired_legacy_mapping.md
- Row count: 24
- Doc exists: True
- Rows with doc anchor: 24
- Rows mentioned in doc: 24
- Rows with candidate replacement note: 24
- Ready for retired legacy mapping claim: True
- Assessment: The retired/legacy-only rows are no longer just a count in the closeout bundle. They now have an explicit mapping note that enumerates every retired row and the candidate 2025 replacement surface, which makes the exclusion boundary auditable rather than implied.
- Residual boundary: This audit proves exclusion mapping and documentation quality for retired rows. It does not convert those legacy-only rows into active 2025 support obligations.

Retired rows by service group:

- Federate Interface legacy API: 11 rows (HLA2025-FI-RET-001, HLA2025-FI-RET-002, HLA2025-FI-RET-003, HLA2025-FI-RET-004, HLA2025-FI-RET-005, HLA2025-FI-RET-006, HLA2025-FI-RET-007, HLA2025-FI-RET-008, HLA2025-FI-RET-009, HLA2025-FI-RET-010, HLA2025-FI-RET-011)
- OMT legacy schema: 13 rows (HLA2025-OMT-RET-001, HLA2025-OMT-RET-002, HLA2025-OMT-RET-003, HLA2025-OMT-RET-004, HLA2025-OMT-RET-005, HLA2025-OMT-RET-006, HLA2025-OMT-RET-007, HLA2025-OMT-RET-008, HLA2025-OMT-RET-009, HLA2025-OMT-RET-010, HLA2025-OMT-RET-011, HLA2025-OMT-RET-012, HLA2025-OMT-RET-013)

## OMT xs:any Mapping Audit

- Audit status: omt-xs-any-mapping-captured
- Doc path: docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md
- Row count: 45
- Doc exists: True
- Rows with doc anchor: 45
- Rows mentioned in doc: 45
- Family count: 5
- Family headings ready: True
- Ready for OMT xs:any mapping claim: True
- Assessment: The 45 OMT xs:any rows are no longer just grouped under a bounded decomposition slice. They now have a requirement-facing proof note that enumerates every row by family, a concrete parser round-trip test for foreign namespace payload preservation, and explicit implementation anchors that keep those payloads isolated from repo-native HLA semantics.
- Residual boundary: This audit makes the xs:any bounded claim explicit and fully reviewable, but it does not convert foreign extension payload tolerance into arbitrary third-party extension execution semantics.

OMT xs:any rows by family:

- object-model-root-and-identity: 2 rows (HLA2025-OMT-COMP-006, HLA2025-OMT-COMP-008)
- object-class-and-attribute-extension-points: 16 rows (HLA2025-OMT-COMP-019, HLA2025-OMT-COMP-021, HLA2025-OMT-COMP-027, HLA2025-OMT-COMP-035, HLA2025-OMT-COMP-039, HLA2025-OMT-COMP-045, HLA2025-OMT-COMP-047, HLA2025-OMT-COMP-056, HLA2025-OMT-COMP-057, HLA2025-OMT-COMP-059, HLA2025-OMT-COMP-067, HLA2025-OMT-COMP-068, HLA2025-OMT-COMP-070, HLA2025-OMT-COMP-077, HLA2025-OMT-COMP-081, HLA2025-OMT-COMP-082)
- interaction-class-and-parameter-extension-points: 8 rows (HLA2025-OMT-COMP-102, HLA2025-OMT-COMP-106, HLA2025-OMT-COMP-107, HLA2025-OMT-COMP-113, HLA2025-OMT-COMP-115, HLA2025-OMT-COMP-129, HLA2025-OMT-COMP-130, HLA2025-OMT-COMP-134)
- datatype-and-encoding-extension-points: 12 rows (HLA2025-OMT-COMP-145, HLA2025-OMT-COMP-147, HLA2025-OMT-COMP-154, HLA2025-OMT-COMP-156, HLA2025-OMT-COMP-171, HLA2025-OMT-COMP-176, HLA2025-OMT-COMP-178, HLA2025-OMT-COMP-181, HLA2025-OMT-COMP-189, HLA2025-OMT-COMP-193, HLA2025-OMT-COMP-197, HLA2025-OMT-COMP-198)
- container-table-and-reference-extension-points: 7 rows (HLA2025-OMT-COMP-202, HLA2025-OMT-COMP-204, HLA2025-OMT-COMP-208, HLA2025-OMT-COMP-210, HLA2025-OMT-COMP-219, HLA2025-OMT-COMP-222, HLA2025-OMT-COMP-224)

## Binding Boundary Mapping Audit

- Audit status: binding-boundary-mapping-captured
- Doc path: docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md
- Row count: 3
- Doc exists: True
- Rows with doc anchor: 3
- Rows mentioned in doc: 3
- Boundary narrative ready: True
- Ready for binding boundary mapping claim: True
- Assessment: The binding and hosted boundary rows are no longer only counted as bounded blockers in the closeout reporting bundle. They now have an explicit boundary note that enumerates all three rows and states that hla-backend-python1516-2025 is the main 2025 Python RTI lane while the Java/C++ bindings and hosted FedPro route remain bounded wrapper or transport evidence over that same runtime.
- Residual boundary: This audit makes the binding and hosted boundary mapping explicit and reviewable. It does not promote the Java/C++ rows into exhaustive cross-binding behavior conformance or the hosted FedPro row into a second full RTI implementation lane.

Binding boundary rows by role:

- java-binding: 1 rows (HLA2025-BND-001)
- cpp-binding: 1 rows (HLA2025-BND-002)
- hosted-fedpro: 1 rows (HLA2025-BND-003)

## Python2025 Direct Bounded Proof Audit

- Audit status: python1516_2025-direct-bounded-proof-captured
- Doc path: docs/requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md
- Doc exists: True
- Route: python1516_2025
- Scenario count: 8
- All rows parity-covered: True
- Identity ready: True
- Doc narrative ready: True
- Ready for python1516_2025 direct bounded proof claim: True
- Assessment: The direct python1516_2025 lane is no longer only implied by architecture prose and the main runtime suite. It now has an explicit requirement-facing proof note tied to the eight tracked in-process scenario families, explicit python1516_2025 runtime identity, the paired hosted companion note, and the operator-facing verify-main-2025 versus verify-routes-2025 proof split.
- Residual boundary: This audit makes the direct bounded proof claim explicit and reviewable, but it does not convert the direct lane into a full clause-by-clause 2025 conformance statement or erase the separate hosted, binding, umbrella-row, retired-row, and OMT-extension boundaries.

Direct scenarios: ddm, federation_lifecycle, mom, object_exchange, ownership, save_restore, support_services, time_management

## Python2025 Exclusion Boundaries Audit

- Audit status: python1516_2025-exclusion-boundaries-captured
- Doc path: docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md
- Doc exists: True
- Finish-line source path: packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py
- Direct compat anchor count: 0
- Duplicate/umbrella row count: 22
- Retired row count: 24
- Doc narrative ready: True
- Ready for python1516_2025 exclusion boundaries claim: True
- Assessment: The excluded-area map is no longer only scattered across the backend audit, route-parity notes, and generated finish-line prose. It now has an explicit requirement-facing boundary note that enumerates the legacy-alias, binding, hosted-route, duplicate/umbrella, retired-row, and OMT-extension non-claim areas around the main python1516_2025 implementation statement, and the generated finish-line source no longer carries compat-era direct runtime anchors for the python1516_2025 proof lane.
- Residual boundary: This audit makes the current non-claim map explicit and reviewable, but it does not by itself prove the underlying direct or hosted runtime behavior; it documents the boundaries around those bounded claims.

## Hosted FedPro Bounded Proof Audit

- Audit status: hosted-fedpro-bounded-proof-captured
- Doc path: docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md
- Doc exists: True
- Route: python1516_2025-fedpro-grpc
- Scenario count: 8
- All rows parity-covered: True
- Identity ready: True
- Doc narrative ready: True
- Ready for hosted FedPro bounded proof claim: True
- Assessment: The hosted FedPro route is no longer only implied by route-parity tables and finish-line summaries. It now has a requirement-facing proof note tied to the eight tracked hosted scenario families, explicit python1516_2025 runtime identity, per-scenario transport-plus-parity test anchors, and an auditable statement that the route is a bounded transport/runtime slice over hla-backend-python1516-2025.
- Residual boundary: This audit strengthens the hosted-route proof and identity story, but it does not promote the hosted FedPro lane into full remote-RTI semantics or exhaustive cross-binding conformance.

Hosted scenarios: ddm, federation_lifecycle, mom, object_exchange, ownership, save_restore, support_services, time_management


## Lookahead Window Bounded Proof Audit

- Audit status: lookahead-window-bounded-proof-captured
- Doc path: docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md
- Doc exists: True
- Proof level count: 10
- Route row count: 4
- Route note checks ready: True
- Doc narrative ready: True
- Ready for lookahead window bounded proof claim: True
- Assessment: The Target/Radar lookahead ladder is no longer only embedded in the generic time-management and milestone wording. It now has an explicit requirement-facing proof note tied to the direct-lane and hosted FedPro time-management rows, the save/restore window-resume rows, the named proof ladder, and the narrow Pitch-safe vendor-credence boundary.
- Residual boundary: This audit makes the current lookahead-window claim explicit and reviewable, but it does not convert the bounded ladder into an unconditional clause-by-clause 2025 time-policy conformance pass for every possible topology.

Pitch probe routes: ./tools/pitch time-window-probe, ./tools/pitch time-window-restore-state-probe

## Save/Restore Bounded Proof Audit

- Audit status: save-restore-bounded-proof-captured
- Doc path: docs/requirements/ieee-1516-2025/save_restore_bounded_proof.md
- Doc exists: True
- Proof family count: 5
- Requirement-family count: 5
- Doc narrative ready: True
- Ready for save/restore bounded proof claim: True
- Assessment: The save/restore surface is no longer only captured as one generated decomposition plus family-map pair. It now has an explicit requirement-facing proof note tied to lifecycle control, shared rollback, routing/policy rollback, ownership rollback, and time-window/time-state rollback over the main python1516_2025 runtime lane and hosted replay.
- Residual boundary: This audit makes the current save/restore rollback claim explicit and reviewable, but it does not turn every save/restore requirement into its own standalone clause-by-clause conformance proof.

## Callback Bounded Proof Audit

- Audit status: callback-bounded-proof-captured
- Doc path: docs/requirements/ieee-1516-2025/callback_bounded_proof.md
- Doc exists: True
- Proof family count: 8
- Callback row count: 55
- Hosted/direct route-backed callback count: 55
- Doc narrative ready: True
- Ready for callback bounded proof claim: True
- Assessment: The callback surface is no longer only captured as a callback ledger plus decomposition audit. It now has an explicit requirement-facing proof note tied to the current callback proof families, direct callback anchors, and hosted replay over the main python1516_2025 runtime lane.
- Residual boundary: This audit makes the current callback claim explicit and reviewable, but it does not turn the repo into an exhaustive callback signature/ordering equivalence proof across every binding.

## Standard Binding Runtime-Capability Audit

- Audit status: standard-binding-runtime-capability-captured
- Doc path: docs/requirements/ieee-1516-2025/standard_binding_runtime_capability_bounded_proof.md
- Doc exists: True
- Row count: 32
- Identity ready: True
- Doc narrative ready: True
- Ready for standard binding runtime-capability claim: True
- Assessment: The Java and C++ standard binding lanes are no longer only described as a generic artifact-gated blocker. They now have a requirement-facing bounded-proof note tied to their route families, per-row executable plus artifact anchors, parity-covered scenario counts, and explicit main-runtime identity over hla-backend-python1516-2025.
- Residual boundary: This audit strengthens the Java/C++ binding proof story, but it does not promote standard-route traces into exhaustive cross-binding behavior equivalence or separate RTI implementation ownership.

Standard binding rows by requirement:

- HLA2025-BND-001: routes=java-standard-2025-jpype, java-standard-2025-py4j; parity-covered=16; non-covered=0
- HLA2025-BND-002: routes=cpp-standard-2025-grpc, cpp-standard-2025-pybind; parity-covered=16; non-covered=0

Requirement-by-requirement area closure:

- fi_service_catalog: covered=196
- som_fom_service_usage: covered=196
- omt_component_conformance: covered=224
- omt_validator_negative_conformance: covered=29
- framework_rules: duplicate/umbrella=10
- callback_configuration_binding_deltas: duplicate/umbrella=12
- retired_replacement_mapping_candidates: retired/legacy-only=24

## Completion Claim Audit

- Claim shape: bounded-working-surface-with-explicit-boundaries
- Ready for supported-boundary statement: True
- Ready for full 2025 conformance claim: False
- Assessment: The repo can now make a defensible supported-boundary statement: the claimed working surface is backed by explicit requirement ledgers, the backlog is closed at the tracked 2025 delta level, and legacy-only or bounded-extension areas are named rather than hidden. This is still short of a full 2025 conformance claim.

Requirement universe:

- Total rows: 691
- Covered rows: 645
- Unsupported-boundary rows: 0
- Retired/legacy-only rows: 24
- Duplicate/umbrella rows: 22

Full-claim blockers:

### python1516_2025

- Milestone count: 6
- All milestone parity-covered: True
- Assessment: The route clears the tracked milestone gates as a bounded Python 2025 working surface.

- Best-attempt Python RTI 2025 working surface: bounded-working-slice (In-process Python 2025 is a best-attempt bounded working surface across the tracked runtime scenario set, not a full requirement-by-requirement conformance claim.)
- Tracked example and FOM-backed scenario execution: covered-scenario-slice (The in-process route executes the tracked repo example/FOM-backed scenarios, including object exchange, FOM showcase, and save/restore rollback paths.)
- Message exchange and routing: covered-routing-slice (The in-process route sends, receives, discovers, reflects, directs, and DDM-filters the tracked message flows end to end.)
- Time synchronization and advance flow: covered-time-advance-slice (The in-process route exercises regulation/constrained enablement, time advance, flush queue, timestamped delivery, retraction, restore rollback of logical time, and restore recovery of saved lookahead plus time/switch control state.)
- GALT and LITS behavior: bounded-query-evidence (The in-process route has executable GALT/LITS query evidence inside the logical-time slice and the Target/Radar future-exclusion proof, with the integrated lookahead-processing-window gauntlet exercising the combined closure/output/consumer-order/pipeline ladder on the actual current Python 2025 RTI lane, plus negative-oracle guards rejecting mismatched LITS boundaries, premature output, reversed consumer order, cross-window contamination, and dirty post-restore replay while save/restore evidence still shows that dirty lookahead changes are rolled back and a pre-save queued TSO is redelivered after restore.)
- Lookahead handling and windows: bounded-lookahead-evidence (The in-process route exercises lookahead query/modify behavior, queued timestamped delivery, the integrated Target/Radar lookahead-processing-window gauntlet, and the time-window core, output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, save-restore lookahead rollback with queued-TSO redelivery, save-restore-output-resume, and save-restore-pipeline-resume scenarios together with matching negative-oracle guards.)

### python1516_2025-fedpro-grpc

- Milestone count: 6
- All milestone parity-covered: True
- Assessment: The route clears the tracked milestone gates as a bounded Python 2025 working surface.

- Best-attempt Python RTI 2025 working surface: bounded-working-slice (Hosted FedPro Python 2025 is a best-attempt bounded working surface across the tracked runtime scenario set, with broad hosted replay across lifecycle, object, time, save/restore, support-service, and callback scenarios, not a full RTI semantics or exhaustive cross-binding conformance claim.)
- Tracked example and FOM-backed scenario execution: covered-scenario-slice (The hosted FedPro route now executes the tracked FOM-backed runtime scenarios through the package-owned Proto2025 example/FOM showcase, including MessageTest, SpaceLite, TimeMgmtTest, and Target/Radar, rather than relying only on indirect object, MOM, and save/restore route slices.)
- Message exchange and routing: covered-routing-slice (The hosted FedPro route sends, receives, discovers, reflects, directs, and DDM-filters the tracked message flows over the typed transport surface.)
- Time synchronization and advance flow: covered-time-advance-slice (The hosted FedPro route exercises regulation/constrained enablement, async delivery control, advance/grant flow, queued TSO delivery, retraction, restore rollback of logical time, and restore recovery of saved lookahead plus time/switch control state.)
- GALT and LITS behavior: bounded-query-evidence (The hosted FedPro route has executable GALT/LITS query evidence inside the hosted time-management slice, including queued-TSO GALT/LITS divergence after a live lookahead change, the hosted Target/Radar proof-ladder replay, negative-oracle guards rejecting mismatched LITS boundaries, premature output, reversed consumer order, cross-window contamination, and dirty post-restore replay, restore rollback of dirty lookahead with pre-save queued TSO redelivered after restore, and the Target/Radar future-exclusion proof.)
- Lookahead handling and windows: bounded-lookahead-evidence (The hosted FedPro route exercises lookahead queries together with advance/grant, queued timestamped delivery, the hosted Target/Radar proof-ladder replay, and the Target/Radar output-delivery, consumer-order, pipeline-two-scans, receive-order-poison, future-exclusion, save-restore-window-state, save-restore lookahead rollback with queued-TSO redelivery, save-restore-output-resume, and save-restore-pipeline-resume scenarios together with matching negative-oracle guards.)

- Covered rows include bounded supported-scope evidence, including OMT xs:any extension payload preservation without arbitrary third-party extension execution semantics.
- Java and C++ binding rows remain artifact/runtime-capability evidence rather than exhaustive behavior-conformance proof.
- The hosted FedPro route remains a bounded runtime slice and not a full RTI semantics or exhaustive cross-binding conformance pass.
- Duplicate/umbrella rows remain normalization aids rather than direct one-row conformance assertions.

## Supported Boundary Statement

- Status: supported-boundary-statement
- Ready: True
- Statement: The Python-centered 2025 RTI surface is validated as a bounded working surface across federation management, object management, time management, support services, callbacks, OMT handling, and binding routes and the hosted FedPro route, with explicit legacy-only, bounded-extension, and artifact-gated boundaries recorded in the repo.

Supported scope:

- Python 2025 in-process runtime behavior is executable and parity-covered across the tracked scenario set.
- Hosted FedPro 2025 transport behavior is executable as a bounded runtime slice with explicit route parity coverage, spanning lifecycle, object, time, save/restore, support-service, and callback scenario replay over hla-backend-python1516-2025; its remaining proof burden is transport-seam evidence over hla-backend-python1516-2025 rather than missing core runtime ownership.
- FI service requirements are traced across all 196 catalog rows.
- Common delta rows, binding rows, and OMT-related rows are all represented by explicit requirement ledgers.

Explicit boundaries:

- Foreign OMT xs:any extension payloads are preserved for XML round-trip but not interpreted as repo-native runtime semantics.
- Retired or legacy-only rows remain excluded from the supported 2025 working surface.
- Java and C++ bindings remain artifact/runtime-capability bounded as binding/adaptation-seam proof over the main python1516_2025 runtime rather than full behavior-conformance proof.
- FedPro remains a hosted runtime slice rather than a full RTI semantics or exhaustive cross-binding conformance pass, and its remaining gaps are transport-seam proof gaps rather than evidence that hla-backend-python1516-2025 lacks the underlying semantics.

## Implementation Concentration Audit

- Audit status: implementation-concentration-captured
- Implemented slices: 80
- Runtime backend implementation path: packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py
- Runtime backend-backed slices: 43
- Runtime backend slice share: 0.537
- 2025 spec-package-backed slices: 9
- Transport-backed slices: 11
- Semantic concentration is material: False
- Assessment: The primary 2025 Python RTI lane still cites hla-backend-python1516-2025/backend.py as a frequent evidence anchor, but semantic concentration is no longer material there: the ambassador shell is thin and most runtime behavior now lives in extracted python1516_2025 modules. Remaining pressure is architectural hygiene, not proof that core 2025 semantics still live in one oversized backend class.
- Extraction pressure boundary: The main python1516_2025 runtime should keep absorbing real RTI semantics, while wrapper-only compatibility logic should keep shrinking or moving outward into narrower adapters and reusable runtime modules.

Top evidence anchors:

- 55: tests/transport/test_grpc_transport_2025.py
- 52: tests/test_rti1516_2025_python1516_2025_runtime.py
- 43: packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py
- 15: tests/test_rti1516_2025_validation.py
- 13: packages/hla-rti-core/src/hla/fom/__init__.py
- 7: packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py
- 7: tests/factories/test_fom_omt_parsing.py
- 7: tests/scenarios/test_object_management_backend_matrix.py
- 6: packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py
- 5: packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py

Leading extracted runtime owners:

- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/hosted_fedpro.py: callback-delivery-and-control, 1876 lines
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/runtime_helper_surface_mixin.py: misc-support, 739 lines
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/mom_runtime.py: mom-and-switch-services, 694 lines
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_surface_mixin.py: misc-support, 666 lines
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/interaction_runtime.py: interaction-routing-runtime, 499 lines

## Python 2025 Source Responsibility Audit

- Audit status: python1516_2025-source-responsibility-captured
- Source path: packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py
- Source line count: 488
- Extracted runtime helper modules: 50
- Extracted runtime helper lines: 11766
- Runtime ambassador class: Python2025RTIAmbassador
- Runtime ambassador line count: 18
- Runtime ambassador methods: 0
- Runtime ambassador method lines: 0
- Shim wrapper ambassador class: Shim2025RTIAmbassador
- Shim wrapper ambassador line count: 2
- Responsibility families: 11
- Largest family: misc-support (2354 lines)
- Assessment: The live Python 2025 RTI source now presents a thin ambassador shell in hla-backend-python1516-2025, while the substantive runtime behavior is spread across extracted python1516_2025 modules and hla-backend-shim has been reduced to a legacy compatibility shim. Save/restore lifecycle, directed-interaction routing, time management, declaration/DDM surfaces, ownership, MOM/reporting, federation bootstrap/state handling, catalog access, object lifecycle/update handling, attribute policy/scope, and callback delivery are now measurable as named source-owned families under the main python1516_2025 runtime package.
- Extraction use: Use these families as the source ownership baseline while continuing to shrink hla-backend-shim toward a legacy compatibility shim; new runtime movement should reduce compatibility-surface pressure without weakening direct or hosted route evidence.

Python 2025 source responsibility families:

- misc-support: 33 methods, 2354 lines; sample=create_python2025_backend, require_connected, require_joined, require_no_save_or_restore, normalize_reserved_object_instance_name, normalize_reserved_object_instance_name_set, normalize_object_class_subscription_args, coerce_time
- callback-delivery-and-control: 21 methods, 2162 lines; sample=deliver_forced_remove_callbacks, evaluate_attribute_scope_advisories, _callback_requires_evocation, force_connection_lost, evoke_callback, evoke_multiple_callbacks, enable_callbacks, disable_callbacks
- object-attribute-runtime: 82 methods, 1535 lines; sample=known_object_classes_for_federate, publish_object_class_attributes, unpublish_object_class, unpublish_object_class_attributes, subscribe_object_class_attributes, unsubscribe_object_class, unsubscribe_object_class_attributes, reserve_object_instance_name
- mom-and-switch-services: 39 methods, 1350 lines; sample=mom_request_params_by_name, mom_target_rti, mom_bool, mom_int, mom_attribute_handles, mom_text, mom_number, mom_handle_list_payload
- federation-management-runtime: 48 methods, 1069 lines; sample=extract_federation_name, extract_create_federation_name, extract_join_names, extract_federate_type, extract_logical_time_implementation_name, extract_fom_sources, extract_mim_source, extract_additional_fom_modules
- time-management-runtime: 27 methods, 887 lines; sample=queue_tso_callback, register_retraction_group, resolve_retraction_group, drop_retraction_group_member, finalize_retraction_group_if_inactive, canonicalize_retraction_handles, deliver_due_tso_callbacks, has_attribute_candidate
- interaction-routing-runtime: 23 methods, 628 lines; sample=matching_directed_interaction_targets, parameter_names_from_handles, interaction_class_names_from_handles, interaction_order_for, interaction_transportation_for, coerce_order_type, publish_interaction_class, unpublish_interaction_class
- ownership-runtime: 11 methods, 601 lines; sample=unconditional_attribute_ownership_divestiture, negotiated_attribute_ownership_divestiture, confirm_divestiture, attribute_ownership_acquisition, attribute_ownership_acquisition_if_available, attribute_ownership_release_denied, attribute_ownership_divestiture_if_wanted, cancel_negotiated_attribute_ownership_divestiture
- ddm-region-runtime: 9 methods, 505 lines; sample=ranges_overlap, region_owner_key, regions_overlap_pair, region_sets_overlap, reflectable_attribute_names_for_subscriber, default_transportation_for, attribute_transportation_for, default_order_for
- save-restore-runtime: 13 methods, 462 lines; sample=capture_federation_save_snapshot, restore_federation_save_snapshot, request_federation_save, start_federation_save, process_scheduled_save, federate_save_begun, complete_save, abort_federation_save
- fom-catalog-and-handle-support: 18 methods, 213 lines; sample=normalize_handle, federation_record, catalog, stable_handles, object_class_handles, interaction_class_handles, dimension_handles, dimension_spec

Extracted Python 2025 runtime helper modules:

- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ambassador_core_surface_mixin.py: misc-support, 0 functions, 140 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/attribute_policy.py: object-attribute-runtime, 0 functions, 21 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/attribute_policy_runtime.py: object-attribute-runtime, 1 functions, 39 lines; functions=known_object_classes_for_federate
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/attribute_scope.py: object-attribute-runtime, 0 functions, 10 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/attribute_scope_runtime.py: callback-delivery-and-control, 2 functions, 104 lines; functions=deliver_forced_remove_callbacks, evaluate_attribute_scope_advisories
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend_factory_runtime.py: misc-support, 1 functions, 97 lines; functions=create_python2025_backend
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/callback_runtime.py: callback-delivery-and-control, 15 functions, 182 lines; functions=_callback_requires_evocation, force_connection_lost, evoke_callback, evoke_multiple_callbacks, enable_callbacks, disable_callbacks, enable_asynchronous_delivery, disable_asynchronous_delivery, deliver_callback, deliver_callback_now, deliver_to_federate_handle, deliver_to_federate_handle_now, apply_object_callback_state, deliver_queued_callback, deliver_mom_service_report
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/catalog_access_runtime.py: fom-catalog-and-handle-support, 10 functions, 101 lines; functions=normalize_handle, federation_record, catalog, stable_handles, object_class_handles, interaction_class_handles, dimension_handles, dimension_spec, dimension_default_upper_bound, transportation_handles
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/catalog_runtime.py: fom-catalog-and-handle-support, 8 functions, 112 lines; functions=attribute_handles, parameter_handles, object_class_name, interaction_class_name, transportation_handle_by_name, object_instance_record, object_instance_record_known, synchronization_required_federates
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ddm_default_attribute_policy.py: ddm-region-runtime, 9 functions, 155 lines; functions=ranges_overlap, region_owner_key, regions_overlap_pair, region_sets_overlap, reflectable_attribute_names_for_subscriber, default_transportation_for, attribute_transportation_for, default_order_for, attribute_order_for
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/declaration_ddm_surface_mixin.py: ddm-region-runtime, 0 functions, 350 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/declaration_management.py: object-attribute-runtime, 0 functions, 29 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/declaration_management_runtime.py: object-attribute-runtime, 10 functions, 245 lines; functions=publish_object_class_attributes, unpublish_object_class, unpublish_object_class_attributes, subscribe_object_class_attributes, unsubscribe_object_class, unsubscribe_object_class_attributes, reserve_object_instance_name, release_object_instance_name, reserve_multiple_object_instance_names, release_multiple_object_instance_names
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/delivery_state_runtime.py: time-management-runtime, 11 functions, 177 lines; functions=queue_tso_callback, register_retraction_group, resolve_retraction_group, drop_retraction_group_member, finalize_retraction_group_if_inactive, canonicalize_retraction_handles, deliver_due_tso_callbacks, has_attribute_candidate, add_attribute_candidate, remove_attribute_candidate, pop_attribute_candidate
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/directed_interaction_boundary.py: interaction-routing-runtime, 1 functions, 41 lines; functions=matching_directed_interaction_targets
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_bootstrap_runtime.py: federation-management-runtime, 16 functions, 262 lines; functions=extract_federation_name, extract_create_federation_name, extract_join_names, extract_federate_type, extract_logical_time_implementation_name, extract_fom_sources, extract_mim_source, extract_additional_fom_modules, normalize_module_sources, coerce_callback_model, validate_credentials, resolve_fom_modules, merge_fom_modules, standard_mim_module, get_time_factory, select_logical_time_implementation
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_management.py: federation-management-runtime, 0 functions, 33 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_management_runtime.py: federation-management-runtime, 12 functions, 388 lines; functions=connect, disconnect, force_federate_loss, create_federation_execution, create_federation_execution_with_mim, destroy_federation_execution, list_federation_executions, list_federation_execution_members, join_federation_execution, resign_federation_execution, register_federation_synchronization_point, synchronization_point_achieved
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_state_runtime.py: federation-management-runtime, 20 functions, 386 lines; functions=release_join, prune_tso_state_for_departing_federate, apply_resign_action, cancel_resigning_federate_pending_acquisitions, resigning_federate_has_pending_acquisitions, resigning_federate_owns_attributes, delete_objects_owned_by_resigning_federate, delete_objects_owned_by_specific_federate, divest_resigning_federate_attributes, divest_attributes_owned_by_specific_federate, is_mom_object_class_name, mom_runtime_federate_handle, ensure_mom_objects, ensure_mom_federation_object, ensure_mom_federate_object, register_internal_object_instance, refresh_mom_federation_object, refresh_mom_federate_object, remove_current_federate_mom_object, backend_drop_retraction_group_member
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_time_surface_mixin.py: time-management-runtime, 0 functions, 424 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/hosted_fedpro.py: callback-delivery-and-control, 4 functions, 1876 lines; functions=resolve_fedpro_fom_path, _decode_logical_time, _invoke_federate_callback, dispatch_fedpro_helper_callback
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/input_guard_runtime.py: misc-support, 8 functions, 114 lines; functions=require_connected, require_joined, require_no_save_or_restore, normalize_reserved_object_instance_name, normalize_reserved_object_instance_name_set, normalize_object_class_subscription_args, coerce_time, coerce_interval
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/interaction_policy.py: misc-support, 0 functions, 19 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/interaction_policy_runtime.py: interaction-routing-runtime, 5 functions, 88 lines; functions=parameter_names_from_handles, interaction_class_names_from_handles, interaction_order_for, interaction_transportation_for, coerce_order_type
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/interaction_runtime.py: interaction-routing-runtime, 17 functions, 499 lines; functions=publish_interaction_class, unpublish_interaction_class, subscribe_interaction_class, unsubscribe_interaction_class, subscribe_interaction_class_with_regions, unsubscribe_interaction_class_with_regions, publish_object_class_directed_interactions, unpublish_object_class_directed_interactions, subscribe_object_class_directed_interactions, unsubscribe_object_class_directed_interactions, change_interaction_order_type, send_interaction, send_interaction_with_regions, send_directed_interaction, request_interaction_transportation_type_change, query_interaction_transportation_type, _parameter_value_map
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/mom_codec.py: mom-and-switch-services, 14 functions, 191 lines; functions=mom_request_params_by_name, mom_target_rti, mom_bool, mom_int, mom_attribute_handles, mom_text, mom_number, mom_handle_list_payload, mom_ownership_state, mom_order_type, mom_resign_action, mom_index, mom_module_data, mom_single_module_data
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/mom_runtime.py: mom-and-switch-services, 16 functions, 694 lines; functions=handle_mom_interaction, handle_mom_federate_request_interaction, send_mom_publication_reports, send_mom_subscription_reports, send_mom_object_instance_information_report, send_mom_object_class_count_report, send_mom_transport_count_report, mom_deletable_object_counts, mom_counts_for_federate, mom_transport_counts_for_federate, handle_mom_service_interaction, handle_mom_adjust_interaction, modify_mom_attribute_state, mom_request_report_values, send_mom_report_interaction, send_mom_exception_interaction
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/mom_surface_mixin.py: mom-and-switch-services, 0 functions, 330 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_instance_runtime.py: object-attribute-runtime, 8 functions, 373 lines; functions=register_object_instance, update_attribute_values, delete_object_instance, local_delete_object_instance, request_attribute_value_update, request_instance_attribute_value_update, deliver_value_update_requests, set_internal_object_attribute_values
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_model.py: object-attribute-runtime, 0 functions, 25 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_model_runtime.py: object-attribute-runtime, 8 functions, 148 lines; functions=matching_object_publishers, has_object_registration_interest, subscribed_discovery_class_name, object_class_lineage, attribute_name_by_handle, attribute_names_from_handles, published_attributes_for_current_federate, discover_existing_objects_for_current_subscription
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_ownership_surface_mixin.py: ownership-runtime, 0 functions, 308 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_reflection.py: object-attribute-runtime, 0 functions, 10 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_reflection_runtime.py: misc-support, 2 functions, 155 lines; functions=group_source_values_by_transport, fanout_attribute_update
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/object_region_runtime.py: object-attribute-runtime, 20 functions, 317 lines; functions=create_region, commit_region_modifications, delete_region, get_dimension_handle_set, get_range_bounds, set_range_bounds, region_values_from_handles, coerce_range_bounds, attribute_region_pairs, object_instance_region_values, subscribe_object_class_attributes_with_regions, unsubscribe_object_class_attributes_with_regions, register_object_instance_with_regions, associate_regions_for_updates, unassociate_regions_for_updates, change_default_attribute_transportation_type, change_default_attribute_order_type, change_attribute_order_type, request_attribute_transportation_type_change, query_attribute_transportation_type
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ownership_runtime.py: ownership-runtime, 11 functions, 293 lines; functions=unconditional_attribute_ownership_divestiture, negotiated_attribute_ownership_divestiture, confirm_divestiture, attribute_ownership_acquisition, attribute_ownership_acquisition_if_available, attribute_ownership_release_denied, attribute_ownership_divestiture_if_wanted, cancel_negotiated_attribute_ownership_divestiture, cancel_attribute_ownership_acquisition, query_attribute_ownership, is_attribute_owned_by_federate
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/runtime_helper_surface_mixin.py: misc-support, 0 functions, 739 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/runtime_state.py: misc-support, 0 functions, 122 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/save_restore.py: save-restore-runtime, 0 functions, 35 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/save_restore_lifecycle.py: save-restore-runtime, 13 functions, 427 lines; functions=capture_federation_save_snapshot, restore_federation_save_snapshot, request_federation_save, start_federation_save, process_scheduled_save, federate_save_begun, complete_save, abort_federation_save, query_federation_save_status, request_federation_restore, complete_restore, abort_federation_restore, query_federation_restore_status
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_lookup.py: misc-support, 0 functions, 53 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_lookup_runtime.py: misc-support, 22 functions, 249 lines; functions=get_object_class_handle, get_object_class_name, get_attribute_handle, get_attribute_name, get_interaction_class_handle, get_interaction_class_name, get_parameter_handle, get_parameter_name, get_transportation_type_handle, get_transportation_type_name, get_dimension_handle, get_dimension_name, get_dimension_upper_bound, get_available_dimensions_for_object_class, get_available_dimensions_for_interaction_class, get_federate_handle, get_federate_name, get_known_object_class_handle, get_object_instance_handle, get_object_instance_name, get_order_type, get_order_name
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_policy.py: mom-and-switch-services, 0 functions, 27 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_policy_runtime.py: mom-and-switch-services, 9 functions, 108 lines; functions=serialize_mom_service_report, service_report_records_snapshot, normalize_service_group, get_switch, set_switch, set_attribute_scope_advisory_switch, get_automatic_resign_directive, set_automatic_resign_directive, safe_report_arg
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py: object-attribute-runtime, 28 functions, 150 lines; functions=make_attribute_handle_factory, make_attribute_handle_set_factory, make_attribute_handle_value_map_factory, make_attribute_set_region_set_pair_list_factory, make_dimension_handle_factory, make_dimension_handle_set_factory, make_federate_handle_factory, make_federate_handle_set_factory, make_interaction_class_handle_factory, make_interaction_class_handle_set_factory, make_object_class_handle_factory, make_object_instance_handle_factory, make_parameter_handle_factory, make_parameter_handle_value_map_factory, make_region_handle_factory, make_region_handle_set_factory, make_message_retraction_handle_factory, make_transportation_type_handle_factory, decode_handle, decode_federate_handle, decode_object_class_handle, decode_interaction_class_handle, decode_object_instance_handle, decode_attribute_handle, decode_parameter_handle, decode_dimension_handle, decode_message_retraction_handle, decode_region_handle
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_surface_mixin.py: misc-support, 0 functions, 666 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/time_management.py: time-management-runtime, 0 functions, 41 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/time_management_runtime.py: time-management-runtime, 16 functions, 245 lines; functions=build_time_management_state, build_time_management_federation, query_galt_for, query_lits_for, validate_tso_send_time, enable_time_regulation, disable_time_regulation, enable_time_constrained, disable_time_constrained, modify_lookahead, query_lookahead, retract_message, request_time_advance, process_time_advances, try_grant_pending_time_advance, deliver_due_tso_callbacks_for_request
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/update_rate.py: object-attribute-runtime, 0 functions, 23 lines; functions=
- packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/update_rate_runtime.py: object-attribute-runtime, 7 functions, 145 lines; functions=get_update_rate_value, resolve_update_rate_designator, default_update_rate_for_attribute, default_update_rate_designator_for_attribute, subscribed_update_rate_for_attribute, time_scalar, apply_update_rate_reduction_for_subscriber

## Slice Aggregation Pressure Audit

- Audit status: slice-aggregation-pressure-captured
- Implemented slices: 78
- Aggregated slices >=10 requirements: 10
- Aggregated slices >=10 requirements and runtime-backed: 3
- Aggregated slices >=20 requirements: 7
- Aggregated slices >=20 requirements and runtime-backed: 2
- Assessment: Most implemented 2025 slices are not huge aggregations, but a small set of large slices still carry a lot of requirement mass. The runtime-heavy DDM/default-policy, save/restore, and directed-interaction slices now have explicit requirement-family maps, so the remaining pressure is no longer about unnamed large bundles; it is about whether the repo wants leaf-level implemented slices rather than larger family-mapped aggregates.
- Next decomposition boundary: If deeper proof is needed, start by splitting the largest runtime-heavy slices into narrower service- or behavior-family audits inside the main python1516_2025 backend lane.

Largest implemented slices:

- 2025-service-utilization-crosscheck: 200 requirements (runtime-backed: False)
- 2025-omt-extended-supported-subset: 110 requirements (runtime-backed: False)
- 2025-omt-xs-any-extension-tolerance: 45 requirements (runtime-backed: False)
- 2025-omt-schema-constraint-validation: 29 requirements (runtime-backed: False)
- 2025-omt-component-metadata-roundtrip: 24 requirements (runtime-backed: False)
- 2025-ddm-default-attribute-policy: 23 requirements (runtime-backed: True)
- 2025-save-restore-lifecycle: 20 requirements (runtime-backed: True)
- 2025-omt-switch-and-transport-subset: 19 requirements (runtime-backed: False)
- 2025-standard-route-runtime-capability: 18 requirements (runtime-backed: False)
- 2025-directed-interaction-boundary: 11 requirements (runtime-backed: True)

Largest runtime-backed aggregated slices:

- 2025-ddm-default-attribute-policy: 23 requirements
- 2025-save-restore-lifecycle: 20 requirements
- 2025-directed-interaction-boundary: 11 requirements

## Service Utilization Decomposition Audit

- Audit status: service-utilization-decomposition-captured
- Slice id: 2025-service-utilization-crosscheck
- Requirement count: 196
- Family count: 11
- All service-utilization rows family-mapped: True
- All backing FI rows traceable: True
- Assessment: The 196-row service-utilization slice is no longer only one broad OMT parser claim. It is decomposed by the same Federate Interface service families used by the runtime proof audit, so each OMT service usage row has a corresponding FI service row, service number, family, and supporting runtime slice.
- Residual boundary: This proves service-utilization table extraction and alignment with runtime-backed FI service families; it does not turn optional SOM/FOM service-usage declarations into independent execution of every service.

Service-utilization families:

- callback_control: 4 services (193..196), traceable=True
- ddm: 12 services (126..137), traceable=True
- declaration_management: 12 services (35..46), traceable=True
- federation_management: 17 services (1..17), traceable=True
- name_reservation: 6 services (51..56), traceable=True
- object_class_relevance: 4 services (47..50), traceable=True
- object_management: 26 services (57..82), traceable=True
- ownership_management: 18 services (83..100), traceable=True
- save_restore: 17 services (18..34), traceable=True
- support_services: 55 services (138..192), traceable=True
- time_management: 25 services (101..125), traceable=True

## OMT Extended Subset Decomposition Audit

- Audit status: omt-extended-subset-decomposition-captured
- Slice id: 2025-omt-extended-supported-subset
- Requirement count: 110
- Family count: 5
- All extended-subset rows family-mapped: True
- Unmapped requirement ids: 0
- Unexpected requirement ids: 0
- Assessment: The 110-row OMT extended supported-subset slice is now decomposed into model identity, object/attribute metadata, interaction/parameter metadata, datatype tables, and container/table-section families. That makes the broad parser/serializer claim auditable by OMT structure instead of leaving one opaque requirement bundle.
- Residual boundary: This is still OMT metadata parse/serialize preservation evidence for the supported subset; it does not claim execution of arbitrary OMT extension semantics or every possible semantic interpretation of preserved table fields.

OMT extended-subset families:

- model-identification-and-taxonomy: 8 requirements (1..83), in-slice=True
- object-attribute-and-class-metadata: 33 requirements (16..73), in-slice=True
- interaction-parameter-and-routing-metadata: 36 requirements (86..139), in-slice=True
- datatype-table-roundtrip: 18 requirements (148..188), in-slice=True
- container-reference-and-table-sections: 15 requirements (199..223), in-slice=True

## OMT xs:any Extension Decomposition Audit

- Audit status: omt-xs-any-extension-decomposition-captured
- Slice id: 2025-omt-xs-any-extension-tolerance
- Requirement count: 45
- Family count: 5
- All xs:any extension rows family-mapped: True
- Unmapped requirement ids: 0
- Unexpected requirement ids: 0
- Assessment: The 45-row OMT xs:any extension slice is now decomposed by the parent OMT structures where foreign extensions may appear. This preserves the stronger payload-preservation claim while keeping the extension boundary explicit and auditable.
- Residual boundary: The parser preserves and reserializes foreign XML payloads at these extension points and isolates them from native HLA elements; it still does not execute arbitrary third-party extension semantics.

OMT xs:any extension families:

- object-model-root-and-identity: 2 requirements (6..8), in-slice=True
- object-class-and-attribute-extension-points: 16 requirements (19..82), in-slice=True
- interaction-class-and-parameter-extension-points: 8 requirements (102..134), in-slice=True
- datatype-and-encoding-extension-points: 12 requirements (145..198), in-slice=True
- container-table-and-reference-extension-points: 7 requirements (202..224), in-slice=True

## OMT Schema Constraint Decomposition Audit

- Audit status: omt-schema-constraint-decomposition-captured
- Slice id: 2025-omt-schema-constraint-validation
- Requirement count: 29
- Family count: 4
- All schema-constraint rows family-mapped: True
- Unmapped requirement ids: 0
- Unexpected requirement ids: 0
- Assessment: The 29-row OMT validator-negative slice is now decomposed into key, keyref, unique, and enumeration/domain validation families. That makes the schema-validation proof auditable as negative validator coverage rather than one broad XSD-backed claim.
- Residual boundary: This proves the supported Python validation path reports the imported 2025 schema and value-domain negative cases; it does not claim exhaustive third-party schema-validator certification beyond the bundled IEEE1516-OMT-2025 subset fixture coverage.

OMT schema-constraint families:

- xsd-key-constraints: 5 requirements (1..9), in-slice=True
- xsd-keyref-constraints: 5 requirements (2..10), in-slice=True
- xsd-unique-constraints: 4 requirements (11..14), in-slice=True
- enumeration-and-union-domain-constraints: 15 requirements (15..29), in-slice=True

## Save/Restore Decomposition Audit

- Audit status: save-restore-decomposition-captured
- Slice id: 2025-save-restore-lifecycle
- Requirement count: 20
- Proof families: 5
- Direct-backed families: 5
- FedPro-hosted-backed families: 5
- REST-hosted-backed families: 1
- Assessment: The save/restore slice is no longer just one broad working-surface claim. Its current evidence already separates into lifecycle control, shared rollback scenarios, routing/policy rollback, ownership rollback, and time-window/time-state rollback. FedPro-hosted replay backs every named family, while the REST-hosted Python route currently extends the lifecycle-control family only; the broader rollback families remain direct-lane plus FedPro-hosted proof. Restore-failure/abort control flow and transport/order policy persistence stay explicit inside that split.
- Next split boundary: If this slice needs further tightening, split it first by these proof families and by explicit FedPro-versus-REST hosted route resolution before further modularizing save/restore runtime semantics inside hla-backend-python1516-2025.

### save-restore/lifecycle-control

- Focus: save/restore request, initiate, completion, failure, abort, and precondition control flow
- Direct test count: 14
- FedPro hosted test count: 9
- REST hosted test count: 1

### save-restore/shared-scenario-rollback

- Focus: shared two-federate save/restore, object-state rollback, and federate-local rollback
- Direct test count: 4
- FedPro hosted test count: 4
- REST hosted test count: 0

### save-restore/routing-policy-rollback

- Focus: callback policy, transport/order policy, object routing, interaction routing, directed routing, and stale queued callback cleanup
- Direct test count: 7
- FedPro hosted test count: 7
- REST hosted test count: 0

### save-restore/ownership-rollback

- Focus: ownership gauntlets, inflight acquisition/divestiture state, and owner-visibility rollback
- Direct test count: 4
- FedPro hosted test count: 4
- REST hosted test count: 0

### save-restore/time-window-and-time-state-rollback

- Focus: lookahead, queued TSO, time/switch state, open/closed window state, output resume, and pipeline resume
- Direct test count: 5
- FedPro hosted test count: 5
- REST hosted test count: 0


## Save/Restore Requirement-Family Audit

- Audit status: save-restore-requirement-family-map-captured
- Slice id: 2025-save-restore-lifecycle
- Requirement count: 20
- Family count: 5
- All save/restore rows family-mapped: True
- Unmapped requirement ids: 0
- Unexpected requirement ids: 0
- Assessment: The large save/restore aggregate is now backed by an explicit requirement-family map instead of only one flat slice-level claim. That makes the lifecycle-control, shared rollback, routing rollback, and ownership/time rollback boundaries auditable requirement-by-requirement.
- Residual boundary: This is still a requirement-family map over one larger save/restore runtime slice, not a promise that every save/restore requirement now has its own standalone implemented-evidence slice.

Save/restore requirement families:

- lifecycle-control: 13 requirements, in-slice=True
- shared-scenario-rollback: 1 requirements, in-slice=True
- routing-policy-rollback: 4 requirements, in-slice=True
- ownership-rollback: 1 requirements, in-slice=True
- time-window-and-time-state-rollback: 1 requirements, in-slice=True

## Federation-Management Decomposition Audit

- Audit status: federation-management-decomposition-captured
- Slice id: 2025-federation-management-proof-families
- Slice ids: 2025-lifecycle-and-members, 2025-connection-lifecycle-services, 2025-connect-and-federation-catalog-services, 2025-federate-membership-and-resign-services, 2025-synchronization-point-services, 2025-save-restore-lifecycle
- Requirement count: 40
- Proof families: 6
- Direct-backed families: 6
- FedPro-hosted-backed families: 6
- REST-hosted-backed families: 0
- Assessment: Federation-management proof is no longer just one broad strong-slice claim. Its current evidence separates into connect/create/catalog control, join or membership reporting, resign or disconnect cleanup, synchronization barriers, save/restore lifecycle control, and save/restore participant recovery families. FedPro-hosted replay backs every named family, while the REST-hosted Python route is not currently promoted to these broader federation-management proof families; its checked-in 2025 evidence stays in the narrower execution-membership slice for lifecycle-negative, join-precondition, and resign-precondition control. That narrower seam is owned explicitly by HLA2025-FI-SVC-005, HLA2025-FI-SVC-008, HLA2025-FI-SVC-010, and HLA2025-FI-SVC-011 rather than only by a broad family label.
- Next split boundary: If this area needs further tightening, split it first by these federation-management proof families and by the narrower execution-membership-versus-broader-family REST boundary before attempting clause-by-clause completion claims across connect, join, resign, sync, and save/restore services.

### federation-management/connect-create-destroy-and-catalog-control

- Focus: connect or disconnect state, create or destroy federation control, federation listing, duplicate-create rejection, and FOM-validation or callback-model connect preconditions
- Direct test count: 7
- FedPro hosted test count: 6
- REST hosted test count: 0

### federation-management/join-membership-and-name-preconditions

- Focus: join preconditions, federation-execution member reporting, multi-participation visibility, and federate-name uniqueness or joined-state constraints
- Direct test count: 4
- FedPro hosted test count: 4
- REST hosted test count: 0

### federation-management/resign-disconnect-loss-and-member-cleanup

- Focus: resign and disconnect preconditions, federation member cleanup after resign or loss, connectionLost teardown, and federateResigned callback or MOM cleanup behavior
- Direct test count: 7
- FedPro hosted test count: 7
- REST hosted test count: 0

### federation-management/synchronization-barriers-and-targeted-callbacks

- Focus: sync-point registration, announce or achieved flow, federationSynchronized completion, failure cases, late joiners, multiple sync points, and targeted sync callback routing
- Direct test count: 6
- FedPro hosted test count: 7
- REST hosted test count: 0

### federation-management/save-restore-lifecycle-control

- Focus: request or initiate, status, fail, abort, and completion control flow for federation save or restore across the direct lane and hosted FedPro replay
- Direct test count: 5
- FedPro hosted test count: 7
- REST hosted test count: 0

### federation-management/save-restore-participant-recovery-and-branching

- Focus: multi-federate participant tracking, restore after disconnect, example FOM rollback branching, and recovery of saved participant state rather than dirty future state
- Direct test count: 2
- FedPro hosted test count: 5
- REST hosted test count: 0


## Callback Decomposition Audit

- Audit status: callback-decomposition-captured
- Slice id: 2025-callback-proof-families
- Slice ids: 2025-callback-context-object-delivery, 2025-callback-context-interaction-delivery, 2025-connection-lifecycle-services, 2025-connect-and-federation-catalog-services, 2025-federate-membership-and-resign-services, 2025-synchronization-point-services, 2025-object-delete-remove-flows, 2025-object-attribute-update-request-callbacks, 2025-object-scope-advisory-callbacks, 2025-object-update-rate-advisory-callbacks, 2025-object-attribute-transport-callbacks, 2025-object-interaction-transport-callbacks, 2025-single-name-reservation-services, 2025-multi-name-reservation-services, 2025-save-restore-lifecycle, 2025-fedpro-hosted-runtime-core, 2025-fedpro-hosted-runtime-extended-state
- Requirement count: 66
- Proof families: 8
- Direct-backed families: 8
- Hosted-backed families: 8
- Assessment: Callback proof is no longer just a flat ledger plus one route-backed count. Its current evidence separates into declaration advisories, federation sync/save-restore/reporting, object delivery, advisory or name-reservation callbacks, supplemental callback context, ownership callbacks, time or retraction callbacks, and callback-control hygiene families, with direct-lane and hosted FedPro replay anchors across every family.
- Next split boundary: If this area needs further tightening, split it first by these callback proof families before attempting callback-by-callback signature or ordering claims beyond the current Python lanes.

### callbacks/declaration-relevance-and-interest-advisories

- Focus: start or stop registration plus turnInteractionsOn/off callback delivery across declaration and time-managed declaration flows
- Direct test count: 3
- Hosted test count: 2

### callbacks/federation-sync-save-restore-and-reporting

- Focus: synchronization registration and announce flow, federationSynchronized completion, save/restore lifecycle callbacks, connectionLost teardown, and federation execution reporting
- Direct test count: 5
- Hosted test count: 5

### callbacks/object-discovery-delivery-and-removal

- Focus: discoverObjectInstance, reflectAttributeValues, receiveInteraction, provideAttributeValueUpdate, and removeObjectInstance delivery across plain, timed, restore, and requester-only routing paths
- Direct test count: 3
- Hosted test count: 4

### callbacks/object-advisory-transport-and-name-reservation-callbacks

- Focus: scope advisories, update-rate advisories, transport change/query callbacks, and single or multiple object-instance name reservation callback flows
- Direct test count: 4
- Hosted test count: 4

### callbacks/supplemental-context-and-region-introspection

- Focus: callback-context preservation for producing-federate and sent-region metadata on the direct lane and hosted FedPro callback delivery surfaces
- Direct test count: 1
- Hosted test count: 2

### callbacks/ownership-negotiation-and-query-callbacks

- Focus: ownership assumption, release, divestiture confirmation, acquisition notification, unavailable/query callbacks, and restore recovery of inflight ownership state
- Direct test count: 3
- Hosted test count: 3

### callbacks/time-grant-regulation-and-retraction

- Focus: time regulation/time constrained enable callbacks, timeAdvanceGrant progression, and requestRetraction delivery across the direct lane and hosted FedPro time-window or queued-TSO flows
- Direct test count: 3
- Hosted test count: 4

### callbacks/callback-control-and-backlog-hygiene

- Focus: disableCallbacks or enableCallbacks queue control, evokeCallback ordering, and reconnect-safe stale-backlog cleanup on the hosted seam
- Direct test count: 2
- Hosted test count: 4


## Time-Management Decomposition Audit

- Audit status: time-management-decomposition-captured
- Slice id: 2025-time-management-proof-families
- Slice ids: 2025-time-mode-enable-disable, 2025-time-advance-request-modes, 2025-time-grant-and-async-delivery, 2025-time-query-and-lookahead-control, 2025-time-queries-retraction-and-order, 2025-lookahead-window-proofs, 2025-save-restore-lifecycle
- Requirement count: 50
- Proof families: 5
- Direct-backed families: 5
- Hosted-backed families: 5
- Assessment: Time-management proof is no longer just one bounded query/window bucket. Its current evidence separates into factory/mode/request primitives, GALT/LITS and lookahead observability, timestamped delivery and retraction ordering, the Target/Radar lookahead-window proof ladder, and save/restore rollback of time, lookahead, and window state, with direct-lane and hosted FedPro replay anchors across every family.
- Next split boundary: If this area needs further tightening, split it first by these time-management proof families before attempting per-service completion claims across regulation, advance requests, timestamped delivery, queries, and save/restore time-state semantics.

### time-management/factory-mode-enable-and-request-primitives

- Focus: logical-time factory selection, regulation/constrained enablement, advance-request modes, MOM time-management control routing, and typed flush-queue request handling
- Direct test count: 6
- Hosted test count: 4

### time-management/galt-lits-query-and-lookahead-observability

- Focus: queryLogicalTime, queryGALT, queryLITS, queryLookahead, modifyLookahead, and visible divergence or convergence of GALT/LITS under queued traffic and live lookahead changes
- Direct test count: 4
- Hosted test count: 4

### time-management/timestamped-delivery-retraction-and-ordering

- Focus: queued timestamped delivery, requestRetraction fanout or suppression, lagging-subscriber behavior, and receive-order versus timestamp-order handling across the direct lane and hosted FedPro route
- Direct test count: 7
- Hosted test count: 4

### time-management/lookahead-window-proof-ladder

- Focus: Target/Radar safe-window closure, future-message exclusion, output delivery, consumer ordering, pipeline overlap, receive-order poison rejection, and the integrated lookahead-processing-window gauntlet
- Direct test count: 7
- Hosted test count: 7

### time-management/save-restore-time-state-and-lookahead-rollback

- Focus: saved logical-time, lookahead, switch-control, queued-TSO, and open or closed window state rollback, including restore resumption without dirty post-save replay
- Direct test count: 6
- Hosted test count: 6


## Binding-Route Decomposition Audit

- Audit status: binding-route-decomposition-captured
- Slice id: 2025-binding-route-proof-families
- Slice ids: 2025-java-binding-source-trace, 2025-cpp-binding-source-trace, 2025-standard-route-runtime-capability, 2025-fedpro-typed-transport-surface, 2025-fedpro-hosted-runtime-core, 2025-fedpro-hosted-runtime-extended-state
- Requirement count: 24
- Proof families: 6
- Route-group coverage count: 16
- Assessment: Binding and hosted-route proof is no longer just one bounded route bucket. Its current evidence now separates into named binding and hosted-route families: Java intake/source traces, C++ intake/source traces, artifact-gated standard runtime-capability traces, the typed FedPro schema surface, the hosted FedPro runtime slices, and the cross-route scenario parity ledger, while keeping the distinction between bounded adapter evidence and the main python1516_2025 runtime owner explicit.
- Next split boundary: If this area needs further tightening, split it first by these route families before attempting any stronger behavior-equivalence or hosted-conformance claim.

### binding-routes/java-binding-source-and-intake-evidence

- Focus: Java package inventory, source trace, intake manifests, and the distinction between Java wrapper surfaces and the main python1516_2025 runtime owner
- Evidence test count: 2
- Route groups: java-standard-2025-jpype, java-standard-2025-py4j

### binding-routes/cpp-binding-source-and-intake-evidence

- Focus: C++ namespace/source trace, intake evidence, and wrapper-surface separation from the main python1516_2025 runtime lane
- Evidence test count: 2
- Route groups: cpp-standard-2025-pybind, cpp-standard-2025-grpc

### binding-routes/standard-java-cpp-runtime-capability-traces

- Focus: artifact-gated standard-route lifecycle, object, ownership, time, MOM, DDM, support-service, and save/restore capability traces executed over the primary python1516_2025 runtime lane
- Evidence test count: 3
- Route groups: java-standard-2025-jpype, java-standard-2025-py4j, cpp-standard-2025-pybind, cpp-standard-2025-grpc

### binding-routes/fedpro-typed-transport-and-schema-surface

- Focus: typed RTI request oneofs, typed callback oneofs, schema-tagged client selection, federation-list plus create-with-MIM transport commands, and executable FedPro transport-schema proof
- Evidence test count: 3
- Route groups: python1516_2025-fedpro-grpc

### binding-routes/fedpro-hosted-runtime-core-and-extended-state

- Focus: hosted 2025 runtime lifecycle, object, ownership, time, save/restore, callback, MOM, support-service, and example-FOM replay over create_rti_ambassador('python1516_2025', transport=...)
- Evidence test count: 3
- Route groups: python1516_2025-fedpro-grpc

### binding-routes/cross-route-scenario-parity-ledger

- Focus: the explicit parity ledger across federation_lifecycle, object_exchange, ownership, ddm, time_management, save_restore, mom, and support_services for all current 2025 routes
- Evidence test count: 3
- Route groups: python1516_2025, python1516_2025-fedpro-grpc, java-standard-2025-jpype, java-standard-2025-py4j, cpp-standard-2025-pybind, cpp-standard-2025-grpc


## Support-Services Decomposition Audit

- Audit status: support-services-decomposition-captured
- Slice id: 2025-support-services-proof-families
- Slice ids: 2025-switch-set-get-model, 2025-single-name-reservation-services, 2025-multi-name-reservation-services, 2025-support-federate-and-object-identity-lookups, 2025-support-attribute-interaction-catalog-lookups, 2025-support-policy-update-and-transport-lookups, 2025-support-interaction-dimension-and-range-lookups, 2025-support-handle-normalization-and-region-introspection, 2025-support-advisory-and-reporting-state-inquiries, 2025-support-runtime-policy-state-inquiries, 2025-support-advisory-and-reporting-state-controls, 2025-support-runtime-policy-state-controls
- Requirement count: 59
- Proof families: 5
- Direct-backed families: 5
- FedPro-hosted-backed families: 5
- REST-hosted-backed families: 0
- Assessment: Support-service proof is no longer just one large ledger summary. Its current evidence separates into name reservation and release flows, identity/catalog normalization lookups, transport or range lookups, the 2025 switch inquiry/control model, and factory/decode plus hosted support-seam families, with direct-lane plus hosted FedPro replay anchors across every family while the REST-hosted Python route remains outside those named support-service proof families.
- Next split boundary: If this area needs further tightening, split it first by these support-service proof families and by explicit FedPro-versus-REST hosted route resolution before attempting clause-by-clause completion claims across lookup, inquiry, control, reservation, and decode surfaces.

### support-services/name-reservation-and-release-flows

- Focus: single and multi-name reservation success or failure callbacks, release flows, handoff behavior, and save or join preconditions around reservation state
- Direct test count: 3
- FedPro hosted test count: 4
- REST hosted test count: 0

### support-services/identity-catalog-and-handle-normalization-lookups

- Focus: federate, object, interaction, parameter, and service-group lookup or normalization flows across joined runtime state and loaded catalog metadata
- Direct test count: 2
- FedPro hosted test count: 3
- REST hosted test count: 0

### support-services/transport-order-update-dimension-and-range-lookups

- Focus: transportation, order type, update-rate, dimension, and range-bound lookups plus requester-only transport query callback routing
- Direct test count: 4
- FedPro hosted test count: 4
- REST hosted test count: 0

### support-services/switch-inquiry-and-control-model

- Focus: 2025 set/get support switch model for advisory, reporting, and runtime policy state, including automatic resign, with validation of switch-control inputs
- Direct test count: 2
- FedPro hosted test count: 2
- REST hosted test count: 0

### support-services/factory-decode-and-hosted-support-seam

- Focus: support handle factories, decode helpers, hosted direct support route execution, callback-backlog control around support seams, and preservation of support surfaces across transport
- Direct test count: 3
- FedPro hosted test count: 6
- REST hosted test count: 0


## Object-Management Decomposition Audit

- Audit status: object-management-decomposition-captured
- Slice id: 2025-object-management-proof-families
- Slice ids: 2025-basic-object-exchange, 2025-declaration-publication-services, 2025-declaration-subscription-services, 2025-declaration-relevance-advisory-callbacks, 2025-object-delete-remove-flows, 2025-object-attribute-update-request-callbacks, 2025-object-scope-advisory-callbacks, 2025-object-update-rate-advisory-callbacks, 2025-object-attribute-transport-callbacks, 2025-object-interaction-transport-callbacks, 2025-directed-interaction-boundary, 2025-ddm-default-attribute-policy
- Requirement count: 67
- Proof families: 7
- Direct-backed families: 7
- Hosted-backed families: 7
- Assessment: Object-management proof is no longer just one broad strong-slice claim. Its current evidence separates into declaration/exchange gating, deletion and local-known-state lifecycle, attribute-value-update routing, advisory/update-rate callbacks, transportation policy callbacks, object-region scope routing, and directed or directed-DDM routing families, with direct-lane and hosted FedPro replay anchors across every family.
- Next split boundary: If this area needs further tightening, split it first by these object-management proof families before attempting clause-by-clause completion claims for object, declaration, directed-routing, and DDM services.

### object-management/declaration-and-basic-exchange-gating

- Focus: publish and subscribe control, discovery metadata/class visibility, plain object exchange, and declaration gating or rejection paths
- Direct test count: 7
- Hosted test count: 9

### object-management/deletion-and-local-known-state-lifecycle

- Focus: local delete, timed delete, orphan and remove flows, subscriber known-state rollback, and stale remove cleanup
- Direct test count: 6
- Hosted test count: 7

### object-management/attribute-value-update-request-routing

- Focus: instance and class-wide requestAttributeValueUpdate callbacks, owner-only routing, and disconnected-owner suppression
- Direct test count: 3
- Hosted test count: 5

### object-management/advisory-and-update-rate-callbacks

- Focus: turnUpdatesOn/off advisories, object-scope in-scope or out-of-scope transitions, update-rate routing, and rate alias parity
- Direct test count: 3
- Hosted test count: 4

### object-management/transportation-query-and-policy-state

- Focus: attribute and interaction transportation change confirmation, requester-only query/report callbacks, rejection paths, and restore persistence
- Direct test count: 6
- Hosted test count: 5

### object-management/object-region-scope-and-passive-alias-routing

- Focus: DDM object-region routing, attributesInScope and attributesOutOfScope advisories, passive region aliases, and DDM cleanup
- Direct test count: 6
- Hosted test count: 7

### object-management/directed-and-directed-ddm-interaction-routing

- Focus: directed interaction delivery, timestamped directed routing and retraction, selective directed publication or subscription isolation, and directed DDM overlap routing
- Direct test count: 6
- Hosted test count: 6


## Ownership Decomposition Audit

- Audit status: ownership-decomposition-captured
- Slice ids: 2025-ownership-divestiture-confirmation-flows, 2025-ownership-release-and-if-wanted-flows, 2025-ownership-acquisition-assumption-flows, 2025-ownership-acquisition-availability-cancellation-flows, 2025-ownership-query-and-resign-policies, 2025-save-restore-lifecycle
- Requirement count: 18
- Proof families: 7
- Direct-backed families: 7
- FedPro-hosted-backed families: 7
- REST-hosted-backed families: 5
- Assessment: Ownership proof is no longer just a broad strong-slice claim. Its current evidence separates into divestiture/confirmation, release/if-wanted, acquisition/assumption, availability/cancellation, query visibility, resign-policy, and rollback/restore families. FedPro-hosted replay backs every named family, while the REST-hosted Python route backs the transfer, release, acquisition, cancellation, and query-visibility families but not the narrower resign-policy or rollback families.
- Next split boundary: If this area needs further tightening, split it first by these ownership proof families and by explicit FedPro-versus-REST hosted route resolution before attempting a clause-by-clause ownership conformance audit.

### ownership/divestiture-and-confirmation-flows

- Focus: unconditional and negotiated divestiture, requestDivestitureConfirmation, confirmDivestiture, and cancel-negotiated-offer handling
- Direct test count: 4
- FedPro hosted test count: 4
- REST hosted test count: 2

### ownership/release-and-if-wanted-flows

- Focus: requestAttributeOwnershipRelease, attributeOwnershipReleaseDenied, and divestiture-if-wanted transfer behavior
- Direct test count: 3
- FedPro hosted test count: 3
- REST hosted test count: 2

### ownership/acquisition-assumption-and-notification

- Focus: requestAttributeOwnershipAssumption, explicit acquisition requests, and ownership acquisition notification delivery
- Direct test count: 3
- FedPro hosted test count: 3
- REST hosted test count: 2

### ownership/acquisition-availability-and-cancellation

- Focus: attributeOwnershipAcquisitionIfAvailable, unavailable callbacks, acquisition cancellation, and cancel-confirmation flows
- Direct test count: 3
- FedPro hosted test count: 3
- REST hosted test count: 2

### ownership/query-visibility

- Focus: queryAttributeOwnership, attributeIsOwnedByRTI and attributeIsNotOwned callback outcomes, and isAttributeOwnedByFederate checks
- Direct test count: 2
- FedPro hosted test count: 2
- REST hosted test count: 1

### ownership/resign-policies

- Focus: resign-time ownership divest/delete/cancel behavior
- Direct test count: 1
- FedPro hosted test count: 1
- REST hosted test count: 0

### ownership/rollback-and-restore-state

- Focus: save/restore ownership gauntlets, inflight acquisition or divestiture state, and cross-federate owner-visibility rollback
- Direct test count: 4
- FedPro hosted test count: 4
- REST hosted test count: 0


## Directed Interaction Decomposition Audit

- Audit status: directed-interaction-decomposition-captured
- Slice id: 2025-directed-interaction-boundary
- Requirement count: 11
- Proof families: 5
- Direct-backed families: 5
- Hosted-backed families: 5
- Assessment: The directed-interaction slice is no longer just one boundary claim. Its evidence separates into base routing/callback delivery, timestamped delivery and retraction, DDM overlap filtering, selective set and publication isolation, and restore-path routing cleanup, with direct-lane and hosted FedPro replay anchors across all families.
- Next split boundary: If this slice needs further tightening, split it first by these directed-interaction proof families before further modularizing directed-routing semantics inside hla-backend-python1516-2025.

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


## Directed Interaction Requirement-Family Audit

- Audit status: directed-interaction-requirement-family-map-captured
- Slice id: 2025-directed-interaction-boundary
- Requirement count: 11
- Family count: 5
- All directed-interaction rows family-mapped: True
- Unmapped requirement ids: 0
- Unexpected requirement ids: 0
- Assessment: The directed-interaction aggregate is now backed by an explicit requirement-family map instead of only one flat slice-level claim. That makes the directed declaration-control, send/receive routing, spec-delta, and FI matrix umbrella rows auditable requirement-by-requirement.
- Residual boundary: This is still a requirement-family map over one larger directed-interaction runtime slice, not a promise that every directed-interaction requirement now has its own standalone implemented-evidence slice.

Directed-interaction requirement families:

- declaration-publication-control: 2 requirements, in-slice=True
- declaration-subscription-control: 2 requirements, in-slice=True
- send-receive-routing-and-hla-surface: 4 requirements, in-slice=True
- directed-interaction-delta-rows: 2 requirements, in-slice=True
- service-group-matrix-traceability: 1 requirements, in-slice=True

## DDM Default-Policy Decomposition Audit

- Audit status: ddm-default-policy-decomposition-captured
- Slice id: 2025-ddm-default-attribute-policy
- Requirement count: 23
- Proof families: 6
- Direct-backed families: 6
- Hosted-backed families: 6
- Assessment: The DDM/default-policy slice is no longer just one large region-policy bucket. Its evidence separates into lookup/default-policy control, object-region routing and scope advisories, interaction-region routing, directed DDM routing, passive/compat aliases, and DDM restore/disconnect cleanup.
- Next split boundary: If this slice needs further tightening, split it first by these DDM/default-policy proof families before further modularizing region-routing semantics inside hla-backend-python1516-2025.

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


## DDM Default-Policy Requirement-Family Audit

- Audit status: ddm-default-policy-requirement-family-map-captured
- Slice id: 2025-ddm-default-attribute-policy
- Requirement count: 23
- Family count: 6
- All DDM rows family-mapped: True
- Unmapped requirement ids: 0
- Unexpected requirement ids: 0
- Assessment: The largest runtime-backed DDM/default-policy aggregate is now backed by an explicit requirement-family map instead of only one flat slice-level claim. That makes the lookup/default-policy, region-routing, directed-DDM, passive-alias, and restore/disconnect cleanup boundaries auditable requirement-by-requirement.
- Residual boundary: This is still a requirement-family map over one larger runtime slice, not a promise that every DDM/default-policy requirement now has its own standalone implemented-evidence slice.

DDM default-policy requirement families:

- lookup-and-default-policy-control: 8 requirements, in-slice=True
- object-region-routing-and-scope-advisories: 9 requirements, in-slice=True
- interaction-region-routing: 3 requirements, in-slice=True
- directed-ddm-routing: 1 requirements, in-slice=True
- passive-alias-and-compat-scenarios: 1 requirements, in-slice=True
- ddm-restore-and-disconnect-cleanup: 1 requirements, in-slice=True

## Wrapper-Boundary Family Route-Backing Audit

- Audit status: wrapper-boundary-family-route-backing-captured
- Family count: 23
- Fully route-backed family count: 23
- All families route-backed across current Python lanes: True
- Assessment: The decomposed current-package pressure families are not in-process-only claims. Every currently named family across save/restore, ownership, directed interaction, and DDM/default-policy has both direct python1516_2025 proof and hosted FedPro proof, which strengthens the current-lane working-RTI claim.
- Residual boundary: This still does not prove full cross-binding conformance or full requirement-by-requirement closure; it proves that the main current-package pressure families are executable across the current Python 2025 lanes.

- 2025-save-restore-lifecycle/lifecycle-control: direct=14, hosted=9, route-backed=True
- 2025-save-restore-lifecycle/shared-scenario-rollback: direct=4, hosted=4, route-backed=True
- 2025-save-restore-lifecycle/routing-policy-rollback: direct=7, hosted=7, route-backed=True
- 2025-save-restore-lifecycle/ownership-rollback: direct=4, hosted=4, route-backed=True
- 2025-save-restore-lifecycle/time-window-and-time-state-rollback: direct=5, hosted=5, route-backed=True
- 2025-ownership-proof-families/divestiture-and-confirmation-flows: direct=4, hosted=4, route-backed=True
- 2025-ownership-proof-families/release-and-if-wanted-flows: direct=3, hosted=3, route-backed=True
- 2025-ownership-proof-families/acquisition-assumption-and-notification: direct=3, hosted=3, route-backed=True
- 2025-ownership-proof-families/acquisition-availability-and-cancellation: direct=3, hosted=3, route-backed=True
- 2025-ownership-proof-families/query-visibility: direct=2, hosted=2, route-backed=True
- 2025-ownership-proof-families/resign-policies: direct=1, hosted=1, route-backed=True
- 2025-ownership-proof-families/rollback-and-restore-state: direct=4, hosted=4, route-backed=True
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

## Wrapper-Boundary Family Asymmetry Audit

- Audit status: wrapper-boundary-family-asymmetry-captured
- Family count: 23
- Balanced families: 22
- Direct-heavier families: 1
- Hosted-heavier families: 0
- Assessment: The main current-package pressure families are route-backed across the current Python lanes, but they are not perfectly symmetric. The remaining parity work is now clearer: close hosted-heavier and direct-heavier family imbalances rather than inventing new top-level proof areas.
- Next parity boundary: Use the hosted-heavier and direct-heavier family rows as the next executable parity worklist for the current 2025 lane.

- 2025-save-restore-lifecycle/lifecycle-control: balance=direct-heavier, direct=14, hosted=9, delta=5
- 2025-save-restore-lifecycle/shared-scenario-rollback: balance=balanced, direct=4, hosted=4, delta=0
- 2025-save-restore-lifecycle/routing-policy-rollback: balance=balanced, direct=7, hosted=7, delta=0
- 2025-save-restore-lifecycle/ownership-rollback: balance=balanced, direct=4, hosted=4, delta=0
- 2025-save-restore-lifecycle/time-window-and-time-state-rollback: balance=balanced, direct=5, hosted=5, delta=0
- 2025-ownership-proof-families/divestiture-and-confirmation-flows: balance=balanced, direct=4, hosted=4, delta=0
- 2025-ownership-proof-families/release-and-if-wanted-flows: balance=balanced, direct=3, hosted=3, delta=0
- 2025-ownership-proof-families/acquisition-assumption-and-notification: balance=balanced, direct=3, hosted=3, delta=0
- 2025-ownership-proof-families/acquisition-availability-and-cancellation: balance=balanced, direct=3, hosted=3, delta=0
- 2025-ownership-proof-families/query-visibility: balance=balanced, direct=2, hosted=2, delta=0
- 2025-ownership-proof-families/resign-policies: balance=balanced, direct=1, hosted=1, delta=0
- 2025-ownership-proof-families/rollback-and-restore-state: balance=balanced, direct=4, hosted=4, delta=0
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
- Python2025 backend concentration is material: False
- All pressure families route-backed across current Python lanes: True
- Assessment: The primary 2025 Python RTI lane now has a defensible coherence story: its main current-package pressure slices are identified, decomposed into named proof families, and all of those families are executable across the current Python 2025 lanes. That is strong evidence for a coherent bounded working RTI surface even though the lane still depends on disciplined ownership across the extracted hla-backend-python1516-2025 runtime/state/surface modules.

Residual blockers:

- The public hla-backend-python1516-2025/backend.py shell is now thin, but the extracted runtime/state/surface split still needs continued discipline so coherence is not mistaken for a permanently settled architecture.
- The repo now has a row-level requirement-by-requirement audit, but it still stops at bounded disposition and supported-scope proof rather than an all-covered conformance pass.
- Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.
- Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or MOM action/request conformance pass.

## Current Lane Working-Surface Statement

- Status: current-lane-working-surface-statement
- Ready: True
- Statement: The primary 2025 Python RTI lane can be promoted as the repo's coherent bounded working Python RTI surface: the main full Python 2025 RTI implementation now runs from hla-backend-python1516-2025 while hla-backend-shim is retained only as a legacy compatibility shim, its main current-package pressure families are route-backed across the current Python lanes and the route-parity matrix now serves as the scenario-family ledger for federation, object, ownership, DDM, time, save/restore, MOM, and support-services evidence, Java and C++ shim/binding packages remain segregated supporting lanes rather than alternate Python RTIs, and the repo has enough evidence to make that bounded working-surface claim without hiding legacy-only, bounded-extension, or artifact-gated boundaries.
- Assessment: The repo now has a single explicit statement for the primary 2025 Python RTI lane: promote it as the bounded working Python 2025 RTI surface, treat it as the main full implementation rather than as a mere adapter layer, use the route-parity matrix as the scenario-family ledger behind that claim, keep the architecture seam intact, and continue using the remaining requirement-level and cross-binding blockers to decide whether extraction is ever warranted.

Non-claims:

- This is not a full requirement-by-requirement IEEE 1516.1-2025 conformance claim.
- This is not a permanent no-split architecture decision.
- This does not upgrade Java or C++ bindings into exhaustive behavior-conformance lanes.
- This does not turn the hosted FedPro route into a full RTI semantics or exhaustive cross-binding conformance pass.

## Main Python2025 Implementation Claim Audit

- Audit status: main-python1516_2025-implementation-claim-captured
- Claim shape: bounded-main-python1516_2025-rti-implementation
- Ready for main python1516_2025 implementation claim: True
- Ready for full 2025 conformance claim: False
- Implementation owner: hla-backend-python1516-2025
- Compatibility wrapper: hla-backend-shim
- Default operator lane: python1516_2025-main
- Hosted extension lane: python1516_2025-routes
- Claim: The repo can now make a distinct bounded claim for the main Python 2025 RTI implementation lane: hla-backend-python1516-2025 is the implementation owner for the real executable 2025 Python RTI surface, hla-backend-shim is a legacy compatibility shim, and the direct plus hosted Python 2025 proof lanes are sufficiently green to promote that lane as the main bounded working RTI implementation.
- Assessment: The repo now separates the two judgments cleanly: the main python1516_2025 RTI implementation claim is ready as a bounded working-surface statement, while the broader full-2025 conformance claim remains blocked by row-granularity, cross-binding, hosted-route, xs:any-extension, and legacy-only boundaries.

Promotion basis:

- hla-backend-python1516-2025 is the discovered dedicated rti1516_2025 backend package and current implementation owner.
- The canonical operator lane marks verify-main-2025 as the default direct proof route for the real python1516_2025 runtime.
- All tracked objective dimensions are bounded-ready for the Python-centered 2025 working surface.
- The current-lane working-surface statement is ready without relying on shim-owned runtime semantics.
- The promotion-vs-split audit already says the current python1516_2025 lane can be promoted as the working surface while keeping future extraction optional.

Non-claims:

- This is not a full IEEE 1516.1-2025 conformance claim.
- This does not promote Java or C++ binding routes into full behavior-conformance lanes.
- This does not turn the hosted FedPro route into a second full RTI implementation owner.
- This does not settle a permanent no-split architecture decision.

Full-conformance blockers:

- Covered rows include bounded supported-scope evidence, including OMT xs:any extension payload preservation without arbitrary third-party extension execution semantics.
- Java and C++ binding rows remain artifact/runtime-capability evidence rather than exhaustive behavior-conformance proof.
- The hosted FedPro route remains a bounded runtime slice and not a full RTI semantics or exhaustive cross-binding conformance pass.
- Duplicate/umbrella rows remain normalization aids rather than direct one-row conformance assertions.

## Full-Claim Blocker Partition Audit

- Audit status: full-claim-blocker-partition-captured
- Full-claim blocker count: 4
- Partitioned blocker count: 4
- Direct-runtime incompleteness blocker count: 0
- Boundary-only blocker count: 4
- All current full-claim blockers external to main python1516_2025 runtime: True
- Assessment: The remaining blockers in the full-2025 claim are now explicitly partitioned. On the current tree they all sit outside direct main-lane python1516_2025 runtime completeness: they are OMT extension-scope, Java/C++ binding, hosted-route, or row-granularity boundaries rather than missing core executable behavior in hla-backend-python1516-2025.
- Residual boundary: This partition audit clarifies blocker ownership. It does not convert those external boundaries into a full 2025 conformance pass.

Partitioned blockers:

- omt_xs_any_extension_boundary: external-boundary, counts_against_main_python2025_runtime_completeness=False (bounded OMT extension-payload preservation rather than arbitrary third-party extension execution semantics)
- standard_java_cpp_binding_behavior_gap: external-binding-boundary, counts_against_main_python2025_runtime_completeness=False (Java/C++ rows remain artifact/runtime-capability binding evidence rather than exhaustive behavior conformance)
- hosted_fedpro_full_conformance_gap: external-hosted-boundary, counts_against_main_python2025_runtime_completeness=False (hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or cross-binding pass)
- duplicate_umbrella_row_granularity_gap: row-granularity-boundary, counts_against_main_python2025_runtime_completeness=False (duplicate/umbrella rows remain normalization aids instead of direct one-row conformance assertions)

## Implementation Lane Audit

- Audit status: current-lane-architecture-captured
- Current 2025 backend package: hla-backend-python1516-2025
- Primary 2025 RTI role: main full Python 2025 RTI implementation lane (owned by hla-backend-python1516-2025 with hla-backend-shim retained only as a legacy compatibility shim)
- Current 2025 plugin family: python-rti-1516-2025
- Current 2025 spec support: rti1516_2025
- Compatibility wrapper package: hla-backend-shim
- Compatibility wrapper status: compatibility-maintained
- Compatibility wrapper role: compatibility-wrapper
- Compatibility wrapper delegates runtime semantics to: hla-backend-python1516-2025
- Reference 2010 backend package: hla-backend-python1516e
- Reference 2010 role: 2010 pure Python RTI backend
- Backend packages discovered: 6
- Dedicated 2025 backend package present: True
- Dedicated 2025 candidates cleanly separated: True
- Dedicated 2025 legacy-package delegation violations: 0
- Ready for working-surface promotion: True
- Ready for permanent no-split decision: False
- Clean extraction still optional: True
- Assessment: The repo's current 2025 implementation reality is explicit: the main full Python 2025 RTI implementation now runs from hla-backend-python1516-2025, hla-backend-shim remains only as temporary import-compatibility a legacy compatibility shim over that runtime, the hosted FedPro route is a route variant over that implementation rather than a separate RTI family, the older pure-Python backend remains the 2010-only inmemory lane, and the Java/C++ lanes remain segregated as non-Python binding-capability surfaces rather than being mixed into the Python 2025 RTI claim.
- Extraction boundary: Keep using hla-backend-python1516-2025 as the executable Python 2025 RTI surface while continuing to narrow hla-backend-shim as a legacy compatibility shim; only reopen a deeper extraction question if future evidence shows that residual compatibility or route normalization logic is still obscuring core runtime semantics.

Discovered backend packages:

- hla-backend-certi
- hla-backend-common
- hla-backend-cpp-shim
- hla-backend-python1516e
- hla-backend-python1516-2025
- hla-backend-shim

Discovered 2025-capable backend plugin records:

- cpp-shim-pybind (cpp-shim): hla-backend-cpp-shim supports rti1516e, rti1516_2025
- cpp-shim-grpc (cpp-shim): hla-backend-cpp-shim supports rti1516e, rti1516_2025
- cpp-standard-2025-pybind (standard/cpp): hla-backend-cpp-shim supports rti1516_2025
- cpp-standard-2025-grpc (standard/cpp): hla-backend-cpp-shim supports rti1516_2025
- cpp-2025-sdk-pybind (intake/cpp): hla-backend-cpp-shim supports rti1516_2025
- cpp-2025-sdk-grpc (intake/cpp): hla-backend-cpp-shim supports rti1516_2025
- python1516_2025 (python-rti-1516-2025): hla-backend-python1516-2025 supports rti1516_2025

Python 2025 route variants:

- python1516_2025: in-process-backend-route (separate RTI family: False, all milestone parity-covered: True)
- python1516_2025-fedpro-grpc: hosted-transport-route (separate RTI family: False, all milestone parity-covered: True)

## Python2025 Proof-Lane Audit

- Audit status: python1516_2025-proof-lanes-captured
- Ready for main-implementation operator-lane claim: True
- Direct lane: ./tools/python verify-main-2025
- Direct lane id: python1516_2025-main
- Direct lane cost: medium
- Hosted extension lane: ./tools/python verify-routes-2025
- Hosted extension lane id: python1516_2025-routes
- Hosted extension lane cost: medium
- Claim: The repo does not treat hla-backend-python1516-2025 as a package-only promotion. The canonical operator surface declares ./tools/python verify-main-2025 as the default direct proof lane for the real python1516_2025 runtime and ./tools/python verify-routes-2025 as the bounded hosted FedPro extension over that same runtime.
- Residual boundary: This lane audit now proves command identity, operator-facing proof-lane ownership, and one current-tree green execution of both canonical wrapper commands. It still does not replace the need to keep those proof lanes green as the tree changes.

Current operator runs:

- python1516_2025-main / ./tools/python verify-main-2025: 324 passed across wrapper subcommands plus Target/Radar example (current-tree direct python1516_2025 package-boundary, federation/object/DDM, support/ownership/MOM, time-window, save/restore, callback, OMT, and example-scenario proof lane)
- python1516_2025-routes / ./tools/python verify-routes-2025: 434 passed across direct-plus-hosted wrapper subcommands plus closeout bundle and Target/Radar example (current-tree direct python1516_2025 plus bounded hosted FedPro route verification lane, including transport suite, route-parity bundle, closeout artifact generation, and package-owned example replay)

Evidence anchors: testing/test_surface_manifest.json, tools/python, docs/test_surface.md, README.md


Hosted runtime identity evidence:

- Audit status: direct-server-client-identity-aligned
- Route: python1516_2025-fedpro-grpc
- Claim: The hosted 2025 FedPro route is explicitly evidenced as a route variant over hla-backend-python1516-2025 rather than a separate shim or RTI family.
- Assessment: Hosted-client and hosted-server capability surfaces now agree with the direct 2025 ambassador that python1516_2025-fedpro-grpc is a route variant over the primary python1516_2025 RTI lane in hla-backend-python1516-2025 rather than a wrapper-defined implementation family.

Hosted runtime identity reports:

- Direct ambassador: python1516_2025-rti / python/2025 / python1516_2025 / hla-backend-python1516-2025 / counts_as_python_2025_rti=True
- Hosted server: python1516_2025 / hla-backend-python1516-2025 / counts_as_python_2025_rti=True / wrapper_only=False / rti1516_2025 / grpc
- Hosted client: python1516_2025 / hla-backend-python1516-2025 / counts_as_python_2025_rti=True / wrapper_only=False / rti1516_2025 / grpc / fedpro

Hosted runtime identity evidence tests:

- tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_reports_python2025_main_lane_identity
- tests/test_rti1516_2025_python1516_2025_runtime.py::test_dedicated_python2025_backend_is_discoverable_and_executable

Hosted factory boundary evidence:

- Audit status: factory-boundary-explicit
- Supported hosted creation surface: start_2025_grpc_server(...) plus GrpcTransport(..., schema='rti1516_2025') plus create_rti_ambassador(backend='python1516_2025'|'python-1516-2025'|'python-1516-2025', transport={'kind': 'grpc', ...})
- Unsupported factory surfaces: create_rti_ambassador(backend='shim', transport=...)
- Policy: The primary python1516_2025 backend path and its supported runtime aliases now accept transport=... and create the hosted FedPro 2025 ambassador over the main hla-backend-python1516-2025 lane, while the legacy shim provider spelling is no longer part of the supported public backend-selection surface and therefore rejects hosted ownership and other backend-specific factory transport routing. The same factory-hosted python1516_2025 path now also runs a direct federation listing/member-report slice, the package-owned Target/Radar future-exclusion, output-delivery, consumer-order, and integrated lookahead-processing-window gauntlet time-window proofs, restore-state, restore-output-resume, and pipeline-resume save/restore proofs, a direct restore-control negative slice, a direct local-delete restore slice, a direct plain-callback restore cleanup slice, a direct timed-remove restore cleanup slice, a direct plain-object restore routing slice, a direct plain-interaction restore routing slice, a direct directed-DDM restore routing slice, a direct restore time/switch-control slice, and a direct restore lookahead/queued-TSO slice, direct MOM federation-management and time-management service interactions, a direct MOM request/report slice, a direct MOM object/ownership service slice, a direct support-service slice, the shared support factory/decode scenario, a direct object-exchange slice, a direct timestamped delivery/retraction slice, a direct directed-interaction slice, a direct callback-backlog disconnect/rejoin slice, and a direct ownership slice instead of stopping at ambassador-construction evidence.

Hosted factory boundary evidence tests:

- tests/test_python_api_spec.py::test_runtime_backend_listing_exposes_python1516_2025_as_primary_2025_lane
- tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_python1516_2025_aliases_and_keeps_primary_identity
- tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_legacy_shim_provider_name
- tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_accepts_hosted_transport_on_python1516_2025_aliases
- tests/test_python_api_spec.py::test_generic_runtime_creation_for_2025_rejects_hosted_transport_on_legacy_shim_provider
- tests/test_hla_factory_composition.py::test_2025_version_local_factory_accepts_hosted_transport_creation_on_python1516_2025_lane
- tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_legacy_shim_provider_name
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_transport_route_creates_hosted_python2025_ambassador
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_federation_listing_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_restore_control_negative_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_local_delete_restore_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_plain_callbacks_and_preserves_post_restore_routing
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_clears_stale_timed_remove_and_preserves_post_restore_remove_routing
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_object_subscriber_routing_after_restore
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_plain_interaction_subscriber_routing_after_restore
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_directed_ddm_subscriber_routing_after_restore
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_recovers_time_and_switch_control_state_after_restore
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_lookahead_and_redelivers_presave_queued_tso
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_federation_management_service_interactions
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_mom_time_management_service_interactions
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_request_report_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_mom_object_and_ownership_service_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_support_service_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_shared_support_factory_and_decode_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_drops_disconnected_callback_backlog_before_reconnect
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_object_exchange_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_timestamped_delivery_and_retraction_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_directed_interaction_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_direct_ownership_slice
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_smoke_fom_save_restore_ownership_gauntlet
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_inflight_ownership_state
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_restores_cross_federate_attribute_owner_visibility
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario
- tests/test_hla_factory_composition.py::test_2025_version_local_factory_rejects_unknown_backend_specific_options
- tests/test_hla_factory_composition.py::test_hla_factory_registry_strips_composition_only_options_before_2025_backend_creation
- tests/test_hla_factory_composition.py::test_2025_direct_factory_rejects_composition_only_options_without_hla_factory_layer
- tests/requirements/test_2025_python_rti_backend_audit.py::test_2025_python_rti_backend_audit_keeps_package_docs_aligned_with_runtime_wrapper_boundary

Package-owned shared scenario evidence:

- Audit status: package-owned-target-radar-2025-path-captured
- Scenario package: hla-fom-target-radar
- Shared route: target-radar-shared-scenario
- Example entrypoint: python examples/target_radar_simulation.py --backend python1516_2025 --steps 5
- Adapter class: hla.foms.target_radar._internal.target_radar_2025_adapter.TargetRadar2025RTIAdapter
- Supported backend names: python1516_2025, python-1516-2025, python-1516-2025
- Claim: The shared Target/Radar 2025 execution seam is now owned by the hla-fom-target-radar package, where one package-owned compatibility adapter wraps the primary python1516_2025 backend lane without moving implementation ownership back into hla-backend-shim.
- Assessment: The README-advertised Target/Radar python1516_2025 example path is now executable under package-owned 2025 adapter coverage. The legacy shim package is no longer treated as a backend-selection route, and the same package-owned adapter now also proves that the factory-hosted python1516_2025 FedPro route can execute the shared Target/Radar example scenario plus the shared future-exclusion, output-delivery, consumer-order, integrated lookahead-processing-window gauntlet, restore-state, restore-output-resume, and pipeline-resume scenarios without falling back to shim-owned semantics or raw transport-only wrappers.

Package-owned shared scenario runtime reports:

- python1516_2025: python/2025 / hla-backend-python1516-2025 / counts_as_python_2025_rti=True / wrapper_only=False
- shim: shim/2025 / hla-backend-python1516-2025 / counts_as_python_2025_rti=False / wrapper_only=True

Package-owned shared scenario evidence tests:

- tests/scenarios/test_target_radar_scenario.py::test_target_radar_example_supports_2025_backends
- tests/test_fom_target_radar_split_package.py::test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter
- tests/test_fom_target_radar_split_package.py::test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_target_radar_shared_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario
- tests/transport/test_grpc_transport_2025.py::test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario

Hosted shared-scenario coverage audit:

- Audit status: hosted-shared-fedpro-scenarios-accounted-for
- Shared hosted FedPro scenarios: 36
- Shared hosted scenarios represented in conformance evidence: 36
- Ready for full shared-scenario representation claim: True
- Assessment: Every shared hosted FedPro 2025 scenario is now represented in the conformance evidence ledger, so the hosted route summary is no longer silently under-counting the main python1516_2025 runtime surface.

## Time-Window Vendor Parity Audit

- Audit status: time-window-vendor-parity-captured
- Route count: 3
- Trial-Pitch-safe route count: 2
- Trial-Pitch-safe routes: time-window-future-exclusion, time-window-restore-state
- Trial-Pitch-unsafe routes: time-window-restore-output
- Current trial candidate: time-window-future-exclusion (2 federates)
- Assessment: The Target/Radar time-window ladder now has an explicit vendor-parity shape audit. The future-exclusion route is intentionally two-federate-safe and is the right Pitch trial candidate; the current Pitch gap is runtime seat availability, not an overgrown scenario topology.
- Residual boundary: A green Pitch result would add vendor credence for the two-federate future-exclusion proof, but it would still not replace the broader in-process and hosted Python evidence for output delivery, consumer order, pipeline overlap, or save/restore window replay.

Time-window vendor parity routes:

- time-window-future-exclusion: federates=2, trial-pitch-safe=True, boundary=seat-availability
- time-window-restore-state: federates=2, trial-pitch-safe=True, boundary=seat-availability
- time-window-restore-output: federates=3, trial-pitch-safe=False, boundary=trial-federate-limit-and-seat-availability

## Extraction Readiness Audit

- Audit status: extraction-readiness-map-captured
- Extraction needed now: False
- Dedicated Python 2025 backend present: True
- Recommended current action: promote-python1516_2025-as-live-lane-and-keep-shim-wrapper-narrowing-map
- Future backend package target: hla-backend-python1516-2025
- Future backend plugin family: python-rti-1516-2025
- Runtime semantics to extract first: 4
- Route-backed runtime semantics: 4
- All candidate runtime semantics route-backed: True
- Assessment: The extraction cutover is materially underway: hla-backend-python1516-2025 now owns the live backend, hla-backend-shim remains only as a legacy compatibility shim, and the repo still has a concrete migration map for continuing to narrow that remaining compatibility surface while preserving the direct lane and hosted FedPro proof families.

Extraction package contract:

- Current package state: live-runtime-present
- Target distribution: hla-backend-python1516-2025
- Target import root: hla.backends.python1516_2025
- Target plugin path: packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py
- Target backend name: python1516_2025
- Target plugin family: python-rti-1516-2025
- Target supports: rti1516_2025
- Must not delegate to: hla.backends.shim.backend.create_shim_backend
- Scanner regression test: tests/requirements/test_2025_finish_line_snapshot.py::test_2025_backend_plugin_scan_detects_future_dedicated_python_2025_backend
- Package creation rule: Keep this package as the promoted live backend only while the direct-lane and hosted FedPro proof families stay green and hla-backend-shim continues narrowing as a legacy compatibility shim.

Extraction cutover invariants:

- python1516_2025 and python1516_2025-fedpro-grpc parity rows remain green for every migrated slice
- hla-backend-shim keeps only route normalization, compatibility aliases, and binding bridge behavior
- the dedicated python1516_2025 plugin owns core RTI state for migrated save/restore, directed interaction, DDM, and time semantics
- backend plugin discovery reports hla-backend-python1516-2025 as a dedicated rti1516_2025 candidate before any promotion claim changes

Shim responsibilities after extraction:

- standard-route adaptation and compatibility aliases
- transport-facing normalization that is not core RTI state
- binding/package bridge behavior for standard Java/C++/hosted routes

Runtime semantics migration worklist:

- 2025-save-restore-lifecycle: 5 proof families, direct=34, hosted=29, route-backed=True, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/save_restore_lifecycle.py
- 2025-ownership-proof-families: 7 proof families, direct=20, hosted=20, route-backed=True, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ownership_runtime.py
- 2025-directed-interaction-boundary: 5 proof families, direct=12, hosted=12, route-backed=True, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/directed_interaction_boundary.py
- 2025-ddm-default-attribute-policy: 6 proof families, direct=14, hosted=14, route-backed=True, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ddm_default_attribute_policy.py

Pre-extraction gates:

- keep the dedicated rti1516_2025 Python backend plugin discoverable and keep the backend scan detecting it
- move one decomposed pressure slice at a time while keeping direct-lane and hosted FedPro route tests green
- keep hla-backend-shim as a narrower adapter layer instead of deleting the route-normalization seam

## Extraction Impact Audit

- Audit status: extraction-impact-map-captured
- Candidate slices: 4
- All candidate slices have source-family maps: True
- All candidate slices route-backed: True
- Largest current source baseline: 2025-ddm-default-attribute-policy
- Assessment: The extraction worklist is now tied to measurable current source families. Save/restore, directed interaction, and DDM/default-policy migration candidates each identify the remaining adapter pressure and runtime line baselines that should keep shrinking around hla-backend-python1516-2025.
- Non-claim: This is an impact map, not a migration-complete claim. The dedicated backend is present, but the line baselines are intentionally overlapping because some source families support multiple candidate slices.

Extraction impact rows:

- 2025-save-restore-lifecycle: source families=4, baseline=4112 lines/72 methods, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/save_restore_lifecycle.py; save-restore-runtime=462 lines/13 methods, time-management-runtime=887 lines/27 methods, ownership-runtime=601 lines/11 methods, callback-delivery-and-control=2162 lines/21 methods
- 2025-ownership-proof-families: source families=3, baseline=3225 lines/45 methods, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ownership_runtime.py; ownership-runtime=601 lines/11 methods, save-restore-runtime=462 lines/13 methods, callback-delivery-and-control=2162 lines/21 methods
- 2025-directed-interaction-boundary: source families=3, baseline=3295 lines/53 methods, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/directed_interaction_boundary.py; interaction-routing-runtime=628 lines/23 methods, ddm-region-runtime=505 lines/9 methods, callback-delivery-and-control=2162 lines/21 methods
- 2025-ddm-default-attribute-policy: source families=4, baseline=4830 lines/135 methods, target=packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ddm_default_attribute_policy.py; ddm-region-runtime=505 lines/9 methods, object-attribute-runtime=1535 lines/82 methods, interaction-routing-runtime=628 lines/23 methods, callback-delivery-and-control=2162 lines/21 methods

## Promotion Vs Split Audit

- Decision shape: promote-current-lane-or-split-later-based-on-evidence
- Primary lane package: hla-backend-python1516-2025
- Primary lane role: main full Python 2025 RTI implementation lane (owned by hla-backend-python1516-2025 with hla-backend-shim retained only as a legacy compatibility shim)
- Recommendation: promote-current-lane-as-working-surface-and-keep-split-optional
- Ready for working-surface promotion: True
- Ready for permanent no-split decision: False
- Assessment: Current evidence is strong enough to treat the real Python 2025 RTI implementation now owned by hla-backend-python1516-2025, with hla-backend-shim retained only as a legacy compatibility shim, as the live bounded working-surface lane across the main current-package pressure families, while keeping Java and C++ shim/binding packages segregated from that claim, but not strong enough to make a permanent no-split architectural decision.

Promotion basis:

- The primary 2025 Python RTI lane has green executable runtime coverage in the main in-process suite.
- Both Python 2025 routes clear the tracked bounded working-surface milestones.
- The extracted hla-backend-python1516-2025 package now has direct split-package proof instead of relying only on legacy shim-facing package evidence.
- The python1516_2025 runtime lane is protected by explicit import-boundary guardrails that forbid runtime backflow into hla.backends.shim modules.
- The repo can make a supported-boundary statement over the primary 2025 Python RTI lane without hiding legacy-only or bounded-extension areas.
- Route parity partial and missing counts are both zero for the tracked 2025 matrix.
- The callback ledger is fully route-backed across the current Python 2025 lanes, eliminating callback-helper-only gaps in the promotion surface.
- The main current-package pressure families across save/restore, directed interaction, and DDM/default-policy are all route-backed across the current Python 2025 lanes.

Split triggers:

- Adapter concerns begin to obscure or distort core RTI semantics.
- Callback or route normalization grows more complex than the underlying RTI behavior it wraps.
- New 2025 behavior is materially harder to implement because shim and RTI state management are too tightly mixed.
- The row-level requirement-by-requirement audit cannot be promoted from bounded disposition evidence to cleaner all-covered runtime proof without further shrinking wrapper-only compatibility logic around the main python1516_2025 runtime.

Permanent-decision blockers:

- The repo now has a row-level requirement-by-requirement audit, but it is still a bounded disposition audit rather than an all-covered 2025 conformance pass.
- Several implemented slices still aggregate multiple requirements under bounded supported-scope language.
- Hosted FedPro remains a bounded runtime slice rather than a full RTI semantics or exhaustive cross-binding conformance pass.
- Java and C++ bindings remain artifact/runtime-capability bounded rather than exhaustive behavior-conformance proof.

## Objective Audit

- Surface claim: bounded-working-surface
- Ready for bounded working-surface claim: True
- Ready for full 2025 completion claim: False
- Bounded-ready dimensions: 8 / 8
- Assessment: The repo now supports a bounded working-surface claim across the core runtime dimensions, but that is still weaker than a final 2025 conformance claim because several areas remain slice-bounded or artifact-gated rather than requirement-by-requirement proven.

### Federation Management

- Evidence level: decomposed-strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: federation_lifecycle, save_restore
- Assessment: Connection, federation catalog control, membership reporting and resign handling, synchronization barriers, and save or restore behavior are exercised directly through the current Python 2025 RTI and the hosted FedPro route, and the closeout reporting layer now separates that proof into named families instead of leaving it as one large bucket: connect/create/catalog control, join or membership reporting, resign or disconnect cleanup, synchronization barriers, save/restore lifecycle control, and save/restore participant recovery. The execution-state seam inside that split is now explicit: HLA2025-FI-SVC-005, HLA2025-FI-SVC-008, HLA2025-FI-SVC-010, and HLA2025-FI-SVC-011 anchor the destroy, membership-listing, join, and resign control surface.

- Evidence basis: route_summary.scenario_count=2
- Evidence basis: route_summary.row_count=12
- Evidence basis: route_summary.routes_with_full_parity=6
- Evidence basis: federation_management_decomposition.slice_id=2025-federation-management-proof-families
- Evidence basis: federation_management_decomposition.proof_family_count=6
- Residual blocker: The closeout reporting layer now decomposes federation-management proof families, but it still stops short of clause-by-clause service closure.
- Residual blocker: Standard Java and C++ route coverage remains scenario parity/runtime capability evidence, not exhaustive behavior conformance.

### Object Management

- Evidence level: decomposed-strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: object_exchange, ownership, ddm
- Assessment: The current repo proves a coherent object-management surface and the closeout reporting layer now separates that proof into named families instead of leaving it as one large bucket: declaration and exchange gating, delete/local-known-state lifecycle, attribute-value-update routing, advisory/update-rate callbacks, transportation policy callbacks, object-region scope routing, and directed or directed-DDM routing. Hosted FedPro replay now also covers rollback-sensitive object state including plain and directed routing restore, stale timed-remove cleanup, and restored local-known-state after local delete, plus hosted shared scenario replay for request-attribute-value-update routing and object-scope relevance over the main python1516_2025 runtime.

- Evidence basis: route_summary.scenario_count=3
- Evidence basis: route_summary.row_count=18
- Evidence basis: route_summary.scenarios=ddm,object_exchange,ownership
- Evidence basis: object_management_decomposition.slice_id=2025-object-management-proof-families
- Evidence basis: object_management_decomposition.proof_family_count=7
- Residual blocker: The closeout reporting layer now decomposes object-management proof families, but it still stops short of clause-by-clause service closure.
- Residual blocker: FedPro coverage is a hosted runtime slice and does not yet constitute full RTI semantics proof.

### Time Management

- Evidence level: decomposed-query-and-window-proof-backed
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: time_management, save_restore
- Assessment: Logical-time factories, regulation/constrained mode transitions, advance-request modes, grants, lookahead/query control, timestamped delivery, retraction, and save/restore rollback are all backed by executable runtime traces. The time proof now also includes bounded GALT/LITS query evidence, the Target/Radar lookahead-window proof ladder, matching negative-oracle guards across the current Python 2025 lanes, and named runtime proof families instead of one flat bounded time bucket.

- Evidence basis: python_rti_milestone_audit bounded time rows=python1516_2025-fedpro-grpc:bounded-lookahead-evidence,python1516_2025-fedpro-grpc:bounded-query-evidence,python1516_2025:bounded-lookahead-evidence,python1516_2025:bounded-query-evidence
- Evidence basis: time_window_vendor_parity_audit.audit_status=time-window-vendor-parity-captured
- Evidence basis: time_window_vendor_parity_audit.current_trial_candidate.scenario_id=time-window-future-exclusion
- Evidence basis: time_management_decomposition.slice_id=2025-time-management-proof-families
- Evidence basis: time_management_decomposition.proof_family_count=5
- Residual blocker: The closeout now separates time proof into named runtime families, but it still stops short of final per-requirement time-service proof.
- Residual blocker: Cross-binding runtime evidence is narrower than the Python in-process and hosted FedPro slices.

### Support Services

- Evidence level: decomposed-per-service-runtime-traceable
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: support_services
- Assessment: Handle lookup, dimension bounds, default policy control, normalization and switch inquiry/set flows are exercised through the Python runtime and are represented across tracked binding routes and the hosted FedPro route. The closeout reporting now also carries an explicit support-service ledger via the RTIambassador conformance matrix, and it now separates that proof into named families instead of leaving it as one ledger-only summary: reservation/release flows, lookup and normalization surfaces, transport or dimension lookups, the 2025 switch model, and factory/decode plus hosted support seams. That gives the Python lanes per-service runtime traceability plus complete actionable negative-path coverage. Hosted FedPro support-service replay now also proves reconnect-safe discard of a disconnected peer's disabled callback backlog before later reconnect.

- Evidence basis: support_service_proof_audit.ready_for_support_service_traceability_claim=true
- Evidence basis: support_service_proof_audit.focused_executable_row_count=64
- Evidence basis: support_service_proof_audit.complete_negative_path_row_count=61
- Evidence basis: support_services_decomposition.slice_id=2025-support-services-proof-families
- Evidence basis: support_services_decomposition.proof_family_count=5
- Residual blocker: The closeout reporting layer now decomposes support-service proof families and reaches per-service runtime traceability plus complete actionable negative-path coverage inside the Python routes, but it still stops short of exhaustive cross-binding behavior-conformance proof.
- Residual blocker: Java and C++ proof remains capability-oriented rather than a full standard-route behavior pass, and the hosted FedPro route remains a bounded runtime slice rather than a full support-service conformance route.

### Ownership Management

- Evidence level: decomposed-strong-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: ownership, save_restore
- Assessment: Ownership acquisition, divestiture, release negotiation, query callbacks, resign-time policies, and rollback-sensitive ownership state are all exercised directly through the current Python 2025 RTI and through shared backend-matrix scenarios. Hosted FedPro replay now also proves restored in-flight ownership negotiation state plus restored cross-federate owner-visibility queries, and the closeout reporting now separates that proof into named ownership families instead of leaving it as one opaque bucket.

- Evidence basis: route_summary.scenario_count=2
- Evidence basis: route_summary.row_count=12
- Evidence basis: route_summary.scenarios=ownership,save_restore
- Evidence basis: ownership_decomposition.slice_id=2025-ownership-proof-families
- Evidence basis: ownership_decomposition.proof_family_count=7
- Residual blocker: The closeout now separates ownership proof into named runtime families, but it still stops short of a final clause-by-clause ownership audit.
- Residual blocker: Hosted route parity remains scenario-backed runtime evidence, not a full vendor-equivalent ownership conformance pass.

### Callbacks

- Evidence level: decomposed-callback-ledger-route-backed
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: federation_lifecycle, object_exchange, ownership, time_management, save_restore, mom, support_services
- Assessment: Callback delivery is broad and executable across lifecycle, object, ownership, DDM, time, MOM, and support-service flows, including hosted FedPro callback decoding, reconnect-safe callback backlog cleanup across disconnect/reconnect, and direct Python ambassador behavior. The closeout reporting layer now also carries an explicit callback-by-callback ledger via the FederateAmbassador conformance matrix, that ledger is fully route-backed across the current Python 2025 lanes, and the closeout reporting now separates callback proof into named runtime families instead of leaving it as a flat ledger.

- Evidence basis: callback_proof_audit.ready_for_callback_by_callback_working_surface_claim=true
- Evidence basis: callback_route_parity_audit.ready_for_full_python_lane_callback_route_parity_claim=true
- Evidence basis: callback_route_parity_audit.hosted_or_route_backed_callback_count=55
- Evidence basis: callback_decomposition.slice_id=2025-callback-proof-families
- Evidence basis: callback_decomposition.proof_family_count=8
- Residual blocker: The callback proof is now decomposed into named runtime families, but it still stops short of exhaustive cross-binding callback signature/ordering equivalence proof.
- Residual blocker: Binding-route callback parity is tracked at the scenario level, not as exhaustive callback signature/ordering proof.

### OMT Handling

- Evidence level: decomposed-bounded-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: none
- Assessment: The OMT path is well-instrumented for parser/serializer/schema handling, metadata round-trips, association metadata, and foreign xs:any extension tolerance with extension payload preservation round-trip evidence. The closeout reporting layer now also separates that bounded OMT proof into named decomposition audits for the extended supported subset, service-utilization crosschecks, xs:any extension tolerance, and schema-constraint validation instead of leaving it as one flat parser/validator bucket. Arbitrary third-party extension semantics remain outside the repo-native runtime claim.

- Evidence basis: omt_requirement_proof_audit.ready_for_omt_traceability_claim=false
- Evidence basis: omt_requirement_proof_audit.row_count=461
- Evidence basis: omt_requirement_proof_audit.by_proof_status=supported-subset-traceable:461
- Evidence basis: omt_decomposition.slice_ids=2025-service-utilization-crosscheck,2025-omt-extended-supported-subset,2025-omt-xs-any-extension-tolerance,2025-omt-schema-constraint-validation
- Evidence basis: omt_decomposition.family_counts=service-utilization:10,extended-subset:5,xs-any:5,schema-constraint:4
- Residual blocker: The OMT proof is now decomposed into named subset and validator families, but foreign xs:any extension payloads are still preserved as XML payloads rather than interpreted as repo-native HLA metadata.
- Residual blocker: Parser/serializer support remains a decomposed bounded OMT working surface rather than exhaustive third-party extension execution semantics.

### Binding Routes

- Evidence level: decomposed-bounded-slice
- Bounded working-surface ready: True
- Ready for full claim: False
- Route scenarios: federation_lifecycle, object_exchange, ownership, ddm, time_management, save_restore, mom, support_services
- Assessment: Every tracked 2025 route now has explicit scenario parity rows, and the Python in-process plus hosted FedPro routes provide substantive runtime proof for the working surface. The closeout reporting layer now also separates route evidence into named binding and hosted-route families instead of one flat bounded bucket.

- Evidence basis: route_summary.scenario_count=8
- Evidence basis: route_summary.row_count=48
- Evidence basis: route_summary.routes_with_full_parity=6
- Evidence basis: binding_route_decomposition.slice_id=2025-binding-route-proof-families
- Evidence basis: binding_route_decomposition.proof_family_count=6
- Residual blocker: The route evidence is now decomposed into named families, but Java and C++ routes are still backed by artifact/runtime-capability traces rather than exhaustive behavior equivalence proof.
- Residual blocker: The hosted FedPro route remains a bounded working slice, not a full RTI conformance route.


## Implemented Evidence Slices

These are slice-level implementation readings, not canonical requirement-status rows.
Use the slice disposition column for the local proof-unit state and the backend-scope column for route or adapter reading.

| Slice | Slice disposition | Backend or route scope | Requirements | Evidence |
|---|---|---|---|---|
| 2025-factory-composition | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-REQ-001, HLA2025-FI-003, HLA2025-FI-004 | tests/test_hla_factory_composition.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-auth-connect | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-001, HLA2025-FI-005 | tests/test_rti1516_2025_encoding_auth_contexts.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-fi-service-group-taxonomy | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-002 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, tests/transport/test_rest_transport.py, docs/backend_capability_matrix.md |
| 2025-fom-validation | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FR-001, HLA2025-OMT-001, HLA2025-OMT-005, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, tests/test_hla_factory_composition.py, packages/hla-rti-core/src/hla/fom/validation.py |
| 2025-fi-fdd-minimum-structure | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-007 | tests/factories/test_proto2025_fom_resources.py, tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/validation.py |
| 2025-lifecycle-and-members | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-005, HLA2025-FI-006, HLA2025-NEW-002, HLA2025-NEW-003 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-time-mode-enable-disable | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-027, HLA2025-FI-028, HLA2025-FI-SVC-101, HLA2025-FI-SVC-102, HLA2025-FI-SVC-103, HLA2025-FI-SVC-104, HLA2025-FI-SVC-105, HLA2025-FI-SVC-106 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-create-join-fom-time-effects | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-029, HLA2025-FI-030, HLA2025-FI-031 | tests/backends/test_python_backend_federation_extended.py, tests/test_rti1516_2025_python1516_2025_runtime.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-time-advance-request-modes | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-107, HLA2025-FI-SVC-108, HLA2025-FI-SVC-109, HLA2025-FI-SVC-110, HLA2025-FI-SVC-111 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-grant-and-async-delivery | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-112, HLA2025-FI-SVC-113, HLA2025-FI-SVC-114, HLA2025-FI-SVC-115 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-query-and-lookahead-control | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-116, HLA2025-FI-SVC-117, HLA2025-FI-SVC-118, HLA2025-FI-SVC-119, HLA2025-FI-SVC-120 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-time-queries-retraction-and-order | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-121, HLA2025-FI-SVC-122, HLA2025-FI-SVC-123, HLA2025-FI-SVC-124, HLA2025-FI-SVC-125, HLA2025-FR-010, HLA2025-FI-009 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, tests/backends/test_shim_route_trace_evidence.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-lookahead-window-proofs | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-107, HLA2025-FI-SVC-108, HLA2025-FI-SVC-121, HLA2025-FI-SVC-122, HLA2025-FI-SVC-123, HLA2025-MOD-006 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, tests/backends/test_shim_route_trace_evidence.py |
| 2025-save-restore-lifecycle | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-018, HLA2025-FI-SVC-019, HLA2025-FI-SVC-020, HLA2025-FI-SVC-021, HLA2025-FI-SVC-022, HLA2025-FI-SVC-023, HLA2025-FI-SVC-024, HLA2025-FI-SVC-025, HLA2025-FI-SVC-026, HLA2025-FI-SVC-027, HLA2025-FI-SVC-028, HLA2025-FI-SVC-029, HLA2025-FI-SVC-030, HLA2025-FI-SVC-031, HLA2025-FI-SVC-032, HLA2025-FI-SVC-033, HLA2025-FI-SVC-034, HLA2025-FI-001, HLA2025-FI-005, HLA2025-REQ-002 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-fom-showcase | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FR-001, HLA2025-FR-003, HLA2025-FR-004 | tests/scenarios/test_proto2025_fom_showcase.py, tests/transport/test_grpc_transport_2025.py, packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py |
| 2025-handle-normalization | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-NEW-005, HLA2025-FI-001 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-switch-set-get-model | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-008, HLA2025-FI-001 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-retired-advisory-switch-enable-disable-mapping | legacy-only | explicit legacy-only exclusion; not active backend support | HLA2025-RET-001 | docs/requirements/ieee-1516-2025/retired_legacy_mapping.md, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-fom-mim-error-taxonomy | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-002, HLA2025-MOD-003, HLA2025-FI-008, HLA2025-OMT-007 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-callback-context-object-delivery | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-004, HLA2025-RET-002, HLA2025-FI-001 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-callback-context-interaction-delivery | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-004, HLA2025-RET-002, HLA2025-FI-001 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-directed-interaction-boundary | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-007, HLA2025-NEW-001, HLA2025-FR-003, HLA2025-FR-004, HLA2025-FI-001, HLA2025-FI-SVC-039, HLA2025-FI-SVC-040, HLA2025-FI-SVC-045, HLA2025-FI-SVC-046, HLA2025-FI-SVC-063, HLA2025-FI-SVC-064 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-omt-reference-value-required | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-NEW-006, HLA2025-OMT-002, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py, packages/hla-rti-core/src/hla/fom/validation.py |
| 2025-omt-component-metadata-roundtrip | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-004, HLA2025-OMT-COMP-013, HLA2025-OMT-COMP-030, HLA2025-OMT-COMP-084, HLA2025-OMT-COMP-085, HLA2025-OMT-COMP-087, HLA2025-OMT-COMP-090, HLA2025-OMT-COMP-094, HLA2025-OMT-COMP-140, HLA2025-OMT-COMP-141, HLA2025-OMT-COMP-142, HLA2025-OMT-COMP-143, HLA2025-OMT-COMP-144, HLA2025-OMT-COMP-146, HLA2025-OMT-COMP-150, HLA2025-OMT-COMP-151, HLA2025-OMT-COMP-152, HLA2025-OMT-COMP-190, HLA2025-OMT-COMP-191, HLA2025-OMT-COMP-192, HLA2025-OMT-COMP-194, HLA2025-OMT-COMP-195, HLA2025-OMT-COMP-196, HLA2025-OMT-COMP-215 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-switch-and-transport-subset | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-078, HLA2025-OMT-COMP-125, HLA2025-OMT-COMP-157, HLA2025-OMT-COMP-158, HLA2025-OMT-COMP-159, HLA2025-OMT-COMP-160, HLA2025-OMT-COMP-161, HLA2025-OMT-COMP-162, HLA2025-OMT-COMP-163, HLA2025-OMT-COMP-164, HLA2025-OMT-COMP-165, HLA2025-OMT-COMP-166, HLA2025-OMT-COMP-167, HLA2025-OMT-COMP-168, HLA2025-OMT-COMP-169, HLA2025-OMT-COMP-170, HLA2025-OMT-COMP-200, HLA2025-OMT-COMP-201, HLA2025-OMT-COMP-207 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-extended-supported-subset | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-001, HLA2025-OMT-COMP-002, HLA2025-OMT-COMP-003, HLA2025-OMT-COMP-005, HLA2025-OMT-COMP-007, HLA2025-OMT-COMP-009, HLA2025-OMT-COMP-010, HLA2025-OMT-COMP-016, HLA2025-OMT-COMP-020, HLA2025-OMT-COMP-022, HLA2025-OMT-COMP-023, HLA2025-OMT-COMP-024, HLA2025-OMT-COMP-025, HLA2025-OMT-COMP-026, HLA2025-OMT-COMP-028, HLA2025-OMT-COMP-029, HLA2025-OMT-COMP-031, HLA2025-OMT-COMP-032, HLA2025-OMT-COMP-033, HLA2025-OMT-COMP-034, HLA2025-OMT-COMP-036, HLA2025-OMT-COMP-046, HLA2025-OMT-COMP-050, HLA2025-OMT-COMP-051, HLA2025-OMT-COMP-052, HLA2025-OMT-COMP-053, HLA2025-OMT-COMP-054, HLA2025-OMT-COMP-055, HLA2025-OMT-COMP-058, HLA2025-OMT-COMP-060, HLA2025-OMT-COMP-061, HLA2025-OMT-COMP-062, HLA2025-OMT-COMP-063, HLA2025-OMT-COMP-064, HLA2025-OMT-COMP-065, HLA2025-OMT-COMP-066, HLA2025-OMT-COMP-069, HLA2025-OMT-COMP-071, HLA2025-OMT-COMP-072, HLA2025-OMT-COMP-073, HLA2025-OMT-COMP-083, HLA2025-OMT-COMP-086, HLA2025-OMT-COMP-088, HLA2025-OMT-COMP-089, HLA2025-OMT-COMP-091, HLA2025-OMT-COMP-092, HLA2025-OMT-COMP-093, HLA2025-OMT-COMP-095, HLA2025-OMT-COMP-096, HLA2025-OMT-COMP-097, HLA2025-OMT-COMP-098, HLA2025-OMT-COMP-099, HLA2025-OMT-COMP-100, HLA2025-OMT-COMP-101, HLA2025-OMT-COMP-103, HLA2025-OMT-COMP-104, HLA2025-OMT-COMP-105, HLA2025-OMT-COMP-108, HLA2025-OMT-COMP-116, HLA2025-OMT-COMP-117, HLA2025-OMT-COMP-118, HLA2025-OMT-COMP-119, HLA2025-OMT-COMP-120, HLA2025-OMT-COMP-121, HLA2025-OMT-COMP-122, HLA2025-OMT-COMP-123, HLA2025-OMT-COMP-124, HLA2025-OMT-COMP-126, HLA2025-OMT-COMP-127, HLA2025-OMT-COMP-128, HLA2025-OMT-COMP-131, HLA2025-OMT-COMP-132, HLA2025-OMT-COMP-135, HLA2025-OMT-COMP-136, HLA2025-OMT-COMP-137, HLA2025-OMT-COMP-138, HLA2025-OMT-COMP-139, HLA2025-OMT-COMP-148, HLA2025-OMT-COMP-149, HLA2025-OMT-COMP-153, HLA2025-OMT-COMP-155, HLA2025-OMT-COMP-172, HLA2025-OMT-COMP-173, HLA2025-OMT-COMP-174, HLA2025-OMT-COMP-175, HLA2025-OMT-COMP-177, HLA2025-OMT-COMP-179, HLA2025-OMT-COMP-180, HLA2025-OMT-COMP-182, HLA2025-OMT-COMP-183, HLA2025-OMT-COMP-184, HLA2025-OMT-COMP-185, HLA2025-OMT-COMP-186, HLA2025-OMT-COMP-187, HLA2025-OMT-COMP-188, HLA2025-OMT-COMP-199, HLA2025-OMT-COMP-203, HLA2025-OMT-COMP-205, HLA2025-OMT-COMP-206, HLA2025-OMT-COMP-209, HLA2025-OMT-COMP-211, HLA2025-OMT-COMP-212, HLA2025-OMT-COMP-213, HLA2025-OMT-COMP-214, HLA2025-OMT-COMP-216, HLA2025-OMT-COMP-217, HLA2025-OMT-COMP-218, HLA2025-OMT-COMP-220, HLA2025-OMT-COMP-221, HLA2025-OMT-COMP-223 | tests/test_rti1516_2025_validation.py, tests/factories/test_fom_omt_parsing.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-dimension-metadata-roundtrip | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-037, HLA2025-OMT-COMP-038, HLA2025-OMT-COMP-040, HLA2025-OMT-COMP-041, HLA2025-OMT-COMP-042, HLA2025-OMT-COMP-043, HLA2025-OMT-COMP-044 | tests/factories/test_fom_omt_parsing.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-attribute-metadata-roundtrip | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-011, HLA2025-OMT-COMP-012, HLA2025-OMT-COMP-014, HLA2025-OMT-COMP-015, HLA2025-OMT-COMP-017, HLA2025-OMT-COMP-018 | tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-class-parameter-metadata-roundtrip | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-074, HLA2025-OMT-COMP-079, HLA2025-OMT-COMP-080, HLA2025-OMT-COMP-109, HLA2025-OMT-COMP-114, HLA2025-OMT-COMP-133 | tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-association-metadata-roundtrip | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-048, HLA2025-OMT-COMP-049, HLA2025-OMT-COMP-075, HLA2025-OMT-COMP-076, HLA2025-OMT-COMP-110, HLA2025-OMT-COMP-111, HLA2025-OMT-COMP-112 | tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-omt-xs-any-extension-tolerance | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-COMP-006, HLA2025-OMT-COMP-008, HLA2025-OMT-COMP-019, HLA2025-OMT-COMP-021, HLA2025-OMT-COMP-027, HLA2025-OMT-COMP-035, HLA2025-OMT-COMP-039, HLA2025-OMT-COMP-045, HLA2025-OMT-COMP-047, HLA2025-OMT-COMP-056, HLA2025-OMT-COMP-057, HLA2025-OMT-COMP-059, HLA2025-OMT-COMP-067, HLA2025-OMT-COMP-068, HLA2025-OMT-COMP-070, HLA2025-OMT-COMP-077, HLA2025-OMT-COMP-081, HLA2025-OMT-COMP-082, HLA2025-OMT-COMP-102, HLA2025-OMT-COMP-106, HLA2025-OMT-COMP-107, HLA2025-OMT-COMP-113, HLA2025-OMT-COMP-115, HLA2025-OMT-COMP-129, HLA2025-OMT-COMP-130, HLA2025-OMT-COMP-134, HLA2025-OMT-COMP-145, HLA2025-OMT-COMP-147, HLA2025-OMT-COMP-154, HLA2025-OMT-COMP-156, HLA2025-OMT-COMP-171, HLA2025-OMT-COMP-176, HLA2025-OMT-COMP-178, HLA2025-OMT-COMP-181, HLA2025-OMT-COMP-189, HLA2025-OMT-COMP-193, HLA2025-OMT-COMP-197, HLA2025-OMT-COMP-198, HLA2025-OMT-COMP-202, HLA2025-OMT-COMP-204, HLA2025-OMT-COMP-208, HLA2025-OMT-COMP-210, HLA2025-OMT-COMP-219, HLA2025-OMT-COMP-222, HLA2025-OMT-COMP-224 | tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-carry-forward-cleanup | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-BLG-001, HLA2025-BLG-002, HLA2025-REQ-001 | requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv, requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv, tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-service-utilization-crosscheck | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-SU-001, HLA2025-OMT-SU-002, HLA2025-OMT-SU-003, HLA2025-OMT-SU-004, HLA2025-OMT-SU-005, HLA2025-OMT-SU-006, HLA2025-OMT-SU-007, HLA2025-OMT-SU-008, HLA2025-OMT-SU-009, HLA2025-OMT-SU-010, HLA2025-OMT-SU-011, HLA2025-OMT-SU-012, HLA2025-OMT-SU-013, HLA2025-OMT-SU-014, HLA2025-OMT-SU-015, HLA2025-OMT-SU-016, HLA2025-OMT-SU-017, HLA2025-OMT-SU-018, HLA2025-OMT-SU-019, HLA2025-OMT-SU-020, HLA2025-OMT-SU-021, HLA2025-OMT-SU-022, HLA2025-OMT-SU-023, HLA2025-OMT-SU-024, HLA2025-OMT-SU-025, HLA2025-OMT-SU-026, HLA2025-OMT-SU-027, HLA2025-OMT-SU-028, HLA2025-OMT-SU-029, HLA2025-OMT-SU-030, HLA2025-OMT-SU-031, HLA2025-OMT-SU-032, HLA2025-OMT-SU-033, HLA2025-OMT-SU-034, HLA2025-OMT-SU-035, HLA2025-OMT-SU-036, HLA2025-OMT-SU-037, HLA2025-OMT-SU-038, HLA2025-OMT-SU-039, HLA2025-OMT-SU-040, HLA2025-OMT-SU-041, HLA2025-OMT-SU-042, HLA2025-OMT-SU-043, HLA2025-OMT-SU-044, HLA2025-OMT-SU-045, HLA2025-OMT-SU-046, HLA2025-OMT-SU-047, HLA2025-OMT-SU-048, HLA2025-OMT-SU-049, HLA2025-OMT-SU-050, HLA2025-OMT-SU-051, HLA2025-OMT-SU-052, HLA2025-OMT-SU-053, HLA2025-OMT-SU-054, HLA2025-OMT-SU-055, HLA2025-OMT-SU-056, HLA2025-OMT-SU-057, HLA2025-OMT-SU-058, HLA2025-OMT-SU-059, HLA2025-OMT-SU-060, HLA2025-OMT-SU-061, HLA2025-OMT-SU-062, HLA2025-OMT-SU-063, HLA2025-OMT-SU-064, HLA2025-OMT-SU-065, HLA2025-OMT-SU-066, HLA2025-OMT-SU-067, HLA2025-OMT-SU-068, HLA2025-OMT-SU-069, HLA2025-OMT-SU-070, HLA2025-OMT-SU-071, HLA2025-OMT-SU-072, HLA2025-OMT-SU-073, HLA2025-OMT-SU-074, HLA2025-OMT-SU-075, HLA2025-OMT-SU-076, HLA2025-OMT-SU-077, HLA2025-OMT-SU-078, HLA2025-OMT-SU-079, HLA2025-OMT-SU-080, HLA2025-OMT-SU-081, HLA2025-OMT-SU-082, HLA2025-OMT-SU-083, HLA2025-OMT-SU-084, HLA2025-OMT-SU-085, HLA2025-OMT-SU-086, HLA2025-OMT-SU-087, HLA2025-OMT-SU-088, HLA2025-OMT-SU-089, HLA2025-OMT-SU-090, HLA2025-OMT-SU-091, HLA2025-OMT-SU-092, HLA2025-OMT-SU-093, HLA2025-OMT-SU-094, HLA2025-OMT-SU-095, HLA2025-OMT-SU-096, HLA2025-OMT-SU-097, HLA2025-OMT-SU-098, HLA2025-OMT-SU-099, HLA2025-OMT-SU-100, HLA2025-OMT-SU-101, HLA2025-OMT-SU-102, HLA2025-OMT-SU-103, HLA2025-OMT-SU-104, HLA2025-OMT-SU-105, HLA2025-OMT-SU-106, HLA2025-OMT-SU-107, HLA2025-OMT-SU-108, HLA2025-OMT-SU-109, HLA2025-OMT-SU-110, HLA2025-OMT-SU-111, HLA2025-OMT-SU-112, HLA2025-OMT-SU-113, HLA2025-OMT-SU-114, HLA2025-OMT-SU-115, HLA2025-OMT-SU-116, HLA2025-OMT-SU-117, HLA2025-OMT-SU-118, HLA2025-OMT-SU-119, HLA2025-OMT-SU-120, HLA2025-OMT-SU-121, HLA2025-OMT-SU-122, HLA2025-OMT-SU-123, HLA2025-OMT-SU-124, HLA2025-OMT-SU-125, HLA2025-OMT-SU-126, HLA2025-OMT-SU-127, HLA2025-OMT-SU-128, HLA2025-OMT-SU-129, HLA2025-OMT-SU-130, HLA2025-OMT-SU-131, HLA2025-OMT-SU-132, HLA2025-OMT-SU-133, HLA2025-OMT-SU-134, HLA2025-OMT-SU-135, HLA2025-OMT-SU-136, HLA2025-OMT-SU-137, HLA2025-OMT-SU-138, HLA2025-OMT-SU-139, HLA2025-OMT-SU-140, HLA2025-OMT-SU-141, HLA2025-OMT-SU-142, HLA2025-OMT-SU-143, HLA2025-OMT-SU-144, HLA2025-OMT-SU-145, HLA2025-OMT-SU-146, HLA2025-OMT-SU-147, HLA2025-OMT-SU-148, HLA2025-OMT-SU-149, HLA2025-OMT-SU-150, HLA2025-OMT-SU-151, HLA2025-OMT-SU-152, HLA2025-OMT-SU-153, HLA2025-OMT-SU-154, HLA2025-OMT-SU-155, HLA2025-OMT-SU-156, HLA2025-OMT-SU-157, HLA2025-OMT-SU-158, HLA2025-OMT-SU-159, HLA2025-OMT-SU-160, HLA2025-OMT-SU-161, HLA2025-OMT-SU-162, HLA2025-OMT-SU-163, HLA2025-OMT-SU-164, HLA2025-OMT-SU-165, HLA2025-OMT-SU-166, HLA2025-OMT-SU-167, HLA2025-OMT-SU-168, HLA2025-OMT-SU-169, HLA2025-OMT-SU-170, HLA2025-OMT-SU-171, HLA2025-OMT-SU-172, HLA2025-OMT-SU-173, HLA2025-OMT-SU-174, HLA2025-OMT-SU-175, HLA2025-OMT-SU-176, HLA2025-OMT-SU-177, HLA2025-OMT-SU-178, HLA2025-OMT-SU-179, HLA2025-OMT-SU-180, HLA2025-OMT-SU-181, HLA2025-OMT-SU-182, HLA2025-OMT-SU-183, HLA2025-OMT-SU-184, HLA2025-OMT-SU-185, HLA2025-OMT-SU-186, HLA2025-OMT-SU-187, HLA2025-OMT-SU-188, HLA2025-OMT-SU-189, HLA2025-OMT-SU-190, HLA2025-OMT-SU-191, HLA2025-OMT-SU-192, HLA2025-OMT-SU-193, HLA2025-OMT-SU-194, HLA2025-OMT-SU-195, HLA2025-OMT-SU-196, HLA2025-OMT-ISU-001, HLA2025-OMT-ISU-002, HLA2025-OMT-ISU-003, HLA2025-OMT-ISU-004 | tests/factories/test_fom_omt_parsing.py, tests/factories/test_fom_roundtrip.py, tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-exception-and-logical-time-deltas | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-009, HLA2025-MOD-010, HLA2025-VER-002 | tests/test_rti1516_2025_validation.py, requirements/2025/STRICT_DOC_INVENTORY.json, packages/hla-rti-core/src/hla/fom/__init__.py |
| 2025-java-binding-source-trace | implemented-slice | Java/C++ binding or standard-route evidence over python1516_2025 | HLA2025-BND-001, HLA2025-FI-003, HLA2025-FI-004, HLA2025-FI-035, HLA2025-FI-036, HLA2025-FI-037, HLA2025-FI-038, HLA2025-TRACE-004 | requirements/2025/STRICT_DOC_INVENTORY.json, requirements/2025/SOURCE_TRACE.md, docs/evidence/java-intake/java-2025-standard-shim-2025-jpype.json, docs/evidence/java-intake/java-2025-standard-shim-2025-py4j.json, tests/backends/test_standard_shim_artifacts.py, tests/test_standard_shim_contract.py |
| 2025-cpp-binding-source-trace | implemented-slice | Java/C++ binding or standard-route evidence over python1516_2025 | HLA2025-BND-002, HLA2025-FI-003, HLA2025-FI-004, HLA2025-FI-035, HLA2025-FI-036, HLA2025-TRACE-004 | requirements/2025/SOURCE_TRACE.md, docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json, docs/evidence/cpp-intake/cpp-standard-2025-2025-grpc.json, docs/evidence/shim_routes/cpp-standard-2025.json, tests/backends/test_standard_shim_artifacts.py, tests/test_standard_shim_contract.py |
| 2025-standard-route-runtime-capability | implemented-slice | Java/C++ binding or standard-route evidence over python1516_2025 | HLA2025-BND-001, HLA2025-BND-002, HLA2025-FR-001, HLA2025-FR-004, HLA2025-FI-001, HLA2025-FI-003, HLA2025-FI-004, HLA2025-FI-005, HLA2025-FI-006, HLA2025-FI-009, HLA2025-FI-032, HLA2025-FI-034, HLA2025-MOD-005, HLA2025-MOD-006, HLA2025-MOD-007, HLA2025-NEW-004, HLA2025-NEW-007, HLA2025-OMT-018 | tests/backends/test_standard_shim_artifacts.py, tests/test_standard_shim_contract.py, packages/hla-verification/src/hla/verification/shim_route_evidence.py, packages/hla-bridge-java-common/src/hla/bridges/java/common/java_standard_2025.py, packages/hla-backend-cpp-shim/src/hla/backends/cpp_shim/standard.py, packages/hla-rti-core/src/hla/rti/standard_shims.py |
| 2025-omt-tool-validation-boundary | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-018, HLA2025-OMT-020, HLA2025-TRACE-005 | tests/backends/test_standard_shim_artifacts.py, tests/factories/test_fom_omt_parsing.py, tests/test_rti1516_2025_validation.py, tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-bridge-java-common/src/hla/bridges/java/common/java_standard_2025.py, packages/hla-backend-cpp-shim/src/hla/backends/cpp_shim/standard.py, packages/hla-rti-core/src/hla/fom/__init__.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_bootstrap_runtime.py |
| 2025-fedpro-typed-transport-surface | implemented-slice | hosted FedPro route slice over python1516_2025 | HLA2025-BND-003, HLA2025-FI-004 | tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto |
| 2025-fedpro-hosted-runtime-core | implemented-slice | hosted FedPro route slice over python1516_2025 | HLA2025-BND-003, HLA2025-FI-004 | tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-fedpro-hosted-runtime-extended-state | implemented-slice | hosted FedPro route slice over python1516_2025 | HLA2025-BND-003, HLA2025-FI-004 | tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py |
| 2025-ddm-default-attribute-policy | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOD-007, HLA2025-NEW-004, HLA2025-FI-001, HLA2025-FI-005, HLA2025-FI-SVC-159, HLA2025-FI-SVC-160, HLA2025-FI-SVC-161, HLA2025-FI-SVC-164, HLA2025-FI-SVC-128, HLA2025-FI-SVC-129, HLA2025-FI-SVC-126, HLA2025-FI-SVC-127, HLA2025-FI-SVC-130, HLA2025-FI-SVC-131, HLA2025-FI-SVC-132, HLA2025-FI-SVC-133, HLA2025-FI-SVC-134, HLA2025-FI-SVC-135, HLA2025-FI-SVC-136, HLA2025-FI-SVC-137, HLA2025-FI-SVC-076, HLA2025-FI-SVC-124, HLA2025-FI-SVC-157 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/backends/test_python_backend_time_ddm_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-omt-schema-constraint-validation | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-OMT-CV-001, HLA2025-OMT-CV-002, HLA2025-OMT-CV-003, HLA2025-OMT-CV-004, HLA2025-OMT-CV-005, HLA2025-OMT-CV-006, HLA2025-OMT-CV-007, HLA2025-OMT-CV-008, HLA2025-OMT-CV-009, HLA2025-OMT-CV-010, HLA2025-OMT-CV-011, HLA2025-OMT-CV-012, HLA2025-OMT-CV-013, HLA2025-OMT-CV-014, HLA2025-OMT-CV-015, HLA2025-OMT-CV-016, HLA2025-OMT-CV-017, HLA2025-OMT-CV-018, HLA2025-OMT-CV-019, HLA2025-OMT-CV-020, HLA2025-OMT-CV-021, HLA2025-OMT-CV-022, HLA2025-OMT-CV-023, HLA2025-OMT-CV-024, HLA2025-OMT-CV-025, HLA2025-OMT-CV-026, HLA2025-OMT-CV-027, HLA2025-OMT-CV-028, HLA2025-OMT-CV-029 | tests/test_rti1516_2025_validation.py, packages/hla-rti-core/src/hla/fom/validation.py, docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd |
| 2025-basic-object-exchange | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-057, HLA2025-FI-SVC-058, HLA2025-FI-SVC-059, HLA2025-FI-SVC-060, HLA2025-FI-SVC-061, HLA2025-FI-SVC-062, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-object-delete-remove-flows | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-065, HLA2025-FI-SVC-066, HLA2025-FI-SVC-067, HLA2025-FR-003, HLA2025-FR-004, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-object-attribute-update-request-callbacks | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-070, HLA2025-FI-SVC-071, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-object-scope-advisory-callbacks | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-068, HLA2025-FI-SVC-069, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-object-update-rate-advisory-callbacks | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-072, HLA2025-FI-SVC-073, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-object-attribute-transport-callbacks | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-074, HLA2025-FI-SVC-075, HLA2025-FI-SVC-077, HLA2025-FI-SVC-078, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-object-interaction-transport-callbacks | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-079, HLA2025-FI-SVC-080, HLA2025-FI-SVC-081, HLA2025-FI-SVC-082, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-single-name-reservation-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-051, HLA2025-FI-SVC-052, HLA2025-FI-SVC-053, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-multi-name-reservation-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-054, HLA2025-FI-SVC-055, HLA2025-FI-SVC-056, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-connection-lifecycle-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-002, HLA2025-FI-SVC-003 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-connect-and-federation-catalog-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-001, HLA2025-FI-SVC-004, HLA2025-FI-SVC-005, HLA2025-FI-SVC-006, HLA2025-FI-SVC-007 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-federate-membership-and-resign-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-008, HLA2025-FI-SVC-009, HLA2025-FI-SVC-010, HLA2025-FI-SVC-011, HLA2025-FI-SVC-012 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-synchronization-point-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-013, HLA2025-FI-SVC-014, HLA2025-FI-SVC-015, HLA2025-FI-SVC-016, HLA2025-FI-SVC-017 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-declaration-publication-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-035, HLA2025-FI-SVC-036, HLA2025-FI-SVC-037, HLA2025-FI-SVC-038, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-declaration-subscription-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-041, HLA2025-FI-SVC-042, HLA2025-FI-SVC-043, HLA2025-FI-SVC-044, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-declaration-relevance-advisory-callbacks | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-047, HLA2025-FI-SVC-048, HLA2025-FI-SVC-049, HLA2025-FI-SVC-050 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_object_management_backend_matrix.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-federate-and-object-identity-lookups | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-138, HLA2025-FI-SVC-139, HLA2025-FI-SVC-140, HLA2025-FI-SVC-141, HLA2025-FI-SVC-142, HLA2025-FI-SVC-143, HLA2025-FI-SVC-144, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_support_services_backend_matrix.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-attribute-interaction-catalog-lookups | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-145, HLA2025-FI-SVC-146, HLA2025-FI-SVC-149, HLA2025-FI-SVC-150, HLA2025-FI-SVC-151, HLA2025-FI-SVC-152, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_support_services_backend_matrix.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-policy-update-and-transport-lookups | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-147, HLA2025-FI-SVC-148, HLA2025-FI-SVC-153, HLA2025-FI-SVC-154, HLA2025-FI-SVC-155, HLA2025-FI-SVC-156, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_support_services_backend_matrix.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-interaction-dimension-and-range-lookups | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-158, HLA2025-FI-SVC-163, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/backends/test_python_backend_support_services.py, tests/backends/test_python_backend_time_ddm_extended.py, tests/verification/test_spec_traceability_and_extended_python_rti.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-handle-normalization-and-region-introspection | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-162, HLA2025-FI-SVC-165, HLA2025-FI-SVC-166, HLA2025-FI-SVC-167, HLA2025-FI-SVC-168, HLA2025-FI-SVC-169 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/backends/test_python_backend_time_ddm_extended.py, tests/backends/test_python_backend_support_services.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-advisory-and-reporting-state-inquiries | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-170, HLA2025-FI-SVC-172, HLA2025-FI-SVC-174, HLA2025-FI-SVC-176, HLA2025-FI-SVC-178, HLA2025-FI-SVC-182, HLA2025-FI-SVC-184, HLA2025-FI-SVC-186 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-runtime-policy-state-inquiries | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-180, HLA2025-FI-SVC-188, HLA2025-FI-SVC-189, HLA2025-FI-SVC-190, HLA2025-FI-SVC-191, HLA2025-FI-SVC-192 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-advisory-and-reporting-state-controls | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-171, HLA2025-FI-SVC-173, HLA2025-FI-SVC-175, HLA2025-FI-SVC-177, HLA2025-FI-SVC-179, HLA2025-FI-SVC-183, HLA2025-FI-SVC-185, HLA2025-FI-SVC-187 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-support-runtime-policy-state-controls | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-181 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-callback-control-services | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-193, HLA2025-FI-SVC-194, HLA2025-FI-SVC-195, HLA2025-FI-SVC-196 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto |
| 2025-ownership-divestiture-confirmation-flows | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-083, HLA2025-FI-SVC-084, HLA2025-FI-SVC-086, HLA2025-FI-SVC-087, HLA2025-FI-SVC-095, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-ownership-release-and-if-wanted-flows | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-092, HLA2025-FI-SVC-093, HLA2025-FI-SVC-094, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-ownership-acquisition-assumption-flows | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-085, HLA2025-FI-SVC-088, HLA2025-FI-SVC-089, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-ownership-acquisition-availability-cancellation-flows | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-090, HLA2025-FI-SVC-091, HLA2025-FI-SVC-096, HLA2025-FI-SVC-097, HLA2025-MOD-005, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-ownership-query-and-resign-policies | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-FI-SVC-098, HLA2025-FI-SVC-099, HLA2025-FI-SVC-100, HLA2025-FI-001, HLA2025-FI-005 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/scenarios/test_ownership_management_backend_matrix.py, tests/backends/test_python_backend_object_ownership_extended.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py |
| 2025-mom-service-report-records | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOM-004, HLA2025-NEW-007, HLA2025-REQ-002 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-mom-manager-action-routing | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-NEW-007, HLA2025-REQ-002 | tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py |
| 2025-mom-manager-query-and-report-routing | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MOM-001, HLA2025-MOM-002, HLA2025-MOM-003, HLA2025-MOM-005, HLA2025-OMT-011, HLA2025-NEW-007, HLA2025-REQ-002 | tests/factories/test_fom_omt_parsing.py, tests/test_rti1516_2025_python1516_2025_runtime.py, tests/transport/test_grpc_transport_2025.py, packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py, packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py, packages/hla-rti-core/src/hla/fom/mom.py |
| 2025-wsdl-legacy-only | legacy-only | explicit legacy-only exclusion; not active backend support | HLA2025-RET-003, HLA2025-BND-003, HLA2025-REQ-002 | requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv, CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto |
| 2025-verification-anchor-matrix | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-VER-001, HLA2025-TRACE-001, HLA2025-TRACE-002 | tests/requirements/test_2025_finish_line_snapshot.py, packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py, requirements/2025/requirement_completion_backlog.csv, docs/requirements/ieee-1516-2025/executable_tests/hla_2025_executable_test_requirements_v3.csv |
| 2025-python-rti-milestone-ledger | implemented-slice | direct python1516_2025 slice; widen to hosted or bindings only through linked route evidence | HLA2025-MIL-001, HLA2025-MIL-002, HLA2025-MIL-003, HLA2025-MIL-004, HLA2025-MIL-005, HLA2025-MIL-006 | tests/requirements/test_2025_finish_line_snapshot.py, packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py, packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py, requirements/2025/requirement_completion_backlog.csv |

## Highest-Priority Open Work

These are backlog rows. Keep canonical backlog disposition separate from backend or binding scope.

| ID | Area | Priority | Canonical backlog disposition | Backend or binding scope | Verification work |
|---|---|---|---|---|---|

## Finish Rule

Each future or reopened row needs a positive test, a negative unsupported-boundary test, or an explicit supported-subset/unsupported-boundary disposition before it can be counted as closed.

Do not promote `partial` rows by broad wording. Narrow the claim or add the missing positive/negative evidence.
