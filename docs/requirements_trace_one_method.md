# Trace One Method

This is the shortest maintainer path for answering one question:

"What requirement owns this method, where is the implementation, and what test
proves it?"

Use this when you do not want to read the whole traceability stack first.

## The One Command

Start here:

<!-- GENERATED:TRACE_ONE_METHOD_INTRO_COMMANDS:START -->
```bash
./tools/human-editability requirements-flow
./tools/human-editability trace-summary getHLAversion
./tools/human-editability trace getHLAversion
```
<!-- GENERATED:TRACE_ONE_METHOD_INTRO_COMMANDS:END -->

Or for a stateful service:

```bash
./tools/human-editability trace-summary timeAdvanceRequest
./tools/human-editability trace timeAdvanceRequest
```

The summary command is the canonical human entrypoint. Use the full `trace`
command only when you need the expanded artifact view.

It should tell you:

1. requirement id
2. IEEE section
3. Python method name
4. implementation symbol
5. implementation file
6. focused test evidence
7. artifact evidence

If it does not tell you those things, the repo is still too hard to trace.

## Recommended First Example

<!-- GENERATED:TRACE_ONE_METHOD_FIRST_EXAMPLE:START -->
Start with `getHLAversion`.

It is the smallest requirement-to-code path because it:

- resolves to one clear requirement row
- lands on one plain Python RTI implementation file
- has direct focused tests
- does not require time-management context first

Run:

```bash
./tools/human-editability trace-summary getHLAversion
./tools/human-editability trace getHLAversion
```

Then open:

1. packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py
2. tests/scenarios/test_support_services_backend_matrix.py
3. requirements/active_service_rows.csv
<!-- GENERATED:TRACE_ONE_METHOD_FIRST_EXAMPLE:END -->

## Stateful Example

<!-- GENERATED:TRACE_ONE_METHOD_STATEFUL_EXAMPLE:START -->
After that, use `timeAdvanceRequest`.

Run:

```bash
./tools/human-editability trace-summary timeAdvanceRequest
./tools/human-editability trace timeAdvanceRequest
```

Then open:

1. packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py
2. tests/time/test_mom_mim_time_v10.py
3. requirements/active_service_rows.csv
<!-- GENERATED:TRACE_ONE_METHOD_STATEFUL_EXAMPLE:END -->

## Trace Loop

Use this loop when changing a requirement mapping or validating one code path:

1. Run `./tools/human-editability trace-summary <MethodName>`.
2. Open the implementation file the command prints.
3. Open one focused positive test from the command output.
4. If you changed requirement input rows, run validation.
5. Regenerate the trace index only when the source mapping changed.
6. Run the summary again and confirm it still lands on the right code.

Commands:

<!-- GENERATED:TRACE_ONE_METHOD_LOOP_COMMANDS:START -->
```bash
./tools/human-editability trace-summary getHLAversion
./tools/human-editability trace getHLAversion
./tools/human-editability requirements-lanes
./tools/human-editability requirements-active timeAdvanceRequest
./tools/human-editability requirement-template REQ-RTI-SUP-10_25-getHLAversion
./tools/human-editability check
./tools/human-editability generate-requirements-source
./tools/human-editability generate-trace-index
./tools/human-editability trace-summary getHLAversion
./tools/human-editability trace getHLAversion
```
<!-- GENERATED:TRACE_ONE_METHOD_LOOP_COMMANDS:END -->

## What To Edit

In the normal case, edit only:

- `requirements/active_service_rows.csv` when the mapping itself is wrong
- the implementation file the trace command points at
- the focused tests that prove that method

If the row is missing entirely, print a template first with
`./tools/human-editability requirement-template <RequirementIdOrArtifactId>`.

Do not start by editing:

- `analysis/compliance/requirements_ledger.csv`
- `analysis/traceability/service_trace_index.*`
- other generated files under `analysis/`

Treat those as outputs.

## Backing Files

You only need these after the one-command path is already clear:

- `requirements/active_service_rows.csv`
- `requirements/traceability_matrix.csv`
- `analysis/compliance/requirements_ledger.csv`
- `analysis/traceability/service_trace_index.md`
- `scripts/validate_traceability_paths.py`
- `src/hla2010_repo_internal/traceability.py`

Those are implementation assets behind the human path, not equal-priority
starting points.

The canonical machine-readable source of truth for the requirements surfaces is
`requirements/source_of_truth.json`. Use that file when you need the compact
repo-wide contract rather than this one-method walkthrough.

## Read Next

1. [requirements_traceability.md](requirements_traceability.md)
2. [../requirements/README.md](../requirements/README.md)
3. [requirements_authoring_map.md](requirements_authoring_map.md)
4. [python_rti_edit_one_service.md](python_rti_edit_one_service.md)
