# Python Route Wrapping Guide

Use this guide when you want the Python 2010 and 2025 routes to look as close
to each other as possible.

## What To Open

For the smallest edition-specific examples:

- `examples/python_rti_2010_minimal.py`
- `examples/python_rti_2025_minimal.py`

For one runnable example that switches editions with one flag:

- `examples/python_route_federate.py`

## Route Matrix

| Edition | Minimal example | Factory import | Default backend |
| --- | --- | --- | --- |
| 2010 | `examples/python_rti_2010_minimal.py` | `hla.runtime.factory.create_rti_ambassador` | `python1516e` |
| 2025 | `examples/python_rti_2025_minimal.py` | `hla.runtime.rti1516_2025_factory.create_rti_ambassador` | `python1516_2025` |

The runnable example covers the same matrix:

```bash
python examples/python_route_federate.py --edition 2010
python examples/python_route_federate.py --edition 2025
```

## Keep The Shapes The Same

If you want wrapping code to stay easy to compare, keep the structure identical
between editions:

1. import the edition-specific factory
2. import the edition-specific `NullFederateAmbassador`
3. subclass the ambassador and implement lowerCamelCase callbacks
4. create the RTI with the edition-default backend
5. connect the federate

2010:

```python
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel
```

2025:

```python
from hla.runtime.rti1516_2025_factory import create_rti_ambassador
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador
from hla.rti1516_2025.enums import CallbackModel
```

The only intentional differences are:

- the package root: `hla.rti1516e` vs `hla.rti1516_2025`
- the factory import path
- the default backend string

## Practical Guidance

Use the 2010 route when you need the existing 1516e surface and established
examples.

Use the 2025 route when you need the newer IEEE 1516.1-2025 surface and the
native `python1516_2025` runtime.

If you are writing wrappers or integration code that should support both, start
from `examples/python_route_federate.py` and keep all edition branching at the
factory/import edge.

## Recommended Reading Order

1. `examples/python_route_federate.py`
2. `examples/python_rti_2010_minimal.py`
3. `examples/python_rti_2025_minimal.py`
4. `docs/create_federate_and_fom.md`
