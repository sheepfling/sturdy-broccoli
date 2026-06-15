# pitch-py4j Requirement Disposition

This audit projects the shared IEEE 1516-2010 (2010 edition) / IEEE 1516.1-2010 (2010 edition) / IEEE 1516.2-2010 (2010 edition) requirements matrix onto `pitch-py4j` so every row has an explicit generated `pitch-py4j` disposition.

This profile currently inherits the Pitch family-level requirement disposition because the JPype and Py4J routes are adapter profiles over the same generated Pitch requirement packet, with profile-specific evidence carried through the family artifact fields.

## Summary

| Document clause | Total | Verified | Blocked | Vendor divergent | Not yet tested | Not applicable | Classification required |
|---|---:|---:|---:|---:|---:|---:|---:|
| IEEE 1516-2010 (2010 edition) unknown | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| IEEE 1516-2010 (2010 edition) §12 | 21 | 0 | 0 | 0 | 0 | 0 | 21 |
| IEEE 1516.1-2010 (2010 edition) §10 | 84 | 0 | 0 | 0 | 82 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §11 | 37 | 0 | 0 | 0 | 0 | 2 | 35 |
| IEEE 1516.1-2010 (2010 edition) §12 | 10 | 0 | 0 | 0 | 9 | 1 | 0 |
| IEEE 1516.1-2010 (2010 edition) §4 | 281 | 274 | 2 | 3 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §5 | 52 | 45 | 2 | 0 | 0 | 5 | 0 |
| IEEE 1516.1-2010 (2010 edition) §6 | 110 | 99 | 0 | 9 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §7 | 39 | 27 | 0 | 10 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §8 | 61 | 41 | 0 | 18 | 0 | 2 | 0 |
| IEEE 1516.1-2010 (2010 edition) §9 | 31 | 29 | 0 | 0 | 0 | 2 | 0 |
| IEEE 1516.2-2010 (2010 edition) unknown | 15 | 0 | 0 | 0 | 0 | 0 | 15 |
| IEEE 1516.2-2010 (2010 edition) §4 | 99 | 0 | 0 | 0 | 0 | 0 | 99 |
| IEEE 1516.2-2010 (2010 edition) §5 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| IEEE 1516.2-2010 (2010 edition) §6 | 2 | 1 | 0 | 0 | 0 | 1 | 0 |
| IEEE 1516.2-2010 (2010 edition) §7 | 13 | 12 | 0 | 1 | 0 | 0 | 0 |
| multi-section unknown | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| multi-section §11 | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| multi-section §12 | 4 | 2 | 0 | 0 | 0 | 2 | 0 |
| multi-section §4 | 3 | 1 | 0 | 0 | 0 | 2 | 0 |
| multi-section §5 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| multi-section §6 | 14 | 13 | 0 | 1 | 0 | 0 | 0 |
| multi-section §7 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| multi-section §8 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |

## Non-Verified Rows

