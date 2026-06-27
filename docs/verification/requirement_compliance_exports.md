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

Operational note:

- this output directory is a generated presentation surface, not a checked-in
  owner surface
- in the current repo policy, `analysis/compliance/presentation_packets/` is
  ignored by git
- regenerate these files when you need a fresh handoff packet, but do not use
  the absence of a `git diff` there as evidence that nothing changed in the
  canonical requirement story
- do not treat checked-in historical or comparison snapshots such as
  `analysis/compliance/compliance.before/` as the current owner surface or the
  current spreadsheet handoff packet; they are not the live closeout answer

Generated files:

- `requirements_2010_backend_compliance_summary.csv`
- `requirements_2010_backend_compliance_detail.csv`
- `requirements_2010_backend_compliance_policy_parents.csv`
- `requirements_2010_backend_compliance.xlsx`
- `requirements_2025_backend_compliance_summary.csv`
- `requirements_2025_backend_compliance_detail.csv`
- `requirements_2025_backend_compliance.xlsx`

Each workbook contains:

- `summary`
- `detail`
- `metadata`
- `policy_parents` for the `2010` workbook only

## Edition Sources

The export is a secondary presentation layer over canonical repo-owned sources.

### 2010 / 1516e

Canonical source:

- `analysis/compliance/requirements_matrix_2010.csv`

Human-facing front doors:

- [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md)
- [`../../requirements/2010/README.md`](../../requirements/2010/README.md)
- [`../plans/2010_python_rti_bounded_family_execution_worklist.md`](../plans/2010_python_rti_bounded_family_execution_worklist.md)

The 2010 detail export carries:

- requirement and matrix identifiers
- canonical status
- backend resolution columns for `python`, `certi`, `pitch`, and `portico`
- claim-scope and artifact references

Read those `2010` columns with this split:

- `canonical_status` answers requirement coverage state only
- `python_runtime_disposition` answers whether the direct Python `2010` lane is
  verified, bounded, blocked, not applicable, or still needs explicit
  classification
- hosted `gRPC`/`REST` replay, when present in titles, notes, or artifact refs,
  is separate route evidence rather than a second meaning of canonical status
- vendor disposition columns answer backend-specific support, not whether a
  hosted replay row exists for Python

The `2010` policy-parent export carries:

- the `9 broad partial rows` intentionally defended by supported-subset proof
- each broad requirement ID and policy basis
- the exact passing supported-subset child IDs that justify the bounded claim
- a direct reminder that this surface is `not an open Python gap list`

For `2010`, read the spreadsheet detail rows together with:

- the canonical owner front door in
  [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md)
- the current bounded-family execution companion in
  [`../plans/2010_python_rti_bounded_family_execution_worklist.md`](../plans/2010_python_rti_bounded_family_execution_worklist.md)
- the supported-subset and defended-partials ledgers in
  [`../../analysis/compliance/supported_subset_policy.md`](../../analysis/compliance/supported_subset_policy.md)
  and
  [`../../analysis/compliance/defended_partials_index.md`](../../analysis/compliance/defended_partials_index.md)

That keeps manager-facing packet review separate from:

- canonical row ownership
- mixed-backend boundary reading
- bounded family tightening decisions
- defended policy-parent partials versus actual unresolved runtime gaps

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

Read those `2025` columns with this split:

- `canonical_disposition` answers coverage state only
- `python_runtime_resolution` answers whether the direct `python1516_2025`
  lane is the real proof owner, a bounded runtime surface, or an explicit
  exclusion
- `java_cpp_binding_resolution` answers whether Java/C++ rows are
  wrapper-only binding surfaces over `python1516_2025` or have no active
  behavior-support claim
- `hosted_fedpro_resolution` answers whether FedPro is a bounded hosted-route
  surface over `python1516_2025` rather than an independent RTI owner
- `pitch_202x_resolution` answers whether any Pitch proto HLA 4 / `202X`
  overlap is explicit vendor-resolution context rather than inferred grouped
  coverage

## Presentation Rule

Use the spreadsheets for:

- boss review
- status meetings
- offline sorting and filtering
- attaching a current backend-compliance snapshot to a work packet

For `2025`, keep these presentation metrics separate:

- `100% dispositioned` across all `691` tracked rows
- `100% covered` across the `645` active normative non-retired
  non-umbrella rows
- explicit separate counts for:
  - `duplicate/umbrella`
  - `retired/legacy-only`

Do not compress those into one manager-facing percentage without naming the
denominator.

Current packet snapshot:

- `2025` grouped packet summary currently reports:
  - `64` grouped buckets
  - `57` `covered`
  - `5` `duplicate/umbrella`
  - `2` `retired/legacy-only`
- `2010` packet summary currently reports:
  - `931` backend-compliance matrix rows
  - `865` `pass`
  - `40` `implemented-slice`
  - `1` `implemented-smoke`
  - `25` `partial`
  - `9` defended policy-parent partial rows backed by `23` passing supported-subset children

Interpret those packet counts together with the edition-specific owner docs.
They are not one shared cross-edition denominator.

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
- [`../plans/2010_python_rti_bounded_family_execution_worklist.md`](../plans/2010_python_rti_bounded_family_execution_worklist.md)
- [`../../requirements/README.md`](../../requirements/README.md)
