# Docs

Project documentation for the IEEE 1516-2010-focused workspace.

This tree uses one simple parallel pattern:

`family -> mechanism -> evidence`

Start here:

- [documentation_hierarchy.md](documentation_hierarchy.md): canonical doc flow and hierarchy
- [../README.md](../README.md): install, bootstrap, smoke, and operator commands

Doc families:

- `reference/`: source acquisition notes and retained archive copies
- `evidence/`: unpacked verification packets and imported analysis artifacts
- `specs/`: clause indexes, matrices, and evidence-ledger artifacts
- `verification/`: requirements, traceability, proof, and comparison artifacts
- `plans/`: roadmap items and implementation sequencing

Backend and runtime docs:

- [backend_route_inventory.md](backend_route_inventory.md): exhaustive runtime families, bridge routes, transport routes, named baselines, and evidence anchors
- [backend_route_inventory_routes.md](backend_route_inventory_routes.md): backend route table
- [backend_route_inventory_baselines.md](backend_route_inventory_baselines.md): CERTI baseline attribution
- [backend_route_inventory_remote.md](backend_route_inventory_remote.md): remote transport routes
- [backend_route_inventory_commands.md](backend_route_inventory_commands.md): backend route commands
- [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): operator-facing runtime and test matrix
- [backend_capability_matrix.md](backend_capability_matrix.md): backend feature coverage
- [backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance and parity status
- [certi_spec_traceability.md](certi_spec_traceability.md): real CERTI sync/ownership coverage
- [certi_runtime_limitations.md](certi_runtime_limitations.md): patched-vs-upstream CERTI baseline policy and runtime shortfalls
- [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md): CERTI negotiated ownership investigation
- [pitch_decision_tree.md](pitch_decision_tree.md): Pitch runtime selection and troubleshooting
- [pitch_docker_quickstart.md](pitch_docker_quickstart.md): shortest Pitch operator path
- [certi_section8_runbook.md](certi_section8_runbook.md): CERTI operator runbook

Verification and provenance:

- [source_documents.md](source_documents.md): retained source references and provenance
- [source_documents_inventory.md](source_documents_inventory.md): source inventory
- [source_documents_policy.md](source_documents_policy.md): source policy and extraction notes
- [reference/README.md](reference/README.md): reference family index
- [reference/source_index.md](reference/source_index.md): reference source index
- [reference/archive_index.md](reference/archive_index.md): reference archive index
- [specs/README.md](specs/README.md): spec-index family and parallel artifact order
- [evidence/README.md](evidence/README.md): unpacked verification packets
- [evidence/packet_index.md](evidence/packet_index.md): unpacked packet index
- [verification/README.md](verification/README.md): verification family index
- [verification/run_sequence.md](verification/run_sequence.md): easy-run lifecycle sequence

Planning:

- [plans/README.md](plans/README.md): plan index
- [development_next_steps.md](development_next_steps.md): current next-step backlog
- [inbox_inventory_2026-06-05.md](inbox_inventory_2026-06-05.md): source-drop promotion out of `INBOX`
