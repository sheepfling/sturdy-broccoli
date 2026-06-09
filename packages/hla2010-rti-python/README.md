# hla2010-rti-python

Migration scaffold for the pure in-memory Python RTI backend package.

This package now contains the Python RTI backend implementation under
`src/hla2010_rti_python/`. The old `hla2010.backends.python` package is a
compatibility facade that re-exports these modules during the migration.

Bootstrap the repo root before working in this package:

```bash
./bootstrap python
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

Next migration step: update repo code and tests to import from
`hla2010_rti_python` where they are intentionally using the pure Python backend,
then narrow the old compatibility facade.
