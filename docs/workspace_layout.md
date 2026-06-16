# Workspace Layout

This repository is a workspace, not just a library checkout.
The top level is intentionally split by ownership:

`package -> entrypoints -> generated evidence -> local runtime state -> vendor trees -> provenance`

The Python namespace root is `hla`, contributed by PEP 420 namespace packages.
No distribution owns `src/hla/__init__.py`.

## Top-Level Areas

- `packages/hla-rti1516e/src/hla/rti1516e/`: IEEE 1516.1-2010 API package.
- `packages/hla-rti1516-2025/src/hla/rti1516_2025/`: IEEE 1516.1-2025 API scaffold.
- `packages/hla-rti-core/src/hla/rti/`: cross-version discovery and factory package.
- `packages/*/src/`: package-owned backend, transport, bridge, FOM, verification, and support implementation roots.
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

- Keep version-specific API code under `hla.rti1516e` or `hla.rti1516_2025`.
- Keep cross-version discovery and ambassador-factory helpers under `hla.rti`.
- Package-owned implementation should import `hla.rti` directly when it needs backend discovery or ambassador-factory helpers.
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
