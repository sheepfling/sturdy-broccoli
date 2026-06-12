# Documentation Hierarchy

This repository works best when the documentation follows the same pattern as
the code:

`start here -> reference -> historical/provenance`

That keeps the repo usable for a human reader before they know the package and
backend vocabulary.

## Canonical Top-Level Paths

The intended reading order for a new contributor is:

1. repo front door
2. first working example
3. environment and package map
4. deeper backend or verification reference

### Start Here

- [README.md](../README.md): install, bootstrap, smoke, and operator commands
- [docs/first_run.md](first_run.md): shortest path from fresh checkout to a working pure-Python example
- [docs/networked_rti_python.md](networked_rti_python.md): hosted Python RTI and Target/Radar extension path
- [docs/python_environment.md](python_environment.md): Python environment setup and install order
- [docs/two_federate_quickstart.md](two_federate_quickstart.md): first artifact-producing two-federate example
- [docs/install_matrix.md](install_matrix.md): extras, bridge deps, and vendor-runtime install order
- [docs/agent_runbook.md](agent_runbook.md): startup sequence for agents and automation

### Reference

- [docs/README.md](README.md): documentation map and doc-family index
- [docs/package_dependency_tree.md](package_dependency_tree.md): machine-derived installable package dependency tree
- [docs/architecture.md](architecture.md): package and module structure
- [docs/package_layout.md](package_layout.md): source-tree layout and import discipline
- [docs/python_api_spec.md](python_api_spec.md): supported HLA-facing import surface
- [docs/import_boundary_rules.md](import_boundary_rules.md): package-family dependency rules and transport/backend separation
- [docs/backend_route_inventory.md](backend_route_inventory.md): runtime/bridge/transport route inventory
- [docs/backend_route_inventory_routes.md](backend_route_inventory_routes.md): backend route table
- [docs/backend_route_inventory_baselines.md](backend_route_inventory_baselines.md): CERTI baseline attribution
- [docs/backend_route_inventory_remote.md](backend_route_inventory_remote.md): remote transport routes
- [docs/backend_route_inventory_commands.md](backend_route_inventory_commands.md): route test commands
- [docs/backend_compliance_discovery.md](backend_compliance_discovery.md): one-command backend/spec compliance discovery path
- [docs/rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): operator-facing runtime and test matrix
- [docs/backend_capability_matrix.md](backend_capability_matrix.md): backend feature coverage
- [docs/backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance and parity status
- [docs/vendor_runtime_gap_map.md](vendor_runtime_gap_map.md): promoted slices vs environment prerequisites vs true vendor/runtime gaps
- [docs/vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md): supported unsandboxed-local and dedicated-runner path for real vendor runtimes
- [docs/vendor_runner_provisioning.md](vendor_runner_provisioning.md): dedicated runner variables, marker paths, and provisioning checklist
- [docs/vendor_runner_provisioning_template.yaml](vendor_runner_provisioning_template.yaml): machine-readable runner provisioning template

### Historical / Provenance

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
- [docs/verification/requirements_hierarchy.md](verification/requirements_hierarchy.md): L1/L2/L3 requirements hierarchy
- [docs/verification/verification_validation_split.md](verification/verification_validation_split.md): verification vs validation boundary
- [docs/verification/verification_plan.md](verification/verification_plan.md): layered conformance plan
- [docs/verification/validation_plan.md](verification/validation_plan.md): layered scenario-validation plan
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
- verification/validation planning
- executable tests
- generated artifacts

That means a reader can move from claim to evidence without learning a new
document structure for each backend or test family.

### Install / Run / Verify

Keep operator-facing docs in this order:

1. install or bootstrap
2. activate `.venv`
3. run a smoke command
4. run the focused test set
5. generate the evidence packet
6. compare or attribute failures

The root [README.md](../README.md) should stay the shortest path to that flow.

## Read Next

1. [first_run.md](first_run.md)
2. [python_environment.md](python_environment.md)
3. [two_federate_quickstart.md](two_federate_quickstart.md)
4. [README.md](README.md)
