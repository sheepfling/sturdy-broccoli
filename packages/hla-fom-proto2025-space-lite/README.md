# hla-fom-proto2025-space-lite

Package-owned Proto2025 SpaceLite showcase runner for the `hla2010` workspace.

This package now owns:

- the repo-internal SpaceLite showcase scenario runner
- package-local docs and split-package guard coverage
- the package boundary for future SpaceLite-specific examples and helpers

This package does not expose a supported public Python import surface. Treat its
implementation as package-owned and repo-internal.

The `hla.foms.proto2025_space_lite` namespace remains the owning package root for
this showcase implementation.

The Proto2025 v0.1 SpaceLite FOM XML modules remain owned by `hla-rti1516-2025`
for now. This package consumes those packaged resources and owns the executable
showcase scenario built on top of them.

The combined human-facing showcase surface remains:

- `./tools/shim-routes demo fom-showcase`

Split-package guard coverage lives in
`tests/test_fom_proto2025_space_lite_split_package.py`.

For setup, bootstrap the repo root first:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

If you want the package entrypoint and usage story, read
[`docs/README.md`](docs/README.md).
