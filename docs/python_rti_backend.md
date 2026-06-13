# Python RTI Backend

The Python RTI is the primary development backend in this repo.

Use it when you want:

- the fastest local RTI path
- a dependency-free backend for new services and scenarios
- the first verification lane for a new federate or FOM package

## Package Location

The backend lives in:

- `packages/hla2010-rti-python/src/hla2010_rti_python/`

The stable service registry lives in:

- `packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`

The generated contributor-facing service maps live in:

- `analysis/traceability/python_rti_service_map.csv`
- `analysis/traceability/python_rti_service_map.json`
- `analysis/traceability/python_rti_service_map.md`

## How Dispatch Works

`DelegatingRTIAmbassador` forwards each HLA method into `PythonRTIBackend.invoke()`.

`PythonRTIBackend.invoke()` then resolves:

- `_svc_<HLA method name>`

Example:

- `timeAdvanceRequest`
- `PythonRTIBackend.invoke()`
- `PythonRTITimePublicServicesMixin._svc_timeAdvanceRequest`
- `packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py`

## Service Domains

The Python RTI service mixins are grouped by domain:

- `federation_creation.py`
- `federation_membership.py`
- `federation_sync.py`
- `save_restore_services.py`
- `declaration.py`
- `object.py`
- `object_delivery_attributes.py`
- `object_delivery_control.py`
- `object_delivery_interactions.py`
- `ownership_services.py`
- `time_public_services.py`
- `ddm_services.py`
- `support_control.py`
- `support_lookup.py`
- `support_factories.py`
- `callbacks.py`

## How To Find A Service

Use:

```bash
./tools/human-editability generate-python-rti-map
./tools/human-editability trace requestAttributeValueUpdate
```

That trace path now prints the exact implementation symbol and file from the
generated Python RTI service map.

## How To Add A Service

1. Add or update the `_svc_<MethodName>` implementation in the right domain mixin.
2. Regenerate the registry and service maps.
3. Add or update requirement evidence in `analysis/compliance/requirements_ledger.csv` inputs.
4. Verify the trace command resolves to the new implementation.

Commands:

```bash
python3 scripts/generate_python_rti_service_map.py generate
python3 scripts/generate_python_rti_service_map.py check
./tools/human-editability trace createFederationExecution
```

## How To Test A Service

Use targeted backend tests first, then scenario or verification slices.

Examples:

```bash
python3 -m pytest tests/backends/test_python_rti_service_registry.py
python3 -m pytest tests/test_python_api_spec.py
./tools/human-editability trace timeAdvanceRequest
```

## How To Run It

Direct Python RTI path:

```bash
./tools/bootstrap python
source .venv/bin/activate
python examples/target_radar_simulation.py --backend python --steps 5
```

Hosted over gRPC:

- use the same Python backend package first
- then use the gRPC transport package after the direct in-memory path is green

## Traceability Link

The Python RTI backend is part of the active requirement trace chain:

- requirement row
- Python public RTI method
- Python RTI `_svc_*` implementation
- tests
- generated artifacts

Start with:

```bash
./tools/human-editability trace createFederationExecution
./tools/human-editability trace requestAttributeValueUpdate
./tools/human-editability trace timeAdvanceRequest
```
