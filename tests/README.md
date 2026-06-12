# Tests

Reserved for deterministic checks that are specific to the HLA 2010 workspace.

## Start Here

Fastest human-friendly starting points:

- `./tools/test`: default pytest wrapper once `.venv` is active
- `python examples/backend_recording.py`: simplest runtime smoke before wider test work
- `source .venv/bin/activate && ./tools/two-federate`: first artifact-producing two-federate flow

Do not start with vendor/runtime-dependent suites unless the base Python path is
already working.

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
- `tests/`: direct executable slices that have not been grouped further yet.

## Environment-Aware Markers

- `requires_loopback_server`: skips local REST/gRPC host tests when the environment cannot bind `127.0.0.1` sockets.

## Read Next

1. [`../docs/first_run.md`](../docs/first_run.md)
2. [`../docs/python_environment.md`](../docs/python_environment.md)
3. [`../docs/two_federate_quickstart.md`](../docs/two_federate_quickstart.md)
