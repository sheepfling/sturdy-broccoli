# hla-backend-inmemory

Pure in-memory Python RTI backend package.

This package owns the local reference RTI implementation under
`src/hla.backends.inmemory/`. The old `hla.rti1516e.backends.python` compatibility
package has been removed; import this package directly.

The public package root is the normal entrypoint:

- `hla.backends.inmemory`
- `hla.backends.inmemory.backend`
- `hla.backends.inmemory.engine`
- `hla.backends.inmemory.factory`
- `hla.backends.inmemory.state`
- `hla.backends.inmemory.plugin`

Use it when you want:

- the dependency-free local reference RTI
- backend behavior that is easy to debug and fast to run
- a backend for the Target/Radar example and the two-federate verification
  scenarios

Use `./tools/python verify` for the repo-green verification lane.
The human operator surface for this backend stays `./tools/python`; this
package does not add a package-local command.

Package-owned verification policy helpers live in
`src/hla.backends.inmemory/testing_policy.py`.
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
and [`../../packages/hla-fom-target-radar/README.md`](../../packages/hla-fom-target-radar/README.md).
