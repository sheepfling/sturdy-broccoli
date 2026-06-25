# Artifacts

This directory is the default home for fresh generated run outputs.

Use `artifacts/` for:

- ad hoc run outputs
- temporary or repeatable reports
- generated CSV/JSON/Markdown manifests from tools and scripts
- local showcase packets that are not yet promoted into stable repo evidence

Do not treat everything here as curated evidence.

Promote outputs into `analysis/` only when they become:

- intentionally retained evidence packets
- docs- or test-referenced proof artifacts
- stable summaries we expect contributors or CI to cite

Operator rule:

- default new `--output-dir` flows to `artifacts/...`
- use explicit `--output-dir analysis/...` when publishing a promoted packet
