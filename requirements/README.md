# Requirements

This directory contains both:

- the active authored requirement mapping surface for day-to-day maintenance
- a larger reference/provenance catalog family for broader clause harmonization

The important distinction is simple.

## Start Here

Use this page for requirement-surface classification.

For normal repo maintenance, start with:

1. [`traceability_matrix.csv`](traceability_matrix.csv)
2. [`../docs/requirements_trace_one_method.md`](../docs/requirements_trace_one_method.md)
3. [`../docs/requirements_edit_one_row.md`](../docs/requirements_edit_one_row.md)
4. [`surface_manifest.json`](surface_manifest.json)

## Surface Types

### Active Authored

This is the normal edit surface when you missed one requirement row or one
mapping is wrong:

- `traceability_matrix.csv`
- `requirement_id_registry.yaml`
- `surface_manifest.json`

If you are adding or repairing one active requirement mapping, start here.

### Generated

These are outputs. Do not hand-edit them:

- `../analysis/compliance/requirements_ledger.csv`
- `../analysis/traceability/service_trace_index.csv`
- `../analysis/traceability/service_trace_index.md`
- `../analysis/traceability/service_trace_index.json`

### Reference / Provenance

Most of the other `requirements/*.csv` files are broader clause catalogs,
packet reconciliations, imported work-packet bridges, or detailed family
harmonization assets.

Those files are valid and useful, but they are not the normal starting point
for fixing one active mapping row.

Examples:

- `hla1516_1_clause_4_fm_service_decomposition.csv`
- `hla1516_1_clause_6_object_management.csv`
- `hla1516_1_tm_detailed_reconciliation.csv`
- `hla1516_2_omt.csv`
- `hla_1516_master_harmonization_index_v1_0.csv`

## Normal Edit Loop

If you need to add or repair one requirement row, the normal maintainer path
is:

1. edit `traceability_matrix.csv`
2. run `./tools/human-editability requirements-surfaces`
3. run `./tools/human-editability check`
4. run `./tools/human-editability generate-trace-index`
5. run `./tools/human-editability trace <MethodName>`

For the narrower guided lane, use
[`../docs/requirements_edit_one_row.md`](../docs/requirements_edit_one_row.md).

## What To Ignore First

Do not start by reading or editing:

- `analysis/compliance/requirements_ledger.csv`
- `analysis/traceability/service_trace_index.*`
- every `hla1516_*.csv` file in this directory

Those make the system look larger than the normal active-maintenance path
really is.

The machine-readable surface classification lives in
[`surface_manifest.json`](surface_manifest.json).
To print it from the operator surface, run:

```bash
./tools/human-editability requirements-surfaces
```

## When The Broader Catalogs Matter

Use the broader `requirements/*.csv` family only when you are doing work such
as:

- clause-by-clause reconciliation
- imported packet harmonization
- detailed bridge maintenance
- framework or OMT family backfill

That is real work, but it is a different task from “I need to add or fix one
active requirement mapping row.”

## Honest Test Rule

When you turn a requirement row into `mapped` or `partial`, attach concrete
evidence:

- a focused positive test
- an explicit negative test
- or a generated artifact that is itself regression-checked

Do not promote a row based only on nearby implementation.

## Read Next

1. [`../docs/requirements_trace_one_method.md`](../docs/requirements_trace_one_method.md)
2. [`../docs/requirements_edit_one_row.md`](../docs/requirements_edit_one_row.md)
3. [`../docs/requirements_traceability.md`](../docs/requirements_traceability.md)
4. [`../docs/requirements_authoring_map.md`](../docs/requirements_authoring_map.md)
