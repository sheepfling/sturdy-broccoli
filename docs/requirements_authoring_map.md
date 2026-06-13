# Requirements Authoring Map

This is the shortest reading path for someone who needs to move from one
requirement row to code, tests, and generated proof, or back again.

If you only need to trace one method rather than edit the broader mapping,
start with [requirements_trace_one_method.md](requirements_trace_one_method.md).

If you only need to fix one missing or wrong row, start with
[requirements_edit_one_row.md](requirements_edit_one_row.md).

This page is secondary reading. It should not be the first requirement doc a
new contributor opens.

Use this page for the ordered reading path.

Read these files in order:

1. [`docs/requirements_edit_one_row.md`](requirements_edit_one_row.md)
2. [`requirements/README.md`](../requirements/README.md)
3. [`requirements/surface_manifest.json`](../requirements/surface_manifest.json)
4. [`requirements/traceability_matrix.csv`](../requirements/traceability_matrix.csv)
5. [`docs/requirements_traceability.md`](requirements_traceability.md)
6. [`analysis/compliance/requirements_ledger.csv`](../analysis/compliance/requirements_ledger.csv)
7. [`analysis/traceability/service_trace_index.md`](../analysis/traceability/service_trace_index.md)
8. [`scripts/validate_traceability_paths.py`](../scripts/validate_traceability_paths.py)
9. [`src/hla2010_repo_internal/traceability.py`](../src/hla2010_repo_internal/traceability.py)

## Why These Files

- `requirements_edit_one_row.md`: shortest active-row editing path
- `requirements/README.md`: active versus generated versus reference classification
- `surface_manifest.json`: machine-readable source of truth for that classification
- `traceability_matrix.csv`: active authored requirement mapping surface
- `requirements_traceability.md`: broader traceability model and generated artifact meaning
- `requirements_ledger.csv`: generated normalized ledger used by checks and reporting
- `service_trace_index.md`: human-readable generated service trace index
- `validate_traceability_paths.py`: executable contract for refs and evidence
- `traceability.py`: shared resolver logic behind the operator flow

## Authoring Loop

When changing a requirement mapping:

1. Edit the active authored requirement input:
   [`requirements/traceability_matrix.csv`](../requirements/traceability_matrix.csv).
2. Run `./tools/human-editability requirements-surfaces`.
3. Run `./tools/human-editability requirement <RequirementId>`.
4. Run `./tools/human-editability check`.
5. Run `./tools/human-editability generate-trace-index`.
6. Run `./tools/human-editability trace <MethodName>`.
7. Confirm the test and artifact refs are still concrete.

## What To Ignore First

Do not start by editing generated files under `analysis/compliance/` or
`analysis/traceability/` by hand. Treat them as outputs.

The normal authored surface for active mapping work is
[`requirements/traceability_matrix.csv`](../requirements/traceability_matrix.csv).
Treat the generated ledger and trace indexes as outputs, and treat most of the
other `requirements/*.csv` catalogs as reference/provenance material unless you
are doing broader clause-harmonization work.

The authoritative classification for that split is
[`requirements/surface_manifest.json`](../requirements/surface_manifest.json),
and the shortest operator view is:

```bash
./tools/human-editability requirements-surfaces
```

## Read Next

1. [requirements_edit_one_row.md](requirements_edit_one_row.md)
2. [requirements_trace_one_method.md](requirements_trace_one_method.md)
3. [requirements_traceability.md](requirements_traceability.md)
4. [spec_reading_map.md](spec_reading_map.md)
5. [python_rti_reading_map.md](python_rti_reading_map.md)
