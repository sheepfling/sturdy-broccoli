# FOM Reading Map

This is the shortest reading path for contributors working on FOM parsing,
merge behavior, datatype validation, or OMT serialization.

Read these files in order:

1. [`packages/hla2010-spec/src/hla2010/fom.py`](../packages/hla2010-spec/src/hla2010/fom.py)
2. [`packages/hla2010-spec/src/hla2010/_fom_parsing.py`](../packages/hla2010-spec/src/hla2010/_fom_parsing.py)
3. [`packages/hla2010-spec/src/hla2010/_fom_merge.py`](../packages/hla2010-spec/src/hla2010/_fom_merge.py)
4. [`packages/hla2010-spec/src/hla2010/_fom_datatypes.py`](../packages/hla2010-spec/src/hla2010/_fom_datatypes.py)
5. [`packages/hla2010-spec/src/hla2010/_fom_serialization.py`](../packages/hla2010-spec/src/hla2010/_fom_serialization.py)
6. [`packages/hla2010-spec/src/hla2010/_fom_models.py`](../packages/hla2010-spec/src/hla2010/_fom_models.py)
7. [`tests/factories/test_fom_omt_parsing.py`](../tests/factories/test_fom_omt_parsing.py)

## Why These Files

- `fom.py`: public front door, standard MIM helpers, resolver, and exported parse/merge surface
- `_fom_parsing.py`: XML parsing, schema validation, model extraction, and semantic validation
- `_fom_merge.py`: FOM and MIM catalog merge rules
- `_fom_datatypes.py`: encoded datatype validation and structured payload consumption
- `_fom_serialization.py`: strict OMT XML serialization for the implemented subset
- `_fom_models.py`: dataclasses and structured model/spec shapes used by the rest of the subsystem
- `test_fom_omt_parsing.py`: parser, validator, merge, schema, and round-trip regression contract

## Edit Here For

- Parse a new OMT element or validation rule:
  Start with `_fom_parsing.py`.
- Change merge behavior across FOM modules:
  Start with `_fom_merge.py`.
- Change encoded datatype validation:
  Start with `_fom_datatypes.py`.
- Change OMT XML output shape:
  Start with `_fom_serialization.py`.
- Change the public entrypoint or standard MIM convenience behavior:
  Start with `fom.py`.

## What To Ignore First

Do not start with these unless you are debugging a specific backend consumer or
generated artifact:

- `analysis/traceability/service_trace_index.md`
- `analysis/compliance/requirements_ledger.csv`
- backend mixins under `packages/hla2010-rti-python/src/hla2010_rti_python/`

Those are useful later, but they are not the best first read when the task is
to understand or edit FOM behavior.

## Verification Loop

Use this focused loop while editing the FOM subsystem:

1. run `python3 -m pytest tests/factories/test_fom_omt_parsing.py -q`
2. run `python3 -m pytest tests/factories/test_fom_time_factories.py tests/test_fom_target_radar_split_package.py tests/examples/test_minimal_fom_demo.py -q`
3. run `./tools/human-editability front-doors fom`

## Read Next

1. [spec_reading_map.md](spec_reading_map.md)
2. [python_rti_reading_map.md](python_rti_reading_map.md)
3. [requirements_authoring_map.md](requirements_authoring_map.md)
