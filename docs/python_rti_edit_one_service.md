# Edit One Python RTI Service

This is the shortest contributor path for changing one Python RTI service
without first reading the whole backend.

Use this when your goal is:

- find one public RTI method
- find the real Python RTI implementation
- make one behavior change
- run one focused verification slice
- confirm the requirement trace still points at the right code

If you first need to choose which backend to use, stop here and read
[rti_factory_reading_map.md](rti_factory_reading_map.md). The normal edit path
in this repo is the `python` / `in-memory` backend.

## The Smallest Service Chain

For one RTI service, read and verify this chain in order:

1. public runtime method in `packages/hla2010-spec/src/hla2010/runtime_api.py`
2. backend dispatch in `packages/hla2010-rti-python/src/hla2010_rti_python/backend.py`
3. generated registry row in `packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`
4. owning `_svc_*` implementation in the domain mixin
5. targeted test slice
6. trace command output

That is the only chain you need for a normal service edit.

## Recommended First Example

Start with `getHLAversion`.

It is the smallest end-to-end service because it:

- has a public runtime method
- has a registry entry
- has a real Python RTI implementation
- has direct focused tests
- does not require federation setup to understand the edit path

Find it with:

```bash
./tools/human-editability trace getHLAversion
```

Then open:

1. `packages/hla2010-spec/src/hla2010/runtime_api.py`
2. `packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`
3. `packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py`
4. `tests/backends/test_python_rti_service_registry.py`

## Stateful Example

After that, use `timeAdvanceRequest` when you want a real stateful service.

Find it with:

```bash
./tools/human-editability trace timeAdvanceRequest
./tools/human-editability trace-summary timeAdvanceRequest
```

That lands on:

- public runtime method: `time_advance_request`
- HLA service key: `timeAdvanceRequest`
- registry row in `service_registry.py`
- implementation in `packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py`
- requirement and test evidence from the generated trace

## Edit Loop

Use this exact loop:

1. Confirm you are on the intended backend path.
2. Find the service with `./tools/human-editability trace <MethodName>`.
3. Edit the owning `_svc_*` method in the domain mixin.
4. If the service inventory changed, regenerate and check the registry outputs.
5. Run one focused backend test slice.
6. Run the trace command again and confirm it still lands on the right code.

Commands:

```bash
./tools/rti-factories show in-memory --probe
./tools/human-editability trace getHLAversion
python3 scripts/generate_python_rti_service_map.py check
python3 -m pytest tests/backends/test_python_rti_service_registry.py -q
./tools/human-editability trace getHLAversion
```

For a stateful service:

```bash
./tools/human-editability trace timeAdvanceRequest
python3 scripts/generate_python_rti_service_map.py check
python3 -m pytest tests/test_python_api_spec.py tests/backends/test_python_rti_service_registry.py -q
./tools/human-editability trace timeAdvanceRequest
```

## What To Edit

In the normal case, edit only:

- the owning `_svc_*` method in the domain mixin
- nearby plain helper methods that service already uses
- focused tests for that service family

Do not start by editing:

- generated files under `analysis/traceability/`
- generated `service_registry.py` entries by hand
- unrelated mixins in other service domains
- Java or vendor backends

## When To Regenerate

Run the generator when you change service inventory or ownership, not for every
ordinary logic edit.

Use:

```bash
python3 scripts/generate_python_rti_service_map.py generate
python3 scripts/generate_python_rti_service_map.py check
```

Examples that require regeneration:

- new RTI method added
- service moved to a different mixin
- implementation symbol changed

Examples that usually do not:

- logic change inside an existing `_svc_*` method
- new focused tests
- new helper function called by an existing service

## Requirement Trace Back

The canonical human path is:

```bash
./tools/human-editability trace <MethodName>
```

That should give you:

- requirement id
- spec section
- Python public method
- Python RTI implementation symbol and file
- focused test evidence
- artifact evidence

If that command does not tell you where to edit, the repo is still too hard to
work in.

## Read Next

1. [python_rti_backend.md](python_rti_backend.md)
2. [python_rti_reading_map.md](python_rti_reading_map.md)
3. [requirements_traceability.md](requirements_traceability.md)
