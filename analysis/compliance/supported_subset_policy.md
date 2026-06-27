# Supported-Subset Policy

This packet separates broad specification claims from narrower supported-subset claims for the current Python reference backend.

Interpretation:

- `broad-spec`: the full standard wording. These rows stay `partial` when the backend intentionally implements only a defensible subset.
- `supported-subset`: a narrowed claim that is explicitly implemented and evidenced in the current backend.

## Logical-time update-rate subset

- Policy ID: `logical-time-update-rate-only`
- Supported behavior: Update-rate reduction is implemented as logical-time-based throttling. Explicit and FOM-declared update-rate designators apply across direct, inherited, and regioned subscriptions when there is a logical-time basis.
- Broad-gap rationale: The backend does not invent a wall-clock or unmanaged receive-order throttling policy, so broader vendor-style update-rate semantics remain out of scope.
- Broad-spec status counts: none
- Supported-subset status counts: none

Broad-spec rows:

| Requirement ID | Section | Status | Title | Notes |
|---|---|---|---|---|
| - | - | - | - | - |

Supported-subset rows:

| Requirement ID | Section | Status | Broad row | Title | Notes |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

## Reliable and best-effort transport subset

- Policy ID: `reliable-best-effort-transport-only`
- Supported behavior: Transportation semantics are implemented for the standard HLAreliable and HLAbestEffort pair, including FOM-defined defaults, explicit overrides, callback/query reporting, and restore persistence.
- Broad-gap rationale: The backend does not model arbitrary custom transportation-type behavior beyond the reliable/best-effort subset.
- Broad-spec status counts: none
- Supported-subset status counts: pass=11

Broad-spec rows:

| Requirement ID | Section | Status | Title | Notes |
|---|---|---|---|---|
| - | - | - | - | - |

Supported-subset rows:

| Requirement ID | Section | Status | Broad row | Title | Notes |
|---|---|---|---|---|---|
| HLA1516.1-OM-6.1.10-001 | IEEE 1516.1-2010 (2010 edition) §6.1.10 | pass | - | RTI shall use FOM-declared and explicitly selected reliable and best-effort transportation types for object updates and interactions, including query/report visibility and restore persistence within the implemented transport subset. | This canonical narrowed row captures the transport behavior the repo proves today: FOM-declared defaults, explicit reliable and best-effort override changes, distinct best-effort delivery semantics, query/report callback visibility, and restore persistence within the implemented transport subset. |
| HLA1516.1-OM-6.10-005 | IEEE 1516.1-2010 (2010 edition) §6.10 | pass | - | RTI shall deliver reflected attribute updates with transportation metadata that matches the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.12-005 | IEEE 1516.1-2010 (2010 edition) §6.12 | pass | - | RTI shall deliver received interactions with transportation metadata that matches the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.23-001 | IEEE 1516.1-2010 (2010 edition) §6.23 | pass | - | RTI shall support Request Attribute Transportation Type Change for the implemented reliable and best-effort transport subset, including invalid-request rejection and restore persistence of selected overrides. | This canonical narrowed row captures the repo-owned Clause 6.23 behavior: attribute transportation overrides can be changed within the reliable/best-effort subset, invalid requests are rejected, and selected override state survives restore. |
| HLA1516.1-OM-6.24-001 | IEEE 1516.1-2010 (2010 edition) §6.24 | pass | - | RTI shall invoke Confirm Attribute Transportation Type Change only for accepted requester-owned attribute transport changes in the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected requests. | This canonical narrowed row captures the repo-owned Clause 6.24 callback behavior: attribute transport-change confirmations are requester-routed for accepted changes and are not emitted when the underlying request is rejected. |
| HLA1516.1-OM-6.25-001 | IEEE 1516.1-2010 (2010 edition) §6.25 | pass | - | RTI shall provide Query Attribute Transportation Type for the implemented reliable and best-effort transport subset, including stored overrides and default reliable transport reporting. | This canonical narrowed row captures the repo-owned Clause 6.25 query behavior: valid queries expose stored attribute transport overrides or the default reliable state, and invalid queries are rejected. |
| HLA1516.1-OM-6.26-001 | IEEE 1516.1-2010 (2010 edition) §6.26 | pass | - | RTI shall invoke Report Attribute Transportation Type only to the querying federate for the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected queries. | This canonical narrowed row captures the repo-owned Clause 6.26 callback behavior: attribute transportation reports are requester-routed for valid queries and are not emitted when the query is rejected. |
| HLA1516.1-OM-6.27-001 | IEEE 1516.1-2010 (2010 edition) §6.27 | pass | - | RTI shall support Request Interaction Transportation Type Change for the implemented reliable and best-effort transport subset, including invalid-request rejection and restore persistence of selected overrides. | This canonical narrowed row captures the repo-owned Clause 6.27 behavior: interaction transportation overrides can be changed within the reliable/best-effort subset, invalid requests are rejected, and selected override state survives restore. |
| HLA1516.1-OM-6.28-001 | IEEE 1516.1-2010 (2010 edition) §6.28 | pass | - | RTI shall invoke Confirm Interaction Transportation Type Change only for accepted requester-published interaction transport changes in the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected requests. | This canonical narrowed row captures the repo-owned Clause 6.28 callback behavior: interaction transport-change confirmations are requester-routed for accepted changes and are not emitted when the underlying request is rejected. |
| HLA1516.1-OM-6.29-001 | IEEE 1516.1-2010 (2010 edition) §6.29 | pass | - | RTI shall provide Query Interaction Transportation Type for the implemented reliable and best-effort transport subset, including stored overrides and default reliable transport reporting. | This canonical narrowed row captures the repo-owned Clause 6.29 query behavior: valid queries expose stored interaction transport overrides or the default reliable state, and invalid queries are rejected. |
| HLA1516.1-OM-6.30-001 | IEEE 1516.1-2010 (2010 edition) §6.30 | pass | - | RTI shall invoke Report Interaction Transportation Type only to the querying federate for the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected queries. | This canonical narrowed row captures the repo-owned Clause 6.30 callback behavior: interaction transportation reports are requester-routed for valid queries and are not emitted when the query is rejected. |

## Unbatched callback delivery subset

- Policy ID: `unbatched-callback-delivery-only`
- Supported behavior: The backend preserves externally visible delivery semantics with direct unbatched callbacks.
- Broad-gap rationale: Message combination, packaging, and passelization are not explicitly modeled, so the permissive broad row stays partial by policy.
- Broad-spec status counts: none
- Supported-subset status counts: none

Broad-spec rows:

| Requirement ID | Section | Status | Title | Notes |
|---|---|---|---|---|
| - | - | - | - | - |

Supported-subset rows:

| Requirement ID | Section | Status | Broad row | Title | Notes |
|---|---|---|---|---|---|
| - | - | - | - | - | - |

