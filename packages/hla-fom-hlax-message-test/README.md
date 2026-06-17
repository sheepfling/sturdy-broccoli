# hla-fom-hlax-message-test

Package-owned HLA-X MessageTest showcase runner for the `hla2010` workspace.

This package now owns:

- the repo-internal MessageTest showcase scenario runner
- package-local docs and split-package guard coverage
- the package boundary for future MessageTest-specific examples and helpers

This package does not expose a supported public Python import surface. Treat its
implementation as package-owned and repo-internal.

The `hla.foms.hlax_message_test` namespace remains the owning package root for
this showcase implementation.

The HLA-X v0.1 MessageTest FOM XML modules remain owned by
`hla-rti1516-2025` for now. This package consumes those packaged resources and
owns the executable showcase scenario built on top of them.

The combined human-facing showcase surface remains:

- `./tools/hla-x demo fom-showcase`

Split-package guard coverage lives in
`tests/test_fom_hlax_message_test_split_package.py`.

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

If you want the package entrypoint and usage story, read
[`docs/README.md`](docs/README.md).
