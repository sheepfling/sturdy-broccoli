# Documentation Hierarchy

This repository works best when the documentation follows the same pattern as
the code:

`family -> subfamily -> mechanism -> evidence`

That keeps the story simple for each backend, transport, and verification path.
It also makes it easier to answer the same question at different levels:

- what runtime family is this?
- how does Python talk to it?
- what transport or bridge is underneath?
- what test or artifact proves it?

## Canonical Top-Level Paths

Use these as the normal entry points:

- [README.md](../README.md): install, bootstrap, smoke, and operator commands
- [docs/README.md](README.md): documentation map and doc-family index
- [docs/architecture.md](architecture.md): package and module structure
- [docs/package_layout.md](package_layout.md): source-tree layout and import discipline
- [docs/backend_route_inventory.md](backend_route_inventory.md): runtime/bridge/transport route inventory
- [docs/backend_route_inventory_routes.md](backend_route_inventory_routes.md): backend route table
- [docs/backend_route_inventory_baselines.md](backend_route_inventory_baselines.md): CERTI baseline attribution
- [docs/backend_route_inventory_remote.md](backend_route_inventory_remote.md): remote transport routes
- [docs/backend_route_inventory_commands.md](backend_route_inventory_commands.md): route test commands
- [docs/rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): operator-facing runtime and test matrix
- [docs/backend_capability_matrix.md](backend_capability_matrix.md): backend feature coverage
- [docs/backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance and parity status
- [docs/source_documents.md](source_documents.md): retained source references and provenance
- [docs/source_documents_inventory.md](source_documents_inventory.md): source inventory
- [docs/source_documents_policy.md](source_documents_policy.md): source policy and extraction notes
- [docs/reference/README.md](reference/README.md): reference family index
- [docs/reference/source_index.md](reference/source_index.md): reference source index
- [docs/reference/archive_index.md](reference/archive_index.md): reference archive index
- [docs/specs/README.md](specs/README.md): spec-family index and artifact order
- [docs/evidence/README.md](evidence/README.md): unpacked evidence packets
- [docs/evidence/packet_index.md](evidence/packet_index.md): evidence packet index
- [docs/verification/README.md](verification/README.md): verification-family index
- [docs/verification/run_sequence.md](verification/run_sequence.md): full verification sequence with lint and type annotations
- [docs/plans/README.md](plans/README.md): implementation plans and sequencing

## Parallel Documentation Pattern

Every backend family should be documented in the same order:

1. Identify the runtime family.
2. Identify the interaction model, if there is one.
3. Identify the transport or adapter layer.
4. Identify the tests that prove the route.
5. Identify the evidence artifacts that record the result.

The existing docs already follow this pattern; this page makes it explicit so
new pages can stay aligned.

### Backend Families

For each family, keep the same story in each layer:

- runtime family: what it is
- route inventory: how it is reached
- capability matrix: what it supports
- conformance matrix: which clauses are proven
- tests: what exercises it
- evidence: what records the result

Current families in the repo:

- Python RTI
- CERTI
- CERTI Java profile
- JPype
- Py4J
- Pitch
- Portico

### Verification Families

Verification docs should use the same shape:

- requirements ledger
- service/clause matrices
- spec traceability
- executable tests
- generated artifacts

That means a reader can move from claim to evidence without learning a new
document structure for each backend or test family.

### Install / Run / Verify

Keep operator-facing docs in this order:

1. install or bootstrap
2. run a smoke command
3. run the focused test set
4. generate the evidence packet
5. compare or attribute failures

The root [README.md](../README.md) should stay the shortest path to that flow.