| Document | Clause | Requirement | Disposition | Kind | Title |
|---|---|---|---|---|---|
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.1-001 | classification-required | extracted-requirement | Coordinated save |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.1-002 | classification-required | extracted-requirement | Save outcome collection |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.1-003 | classification-required | extracted-requirement | Scheduled save at logical time |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.1-004 | classification-required | extracted-requirement | Abort save |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-001 | classification-required | extracted-requirement | Coordinated restore |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-002 | classification-required | extracted-requirement | Restore outcome collection |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-003 | classification-required | extracted-requirement | Restore logical time state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-004 | classification-required | extracted-requirement | Abort restore |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-005 | classification-required | extracted-requirement | Restore object instance names values and existence |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-006 | classification-required | extracted-requirement | Restore object ownership and attribute ownership state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-007 | classification-required | extracted-requirement | Restore federate runtime flags and lookahead |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-008 | classification-required | extracted-requirement | Restore automatic resign and advisory policy state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-009 | classification-required | extracted-requirement | Restore reporting and conveyance switch state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-010 | classification-required | extracted-requirement | Discard stale callback queue state on restore |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-011 | classification-required | extracted-requirement | Discard stale message retraction bookkeeping on restore |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-012 | classification-required | extracted-requirement | Restore attribute order override state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-013 | classification-required | extracted-requirement | Restore interaction order override state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-014 | classification-required | extracted-requirement | Callback enablement remains runtime policy not restored state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-015 | classification-required | extracted-requirement | Restore attribute transportation override state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.2-016 | classification-required | extracted-requirement | Restore interaction transportation override state |
| IEEE 1516-2010 (2010 edition) | 12 | HLA1516-RULE-12.3-001 | classification-required | extracted-requirement | Unknown restore label failure |
| IEEE 1516-2010 (2010 edition) | unknown | HLA1516-RULE-001 | classification-required | extracted-requirement | Federation rules |
| IEEE 1516-2010 (2010 edition) | unknown | HLA1516-FW-001 | classification-required | extracted-requirement | Framework concepts |
| IEEE 1516.1-2010 (2010 edition) | 4 | AREA-1516.1-4 | not-applicable | section-area | Federation management |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-001 | not-applicable | curated-seed | Federation Management |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.5-001 | blocked | extracted-requirement | RTI shall detect lost federates and report them through MOM |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.1.5-002 | blocked | extracted-requirement | RTI shall resign lost federates using the current automatic resign directive |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.5-EXC-001 | vendor-divergent | extracted-requirement | Create Federation Execution shall distinguish duplicate-name, FOM-open, FOM-read, MIM-open, MIM-read, invalid-time-factory, inconsistent-FOM, and invalid-standard-MIM-designator failures. |
| IEEE 1516.1-2010 (2010 edition) | 4 | REQ-RTI-FM-4_5-createFederationExecutionWithMIM | vendor-divergent | service-requirement | Create Federation Execution service |
| IEEE 1516.1-2010 (2010 edition) | 4 | HLA1516.1-FM-4.9-EXC-001 | vendor-divergent | extracted-requirement | Join Federation Execution shall distinguish not-connected, missing-federation, duplicate-federate-name, already-joined, save-in-progress, restore-in-progress, FOM-open, FOM-read, invalid-time-factory, and inconsistent-FOM failures. |
| IEEE 1516.1-2010 (2010 edition) | 5 | AREA-1516.1-5 | not-applicable | section-area | Declaration management |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-001 | not-applicable | extracted-requirement | The RTI shall implement declaration-management services for publication |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.1-001 | not-applicable | extracted-requirement | Each FDD class shall have at most one immediate superclass. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.1-002 | not-applicable | extracted-requirement | Object classes shall expose declared and inherited available attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.1.1-003 | not-applicable | extracted-requirement | Interaction classes shall expose declared and inherited available parameters. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.3-002 | blocked | extracted-requirement | Unpublishing shall remove the federate’s ability to update the specified attributes. |
| IEEE 1516.1-2010 (2010 edition) | 5 | HLA1516.1-DM-5.5-002 | blocked | extracted-requirement | Unpublishing an interaction class shall remove the federate’s ability to send interactions of that class. |
| IEEE 1516.1-2010 (2010 edition) | 6 | AREA-1516.1-6 | not-applicable | section-area | Object management |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-001 | not-applicable | extracted-requirement | The RTI shall implement object-management services for registration |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.1.10-001 | vendor-divergent | extracted-requirement | RTI shall use transportation types for object updates and interactions as defined by the FDD and service arguments. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.23-001 | vendor-divergent | extracted-requirement | RTI shall provide Request Attribute Transportation Type Change across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.24-001 | vendor-divergent | extracted-requirement | RTI shall invoke Confirm Attribute Transportation Type Change across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.25-001 | vendor-divergent | extracted-requirement | RTI shall provide Query Attribute Transportation Type across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.26-001 | vendor-divergent | extracted-requirement | RTI shall invoke Report Attribute Transportation Type across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.27-001 | vendor-divergent | extracted-requirement | RTI shall provide Request Interaction Transportation Type Change across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.28-001 | vendor-divergent | extracted-requirement | RTI shall invoke Confirm Interaction Transportation Type Change across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.29-001 | vendor-divergent | extracted-requirement | RTI shall provide Query Interaction Transportation Type across the full transportation semantic space defined by the standard. |
| IEEE 1516.1-2010 (2010 edition) | 6 | HLA1516.1-OM-6.30-001 | vendor-divergent | extracted-requirement | RTI shall invoke Report Interaction Transportation Type across the full transportation semantic space. |
| IEEE 1516.1-2010 (2010 edition) | 7 | AREA-1516.1-7 | not-applicable | section-area | Ownership management |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-001 | not-applicable | curated-seed | Ownership Management |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.10-001 | vendor-divergent | extracted-requirement | Cancel ownership acquisition |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.11-001 | vendor-divergent | extracted-requirement | Cancellation confirmation |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture | vendor-divergent | service-requirement | Cancel Negotiated Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition | vendor-divergent | service-requirement | Cancel Attribute Ownership Acquisition service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation | vendor-divergent | service-requirement | Confirm Attribute Ownership Acquisition Cancellation service |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.3-001 | vendor-divergent | extracted-requirement | Negotiated divestiture |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture | vendor-divergent | service-requirement | Negotiated Attribute Ownership Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 7 | HLA1516.1-OWN-7.4-001 | vendor-divergent | extracted-requirement | Divestiture request notification |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-FED-OWN-7_5-requestDivestitureConfirmation | vendor-divergent | service-requirement | Request Divestiture Confirmation service |
| IEEE 1516.1-2010 (2010 edition) | 7 | REQ-RTI-OWN-7_6-confirmDivestiture | vendor-divergent | service-requirement | Confirm Divestiture service |
| IEEE 1516.1-2010 (2010 edition) | 8 | AREA-1516.1-8 | not-applicable | section-area | Time management |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-001 | not-applicable | curated-seed | Time Management |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1-001 | vendor-divergent | extracted-requirement | RTI shall represent modeled time as points on the HLA time axis |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1-002 | vendor-divergent | extracted-requirement | RTI shall coordinate logical time advancement with object updates and interactions |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.1-001 | vendor-divergent | extracted-requirement | RTI shall treat attribute updates interactions object deletes and DDM region messages as HLA messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-001 | vendor-divergent | extracted-requirement | Each message shall be either timestamp order TSO or receive order RO |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-002 | vendor-divergent | extracted-requirement | RTI shall determine sent message order type from preferred order type timestamp presence and federate time status |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-003 | vendor-divergent | extracted-requirement | RTI shall never convert RO messages into received TSO messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.2-004 | vendor-divergent | extracted-requirement | RTI shall deliver received TSO messages in timestamp order except where flush queue behavior applies |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.3-002 | vendor-divergent | extracted-requirement | A joined federate logical time shall only advance |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.3-003 | vendor-divergent | extracted-requirement | RTI shall advance logical time only by issuing Time Advance Grant |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.5-001 | vendor-divergent | extracted-requirement | Only time constrained federates may receive TSO messages |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.6-001 | vendor-divergent | extracted-requirement | RTI shall support time advance request services and grant only when delivery guarantees are satisfied |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.1.7-001 | vendor-divergent | extracted-requirement | RTI shall queue pending TSO and RO messages until eligible for delivery |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.10-001 | vendor-divergent | extracted-requirement | RTI shall provide Next Message Request |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_10-nextMessageRequest | vendor-divergent | service-requirement | Next Message Request service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_11-nextMessageRequestAvailable | vendor-divergent | service-requirement | Next Message Request Available service |
| IEEE 1516.1-2010 (2010 edition) | 8 | HLA1516.1-TM-8.21-001 | vendor-divergent | extracted-requirement | RTI shall provide Retract |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-RTI-TM-8_21-retract | vendor-divergent | service-requirement | Retract service |
| IEEE 1516.1-2010 (2010 edition) | 8 | REQ-FED-TM-8_22-requestRetraction | vendor-divergent | service-requirement | Request Retraction service |
| IEEE 1516.1-2010 (2010 edition) | 9 | AREA-1516.1-9 | not-applicable | section-area | Data distribution management |
| IEEE 1516.1-2010 (2010 edition) | 9 | HLA1516.1-DDM-001 | not-applicable | curated-seed | Data Distribution Management |
| IEEE 1516.1-2010 (2010 edition) | 10 | AREA-1516.1-10 | not-applicable | section-area | Support services |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-001 | not-applicable | curated-seed | Support Services |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.1-001 | not-yet-tested | extracted-requirement | Name-handle lookup services |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.1-002 | not-yet-tested | extracted-requirement | Advisory switch services |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.1-003 | not-yet-tested | extracted-requirement | Ordering transportation and dimension metadata queries |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.10-001 | not-yet-tested | extracted-requirement | Object instance handle by name |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_10-getObjectInstanceName | not-yet-tested | service-requirement | Get Object Instance Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.11-001 | not-yet-tested | extracted-requirement | Object instance name by handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_11-getAttributeHandle | not-yet-tested | service-requirement | Get Attribute Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.12-001 | not-yet-tested | extracted-requirement | Dimension handle by name |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_12-getAttributeName | not-yet-tested | service-requirement | Get Attribute Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.13-001 | not-yet-tested | extracted-requirement | Dimension name by handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_13-getUpdateRateValue | not-yet-tested | service-requirement | Get Update Rate Value service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.14-001 | not-yet-tested | extracted-requirement | Available dimensions query |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_14-getUpdateRateValueForAttribute | not-yet-tested | service-requirement | Get Update Rate Value For Attribute service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.15-001 | not-yet-tested | extracted-requirement | Transportation type handles and names |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_15-getInteractionClassHandle | not-yet-tested | service-requirement | Get Interaction Class Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.16-001 | not-yet-tested | extracted-requirement | Order type handles and names |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_16-getInteractionClassName | not-yet-tested | service-requirement | Get Interaction Class Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.17-001 | not-yet-tested | extracted-requirement | Enable-disable advisory switches |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_17-getParameterHandle | not-yet-tested | service-requirement | Get Parameter Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.18-001 | not-yet-tested | extracted-requirement | Callbacks for advisory switch changes |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_18-getParameterName | not-yet-tested | service-requirement | Get Parameter Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_19-getOrderType | not-yet-tested | service-requirement | Get Order Type service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.2-001 | not-yet-tested | extracted-requirement | Object class handle by name |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_2-getAutomaticResignDirective | not-yet-tested | service-requirement | Get Automatic Resign Directive service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_20-getOrderName | not-yet-tested | service-requirement | Get Order Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_21-getTransportationType | not-yet-tested | service-requirement | Get Transportation Type Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_21-getTransportationTypeHandle | not-yet-tested | service-requirement | Get Transportation Type Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_22-getTransportationName | not-yet-tested | service-requirement | Get Transportation Type Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_22-getTransportationTypeName | not-yet-tested | service-requirement | Get Transportation Type Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_23-getAvailableDimensionsForClassAttribute | not-yet-tested | service-requirement | Get Available Dimensions For Class Attribute service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_24-getAvailableDimensionsForInteractionClass | not-yet-tested | service-requirement | Get Available Dimensions For Interaction Class service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_25-getDimensionHandle | not-yet-tested | service-requirement | Get Dimension Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_26-getDimensionName | not-yet-tested | service-requirement | Get Dimension Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_27-getDimensionUpperBound | not-yet-tested | service-requirement | Get Dimension Upper Bound service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_28-getDimensionHandleSet | not-yet-tested | service-requirement | Get Dimension Handle Set service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_29-getRangeBounds | not-yet-tested | service-requirement | Get Range Bounds service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.3-001 | not-yet-tested | extracted-requirement | Object class name by handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_3-setAutomaticResignDirective | not-yet-tested | service-requirement | Set Automatic Resign Directive service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_30-setRangeBounds | not-yet-tested | service-requirement | Set Range Bounds service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_31-normalizeFederateHandle | not-yet-tested | service-requirement | Normalize Federate Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_32-normalizeServiceGroup | not-yet-tested | service-requirement | Normalize Service Group service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_33-enableObjectClassRelevanceAdvisorySwitch | not-yet-tested | service-requirement | Enable Object Class Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_34-disableObjectClassRelevanceAdvisorySwitch | not-yet-tested | service-requirement | Disable Object Class Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_35-enableAttributeRelevanceAdvisorySwitch | not-yet-tested | service-requirement | Enable Attribute Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_36-disableAttributeRelevanceAdvisorySwitch | not-yet-tested | service-requirement | Disable Attribute Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_37-enableAttributeScopeAdvisorySwitch | not-yet-tested | service-requirement | Enable Attribute Scope Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_38-disableAttributeScopeAdvisorySwitch | not-yet-tested | service-requirement | Disable Attribute Scope Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_39-enableInteractionRelevanceAdvisorySwitch | not-yet-tested | service-requirement | Enable Interaction Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.4-001 | not-yet-tested | extracted-requirement | Attribute handle by name and class |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_4-getFederateHandle | not-yet-tested | service-requirement | Get Federate Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_40-disableInteractionRelevanceAdvisorySwitch | not-yet-tested | service-requirement | Disable Interaction Relevance Advisory Switch service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_41-evokeCallback | not-yet-tested | service-requirement | Evoke Callback service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_42-evokeMultipleCallbacks | not-yet-tested | service-requirement | Evoke Multiple Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_43-enableCallbacks | not-yet-tested | service-requirement | Enable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-disableCallbacks | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeHandleSetFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeHandleValueMapFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getAttributeSetRegionSetPairListFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getDimensionHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getDimensionHandleSetFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getFederateHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getFederateHandleSetFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getHLAversion | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getInteractionClassHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getObjectClassHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getObjectInstanceHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getParameterHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getParameterHandleValueMapFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getRegionHandleSetFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getTimeFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_44-getTransportationTypeHandleFactory | not-yet-tested | service-requirement | Disable Callbacks service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.5-001 | not-yet-tested | extracted-requirement | Attribute name by handle and class |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_5-getFederateName | not-yet-tested | service-requirement | Get Federate Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.6-001 | not-yet-tested | extracted-requirement | Interaction class handle by name |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_6-getObjectClassHandle | not-yet-tested | service-requirement | Get Object Class Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.7-001 | not-yet-tested | extracted-requirement | Interaction class name by handle |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_7-getObjectClassName | not-yet-tested | service-requirement | Get Object Class Name service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.8-001 | not-yet-tested | extracted-requirement | Parameter handle by name and interaction |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_8-getKnownObjectClassHandle | not-yet-tested | service-requirement | Get Known Object Class Handle service |
| IEEE 1516.1-2010 (2010 edition) | 10 | HLA1516.1-SUP-10.9-001 | not-yet-tested | extracted-requirement | Parameter name by handle and interaction |
| IEEE 1516.1-2010 (2010 edition) | 10 | REQ-RTI-SS-10_9-getObjectInstanceHandle | not-yet-tested | service-requirement | Get Object Instance Handle service |
| IEEE 1516.1-2010 (2010 edition) | 11 | AREA-1516.1-11 | not-applicable | section-area | Management object model |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-001 | not-applicable | curated-seed | Management Object Model behavior |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-001 | classification-required | extracted-requirement | RTI shall expose management information through standard MOM objects and interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-002 | classification-required | extracted-requirement | MOM shall use the OMT format |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-003 | classification-required | extracted-requirement | FDD for a federation execution shall include all MOM elements |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-004 | classification-required | extracted-requirement | MOM object classes interaction classes attributes and parameters shall be predefined in the FDD |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.1-005 | classification-required | extracted-requirement | MOM definitions shall not be revised though they may be extended |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-001 | classification-required | extracted-requirement | RTI shall publish MOM object classes required by the standard |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-002 | classification-required | extracted-requirement | MOM federate object instance |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-003 | classification-required | extracted-requirement | RTI shall register one MOM federation object instance for the federation execution |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2-004 | classification-required | extracted-requirement | RTI shall periodically update MOM object attributes according to timing data |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2.1-001 | classification-required | extracted-requirement | MOM classes can be extended by subclasses and additional attributes |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2.1-002 | classification-required | extracted-requirement | RTI does not create hidden MOM subscriptions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.2.1-003 | classification-required | extracted-requirement | MOM attributes remain RTI-owned |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-001 | classification-required | extracted-requirement | RTI shall support MOM interaction classes according to their defined roles |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-002 | classification-required | extracted-requirement | RTI shall act on MOM adjustment interactions |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-003 | classification-required | extracted-requirement | MOM request to report behavior |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-004 | classification-required | extracted-requirement | MOM report interactions are emitted with the standard payload |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-005 | classification-required | extracted-requirement | RTI shall act on MOM service interactions by invoking HLA services on behalf of another federate |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3-006 | classification-required | extracted-requirement | Rejected MOM requests actions or federate-sent MOM reports do not emit the corresponding positive MOM report interaction |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3.1-001 | classification-required | extracted-requirement | RTI shall publish MOM report interactions at the leaf class level |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.3.1-002 | classification-required | extracted-requirement | Nonstandard MOM interaction parameters are ignored on receipt |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4-001 | classification-required | extracted-requirement | RTI shall apply MOM-specific RTI characteristics defined by the standard rather than behaving as a normal joined federate |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-001 | classification-required | extracted-requirement | RTI shall publish all MOM leaf object classes designated as published in the MOM tables |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-002 | classification-required | extracted-requirement | RTI shall publish all required attributes for published MOM object classes |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-003 | classification-required | extracted-requirement | RTI shall publish all MOM leaf interaction classes designated as published |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-004 | classification-required | extracted-requirement | RTI shall subscribe to MOM leaf interaction classes designated as subscribed |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-005 | classification-required | extracted-requirement | RTI does not join as a time-managed MOM federate |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-006 | classification-required | extracted-requirement | MOM messages carry no timestamp or retraction metadata |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-007 | classification-required | extracted-requirement | MOM instance attributes remain under RTI ownership |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-008 | classification-required | extracted-requirement | MOM messages retain fixed reliable transport and receive order |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.4.1-009 | classification-required | extracted-requirement | MOM rejects DDM region services |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-001 | classification-required | extracted-requirement | Service invocation reporting |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-002 | classification-required | extracted-requirement | RTI shall determine each federate service reporting behavior from the service reporting switch state |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-003 | classification-required | extracted-requirement | Rejected MOM adjustments do not emit HLAreportServiceInvocation |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.5-004 | classification-required | extracted-requirement | RTI shall report standard MOM exception information when exception reporting is enabled |
| IEEE 1516.1-2010 (2010 edition) | 11 | HLA1516.1-MOM-11.6-001 | classification-required | extracted-requirement | MOM table information appears in compliant FOMs without alteration |
| IEEE 1516.1-2010 (2010 edition) | 12 | AREA-1516.1-12 | not-applicable | section-area | Programming language mappings |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeAttributeHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeDimensionHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeFederateHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeInteractionClassHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeMessageRetractionHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeObjectClassHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeObjectInstanceHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeParameterHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.1-2010 (2010 edition) | 12 | REQ-RTI-PLM-12_2-decodeRegionHandle | not-yet-tested | service-requirement | Designators |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ID-4-001 | classification-required | extracted-requirement | Object model modules shall contain identification information sufficient to distinguish the module and its provenance |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-001 | classification-required | extracted-requirement | HLA object models shall be represented using the OMT components defined by the standard |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-002 | classification-required | extracted-requirement | FOM SOM and MIM parsers shall recognize all standard OMT component tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMT-4.0-003 | classification-required | extracted-requirement | Validators shall distinguish required optional and conditionally required OMT entries |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4-omt_components | classification-required | omt-area | HLA OMT components |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-001 | classification-required | extracted-requirement | Object models shall include object model identification information |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-002 | classification-required | extracted-requirement | Parser shall extract object model name and model type identification fields when present |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-003 | classification-required | extracted-requirement | Implementation shall distinguish FOM SOM and standard MIM object model types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OMID-4.1-004 | classification-required | extracted-requirement | Implementation shall preserve identification metadata during parse and serialize round trip |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_1-object_model_identification | classification-required | omt-area | Object model identification |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-001 | classification-required | extracted-requirement | Object models shall define transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-002 | classification-required | extracted-requirement | Transportation type names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-003 | classification-required | extracted-requirement | Parser shall preserve declared transportation type names |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-004 | classification-required | extracted-requirement | Attributes shall reference only valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-005 | classification-required | extracted-requirement | Interaction classes shall reference only valid transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TRANS-4.10-006 | classification-required | extracted-requirement | Validator shall reject references to undefined transportation types |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_10-transportation_type_table | classification-required | omt-area | Transportation type table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-001 | classification-required | extracted-requirement | Object models shall support update rate designators |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-002 | classification-required | extracted-requirement | Update rate designator names shall be unique |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-003 | classification-required | extracted-requirement | Parser shall preserve declared update rate names and values |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-004 | classification-required | extracted-requirement | Attributes referencing update rate designators shall reference valid entries |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-URATE-4.11-005 | classification-required | extracted-requirement | Validator shall reject undefined update rate references |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_11-update_rate_table | classification-required | omt-area | Update rate table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-001 | classification-required | extracted-requirement | Object models shall support declaration of switch metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-002 | classification-required | extracted-requirement | Parser shall preserve declared switch settings |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SWITCH-4.12-003 | classification-required | extracted-requirement | Validator shall ensure switch references are resolvable |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_12-switches_table | classification-required | omt-area | Switches table |
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
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_13-datatype_table | classification-required | omt-area | Datatype tables |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-001 | classification-required | extracted-requirement | OMT elements may contain note metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-002 | classification-required | extracted-requirement | Parser shall preserve note content |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-NOTE-4.14-003 | classification-required | extracted-requirement | Serializer shall reproduce note content |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_14-notes_table | classification-required | omt-area | Notes table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-4.2-001 | classification-required | extracted-requirement | Object class structure shall preserve class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OC-4.2-002 | classification-required | extracted-requirement | Object class definitions shall expose declared and inherited attributes consistently through the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-001 | classification-required | extracted-requirement | Object models shall define object class hierarchy beneath ObjectRoot |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-002 | classification-required | extracted-requirement | Each object class except ObjectRoot shall have exactly one immediate superclass |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-003 | classification-required | extracted-requirement | Parser shall preserve parent-child object class relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-004 | classification-required | extracted-requirement | Validator shall reject duplicate object class names in the same object class hierarchy |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-OCS-4.2-005 | classification-required | extracted-requirement | Implementation shall support inherited attributes through superclass traversal |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_2-object_class_structure | classification-required | omt-area | Object class structure table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-4.3-001 | classification-required | extracted-requirement | Interaction class structure shall preserve class hierarchy and inheritance relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-IC-4.3-002 | classification-required | extracted-requirement | Interaction class definitions shall expose declared and inherited parameters consistently through the active catalog |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-001 | classification-required | extracted-requirement | Object models shall define interaction class hierarchy beneath InteractionRoot |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-002 | classification-required | extracted-requirement | Each interaction class except InteractionRoot shall have exactly one immediate superclass |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-003 | classification-required | extracted-requirement | Parser shall preserve parent-child interaction class relationships |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-004 | classification-required | extracted-requirement | Validator shall reject duplicate interaction class names in the same interaction hierarchy |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ICS-4.3-005 | classification-required | extracted-requirement | Implementation shall support inherited parameters through superclass traversal |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_3-interaction_class_structure | classification-required | omt-area | Interaction class structure table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-ATTR-4.4-001 | classification-required | extracted-requirement | Attribute tables shall preserve attribute names and availability for object class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_4-attribute_table | classification-required | omt-area | Attribute table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-PARAM-4.5-001 | classification-required | extracted-requirement | Parameter tables shall preserve parameter names and availability for interaction class lookup |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_5-parameter_table | classification-required | omt-area | Parameter table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-4.6-001 | classification-required | extracted-requirement | Dimension tables shall preserve routing-space dimension names for active region and DDM use |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DIM-4.6-002 | classification-required | extracted-requirement | Dimension names shall be unique within the object model |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_6-dimension_table | classification-required | omt-area | Dimension table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-DT-4.7-001 | classification-required | extracted-requirement | Time representation tables shall preserve logical time implementation selection from the active model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-001 | classification-required | extracted-requirement | Object models shall identify logical time representation information where required |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-002 | classification-required | extracted-requirement | Parser shall extract time datatype and time factory metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TIME-4.7-003 | classification-required | extracted-requirement | RTI integration shall use OMT time representation data to select logical time factories |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_7-time_representation_table | classification-required | omt-area | Time representation table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-001 | classification-required | extracted-requirement | Object models shall define user-supplied tag datatype information where required |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-002 | classification-required | extracted-requirement | Parser shall extract and preserve user-supplied tag representation |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-TAG-4.8-003 | classification-required | extracted-requirement | RTI services that carry tags shall validate tag values against the declared tag representation where applicable |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_8-user_supplied_tag_table | classification-required | omt-area | User-supplied tag table |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-001 | classification-required | extracted-requirement | Object models shall support declaration of synchronization points |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-002 | classification-required | extracted-requirement | Synchronization point names shall be unique within the object model |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-003 | classification-required | extracted-requirement | Parser shall preserve synchronization point metadata |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-004 | classification-required | extracted-requirement | Validator shall reject duplicate synchronization point definitions |
| IEEE 1516.2-2010 (2010 edition) | 4 | HLA1516.2-SYNC-4.9-005 | classification-required | extracted-requirement | Synchronization definitions shall survive parse/serialize round-trip |
| IEEE 1516.2-2010 (2010 edition) | 4 | REQ-OMT-4_9-synchronization_table | classification-required | omt-area | Synchronization table |
| IEEE 1516.2-2010 (2010 edition) | 5 | HLA1516.2-OMT-5-001 | classification-required | extracted-requirement | Implementation documentation shall use the FOM SOM lexicon consistently when naming object model artifacts |
| IEEE 1516.2-2010 (2010 edition) | 5 | REQ-OMT-5-lexicon | classification-required | omt-area | FOM/SOM lexicon |
| IEEE 1516.2-2010 (2010 edition) | 6 | REQ-OMT-6-conformance | not-applicable | omt-area | Conformance |
| IEEE 1516.2-2010 (2010 edition) | 7 | HLA1516.2-MERGE-7-002 | vendor-divergent | extracted-requirement | Create federation with an explicit MIM shall preserve the requested MIM module as active provenance |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-MIM-D-001 | classification-required | extracted-requirement | Standard MIM content shall be available through the active catalog and MOM request report paths |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-001 | classification-required | extracted-requirement | Parser shall accept OMT XML interchange documents rooted at objectModel |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-002 | classification-required | extracted-requirement | Resolver shall normalize XML module designators into backend-consumable URLs or file URIs |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-D-003 | classification-required | extracted-requirement | MIM XML module payloads shall remain available for MOM request and report paths in the active implementation subset |
| IEEE 1516.2-2010 (2010 edition) | unknown | REQ-OMT-Annex_D-dif | classification-required | omt-area | OMT data interchange format |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-E-001 | classification-required | extracted-requirement | Schema-level XML conformance shall be validated against the standard schema when full schema validation is implemented |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-001 | classification-required | extracted-requirement | OMT XML documents shall conform to the published XML schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-002 | classification-required | extracted-requirement | Parser shall validate XML namespace usage |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-003 | classification-required | extracted-requirement | Parser shall reject schema-invalid XML documents |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-004 | classification-required | extracted-requirement | Serializer shall emit schema-valid XML |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-ANNEX-005 | classification-required | extracted-requirement | Parse to serialize to parse shall preserve semantic equivalence |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-XML-E-001 | classification-required | extracted-requirement | Schema-level XML conformance shall be validated against the standard schema when full schema validation is implemented |
| IEEE 1516.2-2010 (2010 edition) | unknown | REQ-OMT-Annex_E-schema | classification-required | omt-area | OMT conformance XML Schema |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-F-001 | classification-required | extracted-requirement | Standard SOM example artifacts shall be maintained as parser regression fixtures |
| IEEE 1516.2-2010 (2010 edition) | unknown | HLA1516.2-OMT-G-001 | classification-required | extracted-requirement | Standard FOM example artifacts shall be maintained as parser regression fixtures |
| multi-section | 4 | SCENARIO-TARGET-RADAR-001 | not-applicable | verification-slice | Two-federate Target/Radar simulation runs over Python RTI and Java shim profiles |
| multi-section | 4 | REQ-OMT-PARSE-001 | not-applicable | verification-slice | FOM/MIM XML parsing and name-bearing OMT catalog extraction cover the active 1516.2 object, interaction, attribute, parameter, dimension, and time tables |
| multi-section | 5 | REQ-DM-DDM-INTERPLAY-001 | classification-required | verification-slice | DM subscriptions and DDM scope filtering compose before delivery |
| multi-section | 5 | REQ-DM-DDM-OBJECT-SCOPE-001 | classification-required | verification-slice | Object attribute routing is suppressed while regions are out of scope and resumes when regions overlap |
| multi-section | 5 | REQ-OM-UPDATE-RATE-001 | classification-required | verification-slice | Subscribed and FOM-declared update-rate settings throttle eligible reflected updates across direct, inherited, and regioned subscriptions without suppressing receive-order delivery that has no logical-time basis |
| multi-section | 5 | REQ-DM-DECLARATION-STATE-001 | classification-required | verification-slice | Declaration-management state gates registration, update, and interaction send behavior |
| multi-section | 5 | REQ-DM-DDM-GATING-001 | classification-required | verification-slice | DM or DDM subscription declarations are required before object discovery, attribute reflection, or interaction receipt occurs |
| multi-section | 5 | REQ-DM-TIME-INDEPENDENCE-001 | classification-required | verification-slice | Declaration-management publication and subscription state takes effect even while federates are time managed |
| multi-section | 5 | REQ-DM-UNPUBLISH-OBJECT-001 | classification-required | verification-slice | Unpublishing object-class attributes removes the federate's ability to perform strict updates for those attributes |
| multi-section | 5 | REQ-DM-UNPUBLISH-INTERACTION-001 | classification-required | verification-slice | Unpublishing an interaction class removes the federate's ability to perform strict sends for that class |
| multi-section | 5 | REQ-DM-SUBSCRIPTION-DELIVERY-001 | classification-required | verification-slice | Declaration subscriptions drive discover/reflect/receive delivery visibility |
| multi-section | 5 | REQ-DM-UNSUBSCRIBE-OBJECT-001 | classification-required | verification-slice | Unsubscribing object-class attributes removes interest in later reflected updates for those attributes |
| multi-section | 6 | REQ-OM-TRANSPORT-SCOPE-001 | vendor-divergent | verification-slice | Object-management routing semantics cover transport choice, scope, and local-delete restrictions |
| multi-section | 8 | REQ-TIME-ORDER-001 | vendor-divergent | verification-slice | Timestamp-order queues respect local GALT/LITS-style lower-bound rules and DDM filtering before delivery |
| multi-section | 11 | REQ-MOM-TABLE-001 | classification-required | verification-slice | MOM object and interaction exposure is derived from the active MIM/FOM catalog |
| multi-section | 11 | REQ-MOM-OBSERVER-001 | classification-required | verification-slice | A MOM observer witness can reconstruct federation-visible MOM objects, reports, and service invocation traffic |
| multi-section | 11 | REQ-MOM-SERVICE-001 | classification-required | verification-slice | MOM HLAservice interactions are modeled as RTI-received actions with negative-path service failure reporting |
| multi-section | 11 | REQ-MOM-REPORT-001 | classification-required | verification-slice | MOM reports use the exact parameter names declared in the active MIM catalog |
| multi-section | 11 | REQ-MOM-NEG-001 | classification-required | verification-slice | Strict MOM decoding reports and raises through generated parameterized negative-path tests |
| multi-section | 11 | REQ-SERVICE-FILE-001 | classification-required | verification-slice | Service-report file output contains initial and per-service records with section anchors |
| multi-section | 12 | REQ-SAVE-RESTORE-CALLBACK-POLICY-001 | not-applicable | verification-slice | Save/restore treats callback enablement as local runtime policy rather than persisted federation state |
| multi-section | 12 | REQ-SAVE-RESTORE-TRANSIENT-STATE-001 | not-applicable | verification-slice | Save/restore discards stale pre-restore callback-queue and message-retraction bookkeeping state |
| multi-section | unknown | REQ-OMT-SCHEMA-001 | classification-required | verification-slice | Annex E schema-level conformance checking is identified explicitly and remains planned |
