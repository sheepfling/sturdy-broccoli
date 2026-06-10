# Workspace Layout

This repository is a workspace, not just a library checkout.
The top level is intentionally split by ownership:

`package -> entrypoints -> generated evidence -> local runtime state -> vendor trees -> provenance`

## Top-Level Areas

- `src/hla2010/`: core API layer and compatibility facades.
- `hla2010/`: narrow plugin-facing shim area.
- `packages/*/src/`: package-owned backend and support implementation roots.
- `examples/`: runnable example entrypoints and thin scenario scripts.
- `scripts/`: operator commands, CI wrappers, and generated-artifact entrypoints.
- `tests/`: executable verification for the package and the workspace helpers.
- `docs/`: navigation, runbooks, architecture notes, and evidence maps.
- `analysis/`: generated compliance and verification outputs.
- `.local/`: machine-local runtime/build state for CERTI, Pitch, and similar vendor tools.
- `requirements/`: seed requirement catalogs and traceability bridges.
- `CERTI/`: vendored CERTI source tree.
- `java_shims/`: Java bridge verification-fixture source and shim build tooling.
- `third_party/pitch/`: local Pitch vendor drop contract.
- `tools/`: legacy source-analysis and extraction helpers retained for provenance.
- `INBOX/`: unpromoted source drops and intake material.
- `archives/`: retained source-drop and verification archives.

## Practical Guidance

- Keep core API code, shared abstractions, and compatibility facades in `src/hla2010/`.
- Keep concrete backend and support implementations in their owning `packages/<name>/src/` trees.
- Keep runnable examples thin and repo-local under `examples/`.
- Keep operator entrypoints and CI wrappers in `scripts/`.
- Keep generated outputs out of the installable package.
- Keep generated compliance, proof, preflight, and matrix outputs under `analysis/` rather than scattered top-level report directories.
- Keep vendor runtime/build state out of the repo root and under `.local/`.
- Keep provenance-only analysis helpers in `tools/` unless they are promoted into `scripts/` or `docs/evidence/`.
- The backend-alias matrix generator has already been promoted into `scripts/update_rti_options_matrix.py` because CI and operator flows treat it as a supported entrypoint.

## Setup First

Before you touch vendor runtimes or bridge profiles, set up Python first:

1. run `./scripts/bootstrap_profile.sh python`
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
