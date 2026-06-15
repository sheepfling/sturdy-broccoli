# Spec Reading Map

This is the shortest reading path for the abstract/public HLA surface.

Read these files in order:

1. [`packages/hla2010-spec/src/hla2010/spec/__init__.py`](../packages/hla2010-spec/src/hla2010/spec/__init__.py)
2. [`packages/hla2010-spec/src/hla2010/runtime_api.py`](../packages/hla2010-spec/src/hla2010/runtime_api.py)
3. [`packages/hla2010-spec/src/hla2010/ambassadors.py`](../packages/hla2010-spec/src/hla2010/ambassadors.py)
4. [`packages/hla2010-spec/src/hla2010/spec_inventory.py`](../packages/hla2010-spec/src/hla2010/spec_inventory.py)
5. [`packages/hla2010-spec/src/hla2010/spec_refs.py`](../packages/hla2010-spec/src/hla2010/spec_refs.py)
6. [`specs/hla2010_api.json`](../specs/hla2010_api.json)

## Why These Files

- `spec/__init__.py`: clean abstract interface front door
- `runtime_api.py`: Python-facing runtime aliases over the snake_case spec surface
- `ambassadors.py`: explicit callback surface and recording ambassador helpers
- `spec_inventory.py`: method inventory without generator noise
- `spec_refs.py`: IEEE section and source-reference lookup helpers
- `specs/hla2010_api.json`: authored metadata source for generated spec artifacts

## What To Ignore First

Do not start with these unless you are changing generator behavior or deep FOM parsing:

- `packages/hla2010-spec/src/hla2010/raw_api.py`
- `packages/hla2010-spec/src/hla2010/resources/api_metadata.json`
- `packages/hla2010-spec/src/hla2010/_spec_impl.py`
- `packages/hla2010-spec/src/hla2010/fom.py`

Those files are valid, but they are not the best first read for a contributor
trying to understand the public surface.

## Common Tasks

- Add or change spec metadata:
  Edit [`specs/hla2010_api.json`](../specs/hla2010_api.json), then run `./tools/spec-api generate` and `./tools/spec-api check`.
- Find the public method for a requirement row:
  Start with [`spec_refs.py`](../packages/hla2010-spec/src/hla2010/spec_refs.py) and [`docs/requirements_traceability.md`](requirements_traceability.md).
- Understand the callback contract:
  Start with [`ambassadors.py`](../packages/hla2010-spec/src/hla2010/ambassadors.py).

## Read Next

1. [python_rti_reading_map.md](python_rti_reading_map.md)
2. [requirements_authoring_map.md](requirements_authoring_map.md)
