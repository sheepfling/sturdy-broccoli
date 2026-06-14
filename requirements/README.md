# Requirements

Use this page for requirement-surface classification.

If you want the smallest possible human workflow first, go to
[`../docs/requirements_crud.md`](../docs/requirements_crud.md).

The compact machine-readable source of truth is
[`source_of_truth.json`](source_of_truth.json). This README explains that file
for humans. [`surface_manifest.json`](surface_manifest.json) is now a generated
compatibility projection from it.

For normal repo maintenance, start with:

<!-- GENERATED:README_START_HERE:START -->
1. ../docs/requirements_crud.md
2. run ./tools/human-editability requirements-crud
3. run ./tools/human-editability requirements-read <MethodNameOrRequirementId>
4. run ./tools/human-editability requirements-create <RequirementIdOrArtifactId>
5. ../docs/requirements_trace_one_method.md
6. ../docs/requirements_edit_one_row.md
7. active_service_rows.csv
8. source_of_truth.json
9. surface_manifest.json
10. traceability_matrix.csv
<!-- GENERATED:README_START_HERE:END -->

The rule is simple:

- trace first
- edit one active row only if needed
- validate
- regenerate outputs

## Surface Types

### Active Authored

This is the normal edit surface when one mapping is wrong or missing:

- `active_service_rows.csv` is the normal row-edit surface
- `family_seed_rows.csv` is the small authored family/seed lane
- `source_of_truth.json` is the canonical machine-readable source
- `source_of_truth.json` also owns the traceability row header and status meanings
- `requirement_id_registry.yaml` is a generated compatibility registry
- `traceability_matrix.csv` is the generated compatibility merge
- `surface_manifest.json` is the generated compatibility projection
- `../analysis/traceability/requirements_authoring_index.md` separates normal `active_service` rows from `family_seed` rows
- `../analysis/traceability/active_service_requirements_index.md` is the generated active-only browse/search surface

### Generated

These are outputs. Do not hand-edit them:

- `../analysis/compliance/requirements_ledger.csv`
- `../analysis/traceability/service_trace_index.csv`
- `../analysis/traceability/service_trace_index.md`
- `../analysis/traceability/service_trace_index.json`

### Reference / Provenance

The broader clause catalogs and packet-facing reconciliation assets now live
under `requirements/reference/`.

They matter for larger reconciliation work, not for ordinary active-row
maintenance.

Examples:

- `reference/hla1516_1_clause_4_fm_service_decomposition.csv`
- `reference/hla1516_1_clause_6_object_management.csv`
- `reference/hla1516_1_tm_detailed_reconciliation.csv`
- `reference/hla1516_2_omt.csv`
- `reference/hla_1516_master_harmonization_index_v1_0.csv`

## Normal Edit Loop

If you need to add or repair one requirement row:

<!-- GENERATED:README_NORMAL_EDIT_LOOP:START -->
1. run ./tools/human-editability requirements-read <MethodNameOrRequirementId>
2. run ./tools/human-editability requirements-create <RequirementIdOrArtifactId> if you are adding a row
3. run ./tools/human-editability requirements-update <RequirementId> if you are changing a row
4. run ./tools/human-editability requirements-delete <RequirementId> if you are removing a row
5. edit active_service_rows.csv only if the trace shows the active mapping is wrong
6. edit family_seed_rows.csv only for deliberate clause-family harmonization
7. edit source_of_truth.json only if you truly need a new source or prefix family
8. run ./tools/human-editability check
9. run ./tools/human-editability generate-requirements-source
10. run ./tools/human-editability generate-trace-index
11. run ./tools/human-editability generate-requirements-authoring-index
12. run ./tools/human-editability generate-active-service-index
13. run ./tools/human-editability requirements-read <MethodNameOrRequirementId> again
<!-- GENERATED:README_NORMAL_EDIT_LOOP:END -->

## What To Ignore First

Do not start by reading or editing:

- `analysis/compliance/requirements_ledger.csv`
- `analysis/traceability/service_trace_index.*`
- everything under `reference/`

Those make the system look larger than the normal active-maintenance path
really is.

The machine-readable requirements source of truth lives in
[`source_of_truth.json`](source_of_truth.json). The compatibility projection
lives in [`surface_manifest.json`](surface_manifest.json). The compatibility
registry lives in
[`requirement_id_registry.yaml`](requirement_id_registry.yaml).

To print both the compact workflow and the surface split from the operator
surface:

<!-- GENERATED:README_OPERATOR_COMMANDS:START -->
```bash
./tools/human-editability requirements-crud
./tools/human-editability requirements-create HLA1516.1-TM-8.8-001
./tools/human-editability requirements-read timeAdvanceRequest
./tools/human-editability requirements-update REQ-RTI-TM-8_8-timeAdvanceRequest
./tools/human-editability requirements-delete REQ-RTI-TM-8_8-timeAdvanceRequest
./tools/human-editability requirements-flow
./tools/human-editability requirements-surfaces
./tools/human-editability requirements-surfaces --verbose
./tools/human-editability requirements-source
./tools/human-editability requirements-lanes
./tools/human-editability requirements-active
```
<!-- GENERATED:README_OPERATOR_COMMANDS:END -->

## When The Broader Catalogs Matter

Use the broader `requirements/reference/*.csv` family only when you are doing
work such as:

- clause-by-clause reconciliation
- imported packet harmonization
- detailed bridge maintenance
- framework or OMT family backfill

## Honest Test Rule

When you turn a requirement row into `mapped` or `partial`, attach concrete
evidence:

- a focused positive test
- an explicit negative test
- or a generated artifact that is itself regression-checked

Do not promote a row based only on nearby implementation.

## Read Next

1. [`../docs/requirements_crud.md`](../docs/requirements_crud.md)
2. [`../docs/requirements_trace_one_method.md`](../docs/requirements_trace_one_method.md)
3. [`../docs/requirements_edit_one_row.md`](../docs/requirements_edit_one_row.md)
4. [`../docs/requirements_traceability.md`](../docs/requirements_traceability.md)
5. [`../docs/requirements_authoring_map.md`](../docs/requirements_authoring_map.md)
