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

For the 2025 lane, that proof is not limited to algorithm-unit coverage. The
current `hla-backend-python2025` runtime also carries an explicit Target/Radar
lookahead proof ladder over both the in-process and hosted FedPro routes.

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

For the primary 2025 lane, the live implementation path is explicitly package
split too:

- [`hla.backends.python2025.time_management_runtime`](../../packages/hla-backend-python2025/src/hla/backends/python2025/time_management_runtime.py)
  carries the Python 2025 time-service, grant, lookahead, GALT/LITS, and
  queued-TSO runtime behavior
- [`hla.backends.python2025.federation_time_surface_mixin`](../../packages/hla-backend-python2025/src/hla/backends/python2025/federation_time_surface_mixin.py)
  exposes the public 2025 ambassador-facing time surface over that runtime
- [`hla.backends.python2025.runtime_state`](../../packages/hla-backend-python2025/src/hla/backends/python2025/runtime_state.py)
  owns the saved/restored logical-time, lookahead, and queued-callback state
  that the 2025 proof ladder depends on

That matters because the current 2025 time claim is not just an abstract route
claim. It is anchored to the extracted `hla-backend-python2025` runtime
modules, not to a shim-owned path and not only to the older 2010 backend code.

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

## 2025 Lookahead Proof Ladder

The 2025 Python RTI evidence now separates several proof levels instead of
pretending one small time test proves the whole lookahead story.

The bounded 2025 certification ladder is:

- `time-window-core`: proves pending timestamped inputs are not skipped and the
  radar window does not close before known `< window_end` inputs arrive
- `time-window-future-exclusion`: proves closure is blocked while another
  regulating federate could still legally send into the closing window
- `time-window-output-delivery`: proves the closed window can produce a legal
  timestamped output
- `time-window-consumer-order`: proves downstream consumers observe that output
  in timestamp order
- `time-window-pipeline-two-scans`: proves one scan can be processed while the
  next scan is collected without cross-window contamination
- `time-window-receive-order-poison`: proves receive-order side traffic does
  not mutate a closed timestamp-managed window
- `time-window-save-restore-window-state`, `time-window-save-restore-output-resume`,
  and `time-window-save-restore-pipeline-resume`: prove dirty post-save window,
  output, and pipeline state are rolled back rather than leaking across restore

The integrated route is named:

- `lookahead-processing-window-certified`

That integrated route is still a bounded working-surface claim, not an
unqualified blanket correctness claim for every possible time-policy topology.

What it proves today is narrower and more honest:

- the live `hla-backend-python2025` lane can close a time window only when
  GALT/LITS and lookahead state make it safe
- the same lane can process after closure, publish legal output, and deliver it
  in order
- the same proof ladder is replayed over the hosted `python-2025-fedpro-grpc`
  route
- matching negative-oracle tests reject premature closure, mismatched LITS
  boundaries, premature output, reversed consumer order, cross-window
  contamination, closed-window mutation, and dirty post-restore replay

The matching requirement-facing note for that ladder is:

- [`../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`](../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md)
  - keeps the closure/output/order/pipeline/save-restore ladder and its
    vendor-credence boundary explicit instead of leaving it only in generated
    milestone prose

## 2025 Evidence Anchors

The main 2025 runtime evidence is:

- [`../../tests/test_rti1516_2025_python2025_runtime.py`](../../tests/test_rti1516_2025_python2025_runtime.py)
  - direct in-process `python2025` time-management services plus the
    Target/Radar time-window proof ladder and negative-oracle guards
- [`../../tests/scenarios/test_python_route_parity.py`](../../tests/scenarios/test_python_route_parity.py)
  - route-level replay of the proof ladder over the in-process and hosted 2025
    Python routes
- [`../../tests/transport/test_grpc_transport_2025.py`](../../tests/transport/test_grpc_transport_2025.py)
  - hosted FedPro 2025 time-management behavior, including lookahead queries,
    grants, queued TSO delivery, and hosted proof-ladder replay
- [`../plans/spec2025_route_parity_matrix.md`](../plans/spec2025_route_parity_matrix.md)
  - the machine-readable and human-readable route-parity claim for the main
    Python 2025 RTI lane
- [`../plans/spec2025_finish_line.md`](../plans/spec2025_finish_line.md)
  - finish-line snapshot and milestone wording for bounded GALT/LITS and
    lookahead-window evidence

## Vendor Boundary

The repo does not currently treat vendor parity as the primary proof for the
2025 lookahead ladder.

The strongest current 2025 evidence is still the in-process and hosted Python
RTI routes. Vendor runs add credence only where the route topology is small
enough to be meaningful and supported by the vendor runtime.

For Pitch specifically, the current trial-safe candidate is the two-federate
`time-window-future-exclusion` route. That is useful vendor credence, but it
does not replace the broader Python proof for output delivery, consumer order,
pipeline overlap, or save/restore replay.

The operator entrypoints for that bounded vendor-credence slice are:

- `./tools/pitch time-window-probe`
- `./tools/pitch time-window-restore-state-probe`

Use those only as narrow real-runtime probes for the two-federate closure and
restore-state routes. They do not turn Pitch into the implementation owner for
the 2025 lane, and they do not widen the bounded claim beyond what the direct
and hosted `hla-backend-python2025` evidence already proves.

## Where To Look Next

- [`../callback_model_compliance.md`](callback_model_compliance.md): callback delivery boundary
- [`../backend_conformance_matrix.md`](../backend_conformance_matrix.md): clause-level service mapping
- [`../requirements_hierarchy.md`](requirements_hierarchy.md): requirement hierarchy and proof anchors
- [`../certi_runtime_limitations.md`](../../packages/hla-backend-certi/docs/certi_runtime_limitations.md): real-runtime GALT/LITS divergence notes
