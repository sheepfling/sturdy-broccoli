# HLA 2010 Python RTI v0.10: MOM/MIM exposure and time-management ordering

This pass advances the pure-Python RTI from a federation/object-management smoke-test RTI toward a traceable development RTI with real standard-MIM loading, useful MOM object/interaction exposure, and deeper timestamp-order delivery semantics.

The implementation is still a development/reference RTI, not a certified RTI. The code is written to keep the HLA-facing API and Java-backend adapters stable while the pure-Python RTI gains conformance coverage incrementally.

## Spec anchors used in this pass

| Area | IEEE 1516.1-2010 anchor | v0.10 implementation focus |
|---|---:|---|
| Federation creation and FDD construction | §4.5, especially §4.5.5 | Load the MIM before supplied FOM modules; use the standard MIM automatically when no custom MIM is supplied; reject the forbidden `HLAstandardMIM` custom-MIM designator path in strict tests later. |
| MOM/MIM | §11 and Annex G | Bundle and parse the real `HLAstandardMIM.xml`, install MOM class/interaction/attribute/parameter names into the FDD catalog, create RTI-owned MOM federation/federate objects, and provide request/report interactions. |
| Logical time and grants | §8.1, §8.8-§8.14 | Maintain logical time, time-regulation/constrained state, lookahead, GALT/LITS approximations, queued TSO messages, and grant semantics for TAR/TARA/NMR/NMRA/FQR. |
| Retractions | §8 and Object Management timestamped-message services | Return retraction handles for queued timestamp-order messages and remove queued messages when `retract` is invoked before delivery. |

## Standard MIM loading

`hla2010/resources/foms/HLAstandardMIM.xml` is now the real standard MIM extracted from the uploaded IEEE 1516.1-2010 download archive instead of a minimal placeholder.

`hla2010.mom.create_standard_mim_module()` parses the bundled XML through the same `hla2010.fom.parse_fom_file()` path used for normal FOM modules. The fallback mini-MIM remains only as a defensive backup for unusual packaging environments.

Federation creation now builds the current FDD in this order:

1. supplied MIM, or bundled standard MIM if no supplied MIM is provided;
2. supplied FOM module designators;
3. transactional join-time FOM module merges from `joinFederationExecution`.

This gives the pure-Python RTI a single catalog for both normal FOM classes and standard MOM/MIM classes.

## MOM object exposure

The pure-Python RTI now creates RTI-owned internal MOM instances:

| MOM object | Purpose |
|---|---|
| `HLAobjectRoot.HLAmanager.HLAfederation` | Federation-wide metadata and dynamic state, including federation name, federates, FOM/MIM designators, and synchronization points. |
| `HLAobjectRoot.HLAmanager.HLAfederate` | Per-joined-federate metadata and dynamic state, including federate name/type/handle, time values, publication/subscription summaries, and service-reporting state. |

These internal objects are discoverable and reflectable through normal HLA object-management paths. They are not owned by an application federate, and their attributes are refreshed as federation state changes.

## MOM/MIM request-report interactions

The v0.10 RTI exposes a practical MOM request/report subset by name from the parsed standard MIM. The implementation tolerates vendor/MIM spelling variants where the 2010 XML names differ in capitalization, for example `HLArequestMIMdata` versus `HLArequestMIMData`.

Implemented request/report behavior includes:

- MIM data request/report;
- FOM module data request/report;
- synchronization-point status request/report;
- publication/subscription summary request/report;
- federate/federation MOM object refresh through attribute-value-update request;
- service-report emission hooks for RTI service invocations.

Reports are sent using normal HLA interaction delivery, so Java bridges and Python federates see the same typed handle/value structures.

## Time-management ordering model

The v0.10 time-management layer adds a queue of timestamp-order messages for time-constrained receiving federates. Timestamped attribute updates and interactions are delivered immediately only when they are receive-order for the receiver; otherwise they are queued until a time-advance service makes them eligible.

### Supported request semantics

| Service | Section anchor | Local behavior |
|---|---:|---|
| `timeAdvanceRequest` | §8.8 | Delivers eligible RO and TSO messages up to the requested time and grants when the request is below the conservative GALT bound when enforcement is enabled. |
| `timeAdvanceRequestAvailable` | §8.9 | Uses the available variant boundary: messages at the grant time may still arrive later, and the GALT boundary is inclusive. |
| `nextMessageRequest` | §8.10 | Grants to the timestamp of the next queued TSO message no greater than the requested time, or to the requested time when no such TSO message exists. |
| `nextMessageRequestAvailable` | §8.11 | Same next-message selection with the available-service future-delivery boundary. |
| `flushQueueRequest` | §8.12 | Delivers queued TSO messages up to the request and issues a flush-queue grant path. The optimistic/GALT details remain simplified. |
| `timeAdvanceGrant` / `flushQueueGrant` callbacks | §8.13-§8.14 | Complete pending requests and update the joined federate's logical time. |

### Query services

The pure-Python RTI now returns development-useful values for:

- `queryLogicalTime`;
- `queryGALT`;
- `queryLITS`;
- `queryLookahead`.

The GALT/LITS calculations are intentionally conservative approximations suitable for local-process simulations and conformance-test scaffolding. They will need more work before claiming full production RTI conformance.

### Timestamp ordering and retraction

Timestamp-order messages now carry:

- timestamp;
- sender federate;
- receiver federate;
- object/interaction payload;
- delivery mode;
- sequence number;
- message retraction handle.

Queued TSO messages are delivered in `(timestamp, sequence)` order. Calling `retract` before delivery removes the queued message and prevents later reflection/receipt.

## Java adapter implications

The Java JPype/Py4J adapters benefit from this pass because the pure-Python RTI and Java translation layer now both rely on the same handle, set, and map abstractions:

- Java-created object/interaction/attribute handles can be represented as stable Python surrogate handles.
- Python maps/sets used by MOM and time-management callbacks are converted through factory-aware handle set/value map services.
- MOM report interactions use normal interaction delivery, so they exercise the same Java callback conversion paths as user FOM interactions.

## Validation added in v0.10

New tests exercise:

- real standard-MIM parsing and class/interaction lookup;
- creation and reflection of MOM federation/federate objects;
- MOM request/report interactions for MIM/FOM/synchronization/publication/subscription data;
- timestamp-order delivery through `nextMessageRequest`;
- TAR versus TARA GALT boundary behavior;
- `queryGALT`, `queryLITS`, and `queryLogicalTime`;
- timestamped-message retraction before delivery;
- Target/Radar regression through Python and Java-shim backends.

## Known gaps for the next pass

1. Complete all MOM service-action semantics, especially adjust/modify switches and full service-report file behavior.
2. Consolidate time-management helper code into a dedicated module to reduce backend size and clarify state transitions.
3. Add full save/restore coordination with timestamped saves and time-advance state interactions.
4. Tighten strict conformance validation around supplied custom MIM designators, MIM/FOM merge conflicts, and OMT table defaults.
5. Extend DDM/time-management interaction tests for region-associated TSO updates and interactions.
6. Replace conservative GALT/LITS approximations with a more formal state-chart-driven implementation.
