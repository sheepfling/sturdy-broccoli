# hla-fom-target-radar

Concrete Target/Radar FOM and internal example-support package for the `hla2010` workspace.

This package now owns:

- the packaged `TargetRadarFOMmodule.xml` resource
- repo-internal target/radar scenario helpers
- target/radar example runner factory helpers
- target/radar backend-matrix and proof artifact generators
- target/radar-owned two-federate suite helper slices
- target/radar-owned two-federate suite artifact formatting
- target/radar-owned two-federate vendor profile policy

This package does not expose a supported public Python import surface. The old
root-level `hla.rti1516e.scenarios.target_radar` compatibility path remains
removed, and the package-owned scenario helpers now live under a private
namespace.

The `hla.foms.target_radar` namespace remains the owning package root for the
bundled FOM resources and repo-internal example implementation.

Use this package when you want:

- the bundled Target/Radar FOM path
- the internal scenario runner used by repo examples and verification flows
- a backend factory that can target local Python, JPype, Py4J, or the split
  runtime helper defaults
- a stable place to extend the example without touching the generic HLA
  interface package

This package depends on `hla-rti1516e` and may optionally be combined with
backend plugin packages for runnable examples, but it does not own RTI backend
implementations.
Split-package guard coverage lives in
`tests/test_fom_target_radar_split_package.py`.

The human operator surface for Target/Radar stays `./tools/target-radar`; this
package does not add a package-local command.

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Then run the scenario entrypoints. Full install order lives in
[`../../docs/python_environment.md`](../../docs/python_environment.md).

If you are extending the example, keep human-facing usage on
`./tools/target-radar` or the `examples/target_radar*` scripts and treat the
package-owned helpers as repo-internal implementation detail.

The package-local docs page is
[`docs/README.md`](docs/README.md), and the broader walkthrough is in
[`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md).
