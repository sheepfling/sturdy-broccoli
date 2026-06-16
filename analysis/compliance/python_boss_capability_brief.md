# Python RTI Capability Brief

This brief is written for a program/technical leadership audience. It explains what the Python RTI currently proves against the HLA 2010 specification, what has been demonstrated in executable scenarios, and what remains intentionally outside the current claim.

## Executive Summary

The Python RTI is now the repo's strongest reference backend and meets the current Python compliance end state as a fully classified backend:

- `919` total requirement rows classified
- `818` `verified`
- `78` `not-applicable`
- `23` `vendor-divergent`
- `0` `blocked`
- `0` `not-yet-tested`
- `0` `classification-required`

See:

- `analysis/compliance/python_final_requirements_report.md`
- `analysis/compliance/python_requirement_disposition.json`
- `analysis/compliance/python_requirement_disposition.md`

In practical terms, this means the Python RTI no longer has unknown or untested requirement rows in its committed matrix projection. Every row is either proven, intentionally out of scope, or explicitly marked as a known divergence.

That is not the same as saying "every applicable requirement is perfectly spec-identical." The remaining `23` residuals are intentional `vendor-divergent` classifications, not open test debt.

## Recommended Executive Framing

Use this as the headline:

> We now have a fully classified Python RTI reference backend with no open compliance rows. It proves federation management, synchronization, packaged FOM loading, time management, and hosted networked operation. The remaining vendor-divergent items are explicit, documented policy choices, not unresolved test gaps.

Then keep the distinction clear:

- `verified` means proven against the committed spec projection
- `not-applicable` means intentionally out of scope
- `vendor-divergent` means intentionally different or only partially modeled by policy, not unfinished work

Do not present the residual `23` as bugs unless the discussion is specifically about strict spec parity.

Put the divergent rows in an appendix or a secondary "intentional residuals" slide, not on the main success slide.

## What Was Built

At a high level, the project now has:

- a clean HLA 2010 specification surface in `hla-rti1516e`
- a pure Python RTI backend in `hla-backend-inmemory`
- a shared verification harness in `hla-verification`
- packaged FOM support, including `hla-fom-target-radar`
- hosted transport layers for networked operation over REST and gRPC
- bridge packages that keep the RTI/federate API surface from being tied only to an in-process Python federate

The package split is intentional and visible in:

- `docs/package_dependency_tree.md`
- `packages/hla-backend-inmemory/README.md`
- `packages/hla-transport-rest/README.md`
- `packages/hla-transport-grpc/README.md`
- `packages/hla-bridge-java-jpype/README.md`
- `packages/hla-bridge-java-py4j/README.md`

## Spec Position By Boss Concern

### 1. Initial Federate Capabilities

Status: **Proven, with a small number of intentional lifecycle-semantics divergences**

The Python backend has no open states in Clause 4 federation management:

- IEEE 1516.1-2010 §4: `281` total
- `275` verified
- `4` vendor-divergent
- `2` not-applicable
- `0` open states

The exercised surface includes:

- connect / disconnect
- create federation execution
- destroy federation execution
- join federation execution
- resign federation execution
- callback-model behavior
- lifecycle precondition and negative-path handling

Representative executable evidence:

- `tests/backends/test_python_backend_federation_extended.py`
- `tests/scenarios/test_federation_lifecycle_backend_matrix.py`
- `tests/scenarios/test_federation_management_backend_matrix.py`

Important caveat:

- There are still Clause 4 `vendor-divergent` rows where the backend behavior is proven in slices, but the repo policy does not yet treat the entire standard-shaped lifecycle effect vector as asserted in one place.

### 2. Standing Up Federations and Synchronizing Federates

Status: **Proven**

The repo has direct shared-harness and backend-specific evidence for:

- federation startup
- join sequencing
- synchronization point registration
- synchronization announcement
- synchronization achievement/completion
- late joiners
- failed federates
- multiple synchronization points

Representative evidence:

- `tests/scenarios/test_federation_management_backend_matrix.py`
- `packages/hla-verification/src/hla.verification/scenario_sync.py`
- `tests/scenarios/test_startup_sync_fom_java_translation_v09.py`

There is also hosted-transport evidence showing synchronization still works when the Python RTI is served remotely:

- `tests/transport/test_rest_transport.py::test_rest_transport_can_host_python_rti_synchronization_end_to_end`
- `tests/transport/test_grpc_transport_python_server.py::test_grpc_transport_can_host_python_rti_synchronization_end_to_end`

### 3. Loading FOMs, Including Target Radar and Heavier Models

Status: **Target Radar and generic multi-module FOM loading are proven; RPR 3.0 is not yet a committed proof claim**

What is proven now:

- packaged FOM resolution for `TargetRadarFOMmodule.xml`
- FOM parsing and metadata extraction
- create/join with explicit FOM modules
- strict negative handling for missing, malformed, or inconsistent FOMs
- explicit MIM loading and preservation
- multi-module FOM visibility

Representative evidence:

- `tests/factories/test_fom_omt_parsing.py`
- `tests/backends/test_python_backend_federation_extended.py`
- `tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_module_fom_visibility_matrix`
- `packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py`

Target Radar is not just parsed; it is used in executable scenario proofs:

- `analysis/target_radar_proof/target_radar_proof_summary.json`
- `analysis/target_radar_backend_matrix/target_radar_backend_matrix_summary.json`
- `packages/hla-fom-target-radar/src/hla.foms.target_radar/resources/foms/TargetRadarFOMmodule.xml`

What is **not** yet honestly claimed:

- There is no committed proof packet showing that the Python RTI has been qualified end-to-end against an RPR 3.0 FOM in the same way Target Radar has.
- So the correct statement is: the FOM loading architecture is general, the parser/merge surfaces are real, and packaged/example FOM operation is proven, but RPR 3.0 still needs an explicit qualification tranche.

### 4. Time Correctness, Especially GALT / LITS / Lookahead

Status: **Strongly proven**

Clause 8 time management has no open states in the Python packet:

- IEEE 1516.1-2010 §8: `61` total
- `59` verified
- `2` not-applicable
- `0` open states

What is exercised:

- enable / disable time regulation
- enable / disable time constrained
- logical time query
- query lookahead
- modify lookahead
- timeAdvanceRequest
- timeAdvanceRequestAvailable
- nextMessageRequest
- nextMessageRequestAvailable
- flushQueueRequest
- queryGALT
- queryLITS
- early timestamp rejection
- GALT-bound grant behavior
- queued timestamp ordering behavior

Representative evidence:

- `tests/scenarios/test_time_management_federation.py`
- `tests/time/test_section8_backend_matrix.py`
- `tests/time/test_lookahead_backend_matrix.py`
- `packages/hla-verification/src/hla.verification/section8_matrix.py`
- `analysis/compliance/service_conformance.csv`

Important nuance:

- This is algorithmic/time-semantics correctness evidence, not a real-time performance benchmark.
- The current proof shows the RTI behaves correctly with respect to logical-time ordering, GALT/LITS semantics, and lookahead restrictions.

### 5. Networked Operation, Not Being Stuck on One Machine

Status: **Architecturally and functionally demonstrated through hosted transports**

The Python RTI is not only an in-process local object. The repo contains hosted transport layers and end-to-end tests for serving the RTI over:

- REST
- gRPC

Representative evidence:

- `tests/transport/test_rest_transport.py`
- `tests/transport/test_grpc_transport_python_server.py`
- `packages/hla-transport-rest`
- `packages/hla-transport-grpc`

What has been shown:

- remote exchange scenarios
- remote synchronization scenarios
- remote lifecycle scenarios
- remote save/restore scenarios

What should be said carefully:

- The repo proves hosted/networked operation and separation from a single in-process caller.
- It does **not** yet present a production WAN hardening or large-scale distributed performance study.

### 6. Interoperability, Mixed Federate Shapes, and Not Being Python-Locked

Status: **Architecturally strong; runtime portability path is real**

The project is no longer shaped as "Python federate talks only to Python RTI in one process."

The repo now separates:

- specification/API surface
- backend-common contracts
- runtime-common helpers
- transport surfaces
- generic Java bridge layers
- vendor-specific bridge/backend packages

This is visible in:

- `docs/package_dependency_tree.md`
- `packages/hla-bridge-java-jpype/docs/README.md`
- `packages/hla-bridge-java-py4j/docs/README.md`
- `tests/test_rti_java_bridge_split_packages.py`

What this means:

