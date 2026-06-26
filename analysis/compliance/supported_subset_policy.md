# Supported-Subset Policy

This packet separates broad specification claims from narrower supported-subset claims for the current Python reference backend.

Interpretation:

- `broad-spec`: the full standard wording. These rows stay `partial` when the backend intentionally implements only a defensible subset.
- `supported-subset`: a narrowed claim that is explicitly implemented and evidenced in the current backend.

## Logical-time update-rate subset

- Policy ID: `logical-time-update-rate-only`
- Supported behavior: Update-rate reduction is implemented as logical-time-based throttling. Explicit and FOM-declared update-rate designators apply across direct, inherited, and regioned subscriptions when there is a logical-time basis.
- Broad-gap rationale: The backend does not invent a wall-clock or unmanaged receive-order throttling policy, so broader vendor-style update-rate semantics remain out of scope.
- Broad-spec status counts: partial=2
- Supported-subset status counts: pass=2

Broad-spec rows:

| Requirement ID | Section | Status | Title | Notes |
|---|---|---|---|---|
| HLA1516.1-DM-5.1.6-001 | IEEE 1516.1-2010 (2010 edition) §5.1.6 | partial | RTI shall support subscribing with update rate reduction where applicable. | The backend now proves explicit and FOM-declared update-rate defaults across direct, inherited, and regioned subscriptions, plus receive-order non-suppression when no logical-time basis exists. Broader vendor-style update-rate policies remain outside the current model. |
| HLA1516.1-OM-6.1.12-001 | IEEE 1516.1-2010 (2010 edition) §6.1.12 | partial | RTI shall honor update-rate reduction when reflecting attribute updates. | The backend proves explicit and FOM-declared update-rate throttling for direct, inherited, and regioned subscriptions, plus receive-order non-suppression when no logical-time basis exists. Broader vendor-style update-rate policies remain outside the current model, so this row remains partial. |

Supported-subset rows:

| Requirement ID | Section | Status | Broad row | Title | Notes |
|---|---|---|---|---|---|
| HLA1516.1-DM-5.1.6-002 | IEEE 1516.1-2010 (2010 edition) §5.1.6 | pass | HLA1516.1-DM-5.1.6-001 | RTI shall apply explicit and FOM-declared update-rate designators across direct, inherited, and region-based object-class subscriptions within the currently implemented logical-time subset. | This supported-subset row captures the repo-owned subscription-side update-rate behavior: explicit and FOM-declared designators propagate across direct, inherited, and regioned subscriptions within the logical-time model. |
| HLA1516.1-OM-6.1.12-002 | IEEE 1516.1-2010 (2010 edition) §6.1.12 | pass | HLA1516.1-OM-6.1.12-001 | RTI shall throttle timed reflected attribute delivery according to explicit and FOM-declared update-rate designators while preserving receive-order delivery that has no logical-time basis. | This supported-subset row captures the repo-owned reflection-side update-rate behavior: timed reflects are throttled by explicit and FOM-declared designators, but receive-order delivery is not artificially suppressed outside the logical-time model. |

## Reliable and best-effort transport subset

- Policy ID: `reliable-best-effort-transport-only`
- Supported behavior: Transportation semantics are implemented for the standard HLAreliable and HLAbestEffort pair, including FOM-defined defaults, explicit overrides, callback/query reporting, and restore persistence.
- Broad-gap rationale: The backend does not model arbitrary custom transportation-type behavior beyond the reliable/best-effort subset.
- Broad-spec status counts: partial=9
- Supported-subset status counts: pass=25

Broad-spec rows:

