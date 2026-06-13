# Requirements Traceability

This repo treats traceability as an executable product, not a prose claim.

If you only need to trace one method end to end, start with
[`requirements_trace_one_method.md`](requirements_trace_one_method.md).

If you only need to fix one missed or wrong active mapping row, start with
[`requirements_edit_one_row.md`](requirements_edit_one_row.md).

Use this page for:

- the broader traceability model
- the meaning of generated trace artifacts
- the requirement -> implementation -> test -> artifact chain

Do not use this page for:

- the shortest one-method trace workflow
- the shortest one-row authoring loop
- deciding which requirement files are active versus generated versus reference

Those narrower lanes already live in:

- [`requirements_trace_one_method.md`](requirements_trace_one_method.md)
- [`requirements_edit_one_row.md`](requirements_edit_one_row.md)
- [`requirements_authoring_map.md`](requirements_authoring_map.md)
- [`../requirements/README.md`](../requirements/README.md)

Use these operator commands first:

```bash
./tools/human-editability check
./tools/human-editability generate-trace-index
./tools/human-editability trace createFederationExecution
./tools/human-editability trace timeAdvanceRequest
```

## Trace Model

For each service, trace in this order:

1. requirement row
2. IEEE clause
3. public method
4. backend service or callback surface
5. focused test evidence
6. generated artifact evidence

The `./tools/human-editability trace <MethodName>` command prints the same
chain from the generated service trace index when it exists and falls back to
the requirements ledger otherwise.

For the shortest maintainer path, use:

```bash
./tools/human-editability front-doors requirements-trace
./tools/human-editability trace getHLAversion
```

That lane owns the concrete "trace one method" workflow.

## Primary Surfaces

Traceability depends on a small set of surfaces:

- active authored: `requirements/traceability_matrix.csv`
- generated ledger: `analysis/compliance/requirements_ledger.csv`
- generated service trace index:
  `analysis/traceability/service_trace_index.csv`,
  `analysis/traceability/service_trace_index.md`,
  `analysis/traceability/service_trace_index.json`

Treat the generated ledger and trace indexes as outputs. The normal human edit
surface for active mapping work is `requirements/traceability_matrix.csv`.

## Full-Chain Walkthroughs

### createFederationExecution

- Requirement row: `REQ-RTI-FM-4_5-createFederationExecution`
- Spec reference: `1516.1-2010 §4.5`
- Python public method: `createFederationExecution` / `create_federation_execution`
- Backend service: `hla2010_rti_python.backend.PythonRTIBackend._svc_createFederationExecution`
- Implementation file: `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
- Test evidence: `tests/scenarios/test_federation_lifecycle_backend_matrix.py`, `tests/scenarios/test_federation_management_backend_matrix.py`, `tests/factories/test_fom_time_factories.py`
- Artifact evidence: `analysis/compliance/service_conformance.json`
- Trace command: `./tools/human-editability trace createFederationExecution`

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
3. [`requirements_authoring_map.md`](requirements_authoring_map.md)
4. [`../requirements/README.md`](../requirements/README.md)
