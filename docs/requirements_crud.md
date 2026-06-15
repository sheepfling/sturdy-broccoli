# Requirements CRUD

Use this page when you want the smallest possible requirements workflow.

If you only need to create, read, update, or delete one active requirement row,
start here instead of reading the broader requirements surface map.

The requirements surface is edition-selectable in structure, but the current
selected requirement document set is `2010` only. Active rows and authored
requirement document titles should therefore stay explicitly tied to the 2010
edition unless you are deliberately extending the registry structure itself.

Operator summary:

```bash
./tools/human-editability requirements-crud
```

Smallest direct commands:

```bash
./tools/human-editability requirements-create <RequirementIdOrArtifactId>
./tools/human-editability requirements-read <MethodNameOrRequirementId>
./tools/human-editability requirements-update <RequirementId>
./tools/human-editability requirements-delete <RequirementId>
```

<!-- GENERATED:CRUD_ACTIONS:START -->
## Create
add one missing active requirement row.

Edit here: `requirements/active_service_rows.csv`

Commands:

```bash
./tools/human-editability requirements-create <RequirementIdOrArtifactId>
./tools/human-editability check
./tools/human-editability generate-requirements-source
./tools/human-editability generate-trace-index
```

Notes:
- Use a standards-row id in requirement_id.
- Put REQ-* artifact ids in current_artifact_id.

## Read
see one requirement row and its proof without guessing.

Commands:

```bash
./tools/human-editability requirements-read <MethodNameOrRequirementId>
./tools/human-editability trace-summary <MethodName>
./tools/human-editability requirement <RequirementId>
```

Notes:
- Start with trace-summary when you know a method.
- Start with requirement when you already know the requirement id.

## Update
change one existing active requirement row.

Edit here: `requirements/active_service_rows.csv`

Commands:

```bash
./tools/human-editability requirements-update <RequirementId>
./tools/human-editability check
./tools/human-editability generate-requirements-source
./tools/human-editability generate-trace-index
```

Notes:
- Edit family_seed rows only for deliberate clause-family harmonization.
- Mapped rows need test_refs or artifact_refs.

## Delete
remove one wrong or obsolete active requirement row.

Edit here: `requirements/active_service_rows.csv`

Commands:

```bash
./tools/human-editability requirements-delete <RequirementId>
./tools/human-editability check
./tools/human-editability generate-requirements-source
./tools/human-editability generate-trace-index
```

Notes:
- Delete the row from active_service_rows.csv, not from generated outputs.
- Re-run trace-summary afterward to confirm the requirement is really gone or remapped.
<!-- GENERATED:CRUD_ACTIONS:END -->

## Read Next

1. [requirements_trace_one_method.md](requirements_trace_one_method.md)
2. [requirements_edit_one_row.md](requirements_edit_one_row.md)
3. [../requirements/README.md](../requirements/README.md)
