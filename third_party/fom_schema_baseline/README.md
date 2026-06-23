# FOM Schema Validation Baseline

This directory holds the dedicated positive XML schema-validation baseline for the repo.

Purpose:

- prove that the checked-in validation lane is using canonical standard XML/XSD pairs
- keep schema-positive examples separate from parser/merge stress corpora
- avoid hand-jammed fixtures when a standards-derived positive example already exists

Current positive cases:

- `docs/requirements/ieee-1516-2025/encoding_auth_work_packet/05-example-foms/EncodingSmokeTest-2025.xml`
  - validates against `docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-DIF-2025.xsd`
- `docs/requirements/ieee-1516-2025/encoding_auth_work_packet/05-example-foms/SchemaValidProbe-2025.xml`
  - validates against `docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd`

Run the baseline report generator with:

- `./tools/fom-schema-baseline`

Generated artifacts land under:

- `analysis/fom_schema_baseline/fom_schema_baseline.json`
- `analysis/fom_schema_baseline/fom_schema_baseline.md`
