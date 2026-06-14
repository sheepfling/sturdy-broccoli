# Requirements Authoring Map

This page remains only as a thin compatibility map.

You should usually start with:

1. run `./tools/human-editability requirements-flow`
2. [requirements_trace_one_method.md](requirements_trace_one_method.md)
3. [requirements_edit_one_row.md](requirements_edit_one_row.md)
4. [../requirements/README.md](../requirements/README.md)

Use this page only when another doc or an older note still points here.

## Why These Files

- `requirements_trace_one_method.md`: primary human trace lane
- `requirements_edit_one_row.md`: narrow active-row repair lane
- `requirements/README.md`: human explanation of the source-of-truth split
- `requirements/source_of_truth.json`: canonical machine-readable source of truth
- `requirements/source_of_truth.json`: also owns the source/prefix family registry policy
- `requirements/active_service_rows.csv`: normal authored service-row source
- `requirements/family_seed_rows.csv`: small authored family/seed source
- `requirements/requirement_id_registry.yaml`: generated compatibility registry
- `requirements/traceability_matrix.csv`: generated compatibility merge still used by older tools
- `requirements/surface_manifest.json`: generated compatibility projection
- `requirements_traceability.md`: broader traceability model and generated artifact meaning

## Authoring Loop

When changing a requirement mapping:

<!-- GENERATED:AUTHORING_MAP_LOOP:START -->
1. Print the compact lane with ./tools/human-editability requirements-flow.
2. Trace the method first with ./tools/human-editability trace-summary <MethodName>.
3. If the active mapping row is wrong, edit requirements/active_service_rows.csv.
4. If the row is missing, print a template first with ./tools/human-editability requirement-template <RequirementIdOrArtifactId>.
5. Run ./tools/human-editability requirement <RequirementId>.
6. Run ./tools/human-editability check.
7. Run ./tools/human-editability generate-requirements-source.
8. Run ./tools/human-editability generate-trace-index.
9. Run ./tools/human-editability trace-summary <MethodName> again.
<!-- GENERATED:AUTHORING_MAP_LOOP:END -->

## Read Next

1. [requirements_trace_one_method.md](requirements_trace_one_method.md)
2. [requirements_edit_one_row.md](requirements_edit_one_row.md)
3. [../requirements/README.md](../requirements/README.md)
4. [requirements_traceability.md](requirements_traceability.md)
