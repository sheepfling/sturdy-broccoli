# hla-backend-inmemory

## What This Is

`hla-backend-inmemory` is the local pure-Python RTI backend.

It owns concrete backend behavior under `hla.backends.inmemory` and is the
easiest backend to run, debug, and test locally.

## What This Is Not

It is not:

- the public HLA standard surface
- the 2025 Python RTI lane
- a transport package
- a vendor integration package

If you need standard API definitions, start with `hla.rti1516e` or
`hla.rti1516_2025`. If you need the main 2025 runtime, use
`hla-backend-python2025`.

## When To Open It

Open this package when you want:

- the dependency-light local reference RTI
- backend behavior that is fast to run and easy to inspect
- the base backend behind the Target/Radar example and many repo verification
  flows

## Key Imports

The normal entrypoints are:

- `src/hla.backends.inmemory/`
- `src/hla.backends.inmemory/testing_policy.py`
- `hla.backends.inmemory`
- `hla.backends.inmemory.backend`
- `hla.backends.inmemory.engine`
- `hla.backends.inmemory.factory`
- `hla.backends.inmemory.state`
- `hla.backends.inmemory.plugin`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/python_environment.md`](../../docs/python_environment.md)
- [`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md)
- [`../../packages/hla-fom-target-radar/README.md`](../../packages/hla-fom-target-radar/README.md)
- [`docs/README.md`](docs/README.md)

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

The human operator surface stays under `./tools/python`.

Use `./tools/python` as the package-local command surface.

Guard coverage lives in:

- `tests/test_rti_python_split_package.py`
- `tests/test_python_matrix_policy.py`
