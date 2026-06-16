# Time Model Compliance

This page explains how the repo models GALT, LITS, and lookahead, and which
tests prove that the Python backend applies those rules consistently.

## Scope

The time model here covers the core IEEE 1516.1 time-management contract:

- time regulation and time constrained enable/disable
- lookahead as the lower-bound offset for timestamp-order sends
- GALT as the federate's global allowable logical time
- LITS as the least incoming timestamp observed for the federate
- request/grant behavior for TAR, TARA, NMR, NMRA, and FQR

The compliance claim in this repo is bounded to the supported Python backend
subset and the runtime paths that are backed by executable proof.

## How It Works

The implementation is split across the time-management modules:

- [`hla.backends.common/time_management.py`](../../packages/hla-backend-common/src/hla/backends/common/time_management.py) defines the
  core rules:
  - `compute_galt(...)` computes GALT as the minimum lower-bound contribution
    from the other regulating federates
  - `compute_lits(...)` computes LITS as the minimum of GALT and queued TSO
    message timestamps
  - `valid_tso_lower_bound(...)` computes the minimum timestamp allowed for a
    federate's timestamp-order sends
  - `galt_allows_requested_time(...)` and `compute_grant_decision(...)`
    normalize the time-advance request rules
- [`hla.backends.inmemory/time.py`](../../packages/hla-backend-inmemory/src/hla/backends/inmemory/time.py)
  and [`hla.backends.inmemory/time_queue.py`](../../packages/hla-backend-inmemory/src/hla/backends/inmemory/time_queue.py)
  apply those rules to the in-memory Python backend state.
- [`hla.backends.inmemory/time_services.py`](../../packages/hla-backend-inmemory/src/hla/backends/inmemory/time_services.py)
  enforces the public service preconditions, including regulation/constrained
  state, lookahead validity, and outstanding request checks.

The behavior is intended to be straightforward:

1. enabling time regulation records the lookahead and exposes the time-regulation-enabled callback
2. enabling time constrained unlocks constrained delivery and exposes the time-constrained-enabled callback
3. `query_galt()` reports the current safe lower bound across the federation
4. `query_lits()` reports the least incoming time observable to the federate
5. timestamp-order sends must respect the current lookahead bound
6. available-grant services can grant at the inclusive boundary when the request mode allows it

## Lookahead Rule

Lookahead is the offset used to compute the minimum legal timestamp-order send
time.

The Python backend applies that rule by combining:

- the current logical time, or
- the requested advance time when a federate has a pending time advance

with the federate's current lookahead interval.

That means the send-side bound moves with the federate's time state, and it is
not just a fixed constant stored once at enable-time.

The practical enforcement point is:

- `valid_tso_lower_bound(...)` in [`hla.backends.common/time_management.py`](../../packages/hla-backend-common/src/hla/backends/common/time_management.py)
- `_validate_tso_send_time(...)` in [`hla.backends.inmemory/time_services.py`](../../packages/hla-backend-inmemory/src/hla/backends/inmemory/time_services.py)

The negative-path tests prove that a timestamp-order send below that bound is
rejected.

## GALT And LITS Rule

GALT is computed from the federation's other regulating federates. If no other
regulating federate contributes a bound, the result is invalid.

LITS is computed as:

- the minimum valid GALT, if present, and
- the queued incoming timestamp-order messages for the federate

If neither contributes a value, LITS is invalid.

This makes the model consistent with the core safety rule:

- the federate cannot advance or deliver beyond what the current federation
  bounds allow
- queued timestamp-order messages still constrain LITS even when GALT is valid

## Grant Rules

The request/grant logic distinguishes strict and inclusive modes:

- strict modes use a strict GALT boundary for the request side
- available modes can grant at the inclusive boundary when the mode allows it
- `nextMessageRequest` and `nextMessageRequestAvailable` can grant the earliest
  eligible queued timestamp-order message
- `flushQueueRequest` can drain queued timestamps and then grant according to
  the resulting boundary rules

That logic lives in
[`hla.backends.common/time_management.py`](../../packages/hla-backend-common/src/hla/backends/common/time_management.py)
and is exercised by the Python backend time queue/service mixins.

## What We Use As Proof

The main executable evidence is:

- [`../../tests/time/test_time_management_algorithms.py`](../../tests/time/test_time_management_algorithms.py)
  - direct unit tests for `compute_galt(...)`, `compute_lits(...)`,
    `valid_tso_lower_bound(...)`, and the strict/inclusive grant boundary rules
- [`tests/time/test_mom_mim_time_v10.py`](../../tests/time/test_mom_mim_time_v10.py)
  - proves `query_galt()` and `query_lits()` on the timestamp-ordered
    next-message path
  - proves the equal-GALT boundary difference between `timeAdvanceRequest`
    and `timeAdvanceRequestAvailable`
  - proves retract removes queued timestamp-order messages before grant
- [`tests/time/test_mom_mim_and_time_semantics_v010.py`](../../tests/time/test_mom_mim_and_time_semantics_v010.py)
  - proves timestamp-order sends require regulation and respect the lookahead
    lower bound
  - proves lookahead queries require time regulation
  - proves negative lookahead is rejected
  - proves zero-lookahead TAR/NMR restrictions are enforced
- [`tests/backends/test_python_backend_time_ddm_extended.py`](../../tests/backends/test_python_backend_time_ddm_extended.py)
  - proves time-advance services reject invalid state and save/restore blockers
  - proves immediate callback behavior remains correct while time services are active

The CERTI real-runtime notes also record the current promoted baseline behavior
for `queryGALT`, `queryLITS`, and the available-grant services:

- [`../certi_spec_traceability.md`](../../packages/hla-backend-certi/docs/certi_spec_traceability.md)
- [`../certi_runtime_limitations.md`](../../packages/hla-backend-certi/docs/certi_runtime_limitations.md)

## Why This Counts As Compliant

The repo's claim is not that every vendor runtime behaves identically. The claim
is that the supported Python backend and the traced real-runtime slices follow a
coherent, test-backed time model.

That is compliant enough for the supported subset because:

- the implementation encodes the GALT/LITS/lookahead rules directly
- the tests prove both the positive path and the boundary failures
- the docs and traceability matrix point to the same code and evidence
- the unsupported or vendor-divergent cases are kept explicit instead of being
  hidden behind a broader parity claim

## Where To Look Next

- [`../callback_model_compliance.md`](callback_model_compliance.md): callback delivery boundary
- [`../backend_conformance_matrix.md`](../backend_conformance_matrix.md): clause-level service mapping
- [`../requirements_hierarchy.md`](requirements_hierarchy.md): requirement hierarchy and proof anchors
- [`../certi_runtime_limitations.md`](../../packages/hla-backend-certi/docs/certi_runtime_limitations.md): real-runtime GALT/LITS divergence notes
