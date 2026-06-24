# Callback Model Compliance

This page explains how the repo implements the HLA callback delivery split and
what evidence we use to treat that behavior as compliant for the supported
Python backend paths.

## Scope

The callback model here is the RTI-side delivery contract for federate
callbacks:

- `HLA_EVOKED`: callbacks are queued until the federate explicitly drains them
  with `evokeCallback(...)` or `evokeMultipleCallbacks(...)`.
- `HLA_IMMEDIATE`: callbacks may be delivered inline as part of the service
  call that triggered them when the backend permits inline delivery.

The repo treats this as a backend behavior contract, not as a separate public
API surface.

## How It Works

The reference Python backend implementation is explicit:

- [`hla.backends.inmemory/state.py`](../../packages/hla-backend-inmemory/src/hla/backends/inmemory/state.py)
  stores the callback model on each federate state and defaults to
  `HLA_EVOKED`.
- [`hla.backends.inmemory/callbacks.py`](../../packages/hla-backend-inmemory/src/hla/backends/inmemory/callbacks.py)
  routes callback delivery:
  - immediate callbacks are invoked inline when
    `immediate_callbacks_inline` is enabled
  - all other callbacks are queued for later evocation via the callback drain
    services
- The callback invocation path preserves the usual re-entrancy guards and wraps
  unexpected ambassador failures in `FederateInternalError`.

For the primary 2025 lane, the same split is now explicit in the dedicated
runtime too:

- [`hla.backends.python2025.callback_runtime`](../../packages/hla-backend-python2025/src/hla/backends/python2025/callback_runtime.py)
  honors `HLA_EVOKED` by queueing until explicit drain and honors
  `HLA_IMMEDIATE` by delivering inline when callbacks are enabled
- [`hla.backends.python2025.federation_management_runtime`](../../packages/hla-backend-python2025/src/hla/backends/python2025/federation_management_runtime.py)
  stores the selected callback model on the connected `python1516_2025` federate
- [`hla.backends.python2025.federation_time_surface_mixin`](../../packages/hla-backend-python2025/src/hla/backends/python2025/federation_time_surface_mixin.py)
  exposes the public drain/enable/disable services over that runtime

Operationally, that means:

1. an evoked federate does not see a callback until it drains the queue
2. an immediate federate can see the callback before the triggering call
   returns
3. the backend still protects against illegal nested callback invocation

## What We Use As Proof

The strongest executable evidence lives in the Python backend tests:

- [`tests/backends/test_python_backend_federation_extended.py`](../../tests/backends/test_python_backend_federation_extended.py)
  proves that a federate using `HLA_EVOKED` must drain before the callback is
  visible, while a federate using `HLA_IMMEDIATE` sees the callback
  immediately.
- [`tests/backends/test_python_backend_time_ddm_extended.py`](../../tests/backends/test_python_backend_time_ddm_extended.py)
  proves inline immediate delivery for object callbacks and immediate-callback
  behavior during time-management operations.
- [`tests/backends/test_python_backend_object_ownership_extended.py`](../../tests/backends/test_python_backend_object_ownership_extended.py)
  adds immediate-callback coverage for ownership-path failure and callback
  sequencing cases.

For the main 2025 RTI lane, executable evidence now also includes:

- [`tests/test_rti1516_2025_python2025_runtime.py`](../../tests/test_rti1516_2025_python2025_runtime.py)
  proves raw callback-control queueing on the direct `python1516_2025` surface and
  proves inline `HLA_IMMEDIATE` object-callback delivery without explicit
  evocation
- [`tests/transport/test_grpc_transport_2025.py`](../../tests/transport/test_grpc_transport_2025.py)
  proves hosted FedPro callback-control, backlog drain, and reconnect-hygiene
  behavior over the bounded hosted route

The conformance matrix uses those tests as evidence anchors for the service
rows that depend on callback delivery semantics.

## Why This Counts As Compliant

The repo does not claim blanket vendor parity for callback delivery. It claims
compliance for the supported Python backend subsets and for the rows in the
traceability catalog that are backed by executable proof.

That compliance claim is valid because:

- the implementation matches the documented delivery model
- the behavior is exercised by focused tests rather than inferred from docs
- the callback contract is traced into the conformance and requirements
  artifacts
- the failure modes are explicit when a backend does not support inline
  immediate delivery

For the 2025 lane specifically, the honest boundary is:

- direct `hla-backend-python2025` now has positive proof for both
  `HLA_EVOKED` and inline `HLA_IMMEDIATE`
- the hosted FedPro route is still primarily a callback-polling and
  transport-seam proof surface, not the strongest place to claim inline
  immediate-callback semantics

In other words, the repo is compliant where it has positive proof, and it keeps
the unsupported boundary visible instead of collapsing it into a broader claim.

## Where To Look Next

- [`../callback_model_guide.md`](../callback_model_guide.md): operator-friendly overview
- [`../backend_conformance_matrix.md`](../backend_conformance_matrix.md): clause-level evidence mapping
- [`../requirements_hierarchy.md`](requirements_hierarchy.md): how the proof rows fit into the broader hierarchy
- [`../../tests/backends/test_python_backend_federation_extended.py`](../../tests/backends/test_python_backend_federation_extended.py): direct evoked vs immediate behavior proof
