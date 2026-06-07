# Docs

Project documentation for the IEEE 1516-2010-focused workspace.

- `reference/` source acquisition notes and retained archive copies.
- `evidence/` unpacked verification packets and imported analysis artifacts.
- `specs/` clause indexes, matrices, and evidence-ledger artifacts.
- `plans/` roadmap items and implementation sequencing.
- `CERTI/` vendored CERTI source and the local build/install workflow live at
  the repo root, not under `docs/`.
- Generated downloads, service reports, and caches should live outside the
  synced tree by default, under `/private/tmp/hla-2010`.
- `backend_route_inventory.md` is the exhaustive inventory of runtime families,
  bridge routes, transport routes, named CERTI baselines, and evidence anchors.
- `pitch_docker_quickstart.md` is the simplest operator-facing path for
  installing, starting, testing, and troubleshooting the Docker-backed Pitch runtime.
- `backend_conformance_matrix.md` records clause-level backend parity and conformance status across Python, CERTI, and future Pitch.
- `certi_spec_traceability.md` records clause-level real CERTI coverage for sync and ownership services.
- `certi_negotiated_ownership_findings.md` records the source/runtime investigation for CERTI negotiated ownership failures.
- `inbox_inventory_2026-06-05.md` records the source-drop promotion out of `INBOX`.
