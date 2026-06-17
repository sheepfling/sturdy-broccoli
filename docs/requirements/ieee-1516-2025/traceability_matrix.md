# Initial Traceability Matrix

This matrix maps the first 2025 extraction tranche to project lanes and Rosetta
evidence scenarios. It is not a conformance claim.

| Requirement | Primary lane | Initial scenario / evidence |
| --- | --- | --- |
| HLA-X-2025-REQ-001 | requirements | Cross-standard registry links Framework, Federate Interface, and OMT requirements. |
| HLA-X-2025-REQ-002 | evidence | Status vocabulary forbids local `HLA Conforming` claims. |
| HLA-X-2025-FR-001 | FOM validation | Target/Radar FOM-backed demo evidence. |
| HLA-X-2025-FR-002 | RTI architecture | RTI state model review; federate-owned semantic object state. |
| HLA-X-2025-FR-003 | Rosetta routes | `two-federate-core-exchange`, route callback traces. |
| HLA-X-2025-FR-004 | Rosetta routes | Java/C++/Python HLA-shaped service and callback evidence. |
| HLA-X-2025-FR-005 | Ownership | Attribute ownership matrix and negative tests. |
| HLA-X-2025-FR-006 | SOM tooling | SOM generation backlog. |
| HLA-X-2025-FR-007 | Object management | Object update reflection and interaction receive evidence. |
| HLA-X-2025-FR-008 | Ownership | Transfer/divestiture/acquisition backlog. |
| HLA-X-2025-FR-009 | Support/declaration | Update rate, advisory, and threshold backlog. |
| HLA-X-2025-FR-010 | Time | Time factory and grant evidence. |
| HLA-X-2025-FI-001 | Matrix | Service group capability matrix. |
| HLA-X-2025-FI-002 | Matrix | Full interface service/callback accounting. |
| HLA-X-2025-FI-003 | Language evidence | Java 2025, C++ 2025, Python mapping split. |
| HLA-X-2025-FI-004 | Rosetta intake | Java standard jars and C++ standard capsules. |
| HLA-X-2025-FI-005 | Negative tests | Structured RTI exceptions for illegal operations. |
| HLA-X-2025-FI-006 | Callback model | `HLA_EVOKED` evidence now; `HLA_IMMEDIATE` backlog. |
| HLA-X-2025-FI-007 | FOM validation | Required FDD tables and case-sensitive names. |
| HLA-X-2025-FI-008 | FOM validation | Create/join reject invalid FOM modules. |
| HLA-X-2025-FI-009 | Time | Default integer/float time factories and timestamp ordering. |
| HLA-X-2025-OMT-001 | FOM validation | `validate_hla_name(...)`. |
| HLA-X-2025-OMT-002 | FOM validation | DIF parser primary; tabular docs secondary. |
| HLA-X-2025-OMT-003 | FOM validation | Required component presence states. |
| HLA-X-2025-OMT-004 | MOM/MIM | MIM source and MOM inclusion status. |
| HLA-X-2025-OMT-005 | FOM validation | Identification table rows. |
| HLA-X-2025-OMT-006 | FOM validation | Structured validation failures. |
| HLA-X-2025-OMT-007 | FOM merge | Conflict detection and whole-module rejection. |

## Rosetta Requirement IDs

Current route evidence should include requirement IDs. Initial lifecycle traces
exercise a narrow subset:

```json
{
  "requirements_exercised": [
    "HLA-X-2025-REQ-002",
    "HLA-X-2025-FR-004",
    "HLA-X-2025-FI-001",
    "HLA-X-2025-FI-005",
    "HLA-X-2025-FI-006"
  ]
}
```

Core exchange traces should add:

```json
{
  "requirements_exercised": [
    "HLA-X-2025-FR-001",
    "HLA-X-2025-FR-003",
    "HLA-X-2025-FR-007",
    "HLA-X-2025-FR-010",
    "HLA-X-2025-FI-009"
  ]
}
```
