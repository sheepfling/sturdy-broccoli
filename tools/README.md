# Tools

This directory is the canonical home for human-facing operator entrypoints.

Use:

- `./tools/python`
- `./tools/certi-easy`
- `./tools/pitch`
- `./tools/vendor-green`
- `./tools/vendor-state`
- `./tools/vendor-parity`
- `./tools/vendor-probe-review`
- `./tools/vendor-edge`
- `./tools/rti-options`
- `./tools/compliance`
- `./tools/fom-overview`
- `./tools/package-deps`
- `./tools/section8-gate`
- `./tools/target-radar`
- `./tools/lint`
- `./tools/bootstrap`
- `./tools/two-federate`
- `./tools/test`

The `scripts/` tree remains implementation and CI plumbing. Compatibility
wrappers may still exist under `scripts/`, but operator docs, workflows, tests,
and generated guidance should point at `tools/`.
