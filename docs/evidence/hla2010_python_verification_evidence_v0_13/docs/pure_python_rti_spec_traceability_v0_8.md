# Pure Python RTI development and 1516.1/1516.2 traceability

This v0.8 engineering note links the pure Python RTI and ambassador scaffolding to section identifiers from the uploaded IEEE 1516.1-2010 Federate Interface and IEEE 1516.2-2010 OMT materials. The links are section numbers and titles for code-review traceability; they do not replace the standards and this project is not yet a full conforming RTI.

## Coverage summary
- RTIambassador service names in the generated API: **162**
- Pure Python RTI `_svc_*` implementations: **162/162**
- FederateAmbassador callback names with section references: **55/55**
- Ambassador methods without section mapping: **0**

## Implementation status by RTI service group
| Service group | Spec area | Python RTI services implemented |
|---|---|---:|
| Data Distribution Management | IEEE 1516.1-2010 §9 Data distribution management | 14/14 |
| Declaration Management | IEEE 1516.1-2010 §5 Declaration management | 12/12 |
| Federation Management | IEEE 1516.1-2010 §4 Federation management | 21/21 |
| Object Management | IEEE 1516.1-2010 §6 Object management | 14/14 |
| Ownership Management | IEEE 1516.1-2010 §7 Ownership management | 11/11 |
| Programming Language Mappings | IEEE 1516.1-2010 §12 Programming language mappings | 9/9 |
| Support Services | IEEE 1516.1-2010 §10 Support services | 62/62 |
| Time Management | IEEE 1516.1-2010 §8 Time management | 19/19 |

## FOM/OMT parser references
| Parser area | Spec reference |
|---|---|
| `omt_components` | IEEE 1516.2-2010 §4 HLA OMT components |
| `object_class_structure` | IEEE 1516.2-2010 §4.2 Object class structure table |
| `interaction_class_structure` | IEEE 1516.2-2010 §4.3 Interaction class structure table |
| `attribute_table` | IEEE 1516.2-2010 §4.4 Attribute table |
| `parameter_table` | IEEE 1516.2-2010 §4.5 Parameter table |
| `dimension_table` | IEEE 1516.2-2010 §4.6 Dimension table |
| `time_representation_table` | IEEE 1516.2-2010 §4.7 Time representation table |
| `merging_rules` | IEEE 1516.2-2010 §7 FOM module/SOM module merging rules |
| `dif` | IEEE 1516.2-2010 §Annex D OMT data interchange format |
| `schema` | IEEE 1516.2-2010 §Annex E OMT conformance XML Schema |

