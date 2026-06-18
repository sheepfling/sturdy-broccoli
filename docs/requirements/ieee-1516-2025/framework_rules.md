# Framework and Rules Requirements

Source: IEEE 1516-2025 Framework and Rules.

| ID | Clause | Page | Summary | Shim-route / implementation lane |
| --- | ---: | ---: | --- | --- |
| HLA2025-FR-001 | 5.1 | 31 | A federation shall have an HLA FOM documented according to the OMT. | FOM-backed demos; Target/Radar as primary route proof; warn/fail when non-trivial demos lack FOM evidence. |
| HLA2025-FR-002 | 5.2 | 32 | Simulation-associated object instance representation shall be in federates, not in the RTI. | RTI tracks handles, ownership, subscriptions, queues, and routing state; federates own semantic object state. |
| HLA2025-FR-003 | 5.3 | 32 | All exchange of FOM data among joined federates shall occur via the RTI. | Route traces must prove Python/Java/C++ calls travel through selected RTI backend and callback queue. |
| HLA2025-FR-004 | 5.4 | 32 | Joined federates shall interact with the RTI according to the HLA interface specification. | Shims must accept HLA-shaped service invocations and produce HLA-shaped callbacks. |
| HLA2025-FR-005 | 5.5 | 33 | An instance attribute shall be owned by at most one joined federate at a time. | Stage ownership: publisher-owned MVP, query, unconditional transfer, then negotiated ownership. |
| HLA2025-FR-006 | 6.1 | 33 | Federates shall have a SOM documented according to the OMT. | SOM generation and service usage table backlog. |
| HLA2025-FR-007 | 6.2 | 33 | Federates shall be able to update/reflect attributes and send/receive interactions as documented. | Object/interaction exchange scenario coverage. |
| HLA2025-FR-008 | 6.3 | 34 | Federates shall be able to transfer and accept ownership dynamically. | Ownership transfer scenario backlog. |
| HLA2025-FR-009 | 6.4 | 34 | Federates shall be able to vary update conditions such as thresholds. | Update rate, advisory switch, and threshold behavior backlog. |
| HLA2025-FR-010 | 6.5 | 34 | Federates shall manage local time to coordinate data exchange. | Logical time factories, grants, and timestamp-ordering evidence. |

## Cross-Standard Backlog

| ID | Source | Summary |
| --- | --- | --- |
| HLA2025-REQ-001 | IEEE 1516.1-2025 1.4 p. 17 | Treat HLA 2025 as a coordinated three-document product set and cross-link Framework rules, Federate Interface service behavior, and OMT/FOM data requirements. |
| HLA2025-REQ-002 | IEEE 1516.1-2025 13 p. 413; IEEE 1516.2-2025 6.1 p. 90 | Do not overclaim `HLA Conforming`; use scoped evidence vocabulary until certified conformance evidence exists. |
