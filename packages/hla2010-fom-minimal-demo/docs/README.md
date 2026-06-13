# hla2010-fom-minimal-demo docs

This package owns a concrete minimal-demo example FOM, packaged
`resources.foms` assets, and the smallest supported scenario helpers for
copying a new example/FOM package.

Key owned surfaces:

- `hla2010_fom_minimal_demo.resources.foms`: packaged minimal FOM assets.
- `hla2010_fom_minimal_demo.scenarios`: canonical publisher/subscriber scenario
  and factory helpers.
- package-owned example/FOM support for the create-federate-and-FOM tutorial.
- `tests/examples/test_minimal_fom_demo.py`: split-package guard coverage for
  the installable minimal demo package.

This package does not own RTI backend implementations or generic shared
verification-harness scenarios.

If you want the package entrypoint and usage story, read
[`../README.md`](../README.md).
