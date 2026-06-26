# portico-jpype Requirement Disposition

This audit projects the shared HLA 2010 requirements matrix onto `portico-jpype` so every row has an explicit generated `portico-jpype` disposition.

This profile currently inherits the Portico family-level requirement disposition because the JPype and Py4J routes are install-dependent Java adapter profiles over the same Portico runtime family and no profile-specific requirement evidence is generated yet.

## Summary

| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |
|---|---:|---:|---:|---:|---:|---:|---:|
| IEEE 1516-2010 unknown | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| IEEE 1516-2010 §12 | 21 | 0 | 0 | 0 | 0 | 21 | 0 |
| IEEE 1516.1-2010 (2010 edition) §10 | 86 | 0 | 0 | 0 | 0 | 2 | 84 |
| IEEE 1516.1-2010 (2010 edition) §11 | 37 | 0 | 0 | 0 | 0 | 2 | 35 |
| IEEE 1516.1-2010 (2010 edition) §12 | 10 | 0 | 0 | 0 | 0 | 1 | 9 |
| IEEE 1516.1-2010 (2010 edition) §4 | 281 | 0 | 0 | 0 | 0 | 2 | 279 |
| IEEE 1516.1-2010 (2010 edition) §5 | 53 | 0 | 0 | 0 | 0 | 2 | 51 |
| IEEE 1516.1-2010 (2010 edition) §6 | 121 | 0 | 0 | 0 | 0 | 2 | 119 |
| IEEE 1516.1-2010 (2010 edition) §7 | 39 | 0 | 0 | 0 | 0 | 2 | 37 |
| IEEE 1516.1-2010 (2010 edition) §8 | 61 | 0 | 0 | 0 | 0 | 2 | 59 |
| IEEE 1516.1-2010 (2010 edition) §9 | 31 | 0 | 0 | 0 | 0 | 2 | 29 |
| IEEE 1516.2-2010 (2010 edition) unknown | 18 | 0 | 0 | 0 | 0 | 2 | 16 |
| IEEE 1516.2-2010 (2010 edition) §4 | 112 | 0 | 0 | 0 | 0 | 15 | 97 |
| IEEE 1516.2-2010 (2010 edition) §5 | 2 | 0 | 0 | 0 | 0 | 1 | 1 |
| IEEE 1516.2-2010 (2010 edition) §6 | 2 | 0 | 0 | 0 | 0 | 1 | 1 |
| IEEE 1516.2-2010 (2010 edition) §7 | 15 | 0 | 0 | 0 | 0 | 1 | 14 |
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
| IEEE 1516-2010 | unknown | HLA1516-FW-001 | not-applicable | extracted-requirement | The repo shall treat IEEE 1516-2010 as the top-level framework and keep federate behavior |
| IEEE 1516-2010 | unknown | HLA1516-OBJ-001 | not-applicable | extracted-requirement | The repo shall distinguish object-model concepts from programming-language objects and map them to the 1516.1 object services and 1516.2 OMT structure |
| IEEE 1516-2010 | unknown | HLA1516-TIME-001 | not-applicable | extracted-requirement | The repo shall map time concepts to 1516.1 time services and grant/order semantics, including logical time and ordering relationships |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_10-resignFederationExecution | classification-required | service-requirement | Resign Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_11-registerFederationSynchronizationPoint | classification-required | service-requirement | Register Federation Synchronization Point service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_12-synchronizationPointRegistrationFailed | classification-required | service-requirement | Confirm Synchronization Point Registration service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded | classification-required | service-requirement | Confirm Synchronization Point Registration service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_13-announceSynchronizationPoint | classification-required | service-requirement | Announce Synchronization Point service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_14-synchronizationPointAchieved | classification-required | service-requirement | Synchronization Point Achieved service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_15-federationSynchronized | classification-required | service-requirement | Federation Synchronized service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_16-requestFederationSave | classification-required | service-requirement | Request Federation Save service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_17-initiateFederateSave | classification-required | service-requirement | Initiate Federate Save service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_18-federateSaveBegun | classification-required | service-requirement | Federate Save Begun service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_19-federateSaveComplete | classification-required | service-requirement | Federate Save Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_19-federateSaveNotComplete | classification-required | service-requirement | Federate Save Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_2-connect | classification-required | service-requirement | Connect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_20-federationNotSaved | classification-required | service-requirement | Federation Saved service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_20-federationSaved | classification-required | service-requirement | Federation Saved service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_21-abortFederationSave | classification-required | service-requirement | Abort Federation Save service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_22-queryFederationSaveStatus | classification-required | service-requirement | Query Federation Save Status service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_23-federationSaveStatusResponse | classification-required | service-requirement | Federation Save Status Response service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_24-requestFederationRestore | classification-required | service-requirement | Request Federation Restore service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_25-requestFederationRestoreFailed | classification-required | service-requirement | Confirm Federation Restoration Request service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_25-requestFederationRestoreSucceeded | classification-required | service-requirement | Confirm Federation Restoration Request service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_26-federationRestoreBegun | classification-required | service-requirement | Federation Restore Begun service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_27-initiateFederateRestore | classification-required | service-requirement | Initiate Federate Restore service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_28-federateRestoreComplete | classification-required | service-requirement | Federate Restore Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_28-federateRestoreNotComplete | classification-required | service-requirement | Federate Restore Complete service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_29-federationNotRestored | classification-required | service-requirement | Federation Restored service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_29-federationRestored | classification-required | service-requirement | Federation Restored service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_3-disconnect | classification-required | service-requirement | Disconnect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_30-abortFederationRestore | classification-required | service-requirement | Abort Federation Restore service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_31-queryFederationRestoreStatus | classification-required | service-requirement | Query Federation Restore Status service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_32-federationRestoreStatusResponse | classification-required | service-requirement | Federation Restore Status Response service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_4-connectionLost | classification-required | service-requirement | Connection Lost service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_5-createFederationExecution | classification-required | service-requirement | Create Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_5-createFederationExecutionWithMIM | classification-required | service-requirement | Create Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_6-destroyFederationExecution | classification-required | service-requirement | Destroy Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_7-listFederationExecutions | classification-required | service-requirement | List Federation Executions service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-FED-FM-4_8-reportFederationExecutions | classification-required | service-requirement | Report Federation Executions service |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_9-joinFederationExecution | classification-required | service-requirement | Join Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | AREA-1516.1-4 | not-applicable | section-area | Federation management |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-001 | not-applicable | curated-seed | The RTI shall implement federation-management services for create, join, resign, destroy, save, restore, synchronization, and related lifecycle behavior |
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
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-CB-001 | classification-required | extracted-requirement | After successful resignation, the resigned federate shall no longer receive federation-participation callbacks as a joined member. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-EFF-001 | classification-required | extracted-requirement | Successful Resign Federation Execution shall remove the federate from federation membership, remove or divest owned objects as directed by the resign action, remove synchronization-point participation, refresh time advancement processing, and clear local publication and subscription state. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-EXC-001 | classification-required | extracted-requirement | Resign Federation Execution shall distinguish not-connected, not-joined, invalid-resign-action, owns-attributes, and ownership-acquisition-pending failures. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-MOM-001 | classification-required | extracted-requirement | Successful Resign Federation Execution shall remove the resigned federate's MOM federate object and refresh MOM federation state for the remaining federation members. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-PRE-001 | classification-required | extracted-requirement | Resign Federation Execution shall require a connected ambassador that is currently joined and shall validate ownership and pending-acquisition conditions against the selected resign action. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Resign Federation Execution service. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.10-TEST-001 | classification-required | extracted-requirement | Resign Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-001 | classification-required | extracted-requirement | RTI shall provide Register Federation Synchronization Point |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-CB-001 | classification-required | extracted-requirement | Register Federation Synchronization Point shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-EFF-001 | classification-required | extracted-requirement | Successful Register Federation Synchronization Point processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-EXC-001 | classification-required | extracted-requirement | Register Federation Synchronization Point shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-MOM-001 | classification-required | extracted-requirement | Register Federation Synchronization Point effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-PRE-001 | classification-required | extracted-requirement | Register Federation Synchronization Point shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.11. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Register Federation Synchronization Point. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.11-TEST-001 | classification-required | extracted-requirement | Register Federation Synchronization Point shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-001 | classification-required | extracted-requirement | RTI shall confirm federation synchronization point registration success or failure |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-CB-001 | classification-required | extracted-requirement | The Synchronization Point Registration callbacks callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-EFF-001 | classification-required | extracted-requirement | The Synchronization Point Registration callbacks callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-EXC-001 | classification-required | extracted-requirement | The triggering path for Synchronization Point Registration callbacks shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-MOM-001 | classification-required | extracted-requirement | Synchronization Point Registration callbacks effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-PRE-001 | classification-required | extracted-requirement | The Synchronization Point Registration callbacks requirement shall apply only when the synchronization or save/restore preconditions for clause 4.12 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the federation synchronization point registration success or failure. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.12-TEST-001 | classification-required | extracted-requirement | Synchronization Point Registration callbacks shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-001 | classification-required | extracted-requirement | RTI shall announce synchronization points to the appropriate federates |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-CB-001 | classification-required | extracted-requirement | The Announce Synchronization Point callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-EFF-001 | classification-required | extracted-requirement | The Announce Synchronization Point callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-EXC-001 | classification-required | extracted-requirement | The triggering path for Announce Synchronization Point shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-MOM-001 | classification-required | extracted-requirement | Announce Synchronization Point effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-PRE-001 | classification-required | extracted-requirement | The Announce Synchronization Point requirement shall apply only when the synchronization or save/restore preconditions for clause 4.13 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-SIG-001 | classification-required | extracted-requirement | RTI shall announce synchronization points to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.13-TEST-001 | classification-required | extracted-requirement | Announce Synchronization Point shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-001 | classification-required | extracted-requirement | RTI shall provide Synchronization Point Achieved |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-CB-001 | classification-required | extracted-requirement | Synchronization Point Achieved shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-EFF-001 | classification-required | extracted-requirement | Successful Synchronization Point Achieved processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-EXC-001 | classification-required | extracted-requirement | Synchronization Point Achieved shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-MOM-001 | classification-required | extracted-requirement | Synchronization Point Achieved effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-PRE-001 | classification-required | extracted-requirement | Synchronization Point Achieved shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.14. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Synchronization Point Achieved. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.14-TEST-001 | classification-required | extracted-requirement | Synchronization Point Achieved shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-001 | classification-required | extracted-requirement | RTI shall notify federates when a synchronization point is achieved federation wide |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-002 | classification-required | extracted-requirement | RTI shall not invoke federationSynchronized until all required federates for an open whole-federation synchronization point have achieved the point |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-CB-001 | classification-required | extracted-requirement | The Federation Synchronized callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-EFF-001 | classification-required | extracted-requirement | The Federation Synchronized callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-EXC-001 | classification-required | extracted-requirement | The triggering path for Federation Synchronized shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-MOM-001 | classification-required | extracted-requirement | Federation Synchronized effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-PRE-001 | classification-required | extracted-requirement | The Federation Synchronized requirement shall apply only when the synchronization or save/restore preconditions for clause 4.15 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the federates when a synchronization point is achieved federation wide. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.15-TEST-001 | classification-required | extracted-requirement | Federation Synchronized shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-001 | classification-required | extracted-requirement | RTI shall provide Request Federation Save |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-CB-001 | classification-required | extracted-requirement | Request Federation Save shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-EFF-001 | classification-required | extracted-requirement | Successful Request Federation Save processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-EXC-001 | classification-required | extracted-requirement | Request Federation Save shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-MOM-001 | classification-required | extracted-requirement | Request Federation Save effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-PRE-001 | classification-required | extracted-requirement | Request Federation Save shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.16. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Request Federation Save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.16-TEST-001 | classification-required | extracted-requirement | Request Federation Save shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-001 | classification-required | extracted-requirement | RTI shall notify each participating federate to initiate save |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-CB-001 | classification-required | extracted-requirement | The Initiate Federate Save callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-EFF-001 | classification-required | extracted-requirement | The Initiate Federate Save callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-EXC-001 | classification-required | extracted-requirement | The triggering path for Initiate Federate Save shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-MOM-001 | classification-required | extracted-requirement | Initiate Federate Save effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-PRE-001 | classification-required | extracted-requirement | The Initiate Federate Save requirement shall apply only when the synchronization or save/restore preconditions for clause 4.17 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the each participating federate to initiate save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.17-TEST-001 | classification-required | extracted-requirement | Initiate Federate Save shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-001 | classification-required | extracted-requirement | RTI shall provide Federate Save Begun |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-CB-001 | classification-required | extracted-requirement | Federate Save Begun shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-EFF-001 | classification-required | extracted-requirement | Successful Federate Save Begun processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-EXC-001 | classification-required | extracted-requirement | Federate Save Begun shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-MOM-001 | classification-required | extracted-requirement | Federate Save Begun effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-PRE-001 | classification-required | extracted-requirement | Federate Save Begun shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.18. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Federate Save Begun. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.18-TEST-001 | classification-required | extracted-requirement | Federate Save Begun shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-001 | classification-required | extracted-requirement | RTI shall provide Federate Save Complete and Federate Save Not Complete |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-CB-001 | classification-required | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-EFF-001 | classification-required | extracted-requirement | Successful Federate Save Complete and Federate Save Not Complete processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-EXC-001 | classification-required | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-MOM-001 | classification-required | extracted-requirement | Federate Save Complete and Federate Save Not Complete effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-PRE-001 | classification-required | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.19. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Federate Save Complete and Federate Save Not Complete. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.19-TEST-001 | classification-required | extracted-requirement | Federate Save Complete and Federate Save Not Complete shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-001 | classification-required | extracted-requirement | RTI shall provide a Connect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-CB-001 | classification-required | extracted-requirement | Connect shall establish the callback-delivery model that governs subsequent RTI callback behavior for the connected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-EFF-001 | classification-required | extracted-requirement | Successful Connect shall bind the ambassador, persist the selected callback model, persist the optional local settings designator, and mark the ambassador connected. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-EXC-001 | classification-required | extracted-requirement | Connect shall report an AlreadyConnected error for a repeated connection attempt on the same ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-MOM-001 | classification-required | extracted-requirement | Connection state relevant to later federation participation should be representable through MOM-visible federate state once the connected ambassador joins a federation. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-PRE-001 | classification-required | extracted-requirement | Connect shall be rejected when the RTI ambassador is already connected. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Connect service with federate ambassador, callback model, and optional local settings designator inputs. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.2-TEST-001 | classification-required | extracted-requirement | Connect shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-001 | classification-required | extracted-requirement | RTI shall report Federation Saved or Federation Not Saved according to save outcome |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-CB-001 | classification-required | extracted-requirement | The Federation Saved and Federation Not Saved callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-EFF-001 | classification-required | extracted-requirement | The Federation Saved and Federation Not Saved callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-EXC-001 | classification-required | extracted-requirement | The triggering path for Federation Saved and Federation Not Saved shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-MOM-001 | classification-required | extracted-requirement | Federation Saved and Federation Not Saved effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-PRE-001 | classification-required | extracted-requirement | The Federation Saved and Federation Not Saved requirement shall apply only when the synchronization or save/restore preconditions for clause 4.20 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the Federation Saved or Federation Not Saved according to save outcome. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.20-TEST-001 | classification-required | extracted-requirement | Federation Saved and Federation Not Saved shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-001 | classification-required | extracted-requirement | RTI shall provide Abort Federation Save |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-CB-001 | classification-required | extracted-requirement | Abort Federation Save shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-EFF-001 | classification-required | extracted-requirement | Successful Abort Federation Save processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-EXC-001 | classification-required | extracted-requirement | Abort Federation Save shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-MOM-001 | classification-required | extracted-requirement | Abort Federation Save effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-PRE-001 | classification-required | extracted-requirement | Abort Federation Save shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.21. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Abort Federation Save. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.21-TEST-001 | classification-required | extracted-requirement | Abort Federation Save shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-001 | classification-required | extracted-requirement | RTI shall provide Query Federation Save Status |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-CB-001 | classification-required | extracted-requirement | Query Federation Save Status shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-EFF-001 | classification-required | extracted-requirement | Successful Query Federation Save Status processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-EXC-001 | classification-required | extracted-requirement | Query Federation Save Status shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-MOM-001 | classification-required | extracted-requirement | Query Federation Save Status effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-PRE-001 | classification-required | extracted-requirement | Query Federation Save Status shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.22. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Query Federation Save Status. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.22-TEST-001 | classification-required | extracted-requirement | Query Federation Save Status shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-001 | classification-required | extracted-requirement | RTI shall report federation save status through Federation Save Status Response |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-CB-001 | classification-required | extracted-requirement | The Federation Save Status Response callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-EFF-001 | classification-required | extracted-requirement | The Federation Save Status Response callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-EXC-001 | classification-required | extracted-requirement | The triggering path for Federation Save Status Response shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-MOM-001 | classification-required | extracted-requirement | Federation Save Status Response effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-PRE-001 | classification-required | extracted-requirement | The Federation Save Status Response requirement shall apply only when the synchronization or save/restore preconditions for clause 4.23 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the federation save status through Federation Save Status Response. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.23-TEST-001 | classification-required | extracted-requirement | Federation Save Status Response shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-001 | classification-required | extracted-requirement | RTI shall provide Request Federation Restore |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-CB-001 | classification-required | extracted-requirement | Request Federation Restore shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-EFF-001 | classification-required | extracted-requirement | Successful Request Federation Restore processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-EXC-001 | classification-required | extracted-requirement | Request Federation Restore shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-MOM-001 | classification-required | extracted-requirement | Request Federation Restore effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-PRE-001 | classification-required | extracted-requirement | Request Federation Restore shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.24. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Request Federation Restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.24-TEST-001 | classification-required | extracted-requirement | Request Federation Restore shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-001 | classification-required | extracted-requirement | RTI shall confirm federation restoration request success or failure |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-CB-001 | classification-required | extracted-requirement | The Request Federation Restore confirmation callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-EFF-001 | classification-required | extracted-requirement | The Request Federation Restore confirmation callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-EXC-001 | classification-required | extracted-requirement | The triggering path for Request Federation Restore confirmation shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-MOM-001 | classification-required | extracted-requirement | Request Federation Restore confirmation effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-PRE-001 | classification-required | extracted-requirement | The Request Federation Restore confirmation requirement shall apply only when the synchronization or save/restore preconditions for clause 4.25 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the federation restoration request success or failure. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.25-TEST-001 | classification-required | extracted-requirement | Request Federation Restore confirmation shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-001 | classification-required | extracted-requirement | RTI shall report when federation restore has begun |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-CB-001 | classification-required | extracted-requirement | The Federation Restore Begun callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-EFF-001 | classification-required | extracted-requirement | The Federation Restore Begun callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-EXC-001 | classification-required | extracted-requirement | The triggering path for Federation Restore Begun shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-MOM-001 | classification-required | extracted-requirement | Federation Restore Begun effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-PRE-001 | classification-required | extracted-requirement | The Federation Restore Begun requirement shall apply only when the synchronization or save/restore preconditions for clause 4.26 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the when federation restore has begun. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.26-TEST-001 | classification-required | extracted-requirement | Federation Restore Begun shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-001 | classification-required | extracted-requirement | RTI shall notify each participating federate to initiate restore |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-CB-001 | classification-required | extracted-requirement | The Initiate Federate Restore callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-EFF-001 | classification-required | extracted-requirement | The Initiate Federate Restore callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-EXC-001 | classification-required | extracted-requirement | The triggering path for Initiate Federate Restore shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-MOM-001 | classification-required | extracted-requirement | Initiate Federate Restore effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-PRE-001 | classification-required | extracted-requirement | The Initiate Federate Restore requirement shall apply only when the synchronization or save/restore preconditions for clause 4.27 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the each participating federate to initiate restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.27-TEST-001 | classification-required | extracted-requirement | Initiate Federate Restore shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-001 | classification-required | extracted-requirement | RTI shall provide Federate Restore Complete and Federate Restore Not Complete |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-CB-001 | classification-required | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-EFF-001 | classification-required | extracted-requirement | Successful Federate Restore Complete and Federate Restore Not Complete processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-EXC-001 | classification-required | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-MOM-001 | classification-required | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-PRE-001 | classification-required | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.28. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Federate Restore Complete and Federate Restore Not Complete. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.28-TEST-001 | classification-required | extracted-requirement | Federate Restore Complete and Federate Restore Not Complete shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-001 | classification-required | extracted-requirement | RTI shall report Federation Restored or Federation Not Restored according to restore outcome |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-CB-001 | classification-required | extracted-requirement | The Federation Restored and Federation Not Restored callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-EFF-001 | classification-required | extracted-requirement | The Federation Restored and Federation Not Restored callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-EXC-001 | classification-required | extracted-requirement | The triggering path for Federation Restored and Federation Not Restored shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-MOM-001 | classification-required | extracted-requirement | Federation Restored and Federation Not Restored effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-PRE-001 | classification-required | extracted-requirement | The Federation Restored and Federation Not Restored requirement shall apply only when the synchronization or save/restore preconditions for clause 4.29 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the Federation Restored or Federation Not Restored according to restore outcome. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.29-TEST-001 | classification-required | extracted-requirement | Federation Restored and Federation Not Restored shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-001 | classification-required | extracted-requirement | RTI shall provide a Disconnect service |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-CB-001 | classification-required | extracted-requirement | After Disconnect, the RTI shall cease callback delivery to the disconnected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-EFF-001 | classification-required | extracted-requirement | Successful Disconnect shall clear connected state, clear the bound ambassador reference, and clear queued callbacks for the disconnected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-EXC-001 | classification-required | extracted-requirement | Disconnect shall report FederateIsExecutionMember when a joined federate attempts to disconnect before resigning. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-MOM-001 | classification-required | extracted-requirement | Disconnect should leave no active MOM-visible federate session associated with the disconnected ambassador. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-PRE-001 | classification-required | extracted-requirement | Disconnect shall require a connected ambassador that is no longer a federation execution member. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Disconnect service. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.3-TEST-001 | classification-required | extracted-requirement | Disconnect shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-001 | classification-required | extracted-requirement | RTI shall provide Abort Federation Restore |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-CB-001 | classification-required | extracted-requirement | Abort Federation Restore shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-EFF-001 | classification-required | extracted-requirement | Successful Abort Federation Restore processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-EXC-001 | classification-required | extracted-requirement | Abort Federation Restore shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-MOM-001 | classification-required | extracted-requirement | Abort Federation Restore effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-PRE-001 | classification-required | extracted-requirement | Abort Federation Restore shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.30. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Abort Federation Restore. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.30-TEST-001 | classification-required | extracted-requirement | Abort Federation Restore shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-001 | classification-required | extracted-requirement | RTI shall provide Query Federation Restore Status |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-CB-001 | classification-required | extracted-requirement | Query Federation Restore Status shall trigger the clause-defined success, failure, or status callbacks to the appropriate federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-EFF-001 | classification-required | extracted-requirement | Successful Query Federation Restore Status processing shall update federation synchronization or save/restore state consistently for the participating federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-EXC-001 | classification-required | extracted-requirement | Query Federation Restore Status shall distinguish the clause-defined failure modes instead of collapsing them into generic RTIinternalError behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-MOM-001 | classification-required | extracted-requirement | Query Federation Restore Status effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-PRE-001 | classification-required | extracted-requirement | Query Federation Restore Status shall require the caller to satisfy the connected, joined, and in-progress state guards applicable to clause 4.31. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Query Federation Restore Status. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.31-TEST-001 | classification-required | extracted-requirement | Query Federation Restore Status shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-001 | classification-required | extracted-requirement | RTI shall report federation restore status through Federation Restore Status Response |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-CB-001 | classification-required | extracted-requirement | The Federation Restore Status Response callback shall be delivered to the appropriate federates with the clause-defined payload and timing semantics. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-EFF-001 | classification-required | extracted-requirement | The Federation Restore Status Response callback shall expose the resulting federation synchronization or save/restore state transition to the affected federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-EXC-001 | classification-required | extracted-requirement | The triggering path for Federation Restore Status Response shall distinguish the clause-defined success and failure categories visible through callback payloads instead of collapsing them into generic behavior. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-MOM-001 | classification-required | extracted-requirement | Federation Restore Status Response effects should remain visible through observer-facing federation status, reporting, or MOM-adjacent state where the implementation exposes such information. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-PRE-001 | classification-required | extracted-requirement | The Federation Restore Status Response requirement shall apply only when the synchronization or save/restore preconditions for clause 4.32 are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-SIG-001 | classification-required | extracted-requirement | RTI shall deliver the federation restore status through Federation Restore Status Response. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.32-TEST-001 | classification-required | extracted-requirement | Federation Restore Status Response shall be covered by direct service or callback tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-001 | classification-required | extracted-requirement | RTI shall provide Create Federation Execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-CB-001 | classification-required | extracted-requirement | Create Federation Execution shall make the created federation observable to subsequent callback-based reporting services such as Report Federation Executions. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-EFF-001 | classification-required | extracted-requirement | Successful Create Federation Execution shall install the federation, resolve and merge the supplied FOM modules, supply the standard MIM by default when needed, and choose a logical time factory compatible with the merged model. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-EXC-001 | classification-required | extracted-requirement | Create Federation Execution shall distinguish duplicate-name, FOM-open, FOM-read, MIM-open, MIM-read, invalid-time-factory, inconsistent-FOM, and invalid-standard-MIM-designator failures. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-MOM-001 | classification-required | extracted-requirement | Successful Create Federation Execution shall expose the standard MIM-backed federation object model so MOM federation classes and interactions are available once a federate joins. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-PRE-001 | classification-required | extracted-requirement | Create Federation Execution shall require a connected ambassador and shall reject duplicate federation execution names. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Create Federation Execution service, including the explicit-MIM overload shape used by the current API surface. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-TEST-001 | classification-required | extracted-requirement | Create Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-001 | classification-required | extracted-requirement | RTI shall provide Destroy Federation Execution |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-CB-001 | classification-required | extracted-requirement | After successful destruction, callback-based federation listing shall no longer report the destroyed federation execution. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-EFF-001 | classification-required | extracted-requirement | Successful Destroy Federation Execution shall remove the target federation execution from the RTI federation catalog. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-EXC-001 | classification-required | extracted-requirement | Destroy Federation Execution shall report FederatesCurrentlyJoined when members remain and FederationExecutionDoesNotExist when the target federation is unknown. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-MOM-001 | classification-required | extracted-requirement | Successful destruction should remove the destroyed federation from subsequent MOM-visible federation state and reports. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-PRE-001 | classification-required | extracted-requirement | Destroy Federation Execution shall require a connected ambassador and a target federation execution that has no currently joined federates. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-SIG-001 | classification-required | extracted-requirement | RTI shall provide the Destroy Federation Execution service. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.6-TEST-001 | classification-required | extracted-requirement | Destroy Federation Execution shall be covered by direct service tests, with hosted gRPC and REST replay recorded separately as backend-resolution evidence where available. |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-001 | classification-required | extracted-requirement | RTI shall provide Join Federation Execution |
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
| IEEE 1516.1-2010 (2010 edition) | 5 | AREA-1516.1-5 | not-applicable | section-area | Declaration management |
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
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.6-001 | classification-required | extracted-requirement | RTI shall support subscribing with update rate reduction where applicable. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.6-002 | classification-required | extracted-requirement | RTI shall apply explicit and FOM-declared update-rate designators across direct, inherited, and region-based object-class subscriptions within the currently implemented logical-time subset. |
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
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_10-updateAttributeValues | classification-required | service-requirement | Update Attribute Values service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_11-reflectAttributeValues | classification-required | service-requirement | Reflect Attribute Values service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_12-sendInteraction | classification-required | service-requirement | Send Interaction service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_13-receiveInteraction | classification-required | service-requirement | Receive Interaction service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_14-deleteObjectInstance | classification-required | service-requirement | Delete Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_15-removeObjectInstance | classification-required | service-requirement | Remove Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_16-localDeleteObjectInstance | classification-required | service-requirement | Local Delete Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_17-attributesInScope | classification-required | service-requirement | Attributes In Scope service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_18-attributesOutOfScope | classification-required | service-requirement | Attributes Out Of Scope service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_19-requestAttributeValueUpdate | classification-required | service-requirement | Request Attribute Value Update service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_2-reserveObjectInstanceName | classification-required | service-requirement | Reserve Object Instance Name service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_20-provideAttributeValueUpdate | classification-required | service-requirement | Provide Attribute Value Update service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_21-turnUpdatesOnForObjectInstance | classification-required | service-requirement | Turn Updates On For Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_22-turnUpdatesOffForObjectInstance | classification-required | service-requirement | Turn Updates Off For Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_23-requestAttributeTransportationTypeChange | classification-required | service-requirement | Request Attribute Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_24-confirmAttributeTransportationTypeChange | classification-required | service-requirement | Confirm Attribute Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_25-queryAttributeTransportationType | classification-required | service-requirement | Query Attribute Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_26-reportAttributeTransportationType | classification-required | service-requirement | Report Attribute Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_27-requestInteractionTransportationTypeChange | classification-required | service-requirement | Request Interaction Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_28-confirmInteractionTransportationTypeChange | classification-required | service-requirement | Confirm Interaction Transportation Type Change service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_29-queryInteractionTransportationType | classification-required | service-requirement | Query Interaction Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_3-objectInstanceNameReservationFailed | classification-required | service-requirement | Object Instance Name Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_3-objectInstanceNameReservationSucceeded | classification-required | service-requirement | Object Instance Name Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_30-reportInteractionTransportationType | classification-required | service-requirement | Report Interaction Transportation Type service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_4-releaseObjectInstanceName | classification-required | service-requirement | Release Object Instance Name service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_5-reserveMultipleObjectInstanceName | classification-required | service-requirement | Reserve Multiple Object Instance Names service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_6-multipleObjectInstanceNameReservationFailed | classification-required | service-requirement | Multiple Object Instance Names Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_6-multipleObjectInstanceNameReservationSucceeded | classification-required | service-requirement | Multiple Object Instance Names Reserved service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_7-releaseMultipleObjectInstanceName | classification-required | service-requirement | Release Multiple Object Instance Names service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-RTI-OM-6_8-registerObjectInstance | classification-required | service-requirement | Register Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-discoverObjectInstance | classification-required | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-getProducingFederate | classification-required | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-getSentRegions | classification-required | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-hasProducingFederate | classification-required | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | REQ-FED-OM-6_9-hasSentRegions | classification-required | service-requirement | Discover Object Instance service |
| IEEE 1516.1-2010 (2010 edition) | 6 | AREA-1516.1-6 | not-applicable | section-area | Object management |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-001 | not-applicable | extracted-requirement | The RTI shall implement object-management services for registration, update, delete, discovery, and interaction delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1-001 | classification-required | extracted-requirement | RTI shall support registration, modification, and deletion of object instances. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1-002 | classification-required | extracted-requirement | RTI shall support sending and receiving interactions. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-001 | classification-required | extracted-requirement | RTI shall discover object instances at subscribed federates when discovery conditions are satisfied. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-002 | classification-required | extracted-requirement | RTI shall determine a candidate discovery class from the registered class or closest subscribed superclass. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-003 | classification-required | extracted-requirement | Once discovered, an object instance’s discovered class shall not change. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.1-004 | classification-required | extracted-requirement | A registered or discovered object instance shall become known to the joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.10-001 | classification-required | extracted-requirement | RTI shall use transportation types for object updates and interactions as defined by the FDD and service arguments. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.10-002 | classification-required | extracted-requirement | RTI shall support explicit reliable transportation type selection, query reporting, and restore persistence for object updates and interactions in the currently supported transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.10-003 | classification-required | extracted-requirement | RTI shall support distinct best-effort versus reliable delivery semantics for object updates and interactions when explicit transportation selections differ. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.10-004 | classification-required | extracted-requirement | RTI shall honor FOM-declared reliable and best-effort transportation defaults for object updates and interactions in the currently supported transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.11-001 | classification-required | extracted-requirement | RTI may combine, package, or passelize messages without changing externally visible semantics. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.11-002 | classification-required | extracted-requirement | RTI shall preserve externally visible reflect and interaction callback semantics for the currently implemented direct unbatched delivery subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.12-001 | classification-required | extracted-requirement | RTI shall honor update-rate reduction when reflecting attribute updates. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.12-002 | classification-required | extracted-requirement | RTI shall throttle timed reflected attribute delivery according to explicit and FOM-declared update-rate designators while preserving receive-order delivery that has no logical-time basis. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.2-001 | classification-required | extracted-requirement | RTI shall determine whether an instance attribute is in scope for each joined federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.3-001 | classification-required | extracted-requirement | RTI shall reflect attribute updates only when attributes are in scope and subscribed. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.4-001 | classification-required | extracted-requirement | RTI shall not reflect out-of-scope attribute updates except where required by service semantics. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.5-001 | classification-required | extracted-requirement | RTI shall determine attribute relevance from publication, subscription, ownership, and scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.6-001 | classification-required | extracted-requirement | RTI shall handle orphan object instances according to ownership and discovery rules. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.7-001 | classification-required | extracted-requirement | RTI shall deliver interactions to joined federates subscribed to the relevant interaction class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.10-001 | classification-required | extracted-requirement | RTI shall provide Update Attribute Values. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.10-002 | classification-required | extracted-requirement | A federate shall update only attributes it owns and is permitted to publish. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.10-003 | classification-required | extracted-requirement | RTI shall route attribute updates to joined federates with relevant subscriptions and scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.10-004 | classification-required | extracted-requirement | RTI shall support RO and TSO attribute updates according to time-management rules. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.10-005 | classification-required | extracted-requirement | RTI shall deliver reflected attribute updates with transportation metadata that matches the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.11-001 | classification-required | extracted-requirement | RTI shall invoke Reflect Attribute Values to deliver attribute updates. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.11-002 | classification-required | extracted-requirement | Reflected attributes shall correspond to attributes available at the object instance’s known class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.12-001 | classification-required | extracted-requirement | RTI shall provide Send Interaction. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.12-002 | classification-required | extracted-requirement | A federate shall send only interaction classes it has published. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.12-003 | classification-required | extracted-requirement | Sent interaction parameters shall be available parameters of the interaction class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.12-004 | classification-required | extracted-requirement | RTI shall support RO and TSO interactions according to time-management rules. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.12-005 | classification-required | extracted-requirement | RTI shall deliver received interactions with transportation metadata that matches the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.13-001 | classification-required | extracted-requirement | RTI shall invoke Receive Interaction for matching subscribed federates. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.14-001 | classification-required | extracted-requirement | RTI shall provide Delete Object Instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.14-002 | classification-required | extracted-requirement | Delete Object Instance shall remove an object instance from the federation execution according to ownership and time rules. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.15-001 | classification-required | extracted-requirement | RTI shall invoke Remove Object Instance at federates that know the deleted object instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.16-001 | classification-required | extracted-requirement | RTI shall provide Local Delete Object Instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.16-002 | classification-required | extracted-requirement | Local Delete Object Instance shall remove knowledge of the object instance only at the invoking federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.17-001 | classification-required | extracted-requirement | RTI shall invoke Attributes In Scope when subscribed attributes become in scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.18-001 | classification-required | extracted-requirement | RTI shall invoke Attributes Out Of Scope when subscribed attributes go out of scope. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.19-001 | classification-required | extracted-requirement | RTI shall provide Request Attribute Value Update. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.19-002 | classification-required | extracted-requirement | Request Attribute Value Update shall cause relevant owning federates to receive a request to provide current values. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.2-001 | classification-required | extracted-requirement | RTI shall provide Reserve Object Instance Name. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.21-001 | classification-required | extracted-requirement | RTI shall invoke Turn Updates On For Object Instance when subscribed demand makes a published object instance attribute set newly relevant to the owning federate. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.21-002 | classification-required | extracted-requirement | Turn Updates On For Object Instance shall carry the object instance handle, relevant attribute set, and applicable update rate designator when one is in effect. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.22-001 | classification-required | extracted-requirement | RTI shall invoke Turn Updates Off For Object Instance when subscribed demand no longer exists for a published object instance attribute set. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.23-001 | classification-required | extracted-requirement | RTI shall provide Request Attribute Transportation Type Change across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.23-002 | classification-required | extracted-requirement | RTI shall support Request Attribute Transportation Type Change for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.23-003 | classification-required | extracted-requirement | RTI shall persist selected attribute transportation overrides across restore in the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.24-001 | classification-required | extracted-requirement | RTI shall invoke Confirm Attribute Transportation Type Change across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.24-002 | classification-required | extracted-requirement | RTI shall invoke Confirm Attribute Transportation Type Change for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.24-003 | classification-required | extracted-requirement | RTI shall not emit Confirm Attribute Transportation Type Change when the corresponding change request is rejected for invalid state, handle, ownership, publication, or transport inputs. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.24-004 | classification-required | extracted-requirement | RTI shall route Confirm Attribute Transportation Type Change only to the federate that requested the change in the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.25-001 | classification-required | extracted-requirement | RTI shall provide Query Attribute Transportation Type across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.25-002 | classification-required | extracted-requirement | RTI shall report stored attribute transportation overrides for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.25-003 | classification-required | extracted-requirement | RTI shall report the default reliable attribute transportation type when no explicit override exists in the currently implemented transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.26-001 | classification-required | extracted-requirement | RTI shall invoke Report Attribute Transportation Type across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.26-002 | classification-required | extracted-requirement | RTI shall invoke Report Attribute Transportation Type for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.26-003 | classification-required | extracted-requirement | RTI shall not emit Report Attribute Transportation Type when the corresponding query is rejected for invalid state, object, or attribute inputs. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.26-004 | classification-required | extracted-requirement | RTI shall route Report Attribute Transportation Type only to the federate that issued the corresponding query in the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.27-001 | classification-required | extracted-requirement | RTI shall provide Request Interaction Transportation Type Change across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.27-002 | classification-required | extracted-requirement | RTI shall support Request Interaction Transportation Type Change for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.27-003 | classification-required | extracted-requirement | RTI shall persist selected interaction transportation overrides across restore in the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.28-001 | classification-required | extracted-requirement | RTI shall invoke Confirm Interaction Transportation Type Change across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.28-002 | classification-required | extracted-requirement | RTI shall invoke Confirm Interaction Transportation Type Change for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.28-003 | classification-required | extracted-requirement | RTI shall not emit Confirm Interaction Transportation Type Change when the corresponding change request is rejected for invalid state, class, publication, or transport inputs. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.28-004 | classification-required | extracted-requirement | RTI shall route Confirm Interaction Transportation Type Change only to the federate that requested the change in the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.29-001 | classification-required | extracted-requirement | RTI shall provide Query Interaction Transportation Type across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.29-002 | classification-required | extracted-requirement | RTI shall report stored interaction transportation overrides for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.29-003 | classification-required | extracted-requirement | RTI shall report the default reliable interaction transportation type when no explicit override exists in the currently implemented transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.3-001 | classification-required | extracted-requirement | RTI shall invoke Object Instance Name Reserved when a reservation succeeds. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.30-001 | classification-required | extracted-requirement | RTI shall invoke Report Interaction Transportation Type across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.30-002 | classification-required | extracted-requirement | RTI shall invoke Report Interaction Transportation Type for the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.30-003 | classification-required | extracted-requirement | RTI shall not emit Report Interaction Transportation Type when the corresponding query is rejected for invalid state or invalid interaction inputs. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.30-004 | classification-required | extracted-requirement | RTI shall route Report Interaction Transportation Type only to the federate that issued the corresponding query in the currently implemented reliable and best-effort transport subset. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.4-001 | classification-required | extracted-requirement | RTI shall provide Release Object Instance Name. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.5-001 | classification-required | extracted-requirement | RTI shall provide Reserve Multiple Object Instance Names. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.6-001 | classification-required | extracted-requirement | RTI shall invoke Multiple Object Instance Names Reserved when multiple-name reservation succeeds. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.7-001 | classification-required | extracted-requirement | RTI shall provide Release Multiple Object Instance Names. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-001 | classification-required | extracted-requirement | RTI shall provide Register Object Instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-002 | classification-required | extracted-requirement | Register Object Instance shall create an object instance of a published object class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-003 | classification-required | extracted-requirement | RTI shall assign a unique object instance handle to each registered object instance. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.8-004 | classification-required | extracted-requirement | RTI shall support registration with RTI-assigned or federate-supplied object instance names. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.9-001 | classification-required | extracted-requirement | RTI shall invoke Discover Object Instance at federates satisfying discovery conditions. |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_10-attributeOwnershipUnavailable | classification-required | service-requirement | Attribute Ownership Unavailable service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_11-requestAttributeOwnershipRelease | classification-required | service-requirement | Request Attribute Ownership Release service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_12-attributeOwnershipReleaseDenied | classification-required | service-requirement | Attribute Ownership Release Denied service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_13-attributeOwnershipDivestitureIfWanted | classification-required | service-requirement | Attribute Ownership Divestiture If Wanted service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture | classification-required | service-requirement | Cancel Negotiated Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition | classification-required | service-requirement | Cancel Attribute Ownership Acquisition service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation | classification-required | service-requirement | Confirm Attribute Ownership Acquisition Cancellation service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_17-queryAttributeOwnership | classification-required | service-requirement | Query Attribute Ownership service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_18-attributeIsNotOwned | classification-required | service-requirement | Inform Attribute Ownership service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_18-attributeIsOwnedByRTI | classification-required | service-requirement | Inform Attribute Ownership service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_18-informAttributeOwnership | classification-required | service-requirement | Inform Attribute Ownership service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_19-isAttributeOwnedByFederate | classification-required | service-requirement | Is Attribute Owned By Federate service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture | classification-required | service-requirement | Unconditional Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture | classification-required | service-requirement | Negotiated Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption | classification-required | service-requirement | Request Attribute Ownership Assumption service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_5-requestDivestitureConfirmation | classification-required | service-requirement | Request Divestiture Confirmation service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_6-confirmDivestiture | classification-required | service-requirement | Confirm Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_7-attributeOwnershipAcquisitionNotification | classification-required | service-requirement | Attribute Ownership Acquisition Notification service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_8-attributeOwnershipAcquisition | classification-required | service-requirement | Attribute Ownership Acquisition service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable | classification-required | service-requirement | Attribute Ownership Acquisition If Available service |
| IEEE 1516.1-2010 (2010 edition) | 7 | AREA-1516.1-7 | not-applicable | section-area | Ownership management |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-001 | not-applicable | extracted-requirement | The RTI shall implement ownership-management services for unconditional, negotiated, acquisition, divestiture, and release-request flows |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.1-001 | classification-required | extracted-requirement | RTI shall track ownership of object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.1-002 | classification-required | extracted-requirement | At most one federate may own a given attribute of a given object instance at a time |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.1-003 | classification-required | extracted-requirement | A federate shall update only attributes it owns |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.10-001 | classification-required | extracted-requirement | RTI shall support cancellation of ownership acquisition attempts |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.11-001 | classification-required | extracted-requirement | RTI shall report cancellation confirmation where required |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.12-001 | classification-required | extracted-requirement | RTI shall support ownership query for object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.13-001 | classification-required | extracted-requirement | RTI shall notify whether an attribute is owned unowned or owned by another federate |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.2-001 | classification-required | extracted-requirement | RTI shall provide unconditional attribute ownership divestiture |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.3-001 | classification-required | extracted-requirement | RTI shall provide negotiated attribute ownership divestiture |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.4-001 | classification-required | extracted-requirement | RTI shall notify federates when ownership divestiture is requested |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.5-001 | classification-required | extracted-requirement | RTI shall provide attribute ownership acquisition |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.6-001 | classification-required | extracted-requirement | RTI shall provide attribute ownership acquisition if available |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.7-001 | classification-required | extracted-requirement | RTI shall notify a federate when ownership acquisition succeeds |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.7-002 | classification-required | extracted-requirement | RTI shall not invoke attributeOwnershipAcquisitionNotification when the owning federate denies release and acquisition does not complete |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.8-001 | classification-required | extracted-requirement | RTI shall notify a federate when ownership acquisition fails |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.9-001 | classification-required | extracted-requirement | RTI shall allow a federate to release ownership in response to acquisition requests |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.9-002 | classification-required | extracted-requirement | RTI shall not invoke requestAttributeOwnershipRelease when acquisition-if-available cannot proceed immediately and ownership remains with the current owner |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_10-nextMessageRequest | classification-required | service-requirement | Next Message Request service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_11-nextMessageRequestAvailable | classification-required | service-requirement | Next Message Request Available service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_12-flushQueueRequest | classification-required | service-requirement | Flush Queue Request service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-FED-TM-8_13-timeAdvanceGrant | classification-required | service-requirement | Time Advance Grant service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_14-enableAsynchronousDelivery | classification-required | service-requirement | Enable Asynchronous Delivery service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_15-disableAsynchronousDelivery | classification-required | service-requirement | Disable Asynchronous Delivery service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_16-queryGALT | classification-required | service-requirement | Query GALT service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_17-queryLogicalTime | classification-required | service-requirement | Query Logical Time service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_18-queryLITS | classification-required | service-requirement | Query LITS service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_19-modifyLookahead | classification-required | service-requirement | Modify Lookahead service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_2-enableTimeRegulation | classification-required | service-requirement | Enable Time Regulation service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_20-queryLookahead | classification-required | service-requirement | Query Lookahead service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_21-retract | classification-required | service-requirement | Retract service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-FED-TM-8_22-requestRetraction | classification-required | service-requirement | Request Retraction service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_23-changeAttributeOrderType | classification-required | service-requirement | Change Attribute Order Type service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_24-changeInteractionOrderType | classification-required | service-requirement | Change Interaction Order Type service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-FED-TM-8_3-timeRegulationEnabled | classification-required | service-requirement | Time Regulation Enabled service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_4-disableTimeRegulation | classification-required | service-requirement | Disable Time Regulation service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_5-enableTimeConstrained | classification-required | service-requirement | Enable Time Constrained service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-FED-TM-8_6-timeConstrainedEnabled | classification-required | service-requirement | Time Constrained Enabled service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_7-disableTimeConstrained | classification-required | service-requirement | Disable Time Constrained service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_8-timeAdvanceRequest | classification-required | service-requirement | Time Advance Request service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_9-timeAdvanceRequestAvailable | classification-required | service-requirement | Time Advance Request Available service |
| IEEE 1516.1-2010 (2010 edition) | 8 | AREA-1516.1-8 | not-applicable | section-area | Time management |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-001 | not-applicable | extracted-requirement | The RTI shall implement time-management services for regulation, constrained behavior, query services, lookahead, order control, and grant delivery |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1-001 | classification-required | extracted-requirement | RTI shall represent modeled time as points on the HLA time axis |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1-002 | classification-required | extracted-requirement | RTI shall coordinate logical time advancement with object updates and interactions |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.1-001 | classification-required | extracted-requirement | RTI shall treat attribute updates interactions object deletes and DDM region messages as HLA messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-001 | classification-required | extracted-requirement | Each message shall be either timestamp order TSO or receive order RO |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-002 | classification-required | extracted-requirement | RTI shall determine sent message order type from preferred order type timestamp presence and federate time status |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-003 | classification-required | extracted-requirement | HLA1516.1-TM-8.1.2-003 |
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
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.10-001 | classification-required | extracted-requirement | RTI shall provide Next Message Request |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.12-001 | classification-required | extracted-requirement | RTI shall provide Flush Queue Request |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.16-001 | classification-required | extracted-requirement | RTI shall provide Query GALT |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.17-001 | classification-required | extracted-requirement | RTI shall provide Query Logical Time |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.18-001 | classification-required | extracted-requirement | RTI shall provide Query LITS |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.19-001 | classification-required | extracted-requirement | RTI shall provide Modify Lookahead |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.2-001 | classification-required | extracted-requirement | RTI shall provide Enable Time Regulation |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.2-002 | classification-required | extracted-requirement | RTI shall invoke timeRegulationEnabled when Enable Time Regulation succeeds |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.2-003 | classification-required | extracted-requirement | RTI shall not invoke timeRegulationEnabled when Enable Time Regulation is rejected |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.21-001 | classification-required | extracted-requirement | RTI shall provide Retract |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.4-001 | classification-required | extracted-requirement | RTI shall provide Disable Time Regulation |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.5-001 | classification-required | extracted-requirement | RTI shall provide Enable Time Constrained |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.5-002 | classification-required | extracted-requirement | RTI shall invoke timeConstrainedEnabled when Enable Time Constrained succeeds |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.5-003 | classification-required | extracted-requirement | RTI shall not invoke timeConstrainedEnabled when Enable Time Constrained is rejected |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.7-001 | classification-required | extracted-requirement | RTI shall provide Disable Time Constrained |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.8-001 | classification-required | extracted-requirement | RTI shall provide Time Advance Request |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.8-002 | classification-required | extracted-requirement | RTI shall invoke Time Advance Grant when a Time Advance Request succeeds and grant conditions are satisfied |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.8-003 | classification-required | extracted-requirement | RTI shall not invoke Time Advance Grant before a Time Advance Request becomes eligible to grant or when the request is rejected |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions | classification-required | service-requirement | Subscribe Interaction Class With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions | classification-required | service-requirement | Subscribe Interaction Class With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions | classification-required | service-requirement | Unsubscribe Interaction Class With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_12-sendInteractionWithRegions | classification-required | service-requirement | Send Interaction With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions | classification-required | service-requirement | Request Attribute Value Update With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_2-createRegion | classification-required | service-requirement | Create Region service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_3-commitRegionModifications | classification-required | service-requirement | Commit Region Modifications service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_4-deleteRegion | classification-required | service-requirement | Delete Region service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions | classification-required | service-requirement | Register Object Instance With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_6-associateRegionsForUpdates | classification-required | service-requirement | Associate Regions For Updates service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_7-unassociateRegionsForUpdates | classification-required | service-requirement | Unassociate Regions For Updates service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions | classification-required | service-requirement | Subscribe Object Class Attributes With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions | classification-required | service-requirement | Subscribe Object Class Attributes With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions | classification-required | service-requirement | Unsubscribe Object Class Attributes With Regions service |
| IEEE 1516.1-2010 (2010 edition) | 9 | AREA-1516.1-9 | not-applicable | section-area | Data distribution management |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-001 | not-applicable | extracted-requirement | The RTI shall implement DDM services for region creation, routing, and filtered delivery behavior |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.1-001 | classification-required | extracted-requirement | RTI shall support region-based data distribution management |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.1-002 | classification-required | extracted-requirement | RTI shall use FOM-defined dimensions for DDM routing |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.1-003 | classification-required | extracted-requirement | RTI shall determine relevance from subscription regions and update/send regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.10-001 | classification-required | extracted-requirement | RTI shall support subscribing to interaction classes with regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.11-001 | classification-required | extracted-requirement | RTI shall support unsubscribing interaction classes with regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.12-001 | classification-required | extracted-requirement | RTI shall route interactions based on region overlap where dimensions apply |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.13-001 | classification-required | extracted-requirement | RTI shall route attribute-value update requests based on region overlap |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.2-001 | classification-required | extracted-requirement | RTI shall provide Create Region |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.3-001 | classification-required | extracted-requirement | RTI shall provide Commit Region Modifications |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.4-001 | classification-required | extracted-requirement | RTI shall provide Delete Region |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.5-001 | classification-required | extracted-requirement | RTI shall support registering object instances with associated regions where applicable |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.6-001 | classification-required | extracted-requirement | RTI shall support associating regions with object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.7-001 | classification-required | extracted-requirement | RTI shall support unassociating regions from object instance attributes |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.8-001 | classification-required | extracted-requirement | RTI shall support subscribing to object-class attributes with regions |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-9.9-001 | classification-required | extracted-requirement | RTI shall support unsubscribing object-class attributes with regions |
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
| IEEE 1516.1-2010 (2010 edition) | 10 | AREA-1516.1-10 | not-applicable | section-area | Support services |
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
| IEEE 1516.1-2010 (2010 edition) | 11 | AREA-1516.1-11 | not-applicable | section-area | Management object model |
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
| IEEE 1516.1-2010 (2010 edition) | 12 | AREA-1516.1-12 | not-applicable | section-area | Programming language mappings |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ID-001 | classification-required | extracted-requirement | OMT parser shall capture object model identification metadata sufficient to distinguish the module and preserve provenance |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ID-4-001 | classification-required | extracted-requirement | Object model modules shall contain identification information sufficient to distinguish the module and its provenance |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-001 | classification-required | extracted-requirement | HLA object models shall be represented using the OMT components defined by the standard |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-002 | classification-required | extracted-requirement | FOM SOM and MIM parsers shall recognize all standard OMT component tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-003 | classification-required | extracted-requirement | Validators shall distinguish required optional and conditionally required OMT entries |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4-omt_components | not-applicable | omt-area | HLA OMT components |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-001 | classification-required | extracted-requirement | Object models shall include object model identification information |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-002 | classification-required | extracted-requirement | Parser shall extract object model name and model type identification fields when present |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-003 | classification-required | extracted-requirement | Implementation shall distinguish FOM SOM and standard MIM object model types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-004 | classification-required | extracted-requirement | Implementation shall preserve identification metadata during parse and serialize round trip |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_1-object_model_identification | not-applicable | omt-area | Object model identification |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-001 | classification-required | extracted-requirement | OMT parser shall preserve transportation-type declarations and resolve attribute and interaction references to valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-001 | classification-required | extracted-requirement | Object models shall define transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-002 | classification-required | extracted-requirement | Transportation type names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-003 | classification-required | extracted-requirement | Parser shall preserve declared transportation type names |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-004 | classification-required | extracted-requirement | Attributes shall reference only valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-005 | classification-required | extracted-requirement | Interaction classes shall reference only valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-006 | classification-required | extracted-requirement | Validator shall reject references to undefined transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_10-transportation_type_table | not-applicable | omt-area | Transportation type table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-001 | classification-required | extracted-requirement | OMT parser shall preserve update-rate designators and validate references to them from object-model metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-001 | classification-required | extracted-requirement | Object models shall support update rate designators |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-002 | classification-required | extracted-requirement | Update rate designator names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-003 | classification-required | extracted-requirement | Parser shall preserve declared update rate names and values |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-004 | classification-required | extracted-requirement | Attributes referencing update rate designators shall reference valid entries |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-005 | classification-required | extracted-requirement | Validator shall reject undefined update rate references |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_11-update_rate_table | not-applicable | omt-area | Update rate table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-001 | classification-required | extracted-requirement | OMT parser shall preserve switch declarations and resolve switch references used by MOM and support services |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-001 | classification-required | extracted-requirement | Object models shall support declaration of switch metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-002 | classification-required | extracted-requirement | Parser shall preserve declared switch settings |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-003 | classification-required | extracted-requirement | Validator shall ensure switch references are resolvable |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_12-switches_table | not-applicable | omt-area | Switches table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-002 | classification-required | extracted-requirement | OMT parser shall support the basic, simple, enumerated, array, fixed-record, and variant-record datatype families and validate their structure |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-001 | classification-required | extracted-requirement | Object models shall support datatype table declarations |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-002 | classification-required | extracted-requirement | Basic datatype names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-003 | classification-required | extracted-requirement | Parser shall preserve endian size encoding and semantics metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-004 | classification-required | extracted-requirement | Validator shall reject duplicate datatype definitions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-005 | classification-required | extracted-requirement | Parser shall preserve declared datatype names from datatype tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-006 | classification-required | extracted-requirement | Parser shall preserve datatype names referenced by attributes and parameters |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-010 | classification-required | extracted-requirement | Object models shall support simple datatype aliases |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-011 | classification-required | extracted-requirement | Simple datatypes shall reference valid underlying datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-012 | classification-required | extracted-requirement | Validator shall reject unresolved datatype references |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-020 | classification-required | extracted-requirement | Object models shall support enumerated datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-021 | classification-required | extracted-requirement | Enumeration names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-022 | classification-required | extracted-requirement | Enumeration values shall be unique within an enumeration |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-023 | classification-required | extracted-requirement | Parser shall preserve enumeration literal ordering |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-024 | classification-required | extracted-requirement | Validator shall reject duplicate enumeration values |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-030 | classification-required | extracted-requirement | Object models shall support fixed arrays |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-031 | classification-required | extracted-requirement | Object models shall support variable arrays |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-032 | classification-required | extracted-requirement | Array element types shall reference valid datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-033 | classification-required | extracted-requirement | Fixed arrays shall define valid cardinality |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-034 | classification-required | extracted-requirement | Validator shall reject invalid array dimensions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-040 | classification-required | extracted-requirement | Object models shall support fixed record datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-041 | classification-required | extracted-requirement | Fixed records shall contain ordered fields |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-042 | classification-required | extracted-requirement | Fixed record fields shall reference valid datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-043 | classification-required | extracted-requirement | Parser shall preserve field ordering |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-044 | classification-required | extracted-requirement | Validator shall reject unresolved field datatype references |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-050 | classification-required | extracted-requirement | Object models shall support variant record datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-051 | classification-required | extracted-requirement | Variant records shall define a discriminant |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-052 | classification-required | extracted-requirement | Alternative branches shall reference valid datatypes |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-053 | classification-required | extracted-requirement | Parser shall preserve discriminant mappings |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.13-054 | classification-required | extracted-requirement | Validator shall reject duplicate discriminant alternatives |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_13-datatype_table | not-applicable | omt-area | Datatype tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-001 | classification-required | extracted-requirement | OMT parser shall preserve note content through parse and serialization |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-001 | classification-required | extracted-requirement | OMT elements may contain note metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-002 | classification-required | extracted-requirement | Parser shall preserve note content |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-003 | classification-required | extracted-requirement | Serializer shall reproduce note content |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_14-notes_table | not-applicable | omt-area | Notes table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-001 | classification-required | extracted-requirement | OMT parser shall preserve the object-class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-4.2-001 | classification-required | extracted-requirement | Object class structure shall preserve class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-4.2-002 | classification-required | extracted-requirement | Object class definitions shall expose declared and inherited attributes consistently through the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-001 | classification-required | extracted-requirement | Object models shall define object class hierarchy beneath ObjectRoot |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-002 | classification-required | extracted-requirement | Each object class except ObjectRoot shall have exactly one immediate superclass |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-003 | classification-required | extracted-requirement | Parser shall preserve parent-child object class relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-004 | classification-required | extracted-requirement | Validator shall reject duplicate object class names in the same object class hierarchy |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-005 | classification-required | extracted-requirement | Implementation shall support inherited attributes through superclass traversal |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_2-object_class_structure | not-applicable | omt-area | Object class structure table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-001 | classification-required | extracted-requirement | OMT parser shall preserve the interaction-class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-4.3-001 | classification-required | extracted-requirement | Interaction class structure shall preserve class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-4.3-002 | classification-required | extracted-requirement | Interaction class definitions shall expose declared and inherited parameters consistently through the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-001 | classification-required | extracted-requirement | Object models shall define interaction class hierarchy beneath InteractionRoot |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-002 | classification-required | extracted-requirement | Each interaction class except InteractionRoot shall have exactly one immediate superclass |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-003 | classification-required | extracted-requirement | Parser shall preserve parent-child interaction class relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-004 | classification-required | extracted-requirement | Validator shall reject duplicate interaction class names in the same interaction hierarchy |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-005 | classification-required | extracted-requirement | Implementation shall support inherited parameters through superclass traversal |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_3-interaction_class_structure | not-applicable | omt-area | Interaction class structure table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ATTR-001 | classification-required | extracted-requirement | OMT parser shall preserve attribute declarations and make them available for object-class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ATTR-4.4-001 | classification-required | extracted-requirement | Attribute tables shall preserve attribute names and availability for object class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_4-attribute_table | not-applicable | omt-area | Attribute table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-PARAM-001 | classification-required | extracted-requirement | OMT parser shall preserve interaction-parameter declarations and make them available for interaction-class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-PARAM-4.5-001 | classification-required | extracted-requirement | Parameter tables shall preserve parameter names and availability for interaction class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_5-parameter_table | not-applicable | omt-area | Parameter table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-001 | classification-required | extracted-requirement | OMT parser shall preserve routing-space dimension names for DDM and region use |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-4.6-001 | classification-required | extracted-requirement | Dimension tables shall preserve routing-space dimension names for active region and DDM use |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-4.6-002 | classification-required | extracted-requirement | Dimension names shall be unique within the object model |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_6-dimension_table | not-applicable | omt-area | Dimension table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-001 | classification-required | extracted-requirement | OMT parser shall preserve logical-time and datatype metadata used by the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.7-001 | classification-required | extracted-requirement | Time representation tables shall preserve logical time implementation selection from the active model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-001 | classification-required | extracted-requirement | Object models shall identify logical time representation information where required |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-002 | classification-required | extracted-requirement | Parser shall extract time datatype and time factory metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-003 | classification-required | extracted-requirement | RTI integration shall use OMT time representation data to select logical time factories |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_7-time_representation_table | not-applicable | omt-area | Time representation table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-001 | classification-required | extracted-requirement | Object models shall define user-supplied tag datatype information where required |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-002 | classification-required | extracted-requirement | Parser shall extract and preserve user-supplied tag representation |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-003 | classification-required | extracted-requirement | RTI services that carry tags shall validate tag values against the declared tag representation where applicable |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_8-user_supplied_tag_table | not-applicable | omt-area | User-supplied tag table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-001 | classification-required | extracted-requirement | OMT parser shall support declaration, validation, and serialization of synchronization-point metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-001 | classification-required | extracted-requirement | Object models shall support declaration of synchronization points |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-002 | classification-required | extracted-requirement | Synchronization point names shall be unique within the object model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-003 | classification-required | extracted-requirement | Parser shall preserve synchronization point metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-004 | classification-required | extracted-requirement | Validator shall reject duplicate synchronization point definitions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-005 | classification-required | extracted-requirement | Synchronization definitions shall survive parse/serialize round-trip |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_9-synchronization_table | not-applicable | omt-area | Synchronization table |
| IEEE 1516.2-2010 (2010 edition) | 5 | HLA1516.2-OMT-5-001 | classification-required | extracted-requirement | Implementation documentation shall use the FOM SOM lexicon consistently when naming object model artifacts |
| IEEE 1516.2-2010 (2010 edition) | 5 | REQ-OMT-5-lexicon | not-applicable | omt-area | FOM/SOM lexicon |
| IEEE 1516.2-2010 (2010 edition) | 6 | HLA1516.2-OMT-6-001 | classification-required | extracted-requirement | Conformance claims shall distinguish implemented subsets from unimplemented or planned OMT behavior |
| IEEE 1516.2-2010 (2010 edition) | 6 | REQ-OMT-6-conformance | not-applicable | omt-area | Conformance |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-001 | classification-required | extracted-requirement | OMT merge shall compose class, datatype, dimension, and standard MIM content into a consistent merged representation |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7-001 | classification-required | extracted-requirement | FOM module merge shall be transactional when rejecting inconsistent logical time representations |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7-002 | classification-required | extracted-requirement | Create federation with an explicit MIM shall preserve the requested MIM module as active provenance |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-OMT-001 | classification-required | extracted-requirement | OMT merge shall apply the supported merge rules and reject conflicts that would produce an inconsistent merged model |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-OMT-7-001 | classification-required | extracted-requirement | FOM module merge shall reject conflicting logical time representations |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-OMT-7-002 | classification-required | extracted-requirement | FOM module merge shall combine supported modules into one active federation object model catalog |
| IEEE 1516.2-2010 (2010 edition) | 7 | REQ-OMT-7-merging_rules | not-applicable | omt-area | FOM module/SOM module merging rules |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-001 | classification-required | extracted-requirement | RTI shall support composition of a federation object model from multiple FOM modules |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-002 | classification-required | extracted-requirement | Merge process shall preserve class hierarchy consistency |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-003 | classification-required | extracted-requirement | Merge process shall preserve datatype consistency |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-004 | classification-required | extracted-requirement | Merge process shall preserve dimension consistency |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-005 | classification-required | extracted-requirement | Merge process shall detect conflicting definitions |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-006 | classification-required | extracted-requirement | Merge process shall reject incompatible duplicate definitions |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-007 | classification-required | extracted-requirement | Merge process shall generate a merged FDD representation |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7.0-008 | classification-required | extracted-requirement | Merge process shall support inclusion of the standard MIM |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-MIM-D-001 | classification-required | extracted-requirement | Standard MIM content shall be available through the active catalog and MOM request report paths |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-001 | classification-required | extracted-requirement | Parser shall accept OMT XML interchange documents rooted at objectModel |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-002 | classification-required | extracted-requirement | Resolver shall normalize XML module designators into backend-consumable URLs or file URIs |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-003 | classification-required | extracted-requirement | MIM XML module payloads shall remain available for MOM request and report paths in the active implementation subset |
| IEEE 1516.2-2010 (2010 edition) | unknown | REQ-OMT-Annex_D-dif | not-applicable | omt-area | OMT data interchange format |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-MIM-001 | classification-required | extracted-requirement | The standard MIM shall load as part of the effective federation model and expose its MOM/MIM behavior through the normal request and report paths |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-002 | classification-required | extracted-requirement | OMT XML schema validation shall reject XML documents that do not conform to the normative OMT schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-E-001 | classification-required | extracted-requirement | Schema-level XML conformance shall be validated against the standard schema when full schema validation is implemented |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-001 | classification-required | extracted-requirement | OMT XML interchange shall validate namespaces, reject schema-invalid documents, preserve schema-valid serialization, and preserve semantic round-trip fidelity |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-001 | classification-required | extracted-requirement | OMT XML documents shall conform to the published XML schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-002 | classification-required | extracted-requirement | Parser shall validate XML namespace usage |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-003 | classification-required | extracted-requirement | Parser shall reject schema-invalid XML documents |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-004 | classification-required | extracted-requirement | Serializer shall emit schema-valid XML |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-005 | classification-required | extracted-requirement | Parse to serialize to parse shall preserve semantic equivalence |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-E-001 | classification-required | extracted-requirement | Schema-level XML conformance shall be validated against the standard schema when full schema validation is implemented |
| IEEE 1516.2-2010 (2010 edition) | unknown | REQ-OMT-Annex_E-schema | not-applicable | omt-area | OMT conformance XML Schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-F-001 | classification-required | extracted-requirement | Standard SOM example artifacts shall be maintained as parser regression fixtures |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-G-001 | classification-required | extracted-requirement | Standard FOM example artifacts shall be maintained as parser regression fixtures |
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
