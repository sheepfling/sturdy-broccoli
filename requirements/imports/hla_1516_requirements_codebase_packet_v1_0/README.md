# hla_1516_requirements_codebase_packet_v1_0

This directory is a committed intake copy of the external HLA 1516 requirements packet received in `INBOX/REQTS`.

It is intentionally separate from the curated edition-specific requirements surfaces:

- `requirements/2010/*.csv` stays as the hand-harmonized 2010 engineering working set used for repo-native traceability.
- `requirements/2025/` stays as the collected 2025 source-trace and harmonization surface.
- `requirements/imports/hla_1516_requirements_codebase_packet_v1_0/*` preserves the packet-provided v1.0 dump, workpacket, history, and manifest as imported source material.

## Imported structure

- `latest/` — packet canonical v1.0 outputs.
- `catalogs/` — carried-forward API, MIM, XSD, and WSDL catalogs.
- `history/` — earlier tranche outputs for audit/history.
- `scripts/` — build scripts that shipped with the packet.
- `work_packet/` — integration instructions, task CSV, schema contract, placement plan, and acceptance checklist.
- `MANIFEST.json` — packet file inventory with SHA-256 checksums.

## Restricted inputs

The packet's `requirements/restricted_reference_inputs/` subtree was not copied into the repository import because the workpacket itself recommends against committing IEEE source documents or downloaded standards artifacts without license review.

Those omitted artifacts remain referenced by checksum in `MANIFEST.json` and should be handled as local/private reference material only.

## Start here

1. Read `work_packet/AGENT_WORK_PACKET.md`.
2. Use `work_packet/REPO_PLACEMENT_PLAN.yaml` as the packet author's intended layout, but reconcile it against the existing repo structure before moving files.
3. Use `work_packet/CODEBASE_HOOKUP_TASKS.csv` as the packet backlog.
4. Use `work_packet/REQUIREMENTS_SCHEMA.md` as the starting schema contract for future linting and validation.
