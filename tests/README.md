# Tests

Reserved for deterministic checks that are specific to the HLA 2010 workspace.

The repo also carries the current IEEE 1516.1-2025 Python RTI lane. Treat
`hla-backend-python1516-2025` as the main 2025 runtime behind those tests and treat
`hla-backend-shim` only as a legacy compatibility shim.

## Start Here

Fastest human-friendly starting points:

- `./tools/test`: default pytest wrapper once `.venv` is active
- `python examples/backend_recording.py`: simplest runtime smoke before wider test work
- `source .venv/bin/activate && ./tools/two-federate`: first artifact-producing two-federate flow

Do not start with vendor/runtime-dependent suites unless the base Python path is
already working.

For the 2025 lane specifically, the first architecture/proof surfaces to read
after bootstrap are:

- `docs/python_rti_backend.md`
- `docs/python_rti_reading_map.md`
- `docs/verification/time_model_compliance.md`

The routine 2025 proof commands behind those surfaces are:

- `./tools/python verify-main-2025` for the normal direct `python1516_2025`
  main-surface proof lane
- `./tools/python verify-routes-2025` when you also need the bounded hosted
  `python1516_2025-fedpro-grpc` hygiene lane

If the question is specifically "did we break join, resign, destroy, or
not-joined guard behavior?", do not jump straight to the broader 2025 route or
transport lanes. Start with:

- `./tools/test-focus run execution-membership`

That focused target owns the basic execution-state rule rerun surface for both
editions:

- 2010 federation-management rows
  `HLA1516.1-FM-4_6-RTIAPI-001-EXC`,
  `HLA1516.1-FM-4_9-RTIAPI-001-EXC`, and
  `HLA1516.1-FM-4_10-RTIAPI-001-EXC`
- 2010 object-management rows
  `HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001`,
  `HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001`,
  `HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001`,
  `HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`,
  `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`,
  `HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001`,
  `HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`,
  `HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`, and
  `HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`
- 2025 federation-management rows `HLA2025-FI-SVC-005`,
  `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-010`, and `HLA2025-FI-SVC-011`
- 2025 object-management rows `HLA2025-FI-SVC-051`, `HLA2025-FI-SVC-053`,
  `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-061`,
  `HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-070`, and `HLA2025-FI-SVC-077`

Use the owner docs when you need the full requirement-to-test chain:

- `../docs/test_surface.md`
- `../docs/junior_test_diagnosis_runbook.md`
- `../docs/verification/shard_registry.md`
- `../docs/verification/view_registry.md`
- `../docs/requirements/ieee-1516-2010/README.md`
- `../docs/requirements/ieee-1516-2025/README.md`

## Test Families

- `tests/backends/`: backend adapter, shim, and generic backend-unit coverage. Start here for pure API and adapter behavior; do not start here if you only want the first runnable scenario.
- `tests/factories/`: handle, time, parser, and FOM-resolution construction tests. Use these for spec/data-model debugging rather than end-to-end runtime checks.
- `tests/mom/`: MOM catalog and MOM-focused executable slices. Use these when working on MOM/MIM semantics, not for first-run smoke.
- `tests/scenarios/`: end-to-end scenario and startup-flow tests, including the human-meaningful two-federate story. This is the best directory after base bootstrap succeeds.
- `tests/transport/`: REST/gRPC transport and hosted-server tests. These assume the local session can bind loopback sockets; do not start here on a constrained host.
- `tests/runtime/`: runtime discovery, bridge availability, and local runtime smoke tests. Use these when checking environment shape rather than clause semantics.
- `tests/time/`: time-management and MOM/time semantic slices. Use these after the plain exchange path is already healthy.
- `tests/vendors/`: real-vendor backend matrices and vendor smoke tests. These are environment-dependent and are not a newcomer entrypoint.
- `tests/verification/`: conformance, requirements-ledger, MOM negative-matrix, and spec-traceability tests. Use these for defended compliance work, not first-run validation.
- `tests/requirements/`: canonical 2025 requirement-owner, route-parity, backend-resolution, imported-packet, and downstream closeout-reporting checks for the main `python1516_2025` RTI lane. Read these as requirement-surface and reporting-surface tests, not as plan/worklist truth.
- `tests/`: direct executable slices that have not been grouped further yet.

## Environment-Aware Markers

- `requires_loopback_server`: skips local REST/gRPC host tests when the environment cannot bind `127.0.0.1` sockets.

## Read Next

1. [`../docs/first_run.md`](../docs/first_run.md)
2. [`../docs/python_environment.md`](../docs/python_environment.md)
3. [`../docs/two_federate_quickstart.md`](../docs/two_federate_quickstart.md)
