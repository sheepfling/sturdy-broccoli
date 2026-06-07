# Tests

Reserved for deterministic checks that are specific to the HLA 2010 workspace.

Current layout:

- `tests/backends/`: backend adapter, shim, and generic backend smoke tests
- `tests/factories/`: handle/time/factory construction and FOM resolution tests
- `tests/mom/`: MOM catalog and MOM-focused executable slices
- `tests/scenarios/`: end-to-end scenario and startup-flow tests
- `tests/transport/`: REST/gRPC transport and hosted-server tests
- `tests/runtime/`: runtime discovery, bridge availability, and local runtime smoke tests
- `tests/time/`: time-management and MOM/time semantic slices
- `tests/vendors/`: real-vendor backend matrices and vendor smoke tests
- `tests/verification/`: conformance, requirements-ledger, MOM negative-matrix, and spec-traceability tests with coordinated evidence-path updates
- `tests/`: remaining direct executable slices that have not been grouped further yet

Good first tests:

- reference bundle presence checks
- clause inventory completeness checks
- traceability matrix shape checks
- completion-audit gate checks

Environment-aware markers:

- `requires_loopback_server`: skips local REST/gRPC host tests when the environment cannot bind `127.0.0.1` sockets.
