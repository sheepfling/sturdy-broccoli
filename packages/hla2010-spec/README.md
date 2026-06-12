# hla2010-spec

Clean IEEE 1516.1-2010 Python spec package.

This package is the public front door for the canonical runtime namespace from
`hla2010` and the abstract HLA interface surface:

- `hla2010.spec` for the clean contract layer
- `hla2010.runtime_api` for the Pythonic runtime convenience layer
- `hla2010.rti` only as the temporary workspace compatibility facade for
  backend discovery and ambassador creation during the split-package migration

It also owns the shared HLA value types and traceability helpers:

- `handles`, `types`, `enums`, `time`, `exceptions`
- FOM/MOM helpers and source-reference scaffolding
- source-derived metadata used by the spec layer

It must not depend on concrete RTI backends, Java bridge runtimes, CERTI/Pitch
runtime discovery, examples, or repo-internal testing helpers.
It does not own human operator entrypoints; those live under `./tools/`.
Guard coverage for this boundary lives in
`tests/test_package_split_scaffolds.py`, `tests/test_root_facade_policy.py`,
`tests/test_namespace_policy.py`, and `tests/test_python_api_spec.py`.

If you want the user-facing package map, read
[`../../docs/package_layout.md`](../../docs/package_layout.md) and
[`../../docs/python_api_spec.md`](../../docs/python_api_spec.md).