- the federate/RTI contract is being held at a clean package boundary
- JPype and Py4J bridges exist as generic packages, not only as Pitch-specific hacks
- the shared verification harness is backend-neutral by design

What should be said carefully:

- The Python RTI is the clearest **reference implementation**
- the architecture is now much friendlier to adding or hosting non-Python federates and future C++-oriented work
- but this is not yet the same thing as claiming a finished C++ RTI or complete cross-language transparent interoperability for every backend combination

### 7. Faster-Than-Real-Time Operation

Status: **Semantically supported; not yet benchmarked as a throughput claim**

The strongest statement we can make today is:

- the Python RTI is governed by logical time, not wall-clock pacing
- its Clause 8 time-management behavior is proven in executable scenarios
- the lookahead and time-advance surfaces needed for faster-than-real-time simulation are present and tested

Evidence:

- `tests/time/test_section8_backend_matrix.py`
- `tests/time/test_lookahead_backend_matrix.py`
- `tests/scenarios/test_time_management_federation.py`
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/time_queue_delivery.py`
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/time_queue_grants.py`

What is **not** yet honestly claimed:

- there is no committed performance benchmark packet saying "X simulated seconds per wall-clock second"
- so the correct executive claim is that the time-management algorithmic surface needed for faster-than-real-time operation is in place and substantially verified, but throughput remains a separate measurement problem

### 8. Lookahead Correctness

Status: **Proven enough to support the faster-than-real-time argument**

Lookahead correctness is not just present as an API name. The repo has direct evidence for:

- nonnegative lookahead
- querying lookahead
- modifying lookahead
- blocking timestamped sends that violate logical-time-plus-lookahead rules
- correct ordering/grant behavior after regulation/constrained enablement

Representative evidence:

- `tests/time/test_lookahead_backend_matrix.py`
- `packages/hla-verification/src/hla.verification/section8_matrix.py`
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/state.py`
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/time_queue_delivery.py`
- `packages/hla-backend-inmemory/src/hla/backends/inmemory/time_queue_grants.py`

## What Is Still Not Perfect

The Python RTI is not "zero divergence."

The remaining residuals are:

- `23` `vendor-divergent`
- `78` `not-applicable`
- `0` open states

The most relevant remaining divergences for leadership discussion are the `6` IEEE 1516.1 rows still marked `vendor-divergent`:

- `HLA1516.1-FM-4.2-EFF-001`
- `HLA1516.1-FM-4.5-EFF-001`
- `HLA1516.1-FM-4.9-EFF-001`
- `HLA1516.1-FM-4.10-EFF-001`
- `HLA1516.1-DM-5.1.6-001`
- `HLA1516.1-OM-6.1.11-001`

These are not missing tests. They are explicit policy calls where the repo does not yet claim full spec-shaped behavior or a single all-in-one witness for the whole semantic effect.

## Recommended Boss-Level Framing

The safest accurate summary is:

1. We now have a real Python RTI reference implementation, not just a toy adapter.
2. It is fully classified against the repo's HLA 2010 requirements matrix with no open Python rows left.
3. Federation lifecycle, synchronization, FOM loading, MOM/MIM handling, time management, and hosted network transports are all exercised with executable evidence.
4. The architecture is no longer locked to a single in-process Python federate model; the package split, transports, and Java bridges are deliberate preparation for broader interoperability.
5. Target Radar is proven as a packaged example scenario. RPR 3.0 is not yet a claimed proof surface and should be presented as the next major qualification target.
6. Faster-than-real-time capability is supported by the logical-time and lookahead design, but should not yet be sold as a measured performance benchmark.

## One-Minute Talk Track

"We built a spec-driven HLA 2010 RTI reference stack with Python as the first fully classified backend. The Python RTI now has no open compliance rows left in our committed matrix: every requirement is either verified, intentionally not applicable, or explicitly classified as a known divergence. We can stand up federations, synchronize federates, load packaged FOMs like Target Radar, preserve standard MIM behavior, and exercise HLA time-management semantics including lookahead, GALT, and LITS. We also proved the RTI can be hosted over REST and gRPC, so the architecture is not trapped on one machine or inside one Python process. What we have not claimed yet is full RPR 3.0 qualification or a benchmarked faster-than-real-time throughput number. Those are the next credibility tranches, not hidden gaps in what is already claimed."
