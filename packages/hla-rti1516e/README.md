# hla-rti1516e

Strict IEEE 1516.1-2010 Python spec package.

This package is the public front door for the canonical `hla.rti1516e` standard-facing API:

- `hla.rti1516e.RTIambassador` and `hla.rti1516e.FederateAmbassador` for the canonical strict protocol surface
- `hla.rti1516e.rti_ambassador` and `hla.rti1516e.federate_ambassador` for the source-shaped interface modules
- `hla.rti1516e.rti` for version-local backend discovery and ambassador creation

It also owns the shared HLA value types and traceability helpers:

- `handles`, `datatypes`, `logical_time`, `enums`, `time`, `exceptions`
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
