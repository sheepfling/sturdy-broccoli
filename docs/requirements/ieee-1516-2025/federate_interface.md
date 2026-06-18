# Federate Interface Requirements

Source: IEEE 1516.1-2025 Federate Interface Specification.

| ID | Clause | Page | Summary | Implementation lane |
| --- | ---: | ---: | --- | --- |
| HLA2025-FI-001 | 1.4 | 17 | Service groups shall drive the capability and test matrix. | Matrix rows by federation, declaration, object, ownership, time, DDM, and support services. |
| HLA2025-FI-002 | 13.2 | 413 | RTI conformance requires all joined-federate services and all RTI-initiated callbacks. | Split `core_scenario_status` from full interface service and callback completion. |
| HLA2025-FI-003 | 13.2 | 413 | RTI conformance requires at least one language-specific API implementation. | Track Java 2010/2025, C++ 2010/2025, and Python mapping evidence independently. |
| HLA2025-FI-004 | Annex A | 414 | Java and C++ language bindings matter directly; Python may be mapped with documented semantics. | Java jars compile against official API; C++ capsules compile against official headers; Python has mapping evidence. |
| HLA2025-FI-005 | 4.1 | 42 | Illegal operations shall raise RTI exceptions. | Route-neutral negative tests for illegal lifecycle, declaration, object, ownership, and time operations. |
| HLA2025-FI-006 | 4.1 | 38-39 | RTIs shall implement both immediate and evoked callback models. | Report `HLA_EVOKED` and `HLA_IMMEDIATE` evidence separately. |
| HLA2025-FI-007 | 4.1.4 | 47 | The RTI-retained FDD has minimum required tables and case-sensitive names. | FOM parser/validator must preserve and validate required FDD tables. |
| HLA2025-FI-008 | 4.1.4.1 | 47-48 | Create/join shall reject noncompliant FOM modules with exceptions. | Reject bad XML, missing tables, invalid names, and merge conflicts as whole-module failures. |
| HLA2025-FI-009 | 4.1.5 | 48 | Logical time implementation is federation-wide; default integer and floating factories are required. | Evidence rows for integer/float defaults, custom time factory declaration, grants, and timestamp ordering. |

## Core vs Full Interface

The evidence matrix must distinguish lifecycle/core proof from full interface
completion. A route can be `lifecycle-green`, `core-exchange-green`, or
`trace-green` while still having partial service coverage.

Example report shape:

```json
{
  "core_scenario_status": "trace-green",
  "full_interface_surface_status": "partial",
  "joined_federate_initiated_services": {
    "implemented": 42,
    "unsupported": 87
  },
  "rti_initiated_callbacks": {
    "implemented": 15,
    "unsupported": 34
  }
}
```
