# v0.13 MOM negative-path execution and service conformance matrix

This slice turns the table-driven MOM negative-path matrix into executable strict-mode tests and expands the broader service-by-service conformance matrix.

Section anchors:

- IEEE 1516.1-2010 §11.2: MOM object model exposure.
- IEEE 1516.1-2010 §11.3: MOM interaction model exposure and RTI send/receive direction.
- IEEE 1516.1-2010 §11.4.1: MOM request, adjust, and service interaction behavior.
- IEEE 1516.1-2010 §11.5: MOM reporting and service/exception reporting.
- IEEE 1516.1-2010 §4-§10: RTIambassador and FederateAmbassador service matrix.

## MOM negative-path matrix execution

The MOM negative matrix is still generated from the active MIM/FOM catalog, but v0.13 now flattens the matrix into stable case IDs and classifies each row as directly executable or semantic/precondition-oriented.

| Metric | Count |
|---|---:|
| MOM interaction classes in active catalog | 84 |
| RTI-received leaf interactions | 53 |
| Total generated negative cases | 269 |
| Executable parameter-decoding cases | 237 |
| Semantic HLAservice precondition cases | 32 |

The executable rows are now run by:

```text
tests/test_mom_negative_matrix_parametrized_v013.py::test_generated_mom_parameter_negative_matrix_case_executes
```

The executable cases cover strict-mode validation for:

- unexpected parameters;
- missing required parameters;
- missing at-least-one parameter choices;
- bad boolean encodings;
- bad float encodings;
- bad logical-time encodings;
- bad lookahead interval encodings;
- bad handle and handle-set encodings.

Each executed failure must both raise a Python RTI exception and emit a MOM exception report, so the test validates both the direct service result and the management-report side effect.

The 32 semantic rows are not marked complete. They require service-specific federation setup, such as existing objects, ownership state, time-regulation state, save/restore state, or DDM regions. They are retained in the matrix as planned verification work rather than being hidden or made into artificial passes.

## Service-by-service conformance matrix

v0.13 adds `hla2010.verification.build_service_conformance_matrix`, derived from:

- generated Java/C++ API metadata in `hla2010.raw_api.API_METADATA`;
- section references in `hla2010.spec_refs`;
- pure-Python backend `_svc_*` entry points;
- FederateAmbassador helper methods;
- static evidence found in the test tree.

| Metric | Count |
|---|---:|
| Matrix rows | 217 |
| RTIambassador rows | 162 |
| FederateAmbassador rows | 55 |
| Reference-implemented and tested RTI rows | 93 |
| Reference-implemented but statically untested RTI rows | 69 |
| Callback-helper tested rows | 20 |
| Callback-helper untested rows | 35 |

The matrix files are:

```text
analysis/service_conformance_matrix_v0_13.json
analysis/service_conformance_matrix_v0_13.csv
analysis/service_conformance_summary_v0_13.md
```

Every row includes interface, service name, Python alias, section anchor, service group, source language coverage, source overload count, declared exceptions, implementation status, test evidence, negative-path evidence, and explicit gaps.

## Implementation notes

`hla2010.mom_catalog` now includes:

- `negative_case_expectation`;
- `flatten_negative_cases`;
- stable `MOM-NEG-####` case IDs;
- executable/semantic partitioning in `build_negative_matrix`.

The pure-Python RTI strict MOM payload validation was tightened for handle and handle-set parameters. It now rejects undecodable `HLAobjectClass`, `HLAinteractionClass`, `HLAobjectInstance`, `HLAtransportation`, `HLAattributeList`, `HLAfederateList`, and `HLAdimensionHandleSet` payloads before dispatching to service semantics.

## Remaining honest gaps

The next verification slice should target the 32 semantic HLAservice negative rows. Those tests need tailored federation preconditions rather than generic parameter decoding. The service-by-service conformance matrix also shows many services that have reference/subset implementations but no direct negative-path test evidence yet.
