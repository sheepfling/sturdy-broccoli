# Artifacts

This directory is the default home for fresh generated run outputs.

Repository policy:

- everything under `artifacts/` is ignored by Git by default
- `artifacts/README.md` is the only tracked exception
- if an output should live in Git, move or promote it out of `artifacts/`
  into an intentional home such as `analysis/`, `docs/`, or `compat/`

Use `artifacts/` for:

- ad hoc run outputs
- temporary or repeatable reports
- generated CSV/JSON/Markdown manifests from tools and scripts
- local showcase packets that are not yet promoted into stable repo evidence

Do not treat anything here as curated evidence by default.

Promote outputs out of `artifacts/` only when they become:

- intentionally retained evidence packets
- docs- or test-referenced proof artifacts
- stable summaries we expect contributors or CI to cite

Operator rule:

- default new `--output-dir` flows to `artifacts/...`
- use explicit `--output-dir analysis/...` when publishing a promoted packet
- do not add generated files from `artifacts/` to Git as a convenience step
