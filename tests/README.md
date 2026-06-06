# Tests

Reserved for deterministic checks that are specific to the HLA 2010 workspace.

Good first tests:

- reference bundle presence checks
- clause inventory completeness checks
- traceability matrix shape checks
- completion-audit gate checks

Environment-aware markers:

- `requires_loopback_server`: skips local REST/gRPC host tests when the environment cannot bind `127.0.0.1` sockets.