| Requirement ID | Section | Status | Title | Notes |
|---|---|---|---|---|
| HLA1516.1-OM-6.1.10-001 | IEEE 1516.1-2010 (2010 edition) §6.1.10 | partial | RTI shall use transportation types for object updates and interactions as defined by the FDD and service arguments. | This broad standards row remains partial. The backend now proves FOM-defined reliable and best-effort defaults, explicit service-selected overrides, distinct best-effort callback transport behavior, and restore persistence for the supported subset, but it still does not model the full custom transportation semantic space described by the standard. |
| HLA1516.1-OM-6.23-001 | IEEE 1516.1-2010 (2010 edition) §6.23 | partial | RTI shall provide Request Attribute Transportation Type Change across the full transportation semantic space defined by the standard. | The backend exposes this service but the broad standards row remains partial because only the supported reliable plus best-effort subset is modeled directly. |
| HLA1516.1-OM-6.24-001 | IEEE 1516.1-2010 (2010 edition) §6.24 | partial | RTI shall invoke Confirm Attribute Transportation Type Change across the full transportation semantic space. | The backend proves confirm callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space. |
| HLA1516.1-OM-6.25-001 | IEEE 1516.1-2010 (2010 edition) §6.25 | partial | RTI shall provide Query Attribute Transportation Type across the full transportation semantic space defined by the standard. | The backend proves query/report behavior for the supported reliable plus best-effort subset, not the full broader transport semantic space. |
| HLA1516.1-OM-6.26-001 | IEEE 1516.1-2010 (2010 edition) §6.26 | partial | RTI shall invoke Report Attribute Transportation Type across the full transportation semantic space. | The backend proves report callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space. |
| HLA1516.1-OM-6.27-001 | IEEE 1516.1-2010 (2010 edition) §6.27 | partial | RTI shall provide Request Interaction Transportation Type Change across the full transportation semantic space defined by the standard. | The backend exposes this service but the broad standards row remains partial because only the supported reliable plus best-effort subset is modeled directly. |
| HLA1516.1-OM-6.28-001 | IEEE 1516.1-2010 (2010 edition) §6.28 | partial | RTI shall invoke Confirm Interaction Transportation Type Change across the full transportation semantic space. | The backend proves confirm callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space. |
| HLA1516.1-OM-6.29-001 | IEEE 1516.1-2010 (2010 edition) §6.29 | partial | RTI shall provide Query Interaction Transportation Type across the full transportation semantic space defined by the standard. | The backend proves query/report behavior for the supported reliable plus best-effort subset, not the full broader transport semantic space. |
| HLA1516.1-OM-6.30-001 | IEEE 1516.1-2010 (2010 edition) §6.30 | partial | RTI shall invoke Report Interaction Transportation Type across the full transportation semantic space. | The backend proves report callbacks for the supported reliable plus best-effort subset, not the full broader transport semantic space. |

Supported-subset rows:

