# HLA 1516-2025 requirement depth expansion packet

Generated from the uploaded IEEE 1516-2025 PDFs and companion API/XML/XSD download packets, with 2010 API/XSD files used only for delta classification.

This packet is intended as an import/harmonization candidate, not as a claim that repo evidence already satisfies the rows. The Mac-local repository paths named in the prompt were not directly accessible here, so the rows are source-derived and ready to compare against the curated registry/backlog/executable-test packet.

## Files

- `hla_2025_requirement_depth_expansion.csv` - normalized rows using the requested columns.
- `hla_2025_requirement_depth_expansion.json` - same rows as JSON.
- `hla_2025_requirement_depth_expansion_summary.json` - row counts by area, delta type, and source document.
- `source_manifest.json` - local source paths, byte sizes, and SHA-256 hashes.

## Row counts

- Total rows: 691

### By area

- Callback/configuration/binding deltas: 12
- Federate Interface service catalog: 196
- Framework and Rules: 10
- OMT component-level conformance: 224
- OMT validator-negative conformance: 29
- Retired / replacement mapping candidates: 24
- SOM/FOM service-usage requirements: 196

### By delta type

- binding-specific: 2
- carry-forward: 328
- modified: 237
- new: 71
- retired: 24
- verification: 29

## Notes

- `page` uses the printed IEEE page number where available.
- `delta_type` is a generated harmonization hint based on 2025-vs-2010 API/XSD comparison and known 2025 change themes. Treat it as reviewable, not authoritative.
- `OMT-CV-*` rows use `delta_type=verification` because they are validator-negative/evidence rows. Their `notes` field records the 2010 comparison.
- `FI-RET-*` and `OMT-RET-*` rows are legacy-only mapping candidates that can be kept in a migration ledger or filtered out of the 2025 normative set.
