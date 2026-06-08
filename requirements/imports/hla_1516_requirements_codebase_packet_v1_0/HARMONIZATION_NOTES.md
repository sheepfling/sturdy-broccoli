# Harmonization Notes

This note tracks how the imported v1.0 packet relates to the repo's current
curated requirements working set.

## Current split

- `requirements/imports/hla_1516_requirements_codebase_packet_v1_0/latest/*`
  is the raw packet-provided canonical v1.0 dump.
- Top-level `requirements/*.csv` remains the repo-native harmonized working
  set built incrementally from earlier tranches and direct implementation
  evidence.

## Rough correspondence

- Packet `latest/hla_1516_requirements_master_v1_0.csv`
  is the broad external baseline for all three standards.
- Packet `latest/hla_1516_verification_matrix_v1_0.csv`
  is the broad external verification ledger.
- Packet `latest/hla_1516_clause_tracker_v1_0.csv`
  is the external clause coverage and peer-review tracker.
- Repo `requirements/hla1516_1_clause_4_fm_service_decomposition.csv`
  is a deeper implementation-driving decomposition than the packet's coarse
  master rows for Clause 4 Federation Management.
- Repo `requirements/hla1516_1_clause_5_declaration_management.csv`
  and `requirements/hla1516_1_clause_6_object_management.csv`
  are narrower harmonized clause files that should eventually be reconciled
  against packet `latest/hla_1516_clauses5_11_detailed_requirements_v1_0.csv`
  and `latest/hla_1516_clause6_11_detailed_requirements_v1_0.csv`.
- Repo `requirements/traceability_matrix.csv`
  is still hand-maintained and does not yet ingest the packet's full
  verification matrix or clause tracker.

## Immediate next steps

1. Compare packet `latest/hla_1516_clause_tracker_v1_0.csv` against the repo's
   current curated clause coverage and identify clause deltas.
2. Reconcile packet `latest/hla_1516_clauses5_11_detailed_requirements_v1_0.csv`
   with repo Clause 5 and Clause 6 harmonized files.
3. Decide whether packet `latest/hla_1516_requirements_master_v1_0.csv` should
   become a committed upstream source for future tooling and linting, or remain
   an intake artifact only.
4. Add schema and manifest validation around the imported packet before wiring
   its files into CI or generated docs.

## Policy reminder

The packet's restricted IEEE inputs were intentionally excluded from the
committed import. Treat `MANIFEST.json` as the audit trail for those omitted
artifacts.
