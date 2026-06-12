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

This package depends on `hla2010-spec` and may optionally be combined with
backend plugin packages for runnable examples, but it does not own RTI backend
implementations.
Import the canonical implementation from `hla2010_fom_target_radar`.
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
