# HLA 1516.1-2025 Python source trace

This file ties the Python protocol package back to the Java and C++ API source files used in the build.

Primary source bundle: `1516-2025_API_XML_2025_08_14`.

- Java root: `java/hla/rti1516_2025`
- C++ root: `cpp/RTI`
- XML/MIM root: `xml/HLAstandardMIM-2025.xml`

### RTIambassador

| Python method | Java section(s) | Java overloads | C++ overloads | Source files | Java throws summary |
|---|---:|---:|---:|---|---|
| `abortFederationRestore` | §4.33 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreNotInProgress |
| `abortFederationSave` | §4.24 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, SaveNotInProgress |
| `associateRegionsForUpdates` | §9.6 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, NotConnected, ObjectInstanceNotKnown; … |
| `attributeOwnershipAcquisition` | §7.8 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotPublished, FederateNotExecutionMember, FederateOwnsAttributes, NotConnected, ObjectClassNotPublished; … |
| `attributeOwnershipAcquisitionIfAvailable` | §7.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeAlreadyBeingAcquired, AttributeNotDefined, AttributeNotPublished, FederateNotExecutionMember, FederateOwnsAttributes, NotConnected; … |
| `attributeOwnershipDivestitureIfWanted` | §7.13 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError; … |
| `attributeOwnershipReleaseDenied` | §7.12 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError; … |
| `cancelAttributeOwnershipAcquisition` | §7.15 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeAcquisitionWasNotRequested, AttributeAlreadyOwned, AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown; … |
| `cancelNegotiatedAttributeOwnershipDivestiture` | §7.14 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeDivestitureWasNotRequested, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown; … |
| `changeAttributeOrderType` | §8.24 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError; … |
| `changeDefaultAttributeOrderType` | §8.25 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `changeDefaultAttributeTransportationType` | §6.27 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidTransportationTypeHandle, NotConnected, ObjectClassNotDefined, RTIinternalError; … |
| `changeInteractionOrderType` | §8.26 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, NotConnected, RTIinternalError, RestoreInProgress; … |
| `commitRegionModifications` | §9.3 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate, RestoreInProgress; … |
| `confirmDivestiture` | §7.6 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeDivestitureWasNotRequested, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NoAcquisitionPending, NotConnected; … |
| `connect` | §4.2 | 4 | 4 | `RTIambassador.java`, `RTIambassador.h` | AlreadyConnected, CallNotAllowedFromWithinCallback, ConnectionFailed, InvalidCredentials, RTIinternalError, Unauthorized; … |
| `createFederationExecution` | §4.5 | 4 | 2 | `RTIambassador.java`, `RTIambassador.h` | CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM, ErrorReadingFOM, FederationExecutionAlreadyExists, InconsistentFOM, InvalidFOM; … |
| `createFederationExecutionWithMIM` | §4.5 | 2 | 1 | `RTIambassador.java`, `RTIambassador.h` | CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM, CouldNotOpenMIM, DesignatorIsHLAstandardMIM, ErrorReadingFOM, ErrorReadingMIM; … |
| `createRegion` | §9.2 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidDimensionHandle, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `decodeAttributeHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeDimensionHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeFederateHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeInteractionClassHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeMessageRetractionHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeObjectClassHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeObjectInstanceHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeParameterHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `decodeRegionHandle` |  | 0 | 1 | `RTIambassador.h` |  |
| `deleteObjectInstance` | §6.16 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | DeletePrivilegeNotHeld, FederateNotExecutionMember, InvalidLogicalTime, NotConnected, ObjectInstanceNotKnown, RTIinternalError; … |
| `deleteRegion` | §9.4 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RegionInUseForUpdateOrSubscription, RegionNotCreatedByThisFederate; … |
| `destroyFederationExecution` | §4.6 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederatesCurrentlyJoined, FederationExecutionDoesNotExist, NotConnected, RTIinternalError, Unauthorized |
| `disableAsynchronousDelivery` | §8.16 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AsynchronousDeliveryAlreadyDisabled, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `disableCallbacks` | §10.60 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | RTIinternalError, RestoreInProgress, SaveInProgress |
| `disableTimeConstrained` | §8.7 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeConstrainedIsNotEnabled |
| `disableTimeRegulation` | §8.4 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeRegulationIsNotEnabled |
| `disconnect` | §4.3 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | CallNotAllowedFromWithinCallback, FederateIsExecutionMember, RTIinternalError |
| `enableAsynchronousDelivery` | §8.15 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AsynchronousDeliveryAlreadyEnabled, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `enableCallbacks` | §10.59 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | RTIinternalError, RestoreInProgress, SaveInProgress |
| `enableTimeConstrained` | §8.5 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, NotConnected, RTIinternalError, RequestForTimeConstrainedPending, RestoreInProgress; … |
| `enableTimeRegulation` | §8.2 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLookahead, NotConnected, RTIinternalError, RequestForTimeRegulationPending; … |
| `evokeCallback` | §10.57 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | CallNotAllowedFromWithinCallback, RTIinternalError |
| `evokeMultipleCallbacks` | §10.58 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | CallNotAllowedFromWithinCallback, RTIinternalError |
| `federateRestoreComplete` | §4.31 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreNotRequested, SaveInProgress |
| `federateRestoreNotComplete` | §4.31 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreNotRequested, SaveInProgress |
| `federateSaveBegun` | §4.21 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveNotInitiated |
| `federateSaveComplete` | §4.22 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateHasNotBegunSave, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress |
| `federateSaveNotComplete` | §4.22 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateHasNotBegunSave, FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress |
| `flushQueueRequest` | §8.12 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError; … |
| `getAdvisoriesUseKnownClassSwitch` | §10.54 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getAllowRelaxedDDMSwitch` | §10.55 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getAttributeHandle` | §10.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidObjectClassHandle, NameNotFound, NotConnected, RTIinternalError |
| `getAttributeHandleFactory` | §10.60 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAttributeHandleSetFactory` | §10.60 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAttributeHandleValueMapFactory` | §10.60 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAttributeName` | §10.10 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidAttributeHandle, InvalidObjectClassHandle, NotConnected, RTIinternalError |
| `getAttributeRelevanceAdvisorySwitch` | §10.36 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getAttributeScopeAdvisorySwitch` | §10.38 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getAttributeSetRegionSetPairListFactory` | §10.60 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getAutoProvideSwitch` | §10.52 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getAutomaticResignDirective` | §10.44 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getAvailableDimensionsForInteractionClass` | §10.22 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidInteractionClassHandle, NotConnected, RTIinternalError |
| `getAvailableDimensionsForObjectClass` | §10.21 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidObjectClassHandle, NotConnected, RTIinternalError |
| `getConveyRegionDesignatorSetsSwitch` | §10.42 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getDelaySubscriptionEvaluationSwitch` | §10.53 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getDimensionHandle` | §10.23 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError |
| `getDimensionHandleFactory` | §10.60 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getDimensionHandleSet` | §10.26 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getDimensionHandleSetFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getDimensionName` | §10.24 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidDimensionHandle, NotConnected, RTIinternalError |
| `getDimensionUpperBound` | §10.25 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidDimensionHandle, NotConnected, RTIinternalError |
| `getExceptionReportingSwitch` | §10.48 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getFederateHandle` | §10.2 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError |
| `getFederateHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getFederateHandleSetFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getFederateName` | §10.3 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateHandleNotKnown, FederateNotExecutionMember, InvalidFederateHandle, NotConnected, RTIinternalError |
| `getHLAversion` |  | 1 | 0 | `RTIambassador.java` |  |
| `getInteractionClassHandle` | §10.13 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError |
| `getInteractionClassHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getInteractionClassHandleSetFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getInteractionClassName` | §10.14 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidInteractionClassHandle, NotConnected, RTIinternalError |
| `getInteractionRelevanceAdvisorySwitch` | §10.40 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getKnownObjectClassHandle` | §10.6 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError |
| `getMessageRetractionHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getNonRegulatedGrantSwitch` | §10.56 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getObjectClassHandle` | §10.4 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NameNotFound, NotConnected, RTIinternalError |
| `getObjectClassHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getObjectClassName` | §10.5 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidObjectClassHandle, NotConnected, RTIinternalError |
| `getObjectClassRelevanceAdvisorySwitch` | §10.34 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getObjectInstanceHandle` | §10.7 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError |
| `getObjectInstanceHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getObjectInstanceName` | §10.8 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError |
| `getOrderName` | §10.18 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidOrderType, NotConnected, RTIinternalError |
| `getOrderType` | §10.17 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidOrderName, NotConnected, RTIinternalError |
| `getParameterHandle` | §10.15 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidInteractionClassHandle, NameNotFound, NotConnected, RTIinternalError |
| `getParameterHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getParameterHandleValueMapFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getParameterName` | §10.16 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionParameterNotDefined, InvalidInteractionClassHandle, InvalidParameterHandle, NotConnected, RTIinternalError |
| `getRangeBounds` | §10.27 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidRegion, NotConnected, RTIinternalError, RegionDoesNotContainSpecifiedDimension, RestoreInProgress; … |
| `getRegionHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getRegionHandleSetFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getSendServiceReportsToFileSwitch` | §10.50 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getServiceReportingSwitch` | §10.46 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `getTimeFactory` |  | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected |
| `getTransportationTypeHandle` | §10.19 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidTransportationName, NotConnected, RTIinternalError |
| `getTransportationTypeHandleFactory` |  | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, NotConnected |
| `getTransportationTypeName` | §10.20 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidTransportationTypeHandle, NotConnected, RTIinternalError |
| `getUpdateRateValue` | §10.11 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidUpdateRateDesignator, NotConnected, RTIinternalError |
| `getUpdateRateValueForAttribute` | §10.12 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError |
| `isAttributeOwnedByFederate` | §7.19 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress; … |
| `joinFederationExecution` | §4.11 | 4 | 2 | `RTIambassador.java`, `RTIambassador.h` | CallNotAllowedFromWithinCallback, CouldNotCreateLogicalTimeFactory, CouldNotOpenFOM, ErrorReadingFOM, FederateAlreadyExecutionMember, FederateNameAlreadyInUse; … |
| `listFederationExecutionMembers` | §4.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | NotConnected, RTIinternalError |
| `listFederationExecutions` | §4.7 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | NotConnected, RTIinternalError |
| `localDeleteObjectInstance` | §6.18 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, FederateOwnsAttributes, NotConnected, ObjectInstanceNotKnown, OwnershipAcquisitionPending, RTIinternalError; … |
| `modifyLookahead` | §8.20 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLookahead, NotConnected, RTIinternalError, RestoreInProgress; … |
| `negotiatedAttributeOwnershipDivestiture` | §7.3 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeAlreadyBeingDivested, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown; … |
| `nextMessageRequest` | §8.10 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError; … |
| `nextMessageRequestAvailable` | §8.11 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError; … |
| `normalizeFederateHandle` | §10.30 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidFederateHandle, NotConnected, RTIinternalError |
| `normalizeInteractionClassHandle` | §10.32 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidInteractionClassHandle, NotConnected, RTIinternalError |
| `normalizeObjectClassHandle` | §10.31 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidObjectClassHandle, NotConnected, RTIinternalError |
| `normalizeObjectInstanceHandle` | §10.33 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidObjectInstanceHandle, NotConnected, RTIinternalError |
| `normalizeServiceGroup` | §10.29 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidServiceGroup, NotConnected, RTIinternalError |
| `publishInteractionClass` | §5.4 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `publishObjectClassAttributes` | §5.2 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `publishObjectClassDirectedInteractions` | §5.6 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `queryAttributeOwnership` | §7.17 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress; … |
| `queryAttributeTransportationType` | §6.28 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError, RestoreInProgress; … |
| `queryFederationRestoreStatus` | §4.34 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, SaveInProgress |
| `queryFederationSaveStatus` | §4.25 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress |
| `queryGALT` | §8.17 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `queryInteractionTransportationType` | §6.32 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `queryLITS` | §8.19 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `queryLogicalTime` | §8.18 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `queryLookahead` | §8.21 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, TimeRegulationIsNotEnabled |
| `registerFederationSynchronizationPoint` | §4.14 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidFederateHandle, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `registerObjectInstance` | §6.8 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, ObjectClassNotPublished, ObjectInstanceNameInUse, ObjectInstanceNameNotReserved; … |
| `registerObjectInstanceWithRegions` | §9.5 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotPublished, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, NotConnected; … |
| `releaseMultipleObjectInstanceNames` | §6.7 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectInstanceNameNotReserved, RTIinternalError, RestoreInProgress, SaveInProgress |
| `releaseObjectInstanceName` | §6.4 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectInstanceNameNotReserved, RTIinternalError, RestoreInProgress, SaveInProgress |
| `requestAttributeTransportationTypeChange` | §6.25 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeAlreadyBeingChanged, AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, InvalidTransportationTypeHandle, NotConnected; … |
| `requestAttributeValueUpdate` | §6.21 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, ObjectInstanceNotKnown, RTIinternalError; … |
| `requestAttributeValueUpdateWithRegions` | §9.13 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, NotConnected, ObjectClassNotDefined; … |
| `requestFederationRestore` | §4.27 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `requestFederationSave` | §4.19 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, FederateUnableToUseTime, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError; … |
| `requestInteractionTransportationTypeChange` | §6.30 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassAlreadyBeingChanged, InteractionClassNotDefined, InteractionClassNotPublished, InvalidTransportationTypeHandle, NotConnected; … |
| `reserveMultipleObjectInstanceNames` | §6.5 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, IllegalName, NameSetWasEmpty, NotConnected, RTIinternalError, RestoreInProgress; … |
| `reserveObjectInstanceName` | §6.2 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, IllegalName, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `resignFederationExecution` | §4.12 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | CallNotAllowedFromWithinCallback, FederateNotExecutionMember, FederateOwnsAttributes, InvalidResignAction, NotConnected, OwnershipAcquisitionPending; … |
| `retract` | §8.22 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidMessageRetractionHandle, MessageCanNoLongerBeRetracted, NotConnected, RTIinternalError, RestoreInProgress; … |
| `sendDirectedInteraction` | §6.14 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, InteractionParameterNotDefined, InvalidLogicalTime, NotConnected; … |
| `sendInteraction` | §6.12 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, InteractionParameterNotDefined, InvalidLogicalTime, NotConnected; … |
| `sendInteractionWithRegions` | §9.12 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, InteractionClassNotPublished, InteractionParameterNotDefined, InvalidLogicalTime, InvalidRegion; … |
| `setAttributeRelevanceAdvisorySwitch` | §10.37 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setAttributeScopeAdvisorySwitch` | §10.39 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setAutomaticResignDirective` | §10.45 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setConveyRegionDesignatorSetsSwitch` | §10.43 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setExceptionReportingSwitch` | §10.49 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setInteractionRelevanceAdvisorySwitch` | §10.41 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setObjectClassRelevanceAdvisorySwitch` | §10.35 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setRangeBounds` | §10.28 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InvalidRangeBound, InvalidRegion, NotConnected, RTIinternalError, RegionDoesNotContainSpecifiedDimension; … |
| `setSendServiceReportsToFileSwitch` | §10.51 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `setServiceReportingSwitch` | §10.47 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, ReportServiceInvocationsAreSubscribed, RestoreInProgress, SaveInProgress |
| `subscribeInteractionClass` | §5.10 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress; … |
| `subscribeInteractionClassPassively` | §5.10 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress; … |
| `subscribeInteractionClassPassivelyWithRegions` | §9.10 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, InvalidRegion, InvalidRegionContext, NotConnected; … |
| `subscribeInteractionClassWithRegions` | §9.10 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, FederateServiceInvocationsAreBeingReportedViaMOM, InteractionClassNotDefined, InvalidRegion, InvalidRegionContext, NotConnected; … |
| `subscribeObjectClassAttributes` | §5.8 | 2 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidUpdateRateDesignator, NotConnected, ObjectClassNotDefined, RTIinternalError; … |
| `subscribeObjectClassAttributesPassively` | §5.8 | 2 | 0 | `RTIambassador.java` | AttributeNotDefined, FederateNotExecutionMember, InvalidUpdateRateDesignator, NotConnected, ObjectClassNotDefined, RTIinternalError; … |
| `subscribeObjectClassAttributesPassivelyWithRegions` | §9.8 | 2 | 0 | `RTIambassador.java` | AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, InvalidUpdateRateDesignator, NotConnected; … |
| `subscribeObjectClassAttributesWithRegions` | §9.8 | 2 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, InvalidRegionContext, InvalidUpdateRateDesignator, NotConnected; … |
| `subscribeObjectClassDirectedInteractions` | §5.12 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `subscribeObjectClassDirectedInteractionsUniversally` | §5.12 | 1 | 0 | `RTIambassador.java` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `synchronizationPointAchieved` | §4.17 | 2 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress, SynchronizationPointLabelNotAnnounced |
| `timeAdvanceRequest` | §8.8 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError; … |
| `timeAdvanceRequestAvailable` | §8.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InTimeAdvancingState, InvalidLogicalTime, LogicalTimeAlreadyPassed, NotConnected, RTIinternalError; … |
| `unassociateRegionsForUpdates` | §9.7 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, NotConnected, ObjectInstanceNotKnown, RTIinternalError; … |
| `unconditionalAttributeOwnershipDivestiture` | §7.2 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, NotConnected, ObjectInstanceNotKnown, RTIinternalError; … |
| `unpublishInteractionClass` | §5.5 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `unpublishObjectClass` | §5.3 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, OwnershipAcquisitionPending, RTIinternalError, RestoreInProgress; … |
| `unpublishObjectClassAttributes` | §5.3 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, OwnershipAcquisitionPending, RTIinternalError; … |
| `unpublishObjectClassDirectedInteractions` | §5.7 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `unsubscribeInteractionClass` | §5.11 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, RTIinternalError, RestoreInProgress, SaveInProgress |
| `unsubscribeInteractionClassWithRegions` | §9.11 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, InvalidRegion, NotConnected, RTIinternalError, RegionNotCreatedByThisFederate; … |
| `unsubscribeObjectClass` | §5.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress, SaveInProgress |
| `unsubscribeObjectClassAttributes` | §5.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `unsubscribeObjectClassAttributesWithRegions` | §9.9 | 1 | 1 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, FederateNotExecutionMember, InvalidRegion, NotConnected, ObjectClassNotDefined, RTIinternalError; … |
| `unsubscribeObjectClassDirectedInteractions` | §5.13 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | FederateNotExecutionMember, InteractionClassNotDefined, NotConnected, ObjectClassNotDefined, RTIinternalError, RestoreInProgress; … |
| `updateAttributeValues` | §6.10 | 2 | 2 | `RTIambassador.java`, `RTIambassador.h` | AttributeNotDefined, AttributeNotOwned, FederateNotExecutionMember, InvalidLogicalTime, NotConnected, ObjectInstanceNotKnown; … |

### FederateAmbassador

| Python method | Java section(s) | Java overloads | C++ overloads | Source files | Java throws summary |
|---|---:|---:|---:|---|---|
| `announceSynchronizationPoint` | §4.16 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `attributeIsNotOwned` | §7.18 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `attributeIsOwnedByRTI` | §7.18 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `attributeOwnershipAcquisitionNotification` | §7.7 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `attributeOwnershipUnavailable` | §7.10 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `attributesInScope` | §6.19 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `attributesOutOfScope` | §6.20 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `confirmAttributeOwnershipAcquisitionCancellation` | §7.16 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `confirmAttributeTransportationTypeChange` | §6.26 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `confirmInteractionTransportationTypeChange` | §6.31 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `connectionLost` | §4.4 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `discoverObjectInstance` | §6.9 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federateResigned` | §4.13 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationNotRestored` | §4.29 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationNotSaved` | §4.23 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationRestoreBegun` | §4.29 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationRestoreStatusResponse` | §4.35 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationRestored` | §4.32 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationSaveStatusResponse` | §4.26 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationSaved` | §4.23 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `federationSynchronized` | §4.18 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `flushQueueGrant` | §8.13 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `informAttributeOwnership` | §7.18 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `initiateFederateRestore` | §4.30 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `initiateFederateSave` | §4.20 | 2 | 2 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `multipleObjectInstanceNameReservationFailed` | §6.6 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `multipleObjectInstanceNameReservationSucceeded` | §6.6 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `objectInstanceNameReservationFailed` | §6.3 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `objectInstanceNameReservationSucceeded` | §6.3 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `provideAttributeValueUpdate` | §6.22 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `receiveDirectedInteraction` | §6.15 | 2 | 2 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `receiveInteraction` | §6.13 | 2 | 2 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `reflectAttributeValues` | §6.11 | 2 | 2 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `removeObjectInstance` | §6.17 | 2 | 2 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `reportAttributeTransportationType` | §6.29 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `reportFederationExecutionDoesNotExist` | §4.10 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `reportFederationExecutionMembers` | §4.10 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `reportFederationExecutions` | §4.8 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `reportInteractionTransportationType` | §6.33 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `requestAttributeOwnershipAssumption` | §7.4 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `requestAttributeOwnershipRelease` | §7.11 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `requestDivestitureConfirmation` | §7.5 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `requestFederationRestoreFailed` | §4.28 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `requestFederationRestoreSucceeded` | §4.28 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `requestRetraction` | §8.23 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `startRegistrationForObjectClass` | §5.14 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `stopRegistrationForObjectClass` | §5.15 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `synchronizationPointRegistrationFailed` | §4.15 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `synchronizationPointRegistrationSucceeded` | §4.15 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `timeAdvanceGrant` | §8.14 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `timeConstrainedEnabled` | §8.6 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `timeRegulationEnabled` | §8.3 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `turnInteractionsOff` | §5.17 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `turnInteractionsOn` | §5.16 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `turnUpdatesOffForObjectInstance` | §6.24 | 1 | 1 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |
| `turnUpdatesOnForObjectInstance` | §6.23 | 2 | 2 | `FederateAmbassador.java`, `FederateAmbassador.h` | FederateInternalError |

## Encoding/auth/package notes

- `encoding.py` is sourced from Java `encoding/*.java`, C++ `RTI/encoding/*.h`, and `HLAstandardMIM-2025.xml` for `HLAtransportationTypeHandle`.
- `auth.py` is sourced from Java `auth/*.java` and C++ `RTI/auth/*.h`.
- `exceptions.py` is sourced from Java `exceptions/*.java` and C++ `RTI/Exception.h`.
