# Python Requirement Disposition

This audit projects the shared HLA 2010 requirements matrix onto `python` so every row has an explicit generated `python` disposition.

## Summary

| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |
|---|---:|---:|---:|---:|---:|---:|---:|
| IEEE 1516-2010 unknown | 4 | 1 | 0 | 2 | 0 | 1 | 0 |
| IEEE 1516-2010 §12 | 21 | 21 | 0 | 0 | 0 | 0 | 0 |
| IEEE 1516.1-2010 (2010 edition) §10 | 86 | 84 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §11 | 37 | 35 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §12 | 10 | 9 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §4 | 281 | 278 | 0 | 1 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §5 | 53 | 50 | 0 | 1 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §6 | 121 | 118 | 0 | 1 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §7 | 39 | 37 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §8 | 61 | 59 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §9 | 31 | 29 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.2-2010 (2010 edition) unknown | 18 | 16 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.2-2010 (2010 edition) §4 | 112 | 97 | 0 | 0 | 0 | 15 | 0 |
| IEEE 1516.2-2010 (2010 edition) §5 | 2 | 1 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) §6 | 2 | 1 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) §7 | 15 | 14 | 0 | 0 | 0 | 1 | 0 |
| multi-section unknown | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| multi-section §11 | 6 | 0 | 0 | 0 | 0 | 6 | 0 |
| multi-section §12 | 5 | 0 | 0 | 0 | 0 | 5 | 0 |
| multi-section §4 | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| multi-section §5 | 10 | 0 | 0 | 0 | 0 | 10 | 0 |
| multi-section §6 | 14 | 0 | 0 | 0 | 0 | 14 | 0 |
| multi-section §7 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| multi-section §8 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |

## Non-Verified Rows

