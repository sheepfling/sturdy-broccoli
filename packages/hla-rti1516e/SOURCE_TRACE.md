# HLA 1516.1-2010 Python source trace

This file ties the Python protocol package back to the Java and C++ API source files used in the build.

Primary source bundles:

- Java root: `java/src/hla/rti1516e` from `IEEE1516-2010_Java_API.zip`
- C++ root: `cpp/src/RTI` from `IEEE1516-2010_C++_API.zip`
- FDD/MIM/WSDL context: `IEEE1516-FDD-2010.xsd`, `HLAstandardMIM.xml`, `hla1516e.wsdl`
- OMT/DIF context: `IEEE1516-OMT-2010.xsd`, `IEEE1516-DIF-2010.xsd`

### RTIambassador

| Python method | Section(s) | Java overloads | C++ overloads | Source files | Java throws summary |
|---|---:|---:|---:|---|---|
| `connect` | §4.2 | 2 | 1 | `RTIambassador.java, RTIambassador.h` | ConnectionFailed, InvalidLocalSettingsDesignator, UnsupportedCallbackModel, AlreadyConnected, CallNotAllowedFromWithinCallback, RTIinternalError |
| `disconnect` | §4.3 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateIsExecutionMember, CallNotAllowedFromWithinCallback, RTIinternalError |
| `createFederationExecution` | §4.5 | 5 | 2 | `RTIambassador.java, RTIambassador.h` | CouldNotCreateLogicalTimeFactory, InconsistentFDD, ErrorReadingFDD, CouldNotOpenFDD, ErrorReadingMIM, CouldNotOpenMIM; … |
| `destroyFederationExecution` | §4.6 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederatesCurrentlyJoined, FederationExecutionDoesNotExist, NotConnected, RTIinternalError |
| `listFederationExecutions` | §4.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NotConnected, RTIinternalError |
| `joinFederationExecution` | §4.9 | 4 | 2 | `RTIambassador.java, RTIambassador.h` | CouldNotCreateLogicalTimeFactory, FederateNameAlreadyInUse, FederationExecutionDoesNotExist, InconsistentFDD, ErrorReadingFDD, CouldNotOpenFDD; … |
| `resignFederationExecution` | §4.10 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidResignAction, OwnershipAcquisitionPending, FederateOwnsAttributes, FederateNotExecutionMember, NotConnected, CallNotAllowedFromWithinCallback; … |
| `registerFederationSynchronizationPoint` | §4.11 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError, InvalidFederateHandle |
| `synchronizationPointAchieved` | §4.14 | 2 | 1 | `RTIambassador.java, RTIambassador.h` | SynchronizationPointLabelNotAnnounced, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `requestFederationSave` | §4.16 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError, LogicalTimeAlreadyPassed; … |
| `federateSaveBegun` | §4.18 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveNotInitiated, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `federateSaveComplete` | §4.19 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateHasNotBegunSave, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `federateSaveNotComplete` | §4.19 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateHasNotBegunSave, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `abortFederationSave` | §4.21 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveNotInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `queryFederationSaveStatus` | §4.22 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `requestFederationRestore` | §4.24 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `federateRestoreComplete` | §4.28 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RestoreNotRequested, SaveInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `federateRestoreNotComplete` | §4.28 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RestoreNotRequested, SaveInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `abortFederationRestore` | §4.30 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RestoreNotInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `queryFederationRestoreStatus` | §4.31 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `publishObjectClassAttributes` | §5.2 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `unpublishObjectClass` | §5.3 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | OwnershipAcquisitionPending, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `unpublishObjectClassAttributes` | §5.3 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | OwnershipAcquisitionPending, AttributeNotDefined, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `publishInteractionClass` | §5.4 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `unpublishInteractionClass` | §5.5 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `subscribeObjectClassAttributes` | §5.6 | 2 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `subscribeObjectClassAttributesPassively` | §5.6 | 2 | 0 | `RTIambassador.java` | AttributeNotDefined, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `unsubscribeObjectClass` | §5.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `unsubscribeObjectClassAttributes` | §5.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `subscribeInteractionClass` | §5.8 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `subscribeInteractionClassPassively` | §5.8 | 1 | 0 | `RTIambassador.java` | FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `unsubscribeInteractionClass` | §5.9 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `reserveObjectInstanceName` | §6.2 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | IllegalName, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `releaseObjectInstanceName` | §6.4 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectInstanceNameNotReserved, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `reserveMultipleObjectInstanceName` | §6.5 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | IllegalName, NameSetWasEmpty, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `releaseMultipleObjectInstanceName` | §6.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectInstanceNameNotReserved, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `registerObjectInstance` | §6.8 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | ObjectClassNotPublished, ObjectClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `updateAttributeValues` | §6.10 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `sendInteraction` | §6.12 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | InteractionClassNotPublished, InteractionParameterNotDefined, InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `deleteObjectInstance` | §6.14 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | DeletePrivilegeNotHeld, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `localDeleteObjectInstance` | §6.16 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | OwnershipAcquisitionPending, FederateOwnsAttributes, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `requestAttributeValueUpdate` | §6.19 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `requestAttributeTransportationTypeChange` | §6.23 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeAlreadyBeingChanged, AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, InvalidTransportationType, SaveInProgress; … |
| `queryAttributeTransportationType` | §6.25 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `requestInteractionTransportationTypeChange` | §6.27 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionClassAlreadyBeingChanged, InteractionClassNotPublished, InteractionClassNotDefined, InvalidTransportationType, SaveInProgress, RestoreInProgress; … |
| `queryInteractionTransportationType` | §6.29 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `unconditionalAttributeOwnershipDivestiture` | §7.2 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `negotiatedAttributeOwnershipDivestiture` | §7.3 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeAlreadyBeingDivested, AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress; … |
| `confirmDivestiture` | §7.6 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NoAcquisitionPending, AttributeDivestitureWasNotRequested, AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress; … |
| `attributeOwnershipAcquisition` | §7.8 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotPublished, ObjectClassNotPublished, FederateOwnsAttributes, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress; … |
| `attributeOwnershipAcquisitionIfAvailable` | §7.9 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeAlreadyBeingAcquired, AttributeNotPublished, ObjectClassNotPublished, FederateOwnsAttributes, AttributeNotDefined, ObjectInstanceNotKnown; … |
| `attributeOwnershipReleaseDenied` | §7.12 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `attributeOwnershipDivestitureIfWanted` | §7.13 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `cancelNegotiatedAttributeOwnershipDivestiture` | §7.14 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeDivestitureWasNotRequested, AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress; … |
| `cancelAttributeOwnershipAcquisition` | §7.15 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeAcquisitionWasNotRequested, AttributeAlreadyOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress; … |
| `queryAttributeOwnership` | §7.17 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `isAttributeOwnedByFederate` | §7.19 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `enableTimeRegulation` | §8.2 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidLookahead, InTimeAdvancingState, RequestForTimeRegulationPending, TimeRegulationAlreadyEnabled, SaveInProgress, RestoreInProgress; … |
| `disableTimeRegulation` | §8.4 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | TimeRegulationIsNotEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `enableTimeConstrained` | §8.5 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InTimeAdvancingState, RequestForTimeConstrainedPending, TimeConstrainedAlreadyEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `disableTimeConstrained` | §8.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | TimeConstrainedIsNotEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `timeAdvanceRequest` | §8.8 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | LogicalTimeAlreadyPassed, InvalidLogicalTime, InTimeAdvancingState, RequestForTimeRegulationPending, RequestForTimeConstrainedPending, SaveInProgress; … |
| `timeAdvanceRequestAvailable` | §8.9 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | LogicalTimeAlreadyPassed, InvalidLogicalTime, InTimeAdvancingState, RequestForTimeRegulationPending, RequestForTimeConstrainedPending, SaveInProgress; … |
| `nextMessageRequest` | §8.10 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | LogicalTimeAlreadyPassed, InvalidLogicalTime, InTimeAdvancingState, RequestForTimeRegulationPending, RequestForTimeConstrainedPending, SaveInProgress; … |
| `nextMessageRequestAvailable` | §8.11 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | LogicalTimeAlreadyPassed, InvalidLogicalTime, InTimeAdvancingState, RequestForTimeRegulationPending, RequestForTimeConstrainedPending, SaveInProgress; … |
| `flushQueueRequest` | §8.12 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | LogicalTimeAlreadyPassed, InvalidLogicalTime, InTimeAdvancingState, RequestForTimeRegulationPending, RequestForTimeConstrainedPending, SaveInProgress; … |
| `enableAsynchronousDelivery` | §8.14 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AsynchronousDeliveryAlreadyEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `disableAsynchronousDelivery` | §8.15 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AsynchronousDeliveryAlreadyDisabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `queryGALT` | §8.16 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `queryLogicalTime` | §8.17 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `queryLITS` | §8.18 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `modifyLookahead` | §8.19 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidLookahead, InTimeAdvancingState, TimeRegulationIsNotEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `queryLookahead` | §8.20 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | TimeRegulationIsNotEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `retract` | §8.21 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | MessageCanNoLongerBeRetracted, InvalidMessageRetractionHandle, TimeRegulationIsNotEnabled, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `changeAttributeOrderType` | §8.23 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotOwned, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `changeInteractionOrderType` | §8.24 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionClassNotPublished, InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `createRegion` | §9.2 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidDimensionHandle, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `commitRegionModifications` | §9.3 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RegionNotCreatedByThisFederate, InvalidRegion, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `deleteRegion` | §9.4 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RegionInUseForUpdateOrSubscription, RegionNotCreatedByThisFederate, InvalidRegion, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `registerObjectInstanceWithRegions` | §9.5 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotPublished, ObjectClassNotPublished, AttributeNotDefined; … |
| `associateRegionsForUpdates` | §9.6 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress; … |
| `unassociateRegionsForUpdates` | §9.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotDefined, ObjectInstanceNotKnown, SaveInProgress, RestoreInProgress; … |
| `subscribeObjectClassAttributesWithRegions` | §9.8 | 2 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotDefined, ObjectClassNotDefined, SaveInProgress; … |
| `subscribeObjectClassAttributesPassivelyWithRegions` | §9.8 | 2 | 0 | `RTIambassador.java` | InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotDefined, ObjectClassNotDefined, SaveInProgress; … |
| `unsubscribeObjectClassAttributesWithRegions` | §9.9 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotDefined, ObjectClassNotDefined, SaveInProgress, RestoreInProgress; … |
| `subscribeInteractionClassWithRegions` | §9.10 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateServiceInvocationsAreBeingReportedViaMOM, InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, InteractionClassNotDefined, SaveInProgress; … |
| `subscribeInteractionClassPassivelyWithRegions` | §9.10 | 1 | 0 | `RTIambassador.java` | FederateServiceInvocationsAreBeingReportedViaMOM, InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, InteractionClassNotDefined, SaveInProgress; … |
| `unsubscribeInteractionClassWithRegions` | §9.11 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RegionNotCreatedByThisFederate, InvalidRegion, InteractionClassNotDefined, SaveInProgress, RestoreInProgress, FederateNotExecutionMember; … |
| `sendInteractionWithRegions` | §9.12 | 2 | 2 | `RTIambassador.java, RTIambassador.h` | InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, InteractionClassNotPublished, InteractionParameterNotDefined, InteractionClassNotDefined; … |
| `requestAttributeValueUpdateWithRegions` | §9.13 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidRegionContext, RegionNotCreatedByThisFederate, InvalidRegion, AttributeNotDefined, ObjectClassNotDefined, SaveInProgress; … |
| `getAutomaticResignDirective` | §10.2 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError |
| `setAutomaticResignDirective` | §10.3 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidResignAction, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getFederateHandle` | §10.4 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NameNotFound, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getFederateName` | §10.5 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidFederateHandle, FederateHandleNotKnown, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getObjectClassHandle` | §10.6 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NameNotFound, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getObjectClassName` | §10.7 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidObjectClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getKnownObjectClassHandle` | §10.8 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectInstanceNotKnown, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getObjectInstanceHandle` | §10.9 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectInstanceNotKnown, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getObjectInstanceName` | §10.10 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectInstanceNotKnown, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getAttributeHandle` | §10.11 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NameNotFound, InvalidObjectClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getAttributeName` | §10.12 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, InvalidAttributeHandle, InvalidObjectClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getUpdateRateValue` | §10.13 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidUpdateRateDesignator, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getUpdateRateValueForAttribute` | §10.14 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectInstanceNotKnown, AttributeNotDefined, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getInteractionClassHandle` | §10.15 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NameNotFound, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getInteractionClassName` | §10.16 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidInteractionClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getParameterHandle` | §10.17 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NameNotFound, InvalidInteractionClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getParameterName` | §10.18 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionParameterNotDefined, InvalidParameterHandle, InvalidInteractionClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getOrderType` | §10.19 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidOrderName, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getOrderName` | §10.20 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidOrderType, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getTransportationTypeHandle` | §10.21 | 1 | 0 | `RTIambassador.java` | InvalidTransportationName, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getTransportationTypeName` | §10.22 | 1 | 0 | `RTIambassador.java` | InvalidTransportationType, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getAvailableDimensionsForClassAttribute` | §10.23 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeNotDefined, InvalidAttributeHandle, InvalidObjectClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getAvailableDimensionsForInteractionClass` | §10.24 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidInteractionClassHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getDimensionHandle` | §10.25 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | NameNotFound, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getDimensionName` | §10.26 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidDimensionHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getDimensionUpperBound` | §10.27 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidDimensionHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getDimensionHandleSet` | §10.28 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidRegion, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `getRangeBounds` | §10.29 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | RegionDoesNotContainSpecifiedDimension, InvalidRegion, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected; … |
| `setRangeBounds` | §10.30 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidRangeBound, RegionDoesNotContainSpecifiedDimension, RegionNotCreatedByThisFederate, InvalidRegion, SaveInProgress, RestoreInProgress; … |
| `normalizeFederateHandle` | §10.31 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidFederateHandle, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `normalizeServiceGroup` | §10.32 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InvalidServiceGroup, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `enableObjectClassRelevanceAdvisorySwitch` | §10.33 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectClassRelevanceAdvisorySwitchIsOn, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `disableObjectClassRelevanceAdvisorySwitch` | §10.34 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | ObjectClassRelevanceAdvisorySwitchIsOff, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `enableAttributeRelevanceAdvisorySwitch` | §10.35 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeRelevanceAdvisorySwitchIsOn, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `disableAttributeRelevanceAdvisorySwitch` | §10.36 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeRelevanceAdvisorySwitchIsOff, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `enableAttributeScopeAdvisorySwitch` | §10.37 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeScopeAdvisorySwitchIsOn, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `disableAttributeScopeAdvisorySwitch` | §10.38 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | AttributeScopeAdvisorySwitchIsOff, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `enableInteractionRelevanceAdvisorySwitch` | §10.39 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionRelevanceAdvisorySwitchIsOn, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `disableInteractionRelevanceAdvisorySwitch` | §10.40 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | InteractionRelevanceAdvisorySwitchIsOff, SaveInProgress, RestoreInProgress, FederateNotExecutionMember, NotConnected, RTIinternalError |
| `evokeCallback` | §10.41 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | CallNotAllowedFromWithinCallback, RTIinternalError |
| `evokeMultipleCallbacks` | §10.42 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | CallNotAllowedFromWithinCallback, RTIinternalError |
| `enableCallbacks` | §10.43 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, RTIinternalError |
| `disableCallbacks` | §10.44 | 1 | 1 | `RTIambassador.java, RTIambassador.h` | SaveInProgress, RestoreInProgress, RTIinternalError |
| `getAttributeHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAttributeHandleSetFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAttributeHandleValueMapFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAttributeSetRegionSetPairListFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getDimensionHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getDimensionHandleSetFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getFederateHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getFederateHandleSetFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getInteractionClassHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getObjectClassHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getObjectInstanceHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getParameterHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getParameterHandleValueMapFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getRegionHandleSetFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getTransportationTypeHandleFactory` | API-specific services | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getHLAversion` | API-specific services | 1 | 0 | `RTIambassador.java` |  |
| `getTimeFactory` | API-specific services | 1 | 1 | `RTIambassador.java, RTIambassador.h` | FederateNotExecutionMember, NotConnected |
| `createFederationExecutionWithMIM` | §4.5 | 0 | 1 | `RTIambassador.h` |  |
| `getTransportationType` | §10.21 | 0 | 1 | `RTIambassador.h` |  |
| `getTransportationName` | §10.22 | 0 | 1 | `RTIambassador.h` |  |
| `decodeFederateHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeObjectClassHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeInteractionClassHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeObjectInstanceHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeAttributeHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeParameterHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeDimensionHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeMessageRetractionHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |
| `decodeRegionHandle` | Decode handles | 0 | 1 | `RTIambassador.h` |  |

### FederateAmbassador

| Python method | Section(s) | Java overloads | C++ overloads | Source files | Java throws summary |
|---|---:|---:|---:|---|---|
| `connectionLost` | §4.4 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `reportFederationExecutions` | §4.8 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `synchronizationPointRegistrationSucceeded` | §4.12 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `synchronizationPointRegistrationFailed` | §4.12 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `announceSynchronizationPoint` | §4.13 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationSynchronized` | §4.15 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `initiateFederateSave` | §4.17 | 2 | 2 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationSaved` | §4.20 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationNotSaved` | §4.20 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationSaveStatusResponse` | §4.23 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `requestFederationRestoreSucceeded` | §4.25 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `requestFederationRestoreFailed` | §4.25 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationRestoreBegun` | §4.26 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `initiateFederateRestore` | §4.27 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationRestored` | §4.29 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationNotRestored` | §4.29 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `federationRestoreStatusResponse` | §4.32 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `startRegistrationForObjectClass` | §5.10 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `stopRegistrationForObjectClass` | §5.11 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `turnInteractionsOn` | §5.12 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `turnInteractionsOff` | §5.13 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `objectInstanceNameReservationSucceeded` | §6.3 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `objectInstanceNameReservationFailed` | §6.3 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `multipleObjectInstanceNameReservationSucceeded` | §6.6 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `multipleObjectInstanceNameReservationFailed` | §6.6 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `discoverObjectInstance` | §6.9 | 2 | 2 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `reflectAttributeValues` | §6.11 | 3 | 3 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `receiveInteraction` | §6.13 | 3 | 3 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `removeObjectInstance` | §6.15 | 3 | 3 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `attributesInScope` | §6.17 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `attributesOutOfScope` | §6.18 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `provideAttributeValueUpdate` | §6.20 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `turnUpdatesOnForObjectInstance` | §6.21 | 2 | 2 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `turnUpdatesOffForObjectInstance` | §6.22 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `confirmAttributeTransportationTypeChange` | §6.24 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `reportAttributeTransportationType` | §6.26 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `confirmInteractionTransportationTypeChange` | §6.28 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `reportInteractionTransportationType` | §6.30 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `requestAttributeOwnershipAssumption` | §7.4 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `requestDivestitureConfirmation` | §7.5 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `attributeOwnershipAcquisitionNotification` | §7.7 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `attributeOwnershipUnavailable` | §7.10 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `requestAttributeOwnershipRelease` | §7.11 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `confirmAttributeOwnershipAcquisitionCancellation` | §7.16 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `informAttributeOwnership` | §7.18 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `attributeIsNotOwned` | §7.18 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `attributeIsOwnedByRTI` | §7.18 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `timeRegulationEnabled` | §8.3 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `timeConstrainedEnabled` | §8.6 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `timeAdvanceGrant` | §8.13 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |
| `requestRetraction` | §8.22 | 1 | 1 | `FederateAmbassador.java, FederateAmbassador.h` | FederateInternalError |