## RTIambassador method traceability
| Method | Section | Service group | Python RTI |
|---|---|---|---|
| `abortFederationRestore` | §4.30 Abort Federation Restore service | Federation Management | implemented |
| `abortFederationSave` | §4.21 Abort Federation Save service | Federation Management | implemented |
| `associateRegionsForUpdates` | §9.6 Associate Regions For Updates service | Data Distribution Management | implemented |
| `attributeOwnershipAcquisition` | §7.8 Attribute Ownership Acquisition service | Ownership Management | implemented |
| `attributeOwnershipAcquisitionIfAvailable` | §7.9 Attribute Ownership Acquisition If Available service | Ownership Management | implemented |
| `attributeOwnershipDivestitureIfWanted` | §7.13 Attribute Ownership Divestiture If Wanted service | Ownership Management | implemented |
| `attributeOwnershipReleaseDenied` | §7.12 Attribute Ownership Release Denied service | Ownership Management | implemented |
| `cancelAttributeOwnershipAcquisition` | §7.15 Cancel Attribute Ownership Acquisition service | Ownership Management | implemented |
| `cancelNegotiatedAttributeOwnershipDivestiture` | §7.14 Cancel Negotiated Attribute Ownership Divestiture service | Ownership Management | implemented |
| `changeAttributeOrderType` | §8.23 Change Attribute Order Type service | Time Management | implemented |
| `changeInteractionOrderType` | §8.24 Change Interaction Order Type service | Time Management | implemented |
| `commitRegionModifications` | §9.3 Commit Region Modifications service | Data Distribution Management | implemented |
| `confirmDivestiture` | §7.6 Confirm Divestiture service | Ownership Management | implemented |
| `connect` | §4.2 Connect service | Federation Management | implemented |
| `createFederationExecution` | §4.5 Create Federation Execution service | Federation Management | implemented |
| `createFederationExecutionWithMIM` | §4.5 Create Federation Execution service | Federation Management | implemented |
| `createRegion` | §9.2 Create Region service | Data Distribution Management | implemented |
| `decodeAttributeHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeDimensionHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeFederateHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeInteractionClassHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeMessageRetractionHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeObjectClassHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeObjectInstanceHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeParameterHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `decodeRegionHandle` | §12.2 Designators | Programming Language Mappings | implemented |
| `deleteObjectInstance` | §6.14 Delete Object Instance service | Object Management | implemented |
| `deleteRegion` | §9.4 Delete Region service | Data Distribution Management | implemented |
| `destroyFederationExecution` | §4.6 Destroy Federation Execution service | Federation Management | implemented |
| `disableAsynchronousDelivery` | §8.15 Disable Asynchronous Delivery service | Time Management | implemented |
| `disableAttributeRelevanceAdvisorySwitch` | §10.36 Disable Attribute Relevance Advisory Switch service | Support Services | implemented |
| `disableAttributeScopeAdvisorySwitch` | §10.38 Disable Attribute Scope Advisory Switch service | Support Services | implemented |
| `disableCallbacks` | §10.44 Disable Callbacks service | Support Services | implemented |
| `disableInteractionRelevanceAdvisorySwitch` | §10.40 Disable Interaction Relevance Advisory Switch service | Support Services | implemented |
| `disableObjectClassRelevanceAdvisorySwitch` | §10.34 Disable Object Class Relevance Advisory Switch service | Support Services | implemented |
| `disableTimeConstrained` | §8.7 Disable Time Constrained service | Time Management | implemented |
| `disableTimeRegulation` | §8.4 Disable Time Regulation service | Time Management | implemented |
| `disconnect` | §4.3 Disconnect service | Federation Management | implemented |
| `enableAsynchronousDelivery` | §8.14 Enable Asynchronous Delivery service | Time Management | implemented |
| `enableAttributeRelevanceAdvisorySwitch` | §10.35 Enable Attribute Relevance Advisory Switch service | Support Services | implemented |
| `enableAttributeScopeAdvisorySwitch` | §10.37 Enable Attribute Scope Advisory Switch service | Support Services | implemented |
| `enableCallbacks` | §10.43 Enable Callbacks service | Support Services | implemented |
| `enableInteractionRelevanceAdvisorySwitch` | §10.39 Enable Interaction Relevance Advisory Switch service | Support Services | implemented |
| `enableObjectClassRelevanceAdvisorySwitch` | §10.33 Enable Object Class Relevance Advisory Switch service | Support Services | implemented |
| `enableTimeConstrained` | §8.5 Enable Time Constrained service | Time Management | implemented |
| `enableTimeRegulation` | §8.2 Enable Time Regulation service | Time Management | implemented |
| `evokeCallback` | §10.41 Evoke Callback service | Support Services | implemented |
| `evokeMultipleCallbacks` | §10.42 Evoke Multiple Callbacks service | Support Services | implemented |
| `federateRestoreComplete` | §4.28 Federate Restore Complete service | Federation Management | implemented |
| `federateRestoreNotComplete` | §4.28 Federate Restore Complete service | Federation Management | implemented |
| `federateSaveBegun` | §4.18 Federate Save Begun service | Federation Management | implemented |
| `federateSaveComplete` | §4.19 Federate Save Complete service | Federation Management | implemented |
| `federateSaveNotComplete` | §4.19 Federate Save Complete service | Federation Management | implemented |
| `flushQueueRequest` | §8.12 Flush Queue Request service | Time Management | implemented |
| `getAttributeHandle` | §10.11 Get Attribute Handle service | Support Services | implemented |
| `getAttributeHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getAttributeHandleSetFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getAttributeHandleValueMapFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getAttributeName` | §10.12 Get Attribute Name service | Support Services | implemented |
| `getAttributeSetRegionSetPairListFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getAutomaticResignDirective` | §10.2 Get Automatic Resign Directive service | Support Services | implemented |
| `getAvailableDimensionsForClassAttribute` | §10.23 Get Available Dimensions For Class Attribute service | Support Services | implemented |
| `getAvailableDimensionsForInteractionClass` | §10.24 Get Available Dimensions For Interaction Class service | Support Services | implemented |
| `getDimensionHandle` | §10.25 Get Dimension Handle service | Support Services | implemented |
| `getDimensionHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getDimensionHandleSet` | §10.28 Get Dimension Handle Set service | Support Services | implemented |
| `getDimensionHandleSetFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getDimensionName` | §10.26 Get Dimension Name service | Support Services | implemented |
| `getDimensionUpperBound` | §10.27 Get Dimension Upper Bound service | Support Services | implemented |
| `getFederateHandle` | §10.4 Get Federate Handle service | Support Services | implemented |
| `getFederateHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getFederateHandleSetFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getFederateName` | §10.5 Get Federate Name service | Support Services | implemented |
| `getHLAversion` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getInteractionClassHandle` | §10.15 Get Interaction Class Handle service | Support Services | implemented |
| `getInteractionClassHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getInteractionClassName` | §10.16 Get Interaction Class Name service | Support Services | implemented |
| `getKnownObjectClassHandle` | §10.8 Get Known Object Class Handle service | Support Services | implemented |
| `getObjectClassHandle` | §10.6 Get Object Class Handle service | Support Services | implemented |
| `getObjectClassHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getObjectClassName` | §10.7 Get Object Class Name service | Support Services | implemented |
| `getObjectInstanceHandle` | §10.9 Get Object Instance Handle service | Support Services | implemented |
| `getObjectInstanceHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getObjectInstanceName` | §10.10 Get Object Instance Name service | Support Services | implemented |
| `getOrderName` | §10.20 Get Order Name service | Support Services | implemented |
| `getOrderType` | §10.19 Get Order Type service | Support Services | implemented |
| `getParameterHandle` | §10.17 Get Parameter Handle service | Support Services | implemented |
| `getParameterHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getParameterHandleValueMapFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getParameterName` | §10.18 Get Parameter Name service | Support Services | implemented |
| `getRangeBounds` | §10.29 Get Range Bounds service | Support Services | implemented |
| `getRegionHandleSetFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getTimeFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getTransportationName` | §10.22 Get Transportation Type Name service | Support Services | implemented |
| `getTransportationType` | §10.21 Get Transportation Type Handle service | Support Services | implemented |
| `getTransportationTypeHandle` | §10.21 Get Transportation Type Handle service | Support Services | implemented |
| `getTransportationTypeHandleFactory` | §10.44 Disable Callbacks service | Support Services | implemented |
| `getTransportationTypeName` | §10.22 Get Transportation Type Name service | Support Services | implemented |
| `getUpdateRateValue` | §10.13 Get Update Rate Value service | Support Services | implemented |
| `getUpdateRateValueForAttribute` | §10.14 Get Update Rate Value For Attribute service | Support Services | implemented |
| `isAttributeOwnedByFederate` | §7.19 Is Attribute Owned By Federate service | Ownership Management | implemented |
| `joinFederationExecution` | §4.9 Join Federation Execution service | Federation Management | implemented |
| `listFederationExecutions` | §4.7 List Federation Executions service | Federation Management | implemented |
| `localDeleteObjectInstance` | §6.16 Local Delete Object Instance service | Object Management | implemented |
| `modifyLookahead` | §8.19 Modify Lookahead service | Time Management | implemented |
| `negotiatedAttributeOwnershipDivestiture` | §7.3 Negotiated Attribute Ownership Divestiture service | Ownership Management | implemented |
| `nextMessageRequest` | §8.10 Next Message Request service | Time Management | implemented |
| `nextMessageRequestAvailable` | §8.11 Next Message Request Available service | Time Management | implemented |
| `normalizeFederateHandle` | §10.31 Normalize Federate Handle service | Support Services | implemented |
| `normalizeServiceGroup` | §10.32 Normalize Service Group service | Support Services | implemented |
| `publishInteractionClass` | §5.4 Publish Interaction Class service | Declaration Management | implemented |
| `publishObjectClassAttributes` | §5.2 Publish Object Class Attributes service | Declaration Management | implemented |
| `queryAttributeOwnership` | §7.17 Query Attribute Ownership service | Ownership Management | implemented |
| `queryAttributeTransportationType` | §6.25 Query Attribute Transportation Type service | Object Management | implemented |
| `queryFederationRestoreStatus` | §4.31 Query Federation Restore Status service | Federation Management | implemented |
| `queryFederationSaveStatus` | §4.22 Query Federation Save Status service | Federation Management | implemented |
| `queryGALT` | §8.16 Query GALT service | Time Management | implemented |
| `queryInteractionTransportationType` | §6.29 Query Interaction Transportation Type service | Object Management | implemented |
| `queryLITS` | §8.18 Query LITS service | Time Management | implemented |
| `queryLogicalTime` | §8.17 Query Logical Time service | Time Management | implemented |
| `queryLookahead` | §8.20 Query Lookahead service | Time Management | implemented |
| `registerFederationSynchronizationPoint` | §4.11 Register Federation Synchronization Point service | Federation Management | implemented |
| `registerObjectInstance` | §6.8 Register Object Instance service | Object Management | implemented |
| `registerObjectInstanceWithRegions` | §9.5 Register Object Instance With Regions service | Data Distribution Management | implemented |
| `releaseMultipleObjectInstanceName` | §6.7 Release Multiple Object Instance Names service | Object Management | implemented |
| `releaseObjectInstanceName` | §6.4 Release Object Instance Name service | Object Management | implemented |
| `requestAttributeTransportationTypeChange` | §6.23 Request Attribute Transportation Type Change service | Object Management | implemented |
| `requestAttributeValueUpdate` | §6.19 Request Attribute Value Update service | Object Management | implemented |
| `requestAttributeValueUpdateWithRegions` | §9.13 Request Attribute Value Update With Regions service | Data Distribution Management | implemented |
| `requestFederationRestore` | §4.24 Request Federation Restore service | Federation Management | implemented |
| `requestFederationSave` | §4.16 Request Federation Save service | Federation Management | implemented |
| `requestInteractionTransportationTypeChange` | §6.27 Request Interaction Transportation Type Change service | Object Management | implemented |
| `reserveMultipleObjectInstanceName` | §6.5 Reserve Multiple Object Instance Names service | Object Management | implemented |
| `reserveObjectInstanceName` | §6.2 Reserve Object Instance Name service | Object Management | implemented |
| `resignFederationExecution` | §4.10 Resign Federation Execution service | Federation Management | implemented |
| `retract` | §8.21 Retract service | Time Management | implemented |
| `sendInteraction` | §6.12 Send Interaction service | Object Management | implemented |
| `sendInteractionWithRegions` | §9.12 Send Interaction With Regions service | Data Distribution Management | implemented |
| `setAutomaticResignDirective` | §10.3 Set Automatic Resign Directive service | Support Services | implemented |
| `setRangeBounds` | §10.30 Set Range Bounds service | Support Services | implemented |
| `subscribeInteractionClass` | §5.8 Subscribe Interaction Class service | Declaration Management | implemented |
| `subscribeInteractionClassPassively` | §5.8 Subscribe Interaction Class service | Declaration Management | implemented |
| `subscribeInteractionClassPassivelyWithRegions` | §9.10 Subscribe Interaction Class With Regions service | Data Distribution Management | implemented |
| `subscribeInteractionClassWithRegions` | §9.10 Subscribe Interaction Class With Regions service | Data Distribution Management | implemented |
| `subscribeObjectClassAttributes` | §5.6 Subscribe Object Class Attributes service | Declaration Management | implemented |
| `subscribeObjectClassAttributesPassively` | §5.6 Subscribe Object Class Attributes service | Declaration Management | implemented |
| `subscribeObjectClassAttributesPassivelyWithRegions` | §9.8 Subscribe Object Class Attributes With Regions service | Data Distribution Management | implemented |
| `subscribeObjectClassAttributesWithRegions` | §9.8 Subscribe Object Class Attributes With Regions service | Data Distribution Management | implemented |
| `synchronizationPointAchieved` | §4.14 Synchronization Point Achieved service | Federation Management | implemented |
| `timeAdvanceRequest` | §8.8 Time Advance Request service | Time Management | implemented |
| `timeAdvanceRequestAvailable` | §8.9 Time Advance Request Available service | Time Management | implemented |
| `unassociateRegionsForUpdates` | §9.7 Unassociate Regions For Updates service | Data Distribution Management | implemented |
| `unconditionalAttributeOwnershipDivestiture` | §7.2 Unconditional Attribute Ownership Divestiture service | Ownership Management | implemented |
| `unpublishInteractionClass` | §5.5 Unpublish Interaction Class service | Declaration Management | implemented |
| `unpublishObjectClass` | §5.3 Unpublish Object Class Attributes service | Declaration Management | implemented |
| `unpublishObjectClassAttributes` | §5.3 Unpublish Object Class Attributes service | Declaration Management | implemented |
| `unsubscribeInteractionClass` | §5.9 Unsubscribe Interaction Class service | Declaration Management | implemented |
| `unsubscribeInteractionClassWithRegions` | §9.11 Unsubscribe Interaction Class With Regions service | Data Distribution Management | implemented |
| `unsubscribeObjectClass` | §5.7 Unsubscribe Object Class Attributes service | Declaration Management | implemented |
| `unsubscribeObjectClassAttributes` | §5.7 Unsubscribe Object Class Attributes service | Declaration Management | implemented |
| `unsubscribeObjectClassAttributesWithRegions` | §9.9 Unsubscribe Object Class Attributes With Regions service | Data Distribution Management | implemented |
| `updateAttributeValues` | §6.10 Update Attribute Values service | Object Management | implemented |

