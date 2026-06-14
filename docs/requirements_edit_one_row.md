# Edit One Requirement Row

This is the shortest maintainer path for the most common requirements task:

"We missed one requirement row, or one mapping is wrong. What do I edit?"

## Normal Answer

In the normal case, edit only:

1. [`requirements/active_service_rows.csv`](../requirements/active_service_rows.csv)
2. the implementation file the row points at
3. the focused test or artifact refs that prove the row

If you are adding a missing row instead of repairing an existing one, print the
row shape first:

<!-- GENERATED:EDIT_ONE_ROW_DISCOVERY_COMMANDS:START -->
```bash
./tools/human-editability requirements-read timeAdvanceRequest
./tools/human-editability requirements-create HLA1516.1-TM-8.8-001
./tools/human-editability requirements-create REQ-RTI-TM-8_8-timeAdvanceRequest
./tools/human-editability requirements-update REQ-RTI-TM-8_8-timeAdvanceRequest
./tools/human-editability requirements-delete REQ-RTI-TM-8_8-timeAdvanceRequest
```
<!-- GENERATED:EDIT_ONE_ROW_DISCOVERY_COMMANDS:END -->

Do not start by editing generated files under:

- `analysis/compliance/`
- `analysis/traceability/`

Those are outputs.

Use this operator command first when you already know the requirement id:

```bash
./tools/human-editability requirements-read REQ-RTI-TM-8_8-timeAdvanceRequest
./tools/human-editability requirements-update REQ-RTI-TM-8_8-timeAdvanceRequest
```

That prints both:

- the active authored row from `requirements/active_service_rows.csv`
- the generated trace view from `analysis/compliance/requirements_ledger.csv`

## Active Vs Generated Vs Reference

Treat the requirement surfaces like this:

- Active authored:
  `requirements/active_service_rows.csv` is the normal row-edit surface
  `requirements/family_seed_rows.csv` is the small authored family/seed lane
  `requirements/source_of_truth.json` is the canonical machine-readable source
  source/prefix family policy, row header, and status meanings now live inside
  `requirements/source_of_truth.json`
  `requirements/traceability_matrix.csv` is the generated compatibility merge
  `requirements/surface_manifest.json` is the generated compatibility projection
  `requirements/requirement_id_registry.yaml` is generated compatibility output
- Generated:
  `analysis/compliance/requirements_ledger.csv`
  `analysis/traceability/service_trace_index.*`
- Reference / provenance:
  the broader clause and reconciliation catalogs under
  `requirements/reference/`

If you are only fixing one missing or wrong active mapping, the active authored
surface is the place to start. Use [`../requirements/README.md`](../requirements/README.md)
only when you need the fuller surface classification.
The human-readable generated trace view lives at
[`../analysis/traceability/service_trace_index.md`](../analysis/traceability/service_trace_index.md).

## Columns That Usually Matter

For one service-level row, you usually care about:

<!-- GENERATED:EDIT_ONE_ROW_IMPORTANT_COLUMNS:START -->
- `requirement_id`
- `clause`
- `canonical_topic`
- `current_artifact_id`
- `implementation_refs`
- `test_refs`
- `artifact_refs`
- `status`
- `notes`
<!-- GENERATED:EDIT_ONE_ROW_IMPORTANT_COLUMNS:END -->

## One-Row Edit Loop

<!-- GENERATED:EDIT_ONE_ROW_LOOP:START -->
1. Run ./tools/human-editability requirements-read <MethodNameOrRequirementId>.
2. If you are adding a row, run ./tools/human-editability requirements-create <RequirementIdOrArtifactId>.
3. If you are changing a row, run ./tools/human-editability requirements-update <RequirementId>.
4. If you are removing a row, run ./tools/human-editability requirements-delete <RequirementId>.
5. Find the row in requirements/active_service_rows.csv.
6. Fix the implementation, test, artifact, status, or note fields.
7. Run ./tools/human-editability requirements-surfaces only when you truly need the broader surface map.
8. Run ./tools/human-editability check.
9. Run ./tools/human-editability generate-requirements-source.
10. Run ./tools/human-editability generate-trace-index.
11. Run ./tools/human-editability generate-requirements-authoring-index.
12. Run ./tools/human-editability generate-active-service-index.
13. Run ./tools/human-editability requirements-read <MethodNameOrRequirementId>.
14. Confirm the trace lands on the expected implementation and evidence.
<!-- GENERATED:EDIT_ONE_ROW_LOOP:END -->

## Example

If you missed a support-service row, use:

```bash
./tools/human-editability trace-summary getHLAversion
./tools/human-editability trace getHLAversion
```

Then edit:

1. [`requirements/active_service_rows.csv`](../requirements/active_service_rows.csv)
2. [`packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py)
3. [`tests/scenarios/test_support_services_backend_matrix.py`](../tests/scenarios/test_support_services_backend_matrix.py)

## What This Is Not

This is not the full clause harmonization workflow.

If you are reconciling imported clause catalogs, decomposition seeds, or packet
history, that is a broader reference/provenance task. For ordinary active
traceability maintenance, keep the scope narrow and stay on the active authored
surface first. In the normal case that means one command path and one file:
`./tools/human-editability requirements-create ...` and
`requirements/active_service_rows.csv`.

## Read Next

1. [requirements_trace_one_method.md](requirements_trace_one_method.md)
2. [requirements_traceability.md](requirements_traceability.md)
3. [requirements_authoring_map.md](requirements_authoring_map.md)
