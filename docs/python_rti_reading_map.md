# Python RTI Reading Map

This is the shortest reading path for someone who wants to change or add Python
RTI behavior.

If you only want to change one service, use
[python_rti_edit_one_service.md](python_rti_edit_one_service.md) instead of
this broader map.

If you first need to decide which installed backend/factory name to use, stop
here and read [rti_factory_reading_map.md](rti_factory_reading_map.md) first.
The normal development choice is the `python` / `in-memory` factory.

Read these files in order:

1. [`docs/python_rti_backend.md`](python_rti_backend.md)
2. [`packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/backend.py)
3. [`packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py)
4. [`analysis/traceability/python_rti_service_map.md`](../analysis/traceability/python_rti_service_map.md)
5. One domain mixin such as [`packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py)
6. [`packages/hla2010-rti-python/src/hla2010_rti_python/state.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/state.py)

## Why These Files

- `python_rti_backend.md`: operator and contributor overview
- `backend.py`: backend entrypoint and invocation flow
- `service_registry.py`: stable method-to-implementation lookup
- `python_rti_service_map.md`: generated traceable service inventory
- one domain mixin: where you actually implement the service
- `state.py`: federation and federate state model

## Edit Loop

When adding or changing a service:

0. Confirm you are on the intended backend path with `./tools/rti-factories show in-memory --probe`.
1. Find the HLA method in [`service_registry.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py).
2. Edit the owning `_svc_*` implementation in the domain module.
3. Run `python3 scripts/generate_python_rti_service_map.py check`.
4. Run `./tools/human-editability trace <MethodName>`.
5. Run the targeted backend or scenario tests.

For the smaller task-focused version of that loop, run:

```bash
./tools/human-editability front-doors python-rti-service
```

## What To Ignore First

Do not start by reading every Python RTI module. Start with one service chain.

For example:

- `timeAdvanceRequest`
- `requestAttributeValueUpdate`
- `createFederationExecution`

Use `./tools/human-editability trace <MethodName>` to land on the exact file
before expanding into adjacent modules.

## Read Next

1. [python_rti_edit_one_service.md](python_rti_edit_one_service.md)
2. [rti_factory_reading_map.md](rti_factory_reading_map.md)
3. [create_federate_and_fom.md](create_federate_and_fom.md)
4. [requirements_authoring_map.md](requirements_authoring_map.md)
