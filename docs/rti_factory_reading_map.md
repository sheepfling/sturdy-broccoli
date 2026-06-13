# RTI Factory Reading Map

This is the shortest reading path for someone who wants to list installed RTI
factories, inspect the available selection names, and instantiate one cleanly.

If your real goal is “edit or debug the Python RTI,” use this page first to
choose the backend name, then continue into
[python_rti_reading_map.md](python_rti_reading_map.md).

Read these files in order:

1. [`tools/rti-factories`](../tools/rti-factories)
2. [`examples/rti_factory_selection.py`](../examples/rti_factory_selection.py)
3. [`scripts/rti_factories.py`](../scripts/rti_factories.py)
4. [`packages/hla2010-spec/src/hla2010/rti.py`](../packages/hla2010-spec/src/hla2010/rti.py)
5. [`packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/factory.py`](../packages/hla2010-rti-runtime-common/src/hla2010_rti_runtime_common/factory.py)
6. [`packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/plugin_api.py`](../packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/plugin_api.py)
7. One concrete plugin such as [`packages/hla2010-rti-python/src/hla2010_rti_python/plugin.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/plugin.py)

## Why These Files

- `tools/rti-factories`: canonical operator entrypoint
- `examples/rti_factory_selection.py`: smallest runnable Python example for list, select, and instantiate
- `scripts/rti_factories.py`: human-facing list/show formatting and probe output
- `hla2010/rti.py`: temporary root facade for selection helpers
- `runtime_common/factory.py`: installed factory registry, alias resolution, and ambassador creation
- `plugin_api.py`: the stable metadata contract for discovery rows and plugin descriptors
- one concrete plugin: where the selectable name, aliases, family, description, and `discover()` behavior actually come from

## Fastest Useful Commands

Run these before reading every backend package:

- `./tools/rti-factories list`
- `./tools/rti-factories show python`
- `./tools/rti-factories show in-memory --probe`
- `./tools/rti-factories instantiate in-memory --probe`
- `./tools/examples rti-factory-selection --name in-memory --probe`
- `./tools/human-editability front-doors rti-factories`

For the main development route in this repo, `python` and `in-memory` both
resolve to the pure Python RTI factory. After that selection is clear, continue
with the Python RTI map, or run the scenario directly through the alias:

```bash
source .venv/bin/activate
./tools/examples target-radar --backend in-memory --steps 5
```

## Python Usage Shape

```python
from hla2010.rti import get_rti_factory, iter_rti_factories

for factory in iter_rti_factories():
    print(factory.name, factory.selectable_names)

factory = get_rti_factory("in-memory")
rti = factory.create_rti_ambassador()
```

Use `iter_rti_factories()` when you want the canonical installed list. Use
`get_rti_factory(name)` when you want alias-tolerant selection. Use
`discover_rti_backends(probe=True)` only when you need the lower-level
discovery rows directly.

## What To Ignore First

Do not start by reading every vendor backend package or every entry point in
`pyproject.toml`. Start with the list/show flow and then open the concrete
plugin for the backend you care about.

## Read Next

1. [python_rti_reading_map.md](python_rti_reading_map.md)
2. [java_backends_quickstart.md](java_backends_quickstart.md)
