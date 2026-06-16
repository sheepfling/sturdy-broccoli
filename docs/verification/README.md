# Verification

This family is the executable-and-artifact side of the docs tree.

Use it for anything that answers:

- what is implemented
- what is proven
- what is still partial
- what artifact records the proof

## Canonical Order

Keep verification docs in this order:

1. requirements and clause matrices
2. traceability notes
3. executable test suites
4. generated evidence packets
5. comparison and attribution reports

## Primary Entry Points

- [../../requirements/README.md](../../requirements/README.md): seeded requirement sources and ID registry
- [requirements_structure_packet.md](requirements_structure_packet.md): current packet explaining the requirements layout, bridge strategy, and pinned harmonization state
- [requirements_hierarchy.md](requirements_hierarchy.md): L1/L2/L3 capability-feature-requirement hierarchy with test anchors
- [callback_model_compliance.md](callback_model_compliance.md): callback delivery behavior, compliance boundary, and test evidence
- [time_model_compliance.md](time_model_compliance.md): GALT, LITS, lookahead, and time-advance compliance proof
- [imported_packet_requirements_v1_0/README.md](imported_packet_requirements_v1_0/README.md): generated packet-style markdown views from the imported canonical v1.0 requirements catalog
- [clause13_conformance_packet.md](clause13_conformance_packet.md): generated federate/RTI Clause 13 conformance packet
- [verification_validation_split.md](verification_validation_split.md): canonical split between standards verification and operational validation
- [verification_plan.md](verification_plan.md): layered conformance plan
- [validation_plan.md](validation_plan.md): layered operational validation plan
- [../backend_route_inventory.md](../backend_route_inventory.md): runtime and transport route inventory
- [../backend_capability_matrix.md](../backend_capability_matrix.md): feature coverage by backend
- [../backend_conformance_matrix.md](../backend_conformance_matrix.md): clause-level conformance matrix
- [../certi_spec_traceability.md](../../packages/hla-backend-certi/docs/certi_spec_traceability.md): CERTI clause traceability
- [../local_verification.md](../local_verification.md): local verification workflow
- [../source_documents.md](../source_documents.md): source provenance and reference map
- [../evidence/README.md](../evidence/README.md): promoted evidence packets
- [../specs/README.md](../specs/README.md): planned spec/evidence artifact family
- [run_sequence.md](run_sequence.md): documented full verification sequence

## What Belongs Here

- requirements ledgers
- requirement source registries
- service matrices
- spec traceability tables
- verification planning
- validation planning
- compliance packets
- generated analysis artifacts
- scenario comparison reports

## What Does Not Belong Here

- operator install instructions
- package layout rules
- backend implementation details
- ad hoc notes that do not feed verification output

That separation keeps the docs tree easy to scan for juniors:

- `README.md` tells you how to run the repo
- `docs/README.md` tells you where the docs live
- `docs/verification/README.md` tells you where the proof lives
