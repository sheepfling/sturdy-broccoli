# Create A Federate And FOM

This is the supported path for adding a new package-owned FOM and a new
federate workflow without touching RTI backend internals.

Start with the scaffold command:

```bash
./tools/new-fom-package your-demo
```

That creates the repo-native starter shape under:

- `packages/hla2010-fom-your-demo/`
- `examples/your_demo_demo.py`
- `tests/examples/test_your_demo_demo.py`

Use the scaffold first. Use the rest of this document to understand and refine
what it generated.

## 1. Where New FOM Packages Belong

The scaffold creates a split package under `packages/`:

```text
packages/hla2010-fom-your-demo/
  README.md
  pyproject.toml
  src/hla2010_fom_your_demo/
    __init__.py
    resources/foms/YourDemoFOMmodule.xml
    scenarios/__init__.py
    scenarios/your_demo.py
```

Use the existing package-backed examples as references:

- `packages/hla2010-fom-target-radar`
- `packages/hla2010-fom-minimal-demo`

## 2. Minimal Package Layout

The smallest supported layout is:

```text
packages/hla2010-fom-minimal-demo/
  README.md
  pyproject.toml
  src/hla2010_fom_minimal_demo/
    __init__.py
    resources/foms/MinimalDemoFOMmodule.xml
    scenarios/__init__.py
    scenarios/minimal_demo.py
```

## 3. Minimal FOM XML

The package-owned FOM resource lives under `resources/foms/` and resolves
through `importlib.resources`.

```python
from hla2010_fom_minimal_demo.scenarios import minimal_demo_fom_path
```

The minimal demo FOM defines:

- `HLAobjectRoot.DemoObject`
- attribute `Message`
- `HLAinteractionRoot.DemoAnnouncement`
- parameters `Sender` and `Message`

## 4. Minimal Publisher Federate

The publisher only uses ordinary public RTI calls:

```python
from hla2010.spec import FederateAmbassadorSpec


class PublisherFederate(FederateAmbassadorSpec):
    ...
```

The package-backed reference implementation is:

- `hla2010_fom_minimal_demo.scenarios.PublisherFederate`

It:

- gets object and interaction handles from the FOM
- publishes one object class and one interaction class
- registers one object instance
- sends one attribute update and one interaction

## 5. Minimal Subscriber Federate

The subscriber uses the same public RTI surface:

```python
from hla2010.spec import FederateAmbassadorSpec


class SubscriberFederate(FederateAmbassadorSpec):
    ...
```

The package-backed reference implementation is:

- `hla2010_fom_minimal_demo.scenarios.SubscriberFederate`

It:

- subscribes to the object class and interaction class
- records `discover_object_instance`
- records `reflect_attribute_values`
- records `receive_interaction`

## 6. Run With Python RTI

Bootstrap the workspace, then run the package-backed example:

```bash
./tools/bootstrap python
source .venv/bin/activate
./tools/examples minimal-fom-demo --backend in-memory
python examples/minimal_fom_demo.py --backend python
```

For the main development route in this repo, `in-memory` and `python` both
resolve to the same pure Python RTI factory. Use `in-memory` when you want the
example CLI to mirror the factory-selection flow from `./tools/rti-factories`.

The scenario helper entrypoints are:

```python
from hla2010_fom_minimal_demo.scenarios import (
    make_minimal_demo_factory,
    minimal_demo_fom_path,
    run_minimal_demo_scenario,
)
```

## 7. Add A Test

Use `tests/examples/test_minimal_fom_demo.py` as the reference guard.

The minimum checks are:

- packaged FOM path resolves through `importlib.resources`
- two federates can create, join, resign, and destroy against the Python RTI
- one object update reaches `reflect_attribute_values`
- one interaction reaches `receive_interaction`

## 8. Add Requirement Rows

Add requirement rows only for the public RTI services your example exercises.
Do not mark rows as mapped unless the evidence is concrete.

For a small FOM package, the typical services are:

- `createFederationExecution`
- `joinFederationExecution`
- `publishObjectClassAttributes`
- `subscribeObjectClassAttributes`
- `sendInteraction`
- `reflectAttributeValues`

## 9. Add Traceability Refs

If you add new requirement rows or proof assets:

- point implementation refs at the package-owned scenario modules
- point test refs at the exact pytest file or test name
- point artifact refs at generated outputs only

Use:

```bash
./tools/human-editability trace createFederationExecution
```

to verify the repo trace path conventions before you add new rows.

## 10. Optional: Run Through JPype Or Py4J Later

Do the Python RTI path first. After that, you can pass a different backend to
the same scenario factory:

```python
factory = make_minimal_demo_factory("jpype")
```

That is a later integration step, not part of the first-run or template
finish line.
