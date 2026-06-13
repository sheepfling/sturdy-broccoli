# Requirements Traceability

This repo treats traceability as an executable product, not a prose claim.

Use these operator commands first:

```bash
./tools/human-editability check
./tools/human-editability generate-trace-index
./tools/human-editability trace createFederationExecution
./tools/human-editability trace timeAdvanceRequest
```

Primary sources:

- `requirements/traceability_matrix.csv`
- `analysis/compliance/requirements_ledger.csv`
- `analysis/traceability/service_trace_index.csv`
- `analysis/traceability/service_trace_index.md`
- `analysis/traceability/service_trace_index.json`

## How To Read A Trace

For each service, trace in this order:

1. Requirement row
2. IEEE section
3. Python public method
4. Python RTI backend service or callback surface
5. Test evidence
6. Generated artifact evidence

The `./tools/human-editability trace <method>` command prints the same chain from the generated index when it exists, and falls back to the requirements ledger otherwise.

## Service Walkthroughs

### createFederationExecution

- Requirement row: `REQ-RTI-FM-4_5-createFederationExecution`
- Spec reference: `1516.1-2010 §4.5`
- Python public method: `createFederationExecution` / `create_federation_execution`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_createFederationExecution`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/scenarios/test_federation_lifecycle_backend_matrix.py`, `tests/scenarios/test_federation_management_backend_matrix.py`, `tests/factories/test_fom_time_factories.py`, `tests/scenarios/test_startup_sync_fom_java_translation_v09.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace createFederationExecution`

### joinFederationExecution

- Requirement row: `REQ-RTI-FM-4_9-joinFederationExecution`
- Spec reference: `1516.1-2010 §4.9`
- Python public method: `joinFederationExecution` / `join_federation_execution`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_joinFederationExecution`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/scenarios/test_federation_lifecycle_backend_matrix.py`, `tests/scenarios/test_federation_management_backend_matrix.py`, `tests/scenarios/test_startup_sync_fom_java_translation_v09.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace joinFederationExecution`

### timeAdvanceRequest

- Requirement row: `REQ-RTI-TM-8_8-timeAdvanceRequest`
- Spec reference: `1516.1-2010 §8.8`
- Python public method: `timeAdvanceRequest` / `time_advance_request`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_timeAdvanceRequest`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/time/test_mom_mim_time_v10.py`, `tests/time/test_mom_mim_and_time_semantics_v010.py`, `tests/verification/test_compliance_slice_v011.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace timeAdvanceRequest`

### reflectAttributeValues

- Requirement row: `REQ-FED-OM-6_11-reflectAttributeValues`
- Spec reference: `1516.1-2010 §6.11`
- Python public method: `reflectAttributeValues` / `reflect_attribute_values`
- Callback surface: `RecordingFederateAmbassador callback + snake_case alias`
- Implementation file: `packages/hla2010-spec/src/hla2010/ambassadors.py`
- Test evidence: `tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix`, `tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix`, `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_exchange_matrix`, `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace reflectAttributeValues`

### requestAttributeValueUpdate

- Requirement row: `REQ-RTI-OM-6_19-requestAttributeValueUpdate`
- Spec reference: `1516.1-2010 §6.19`
- Python public method: `requestAttributeValueUpdate` / `request_attribute_value_update`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_requestAttributeValueUpdate`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/scenarios/test_object_management_backend_matrix.py`, `tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix`, `tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_routing_matrix`, `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix`, `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_routing_matrix`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace requestAttributeValueUpdate`

### timeAdvanceGrant

- Requirement row: `REQ-FED-TM-8_13-timeAdvanceGrant`
- Spec reference: `1516.1-2010 §8.13`
- Python public method: `timeAdvanceGrant` / `time_advance_grant`
- Callback surface: `RecordingFederateAmbassador callback + snake_case alias`
- Implementation file: `packages/hla2010-spec/src/hla2010/ambassadors.py`
- Test evidence: `tests/verification/test_spec_traceability_and_extended_python_rti.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace timeAdvanceGrant`

## Generated Artifacts

Run this whenever traceability sources change:

```bash
./tools/human-editability generate-trace-index
```

That command validates active traceability inputs, then regenerates:

- `analysis/traceability/service_trace_index.csv`
- `analysis/traceability/service_trace_index.md`
- `analysis/traceability/service_trace_index.json`

## Validation Rules

Active traceability files must satisfy these rules:

- implementation refs resolve to a real file, symbol anchor, or explicit generated/external marker
- test refs resolve to a real file or `file.py::anchor`
- artifact refs resolve to a real artifact
- stale backend-root paths such as `hla2010/backends/python/...` are forbidden in active traceability files
- `mapped` rows must carry concrete test or artifact evidence
- `partial` rows must state the supported boundary explicitly

The enforcement entrypoint is:

```bash
python3 scripts/validate_traceability_paths.py check
```
