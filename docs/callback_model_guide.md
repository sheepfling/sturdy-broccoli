# Callback Model Guide

Use this page when you need to understand the difference between `HLA_EVOKED`
and `HLA_IMMEDIATE`, or when you need a single entry point for the tests and
implementation that prove the behavior.

## What The Models Mean

- `HLA_EVOKED`: callbacks are queued until the federate explicitly drains them
  with `evokeCallback(...)` or `evokeMultipleCallbacks(...)`.
- `HLA_IMMEDIATE`: callbacks may be delivered inline as part of the triggering
  service call when the backend supports inline immediate delivery.

The Python backend makes this explicit in
[`hla.backends.python1516e/callbacks.py`](../packages/hla-backend-python1516e/src/hla/backends/python1516e/callbacks.py)
and defaults to evoked delivery in
[`hla.backends.python1516e/state.py`](../packages/hla-backend-python1516e/src/hla/backends/python1516e/state.py).

## Where To Start

If you want the shortest proof path, start with the Python backend tests:

- [`tests/backends/test_python_backend_federation_extended.py`](../tests/backends/test_python_backend_federation_extended.py):
  connects both callback models and proves that evoked delivery requires an
  explicit drain while immediate delivery is visible immediately.
- [`tests/backends/test_python_backend_time_ddm_extended.py`](../tests/backends/test_python_backend_time_ddm_extended.py):
  proves inline immediate delivery for object callbacks and immediate-callback
  exception behavior during time-management operations.

Those two files are the best executable entry points for the callback-model
split in this workspace.

## Practical Rules

- Use `HLA_EVOKED` when you want the standard polling path and the broadest
  backend compatibility.
- Use `HLA_IMMEDIATE` when you need to prove inline delivery behavior or when a
  backend explicitly supports immediate callbacks.
- Do not assume every backend supports identical immediate semantics. The
  Python backend is the clearest local reference for the split, but vendor
  runtimes can still diverge on edge cases.

## Related Docs

- [`verification/callback_model_compliance.md`](verification/callback_model_compliance.md): compliance boundary and proof anchors
- [`architecture.md`](architecture.md): backend structure and callback-contract notes
- [`package_layout.md`](package_layout.md): where the backend and test code lives
- [`two_federate_quickstart.md`](two_federate_quickstart.md): first runnable example
- [`backend_conformance_matrix.md`](backend_conformance_matrix.md): clause-level behavior mapping
