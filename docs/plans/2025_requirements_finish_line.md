# IEEE 1516-2025 Requirements Finish Line

This inventory is deliberately conservative. It records implemented slices,
partial slices, and planned work without using HLA conformance language.

## Current Scale

- Initial curated registry rows: 28
- Imported executable-test rows: 1117
- Completion-backlog rows: 27
- High-priority rows still open: 22

## Implemented Evidence Slices

| Slice | Status | Requirements | Evidence |
|---|---|---|---|
| 2025-factory-composition | implemented-slice | HLA2025-REQ-001, HLA2025-FI-003, HLA2025-FI-004 | tests/test_hla_factory_composition.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-auth-connect | implemented-slice | HLA2025-MOD-001, HLA2025-FI-005 | tests/test_rti1516_2025_encoding_auth_contexts.py, packages/hla-rti-core/src/hla/rti/factory.py |
| 2025-fom-validation | implemented-slice | HLA2025-FR-001, HLA2025-OMT-001, HLA2025-OMT-005, HLA2025-OMT-006 | tests/test_rti1516_2025_validation.py, tests/test_hla_factory_composition.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/validation.py |
| 2025-lifecycle-and-members | implemented-slice | HLA2025-FI-005, HLA2025-FI-006, HLA2025-NEW-002, HLA2025-NEW-003 | tests/test_rti1516_2025_spec_and_shim.py, packages/hla-backend-shim/src/hla/backends/shim/backend.py |
| 2025-logical-time | partial | HLA2025-FR-010, HLA2025-FI-009, HLA2025-MOD-006 | tests/test_rti1516_2025_spec_and_shim.py, tests/backends/test_shim_route_trace_evidence.py, packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py |
| 2025-fom-showcase | implemented-slice | HLA2025-FR-001, HLA2025-FR-003, HLA2025-FR-004 | tests/scenarios/test_proto2025_fom_showcase.py, packages/hla-verification/src/hla/verification/repo_internal/verification/proto2025_fom_showcase.py |

## Highest-Priority Open Work

| ID | Area | Priority | Status | Verification work |
|---|---|---|---|---|
| HLA2025-MOD-004 | Callback context parameters | very-high | planned | Callback signature inspection plus object/interaction delivery tests with populated context |
| HLA2025-MOD-008 | Switch inquiry and control model | very-high | planned | Switch service matrix over advisory service reporting exception reporting file reporting and relaxed DDM switches |
| HLA2025-NEW-001 | Directed interactions | very-high | planned | Two-federate directed interaction tests plus FOM/OMT parser fixture |
| HLA2025-MOD-002 | Create and join federation FOM handling | very-high | partial | Positive FOM module smoke test and negative module-resolution matrix |
| HLA2025-MOD-003 | FOM and MIM module loading | very-high | partial | XML/MIM fixture tests for parser validator and loader error taxonomy |
| HLA2025-MOD-006 | Time management and flush queue grant | very-high | partial | Python RTI time matrix plus Java/C++ signature conformance checks |
| HLA2025-NEW-006 | OMT reference data types and valueRequired | very-high | partial | OMT fixture parser validator round-trip and generated model check |
| HLA2025-BLG-001 | Renumbered service utilization rows | high | planned | CSV check comparing 2010_section_or_location and 2025_section_or_location for carry-forward rows |
| HLA2025-BLG-002 | Common object model concepts | high | planned | Parser/model round-trip tests with mixed 2010-compatible and 2025-only metadata |
| HLA2025-BND-001 | Java 2025 binding surface | high | planned | Java compile/intake signature tests and source-trace checks |
| HLA2025-BND-002 | C++ 2025 binding surface | high | planned | C++ shim compile/intake signature tests and source-trace checks |
| HLA2025-BND-003 | FedPro protobuf 2025 transport | high | planned | Protobuf schema tests route round-trip tests and error-mapping tests |
| HLA2025-MOD-005 | Ownership user tags and set callbacks | high | planned | Two-federate ownership tests covering positive tag propagation and unsupported boundary |
| HLA2025-MOD-007 | DDM dimension lookup | high | planned | DDM handle lookup tests and retired-row disposition check |
| HLA2025-MOD-009 | Exception delta pass | high | planned | Negative-path matrix driven by differential exception rows |
| HLA2025-MOD-010 | XML logical time naming | high | planned | XML parser round-trip and stale-token grep guard |
| HLA2025-NEW-004 | Default attribute policy changes | high | planned | Object update policy tests for default transportation and order |
| HLA2025-NEW-005 | Handle normalization | high | planned | Handle normalization unit tests and binding adapter tests |
| HLA2025-NEW-007 | MOM service reporting changes | high | planned | MOM report serialization tests and service-reporting switch tests |
| HLA2025-RET-001 | Advisory switch enable disable services | high | planned | Disposition test over retired/mapped rows and switch backlog rows |
| HLA2025-RET-002 | Supplemental callback info helpers | high | planned | Disposition test plus callback signature tests |
| HLA2025-RET-003 | 2010 WSDL | high | planned | FedPro contract tests or legacy-only disposition check |

## Finish Rule

Each remaining row needs a positive test, a negative unsupported-boundary test,
or an explicit supported-subset row before it can be counted as closed.

Do not promote `partial` rows by broad wording. Narrow the claim or add the
missing positive/negative evidence.
