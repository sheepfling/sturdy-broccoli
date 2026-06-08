# Workspace Layout

This repository is a workspace, not just a library checkout.
The top level is intentionally split by ownership:

`package -> entrypoints -> analysis -> vendor trees -> provenance`

## Top-Level Areas

- `hla2010/`: installable Python package and runtime surface.
- `examples/`: runnable example entrypoints and thin scenario scripts.
- `scripts/`: operator commands, CI wrappers, and generated-artifact entrypoints.
- `tests/`: executable verification for the package and the workspace helpers.
- `docs/`: navigation, runbooks, architecture notes, and evidence maps.
- `analysis/`: generated compliance and verification outputs.
- `requirements/`: seed requirement catalogs and traceability bridges.
- `CERTI/`: vendored CERTI source tree.
- `java_shims/`: Java bridge validation source.
- `third_party/pitch/`: local Pitch vendor drop contract.
- `tools/`: legacy source-analysis and extraction helpers retained for provenance.
- `INBOX/`: unpromoted source drops and intake material.
- `archives/`: retained source-drop and verification archives.

## Practical Guidance

- Keep public runtime code in `hla2010/`.
- Keep runnable examples thin and repo-local under `examples/`.
- Keep operator entrypoints and CI wrappers in `scripts/`.
- Keep generated outputs out of the installable package.
- Keep provenance-only analysis helpers in `tools/` unless they are promoted into `scripts/` or `docs/evidence/`.
- The backend-alias matrix generator has already been promoted into `scripts/update_rti_options_matrix.py` because CI and operator flows treat it as a supported entrypoint.

## What Not To Move

Not every top-level directory should be collapsed.
The vendor trees and evidence archives are separate on purpose so the runtime
package stays reviewable and the imported source/provenance stays auditable.
