# Requirements Traceability

This repo treats traceability as an executable product, not a prose claim.

The traceability model is edition-selectable in structure, but the current
selected requirement document set is `2010` only. In normal maintenance, treat
2010-edition document titles and clause references as the active truth and only
introduce other editions when changing the registry structure deliberately.

Use this page for the broad model:

- what the generated service trace index means
- how requirement -> implementation -> test -> artifact chains are expected to look
- what validation rules keep the mapping honest

Do not start here if you only need one narrow task. Use:

- [`requirements_trace_one_method.md`](requirements_trace_one_method.md)
- [`requirements_edit_one_row.md`](requirements_edit_one_row.md)
- [`../requirements/README.md`](../requirements/README.md)

Use these operator commands first:

<!-- GENERATED:TRACEABILITY_OPERATOR_COMMANDS:START -->
```bash
./tools/human-editability check
./tools/human-editability generate-trace-index
./tools/human-editability trace-summary createFederationExecution
./tools/human-editability trace-summary timeAdvanceRequest
./tools/human-editability trace createFederationExecution
./tools/human-editability trace timeAdvanceRequest
```
<!-- GENERATED:TRACEABILITY_OPERATOR_COMMANDS:END -->

## Trace Model

For each service, trace in this order:

1. requirement row
2. IEEE clause
3. public method
4. backend service or callback surface
5. focused test evidence
6. generated artifact evidence

The `./tools/human-editability trace <MethodName>` command prints that chain
from the generated service trace index when it exists and falls back to the
requirements ledger otherwise.

## Primary Surfaces

Traceability depends on a small set of surfaces:

<!-- GENERATED:TRACEABILITY_PRIMARY_SURFACES:START -->
- active authored: `requirements/active_service_rows.csv` is the normal human edit surface
- generated compatibility merge: `requirements/traceability_matrix.csv`
- generated ledger: `analysis/compliance/requirements_ledger.csv`
- generated service trace index: `analysis/traceability/service_trace_index.csv`, `analysis/traceability/service_trace_index.md`, `analysis/traceability/service_trace_index.json`
<!-- GENERATED:TRACEABILITY_PRIMARY_SURFACES:END -->

<!-- GENERATED:TRACEABILITY_EDIT_RULE:START -->
- Treat `requirements/active_service_rows.csv` as the normal human edit surface.
- Treat `requirements/traceability_matrix.csv`, the ledger, and the trace indexes as generated outputs.
<!-- GENERATED:TRACEABILITY_EDIT_RULE:END -->

## Full-Chain Walkthroughs

### createFederationExecution

- Requirement row: `REQ-RTI-FM-4_5-createFederationExecution`
- Spec reference: `IEEE 1516.1-2010 (2010 edition) §4.5`
- Python public method: `create_federation_execution`
- HLA service key: `createFederationExecution`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_createFederationExecution`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/scenarios/test_federation_lifecycle_backend_matrix.py`, `tests/scenarios/test_federation_management_backend_matrix.py`, `tests/factories/test_fom_time_factories.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace createFederationExecution`

### timeAdvanceRequest

- Requirement row: `REQ-RTI-TM-8_8-timeAdvanceRequest`
- Spec reference: `IEEE 1516.1-2010 (2010 edition) §8.8`
- Python public method: `time_advance_request`
- HLA service key: `timeAdvanceRequest`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_timeAdvanceRequest`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/time/test_mom_mim_time_v10.py`, `tests/time/test_mom_mim_and_time_semantics_v010.py`, `tests/verification/test_compliance_slice_v011.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace timeAdvanceRequest`

### reflectAttributeValues

- Requirement row: `REQ-FED-OM-6_11-reflectAttributeValues`
- Spec reference: `IEEE 1516.1-2010 (2010 edition) §6.11`
- Python public method: `reflectAttributeValues` / `reflect_attribute_values`
- Callback surface: `RecordingFederateAmbassador callback + snake_case alias`
- Implementation file: `packages/hla2010-spec/src/hla2010/ambassadors.py`
- Test evidence: `tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix`, `tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace reflectAttributeValues`

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

## Read Next

1. [`requirements_trace_one_method.md`](requirements_trace_one_method.md)
2. [`requirements_edit_one_row.md`](requirements_edit_one_row.md)
3. [`../requirements/README.md`](../requirements/README.md)
4. [`requirements_authoring_map.md`](requirements_authoring_map.md)