| Requirement ID | Section | Status | Broad row | Title | Notes |
|---|---|---|---|---|---|
| HLA1516.1-OM-6.1.10-002 | IEEE 1516.1-2010 (2010 edition) §6.1.10 | pass | HLA1516.1-OM-6.1.10-001 | RTI shall support explicit reliable transportation type selection, query reporting, and restore persistence for object updates and interactions in the currently supported transport subset. | This narrow supported-subset row covers explicit reliable transport selection, report/query callbacks, and restore persistence for object and interaction transport state. |
| HLA1516.1-OM-6.1.10-003 | IEEE 1516.1-2010 (2010 edition) §6.1.10 | pass | HLA1516.1-OM-6.1.10-001 | RTI shall support distinct best-effort versus reliable delivery semantics for object updates and interactions when explicit transportation selections differ. | This supported-subset row is now implemented: explicit reliable versus best-effort transport overrides produce distinct callback transport handles for object updates and interactions, and that non-reliable override state survives restore. |
| HLA1516.1-OM-6.1.10-004 | IEEE 1516.1-2010 (2010 edition) §6.1.10 | pass | HLA1516.1-OM-6.1.10-001 | RTI shall honor FOM-declared reliable and best-effort transportation defaults for object updates and interactions in the currently supported transport subset. | This supported-subset row captures FOM-declared transport defaults for the standard reliable and best-effort pair: reflected attributes, received interactions, and transportation-type query callbacks all report the declared transport without requiring an explicit per-service override. |
| HLA1516.1-OM-6.10-005 | IEEE 1516.1-2010 (2010 edition) §6.10 | pass | - | RTI shall deliver reflected attribute updates with transportation metadata that matches the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.12-005 | IEEE 1516.1-2010 (2010 edition) §6.12 | pass | - | RTI shall deliver received interactions with transportation metadata that matches the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.23-002 | IEEE 1516.1-2010 (2010 edition) §6.23 | pass | HLA1516.1-OM-6.23-001 | RTI shall support Request Attribute Transportation Type Change for the currently implemented reliable and best-effort transport subset. | This supported-subset row covers the live request/change behavior for attribute transportation state in the reliable and best-effort subset, including confirm/query-visible outcomes and invalid-request rejection boundaries. |
| HLA1516.1-OM-6.23-003 | IEEE 1516.1-2010 (2010 edition) §6.23 | pass | HLA1516.1-OM-6.23-001 | RTI shall persist selected attribute transportation overrides across restore in the currently implemented reliable and best-effort transport subset. | This supported-subset row isolates restore persistence for attribute transportation overrides after a request/change has already established non-default transport state. |
| HLA1516.1-OM-6.24-002 | IEEE 1516.1-2010 (2010 edition) §6.24 | pass | HLA1516.1-OM-6.24-001 | RTI shall invoke Confirm Attribute Transportation Type Change for the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.24-003 | IEEE 1516.1-2010 (2010 edition) §6.24 | pass | HLA1516.1-OM-6.24-001 | RTI shall not emit Confirm Attribute Transportation Type Change when the corresponding change request is rejected for invalid state, handle, ownership, publication, or transport inputs. | - |
| HLA1516.1-OM-6.24-004 | IEEE 1516.1-2010 (2010 edition) §6.24 | pass | HLA1516.1-OM-6.24-001 | RTI shall route Confirm Attribute Transportation Type Change only to the federate that requested the change in the currently implemented reliable and best-effort transport subset. | This supported-subset row isolates requester-only callback routing for attribute transport-change confirmations in the native Python lane. |
| HLA1516.1-OM-6.25-002 | IEEE 1516.1-2010 (2010 edition) §6.25 | pass | HLA1516.1-OM-6.25-001 | RTI shall report stored attribute transportation overrides for the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.25-003 | IEEE 1516.1-2010 (2010 edition) §6.25 | pass | HLA1516.1-OM-6.25-001 | RTI shall report the default reliable attribute transportation type when no explicit override exists in the currently implemented transport subset. | This supported-subset row isolates the default-state query behavior: absent any explicit attribute override, the backend reports the effective reliable transportation type. |
| HLA1516.1-OM-6.26-002 | IEEE 1516.1-2010 (2010 edition) §6.26 | pass | HLA1516.1-OM-6.26-001 | RTI shall invoke Report Attribute Transportation Type for the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.26-003 | IEEE 1516.1-2010 (2010 edition) §6.26 | pass | HLA1516.1-OM-6.26-001 | RTI shall not emit Report Attribute Transportation Type when the corresponding query is rejected for invalid state, object, or attribute inputs. | - |
| HLA1516.1-OM-6.26-004 | IEEE 1516.1-2010 (2010 edition) §6.26 | pass | HLA1516.1-OM-6.26-001 | RTI shall route Report Attribute Transportation Type only to the federate that issued the corresponding query in the currently implemented reliable and best-effort transport subset. | This supported-subset row isolates requester-only callback routing for attribute transportation reports in the native Python lane. |
| HLA1516.1-OM-6.27-002 | IEEE 1516.1-2010 (2010 edition) §6.27 | pass | HLA1516.1-OM-6.27-001 | RTI shall support Request Interaction Transportation Type Change for the currently implemented reliable and best-effort transport subset. | This supported-subset row covers the live request/change behavior for interaction transportation state in the reliable and best-effort subset, including confirm/query-visible outcomes and invalid-request rejection boundaries. |
| HLA1516.1-OM-6.27-003 | IEEE 1516.1-2010 (2010 edition) §6.27 | pass | HLA1516.1-OM-6.27-001 | RTI shall persist selected interaction transportation overrides across restore in the currently implemented reliable and best-effort transport subset. | This supported-subset row isolates restore persistence for interaction transportation overrides after a request/change has already established non-default transport state. |
| HLA1516.1-OM-6.28-002 | IEEE 1516.1-2010 (2010 edition) §6.28 | pass | HLA1516.1-OM-6.28-001 | RTI shall invoke Confirm Interaction Transportation Type Change for the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.28-003 | IEEE 1516.1-2010 (2010 edition) §6.28 | pass | HLA1516.1-OM-6.28-001 | RTI shall not emit Confirm Interaction Transportation Type Change when the corresponding change request is rejected for invalid state, class, publication, or transport inputs. | - |
| HLA1516.1-OM-6.28-004 | IEEE 1516.1-2010 (2010 edition) §6.28 | pass | HLA1516.1-OM-6.28-001 | RTI shall route Confirm Interaction Transportation Type Change only to the federate that requested the change in the currently implemented reliable and best-effort transport subset. | This supported-subset row isolates requester-only callback routing for interaction transport-change confirmations in the native Python lane. |
| HLA1516.1-OM-6.29-002 | IEEE 1516.1-2010 (2010 edition) §6.29 | pass | HLA1516.1-OM-6.29-001 | RTI shall report stored interaction transportation overrides for the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.29-003 | IEEE 1516.1-2010 (2010 edition) §6.29 | pass | HLA1516.1-OM-6.29-001 | RTI shall report the default reliable interaction transportation type when no explicit override exists in the currently implemented transport subset. | This supported-subset row isolates the default-state query behavior: absent any explicit interaction override, the backend reports the effective reliable transportation type. |
| HLA1516.1-OM-6.30-002 | IEEE 1516.1-2010 (2010 edition) §6.30 | pass | HLA1516.1-OM-6.30-001 | RTI shall invoke Report Interaction Transportation Type for the currently implemented reliable and best-effort transport subset. | - |
| HLA1516.1-OM-6.30-003 | IEEE 1516.1-2010 (2010 edition) §6.30 | pass | HLA1516.1-OM-6.30-001 | RTI shall not emit Report Interaction Transportation Type when the corresponding query is rejected for invalid state or invalid interaction inputs. | - |
| HLA1516.1-OM-6.30-004 | IEEE 1516.1-2010 (2010 edition) §6.30 | pass | HLA1516.1-OM-6.30-001 | RTI shall route Report Interaction Transportation Type only to the federate that issued the corresponding query in the currently implemented reliable and best-effort transport subset. | This supported-subset row isolates requester-only callback routing for interaction transportation reports in the native Python lane. |

