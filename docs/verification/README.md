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

- [../backend_route_inventory.md](../backend_route_inventory.md): runtime and transport route inventory
- [../backend_capability_matrix.md](../backend_capability_matrix.md): feature coverage by backend
- [../backend_conformance_matrix.md](../backend_conformance_matrix.md): clause-level conformance matrix
- [../certi_spec_traceability.md](../certi_spec_traceability.md): CERTI clause traceability
- [../local_verification.md](../local_verification.md): local verification workflow
- [../source_documents.md](../source_documents.md): source provenance and reference map
- [../evidence/README.md](../evidence/README.md): promoted evidence packets
- [../specs/README.md](../specs/README.md): planned spec/evidence artifact family
- [run_sequence.md](run_sequence.md): documented full verification sequence

## What Belongs Here

- requirements ledgers
- service matrices
- spec traceability tables
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
