# Workspace Layout

This repository is a workspace, not just a library checkout.
The top level is intentionally split by ownership:

`package -> entrypoints -> generated evidence -> local runtime state -> vendor trees -> provenance`

## Top-Level Areas

- `src/hla2010/`: abstract/core API surface plus the one documented temporary split-package workspace facade `hla.rti1516e.rti`.
- `packages/*/src/`: package-owned backend and support implementation roots.
- `examples/`: runnable example entrypoints and thin scenario scripts.
- `scripts/`: implementation helpers, CI wrappers, setup flows, and generated-artifact entrypoints.
- `tools/`: canonical human-facing operator entrypoints.
- `tests/`: executable verification for the package and the workspace helpers.
- `docs/`: navigation, runbooks, architecture notes, and evidence maps.
- `analysis/`: generated compliance and verification outputs.
- `.local/`: machine-local runtime/build state for CERTI, Pitch, and similar vendor tools.
- `requirements/`: seed requirement catalogs and traceability bridges.
- `CERTI/`: vendored CERTI source tree.
- `java_shims/`: Java bridge verification-fixture source and shim build tooling.
- `third_party/pitch/`: local Pitch vendor drop contract.
- `INBOX/`: unpromoted source drops and intake material.
- `archives/`: retained source-drop and verification archives.

## Practical Guidance

- Keep abstract/core API code and only the documented workspace-stable shims in `src/hla2010/`.
- The remaining documented root compatibility facade into split packages is `hla.rti1516e.rti`, and it should be treated as temporary.
- Package-owned implementation should prefer `hla.rti` over `hla.rti1516e.rti` when it needs backend discovery or ambassador-factory helpers.
- Keep concrete backend and support implementations in their owning `packages/<name>/src/` trees.
- Keep runnable examples thin and repo-local under `examples/`.
- Keep human-facing operator entrypoints in `tools/`.
- Keep implementation helpers and CI wrappers in `scripts/`.
- Keep generated outputs out of the installable package.
- Keep generated compliance, proof, preflight, and matrix outputs under `analysis/` rather than scattered top-level report directories.
- Keep vendor runtime/build state out of the repo root and under `.local/`.
- Keep the `tools/` directory narrow and operator-facing; do not let it become a second implementation tree.
- The backend-alias matrix generator has already been promoted into `./tools/rti-options generate` because CI and operator flows treat it as a supported entrypoint.

## Setup First

Before you touch vendor runtimes or bridge profiles, set up Python first:

1. run `./tools/bootstrap python`
2. activate `.venv`
3. run a pure-Python smoke command
4. only then add JPype, Py4J, CERTI, or Pitch paths

The canonical setup guide is [`python_environment.md`](python_environment.md).

## What Not To Move

Not every top-level directory should be collapsed.
The vendor trees and evidence archives are separate on purpose so the runtime
package stays reviewable and the imported source/provenance stays auditable.
Likewise, `.local/` is intentionally separate from `analysis/`: runtime/build
state is machine-local, while verification outputs are part of the repo's
documented evidence flow.
