# Initial Traceability Matrix

This matrix maps the first 2025 extraction tranche to project lanes and route
evidence scenarios. It is not a conformance claim.

| Requirement | Primary lane | Initial scenario / evidence |
| --- | --- | --- |
| HLA2025-REQ-001 | requirements | Cross-standard registry links Framework, Federate Interface, and OMT requirements. |
| HLA2025-REQ-002 | evidence | Status vocabulary forbids local `HLA Conforming` claims. |
| HLA2025-FR-001 | FOM validation | Target/Radar FOM-backed demo evidence. |
| HLA2025-FR-002 | RTI architecture | RTI state model review; federate-owned semantic object state. |
| HLA2025-FR-003 | python2025 runtime + binding routes | `two-federate-core-exchange`, route callback traces. |
| HLA2025-FR-004 | python2025 runtime + binding routes | Java/C++/Python HLA-shaped service and callback evidence. |
| HLA2025-FR-005 | Ownership | Attribute ownership matrix and negative tests. |
| HLA2025-FR-006 | SOM tooling | SOM generation backlog. |
| HLA2025-FR-007 | Object management | Object update reflection and interaction receive evidence. |
| HLA2025-FR-008 | Ownership | Transfer/divestiture/acquisition backlog. |
| HLA2025-FR-009 | Support/declaration | Update rate, advisory, and threshold backlog. |
| HLA2025-FR-010 | Time | Time factory and grant evidence. |
| HLA2025-FI-001 | Matrix | Service group capability matrix. |
| HLA2025-FI-002 | Matrix | Full interface service/callback accounting. |
| HLA2025-FI-003 | Language evidence | Java 2025, C++ 2025, Python mapping split. |
| HLA2025-FI-004 | binding/intake routes | Java standard jars and C++ standard capsules. |
| HLA2025-FI-005 | Negative tests | Structured RTI exceptions for illegal operations. |
| HLA2025-FI-006 | Callback model | Direct `python2025` evidence now proves both `HLA_EVOKED` and inline `HLA_IMMEDIATE`; hosted and binding rows still describe their callback-model boundaries separately. |
| HLA2025-FI-007 | FOM validation | Required FDD tables and case-sensitive names. |
| HLA2025-FI-008 | FOM validation | Create/join reject invalid FOM modules. |
| HLA2025-FI-009 | Time | Default integer/float time factories and timestamp ordering. |
| HLA2025-OMT-001 | FOM validation | `validate_hla_name(...)`. |
| HLA2025-OMT-002 | FOM validation | DIF parser primary; tabular docs secondary. |
| HLA2025-OMT-003 | FOM validation | Required component presence states. |
| HLA2025-OMT-004 | MOM/MIM | MIM source and MOM inclusion status. |
| HLA2025-OMT-005 | FOM validation | Identification table rows. |
| HLA2025-OMT-006 | FOM validation | Structured validation failures. |
| HLA2025-OMT-007 | FOM merge | Conflict detection and whole-module rejection. |

## Route Requirement IDs

Current route evidence should include requirement IDs. Initial lifecycle traces
exercise a narrow subset:

```json
{
  "requirements_exercised": [
    "HLA2025-REQ-002",
    "HLA2025-FR-004",
    "HLA2025-FI-001",
    "HLA2025-FI-005",
    "HLA2025-FI-006"
  ]
}
```

Core exchange traces should add:

```json
{
  "requirements_exercised": [
    "HLA2025-FR-001",
    "HLA2025-FR-003",
    "HLA2025-FR-007",
    "HLA2025-FR-010",
    "HLA2025-FI-009"
  ]
}
```
