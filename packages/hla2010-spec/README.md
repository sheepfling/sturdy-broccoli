# hla2010-spec

Clean IEEE 1516.1-2010 Python spec package.

This package is the public front door for the neutral edition-qualified
namespace `hla.editions.ed2010` and the 2010 compatibility namespace
`hla2010`.

Primary imports:

- `hla.editions.ed2010.spec` for the explicit 2010-edition contract layer
- `hla.editions.ed2010.rti` for the explicit 2010-edition runtime facade
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

## Start Here

Use this package when you need to change the public contract or shared spec-side
behavior.

Shortest path:

1. open `src/hla2010/spec/__init__.py` for public spec ownership
2. open `src/hla2010/runtime_api.py` for the Pythonic runtime layer
3. open `src/hla2010/fom.py` for FOM entrypoints
4. only then read the broader spec maps if the ownership is still unclear

## Ownership Card

- Edit here for: public RTI method surface, callback contracts, shared exceptions, FOM parsing and merge behavior
- Do not edit here for: Python RTI service logic, vendor bridge behavior, transport wiring
- First files to open:
  `src/hla2010/spec/__init__.py`, `src/hla2010/runtime_api.py`,
  `src/hla2010/fom.py`, `src/hla2010/ambassadors.py`
- Quick tests:
  `python3 -m pytest tests/test_python_api_spec.py tests/factories/test_fom_omt_parsing.py -q`

## Read Next

1. [`../../docs/spec_reading_map.md`](../../docs/spec_reading_map.md)
2. [`../../docs/python_api_spec.md`](../../docs/python_api_spec.md)
3. [`../../docs/package_layout.md`](../../docs/package_layout.md)
