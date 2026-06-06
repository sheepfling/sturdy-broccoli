# v0.12 MOM catalog and verification assets

This release slice moves MOM/MIM handling away from handwritten name tables and into a catalog-derived exposure model built from the active merged FDD. The pure Python RTI still remains a development/reference RTI, not a certification claim.

## Section anchors

| Area | Section anchor | v0.12 implementation evidence |
|---|---:|---|
| MOM object exposure | 1516.1-2010 §11.2 | `MOMObjectClassRule` rows derived from `FOMCatalog.object_classes`; MOM object attribute reflections are filtered to the active catalog. |
| MOM interaction direction | 1516.1-2010 §11.3 | `MOMInteractionRule.rti_direction` marks RTI-received adjust/request/service leaves and RTI-sent report leaves. Strict mode rejects federate-sent report interactions. |
| MOM adjust/request/service parameters | 1516.1-2010 §11.4.1 | Required parameters, at-least-one switch groups, request/report pairing, and representative payload datatype checks come from `hla2010.mom_catalog`. |
| Service reporting and diagnostics | 1516.1-2010 §11.5 | MOM exceptions and service-invocation reports are generated through catalog-filtered report payloads. Service report files remain JSONL for auditable development. |
| Standard MIM basis | 1516.1-2010 Annex G | The bundled `HLAstandardMIM.xml` is parsed and merged before user FOM modules. |

## Table-driven MOM model

Current Target/Radar + standard-MIM catalog counts:

| Metric | Count |
|---|---:|
| MOM object classes | 3 |
| MOM interaction classes | 84 |
| request/report pairs | 13 |
| RTI-received leaf interactions | 53 |
| generated negative-case rows | 269 |

The generated model is available as `analysis/mom_table_summary_v0_12.json`. The generated negative-path planning matrix is available as `analysis/mom_negative_matrix_v0_12.json` and `verification/mom_negative_matrix_v0_12.json`.

## Representative RTI-received MOM rows

| Interaction | Role | Parameters | Negative-case specs |
|---|---:|---:|---:|
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAmodifyAttributeState` | HLAadjust | 4 | 7 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetExceptionReporting` | HLAadjust | 2 | 5 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetServiceReporting` | HLAadjust | 2 | 5 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetSwitches` | HLAadjust | 3 | 5 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.HLAsetTiming` | HLAadjust | 2 | 5 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData` | HLArequest | 2 | 4 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsReceived` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsSent` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation` | HLArequest | 2 | 5 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesReflected` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesThatCanBeDeleted` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesUpdated` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestReflectionsReceived` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestUpdatesSent` | HLArequest | 1 | 3 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAchangeAttributeOrderType` | HLAservice | 4 | 9 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAchangeInteractionOrderType` | HLAservice | 3 | 7 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdeleteObjectInstance` | HLAservice | 4 | 7 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdisableAsynchronousDelivery` | HLAservice | 1 | 4 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdisableTimeConstrained` | HLAservice | 1 | 4 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAdisableTimeRegulation` | HLAservice | 1 | 4 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAenableAsynchronousDelivery` | HLAservice | 1 | 4 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAenableTimeConstrained` | HLAservice | 1 | 4 |
| `HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.HLAenableTimeRegulation` | HLAservice | 2 | 6 |

## Strict negative-path behavior added

Strict MOM mode, enabled with `PythonRTIConfig(strict_mom_parameter_decoding=True)`, now covers:

- unknown parameter handles and unexpected parameter names;
- missing required parameters such as `HLAreportPeriod` on `HLAsetTiming`;
- `HLAsetSwitches` at-least-one declared switch choice;
- invalid boolean-style payloads for parameters such as `HLAreportingState`;
- federate attempts to send RTI-sent report interactions.

In each strict failure path, the RTI queues a `HLAreportMOMexception` diagnostic and raises the closest available Python RTI exception. Non-strict mode keeps the development-friendly behavior used by the existing examples and Java shim paths.

## Verification asset summary

| Status | Count |
|---|---:|
| gap | 1 |
| implemented-slice | 8 |
| implemented-smoke | 1 |
| planned | 1 |


## Verification asset register

| Asset ID | Type | Status | Section anchors | Gaps / caveats |
|---|---|---|---|---|
| `REQ-MOM-TABLE-001` | requirement | implemented-slice | 1516.1-2010 §11.2, 1516.1-2010 §11.3, 1516.1-2010 Annex G | — |
| `REQ-MOM-NEG-001` | requirement | implemented-slice | 1516.1-2010 §11.4.1, 1516.1-2010 §11.5 | The generated matrix is complete for planning, but the executable suite samples representative cases rather than every generated row. |
| `REQ-MOM-REPORT-001` | requirement | implemented-slice | 1516.1-2010 §11.3, 1516.1-2010 §11.4.1, 1516.1-2010 Annex G | Report payload values are still local-process diagnostics for several specialized report classes. |
| `REQ-MOM-SERVICE-001` | requirement | implemented-slice | 1516.1-2010 §11.3, 1516.1-2010 §11.4.1 | Not every Annex G service action has a complete semantic implementation yet. |
| `REQ-SERVICE-FILE-001` | requirement | implemented-slice | 1516.1-2010 §11.5 | The current format is JSONL for auditability; exact vendor/report-file formatting is not claimed. |
| `REQ-TIME-ORDER-001` | requirement | implemented-slice | 1516.1-2010 §8.1, 1516.1-2010 §8.13, 1516.1-2010 §8.16, 1516.1-2010 §8.18, 1516.1-2010 §9 | The distributed-time algorithm remains a local-process approximation, not a proven multi-process LBTS algorithm. |
| `REQ-SAVE-RESTORE-001` | requirement | implemented-slice | 1516.1-2010 §4.16-§4.25, 1516.1-2010 §8 | External persistent save-file interchange is not implemented. |
| `SCENARIO-TARGET-RADAR-001` | scenario | implemented-smoke | 1516.1-2010 §4, 1516.1-2010 §5, 1516.1-2010 §6, 1516.1-2010 §8 | Scenario is a smoke demonstration, not a conformance test. |
| `ASSET-CONFORMANCE-MATRIX-001` | planned-artifact | planned | 1516.1-2010 §4-§10 | Needs expected exception/state transitions for every service overload. |
| `ASSET-CROSS-RTI-BRIDGE-001` | planned-artifact | gap | 1516.1-2010 Java binding, 1516.1-2010 §4-§10 | No vendor RTI, jpype1, or py4j package is available in this sandbox. |
| `ASSET-NEGATIVE-MOM-MATRIX-001` | planned-artifact | implemented-slice | 1516.1-2010 §11.4.1, 1516.1-2010 Annex G | The matrix is generated; exhaustive parameterized execution remains the next verification slice. |

## Honest progress notes

The v0.12 verification plan deliberately includes gap and planned assets. The biggest open items are exhaustive generated negative tests for every MOM row, deeper report payload semantics, real JPype/Py4J vendor RTI parity testing, and a service-by-service conformance matrix for every generated ambassador method.

## Validation run

```text
66 passed, 2 skipped
Target/Radar smoke scenario passed over python, java-shim-jpype, and java-shim-py4j.
```
