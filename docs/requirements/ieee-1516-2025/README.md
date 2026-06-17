# IEEE 1516-2025 Requirements Backlog

This directory is the first structured extraction tranche for the 2025 HLA
family:

- IEEE 1516-2025, Framework and Rules
- IEEE 1516.1-2025, Federate Interface Specification
- IEEE 1516.2-2025, Object Model Template Specification

The extraction stance is intentionally conservative. `shall` is the primary
normative marker and drives mandatory backlog entries first. `should`, `may`,
and `can` are retained as advisory, permission, or descriptive notes in later
passes.

Source anchors for modal terms:

| Source | Clause | Page |
| --- | ---: | ---: |
| IEEE 1516-2025 | 1.3 | 11 |
| IEEE 1516.1-2025 | 1.3 | 16 |
| IEEE 1516.2-2025 | 1.3 | 12 |

## Files

- `requirements.json`: machine-readable tranche registry.
- `framework_rules.md`: Framework and Rules requirements, including Rules 1-10.
- `federate_interface.md`: Federate Interface service, conformance, callback, FDD, exception, and time requirements.
- `omt.md`: OMT/FOM naming, DIF, component, identification, conformance, and merge requirements.
- `traceability_matrix.md`: initial requirement-to-project-lane and Rosetta scenario mapping.
- `executable_tests/`: imported v3 executable-test backlog with 1117 candidate test rows.
- `encoding_auth_work_packet/`: imported encoding/auth requirements, vectors, schemas, smoke FOM, and contract-test skeletons.

## Conformance Language

Do not use `HLA Conforming`, `fully conformant`, or `standards compliant` for
local shims, demos, object models, tools, or route reports unless certified
conformance evidence exists.

Allowed project evidence vocabulary:

| Status | Meaning |
| --- | --- |
| `surface-backed` | Standard surface exists and is traceable to source API or schema. |
| `lifecycle-green` | Connect/create/join/callback-poll/resign/destroy/disconnect lifecycle passes. |
| `adapter-smoke-green` | Adapter loads and handles a scoped smoke path. |
| `core-exchange-green` | FOM-backed object/interaction/time exchange path passes. |
| `trace-green` | Route trace matches expected standard-backed events and artifacts. |
| `full-interface-surface-complete` | All joined-federate services and RTI-initiated callbacks are present in surface accounting. |
| `full-interface-behavior-complete` | All joined-federate services and RTI-initiated callbacks are behavior-tested. |

## Next Technical Lane

The next high-value implementation lane is FOM/OMT validation. It connects all
three documents:

- Framework Rule 1 requires a FOM.
- The Federate Interface requires RTI handling, merging, and rejection of FOM modules.
- The OMT defines valid object model naming, content, validation, and merge behavior.
