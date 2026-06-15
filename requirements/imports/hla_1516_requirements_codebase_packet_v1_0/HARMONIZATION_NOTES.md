# Harmonization Notes

This note tracks how the imported v1.0 packet relates to the repo's current
curated requirements working set.

The imported packet baseline and the repo-native harmonization files in this
directory are all aligned to the IEEE 1516-2010 (2010 edition), IEEE 1516.1-2010 (2010 edition), and
IEEE 1516.2-2010 (2010 edition) editions.

## Current split

- `requirements/imports/hla_1516_requirements_codebase_packet_v1_0/latest/*`
  is the raw packet-provided canonical v1.0 dump.
- `requirements/active_service_rows.csv` is the narrow repo-native active
  traceability surface.
- `requirements/traceability_matrix.csv` is the generated compatibility merge.
- `requirements/reference/*.csv` remains the broader harmonized clause and
  reconciliation working set built incrementally from earlier tranches and
  direct implementation evidence.

## Current pin

As of the latest committed harmonization tranche, the repo-wide imported master
index in `requirements/reference/hla_1516_master_harmonization_index_v1_0.csv` stands at:

- `2675 mapped`
- `1328 partial`
- `0 planned`
- `0 unreconciled`

The latest small tranche tightened Federation Management lifecycle evidence in
`requirements/reference/hla1516_1_fm_detailed_reconciliation.csv` by promoting direct
positive rows for:

- Connect successful postconditions
- Create Federation Execution successful existence/joinability
- Join Federation Execution membership and handle return
- Resign Federation Execution delete-capable directive effects

That tranche is backed by direct runtime witnesses in
`tests/backends/test_python_backend_federation_extended.py` and reflected in
the FM family verifier plus the master harmonization index.

## Rough correspondence

- Packet `latest/hla_1516_requirements_master_v1_0.csv`
  is the broad external baseline for all three IEEE 2010 standards.
- Packet `latest/hla_1516_verification_matrix_v1_0.csv`
  is the broad external verification ledger.
- Packet `latest/hla_1516_clause_tracker_v1_0.csv`
  is the external clause coverage and peer-review tracker.
- Repo `requirements/reference/hla1516_1_clause_4_fm_service_decomposition.csv`
  is a deeper implementation-driving decomposition than the packet's coarse
  master rows for Clause 4 Federation Management.
- Repo `requirements/reference/hla1516_1_clause_5_declaration_management.csv`
  and `requirements/reference/hla1516_1_clause_6_object_management.csv`
  are narrower harmonized clause files that should eventually be reconciled
  against packet `latest/hla_1516_clauses5_11_detailed_requirements_v1_0.csv`
  and `latest/hla_1516_clause6_11_detailed_requirements_v1_0.csv`.
- Repo `requirements/active_service_rows.csv`
  is the maintained active row-edit surface.
- Repo `requirements/traceability_matrix.csv`
  is the generated compatibility merge and does not yet ingest the packet's
  full verification matrix or clause tracker.

## Immediate next steps

1. Keep burning down `partial` rows inside the family bridges instead of adding
   new bridge structure. The largest remaining honest debt is still in
   `CAP-API`, `CAP-XML`, `CAP-FM`, `CAP-SUP`, and `CAP-OM`.
2. Prefer small tranches that replace stale or indirect evidence anchors with
   direct node-level runtime or verifier-backed witnesses.
3. Regenerate `requirements/reference/hla_1516_master_harmonization_index_v1_0.csv` after
   every family-bridge promotion so the packet-facing pin stays truthful.
4. Keep broad rows `partial` when current tests only prove a narrower subset;
   do not collapse supported-subset evidence into overstated full-standard
   claims.

## Policy reminder

The packet's restricted IEEE inputs were intentionally excluded from the
committed import. Treat `MANIFEST.json` as the audit trail for those omitted
artifacts.
