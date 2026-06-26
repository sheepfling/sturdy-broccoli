# Requirement Compliance Exports

Use this page when the question is:

- can we hand a manager a spreadsheet instead of a markdown packet?
- which command generates the current 2010 and 2025 backend-compliance exports?
- which canonical requirement sources feed those spreadsheets?

Short answer:

- yes
- CSV and XLSX are supported as presentation outputs
- markdown, JSON, and repo-native CSV ledgers remain the canonical working surfaces

## Output Contract

Run:

```bash
python3 scripts/generate_requirement_compliance_spreadsheets.py
```

Default output directory:

- `analysis/compliance/presentation_packets/`

Generated files:

- `requirements_2010_backend_compliance_summary.csv`
- `requirements_2010_backend_compliance_detail.csv`
- `requirements_2010_backend_compliance.xlsx`
- `requirements_2025_backend_compliance_summary.csv`
- `requirements_2025_backend_compliance_detail.csv`
- `requirements_2025_backend_compliance.xlsx`

Each workbook contains:

- `summary`
- `detail`
- `metadata`

## Edition Sources

The export is a secondary presentation layer over canonical repo-owned sources.

### 2010 / 1516e

Canonical source:

- `analysis/compliance/requirements_matrix_2010.csv`

Human-facing front doors:

- [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md)
- [`../../requirements/2010/README.md`](../../requirements/2010/README.md)

The 2010 detail export carries:

- requirement and matrix identifiers
- canonical status
- backend resolution columns for `python`, `certi`, `pitch`, and `portico`
- claim-scope and artifact references

### 2025 / 1516_2025

Canonical source:

- `requirements/2025/harmonization/hla_2025_harmonization_worklist.csv`

Human-facing front doors:

- [`../requirements/ieee-1516-2025/README.md`](../requirements/ieee-1516-2025/README.md)
- [`../../requirements/2025/README.md`](../../requirements/2025/README.md)

The 2025 detail export carries:

- grouped requirement bucket identity
- canonical disposition
- backend-resolution columns for:
  - `python_runtime_resolution`
  - `java_cpp_binding_resolution`
  - `hosted_fedpro_resolution`
  - `pitch_202x_resolution`
- row counts, backend-reference pointers, and acceptance gates

## Presentation Rule

Use the spreadsheets for:

- boss review
- status meetings
- offline sorting and filtering
- attaching a current backend-compliance snapshot to a work packet

Do not treat the spreadsheets as the canonical owner surface.
When a requirement status changes, update the source-side ledgers and proof docs
first, then regenerate the exports.

## Repeatable Workflow

1. update canonical requirement or harmonization sources
2. run the normal doc or test proof that justifies the change
3. regenerate the spreadsheet packet
4. hand off the `.xlsx` workbook or the `.csv` files as needed

## Verification

The export path is regression-checked by:

- [`../../tests/requirements/test_requirement_compliance_spreadsheet_export.py`](../../tests/requirements/test_requirement_compliance_spreadsheet_export.py)

Recommended local check:

```bash
python3 -m pytest tests/requirements/test_requirement_compliance_spreadsheet_export.py -q
```

## Related Docs

- [README.md](README.md)
- [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md)
- [`../requirements/ieee-1516-2025/README.md`](../requirements/ieee-1516-2025/README.md)
- [`../../requirements/README.md`](../../requirements/README.md)
