# certi-py4j Requirement Disposition

This audit projects the shared HLA 2010 requirements matrix onto `certi-py4j` so every row has an explicit generated `certi-py4j` disposition.

This profile currently inherits the CERTI family-level requirement disposition because the JPype and Py4J routes are documented as Java-profile facades over the same native CERTI runtime path.

## Summary

| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |
|---|---:|---:|---:|---:|---:|---:|---:|
| IEEE 1516-2010 unknown | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| IEEE 1516-2010 §12 | 21 | 0 | 0 | 0 | 0 | 21 | 0 |
| IEEE 1516.1-2010 (2010 edition) §10 | 85 | 0 | 0 | 0 | 0 | 1 | 84 |
| IEEE 1516.1-2010 (2010 edition) §11 | 36 | 0 | 0 | 0 | 0 | 1 | 35 |
| IEEE 1516.1-2010 (2010 edition) §12 | 9 | 0 | 0 | 0 | 0 | 0 | 9 |
| IEEE 1516.1-2010 (2010 edition) §4 | 322 | 82 | 0 | 0 | 153 | 1 | 86 |
| IEEE 1516.1-2010 (2010 edition) §5 | 51 | 0 | 0 | 0 | 0 | 1 | 50 |
| IEEE 1516.1-2010 (2010 edition) §6 | 95 | 12 | 0 | 0 | 80 | 1 | 2 |
| IEEE 1516.1-2010 (2010 edition) §7 | 38 | 12 | 0 | 8 | 16 | 1 | 1 |
| IEEE 1516.1-2010 (2010 edition) §8 | 60 | 37 | 0 | 5 | 0 | 1 | 17 |
| IEEE 1516.1-2010 (2010 edition) §9 | 30 | 0 | 0 | 0 | 29 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) unknown | 16 | 0 | 0 | 0 | 0 | 16 | 0 |
| IEEE 1516.2-2010 (2010 edition) §4 | 97 | 0 | 0 | 0 | 0 | 97 | 0 |
| IEEE 1516.2-2010 (2010 edition) §5 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) §6 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) §7 | 14 | 0 | 0 | 0 | 0 | 14 | 0 |

## Non-Verified Rows

