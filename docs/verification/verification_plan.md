# Verification Plan

This plan defines the standards-conformance work for the Python HLA 1516.1-2010 RTI.

It is intentionally separate from [validation_plan.md](validation_plan.md).

## Goal

Produce defensible evidence that `hla2010` implements the IEEE 1516.1-2010 federate interface correctly enough to support explicit clause-level claims.

## Master Traceability Model

Use one canonical chain for every requirement:

`spec clause -> requirement id -> implementation -> positive test -> negative test -> artifact`

Minimum fields for every row:

- `requirement_id`
- `spec_section`
- `service_or_behavior`
- `implementation_refs`
- `positive_tests`
- `negative_tests`
- `artifact_refs`
- `status`
- `notes`

The repo already has part of this machinery in:

- `hla2010.conformance`
- `hla2010.verification`
- `analysis/compliance/*`

The requirement IDs should be explicit and stable, rather than only relying on service/method names.

Current generated ledger format:

- `REQ-RTI-FM-4_5-createFederationExecution`
- `REQ-RTI-TM-8_2-enableTimeRegulation`
- `REQ-FED-TM-8_13-timeAdvanceGrant`

Pattern:

- `REQ`
- interface token: `RTI` or `FED`
- service area token: `FM`, `DM`, `OM`, `OWN`, `TM`, `DDM`, `SS`, `PLM`
- normalized clause token
- method name

This keeps IDs stable across row reordering while still making the traced clause obvious.

## Levels

### Level 0: Specification Traceability

Build and maintain the master conformance matrix.

Each requirement row should link:

- standard clause
- implementation surface
- positive test
- negative test
- emitted artifact

Primary repo anchors:

- [../backend_conformance_matrix.md](../backend_conformance_matrix.md)
- `analysis/compliance/service_conformance.json`
- `analysis/compliance/requirements_ledger.json`

### Level 1: Unit Verification

Verify internal mechanics that do not require a federation study.

Core targets:

- handle allocation and stability
- handle serialization round-trips
- FOM parsing and lookup
- MOM catalog generation
- local state transitions

Primary test families:

- `tests/mom/*`
- focused support/backend unit slices

### Level 2: Service Verification

Every RTI service should have:

- happy-path proof
- standard exception proof

The standard's exception contract is part of the implementation, not a secondary detail.

Primary test families:

- `tests/verification/*`
- `tests/backends/*`

### Level 3: Cross-Federate Verification

Use multiple federates to prove:

- discovery
- reflection
- interaction delivery
- object naming
- ownership transfer

Primary test families:

- `tests/backends/*`
- `tests/scenarios/*` where the goal is service behavior, not scenario realism

### Level 4: Time Management Verification

Use at least three-federate cases where necessary.

Verify:

- regulation and constrained enablement
- TAR/TARA/NMR/NMRA/FQR behavior
- GALT/LITS/query semantics
- lookahead modification and guard conditions
- TSO ordering
- RO ordering
- late or invalid timestamp handling

Primary test families:

- `tests/time/*`
- `analysis/compliance/section8_backend_matrix.*`

### Level 5: DDM Verification

Verify:

- overlap
- non-overlap
- partial overlap
- ordering interaction with TSO

Primary test families:

- `tests/backends/*ddm*`
- `tests/verification/test_compliance_slice_v011.py`

### Level 6: MOM Verification

MOM needs its own explicit verification track.

Verify:

- object creation/removal
- publication/subscription reporting
- service reports
- ownership reports
- time and federation state reports

Primary test families:

- `tests/mom/*`
- `tests/verification/test_mom_*`

### Level 7: Persistence Verification

Verify:

- save coordination
- restore coordination
- restored logical time
- restored object state
- restored ownership state

Primary test families:

- `tests/verification/test_compliance_slice_v011.py`
- save/restore backend suites

### Level 8: Interoperability Verification

Run equivalent federations against:

- Python reference RTI
- CERTI
- Pitch
- Java shim profiles

Compare:

- behavior
- exceptions
- ordering
- ownership outcomes
- MOM outcomes where available

Primary test families:

- `tests/vendors/*`
- `analysis/compliance/core_backend_matrix.*`
- `analysis/compliance/pitch_backend_matrix.*`

### Level 9: Transport Verification

Run the same verification slices across:

- in-memory Python
- REST-hosted Python
- gRPC-hosted Python
- vendor/bridge paths

Primary test families:

- `tests/time/test_section8_backend_matrix.py`
- transport suites

## Highest-Value Missing Verification Assets

1. broader negative-path coverage for service semantics, not just parameter decoding
2. a reusable standalone MOM observer federate package, beyond the current focused observer proof slice
3. stricter clause-level interoperability comparisons for CERTI and Pitch
4. deeper persistence verification beyond current restore-time slices
5. transport-hosted parity for the newer verification traceability packet

## Acceptance Rule

A verification row is only "complete" when:

- the clause or service is traced
- the implementation location is known
- a positive executable test exists
- a negative executable test exists when the standard defines failure behavior
- an artifact records the result

Anything less should stay marked `partial`, `planned`, `blocked`, or `vendor-divergent`.
