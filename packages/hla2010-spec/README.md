# hla2010-spec

Migration scaffold for the pure IEEE 1516.1-2010 Python spec package.

This package should eventually contain:

- `hla2010.spec`
- `hla2010.runtime_api`
- `hla2010.rti` only as a temporary workspace compatibility facade for backend
  registry and entry point discovery during the split-package migration
- shared transport and backend support should stay in their owning split
  packages, not grow new root facades
- shared `handles`, `types`, `enums`, `time`, `exceptions`, FOM/MOM helpers

It must not depend on concrete RTI backends, Java bridge runtimes, CERTI/Pitch
runtime discovery, examples, or repo-internal testing helpers.
Import the canonical runtime namespace from `hla2010`, with `hla2010.rti`
remaining only as the documented temporary compatibility facade.
Guard coverage for that root-namespace boundary lives in
`tests/test_package_split_scaffolds.py`, `tests/test_root_facade_policy.py`,
`tests/test_namespace_policy.py`, and `tests/test_python_api_spec.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
