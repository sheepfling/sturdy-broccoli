# hla2010-fom-minimal-demo

Minimal packaged FOM and two-federate scenario helpers for the `hla2010`
workspace.

This package owns:

- the packaged `MinimalDemoFOMmodule.xml` resource
- a tiny publisher/subscriber scenario under `hla2010_fom_minimal_demo`
- a copyable example of how to add one FOM package without touching backend
  internals
- split-package guard coverage in
  `tests/examples/test_minimal_fom_demo.py`

Import the canonical implementation from `hla2010_fom_minimal_demo`.

Use this package when you want:

- the smallest package-backed FOM example in the repo
- a reference layout for `resources/foms` plus `scenarios`
- a tutorial-sized scenario that runs against the Python RTI first

This package depends on `hla2010-spec` and `hla2010-rti-runtime-common`. It
does not own RTI backend implementations or a package-local command. The human
operator surface stays the repo-level example
[`examples/minimal_fom_demo.py`](../../examples/minimal_fom_demo.py).

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Then run the minimal example:

```bash
python examples/minimal_fom_demo.py --backend python
```

If you are extending the template, the useful imports are:

```python
from hla2010_fom_minimal_demo.scenarios import (
    make_minimal_demo_factory,
    minimal_demo_fom_path,
    run_minimal_demo_scenario,
)
```

The package-local docs page is [`docs/README.md`](docs/README.md), and the
broader tutorial is [`../../docs/create_federate_and_fom.md`](../../docs/create_federate_and_fom.md).