### EncoderFactory

| Python method | Java overloads | Source files |
|---|---:|---|
| `createHLAASCIIchar` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAASCIIstring` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAboolean` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAbyte` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAvariantRecord` | 1 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAfixedRecord` | 1 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAfixedArray` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAfloat32BE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAfloat32LE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAfloat64BE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAfloat64LE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAinteger16BE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAinteger16LE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAinteger32BE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAinteger32LE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAinteger64BE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAinteger64LE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAoctet` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAoctetPairBE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAoctetPairLE` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAopaqueData` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAunicodeChar` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAunicodeString` | 2 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |
| `createHLAvariableArray` | 1 | `encoding/EncoderFactory.java`; C++ support types in `RTI/encoding/*.h` |

C++ encoding support protocols such as `DataElement`, `VariableLengthData`, and C++ collection operations are traced to `cpp/src/RTI/encoding/*.h`.

### Exceptions

- Java exception classes parsed: 110
- C++ exception macros parsed: 121
- Python exception classes emitted including `RTIexception`: 122

### Enums

- Java enums: `CallbackModel`, `OrderType`, `ResignAction`, `RestoreFailureReason`, `RestoreStatus`, `SaveFailureReason`, `SaveStatus`, `ServiceGroup`, `SynchronizationPointFailureReason`
- C++-only enum included: `TransportationType` from `RTI/Enums.h`
