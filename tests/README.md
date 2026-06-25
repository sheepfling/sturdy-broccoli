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
- `tests/requirements/`: 2025 finish-line, route-parity, backend-audit, and wording-boundary checks for the main `python1516_2025` RTI lane.
- `tests/`: direct executable slices that have not been grouped further yet.

## Environment-Aware Markers

- `requires_loopback_server`: skips local REST/gRPC host tests when the environment cannot bind `127.0.0.1` sockets.

## Read Next

1. [`../docs/first_run.md`](../docs/first_run.md)
2. [`../docs/python_environment.md`](../docs/python_environment.md)
3. [`../docs/two_federate_quickstart.md`](../docs/two_federate_quickstart.md)
