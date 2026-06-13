# Edit One Requirement Row

This is the shortest maintainer path for the most common requirements task:

"We missed one requirement row, or one mapping is wrong. What do I edit?"

## Normal Answer

In the normal case, edit only:

1. [`requirements/traceability_matrix.csv`](../requirements/traceability_matrix.csv)
2. the implementation file the row points at
3. the focused test or artifact refs that prove the row

Do not start by editing generated files under:

- `analysis/compliance/`
- `analysis/traceability/`

Those are outputs.

Use this operator command first when you already know the requirement id:

```bash
./tools/human-editability requirement REQ-RTI-TM-8_8-timeAdvanceRequest
```

That prints both:

- the active authored row from `requirements/traceability_matrix.csv`
- the generated trace view from `analysis/compliance/requirements_ledger.csv`

## Active Vs Generated Vs Reference

Treat the requirement surfaces like this:

- Active authored:
  `requirements/traceability_matrix.csv`
- Generated:
  `analysis/compliance/requirements_ledger.csv`
  `analysis/traceability/service_trace_index.*`
- Reference / provenance:
  most of the other `requirements/*.csv` clause and reconciliation catalogs

The fuller classification lives in
[`../requirements/README.md`](../requirements/README.md), and the machine-readable
source of truth is
[`../requirements/surface_manifest.json`](../requirements/surface_manifest.json).

The human-readable generated trace output lives at
[`../analysis/traceability/service_trace_index.md`](../analysis/traceability/service_trace_index.md).

If you are only fixing one missing or wrong active mapping, the active authored
surface is the place to start.

## Columns That Usually Matter

For one service-level row, you usually care about:

- `requirement_id`
- `clause`
- `canonical_topic`
- `current_artifact_id`
- `implementation_refs`
- `test_refs`
- `artifact_refs`
- `status`
- `notes`

The validator is strict about refs and evidence, but the edit surface itself is
still just the row.

## One-Row Edit Loop

1. Find the row in [`requirements/traceability_matrix.csv`](../requirements/traceability_matrix.csv).
2. Fix the implementation, test, artifact, status, or note fields.
3. Run `./tools/human-editability requirements-surfaces`.
4. Run `./tools/human-editability requirement <RequirementId>`.
5. Run `./tools/human-editability check`.
6. Run `./tools/human-editability generate-trace-index`.
7. Run `./tools/human-editability trace <MethodName>`.
8. Confirm the trace lands on the expected implementation and evidence.

## Example

If you missed a support-service row, use:

```bash
./tools/human-editability trace getHLAversion
```

Then edit:

1. [`requirements/traceability_matrix.csv`](../requirements/traceability_matrix.csv)
2. [`packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py`](../packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py)
3. [`tests/scenarios/test_support_services_backend_matrix.py`](../tests/scenarios/test_support_services_backend_matrix.py)

## What This Is Not

This is not the full clause harmonization workflow.

If you are reconciling imported clause catalogs, decomposition seeds, or packet
history, that is a broader reference/provenance task. For ordinary active
traceability maintenance, keep the scope narrow and stay on the active authored
surface first.

## Read Next

1. [requirements_authoring_map.md](requirements_authoring_map.md)
2. [requirements_trace_one_method.md](requirements_trace_one_method.md)
3. [requirements_traceability.md](requirements_traceability.md)
