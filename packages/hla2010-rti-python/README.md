# hla2010-rti-python

Migration scaffold for the pure in-memory Python RTI backend package.

This package now contains the Python RTI backend implementation under
`src/hla2010_rti_python/`. The old `hla2010.backends.python` compatibility
package has been removed; import this package directly.
Package-owned verification profile helpers live in
`src/hla2010_rti_python/testing_policy.py`.
Package-owned split-package and matrix guard coverage lives in
`tests/test_rti_python_split_package.py` and
`tests/test_python_matrix_policy.py`.
The human operator surface for the pure Python backend stays `./tools/python`;
this package does not add a package-local command.

Bootstrap the repo root before working in this package:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

Use the full setup guide at
[`../../docs/python_environment.md`](../../docs/python_environment.md).

Public transition imports:

- `hla2010_rti_python`
- `hla2010_rti_python.backend`
- `hla2010_rti_python.engine`
- `hla2010_rti_python.factory`
- `hla2010_rti_python.state`
- `hla2010_rti_python.plugin`

Repo code and tests should import from `hla2010_rti_python` where they are
intentionally using the pure Python backend.
