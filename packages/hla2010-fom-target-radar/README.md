# hla2010-fom-target-radar

Concrete Target/Radar FOM and scenario package for the `hla2010` workspace.

This package now owns:

- the packaged `TargetRadarFOMmodule.xml` resource
- reusable target/radar scenario helpers
- target/radar example runner factory helpers
- target/radar backend-matrix and proof artifact generators
- target/radar-owned two-federate suite helper slices
- target/radar-owned two-federate suite artifact formatting
- target/radar-owned two-federate vendor profile policy

Import the canonical implementation from `hla2010_fom_target_radar`; the old
root-level `hla2010.scenarios.target_radar` compatibility path has been
removed.

Use this package when you want:

- the bundled Target/Radar FOM path
- a reusable scenario runner for the example
- a backend factory that can target local Python, JPype, Py4J, or the split
  runtime helper defaults
- a stable place to extend the example without touching the generic HLA
  interface package

This package depends on `hla2010-spec` and may optionally be combined with
backend plugin packages for runnable examples, but it does not own RTI backend
implementations.
Split-package guard coverage lives in
`tests/test_fom_target_radar_split_package.py`.

The human operator surface for Target/Radar stays `./tools/target-radar`; this
package does not add a package-local command.

## Start Here

Use this package when you want to extend the example itself without touching
generic spec code or backend internals.

Shortest path:

1. open `src/hla2010_fom_target_radar/scenarios/`
2. open the packaged FOM resource and scenario helpers together
3. run the example or proof wrapper before changing backend-facing code

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Then run the scenario entrypoints. Full install order lives in
[`../../docs/python_environment.md`](../../docs/python_environment.md).

If you are extending the example, the useful imports are:

```python
from hla2010_fom_target_radar.scenarios import (
    make_target_radar_factory,
    run_target_radar_scenario,
    target_radar_fom_path,
)
```

The package-local docs page is
[`docs/README.md`](docs/README.md), and the broader walkthrough is in
[`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md).

## Read Next

1. [`../../docs/create_federate_and_fom.md`](../../docs/create_federate_and_fom.md)
2. [`docs/README.md`](docs/README.md)
3. [`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md)