| Document | Clause | Requirement | Disposition | Kind | Title |
|---|---|---|---|---|---|
| IEEE 1516-2010 | unknown | HLA1516-FW-001 | vendor-divergent | extracted-requirement | The repo shall treat IEEE 1516-2010 as the top-level framework and keep federate behavior |
| IEEE 1516-2010 | unknown | HLA1516-OBJ-001 | vendor-divergent | extracted-requirement | The repo shall distinguish object-model concepts from programming-language objects and map them to the 1516.1 object services and 1516.2 OMT structure |
| IEEE 1516-2010 | unknown | HLA1516-TIME-001 | not-applicable | extracted-requirement | The repo shall map time concepts to 1516.1 time services and grant/order semantics, including logical time and ordering relationships |
| IEEE 1516.1-2010 (2010 edition) | 4 | AREA-1516.1-4 | not-applicable | section-area | Federation management |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-001 | not-applicable | curated-seed | The RTI shall implement federation-management services for create, join, resign, destroy, save, restore, synchronization, and related lifecycle behavior |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-EFF-001 | vendor-divergent | extracted-requirement | Successful Resign Federation Execution shall remove the federate from federation membership, remove or divest owned objects as directed by the resign action, remove synchronization-point participation, refresh time advancement processing, and clear local publication and subscription state. |
| IEEE 1516.1-2010 (2010 edition) | 5 | AREA-1516.1-5 | not-applicable | section-area | Declaration management |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-001 | not-applicable | extracted-requirement | The RTI shall implement declaration-management services for publication, subscription, registration control, and the associated error and precondition behavior |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.6-001 | vendor-divergent | extracted-requirement | RTI shall support subscribing with update rate reduction where applicable. |
| IEEE 1516.1-2010 (2010 edition) | 6 | AREA-1516.1-6 | not-applicable | section-area | Object management |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-001 | not-applicable | extracted-requirement | The RTI shall implement object-management services for registration, update, delete, discovery, and interaction delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.11-001 | vendor-divergent | extracted-requirement | RTI may combine, package, or passelize messages without changing externally visible semantics. |
| IEEE 1516.1-2010 (2010 edition) | 7 | AREA-1516.1-7 | not-applicable | section-area | Ownership management |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-001 | not-applicable | extracted-requirement | The RTI shall implement ownership-management services for unconditional, negotiated, acquisition, divestiture, and release-request flows |
| IEEE 1516.1-2010 (2010 edition) | 8 | AREA-1516.1-8 | not-applicable | section-area | Time management |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-001 | not-applicable | extracted-requirement | The RTI shall implement time-management services for regulation, constrained behavior, query services, lookahead, order control, and grant delivery |
| IEEE 1516.1-2010 (2010 edition) | 9 | AREA-1516.1-9 | not-applicable | section-area | Data distribution management |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-001 | not-applicable | extracted-requirement | The RTI shall implement DDM services for region creation, routing, and filtered delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 10 | AREA-1516.1-10 | not-applicable | section-area | Support services |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-001 | not-applicable | extracted-requirement | The RTI shall implement support services for lookups, factories, callback control, advisory behavior, and related support operations |
| IEEE 1516.1-2010 (2010 edition) | 11 | AREA-1516.1-11 | not-applicable | section-area | Management object model |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-001 | not-applicable | extracted-requirement | The RTI shall implement MOM behavior for tables, reports, service actions, observer reconstruction, and service-reporting state |
| IEEE 1516.1-2010 (2010 edition) | 12 | AREA-1516.1-12 | not-applicable | section-area | Programming language mappings |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4-omt_components | not-applicable | omt-area | HLA OMT components |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_1-object_model_identification | not-applicable | omt-area | Object model identification |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_10-transportation_type_table | not-applicable | omt-area | Transportation type table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_11-update_rate_table | not-applicable | omt-area | Update rate table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_12-switches_table | not-applicable | omt-area | Switches table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_13-datatype_table | not-applicable | omt-area | Datatype tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_14-notes_table | not-applicable | omt-area | Notes table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_2-object_class_structure | not-applicable | omt-area | Object class structure table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_3-interaction_class_structure | not-applicable | omt-area | Interaction class structure table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_4-attribute_table | not-applicable | omt-area | Attribute table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_5-parameter_table | not-applicable | omt-area | Parameter table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_6-dimension_table | not-applicable | omt-area | Dimension table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_7-time_representation_table | not-applicable | omt-area | Time representation table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_8-user_supplied_tag_table | not-applicable | omt-area | User-supplied tag table |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_9-synchronization_table | not-applicable | omt-area | Synchronization table |
| IEEE 1516.2-2010 (2010 edition) | 5 | REQ-OMT-5-lexicon | not-applicable | omt-area | FOM/SOM lexicon |
| IEEE 1516.2-2010 (2010 edition) | 6 | REQ-OMT-6-conformance | not-applicable | omt-area | Conformance |
| IEEE 1516.2-2010 (2010 edition) | 7 | REQ-OMT-7-merging_rules | not-applicable | omt-area | FOM module/SOM module merging rules |
| IEEE 1516.2-2010 (2010 edition) | unknown | REQ-OMT-Annex_D-dif | not-applicable | omt-area | OMT data interchange format |
| IEEE 1516.2-2010 (2010 edition) | unknown | REQ-OMT-Annex_E-schema | not-applicable | omt-area | OMT conformance XML Schema |
| multi-section | 4 | REQ-SAVE-RESTORE-001 | not-applicable | verification-slice | Save/restore coordinates with time-state and restores logical-time state |
| multi-section | 4 | SCENARIO-TARGET-RADAR-001 | not-applicable | verification-slice | Two-federate Target/Radar simulation runs over Python RTI and Java shim profiles |
| multi-section | 4 | REQ-OMT-PARSE-001 | not-applicable | verification-slice | FOM/MIM XML parsing and name-bearing OMT catalog extraction cover the active 1516.2 object, interaction, attribute, parameter, dimension, and time tables |
| multi-section | 5 | REQ-DM-DDM-INTERPLAY-001 | not-applicable | verification-slice | DM subscriptions and DDM scope filtering compose before delivery |
| multi-section | 5 | REQ-DM-DDM-OBJECT-SCOPE-001 | not-applicable | verification-slice | Object attribute routing is suppressed while regions are out of scope and resumes when regions overlap |
| multi-section | 5 | REQ-OM-UPDATE-RATE-001 | not-applicable | verification-slice | Subscribed and FOM-declared update-rate settings throttle eligible reflected updates across direct, inherited, and regioned subscriptions without suppressing receive-order delivery that has no logical-time basis |
| multi-section | 5 | REQ-DM-DECLARATION-STATE-001 | not-applicable | verification-slice | Declaration-management state gates registration, update, and interaction send behavior |
| multi-section | 5 | REQ-DM-DDM-GATING-001 | not-applicable | verification-slice | DM or DDM subscription declarations are required before object discovery, attribute reflection, or interaction receipt occurs |
| multi-section | 5 | REQ-DM-TIME-INDEPENDENCE-001 | not-applicable | verification-slice | Declaration-management publication and subscription state takes effect even while federates are time managed |
| multi-section | 5 | REQ-DM-UNPUBLISH-OBJECT-001 | not-applicable | verification-slice | Unpublishing object-class attributes removes the federate's ability to perform strict updates for those attributes |
| multi-section | 5 | REQ-DM-UNPUBLISH-INTERACTION-001 | not-applicable | verification-slice | Unpublishing an interaction class removes the federate's ability to perform strict sends for that class |
| multi-section | 5 | REQ-DM-SUBSCRIPTION-DELIVERY-001 | not-applicable | verification-slice | Declaration subscriptions drive discover/reflect/receive delivery visibility |
| multi-section | 5 | REQ-DM-UNSUBSCRIBE-OBJECT-001 | not-applicable | verification-slice | Unsubscribing object-class attributes removes interest in later reflected updates for those attributes |
| multi-section | 6 | REQ-OM-TRANSPORT-REPORT-001 | not-applicable | verification-slice | Transportation-type change, query, and report services emit confirm/report callbacks for the backend's supported reliable and best-effort subset |
| multi-section | 6 | REQ-OM-TRANSPORT-BEST-EFFORT-001 | not-applicable | verification-slice | Best-effort transportation semantics, including FOM-defined defaults and explicit overrides, are implemented distinctly from reliable transport and persist across restore |
| multi-section | 6 | REQ-OM-DISCOVERY-LIFECYCLE-001 | not-applicable | verification-slice | Object registration, discovery, known-class behavior, and removal form a stable object lifecycle |
| multi-section | 6 | REQ-OM-DISCOVERY-CLASS-001 | not-applicable | verification-slice | Discovery chooses the closest subscribed superclass and the discovered class remains stable for later lookups |
| multi-section | 6 | REQ-OM-TRANSPORT-SCOPE-001 | not-applicable | verification-slice | Object-management routing semantics cover transport choice, scope, and local-delete restrictions |
| multi-section | 6 | REQ-OM-ATTRIBUTE-RELEVANCE-001 | not-applicable | verification-slice | Attribute relevance is determined from the combination of publication, subscription, ownership, and DDM scope on a single object instance |
| multi-section | 6 | REQ-OM-ORPHAN-LIFECYCLE-001 | not-applicable | verification-slice | An orphaned object remains discoverable to existing and late subscribers, supports local-delete knowledge clearing, and is removed globally only by explicit delete |
| multi-section | 6 | REQ-OM-LOCAL-KNOWLEDGE-001 | not-applicable | verification-slice | Local delete clears only the invoking federate's object knowledge and allows later rediscovery |
| multi-section | 6 | REQ-OM-ORPHAN-KNOWLEDGE-001 | not-applicable | verification-slice | An ownerless object instance remains discoverable to a joined federate until that federate locally deletes it |
| multi-section | 6 | REQ-OM-REFLECT-KNOWN-CLASS-001 | not-applicable | verification-slice | Reflected attributes are reported using the subscriber's known discovered class handles |
| multi-section | 6 | REQ-OM-TIMED-DELETE-REMOVE-001 | not-applicable | verification-slice | A timestamped delete removes the object from federation knowledge only after the time-managed remove callback is delivered |
| multi-section | 6 | REQ-OM-SCOPE-CALLBACKS-001 | not-applicable | verification-slice | Object-scope transitions emit Attributes In Scope and Attributes Out Of Scope callbacks for known subscribed attributes |
| multi-section | 6 | REQ-OM-REQUEST-VALUE-UPDATE-001 | not-applicable | verification-slice | Attribute-value update requests trigger Provide Attribute Value Update at relevant owners |
| multi-section | 6 | REQ-OM-REQUEST-VALUE-UPDATE-ROUTING-001 | not-applicable | verification-slice | Request Attribute Value Update routes object-target and class-target requests only to relevant owning federates |
| multi-section | 7 | REQ-OMT-MERGE-001 | not-applicable | verification-slice | FOM module merge and MIM/FOM combination rules are enforced for the supported 1516.2 subset |
| multi-section | 8 | REQ-TIME-ORDER-001 | not-applicable | verification-slice | Timestamp-order queues respect local GALT/LITS-style lower-bound rules and DDM filtering before delivery |
| multi-section | 11 | REQ-MOM-TABLE-001 | not-applicable | verification-slice | MOM object and interaction exposure is derived from the active MIM/FOM catalog |
| multi-section | 11 | REQ-MOM-OBSERVER-001 | not-applicable | verification-slice | A MOM observer witness can reconstruct federation-visible MOM objects, reports, and service invocation traffic |
| multi-section | 11 | REQ-MOM-SERVICE-001 | not-applicable | verification-slice | MOM HLAservice interactions are modeled as RTI-received actions with negative-path service failure reporting |
| multi-section | 11 | REQ-MOM-REPORT-001 | not-applicable | verification-slice | MOM reports use the exact parameter names declared in the active MIM catalog |
| multi-section | 11 | REQ-MOM-NEG-001 | not-applicable | verification-slice | Strict MOM decoding reports and raises through generated parameterized negative-path tests |
| multi-section | 11 | REQ-SERVICE-FILE-001 | not-applicable | verification-slice | Service-report file output contains initial and per-service records with section anchors |
| multi-section | 12 | REQ-SAVE-RESTORE-CALLBACK-POLICY-001 | not-applicable | verification-slice | Save/restore treats callback enablement as local runtime policy rather than persisted federation state |
| multi-section | 12 | REQ-SAVE-RESTORE-ROUTING-STATE-001 | not-applicable | verification-slice | Save/restore reinstates saved object and interaction subscription-routing state rather than preserving dirty post-save declaration mutations |
| multi-section | 12 | REQ-SAVE-RESTORE-OBJECT-STATE-001 | not-applicable | verification-slice | Save/restore reinstates saved object existence, name mapping, attribute values, and ownership state |
| multi-section | 12 | REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001 | not-applicable | verification-slice | Save/restore reinstates saved federate runtime flags, policy switches, reporting switches, conveyance state, order-override state, and transportation-override state |
| multi-section | 12 | REQ-SAVE-RESTORE-TRANSIENT-STATE-001 | not-applicable | verification-slice | Save/restore discards stale pre-restore callback-queue and message-retraction bookkeeping state |
| multi-section | unknown | REQ-OMT-SCHEMA-001 | not-applicable | verification-slice | Annex E schema-family conformance validation is executable for the carried standard schemas and round-trip witnesses |
