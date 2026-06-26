# Java Interface Spec Mapping

Generated from source metadata. Do not edit by hand.
Regenerate with `python3 scripts/generate_java_interface_spec_mapping.py`.
Double-check with `./tools/java spec-map --check` or `bash scripts/ci/check_generated_docs.sh`.

This page is the deterministic cross-language mapping reference for the Java HLA surface used by the JPype and Py4J routes.

## Summary

- `RTIambassador` methods in 2010 metadata: `164`
- `FederateAmbassador` callbacks in 2010 metadata: `55`
- Java RTI overload rows mapped here: `172`
- Java callback overload rows mapped here: `70`
- Explicit deterministic overload rows: `23`
- Weighted-or-shape-selected overload rows: `20`
- Single-java-overload rows: `132`

## Route Policy Legend

- `explicit-deterministic`: this exact Java overload has an explicit router entry in the deterministic router table.
- `single-java-overload`: this method has only one Java overload in the source metadata, so no overload choice is required.
- `weighted-or-shape-selected`: multiple Java overloads exist, but this exact overload is not in the explicit deterministic table and therefore remains on the weighted/shape-selected path.
- `direct-callback-dispatch`: inbound Java callback shape is dispatched directly by callback name and converted by signature metadata.
- `no-java-overload`: the 2010 source metadata does not carry a Java overload row for this method.

## Source Authorities

- `packages/hla-rti1516e/src/hla/rti1516e/api_metadata.json` via `hla.rti1516e.raw_api.API_METADATA`
- `packages/hla-backend-common/src/hla/backends/common/invocation.py` deterministic router table
- `packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py`
- `packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py`

## RTIambassador

