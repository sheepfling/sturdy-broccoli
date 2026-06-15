# hla_1516_requirements_codebase_packet_v1_0

This directory is a committed intake copy of the external IEEE 1516-2010 (2010 edition),
IEEE 1516.1-2010 (2010 edition), and IEEE 1516.2-2010 (2010 edition)
requirements packet received in `INBOX/REQTS`.

The packet baseline covers the IEEE 1516-2010 (2010 edition), IEEE 1516.1-2010 (2010 edition), and
IEEE 1516.2-2010 (2010 edition) editions.

It is intentionally separate from the curated repo-native requirement surfaces:

- `requirements/active_service_rows.csv` is the small hand-edited active
  traceability working set.
- `requirements/traceability_matrix.csv` is the generated compatibility merge.
- `requirements/reference/*.csv` carries the broader hand-harmonized clause and
  reconciliation catalogs.
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