| Document | Clause | Requirement | Disposition | Kind | Title |
|---|---|---|---|---|---|
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.1-001 | not-applicable | extracted-requirement | Federations shall support coordinated save of federation state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.1-002 | not-applicable | extracted-requirement | Save coordination shall collect completion or failure from participating federates before declaring the save outcome |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.1-003 | not-applicable | extracted-requirement | Scheduled save requests shall take effect at the requested logical time when time conditions are satisfied |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.1-004 | not-applicable | extracted-requirement | Federations shall support aborting an in progress save |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-001 | not-applicable | extracted-requirement | Federations shall support coordinated restore from a named saved state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-002 | not-applicable | extracted-requirement | Restore coordination shall collect completion or failure from participating federates before declaring the restore outcome |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-003 | not-applicable | extracted-requirement | Successful restore shall reinstate saved logical time state for participating federates |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-004 | not-applicable | extracted-requirement | Federations shall support aborting an in progress restore |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-005 | not-applicable | extracted-requirement | Successful restore shall reinstate saved object instance existence names and attribute values |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-006 | not-applicable | extracted-requirement | Successful restore shall reinstate saved object ownership and attribute ownership state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-007 | not-applicable | extracted-requirement | Successful restore shall reinstate saved federate runtime flags including asynchronous delivery time-regulation time-constrained and lookahead state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-008 | not-applicable | extracted-requirement | Successful restore shall preserve federate automatic resign directives and advisory-switch settings when they are part of the saved local state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-009 | not-applicable | extracted-requirement | Successful restore shall preserve federate reporting and conveyance switches when they are part of the saved local state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-010 | not-applicable | extracted-requirement | Successful restore shall discard stale pre-restore callback-queue state and reestablish post-restore callback flow from the restored coordination sequence |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-011 | not-applicable | extracted-requirement | Successful restore shall discard stale message-retraction bookkeeping and queued transient retraction state inconsistent with the restored federation state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-012 | not-applicable | extracted-requirement | Successful restore shall reinstate saved attribute order override state when those overrides are part of the saved federate-local delivery state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-013 | not-applicable | extracted-requirement | Successful restore shall reinstate saved interaction order override state when those overrides are part of the saved federate-local delivery state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-014 | not-applicable | extracted-requirement | Callback enable or disable state shall remain a post-restore local runtime policy choice and shall not be reinstated from saved federation state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-015 | not-applicable | extracted-requirement | Successful restore shall reinstate saved attribute transportation override state when those overrides are part of the saved federate-local delivery state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.2-016 | not-applicable | extracted-requirement | Successful restore shall reinstate saved interaction transportation override state when those overrides are part of the saved federate-local delivery state |
| IEEE 1516-2010 | 12 | HLA1516-RULE-12.3-001 | not-applicable | extracted-requirement | Restore requests for unknown save labels shall fail without entering restore in progress state |
| IEEE 1516-2010 | unknown | HLA1516-RULE-001 | not-applicable | extracted-requirement | The repo shall map federation-level architectural rules to RTI lifecycle behavior and federation-state transitions |
| IEEE 1516-2010 | unknown | HLA1516-FW-001 | not-applicable | extracted-requirement | The repo shall present IEEE 1516-2010 as the framework-level standard and keep that layer separated from IEEE 1516.1 RTI services and IEEE 1516.2 OMT structure in the authored hierarchy and reference docs. |
| IEEE 1516-2010 | unknown | HLA1516-OBJ-001 | not-applicable | extracted-requirement | The repo shall distinguish HLA object-model structures from programming-language objects by preserving separate OMT object-class and interaction-class catalogs and cross-linking them to the 1516.1 object-service and 1516.2 OMT families. |
| IEEE 1516-2010 | unknown | HLA1516-TIME-001 | not-applicable | extracted-requirement | The repo shall map time concepts to 1516.1 time services and grant/order semantics, including logical time and ordering relationships |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_10-resignFederationExecution | classification-required | service-requirement | Resign Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_19-federateSaveComplete | not-yet-tested | service-requirement | Federate Save Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_19-federateSaveNotComplete | not-yet-tested | service-requirement | Federate Save Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_2-connect | classification-required | service-requirement | Connect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_20-federationNotSaved | not-yet-tested | service-requirement | Federation Saved service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_21-abortFederationSave | not-yet-tested | service-requirement | Abort Federation Save service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_25-requestFederationRestoreFailed | not-yet-tested | service-requirement | Confirm Federation Restoration Request service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_28-federateRestoreComplete | not-yet-tested | service-requirement | Federate Restore Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_28-federateRestoreNotComplete | not-yet-tested | service-requirement | Federate Restore Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_29-federationNotRestored | not-yet-tested | service-requirement | Federation Restored service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_3-disconnect | classification-required | service-requirement | Disconnect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_30-abortFederationRestore | not-yet-tested | service-requirement | Abort Federation Restore service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_4-connectionLost | classification-required | service-requirement | Connection Lost service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_5-createFederationExecution | classification-required | service-requirement | Create Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_5-createFederationExecutionWithMIM | classification-required | service-requirement | Create Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_6-destroyFederationExecution | classification-required | service-requirement | Destroy Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_7-listFederationExecutions | classification-required | service-requirement | List Federation Executions service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_8-reportFederationExecutions | classification-required | service-requirement | Report Federation Executions service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_9-joinFederationExecution | classification-required | service-requirement | Join Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-001 | not-applicable | extracted-requirement | The RTI shall implement federation-management services for create, join, resign, destroy, save, restore, synchronization, and related lifecycle behavior |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1-001 | classification-required | extracted-requirement | RTI shall support federate connection federation creation federation joining resignation and disconnection as distinct lifecycle states |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1-002 | classification-required | extracted-requirement | A federate shall connect before creating or joining a federation execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1-003 | classification-required | extracted-requirement | A federate shall disconnect when it has resigned and has no further intent to create or join federation executions |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1-004 | classification-required | extracted-requirement | RTI shall support callback delivery according to the selected callback model |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1-005 | classification-required | extracted-requirement | RTI shall allow one application to participate as multiple joined federates |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1-006 | classification-required | extracted-requirement | RTI shall allow one application to participate in multiple federation executions |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.2-001 | classification-required | extracted-requirement | RTI shall support federation save and restore coordination |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.2-002 | classification-required | extracted-requirement | RTI shall preserve queued messages required for federation save restore |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.3-001 | classification-required | extracted-requirement | RTI shall track each synchronization point independently |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.4-001 | classification-required | extracted-requirement | RTI shall retain and combine FOM Document Data from FOM modules |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.4-002 | classification-required | extracted-requirement | RTI shall provide the standard MIM automatically when required |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.4.1-001 | classification-required | extracted-requirement | RTI shall reject invalid or incompatible FOM modules |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.4.1-002 | classification-required | extracted-requirement | If a FOM module or MIM definition is rejected the RTI shall reject it in entirety |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.4.2-001 | classification-required | extracted-requirement | RTI shall provide access to the current FDD individual FOM modules and the MIM |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.5-001 | classification-required | extracted-requirement | HLA1516.1-FM-4.1.5-001 |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.5-002 | classification-required | extracted-requirement | HLA1516.1-FM-4.1.5-002 |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-001 | classification-required | extracted-requirement | RTI shall provide Resign Federation Execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-ARG-001 | classification-required | extracted-requirement | Resign Federation Execution shall accept the clause-defined resign directives and apply their corresponding delete-object cancel-pending-acquisition or unconditional-divest behavior to the current federate state. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-CB-001 | classification-required | extracted-requirement | After successful resignation, the resigned federate shall no longer receive federation-participation callbacks as a joined member. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-EFF-001 | classification-required | extracted-requirement | Successful Resign Federation Execution shall remove the federate from federation membership, remove or divest owned objects as directed by the resign action, remove synchronization-point participation, refresh time advancement processing, and clear local publication and subscription state. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-EXC-001 | classification-required | extracted-requirement | Resign Federation Execution shall distinguish not-connected, not-joined, invalid-resign-action, owns-attributes, and ownership-acquisition-pending failures. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-MOM-001 | classification-required | extracted-requirement | Successful Resign Federation Execution shall remove the resigned federate's MOM federate object and refresh MOM federation state for the remaining federation members. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-PRE-001 | classification-required | extracted-requirement | Resign Federation Execution shall require a connected ambassador that is currently joined and shall validate ownership and pending-acquisition conditions against the selected resign action. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Resign Federation Execution service. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-TEST-001 | classification-required | extracted-requirement | Resign Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-ARG-001 | not-yet-tested | extracted-requirement | Request Federation Save shall accept and validate the federation save label that identifies the active save request. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-ARG-002 | not-yet-tested | extracted-requirement | Request Federation Save shall accept and validate the optional logical time timestamp used to schedule a future save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-CB-001 | not-yet-tested | extracted-requirement | Request Federation Save shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-EFF-001 | not-yet-tested | extracted-requirement | Successful Request Federation Save processing shall set the active save label and move joined federates into the instructed-to-save lifecycle status. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-EXC-001 | not-yet-tested | extracted-requirement | Request Federation Save shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-MOM-001 | not-yet-tested | extracted-requirement | Request Federation Save effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-PRE-001 | not-yet-tested | extracted-requirement | Request Federation Save shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.16. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Request Federation Save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-TEST-001 | not-yet-tested | extracted-requirement | Request Federation Save shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-ARG-001 | not-yet-tested | extracted-requirement | Initiate Federate Save shall carry the federation save label being initiated for the participating federate. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-ARG-002 | not-yet-tested | extracted-requirement | Initiate Federate Save shall carry the scheduled logical time timestamp when the save was requested for a future logical time. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-CB-001 | not-yet-tested | extracted-requirement | The Initiate Federate Save callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-EFF-001 | not-yet-tested | extracted-requirement | Initiate Federate Save shall deliver the requested save label to joined federates when a federation save begins. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-EXC-001 | not-yet-tested | extracted-requirement | Initiate Federate Save shall remain a distinct save-start callback that carries the active save label instead of collapsing into only the later federation-saved or save-status-response callbacks. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-MOM-001 | not-yet-tested | extracted-requirement | Initiate Federate Save effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-PRE-001 | not-yet-tested | extracted-requirement | The Initiate Federate Save requirement shall apply only when the synchronization or save/restore preconditions for clause 4.17 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the each participating federate to initiate save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-TEST-001 | not-yet-tested | extracted-requirement | Initiate Federate Save shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-CB-001 | not-yet-tested | extracted-requirement | Federate Save Begun shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-EFF-001 | not-yet-tested | extracted-requirement | Successful Federate Save Begun processing shall move the reporting federate into the FEDERATE_SAVING save-status phase while peers remain instructed to save until they also begin saving. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-EXC-001 | not-yet-tested | extracted-requirement | Federate Save Begun shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-MOM-001 | not-yet-tested | extracted-requirement | Federate Save Begun effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-PRE-001 | not-yet-tested | extracted-requirement | Federate Save Begun shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.18. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Federate Save Begun. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-TEST-001 | not-yet-tested | extracted-requirement | Federate Save Begun shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-001 | not-yet-tested | extracted-requirement | RTI shall provide Federate Save Complete and Federate Save Not Complete |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-ARG-001 | not-yet-tested | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall surface the per-federate save success indicator through the complete versus not-complete service split. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-CB-001 | not-yet-tested | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-EFF-001 | not-yet-tested | extracted-requirement | Successful Federate Save Complete and Federate Save Not Complete processing shall record per-federate save outcomes and transition completed federates into waiting-for-federation-to-save or failure-cleared states. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-EXC-001 | not-yet-tested | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-MOM-001 | not-yet-tested | extracted-requirement | Federate Save Complete and Federate Save Not Complete effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-PRE-001 | not-yet-tested | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.19. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Federate Save Complete and Federate Save Not Complete. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-TEST-001 | not-yet-tested | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-001 | classification-required | extracted-requirement | RTI shall provide a Connect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-ARG-001 | classification-required | extracted-requirement | Connect shall accept and persist the selected callback model argument that governs subsequent RTI callback delivery. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-ARG-002 | classification-required | extracted-requirement | Connect shall accept and persist the optional local settings designator argument when one is supplied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-CB-001 | classification-required | extracted-requirement | Connect shall establish the callback-delivery model that governs subsequent RTI callback behavior for the connected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-EFF-001 | classification-required | extracted-requirement | Successful Connect shall bind the ambassador, persist the selected callback model, persist the optional local settings designator, and mark the ambassador connected. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-EXC-001 | classification-required | extracted-requirement | Connect shall report an AlreadyConnected error for a repeated connection attempt on the same ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-MOM-001 | classification-required | extracted-requirement | Connection state relevant to later federation participation should be representable through MOM-visible federate state once the connected ambassador joins a federation. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-PRE-001 | classification-required | extracted-requirement | Connect shall be rejected when the RTI ambassador is already connected. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Connect service with federate ambassador, callback model, and optional local settings designator inputs. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-TEST-001 | classification-required | extracted-requirement | Connect shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-001 | not-yet-tested | extracted-requirement | RTI shall report Federation Saved or Federation Not Saved according to save outcome |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-ARG-001 | not-yet-tested | extracted-requirement | Federation Saved and Federation Not Saved shall surface the federation save success indicator through the saved versus not-saved callback split. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-ARG-002 | not-yet-tested | extracted-requirement | Federation Saved and Federation Not Saved shall surface an explicit failure reason when the federation save does not complete successfully. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-CB-001 | not-yet-tested | extracted-requirement | The Federation Saved and Federation Not Saved callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-EFF-001 | not-yet-tested | extracted-requirement | Federation Saved and Federation Not Saved callbacks shall report successful save completion or federate-reported save failure and clear active save state afterward. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-EXC-001 | not-yet-tested | extracted-requirement | Federation Saved and Federation Not Saved shall distinguish successful completion federate-reported failure and aborted-save outcomes through distinct callback names and failure reasons. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-MOM-001 | not-yet-tested | extracted-requirement | Federation Saved and Federation Not Saved effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-PRE-001 | not-yet-tested | extracted-requirement | The Federation Saved and Federation Not Saved requirement shall apply only when the synchronization or save/restore preconditions for clause 4.20 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the Federation Saved or Federation Not Saved according to save outcome. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-TEST-001 | not-yet-tested | extracted-requirement | Federation Saved and Federation Not Saved shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-001 | not-yet-tested | extracted-requirement | RTI shall provide Abort Federation Save |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-CB-001 | not-yet-tested | extracted-requirement | Abort Federation Save shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-EFF-001 | not-yet-tested | extracted-requirement | Successful Abort Federation Save processing shall clear the active save label and report the standard SAVE_ABORTED outcome to joined federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-EXC-001 | not-yet-tested | extracted-requirement | Abort Federation Save shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-MOM-001 | not-yet-tested | extracted-requirement | Abort Federation Save effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-PRE-001 | not-yet-tested | extracted-requirement | Abort Federation Save shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.21. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Abort Federation Save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-TEST-001 | not-yet-tested | extracted-requirement | Abort Federation Save shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-CB-001 | not-yet-tested | extracted-requirement | Query Federation Save Status shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-EFF-001 | not-yet-tested | extracted-requirement | Successful Query Federation Save Status processing shall return federation save status pairs that reflect completed or cleared no-save-in-progress outcomes. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-EXC-001 | not-yet-tested | extracted-requirement | Query Federation Save Status shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-MOM-001 | not-yet-tested | extracted-requirement | Query Federation Save Status effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-PRE-001 | not-yet-tested | extracted-requirement | Query Federation Save Status shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.22. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Query Federation Save Status. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-TEST-001 | not-yet-tested | extracted-requirement | Query Federation Save Status shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-ARG-001 | not-yet-tested | extracted-requirement | Federation Save Status Response shall carry the structured list of joined federates together with the current save status for each. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-CB-001 | not-yet-tested | extracted-requirement | The Federation Save Status Response callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-EFF-001 | not-yet-tested | extracted-requirement | The Federation Save Status Response callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-EXC-001 | not-yet-tested | extracted-requirement | Federation Save Status Response shall return structured per-federate save-status pairs for the current save lifecycle instead of collapsing save completion into an unlabeled generic acknowledgement. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-MOM-001 | not-yet-tested | extracted-requirement | Federation Save Status Response effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-PRE-001 | not-yet-tested | extracted-requirement | The Federation Save Status Response requirement shall apply only when the synchronization or save/restore preconditions for clause 4.23 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the federation save status through Federation Save Status Response. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-TEST-001 | not-yet-tested | extracted-requirement | Federation Save Status Response shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-ARG-001 | not-yet-tested | extracted-requirement | Request Federation Restore shall accept and validate the federation save label naming the restore set to request. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-CB-001 | not-yet-tested | extracted-requirement | Request Federation Restore shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-EFF-001 | not-yet-tested | extracted-requirement | Successful Request Federation Restore processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-EXC-001 | not-yet-tested | extracted-requirement | Request Federation Restore shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-MOM-001 | not-yet-tested | extracted-requirement | Request Federation Restore effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-PRE-001 | not-yet-tested | extracted-requirement | Request Federation Restore shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.24. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Request Federation Restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-TEST-001 | not-yet-tested | extracted-requirement | Request Federation Restore shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-001 | not-yet-tested | extracted-requirement | RTI shall confirm federation restoration request success or failure |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-ARG-001 | not-yet-tested | extracted-requirement | Request Federation Restore confirmation shall carry the federation save label that was requested for restoration. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-ARG-002 | not-yet-tested | extracted-requirement | Request Federation Restore confirmation shall surface the request success indicator through the succeeded versus failed callback split. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-CB-001 | not-yet-tested | extracted-requirement | The Request Federation Restore confirmation callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-EFF-001 | not-yet-tested | extracted-requirement | The Request Federation Restore confirmation callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-EXC-001 | not-yet-tested | extracted-requirement | Request Federation Restore confirmation shall distinguish missing-save-label failure from successful restore-request acceptance by using failed versus succeeded callbacks and by suppressing restore-status state on the failed path. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-MOM-001 | not-yet-tested | extracted-requirement | Request Federation Restore confirmation effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-PRE-001 | not-yet-tested | extracted-requirement | The Request Federation Restore confirmation requirement shall apply only when the synchronization or save/restore preconditions for clause 4.25 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the federation restoration request success or failure. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-TEST-001 | not-yet-tested | extracted-requirement | Request Federation Restore confirmation shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-CB-001 | not-yet-tested | extracted-requirement | The Federation Restore Begun callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-EFF-001 | not-yet-tested | extracted-requirement | The Federation Restore Begun callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-EXC-001 | not-yet-tested | extracted-requirement | Federation Restore Begun shall remain a distinct restore-start callback with no payload rather than collapsing into either the restore-status-response or initiate-federate-restore callbacks. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-MOM-001 | not-yet-tested | extracted-requirement | Federation Restore Begun effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-PRE-001 | not-yet-tested | extracted-requirement | The Federation Restore Begun requirement shall apply only when the synchronization or save/restore preconditions for clause 4.26 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the when federation restore has begun. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-TEST-001 | not-yet-tested | extracted-requirement | Federation Restore Begun shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-ARG-001 | not-yet-tested | extracted-requirement | Initiate Federate Restore shall carry the federation save label that the federate is being asked to restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-ARG-002 | not-yet-tested | extracted-requirement | Initiate Federate Restore shall carry the joined federate designator that identifies the pre-restore federate handle being restored. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-ARG-003 | not-yet-tested | extracted-requirement | Initiate Federate Restore shall carry the federate name of the participant being restored. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-CB-001 | not-yet-tested | extracted-requirement | The Initiate Federate Restore callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-EFF-001 | not-yet-tested | extracted-requirement | The Initiate Federate Restore callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-EXC-001 | not-yet-tested | extracted-requirement | Initiate Federate Restore shall remain a distinct targeted restore callback that carries the save label federate name and pre-restore handle instead of collapsing into the restore-begun or status-response callbacks. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-MOM-001 | not-yet-tested | extracted-requirement | Initiate Federate Restore effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-PRE-001 | not-yet-tested | extracted-requirement | The Initiate Federate Restore requirement shall apply only when the synchronization or save/restore preconditions for clause 4.27 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the each participating federate to initiate restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-TEST-001 | not-yet-tested | extracted-requirement | Initiate Federate Restore shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-001 | not-yet-tested | extracted-requirement | RTI shall provide Federate Restore Complete and Federate Restore Not Complete |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-ARG-001 | not-yet-tested | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall surface the per-federate restore success indicator through the complete versus not-complete service split. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-CB-001 | not-yet-tested | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-EFF-001 | not-yet-tested | extracted-requirement | Successful Federate Restore Complete and Federate Restore Not Complete processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-EXC-001 | not-yet-tested | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-MOM-001 | not-yet-tested | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-PRE-001 | not-yet-tested | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.28. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Federate Restore Complete and Federate Restore Not Complete. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-TEST-001 | not-yet-tested | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-001 | not-yet-tested | extracted-requirement | RTI shall report Federation Restored or Federation Not Restored according to restore outcome |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-ARG-001 | not-yet-tested | extracted-requirement | Federation Restored and Federation Not Restored shall surface the federation restore success indicator through the restored versus not-restored callback split. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-ARG-002 | not-yet-tested | extracted-requirement | Federation Restored and Federation Not Restored shall surface an explicit failure reason when the federation restore does not complete successfully. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-CB-001 | not-yet-tested | extracted-requirement | The Federation Restored and Federation Not Restored callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-EFF-001 | not-yet-tested | extracted-requirement | The Federation Restored and Federation Not Restored callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-EXC-001 | not-yet-tested | extracted-requirement | Federation Restored and Federation Not Restored shall distinguish restore-failure outcomes such as federate-reported failure and restore-aborted through distinct failure reasons in the federationNotRestored callback. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-MOM-001 | not-yet-tested | extracted-requirement | Federation Restored and Federation Not Restored effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-PRE-001 | not-yet-tested | extracted-requirement | The Federation Restored and Federation Not Restored requirement shall apply only when the synchronization or save/restore preconditions for clause 4.29 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the Federation Restored or Federation Not Restored according to restore outcome. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-TEST-001 | not-yet-tested | extracted-requirement | Federation Restored and Federation Not Restored shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-001 | classification-required | extracted-requirement | RTI shall provide a Disconnect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-CB-001 | classification-required | extracted-requirement | After Disconnect, the RTI shall cease callback delivery to the disconnected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-EFF-001 | classification-required | extracted-requirement | Successful Disconnect shall clear connected state, clear the bound ambassador reference, and clear queued callbacks for the disconnected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-EXC-001 | classification-required | extracted-requirement | Disconnect shall report FederateIsExecutionMember when a joined federate attempts to disconnect before resigning. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-MOM-001 | classification-required | extracted-requirement | Disconnect should leave no active MOM-visible federate session associated with the disconnected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-PRE-001 | classification-required | extracted-requirement | Disconnect shall require a connected ambassador that is no longer a federation execution member. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Disconnect service. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-TEST-001 | classification-required | extracted-requirement | Disconnect shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-001 | not-yet-tested | extracted-requirement | RTI shall provide Abort Federation Restore |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-CB-001 | not-yet-tested | extracted-requirement | Abort Federation Restore shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-EFF-001 | not-yet-tested | extracted-requirement | Successful Abort Federation Restore processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-EXC-001 | not-yet-tested | extracted-requirement | Abort Federation Restore shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-MOM-001 | not-yet-tested | extracted-requirement | Abort Federation Restore effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-PRE-001 | not-yet-tested | extracted-requirement | Abort Federation Restore shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.30. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Abort Federation Restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-TEST-001 | not-yet-tested | extracted-requirement | Abort Federation Restore shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-CB-001 | not-yet-tested | extracted-requirement | Query Federation Restore Status shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-EFF-001 | not-yet-tested | extracted-requirement | Successful Query Federation Restore Status processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-EXC-001 | not-yet-tested | extracted-requirement | Query Federation Restore Status shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-MOM-001 | not-yet-tested | extracted-requirement | Query Federation Restore Status effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-PRE-001 | not-yet-tested | extracted-requirement | Query Federation Restore Status shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.31. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-SIG-001 | not-yet-tested | extracted-requirement | RTI shall provide the Query Federation Restore Status. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-TEST-001 | not-yet-tested | extracted-requirement | Query Federation Restore Status shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-ARG-001 | not-yet-tested | extracted-requirement | Federation Restore Status Response shall carry the structured list of joined federates together with the current restore status for each. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-CB-001 | not-yet-tested | extracted-requirement | The Federation Restore Status Response callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-EFF-001 | not-yet-tested | extracted-requirement | The Federation Restore Status Response callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-EXC-001 | not-yet-tested | extracted-requirement | Federation Restore Status Response shall distinguish pending restore from cleared no-restore-in-progress states across successful failed aborted and missing-save-label restore paths. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-MOM-001 | not-yet-tested | extracted-requirement | Federation Restore Status Response effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-PRE-001 | not-yet-tested | extracted-requirement | The Federation Restore Status Response requirement shall apply only when the synchronization or save/restore preconditions for clause 4.32 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-SIG-001 | not-yet-tested | extracted-requirement | RTI shall deliver the federation restore status through Federation Restore Status Response. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-TEST-001 | not-yet-tested | extracted-requirement | Federation Restore Status Response shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-001 | classification-required | extracted-requirement | RTI shall provide Create Federation Execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-ARG-001 | classification-required | extracted-requirement | Create Federation Execution shall accept and validate the federation execution name argument across creation and duplicate-name rejection paths. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-ARG-002 | classification-required | extracted-requirement | Create Federation Execution shall accept and validate the supplied FOM module designators used to assemble the created federation model. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-ARG-003 | classification-required | extracted-requirement | Create Federation Execution shall accept and validate the optional explicit MIM designator when the overload surface supplies one. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-ARG-004 | classification-required | extracted-requirement | Create Federation Execution shall accept the optional logical time implementation argument when provided and otherwise choose the active logical time factory from the merged federation model or configured default. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-CB-001 | classification-required | extracted-requirement | Create Federation Execution shall make the created federation observable to subsequent callback-based reporting services such as Report Federation Executions. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-EFF-001 | classification-required | extracted-requirement | Successful Create Federation Execution shall install the federation, resolve and merge the supplied FOM modules, supply the standard MIM by default when needed, and choose a logical time factory compatible with the merged model. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-EXC-001 | classification-required | extracted-requirement | Create Federation Execution shall distinguish duplicate-name, FOM-open, FOM-read, MIM-open, MIM-read, invalid-time-factory, inconsistent-FOM, and invalid-standard-MIM-designator failures. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-MOM-001 | classification-required | extracted-requirement | Successful Create Federation Execution shall expose the standard MIM-backed federation object model so MOM federation classes and interactions are available once a federate joins. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-PRE-001 | classification-required | extracted-requirement | Create Federation Execution shall require a connected ambassador and shall reject duplicate federation execution names. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Create Federation Execution service, including the explicit-MIM overload shape used by the current API surface. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-TEST-001 | classification-required | extracted-requirement | Create Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-001 | classification-required | extracted-requirement | RTI shall provide Destroy Federation Execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-ARG-001 | classification-required | extracted-requirement | Destroy Federation Execution shall accept and validate the target federation execution name argument across missing joined and successful destroy paths. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-CB-001 | classification-required | extracted-requirement | After successful destruction, callback-based federation listing shall no longer report the destroyed federation execution. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-EFF-001 | classification-required | extracted-requirement | Successful Destroy Federation Execution shall remove the target federation execution from the RTI federation catalog. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-EXC-001 | classification-required | extracted-requirement | Destroy Federation Execution shall report FederatesCurrentlyJoined when members remain and FederationExecutionDoesNotExist when the target federation is unknown. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-MOM-001 | classification-required | extracted-requirement | Successful destruction should remove the destroyed federation from subsequent MOM-visible federation state and reports. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-PRE-001 | classification-required | extracted-requirement | Destroy Federation Execution shall require a connected ambassador and a target federation execution that has no currently joined federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Destroy Federation Execution service. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-TEST-001 | classification-required | extracted-requirement | Destroy Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-001 | classification-required | extracted-requirement | RTI shall provide Join Federation Execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-ARG-001 | classification-required | extracted-requirement | Join Federation Execution shall accept an omitted federate-name argument and assign a generated unique federate name to the joiner. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-ARG-002 | classification-required | extracted-requirement | Join Federation Execution shall accept and persist the supplied federate type for the joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-ARG-003 | classification-required | extracted-requirement | Join Federation Execution shall accept and resolve the supplied federation execution name to the target federation. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-ARG-004 | classification-required | extracted-requirement | Join Federation Execution shall accept and merge the optional additional FOM module designators supplied by the joiner. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-CB-001 | classification-required | extracted-requirement | Successful Join Federation Execution shall trigger delivery of any open synchronization-point announcements relevant to the joiner and enable subsequent callback delivery for joined participation. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-EFF-001 | classification-required | extracted-requirement | Successful Join Federation Execution shall allocate a federate handle, bind the federate to the target federation, initialize logical time and lookahead state, merge any accepted additional FOM modules, and register the federate in the federation state. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-EXC-001 | classification-required | extracted-requirement | Join Federation Execution shall distinguish not-connected, missing-federation, duplicate-federate-name, already-joined, save-in-progress, restore-in-progress, FOM-open, FOM-read, invalid-time-factory, and inconsistent-FOM failures. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-MOM-001 | classification-required | extracted-requirement | Successful Join Federation Execution shall create or refresh the joined federate's MOM-visible federate object and refresh MOM federation state. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-PRE-001 | classification-required | extracted-requirement | Join Federation Execution shall require a connected ambassador that is not already joined, an existing federation execution, a non-conflicting federate name, and no save or restore already in progress for the federation. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Join Federation Execution service, including the overload shapes that accept generated federate names and optional additional FOM modules. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-TEST-001 | classification-required | extracted-requirement | Join Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-FED-DM-5_10-startRegistrationForObjectClass | classification-required | service-requirement | Start Registration For Object Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-FED-DM-5_11-stopRegistrationForObjectClass | classification-required | service-requirement | Stop Registration For Object Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-FED-DM-5_12-turnInteractionsOn | classification-required | service-requirement | Turn Interactions On service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-FED-DM-5_13-turnInteractionsOff | classification-required | service-requirement | Turn Interactions Off service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_2-publishObjectClassAttributes | classification-required | service-requirement | Publish Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_3-unpublishObjectClass | classification-required | service-requirement | Unpublish Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_3-unpublishObjectClassAttributes | classification-required | service-requirement | Unpublish Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_4-publishInteractionClass | classification-required | service-requirement | Publish Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_5-unpublishInteractionClass | classification-required | service-requirement | Unpublish Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_6-subscribeObjectClassAttributes | classification-required | service-requirement | Subscribe Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_6-subscribeObjectClassAttributesPassively | classification-required | service-requirement | Subscribe Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_7-unsubscribeObjectClass | classification-required | service-requirement | Unsubscribe Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_7-unsubscribeObjectClassAttributes | classification-required | service-requirement | Unsubscribe Object Class Attributes service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_8-subscribeInteractionClass | classification-required | service-requirement | Subscribe Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_8-subscribeInteractionClassPassively | classification-required | service-requirement | Subscribe Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | REQ-RTI-DM-5_9-unsubscribeInteractionClass | classification-required | service-requirement | Unsubscribe Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-001 | not-applicable | extracted-requirement | The RTI shall implement declaration-management services for publication, subscription, registration control, and the associated error and precondition behavior |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1-001 | classification-required | extracted-requirement | Joined federates shall use DM services to declare intent to generate information. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1-002 | classification-required | extracted-requirement | A joined federate shall invoke appropriate DM services before registering objects, updating attributes, or sending interactions. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1-003 | classification-required | extracted-requirement | Joined federates shall use DM or DDM services before discovering objects, reflecting attributes, or receiving interactions. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1-004 | classification-required | extracted-requirement | DM effects shall be independent of federate logical time. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.1-001 | classification-required | extracted-requirement | Each FDD class shall have at most one immediate superclass. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.1-002 | classification-required | extracted-requirement | Object classes shall expose declared and inherited available attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.1-003 | classification-required | extracted-requirement | Interaction classes shall expose declared and inherited available parameters. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.2-001 | classification-required | extracted-requirement | RTI shall track published object-class attributes per joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.2-002 | classification-required | extracted-requirement | RTI shall track subscribed object-class attributes per joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.3-001 | classification-required | extracted-requirement | RTI shall track published interaction classes per joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.3-002 | classification-required | extracted-requirement | RTI shall track subscribed interaction classes per joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.5-001 | classification-required | extracted-requirement | RTI shall support interaction between DM subscriptions and DDM subscriptions. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.6-001 | classification-required | extracted-requirement | RTI shall apply explicit and FOM-declared update-rate designators across direct, inherited, and region-based object-class subscriptions within the implemented logical-time subset. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.10-001 | classification-required | extracted-requirement | RTI shall invoke Start Registration For Object Class when registration becomes useful for subscribed federates. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.11-001 | classification-required | extracted-requirement | RTI shall invoke Stop Registration For Object Class when registration is no longer useful for subscribed federates. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.12-001 | classification-required | extracted-requirement | RTI shall invoke Turn Interactions On when a published interaction class has matching subscribers. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.13-001 | classification-required | extracted-requirement | RTI shall invoke Turn Interactions Off when a published interaction class no longer has matching subscribers. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.2-001 | classification-required | extracted-requirement | RTI shall provide Publish Object Class Attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.2-002 | classification-required | extracted-requirement | Publish Object Class Attributes shall declare attributes a federate may update for instances of an object class. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.2-003 | classification-required | extracted-requirement | RTI shall reject publication requests for unavailable attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.3-001 | classification-required | extracted-requirement | RTI shall provide Unpublish Object Class Attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.3-002 | classification-required | extracted-requirement | Unpublishing shall remove the federate’s ability to update the specified attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.4-001 | classification-required | extracted-requirement | RTI shall provide Publish Interaction Class. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.4-002 | classification-required | extracted-requirement | Publication of an interaction class shall permit the federate to send interactions of that class. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.5-001 | classification-required | extracted-requirement | RTI shall provide Unpublish Interaction Class. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.5-002 | classification-required | extracted-requirement | Unpublishing an interaction class shall remove the federate’s ability to send interactions of that class. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.6-001 | classification-required | extracted-requirement | RTI shall provide Subscribe Object Class Attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.6-002 | classification-required | extracted-requirement | Subscribing to object-class attributes shall make matching object instances discoverable when discovery conditions are met. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.6-003 | classification-required | extracted-requirement | Subscribing to object-class attributes shall make matching in-scope attribute updates reflectable. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.7-001 | classification-required | extracted-requirement | RTI shall provide Unsubscribe Object Class Attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.7-002 | classification-required | extracted-requirement | Unsubscribing shall remove the federate’s interest in the specified object-class attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.8-001 | classification-required | extracted-requirement | RTI shall provide Subscribe Interaction Class. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.8-002 | classification-required | extracted-requirement | Subscribing to an interaction class shall make matching interactions receivable. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.9-001 | classification-required | extracted-requirement | RTI shall provide Unsubscribe Interaction Class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_11-reflectAttributeValues | not-yet-tested | service-requirement | Reflect Attribute Values service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_13-receiveInteraction | not-yet-tested | service-requirement | Receive Interaction service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_14-deleteObjectInstance | not-yet-tested | service-requirement | Delete Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_15-removeObjectInstance | not-yet-tested | service-requirement | Remove Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_16-localDeleteObjectInstance | not-yet-tested | service-requirement | Local Delete Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_17-attributesInScope | not-yet-tested | service-requirement | Attributes In Scope service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_18-attributesOutOfScope | not-yet-tested | service-requirement | Attributes Out Of Scope service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_19-requestAttributeValueUpdate | not-yet-tested | service-requirement | Request Attribute Value Update service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_2-reserveObjectInstanceName | not-yet-tested | service-requirement | Reserve Object Instance Name service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_20-provideAttributeValueUpdate | classification-required | service-requirement | Provide Attribute Value Update service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_21-turnUpdatesOnForObjectInstance | not-yet-tested | service-requirement | Turn Updates On For Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_22-turnUpdatesOffForObjectInstance | not-yet-tested | service-requirement | Turn Updates Off For Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_23-requestAttributeTransportationTypeChange | not-yet-tested | service-requirement | Request Attribute Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_24-confirmAttributeTransportationTypeChange | not-yet-tested | service-requirement | Confirm Attribute Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_25-queryAttributeTransportationType | not-yet-tested | service-requirement | Query Attribute Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_26-reportAttributeTransportationType | not-yet-tested | service-requirement | Report Attribute Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_27-requestInteractionTransportationTypeChange | not-yet-tested | service-requirement | Request Interaction Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_28-confirmInteractionTransportationTypeChange | not-yet-tested | service-requirement | Confirm Interaction Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_29-queryInteractionTransportationType | not-yet-tested | service-requirement | Query Interaction Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_3-objectInstanceNameReservationFailed | not-yet-tested | service-requirement | Object Instance Name Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_3-objectInstanceNameReservationSucceeded | not-yet-tested | service-requirement | Object Instance Name Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_30-reportInteractionTransportationType | not-yet-tested | service-requirement | Report Interaction Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_4-releaseObjectInstanceName | not-yet-tested | service-requirement | Release Object Instance Name service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_5-reserveMultipleObjectInstanceName | not-yet-tested | service-requirement | Reserve Multiple Object Instance Names service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_6-multipleObjectInstanceNameReservationFailed | not-yet-tested | service-requirement | Multiple Object Instance Names Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_6-multipleObjectInstanceNameReservationSucceeded | not-yet-tested | service-requirement | Multiple Object Instance Names Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_7-releaseMultipleObjectInstanceName | not-yet-tested | service-requirement | Release Multiple Object Instance Names service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_8-registerObjectInstance | not-yet-tested | service-requirement | Register Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-discoverObjectInstance | not-yet-tested | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-getProducingFederate | not-yet-tested | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-getSentRegions | not-yet-tested | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-hasProducingFederate | not-yet-tested | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-hasSentRegions | not-yet-tested | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-001 | not-applicable | extracted-requirement | The RTI shall implement object-management services for registration, update, delete, discovery, and interaction delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1-001 | not-yet-tested | extracted-requirement | RTI shall support registration, modification, and deletion of object instances. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1-002 | not-yet-tested | extracted-requirement | RTI shall support sending and receiving interactions. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-001 | not-yet-tested | extracted-requirement | RTI shall discover object instances at subscribed federates when discovery conditions are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-002 | not-yet-tested | extracted-requirement | RTI shall determine a candidate discovery class from the registered class or closest subscribed superclass. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-003 | not-yet-tested | extracted-requirement | Once discovered, an object instance’s discovered class shall not change. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-004 | not-yet-tested | extracted-requirement | A registered or discovered object instance shall become known to the joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.10-001 | not-yet-tested | extracted-requirement | RTI shall use FOM-declared and explicitly selected reliable and best-effort transportation types for object updates and interactions, including query/report visibility and restore persistence within the implemented transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.11-001 | classification-required | extracted-requirement | RTI shall preserve externally visible reflect, interaction, request-update, and time-managed callback semantics for the implemented direct unbatched delivery subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.12-001 | not-yet-tested | extracted-requirement | RTI shall throttle timed reflected attribute delivery according to explicit and FOM-declared update-rate designators while preserving receive-order delivery that has no logical-time basis. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.2-001 | not-yet-tested | extracted-requirement | RTI shall determine whether an instance attribute is in scope for each joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.3-001 | not-yet-tested | extracted-requirement | RTI shall reflect attribute updates only when attributes are in scope and subscribed. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.4-001 | not-yet-tested | extracted-requirement | RTI shall not reflect out-of-scope attribute updates except where required by service semantics. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.5-001 | not-yet-tested | extracted-requirement | RTI shall determine attribute relevance from publication, subscription, ownership, and scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.6-001 | not-yet-tested | extracted-requirement | RTI shall handle orphan object instances according to ownership and discovery rules. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.7-001 | not-yet-tested | extracted-requirement | RTI shall deliver interactions to joined federates subscribed to the relevant interaction class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.11-001 | not-yet-tested | extracted-requirement | RTI shall invoke Reflect Attribute Values to deliver attribute updates. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.11-002 | not-yet-tested | extracted-requirement | Reflected attributes shall correspond to attributes available at the object instance’s known class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.13-001 | not-yet-tested | extracted-requirement | RTI shall invoke Receive Interaction for matching subscribed federates. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.14-001 | not-yet-tested | extracted-requirement | RTI shall provide Delete Object Instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.14-002 | not-yet-tested | extracted-requirement | Delete Object Instance shall remove an object instance from the federation execution according to ownership and time rules. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.15-001 | not-yet-tested | extracted-requirement | RTI shall invoke Remove Object Instance at federates that know the deleted object instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.16-001 | not-yet-tested | extracted-requirement | RTI shall provide Local Delete Object Instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.16-002 | not-yet-tested | extracted-requirement | Local Delete Object Instance shall remove knowledge of the object instance only at the invoking federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.17-001 | not-yet-tested | extracted-requirement | RTI shall invoke Attributes In Scope when subscribed attributes become in scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.18-001 | not-yet-tested | extracted-requirement | RTI shall invoke Attributes Out Of Scope when subscribed attributes go out of scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.19-001 | not-yet-tested | extracted-requirement | RTI shall provide Request Attribute Value Update. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.19-002 | not-yet-tested | extracted-requirement | Request Attribute Value Update shall cause relevant owning federates to receive a request to provide current values. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.2-001 | not-yet-tested | extracted-requirement | RTI shall provide Reserve Object Instance Name. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.21-001 | not-yet-tested | extracted-requirement | RTI shall invoke Turn Updates On For Object Instance when subscribed demand makes a published object instance attribute set newly relevant to the owning federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.21-002 | not-yet-tested | extracted-requirement | Turn Updates On For Object Instance shall carry the object instance handle, relevant attribute set, and applicable update rate designator when one is in effect. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.22-001 | not-yet-tested | extracted-requirement | RTI shall invoke Turn Updates Off For Object Instance when subscribed demand no longer exists for a published object instance attribute set. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.23-001 | not-yet-tested | extracted-requirement | RTI shall support Request Attribute Transportation Type Change for the implemented reliable and best-effort transport subset, including invalid-request rejection and restore persistence of selected overrides. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.24-001 | not-yet-tested | extracted-requirement | RTI shall invoke Confirm Attribute Transportation Type Change only for accepted requester-owned attribute transport changes in the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected requests. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.25-001 | not-yet-tested | extracted-requirement | RTI shall provide Query Attribute Transportation Type for the implemented reliable and best-effort transport subset, including stored overrides and default reliable transport reporting. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.26-001 | not-yet-tested | extracted-requirement | RTI shall invoke Report Attribute Transportation Type only to the querying federate for the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected queries. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.27-001 | not-yet-tested | extracted-requirement | RTI shall support Request Interaction Transportation Type Change for the implemented reliable and best-effort transport subset, including invalid-request rejection and restore persistence of selected overrides. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.28-001 | not-yet-tested | extracted-requirement | RTI shall invoke Confirm Interaction Transportation Type Change only for accepted requester-published interaction transport changes in the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected requests. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.29-001 | not-yet-tested | extracted-requirement | RTI shall provide Query Interaction Transportation Type for the implemented reliable and best-effort transport subset, including stored overrides and default reliable transport reporting. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.3-001 | not-yet-tested | extracted-requirement | RTI shall invoke Object Instance Name Reserved when a reservation succeeds. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.30-001 | not-yet-tested | extracted-requirement | RTI shall invoke Report Interaction Transportation Type only to the querying federate for the implemented reliable and best-effort transport subset, and shall suppress that callback on rejected queries. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.4-001 | not-yet-tested | extracted-requirement | RTI shall provide Release Object Instance Name. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.5-001 | not-yet-tested | extracted-requirement | RTI shall provide Reserve Multiple Object Instance Names. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.6-001 | not-yet-tested | extracted-requirement | RTI shall invoke Multiple Object Instance Names Reserved when multiple-name reservation succeeds. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.7-001 | not-yet-tested | extracted-requirement | RTI shall provide Release Multiple Object Instance Names. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-001 | not-yet-tested | extracted-requirement | RTI shall provide Register Object Instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-002 | not-yet-tested | extracted-requirement | Register Object Instance shall create an object instance of a published object class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-003 | not-yet-tested | extracted-requirement | RTI shall assign a unique object instance handle to each registered object instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-004 | not-yet-tested | extracted-requirement | RTI shall support registration with RTI-assigned or federate-supplied object instance names. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.9-001 | not-yet-tested | extracted-requirement | RTI shall invoke Discover Object Instance at federates satisfying discovery conditions. |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_10-attributeOwnershipUnavailable | vendor-divergent | service-requirement | Attribute Ownership Unavailable service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_12-attributeOwnershipReleaseDenied | not-yet-tested | service-requirement | Attribute Ownership Release Denied service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_13-attributeOwnershipDivestitureIfWanted | not-yet-tested | service-requirement | Attribute Ownership Divestiture If Wanted service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture | classification-required | service-requirement | Cancel Negotiated Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition | vendor-divergent | service-requirement | Cancel Attribute Ownership Acquisition service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation | vendor-divergent | service-requirement | Confirm Attribute Ownership Acquisition Cancellation service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture | vendor-divergent | service-requirement | Negotiated Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption | vendor-divergent | service-requirement | Request Attribute Ownership Assumption service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_5-requestDivestitureConfirmation | not-yet-tested | service-requirement | Request Divestiture Confirmation service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_6-confirmDivestiture | not-yet-tested | service-requirement | Confirm Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_7-attributeOwnershipAcquisitionNotification | not-yet-tested | service-requirement | Attribute Ownership Acquisition Notification service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_8-attributeOwnershipAcquisition | not-yet-tested | service-requirement | Attribute Ownership Acquisition service |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-001 | not-applicable | extracted-requirement | The RTI shall implement ownership-management services for unconditional, negotiated, acquisition, divestiture, and release-request flows |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.1-001 | not-yet-tested | extracted-requirement | RTI shall track ownership of object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.1-002 | not-yet-tested | extracted-requirement | At most one federate may own a given attribute of a given object instance at a time |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.1-003 | not-yet-tested | extracted-requirement | A federate shall update only attributes it owns |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.10-001 | vendor-divergent | extracted-requirement | RTI shall support cancellation of ownership acquisition attempts |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.12-001 | not-yet-tested | extracted-requirement | RTI shall support ownership query for object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.13-001 | not-yet-tested | extracted-requirement | RTI shall notify whether an attribute is owned unowned or owned by another federate |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.3-001 | vendor-divergent | extracted-requirement | RTI shall provide negotiated attribute ownership divestiture |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.4-001 | vendor-divergent | extracted-requirement | RTI shall notify federates when ownership divestiture is requested |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.5-001 | not-yet-tested | extracted-requirement | RTI shall provide attribute ownership acquisition |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.6-001 | not-yet-tested | extracted-requirement | RTI shall provide attribute ownership acquisition if available |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.7-001 | not-yet-tested | extracted-requirement | RTI shall notify a federate when ownership acquisition succeeds |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.7-002 | not-yet-tested | extracted-requirement | RTI shall not invoke attributeOwnershipAcquisitionNotification when the owning federate denies release and acquisition does not complete |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.8-001 | not-yet-tested | extracted-requirement | RTI shall notify a federate when ownership acquisition fails |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_16-queryGALT | vendor-divergent | service-requirement | Query GALT service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_18-queryLITS | vendor-divergent | service-requirement | Query LITS service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_23-changeAttributeOrderType | vendor-divergent | service-requirement | Change Attribute Order Type service |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-001 | not-applicable | extracted-requirement | The RTI shall implement time-management services for regulation, constrained behavior, query services, lookahead, order control, and grant delivery |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1-001 | classification-required | extracted-requirement | RTI shall represent modeled time as points on the HLA time axis |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1-002 | classification-required | extracted-requirement | RTI shall coordinate logical time advancement with object updates and interactions |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.1-001 | classification-required | extracted-requirement | RTI shall treat attribute updates interactions object deletes and DDM region messages as HLA messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-001 | classification-required | extracted-requirement | Each message shall be either timestamp order TSO or receive order RO |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-002 | classification-required | extracted-requirement | RTI shall determine sent message order type from preferred order type timestamp presence and federate time status |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-004 | classification-required | extracted-requirement | RTI shall deliver received TSO messages in timestamp order except where flush queue behavior applies |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.3-001 | classification-required | extracted-requirement | Each joined federate shall have a logical time |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.3-002 | classification-required | extracted-requirement | A joined federate logical time shall only advance |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.3-003 | classification-required | extracted-requirement | RTI shall advance logical time only by issuing Time Advance Grant |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.4-001 | classification-required | extracted-requirement | Only time regulating federates may send TSO messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.4-002 | classification-required | extracted-requirement | A time regulating federate shall provide nonnegative lookahead |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.4-003 | classification-required | extracted-requirement | A time regulating federate shall not send TSO messages earlier than allowed by logical time plus lookahead |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.5-001 | classification-required | extracted-requirement | Only time constrained federates may receive TSO messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.5-002 | classification-required | extracted-requirement | RTI shall use GALT to constrain time advancement |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.5-003 | classification-required | extracted-requirement | RTI shall expose LITS semantics for least incoming timestamp |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.6-001 | classification-required | extracted-requirement | RTI shall support time advance request services and grant only when delivery guarantees are satisfied |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.7-001 | classification-required | extracted-requirement | RTI shall queue pending TSO and RO messages until eligible for delivery |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.16-001 | vendor-divergent | extracted-requirement | RTI shall provide Query GALT |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.18-001 | vendor-divergent | extracted-requirement | RTI shall provide Query LITS |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions | not-yet-tested | service-requirement | Subscribe Interaction Class With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions | not-yet-tested | service-requirement | Subscribe Interaction Class With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions | not-yet-tested | service-requirement | Unsubscribe Interaction Class With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_12-sendInteractionWithRegions | not-yet-tested | service-requirement | Send Interaction With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions | not-yet-tested | service-requirement | Request Attribute Value Update With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_2-createRegion | not-yet-tested | service-requirement | Create Region service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_3-commitRegionModifications | not-yet-tested | service-requirement | Commit Region Modifications service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_4-deleteRegion | not-yet-tested | service-requirement | Delete Region service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions | not-yet-tested | service-requirement | Register Object Instance With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_6-associateRegionsForUpdates | not-yet-tested | service-requirement | Associate Regions For Updates service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_7-unassociateRegionsForUpdates | not-yet-tested | service-requirement | Unassociate Regions For Updates service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions | not-yet-tested | service-requirement | Subscribe Object Class Attributes With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions | not-yet-tested | service-requirement | Subscribe Object Class Attributes With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions | not-yet-tested | service-requirement | Unsubscribe Object Class Attributes With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-001 | not-applicable | extracted-requirement | The RTI shall implement DDM services for region creation, routing, and filtered delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.1-001 | not-yet-tested | extracted-requirement | RTI shall support region-based data distribution management |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.1-002 | not-yet-tested | extracted-requirement | RTI shall use FOM-defined dimensions for DDM routing |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.1-003 | not-yet-tested | extracted-requirement | RTI shall determine relevance from subscription regions and update/send regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.10-001 | not-yet-tested | extracted-requirement | RTI shall support subscribing to interaction classes with regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.11-001 | not-yet-tested | extracted-requirement | RTI shall support unsubscribing interaction classes with regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.12-001 | not-yet-tested | extracted-requirement | RTI shall route interactions based on region overlap where dimensions apply |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.13-001 | not-yet-tested | extracted-requirement | RTI shall route attribute-value update requests based on region overlap |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.2-001 | not-yet-tested | extracted-requirement | RTI shall provide Create Region |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.3-001 | not-yet-tested | extracted-requirement | RTI shall provide Commit Region Modifications |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.4-001 | not-yet-tested | extracted-requirement | RTI shall provide Delete Region |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.5-001 | not-yet-tested | extracted-requirement | RTI shall support registering object instances with associated regions where applicable |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.6-001 | not-yet-tested | extracted-requirement | RTI shall support associating regions with object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.7-001 | not-yet-tested | extracted-requirement | RTI shall support unassociating regions from object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.8-001 | not-yet-tested | extracted-requirement | RTI shall support subscribing to object-class attributes with regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.9-001 | not-yet-tested | extracted-requirement | RTI shall support unsubscribing object-class attributes with regions |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_10-getObjectInstanceName | classification-required | service-requirement | Get Object Instance Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_11-getAttributeHandle | classification-required | service-requirement | Get Attribute Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_12-getAttributeName | classification-required | service-requirement | Get Attribute Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_13-getUpdateRateValue | classification-required | service-requirement | Get Update Rate Value service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_14-getUpdateRateValueForAttribute | classification-required | service-requirement | Get Update Rate Value For Attribute service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_15-getInteractionClassHandle | classification-required | service-requirement | Get Interaction Class Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_16-getInteractionClassName | classification-required | service-requirement | Get Interaction Class Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_17-getParameterHandle | classification-required | service-requirement | Get Parameter Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_18-getParameterName | classification-required | service-requirement | Get Parameter Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_19-getOrderType | classification-required | service-requirement | Get Order Type service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_2-getAutomaticResignDirective | classification-required | service-requirement | Get Automatic Resign Directive service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_20-getOrderName | classification-required | service-requirement | Get Order Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_21-getTransportationType | classification-required | service-requirement | Get Transportation Type Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_21-getTransportationTypeHandle | classification-required | service-requirement | Get Transportation Type Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_22-getTransportationName | classification-required | service-requirement | Get Transportation Type Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_22-getTransportationTypeName | classification-required | service-requirement | Get Transportation Type Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_23-getAvailableDimensionsForClassAttribute | classification-required | service-requirement | Get Available Dimensions For Class Attribute service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_24-getAvailableDimensionsForInteractionClass | classification-required | service-requirement | Get Available Dimensions For Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_25-getDimensionHandle | classification-required | service-requirement | Get Dimension Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_26-getDimensionName | classification-required | service-requirement | Get Dimension Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_27-getDimensionUpperBound | classification-required | service-requirement | Get Dimension Upper Bound service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_28-getDimensionHandleSet | classification-required | service-requirement | Get Dimension Handle Set service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_29-getRangeBounds | classification-required | service-requirement | Get Range Bounds service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_3-setAutomaticResignDirective | classification-required | service-requirement | Set Automatic Resign Directive service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_30-setRangeBounds | classification-required | service-requirement | Set Range Bounds service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_31-normalizeFederateHandle | classification-required | service-requirement | Normalize Federate Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_32-normalizeServiceGroup | classification-required | service-requirement | Normalize Service Group service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_33-enableObjectClassRelevanceAdvisorySwitch | classification-required | service-requirement | Enable Object Class Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_34-disableObjectClassRelevanceAdvisorySwitch | classification-required | service-requirement | Disable Object Class Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_35-enableAttributeRelevanceAdvisorySwitch | classification-required | service-requirement | Enable Attribute Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_36-disableAttributeRelevanceAdvisorySwitch | classification-required | service-requirement | Disable Attribute Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_37-enableAttributeScopeAdvisorySwitch | classification-required | service-requirement | Enable Attribute Scope Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_38-disableAttributeScopeAdvisorySwitch | classification-required | service-requirement | Disable Attribute Scope Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_39-enableInteractionRelevanceAdvisorySwitch | classification-required | service-requirement | Enable Interaction Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_4-getFederateHandle | classification-required | service-requirement | Get Federate Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_40-disableInteractionRelevanceAdvisorySwitch | classification-required | service-requirement | Disable Interaction Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_41-evokeCallback | classification-required | service-requirement | Evoke Callback service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_42-evokeMultipleCallbacks | classification-required | service-requirement | Evoke Multiple Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_43-enableCallbacks | classification-required | service-requirement | Enable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-disableCallbacks | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeHandleSetFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeHandleValueMapFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeSetRegionSetPairListFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getDimensionHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getDimensionHandleSetFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getFederateHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getFederateHandleSetFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getHLAversion | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getInteractionClassHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getMessageRetractionHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getObjectClassHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getObjectInstanceHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getParameterHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getParameterHandleValueMapFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getRegionHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getRegionHandleSetFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getTimeFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getTransportationTypeHandleFactory | classification-required | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_5-getFederateName | classification-required | service-requirement | Get Federate Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_6-getObjectClassHandle | classification-required | service-requirement | Get Object Class Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_7-getObjectClassName | classification-required | service-requirement | Get Object Class Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_8-getKnownObjectClassHandle | classification-required | service-requirement | Get Known Object Class Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_9-getObjectInstanceHandle | classification-required | service-requirement | Get Object Instance Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-001 | not-applicable | extracted-requirement | The RTI shall implement support services for lookups, factories, callback control, advisory behavior, and related support operations |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.1-001 | classification-required | extracted-requirement | RTI shall provide services for name/handle lookup |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.1-002 | classification-required | extracted-requirement | RTI shall provide services for advisory switches |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.1-003 | classification-required | extracted-requirement | RTI shall provide services for ordering transportation and dimension metadata queries |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.10-001 | classification-required | extracted-requirement | RTI shall return object instance handles by object instance name |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.11-001 | classification-required | extracted-requirement | RTI shall return object instance names by object instance handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.12-001 | classification-required | extracted-requirement | RTI shall return dimension handles by dimension name |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.13-001 | classification-required | extracted-requirement | RTI shall return dimension names by dimension handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.14-001 | classification-required | extracted-requirement | RTI shall return available dimensions for object attributes or interactions |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.15-001 | classification-required | extracted-requirement | RTI shall return transportation type handles and names |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.16-001 | classification-required | extracted-requirement | RTI shall return order type handles and names |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.17-001 | classification-required | extracted-requirement | RTI shall support enabling and disabling advisory switches |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.18-001 | classification-required | extracted-requirement | RTI shall provide callbacks for advisory switch changes where required |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.2-001 | classification-required | extracted-requirement | RTI shall return object class handles by object class name |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.3-001 | classification-required | extracted-requirement | RTI shall return object class names by object class handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.4-001 | classification-required | extracted-requirement | RTI shall return attribute handles by attribute name and class |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.5-001 | classification-required | extracted-requirement | RTI shall return attribute names by attribute handle and class |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.6-001 | classification-required | extracted-requirement | RTI shall return interaction class handles by interaction class name |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.7-001 | classification-required | extracted-requirement | RTI shall return interaction class names by interaction class handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.8-001 | classification-required | extracted-requirement | RTI shall return parameter handles by parameter name and interaction class |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.9-001 | classification-required | extracted-requirement | RTI shall return parameter names by parameter handle and interaction class |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-001 | not-applicable | extracted-requirement | The RTI shall implement MOM behavior for tables, reports, service actions, observer reconstruction, and service-reporting state |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-001 | classification-required | extracted-requirement | RTI shall expose management information through standard MOM objects and interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-002 | classification-required | extracted-requirement | MOM shall use the OMT format |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-003 | classification-required | extracted-requirement | FDD for a federation execution shall include all MOM elements |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-004 | classification-required | extracted-requirement | MOM object classes interaction classes attributes and parameters shall be predefined in the FDD |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-005 | classification-required | extracted-requirement | MOM definitions shall not be revised though they may be extended |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-001 | classification-required | extracted-requirement | RTI shall publish MOM object classes required by the standard |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-002 | classification-required | extracted-requirement | RTI shall register one MOM federate object instance for each joined federate |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-003 | classification-required | extracted-requirement | RTI shall register one MOM federation object instance for the federation execution |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-004 | classification-required | extracted-requirement | RTI shall periodically update MOM object attributes according to timing data |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2.1-001 | classification-required | extracted-requirement | MOM object classes may be extended by subclasses or additional attributes |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2.1-002 | classification-required | extracted-requirement | RTI shall not subscribe to any MOM object class |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2.1-003 | classification-required | extracted-requirement | RTI shall not divest ownership of standard MOM instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-001 | classification-required | extracted-requirement | RTI shall support MOM interaction classes according to their defined roles |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-002 | classification-required | extracted-requirement | RTI shall act on MOM adjustment interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-003 | classification-required | extracted-requirement | RTI shall act on MOM request interactions by sending corresponding report interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-004 | classification-required | extracted-requirement | RTI shall send MOM report interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-005 | classification-required | extracted-requirement | RTI shall act on MOM service interactions by invoking HLA services on behalf of another federate |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-006 | classification-required | extracted-requirement | RTI shall not emit the corresponding positive MOM report interaction when a MOM request action or federate-sent MOM report interaction is rejected |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3.1-001 | classification-required | extracted-requirement | RTI shall publish MOM report interactions at the leaf class level |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3.1-002 | classification-required | extracted-requirement | RTI shall ignore added nonstandard parameters when receiving MOM interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4-001 | classification-required | extracted-requirement | RTI shall apply MOM-specific RTI characteristics defined by the standard rather than behaving as a normal joined federate |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-001 | classification-required | extracted-requirement | RTI shall publish all MOM leaf object classes designated as published in the MOM tables |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-002 | classification-required | extracted-requirement | RTI shall publish all required attributes for published MOM object classes |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-003 | classification-required | extracted-requirement | RTI shall publish all MOM leaf interaction classes designated as published |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-004 | classification-required | extracted-requirement | RTI shall subscribe to MOM leaf interaction classes designated as subscribed |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-005 | classification-required | extracted-requirement | RTI shall be neither time regulating nor time constrained |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-006 | classification-required | extracted-requirement | RTI shall never provide timestamps or retraction handles for MOM messages |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-007 | classification-required | extracted-requirement | RTI shall not engage in ownership transfer of MOM instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-008 | classification-required | extracted-requirement | RTI shall not modify transportation or order type of MOM attributes or interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-009 | classification-required | extracted-requirement | RTI shall not use DDM services with MOM except where specifically defined |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-001 | classification-required | extracted-requirement | RTI shall send service invocation reports when service reporting is enabled |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-002 | classification-required | extracted-requirement | RTI shall determine each federate service reporting behavior from the service reporting switch state |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-003 | classification-required | extracted-requirement | RTI shall not emit HLAreportServiceInvocation when the triggering MOM adjustment or request is rejected before the corresponding service action succeeds |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-004 | classification-required | extracted-requirement | RTI shall report standard MOM exception information when exception reporting is enabled |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.6-001 | classification-required | extracted-requirement | MOM table information shall appear in all compliant FOMs and shall not be altered |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeAttributeHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeDimensionHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeFederateHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeInteractionClassHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeMessageRetractionHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeObjectClassHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeObjectInstanceHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeParameterHandle | classification-required | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeRegionHandle | classification-required | service-requirement | Designators |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ID-001 | not-applicable | extracted-requirement | OMT parser shall capture object model identification metadata sufficient to distinguish the module and preserve provenance |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ID-4-001 | not-applicable | extracted-requirement | Object model modules shall contain identification information sufficient to distinguish the module and its provenance |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-001 | not-applicable | extracted-requirement | HLA object models shall be represented using the OMT components defined by the standard |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-002 | not-applicable | extracted-requirement | FOM SOM and MIM parsers shall recognize all standard OMT component tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-003 | not-applicable | extracted-requirement | Validators shall distinguish required optional and conditionally required OMT entries |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-001 | not-applicable | extracted-requirement | Object models shall include object model identification information |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-002 | not-applicable | extracted-requirement | Parser shall extract object model name and model type identification fields when present |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-003 | not-applicable | extracted-requirement | Implementation shall distinguish FOM SOM and standard MIM object model types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-004 | not-applicable | extracted-requirement | Implementation shall preserve identification metadata during parse and serialize round trip |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-001 | not-applicable | extracted-requirement | OMT parser shall preserve transportation-type declarations and resolve attribute and interaction references to valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-001 | not-applicable | extracted-requirement | Object models shall define transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-002 | not-applicable | extracted-requirement | Transportation type names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-003 | not-applicable | extracted-requirement | Parser shall preserve declared transportation type names |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-004 | not-applicable | extracted-requirement | Attributes shall reference only valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-005 | not-applicable | extracted-requirement | Interaction classes shall reference only valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-006 | not-applicable | extracted-requirement | Validator shall reject references to undefined transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-001 | not-applicable | extracted-requirement | OMT parser shall preserve update-rate designators and validate references to them from object-model metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-001 | not-applicable | extracted-requirement | Object models shall support update rate designators |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-002 | not-applicable | extracted-requirement | Update rate designator names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-003 | not-applicable | extracted-requirement | Parser shall preserve declared update rate names and values |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-004 | not-applicable | extracted-requirement | Attributes referencing update rate designators shall reference valid entries |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-005 | not-applicable | extracted-requirement | Validator shall reject undefined update rate references |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-001 | not-applicable | extracted-requirement | OMT parser shall preserve switch declarations and resolve switch references used by MOM and support services |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-001 | not-applicable | extracted-requirement | Object models shall support declaration of switch metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-002 | not-applicable | extracted-requirement | Parser shall preserve declared switch settings |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-003 | not-applicable | extracted-requirement | Validator shall ensure switch references are resolvable |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-002 | not-applicable | extracted-requirement | OMT parser shall support the basic, simple, enumerated, array, fixed-record, and variant-record datatype families and validate their structure |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-001 | not-applicable | extracted-requirement | Object models shall support datatype table declarations |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-002 | not-applicable | extracted-requirement | Basic datatype names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-003 | not-applicable | extracted-requirement | Parser shall preserve endian size encoding and semantics metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-004 | not-applicable | extracted-requirement | Validator shall reject duplicate datatype definitions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-005 | not-applicable | extracted-requirement | Parser shall preserve declared datatype names from datatype tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-006 | not-applicable | extracted-requirement | Parser shall preserve datatype names referenced by attributes and parameters |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-010 | not-applicable | extracted-requirement | Object models shall support simple datatype aliases |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-011 | not-applicable | extracted-requirement | Simple datatypes shall reference valid underlying datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-012 | not-applicable | extracted-requirement | Validator shall reject unresolved datatype references |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-020 | not-applicable | extracted-requirement | Object models shall support enumerated datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-021 | not-applicable | extracted-requirement | Enumeration names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-022 | not-applicable | extracted-requirement | Enumeration values shall be unique within an enumeration |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-023 | not-applicable | extracted-requirement | Parser shall preserve enumeration literal ordering |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-024 | not-applicable | extracted-requirement | Validator shall reject duplicate enumeration values |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-030 | not-applicable | extracted-requirement | Object models shall support fixed arrays |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-031 | not-applicable | extracted-requirement | Object models shall support variable arrays |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-032 | not-applicable | extracted-requirement | Array element types shall reference valid datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-033 | not-applicable | extracted-requirement | Fixed arrays shall define valid cardinality |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-034 | not-applicable | extracted-requirement | Validator shall reject invalid array dimensions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-040 | not-applicable | extracted-requirement | Object models shall support fixed record datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-041 | not-applicable | extracted-requirement | Fixed records shall contain ordered fields |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-042 | not-applicable | extracted-requirement | Fixed record fields shall reference valid datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-043 | not-applicable | extracted-requirement | Parser shall preserve field ordering |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-044 | not-applicable | extracted-requirement | Validator shall reject unresolved field datatype references |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-050 | not-applicable | extracted-requirement | Object models shall support variant record datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-051 | not-applicable | extracted-requirement | Variant records shall define a discriminant |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-052 | not-applicable | extracted-requirement | Alternative branches shall reference valid datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-053 | not-applicable | extracted-requirement | Parser shall preserve discriminant mappings |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-054 | not-applicable | extracted-requirement | Validator shall reject duplicate discriminant alternatives |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-001 | not-applicable | extracted-requirement | OMT parser shall preserve note content through parse and serialization |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-001 | not-applicable | extracted-requirement | OMT elements may contain note metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-002 | not-applicable | extracted-requirement | Parser shall preserve note content |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-003 | not-applicable | extracted-requirement | Serializer shall reproduce note content |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-001 | not-applicable | extracted-requirement | OMT parser shall preserve the object-class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-4.2-001 | not-applicable | extracted-requirement | Object class structure shall preserve class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-4.2-002 | not-applicable | extracted-requirement | Object class definitions shall expose declared and inherited attributes consistently through the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-001 | not-applicable | extracted-requirement | Object models shall define object class hierarchy beneath ObjectRoot |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-002 | not-applicable | extracted-requirement | Each object class except ObjectRoot shall have exactly one immediate superclass |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-003 | not-applicable | extracted-requirement | Parser shall preserve parent-child object class relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-004 | not-applicable | extracted-requirement | Validator shall reject duplicate object class names in the same object class hierarchy |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-005 | not-applicable | extracted-requirement | Implementation shall support inherited attributes through superclass traversal |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-001 | not-applicable | extracted-requirement | OMT parser shall preserve the interaction-class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-4.3-001 | not-applicable | extracted-requirement | Interaction class structure shall preserve class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-4.3-002 | not-applicable | extracted-requirement | Interaction class definitions shall expose declared and inherited parameters consistently through the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-001 | not-applicable | extracted-requirement | Object models shall define interaction class hierarchy beneath InteractionRoot |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-002 | not-applicable | extracted-requirement | Each interaction class except InteractionRoot shall have exactly one immediate superclass |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-003 | not-applicable | extracted-requirement | Parser shall preserve parent-child interaction class relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-004 | not-applicable | extracted-requirement | Validator shall reject duplicate interaction class names in the same interaction hierarchy |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-005 | not-applicable | extracted-requirement | Implementation shall support inherited parameters through superclass traversal |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ATTR-001 | not-applicable | extracted-requirement | OMT parser shall preserve attribute declarations and make them available for object-class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ATTR-4.4-001 | not-applicable | extracted-requirement | Attribute tables shall preserve attribute names and availability for object class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-PARAM-001 | not-applicable | extracted-requirement | OMT parser shall preserve interaction-parameter declarations and make them available for interaction-class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-PARAM-4.5-001 | not-applicable | extracted-requirement | Parameter tables shall preserve parameter names and availability for interaction class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-001 | not-applicable | extracted-requirement | OMT parser shall preserve routing-space dimension names for DDM and region use |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-4.6-001 | not-applicable | extracted-requirement | Dimension tables shall preserve routing-space dimension names for active region and DDM use |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-4.6-002 | not-applicable | extracted-requirement | Dimension names shall be unique within the object model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-001 | not-applicable | extracted-requirement | OMT parser shall preserve logical-time and datatype metadata used by the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.7-001 | not-applicable | extracted-requirement | Time representation tables shall preserve logical time implementation selection from the active model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-001 | not-applicable | extracted-requirement | Object models shall identify logical time representation information where required |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-002 | not-applicable | extracted-requirement | Parser shall extract time datatype and time factory metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-003 | not-applicable | extracted-requirement | RTI integration shall use OMT time representation data to select logical time factories |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-001 | not-applicable | extracted-requirement | Object models shall define user-supplied tag datatype information where required |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-002 | not-applicable | extracted-requirement | Parser shall extract and preserve user-supplied tag representation |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-003 | not-applicable | extracted-requirement | RTI services that carry tags shall validate tag values against the declared tag representation where applicable |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-001 | not-applicable | extracted-requirement | OMT parser shall support declaration, validation, and serialization of synchronization-point metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-001 | not-applicable | extracted-requirement | Object models shall support declaration of synchronization points |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-002 | not-applicable | extracted-requirement | Synchronization point names shall be unique within the object model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-003 | not-applicable | extracted-requirement | Parser shall preserve synchronization point metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-004 | not-applicable | extracted-requirement | Validator shall reject duplicate synchronization point definitions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-005 | not-applicable | extracted-requirement | Synchronization definitions shall survive parse/serialize round-trip |
| IEEE 1516.2-2010 (2010 edition) | 5 | HLA1516.2-OMT-5-001 | not-applicable | extracted-requirement | Implementation documentation shall use the FOM SOM lexicon consistently when naming object model artifacts |
| IEEE 1516.2-2010 (2010 edition) | 6 | HLA1516.2-OMT-6-001 | not-applicable | extracted-requirement | Conformance claims shall distinguish implemented subsets from unimplemented or planned OMT behavior |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-001 | not-applicable | extracted-requirement | OMT merge shall compose class, datatype, dimension, and standard MIM content into a consistent merged representation |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7-001 | not-applicable | extracted-requirement | FOM module merge shall be transactional when rejecting inconsistent logical time representations |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7-002 | not-applicable | extracted-requirement | Create federation with an explicit MIM shall preserve the requested MIM module as active provenance |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-OMT-001 | not-applicable | extracted-requirement | OMT merge shall apply the supported merge rules and reject conflicts that would produce an inconsistent merged model |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-OMT-7-001 | not-applicable | extracted-requirement | FOM module merge shall reject conflicting logical time representations |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-OMT-7-002 | not-applicable | extracted-requirement | FOM module merge shall combine supported modules into one active federation object model catalog |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-001 | not-applicable | extracted-requirement | RTI shall support composition of a federation object model from multiple FOM modules |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-002 | not-applicable | extracted-requirement | Merge process shall preserve class hierarchy consistency |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-003 | not-applicable | extracted-requirement | Merge process shall preserve datatype consistency |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-004 | not-applicable | extracted-requirement | Merge process shall preserve dimension consistency |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-005 | not-applicable | extracted-requirement | Merge process shall detect conflicting definitions |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-006 | not-applicable | extracted-requirement | Merge process shall reject incompatible duplicate definitions |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-007 | not-applicable | extracted-requirement | Merge process shall generate a merged FDD representation |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-008 | not-applicable | extracted-requirement | Merge process shall support inclusion of the standard MIM |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-MIM-D-001 | not-applicable | extracted-requirement | Standard MIM content shall be available through the active catalog and MOM request report paths |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-001 | not-applicable | extracted-requirement | Parser shall accept OMT XML interchange documents rooted at objectModel |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-002 | not-applicable | extracted-requirement | Resolver shall normalize XML module designators into backend-consumable URLs or file URIs |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-003 | not-applicable | extracted-requirement | MIM XML module payloads shall remain available for MOM request and report paths in the active implementation subset |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-MIM-001 | not-applicable | extracted-requirement | The standard MIM shall load as part of the effective federation model and expose its MOM/MIM behavior through the normal request and report paths |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-002 | not-applicable | extracted-requirement | OMT XML schema validation shall reject XML documents that do not conform to the normative OMT schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-E-001 | not-applicable | extracted-requirement | Schema-level XML conformance shall be validated against the standard schema when full schema validation is implemented |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-001 | not-applicable | extracted-requirement | OMT XML interchange shall validate namespaces, reject schema-invalid documents, preserve schema-valid serialization, and preserve semantic round-trip fidelity |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-001 | not-applicable | extracted-requirement | OMT XML documents shall conform to the published XML schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-002 | not-applicable | extracted-requirement | Parser shall validate XML namespace usage |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-003 | not-applicable | extracted-requirement | Parser shall reject schema-invalid XML documents |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-004 | not-applicable | extracted-requirement | Serializer shall emit schema-valid XML |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-005 | not-applicable | extracted-requirement | Parse to serialize to parse shall preserve semantic equivalence |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-E-001 | not-applicable | extracted-requirement | Schema-level XML conformance shall be validated against the standard schema when full schema validation is implemented |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-F-001 | not-applicable | extracted-requirement | Standard SOM example artifacts shall be maintained as parser regression fixtures |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-G-001 | not-applicable | extracted-requirement | Standard FOM example artifacts shall be maintained as parser regression fixtures |
