# IEEE 1516-2025 Requirements Finish Line

This inventory is deliberately conservative. It records implemented slices, partial slices, and planned work without using HLA conformance language.

## Current Scale

- Initial curated registry rows: 28
- Imported executable-test rows: 1117
- Completion-backlog rows: 27
- High-priority rows still open: 0

## Implemented Evidence Slices

| Slice | Status | Requirements | Evidence |
|---|---|---|---|
| 2025-factory-composition | implemented-slice | HLA2025-REQ-001, HLA2025-FI-003, HLA2025-FI-004 | tests/test_hla_factory_composition.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-auth-connect | implemented-slice | HLA2025-MOD-001, HLA2025-FI-005 | tests/test_rti1516_2025_encoding_auth_contexts.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-fom-validation | implemented-slice | HLA2025-FR-001, HLA2025-OMT-001, HLA2025-OMT-005, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, tests/test_hla_factory_composition.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py |
| 2025-lifecycle-and-members | implemented-slice | HLA2025-FI-005, HLA2025-FI-006, HLA2025-NEW-002, HLA2025-NEW-003 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-logical-time | implemented-slice | HLA2025-FR-010, HLA2025-FI-009, HLA2025-MOD-006 | tests/test_rti1516_2025_spec_and_shim.py, tests/backends/test_shim_route_trace_evidence.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-fom-showcase | implemented-slice | HLA2025-FR-001, HLA2025-FR-003, HLA2025-FR-004 | tests/scenarios/test_proto2025_fom_showcase.py, packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py |
| 2025-handle-normalization | implemented-slice | HLA2025-NEW-005, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/handles.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-switch-inquiry-control | implemented-slice | HLA2025-MOD-008, HLA2025-RET-001, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-fom-mim-error-taxonomy | implemented-slice | HLA2025-MOD-002, HLA2025-MOD-003, HLA2025-FI-008, HLA2025-OMT-007 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-callback-context-parameters | implemented-slice | HLA2025-MOD-004, HLA2025-RET-002, HLA2025-FI-001 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py |
| 2025-directed-interaction-boundary | unsupported-boundary | HLA2025-NEW-001, HLA2025-REQ-002, HLA2025-FI-005 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-omt-reference-value-required | implemented-slice | HLA2025-NEW-006, HLA2025-OMT-002, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py |
| 2025-carry-forward-cleanup | implemented-slice | HLA2025-BLG-001, HLA2025-BLG-002, HLA2025-REQ-001 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/differentials/HLA_1516_2025_vs_2010_Differential_Set.csv, requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv, tests/test_rti1516_2025_validation.py, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-exception-and-logical-time-deltas | implemented-slice | HLA2025-MOD-009, HLA2025-MOD-010, HLA2025-VER-002 | tests/requirements/test_2025_tail_backlog_evidence.py, tests/test_rti1516_2025_validation.py, requirements/2025/STRICT_DOC_INVENTORY.json, packages/hla-rti1516e/src/hla/rti1516e/fom.py |
| 2025-java-binding-source-trace | implemented-slice | HLA2025-BND-001, HLA2025-FI-003, HLA2025-FI-004 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/STRICT_DOC_INVENTORY.json, requirements/2025/SOURCE_TRACE.md, docs/evidence/java-intake/java-2025-standard-shim-2025-jpype.json, docs/evidence/java-intake/java-2025-standard-shim-2025-py4j.json |
| 2025-cpp-binding-source-trace | implemented-slice | HLA2025-BND-002, HLA2025-FI-003, HLA2025-FI-004 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/SOURCE_TRACE.md, docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json, docs/evidence/cpp-intake/cpp-standard-2025-2025-grpc.json, docs/evidence/shim_routes/cpp-standard-2025.json |
| 2025-fedpro-transport-contract | implemented-slice | HLA2025-BND-003, HLA2025-FI-004 | tests/requirements/test_2025_tail_backlog_evidence.py, tests/transport/test_grpc_transport_2025.py, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto |
| 2025-tail-unsupported-behavior-boundaries | unsupported-boundary | HLA2025-MOD-005, HLA2025-MOD-007, HLA2025-NEW-004, HLA2025-NEW-007, HLA2025-REQ-002 | tests/test_rti1516_2025_spec_and_shim.py, tests/requirements/test_2025_tail_backlog_evidence.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-wsdl-legacy-only | legacy-only | HLA2025-RET-003, HLA2025-BND-003, HLA2025-REQ-002 | tests/requirements/test_2025_tail_backlog_evidence.py, requirements/2025/differentials/HLA_1516_2025_vs_2010_Code_Reuse_Disposition.csv, CERTI/xml/ieee1516-2010/1516_1-2010/hla1516e.wsdl, packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto |

## Highest-Priority Open Work

| ID | Area | Priority | Status | Verification work |
|---|---|---|---|---|

## Finish Rule

Each remaining row needs a positive test, a negative unsupported-boundary test, or an explicit supported-subset/unsupported-boundary row before it can be counted as closed.

Do not promote `partial` rows by broad wording. Narrow the claim or add the missing positive/negative evidence.