| Method | Group | Spec Ref | Java Params | Route Policy | 2025 Surface |
| --- | --- | --- | --- | --- | --- |
| `abortFederationRestore` | `Federation Management` | `4.30` | `(none)` | `single-java-overload` | `yes` |
| `abortFederationSave` | `Federation Management` | `4.21` | `(none)` | `single-java-overload` | `yes` |
| `associateRegionsForUpdates` | `Data Distribution Management` | `9.6` | `ObjectInstanceHandle theObject, AttributeSetRegionSetPairList attributesAndRegions` | `single-java-overload` | `yes` |
| `attributeOwnershipAcquisition` | `Ownership Management` | `7.8` | `ObjectInstanceHandle theObject, AttributeHandleSet desiredAttributes, byte[] userSuppliedTag` | `single-java-overload` | `yes` |
| `attributeOwnershipAcquisitionIfAvailable` | `Ownership Management` | `7.9` | `ObjectInstanceHandle theObject, AttributeHandleSet desiredAttributes` | `single-java-overload` | `yes` |
| `attributeOwnershipDivestitureIfWanted` | `Ownership Management` | `7.13` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `single-java-overload` | `yes` |
| `attributeOwnershipReleaseDenied` | `Ownership Management` | `7.12` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `single-java-overload` | `yes` |
| `cancelAttributeOwnershipAcquisition` | `Ownership Management` | `7.15` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `single-java-overload` | `yes` |
| `cancelNegotiatedAttributeOwnershipDivestiture` | `Ownership Management` | `7.14` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `single-java-overload` | `yes` |
| `changeAttributeOrderType` | `Time Management` | `8.23` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, OrderType theType` | `single-java-overload` | `yes` |
| `changeInteractionOrderType` | `Time Management` | `8.24` | `InteractionClassHandle theClass, OrderType theType` | `single-java-overload` | `yes` |
| `commitRegionModifications` | `Data Distribution Management` | `9.3` | `RegionHandleSet regions` | `single-java-overload` | `yes` |
| `confirmDivestiture` | `Ownership Management` | `7.6` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag` | `single-java-overload` | `yes` |
| `connect` | `Federation Management` | `4.2` | `FederateAmbassador federateReference, CallbackModel callbackModel, String localSettingsDesignator` | `weighted-or-shape-selected` | `yes` |
| `connect` | `Federation Management` | `4.2` | `FederateAmbassador federateReference, CallbackModel callbackModel` | `weighted-or-shape-selected` | `yes` |
| `createFederationExecution` | `Federation Management` | `4.5` | `String federationExecutionName, URL[] fomModules, URL mimModule, String logicalTimeImplementationName` | `explicit-deterministic` | `yes` |
| `createFederationExecution` | `Federation Management` | `4.5` | `String federationExecutionName, URL[] fomModules, String logicalTimeImplementationName` | `explicit-deterministic` | `yes` |
| `createFederationExecution` | `Federation Management` | `4.5` | `String federationExecutionName, URL[] fomModules, URL mimModule` | `explicit-deterministic` | `yes` |
| `createFederationExecution` | `Federation Management` | `4.5` | `String federationExecutionName, URL[] fomModules` | `explicit-deterministic` | `yes` |
| `createFederationExecution` | `Federation Management` | `4.5` | `String federationExecutionName, URL fomModule` | `explicit-deterministic` | `yes` |
| `createFederationExecutionWithMIM` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `createRegion` | `Data Distribution Management` | `9.2` | `DimensionHandleSet dimensions` | `single-java-overload` | `yes` |
| `decodeAttributeHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeDimensionHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeFederateHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeInteractionClassHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeMessageRetractionHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeObjectClassHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeObjectInstanceHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeParameterHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `decodeRegionHandle` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `deleteObjectInstance` | `Object Management` | `6.14` | `ObjectInstanceHandle objectHandle, byte[] userSuppliedTag` | `weighted-or-shape-selected` | `yes` |
| `deleteObjectInstance` | `Object Management` | `6.14` | `ObjectInstanceHandle objectHandle, byte[] userSuppliedTag, LogicalTime theTime` | `weighted-or-shape-selected` | `yes` |
| `deleteRegion` | `Data Distribution Management` | `9.4` | `RegionHandle theRegion` | `single-java-overload` | `yes` |
| `destroyFederationExecution` | `Federation Management` | `4.6` | `String federationExecutionName` | `single-java-overload` | `yes` |
| `disableAsynchronousDelivery` | `Time Management` | `8.15` | `(none)` | `single-java-overload` | `yes` |
| `disableAttributeRelevanceAdvisorySwitch` | `Support Services` | `10.36` | `(none)` | `single-java-overload` | `no` |
| `disableAttributeScopeAdvisorySwitch` | `Support Services` | `10.38` | `(none)` | `single-java-overload` | `no` |
| `disableCallbacks` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `disableInteractionRelevanceAdvisorySwitch` | `Support Services` | `10.40` | `(none)` | `single-java-overload` | `no` |
| `disableObjectClassRelevanceAdvisorySwitch` | `Support Services` | `10.34` | `(none)` | `single-java-overload` | `no` |
| `disableTimeConstrained` | `Time Management` | `8.7` | `(none)` | `single-java-overload` | `yes` |
| `disableTimeRegulation` | `Time Management` | `8.4` | `(none)` | `single-java-overload` | `yes` |
| `disconnect` | `Federation Management` | `4.3` | `(none)` | `single-java-overload` | `yes` |
| `enableAsynchronousDelivery` | `Time Management` | `8.14` | `(none)` | `single-java-overload` | `yes` |
| `enableAttributeRelevanceAdvisorySwitch` | `Support Services` | `10.35` | `(none)` | `single-java-overload` | `no` |
| `enableAttributeScopeAdvisorySwitch` | `Support Services` | `10.37` | `(none)` | `single-java-overload` | `no` |
| `enableCallbacks` | `Support Services` | `10.43` | `(none)` | `single-java-overload` | `yes` |
| `enableInteractionRelevanceAdvisorySwitch` | `Support Services` | `10.39` | `(none)` | `single-java-overload` | `no` |
| `enableObjectClassRelevanceAdvisorySwitch` | `Support Services` | `10.33` | `(none)` | `single-java-overload` | `no` |
| `enableTimeConstrained` | `Time Management` | `8.5` | `(none)` | `single-java-overload` | `yes` |
| `enableTimeRegulation` | `Time Management` | `8.2` | `LogicalTimeInterval theLookahead` | `single-java-overload` | `yes` |
| `evokeCallback` | `Support Services` | `10.41` | `double approximateMinimumTimeInSeconds` | `single-java-overload` | `yes` |
| `evokeMultipleCallbacks` | `Support Services` | `10.42` | `double approximateMinimumTimeInSeconds, double approximateMaximumTimeInSeconds` | `single-java-overload` | `yes` |
| `federateRestoreComplete` | `Federation Management` | `4.28` | `(none)` | `single-java-overload` | `yes` |
| `federateRestoreNotComplete` | `Federation Management` | `4.28` | `(none)` | `single-java-overload` | `yes` |
| `federateSaveBegun` | `Federation Management` | `4.18` | `(none)` | `single-java-overload` | `yes` |
| `federateSaveComplete` | `Federation Management` | `4.19` | `(none)` | `single-java-overload` | `yes` |
| `federateSaveNotComplete` | `Federation Management` | `4.19` | `(none)` | `single-java-overload` | `yes` |
| `flushQueueRequest` | `Time Management` | `8.12` | `LogicalTime theTime` | `single-java-overload` | `yes` |
| `getAttributeHandle` | `Support Services` | `10.11` | `ObjectClassHandle whichClass, String theName` | `single-java-overload` | `yes` |
| `getAttributeHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getAttributeHandleSetFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getAttributeHandleValueMapFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getAttributeName` | `Support Services` | `10.12` | `ObjectClassHandle whichClass, AttributeHandle theHandle` | `single-java-overload` | `yes` |
| `getAttributeSetRegionSetPairListFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getAutomaticResignDirective` | `Support Services` | `10.2` | `(none)` | `single-java-overload` | `yes` |
| `getAvailableDimensionsForClassAttribute` | `Support Services` | `10.23` | `ObjectClassHandle whichClass, AttributeHandle theHandle` | `single-java-overload` | `no` |
| `getAvailableDimensionsForInteractionClass` | `Support Services` | `10.24` | `InteractionClassHandle theHandle` | `single-java-overload` | `yes` |
| `getDimensionHandle` | `Support Services` | `10.25` | `String theName` | `single-java-overload` | `yes` |
| `getDimensionHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getDimensionHandleSet` | `Support Services` | `10.28` | `RegionHandle region` | `single-java-overload` | `yes` |
| `getDimensionHandleSetFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getDimensionName` | `Support Services` | `10.26` | `DimensionHandle theHandle` | `single-java-overload` | `yes` |
| `getDimensionUpperBound` | `Support Services` | `10.27` | `DimensionHandle theHandle` | `single-java-overload` | `yes` |
| `getFederateHandle` | `Support Services` | `10.4` | `String theName` | `single-java-overload` | `yes` |
| `getFederateHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getFederateHandleSetFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getFederateName` | `Support Services` | `10.5` | `FederateHandle theHandle` | `single-java-overload` | `yes` |
| `getHLAversion` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getInteractionClassHandle` | `Support Services` | `10.15` | `String theName` | `single-java-overload` | `yes` |
| `getInteractionClassHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getInteractionClassName` | `Support Services` | `10.16` | `InteractionClassHandle theHandle` | `single-java-overload` | `yes` |
| `getKnownObjectClassHandle` | `Support Services` | `10.8` | `ObjectInstanceHandle theObject` | `single-java-overload` | `yes` |
| `getMessageRetractionHandleFactory` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `getObjectClassHandle` | `Support Services` | `10.6` | `String theName` | `single-java-overload` | `yes` |
| `getObjectClassHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getObjectClassName` | `Support Services` | `10.7` | `ObjectClassHandle theHandle` | `single-java-overload` | `yes` |
| `getObjectInstanceHandle` | `Support Services` | `10.9` | `String theName` | `single-java-overload` | `yes` |
| `getObjectInstanceHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getObjectInstanceName` | `Support Services` | `10.10` | `ObjectInstanceHandle theHandle` | `single-java-overload` | `yes` |
| `getOrderName` | `Support Services` | `10.20` | `OrderType theType` | `single-java-overload` | `yes` |
| `getOrderType` | `Support Services` | `10.19` | `String theName` | `single-java-overload` | `yes` |
| `getParameterHandle` | `Support Services` | `10.17` | `InteractionClassHandle whichClass, String theName` | `single-java-overload` | `yes` |
| `getParameterHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getParameterHandleValueMapFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getParameterName` | `Support Services` | `10.18` | `InteractionClassHandle whichClass, ParameterHandle theHandle` | `single-java-overload` | `yes` |
| `getRangeBounds` | `Support Services` | `10.29` | `RegionHandle region, DimensionHandle dimension` | `single-java-overload` | `yes` |
| `getRegionHandleFactory` | n/a | n/a | `n/a` | `no-java-overload` | `yes` |
| `getRegionHandleSetFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getTimeFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getTransportationName` | n/a | n/a | `n/a` | `no-java-overload` | `no` |
| `getTransportationType` | n/a | n/a | `n/a` | `no-java-overload` | `no` |
| `getTransportationTypeHandle` | `Support Services` | `10.21` | `String theName` | `single-java-overload` | `yes` |
| `getTransportationTypeHandleFactory` | `Support Services` | `10.44` | `(none)` | `single-java-overload` | `yes` |
| `getTransportationTypeName` | `Support Services` | `10.22` | `TransportationTypeHandle theHandle` | `single-java-overload` | `yes` |
| `getUpdateRateValue` | `Support Services` | `10.13` | `String updateRateDesignator` | `single-java-overload` | `yes` |
| `getUpdateRateValueForAttribute` | `Support Services` | `10.14` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute` | `single-java-overload` | `yes` |
| `isAttributeOwnedByFederate` | `Ownership Management` | `7.19` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute` | `single-java-overload` | `yes` |
| `joinFederationExecution` | `Federation Management` | `4.9` | `String federateName, String federateType, String federationExecutionName, URL[] additionalFomModules` | `explicit-deterministic` | `yes` |
| `joinFederationExecution` | `Federation Management` | `4.9` | `String federateType, String federationExecutionName, URL[] additionalFomModules` | `explicit-deterministic` | `yes` |
| `joinFederationExecution` | `Federation Management` | `4.9` | `String federateName, String federateType, String federationExecutionName` | `explicit-deterministic` | `yes` |
| `joinFederationExecution` | `Federation Management` | `4.9` | `String federateType, String federationExecutionName` | `explicit-deterministic` | `yes` |
| `listFederationExecutions` | `Federation Management` | `4.7` | `(none)` | `single-java-overload` | `yes` |
| `localDeleteObjectInstance` | `Object Management` | `6.16` | `ObjectInstanceHandle objectHandle` | `single-java-overload` | `yes` |
| `modifyLookahead` | `Time Management` | `8.19` | `LogicalTimeInterval theLookahead` | `single-java-overload` | `yes` |
| `negotiatedAttributeOwnershipDivestiture` | `Ownership Management` | `7.3` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag` | `single-java-overload` | `yes` |
| `nextMessageRequest` | `Time Management` | `8.10` | `LogicalTime theTime` | `single-java-overload` | `yes` |
| `nextMessageRequestAvailable` | `Time Management` | `8.11` | `LogicalTime theTime` | `single-java-overload` | `yes` |
| `normalizeFederateHandle` | `Support Services` | `10.31` | `FederateHandle federateHandle` | `single-java-overload` | `yes` |
| `normalizeServiceGroup` | `Support Services` | `10.32` | `ServiceGroup group` | `single-java-overload` | `yes` |
| `publishInteractionClass` | `Declaration Management` | `5.4` | `InteractionClassHandle theInteraction` | `single-java-overload` | `yes` |
| `publishObjectClassAttributes` | `Declaration Management` | `5.2` | `ObjectClassHandle theClass, AttributeHandleSet attributeList` | `single-java-overload` | `yes` |
| `queryAttributeOwnership` | `Ownership Management` | `7.17` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute` | `single-java-overload` | `yes` |
| `queryAttributeTransportationType` | `Object Management` | `6.25` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute` | `single-java-overload` | `yes` |
| `queryFederationRestoreStatus` | `Federation Management` | `4.31` | `(none)` | `single-java-overload` | `yes` |
| `queryFederationSaveStatus` | `Federation Management` | `4.22` | `(none)` | `single-java-overload` | `yes` |
| `queryGALT` | `Time Management` | `8.16` | `(none)` | `single-java-overload` | `yes` |
| `queryInteractionTransportationType` | `Object Management` | `6.29` | `FederateHandle theFederate, InteractionClassHandle theInteraction` | `single-java-overload` | `yes` |
| `queryLITS` | `Time Management` | `8.18` | `(none)` | `single-java-overload` | `yes` |
| `queryLogicalTime` | `Time Management` | `8.17` | `(none)` | `single-java-overload` | `yes` |
| `queryLookahead` | `Time Management` | `8.20` | `(none)` | `single-java-overload` | `yes` |
| `registerFederationSynchronizationPoint` | `Federation Management` | `4.11` | `String synchronizationPointLabel, byte[] userSuppliedTag` | `weighted-or-shape-selected` | `yes` |
| `registerFederationSynchronizationPoint` | `Federation Management` | `4.11` | `String synchronizationPointLabel, byte[] userSuppliedTag, FederateHandleSet synchronizationSet` | `weighted-or-shape-selected` | `yes` |
| `registerObjectInstance` | `Object Management` | `6.8` | `ObjectClassHandle theClass` | `weighted-or-shape-selected` | `yes` |
| `registerObjectInstance` | `Object Management` | `6.8` | `ObjectClassHandle theClass, String theObjectName` | `weighted-or-shape-selected` | `yes` |
| `registerObjectInstanceWithRegions` | `Data Distribution Management` | `9.5` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions` | `weighted-or-shape-selected` | `yes` |
| `registerObjectInstanceWithRegions` | `Data Distribution Management` | `9.5` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, String theObject` | `weighted-or-shape-selected` | `yes` |
| `releaseMultipleObjectInstanceName` | `Object Management` | `6.7` | `Set<String> theObjectNames` | `single-java-overload` | `no` |
| `releaseObjectInstanceName` | `Object Management` | `6.4` | `String theObjectInstanceName` | `single-java-overload` | `yes` |
| `requestAttributeTransportationTypeChange` | `Object Management` | `6.23` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, TransportationTypeHandle theType` | `single-java-overload` | `yes` |
| `requestAttributeValueUpdate` | `Object Management` | `6.19` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag` | `explicit-deterministic` | `yes` |
| `requestAttributeValueUpdate` | `Object Management` | `6.19` | `ObjectClassHandle theClass, AttributeHandleSet theAttributes, byte[] userSuppliedTag` | `explicit-deterministic` | `yes` |
| `requestAttributeValueUpdateWithRegions` | `Data Distribution Management` | `9.13` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, byte[] userSuppliedTag` | `explicit-deterministic` | `yes` |
| `requestFederationRestore` | `Federation Management` | `4.24` | `String label` | `single-java-overload` | `yes` |
| `requestFederationSave` | `Federation Management` | `4.16` | `String label` | `weighted-or-shape-selected` | `yes` |
| `requestFederationSave` | `Federation Management` | `4.16` | `String label, LogicalTime theTime` | `weighted-or-shape-selected` | `yes` |
| `requestInteractionTransportationTypeChange` | `Object Management` | `6.27` | `InteractionClassHandle theClass, TransportationTypeHandle theType` | `single-java-overload` | `yes` |
| `reserveMultipleObjectInstanceName` | `Object Management` | `6.5` | `Set<String> theObjectNames` | `single-java-overload` | `no` |
| `reserveObjectInstanceName` | `Object Management` | `6.2` | `String theObjectName` | `single-java-overload` | `yes` |
| `resignFederationExecution` | `Federation Management` | `4.10` | `ResignAction resignAction` | `single-java-overload` | `yes` |
| `retract` | `Time Management` | `8.21` | `MessageRetractionHandle theHandle` | `single-java-overload` | `yes` |
| `sendInteraction` | `Object Management` | `6.12` | `InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, byte[] userSuppliedTag` | `weighted-or-shape-selected` | `yes` |
| `sendInteraction` | `Object Management` | `6.12` | `InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, LogicalTime theTime` | `weighted-or-shape-selected` | `yes` |
| `sendInteractionWithRegions` | `Data Distribution Management` | `9.12` | `InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, RegionHandleSet regions, byte[] userSuppliedTag` | `weighted-or-shape-selected` | `yes` |
| `sendInteractionWithRegions` | `Data Distribution Management` | `9.12` | `InteractionClassHandle theInteraction, ParameterHandleValueMap theParameters, RegionHandleSet regions, byte[] userSuppliedTag, LogicalTime theTime` | `weighted-or-shape-selected` | `yes` |
| `setAutomaticResignDirective` | `Support Services` | `10.3` | `ResignAction resignAction` | `single-java-overload` | `yes` |
| `setRangeBounds` | `Support Services` | `10.30` | `RegionHandle region, DimensionHandle dimension, RangeBounds bounds` | `single-java-overload` | `yes` |
| `subscribeInteractionClass` | `Declaration Management` | `5.8` | `InteractionClassHandle theClass` | `single-java-overload` | `yes` |
| `subscribeInteractionClassPassively` | `Declaration Management` | `5.8` | `InteractionClassHandle theClass` | `single-java-overload` | `yes` |
| `subscribeInteractionClassPassivelyWithRegions` | `Data Distribution Management` | `9.10` | `InteractionClassHandle theClass, RegionHandleSet regions` | `single-java-overload` | `yes` |
| `subscribeInteractionClassWithRegions` | `Data Distribution Management` | `9.10` | `InteractionClassHandle theClass, RegionHandleSet regions` | `single-java-overload` | `yes` |
| `subscribeObjectClassAttributes` | `Declaration Management` | `5.6` | `ObjectClassHandle theClass, AttributeHandleSet attributeList` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributes` | `Declaration Management` | `5.6` | `ObjectClassHandle theClass, AttributeHandleSet attributeList, String updateRateDesignator` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributesPassively` | `Declaration Management` | `5.6` | `ObjectClassHandle theClass, AttributeHandleSet attributeList` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributesPassively` | `Declaration Management` | `5.6` | `ObjectClassHandle theClass, AttributeHandleSet attributeList, String updateRateDesignator` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributesPassivelyWithRegions` | `Data Distribution Management` | `9.8` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributesPassivelyWithRegions` | `Data Distribution Management` | `9.8` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, String updateRateDesignator` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributesWithRegions` | `Data Distribution Management` | `9.8` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions` | `explicit-deterministic` | `yes` |
| `subscribeObjectClassAttributesWithRegions` | `Data Distribution Management` | `9.8` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions, String updateRateDesignator` | `explicit-deterministic` | `yes` |
| `synchronizationPointAchieved` | `Federation Management` | `4.14` | `String synchronizationPointLabel` | `weighted-or-shape-selected` | `yes` |
| `synchronizationPointAchieved` | `Federation Management` | `4.14` | `String synchronizationPointLabel, boolean successIndicator` | `weighted-or-shape-selected` | `yes` |
| `timeAdvanceRequest` | `Time Management` | `8.8` | `LogicalTime theTime` | `single-java-overload` | `yes` |
| `timeAdvanceRequestAvailable` | `Time Management` | `8.9` | `LogicalTime theTime` | `single-java-overload` | `yes` |
| `unassociateRegionsForUpdates` | `Data Distribution Management` | `9.7` | `ObjectInstanceHandle theObject, AttributeSetRegionSetPairList attributesAndRegions` | `single-java-overload` | `yes` |
| `unconditionalAttributeOwnershipDivestiture` | `Ownership Management` | `7.2` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `single-java-overload` | `yes` |
| `unpublishInteractionClass` | `Declaration Management` | `5.5` | `InteractionClassHandle theInteraction` | `single-java-overload` | `yes` |
| `unpublishObjectClass` | `Declaration Management` | `5.3` | `ObjectClassHandle theClass` | `single-java-overload` | `yes` |
| `unpublishObjectClassAttributes` | `Declaration Management` | `5.3` | `ObjectClassHandle theClass, AttributeHandleSet attributeList` | `single-java-overload` | `yes` |
| `unsubscribeInteractionClass` | `Declaration Management` | `5.9` | `InteractionClassHandle theClass` | `single-java-overload` | `yes` |
| `unsubscribeInteractionClassWithRegions` | `Data Distribution Management` | `9.11` | `InteractionClassHandle theClass, RegionHandleSet regions` | `single-java-overload` | `yes` |
| `unsubscribeObjectClass` | `Declaration Management` | `5.7` | `ObjectClassHandle theClass` | `single-java-overload` | `yes` |
| `unsubscribeObjectClassAttributes` | `Declaration Management` | `5.7` | `ObjectClassHandle theClass, AttributeHandleSet attributeList` | `single-java-overload` | `yes` |
| `unsubscribeObjectClassAttributesWithRegions` | `Data Distribution Management` | `9.9` | `ObjectClassHandle theClass, AttributeSetRegionSetPairList attributesAndRegions` | `single-java-overload` | `yes` |
| `updateAttributeValues` | `Object Management` | `6.10` | `ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag` | `weighted-or-shape-selected` | `yes` |
| `updateAttributeValues` | `Object Management` | `6.10` | `ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, LogicalTime theTime` | `weighted-or-shape-selected` | `yes` |

## FederateAmbassador

| Method | Group | Spec Ref | Java Params | Route Policy | 2025 Surface |
| --- | --- | --- | --- | --- | --- |
| `announceSynchronizationPoint` | `Federation Management` | `4.13` | `String synchronizationPointLabel, byte[] userSuppliedTag` | `direct-callback-dispatch` | `yes` |
| `attributeIsNotOwned` | `Ownership Management` | `7.18` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute` | `direct-callback-dispatch` | `yes` |
| `attributeIsOwnedByRTI` | `Ownership Management` | `7.18` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute` | `direct-callback-dispatch` | `yes` |
| `attributeOwnershipAcquisitionNotification` | `Ownership Management` | `7.7` | `ObjectInstanceHandle theObject, AttributeHandleSet securedAttributes, byte[] userSuppliedTag` | `direct-callback-dispatch` | `yes` |
| `attributeOwnershipUnavailable` | `Ownership Management` | `7.10` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `direct-callback-dispatch` | `yes` |
| `attributesInScope` | `Object Management` | `6.17` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `direct-callback-dispatch` | `yes` |
| `attributesOutOfScope` | `Object Management` | `6.18` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `direct-callback-dispatch` | `yes` |
| `confirmAttributeOwnershipAcquisitionCancellation` | `Ownership Management` | `7.16` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `direct-callback-dispatch` | `yes` |
| `confirmAttributeTransportationTypeChange` | `Object Management` | `6.24` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, TransportationTypeHandle theTransportation` | `direct-callback-dispatch` | `yes` |
| `confirmInteractionTransportationTypeChange` | `Object Management` | `6.28` | `InteractionClassHandle theInteraction, TransportationTypeHandle theTransportation` | `direct-callback-dispatch` | `yes` |
| `connectionLost` | `Federation Management` | `4.4` | `String faultDescription` | `direct-callback-dispatch` | `yes` |
| `discoverObjectInstance` | `Object Management` | `6.9` | `ObjectInstanceHandle theObject, ObjectClassHandle theObjectClass, String objectName` | `direct-callback-dispatch` | `yes` |
| `discoverObjectInstance` | `Object Management` | `6.9` | `ObjectInstanceHandle theObject, ObjectClassHandle theObjectClass, String objectName, FederateHandle producingFederate` | `direct-callback-dispatch` | `yes` |
| `federationNotRestored` | `Federation Management` | `4.29` | `RestoreFailureReason reason` | `direct-callback-dispatch` | `yes` |
| `federationNotSaved` | `Federation Management` | `4.20` | `SaveFailureReason reason` | `direct-callback-dispatch` | `yes` |
| `federationRestoreBegun` | `Federation Management` | `4.26` | `(none)` | `direct-callback-dispatch` | `yes` |
| `federationRestoreStatusResponse` | `Federation Management` | `4.32` | `FederateRestoreStatus[] response` | `direct-callback-dispatch` | `yes` |
| `federationRestored` | `Federation Management` | `4.29` | `(none)` | `direct-callback-dispatch` | `yes` |
| `federationSaveStatusResponse` | `Federation Management` | `4.23` | `FederateHandleSaveStatusPair[] response` | `direct-callback-dispatch` | `yes` |
| `federationSaved` | `Federation Management` | `4.20` | `(none)` | `direct-callback-dispatch` | `yes` |
| `federationSynchronized` | `Federation Management` | `4.15` | `String synchronizationPointLabel, FederateHandleSet failedToSyncSet` | `direct-callback-dispatch` | `yes` |
| `getProducingFederate` | `Object Management` | `6.9` | `(none)` | `direct-callback-dispatch` | `no` |
| `getProducingFederate` | `Object Management` | `6.11` | `(none)` | `direct-callback-dispatch` | `no` |
| `getProducingFederate` | `Object Management` | `6.13` | `(none)` | `direct-callback-dispatch` | `no` |
| `getSentRegions` | `Object Management` | `6.9` | `(none)` | `direct-callback-dispatch` | `no` |
| `getSentRegions` | `Object Management` | `6.11` | `(none)` | `direct-callback-dispatch` | `no` |
| `hasProducingFederate` | `Object Management` | `6.9` | `(none)` | `direct-callback-dispatch` | `no` |
| `hasProducingFederate` | `Object Management` | `6.11` | `(none)` | `direct-callback-dispatch` | `no` |
| `hasProducingFederate` | `Object Management` | `6.13` | `(none)` | `direct-callback-dispatch` | `no` |
| `hasSentRegions` | `Object Management` | `6.9` | `(none)` | `direct-callback-dispatch` | `no` |
| `hasSentRegions` | `Object Management` | `6.11` | `(none)` | `direct-callback-dispatch` | `no` |
| `informAttributeOwnership` | `Ownership Management` | `7.18` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute, FederateHandle theOwner` | `direct-callback-dispatch` | `yes` |
| `initiateFederateRestore` | `Federation Management` | `4.27` | `String label, String federateName, FederateHandle federateHandle` | `direct-callback-dispatch` | `yes` |
| `initiateFederateSave` | `Federation Management` | `4.17` | `String label` | `direct-callback-dispatch` | `yes` |
| `initiateFederateSave` | `Federation Management` | `4.17` | `String label, LogicalTime time` | `direct-callback-dispatch` | `yes` |
| `multipleObjectInstanceNameReservationFailed` | `Object Management` | `6.6` | `Set<String> objectNames` | `direct-callback-dispatch` | `yes` |
| `multipleObjectInstanceNameReservationSucceeded` | `Object Management` | `6.6` | `Set<String> objectNames` | `direct-callback-dispatch` | `yes` |
| `objectInstanceNameReservationFailed` | `Object Management` | `6.3` | `String objectName` | `direct-callback-dispatch` | `yes` |
| `objectInstanceNameReservationSucceeded` | `Object Management` | `6.3` | `String objectName` | `direct-callback-dispatch` | `yes` |
| `provideAttributeValueUpdate` | `Object Management` | `6.20` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag` | `direct-callback-dispatch` | `yes` |
| `receiveInteraction` | `Object Management` | `6.13` | `InteractionClassHandle interactionClass, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, SupplementalReceiveInfo receiveInfo` | `direct-callback-dispatch` | `yes` |
| `receiveInteraction` | `Object Management` | `6.13` | `InteractionClassHandle interactionClass, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, SupplementalReceiveInfo receiveInfo` | `direct-callback-dispatch` | `yes` |
| `receiveInteraction` | `Object Management` | `6.13` | `InteractionClassHandle interactionClass, ParameterHandleValueMap theParameters, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, MessageRetractionHandle retractionHandle, SupplementalReceiveInfo receiveInfo` | `direct-callback-dispatch` | `yes` |
| `reflectAttributeValues` | `Object Management` | `6.11` | `ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, SupplementalReflectInfo reflectInfo` | `direct-callback-dispatch` | `yes` |
| `reflectAttributeValues` | `Object Management` | `6.11` | `ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, SupplementalReflectInfo reflectInfo` | `direct-callback-dispatch` | `yes` |
| `reflectAttributeValues` | `Object Management` | `6.11` | `ObjectInstanceHandle theObject, AttributeHandleValueMap theAttributes, byte[] userSuppliedTag, OrderType sentOrdering, TransportationTypeHandle theTransport, LogicalTime theTime, OrderType receivedOrdering, MessageRetractionHandle retractionHandle, SupplementalReflectInfo reflectInfo` | `direct-callback-dispatch` | `yes` |
| `removeObjectInstance` | `Object Management` | `6.15` | `ObjectInstanceHandle theObject, byte[] userSuppliedTag, OrderType sentOrdering, SupplementalRemoveInfo removeInfo` | `direct-callback-dispatch` | `yes` |
| `removeObjectInstance` | `Object Management` | `6.15` | `ObjectInstanceHandle theObject, byte[] userSuppliedTag, OrderType sentOrdering, LogicalTime theTime, OrderType receivedOrdering, SupplementalRemoveInfo removeInfo` | `direct-callback-dispatch` | `yes` |
| `removeObjectInstance` | `Object Management` | `6.15` | `ObjectInstanceHandle theObject, byte[] userSuppliedTag, OrderType sentOrdering, LogicalTime theTime, OrderType receivedOrdering, MessageRetractionHandle retractionHandle, SupplementalRemoveInfo removeInfo` | `direct-callback-dispatch` | `yes` |
| `reportAttributeTransportationType` | `Object Management` | `6.26` | `ObjectInstanceHandle theObject, AttributeHandle theAttribute, TransportationTypeHandle theTransportation` | `direct-callback-dispatch` | `yes` |
| `reportFederationExecutions` | `Federation Management` | `4.8` | `FederationExecutionInformationSet theFederationExecutionInformationSet` | `direct-callback-dispatch` | `yes` |
| `reportInteractionTransportationType` | `Object Management` | `6.30` | `FederateHandle theFederate, InteractionClassHandle theInteraction, TransportationTypeHandle theTransportation` | `direct-callback-dispatch` | `yes` |
| `requestAttributeOwnershipAssumption` | `Ownership Management` | `7.4` | `ObjectInstanceHandle theObject, AttributeHandleSet offeredAttributes, byte[] userSuppliedTag` | `direct-callback-dispatch` | `yes` |
| `requestAttributeOwnershipRelease` | `Ownership Management` | `7.11` | `ObjectInstanceHandle theObject, AttributeHandleSet candidateAttributes, byte[] userSuppliedTag` | `direct-callback-dispatch` | `yes` |
| `requestDivestitureConfirmation` | `Ownership Management` | `7.5` | `ObjectInstanceHandle theObject, AttributeHandleSet offeredAttributes` | `direct-callback-dispatch` | `yes` |
| `requestFederationRestoreFailed` | `Federation Management` | `4.25` | `String label` | `direct-callback-dispatch` | `yes` |
| `requestFederationRestoreSucceeded` | `Federation Management` | `4.25` | `String label` | `direct-callback-dispatch` | `yes` |
| `requestRetraction` | `Time Management` | `8.22` | `MessageRetractionHandle theHandle` | `direct-callback-dispatch` | `yes` |
| `startRegistrationForObjectClass` | `Declaration Management` | `5.10` | `ObjectClassHandle theClass` | `direct-callback-dispatch` | `yes` |
| `stopRegistrationForObjectClass` | `Declaration Management` | `5.11` | `ObjectClassHandle theClass` | `direct-callback-dispatch` | `yes` |
| `synchronizationPointRegistrationFailed` | `Federation Management` | `4.12` | `String synchronizationPointLabel, SynchronizationPointFailureReason reason` | `direct-callback-dispatch` | `yes` |
| `synchronizationPointRegistrationSucceeded` | `Federation Management` | `4.12` | `String synchronizationPointLabel` | `direct-callback-dispatch` | `yes` |
| `timeAdvanceGrant` | `Time Management` | `8.13` | `LogicalTime theTime` | `direct-callback-dispatch` | `yes` |
| `timeConstrainedEnabled` | `Time Management` | `8.6` | `LogicalTime time` | `direct-callback-dispatch` | `yes` |
| `timeRegulationEnabled` | `Time Management` | `8.3` | `LogicalTime time` | `direct-callback-dispatch` | `yes` |
| `turnInteractionsOff` | `Declaration Management` | `5.13` | `InteractionClassHandle theHandle` | `direct-callback-dispatch` | `yes` |
| `turnInteractionsOn` | `Declaration Management` | `5.12` | `InteractionClassHandle theHandle` | `direct-callback-dispatch` | `yes` |
| `turnUpdatesOffForObjectInstance` | `Object Management` | `6.22` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `direct-callback-dispatch` | `yes` |
| `turnUpdatesOnForObjectInstance` | `Object Management` | `6.21` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes` | `direct-callback-dispatch` | `yes` |
| `turnUpdatesOnForObjectInstance` | `Object Management` | `6.21` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, String updateRateDesignator` | `direct-callback-dispatch` | `yes` |

