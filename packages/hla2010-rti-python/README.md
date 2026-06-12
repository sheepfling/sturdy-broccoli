# hla2010-rti-python

Pure in-memory Python RTI backend package.

This package owns the local reference RTI implementation under
`src/hla2010_rti_python/`. The old `hla2010.backends.python` compatibility
package has been removed; import this package directly.

The public package root is the normal entrypoint:

- `hla2010_rti_python`
- `hla2010_rti_python.backend`
- `hla2010_rti_python.engine`
- `hla2010_rti_python.factory`
- `hla2010_rti_python.state`
- `hla2010_rti_python.plugin`

Use it when you want:

- the dependency-free local reference RTI
- backend behavior that is easy to debug and fast to run
- a backend for the Target/Radar example and the two-federate verification
  scenarios

Use `./tools/python verify` for the repo-green verification lane.
The human operator surface for this backend stays `./tools/python`; this
package does not add a package-local command.

Package-owned verification policy helpers live in
`src/hla2010_rti_python/testing_policy.py`.
Package-owned split-package and matrix guard coverage lives in
`tests/test_rti_python_split_package.py` and
`tests/test_python_matrix_policy.py`.

For setup order, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Then use the full environment guide at
[`../../docs/python_environment.md`](../../docs/python_environment.md).
If you are extending the example story, read
[`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md)
and [`../../packages/hla2010-fom-target-radar/README.md`](../../packages/hla2010-fom-target-radar/README.md).