## FederateAmbassador callback traceability
| Callback | Section | Service group |
|---|---|---|
| `announceSynchronizationPoint` | §4.13 Announce Synchronization Point service | Federation Management |
| `attributeIsNotOwned` | §7.18 Inform Attribute Ownership service | Ownership Management |
| `attributeIsOwnedByRTI` | §7.18 Inform Attribute Ownership service | Ownership Management |
| `attributeOwnershipAcquisitionNotification` | §7.7 Attribute Ownership Acquisition Notification service | Ownership Management |
| `attributeOwnershipUnavailable` | §7.10 Attribute Ownership Unavailable service | Ownership Management |
| `attributesInScope` | §6.17 Attributes In Scope service | Object Management |
| `attributesOutOfScope` | §6.18 Attributes Out Of Scope service | Object Management |
| `confirmAttributeOwnershipAcquisitionCancellation` | §7.16 Confirm Attribute Ownership Acquisition Cancellation service | Ownership Management |
| `confirmAttributeTransportationTypeChange` | §6.24 Confirm Attribute Transportation Type Change service | Object Management |
| `confirmInteractionTransportationTypeChange` | §6.28 Confirm Interaction Transportation Type Change service | Object Management |
| `connectionLost` | §4.4 Connection Lost service | Federation Management |
| `discoverObjectInstance` | §6.9 Discover Object Instance service | Object Management |
| `federationNotRestored` | §4.29 Federation Restored service | Federation Management |
| `federationNotSaved` | §4.20 Federation Saved service | Federation Management |
| `federationRestoreBegun` | §4.26 Federation Restore Begun service | Federation Management |
| `federationRestoreStatusResponse` | §4.32 Federation Restore Status Response service | Federation Management |
| `federationRestored` | §4.29 Federation Restored service | Federation Management |
| `federationSaveStatusResponse` | §4.23 Federation Save Status Response service | Federation Management |
| `federationSaved` | §4.20 Federation Saved service | Federation Management |
| `federationSynchronized` | §4.15 Federation Synchronized service | Federation Management |
| `getProducingFederate` | §6.9 Discover Object Instance service | Object Management |
| `getSentRegions` | §6.9 Discover Object Instance service | Object Management |
| `hasProducingFederate` | §6.9 Discover Object Instance service | Object Management |
| `hasSentRegions` | §6.9 Discover Object Instance service | Object Management |
| `informAttributeOwnership` | §7.18 Inform Attribute Ownership service | Ownership Management |
| `initiateFederateRestore` | §4.27 Initiate Federate Restore service | Federation Management |
| `initiateFederateSave` | §4.17 Initiate Federate Save service | Federation Management |
| `multipleObjectInstanceNameReservationFailed` | §6.6 Multiple Object Instance Names Reserved service | Object Management |
| `multipleObjectInstanceNameReservationSucceeded` | §6.6 Multiple Object Instance Names Reserved service | Object Management |
| `objectInstanceNameReservationFailed` | §6.3 Object Instance Name Reserved service | Object Management |
| `objectInstanceNameReservationSucceeded` | §6.3 Object Instance Name Reserved service | Object Management |
| `provideAttributeValueUpdate` | §6.20 Provide Attribute Value Update service | Object Management |
| `receiveInteraction` | §6.13 Receive Interaction service | Object Management |
| `reflectAttributeValues` | §6.11 Reflect Attribute Values service | Object Management |
| `removeObjectInstance` | §6.15 Remove Object Instance service | Object Management |
| `reportAttributeTransportationType` | §6.26 Report Attribute Transportation Type service | Object Management |
| `reportFederationExecutions` | §4.8 Report Federation Executions service | Federation Management |
| `reportInteractionTransportationType` | §6.30 Report Interaction Transportation Type service | Object Management |
| `requestAttributeOwnershipAssumption` | §7.4 Request Attribute Ownership Assumption service | Ownership Management |
| `requestAttributeOwnershipRelease` | §7.11 Request Attribute Ownership Release service | Ownership Management |
| `requestDivestitureConfirmation` | §7.5 Request Divestiture Confirmation service | Ownership Management |
| `requestFederationRestoreFailed` | §4.25 Confirm Federation Restoration Request service | Federation Management |
| `requestFederationRestoreSucceeded` | §4.25 Confirm Federation Restoration Request service | Federation Management |
| `requestRetraction` | §8.22 Request Retraction service | Time Management |
| `startRegistrationForObjectClass` | §5.10 Start Registration For Object Class service | Declaration Management |
| `stopRegistrationForObjectClass` | §5.11 Stop Registration For Object Class service | Declaration Management |
| `synchronizationPointRegistrationFailed` | §4.12 Confirm Synchronization Point Registration service | Federation Management |
| `synchronizationPointRegistrationSucceeded` | §4.12 Confirm Synchronization Point Registration service | Federation Management |
| `timeAdvanceGrant` | §8.13 Time Advance Grant service | Time Management |
| `timeConstrainedEnabled` | §8.6 Time Constrained Enabled service | Time Management |
| `timeRegulationEnabled` | §8.3 Time Regulation Enabled service | Time Management |
| `turnInteractionsOff` | §5.13 Turn Interactions Off service | Declaration Management |
| `turnInteractionsOn` | §5.12 Turn Interactions On service | Declaration Management |
| `turnUpdatesOffForObjectInstance` | §6.22 Turn Updates Off For Object Instance service | Object Management |
| `turnUpdatesOnForObjectInstance` | §6.21 Turn Updates On For Object Instance service | Object Management |

## Current implementation boundary

The pure Python RTI now provides a callable implementation for every generated RTIambassador method name. Several areas, especially ownership, save/restore, DDM, and time management, are intentionally simple in-memory behaviors suitable for local simulation and adapter development. Full distributed RTI semantics, complete ordering guarantees, persistence, MOM coverage, security, and formal conformance testing remain future work.
