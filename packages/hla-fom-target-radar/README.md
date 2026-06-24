# hla-fom-target-radar

## What This Is

`hla-fom-target-radar` is the concrete Target/Radar FOM and example-support
package.

It owns the packaged Target/Radar FOM resource plus the repo-local scenario and
artifact helpers used by examples and verification flows.

## What This Is Not

It is not:

- a public standard API package
- a concrete RTI backend
- a generic runtime support package

This is a leaf package. It owns concrete model assets and scenario support.
It does not expose a supported public Python import surface.

## When To Open It

Open this package when you want:

- the bundled `TargetRadarFOMmodule.xml` resource
- the internal scenario runner used by repo examples and verification flows
- a stable place to extend the Target/Radar example without changing core
  runtime packages

## Key Entrypoints

The owning namespace root is:

- `hla.foms.target_radar`

The human-facing entrypoints stay outside the package:

- `./tools/target-radar`
- `examples/target_radar_simulation.py`
- `examples/target_radar.py`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/python_environment.md`](../../docs/python_environment.md)
- [`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md)
- [`docs/README.md`](docs/README.md)

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

If you are extending the example, keep human-facing usage on `./tools` or
`examples/` and treat package-owned helpers as implementation detail.

Guard coverage lives in:

- `tests/test_fom_target_radar_split_package.py`
