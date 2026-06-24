# hla-rti1516e

## What This Is

`hla-rti1516e` is the strict IEEE 1516.1-2010 Python spec package.

It is the public front door for the canonical `hla.rti1516e` standard-facing API.

## What This Is Not

It is not:

- a concrete RTI backend
- a vendor integration package
- a transport package
- a repo-local operator command surface

## When To Open It

Open this package when you need the 2010 standard surface itself:

- public protocol definitions
- standard datatypes, handles, enums, exceptions, and time types
- standard-facing source-trace or contract metadata

- `hla.rti1516e.RTIambassador` and `hla.rti1516e.FederateAmbassador` for the canonical strict protocol surface
- `hla.rti1516e.RTIambassador` as the canonical `hla.rti1516e.RTIambassador` reference surface
- `hla.runtime.rti1516e_ambassador` and `hla.rti1516e.federate_ambassador` for the source-shaped interface modules
- `hla.runtime.rti1516e` for version-local backend discovery and ambassador creation

## Key Imports

It also owns shared HLA value types and traceability helpers:

- `handles`, `datatypes`, `logical_time`, `enums`, `time`, `exceptions`
- FOM/MOM helpers and source-reference scaffolding
- source-derived metadata used by the spec layer

## Related Docs

It must not depend on concrete RTI backends, Java bridge runtimes, CERTI/Pitch
runtime discovery, examples, or repo-internal testing helpers.
It does not own human operator entrypoints; those live under `./tools/`.
Guard coverage for this boundary lives in
`tests/test_package_split_scaffolds.py`, `tests/test_root_facade_policy.py`,
`tests/test_namespace_policy.py`, and `tests/test_python_api_spec.py`.

Retained package-side reports and metadata:

- [`docs/README.md`](docs/README.md): package-local documentation front door
- [`MIGRATION.md`](MIGRATION.md): retained split-package migration notes
- [`MERGE_REPORT.md`](MERGE_REPORT.md): retained merge/import report
- [`STRICT_DOC_REPORT.md`](STRICT_DOC_REPORT.md): retained strict-doc import report
- [`src/hla/rti1516e/api_metadata.json`](src/hla/rti1516e/api_metadata.json): source-derived API metadata used by the spec layer

If you want the user-facing package map, read
[`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md),
[`../../docs/package_layout.md`](../../docs/package_layout.md) and
[`../../docs/python_api_spec.md`](../../docs/python_api_spec.md).
