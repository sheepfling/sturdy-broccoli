# Verification And Validation Split

This repo should treat verification and validation as separate evidence streams.

Verification asks:

- did `hla2010` implement IEEE 1516.1-2010 (2010 edition) correctly?

Validation asks:

- does `hla2010` support realistic federations correctly and usefully?

Those are not the same claim, and mixing them makes both weaker.

## Verification

Verification is the standards-conformance side.

Use verification artifacts to answer:

- which clause or service is implemented
- which positive-path behavior is proven
- which negative-path behavior is proven
- which backend/runtime combinations match the reference path
- which rows remain partial, blocked, or vendor-divergent

Verification evidence in this repo already includes:

- [../backend_conformance_matrix.md](../backend_conformance_matrix.md)
- [../backend_capability_matrix.md](../backend_capability_matrix.md)
- [../certi_spec_traceability.md](../../packages/hla2010-rti-certi/docs/certi_spec_traceability.md)
- `analysis/compliance/*`
- `tests/verification/*`
- `tests/backends/*`
- `tests/time/*`
- `tests/vendors/*`

Verification should own:

- requirement traceability
- unit mechanics
- service-by-service behavior
- standard exceptions
- cross-federate clause behavior
- time management
- DDM routing
- MOM conformance behavior
- save/restore correctness
- cross-RTI interoperability
- transport-invariant behavior

## Validation

Validation is the operational-usefulness side.

Use validation artifacts to answer:

- can a real federation run on this RTI?
- does the federation produce plausible outputs?
- can an operator diagnose failures?
- can a monitoring federate reconstruct what happened?

Validation evidence in this repo should include:

- scenario proof packets
- plotted mission traces
- multi-federate study outputs
- operator rerun wrappers
- monitoring/observer reconstructions

Current validation-oriented assets include:

- `analysis/target_radar_proof/*`
- `analysis/target_radar_backend_matrix/*`
- `analysis/two_federate_suite/*`
- `examples/target_radar_simulation.py`
- `tests/scenarios/*`

Validation should own:

- target/radar study packets
- shooter-style scenario studies
- MOM observer federation studies
- persistence and restore scenario studies
- transport-neutral mission reruns

## Rule

Use this decision rule:

- if the claim is "the standard says this service or exception must behave this way", it is verification
- if the claim is "a realistic federation can use this RTI to do useful work correctly", it is validation

## Four Required Proof Families

For this repo, the highest-confidence package should require four independent proof families:

1. standards traceability matrix
2. automated service verification
3. MOM observer verification
4. cross-RTI interoperability verification

The MOM observer belongs in verification first, not validation, because it is a second conformance witness for the RTI's own state transitions. It also becomes a strong validation asset once it is attached to realistic scenario runs.

## What This Means For The Current Repo

Keep these as verification-first:

- clause matrices
- support/time/ownership/DDM/MOM service tests
- CERTI and Pitch parity comparisons
- transport-invariant backend matrices

Keep these as validation-first:

- target/radar proof packet
- target/radar backend study
- future shooter and multi-sensor scenario packets

Do not use scenario plots by themselves to claim clause conformance.

Do not use a clause matrix by itself to claim realistic federation utility.
