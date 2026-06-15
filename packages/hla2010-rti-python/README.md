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

Backend implementation layout, service registry, and trace commands are
documented in [`../../docs/python_rti_backend.md`](../../docs/python_rti_backend.md).

## Start Here

Use this package when the question is "what does the reference Python RTI do?"
rather than "what should the public API look like?"

Shortest path:

1. open `src/hla2010_rti_python/service_registry.py` to find the concrete service owner
2. open the matching `*_public_services.py` or backend helper module
3. run the focused backend tests before widening out to matrix or scenario docs

## Ownership Card

- Edit here for: concrete Python RTI service behavior, backend-local helpers, callback delivery, stateful backend semantics
- Do not edit here for: public spec signatures, vendor runtime discovery, Java bridge mechanics
- First files to open:
  `src/hla2010_rti_python/backend.py`,
  `src/hla2010_rti_python/service_registry.py`,
  `src/hla2010_rti_python/time_public_services.py`
- Quick tests:
  `python3 -m pytest tests/backends/test_python_rti_service_registry.py tests/test_python_api_spec.py -q`

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

## Read Next

1. [`../../docs/python_rti_edit_one_service.md`](../../docs/python_rti_edit_one_service.md)
2. [`../../docs/python_rti_reading_map.md`](../../docs/python_rti_reading_map.md)
3. [`../../docs/python_rti_backend.md`](../../docs/python_rti_backend.md)
4. [`../hla2010-fom-target-radar/README.md`](../hla2010-fom-target-radar/README.md)