## Unbatched callback delivery subset

- Policy ID: `unbatched-callback-delivery-only`
- Supported behavior: The backend preserves externally visible delivery semantics with direct unbatched callbacks.
- Broad-gap rationale: Message combination, packaging, and passelization are not explicitly modeled, so the permissive broad row stays partial by policy.
- Broad-spec status counts: partial=1
- Supported-subset status counts: pass=1

Broad-spec rows:

| Requirement ID | Section | Status | Title | Notes |
|---|---|---|---|---|
| HLA1516.1-OM-6.1.11-001 | IEEE 1516.1-2010 (2010 edition) §6.1.11 | partial | RTI may combine, package, or passelize messages without changing externally visible semantics. | This backend proves externally visible delivery semantics for unbatched callbacks. It does not explicitly model message combination, packaging, or passelization, so this row remains partial by policy until those semantics are modeled or separately justified. |

Supported-subset rows:

| Requirement ID | Section | Status | Broad row | Title | Notes |
|---|---|---|---|---|---|
| HLA1516.1-OM-6.1.11-002 | IEEE 1516.1-2010 (2010 edition) §6.1.11 | pass | HLA1516.1-OM-6.1.11-001 | RTI shall preserve externally visible reflect and interaction callback semantics for the currently implemented direct unbatched delivery subset. | This supported-subset row captures the behavior the repo actually proves today: direct unbatched callback delivery preserves the externally visible reflect, interaction, request-update, and time-managed ordering semantics consumed by the current Python and hosted route-parity scenarios. |

