# Pure Python RTI traceability and ambassador coverage

This release keeps federate code backend-neutral while expanding the pure Python RTI. Section links are engineering traceability IDs extracted from the uploaded IEEE 1516.1-2010 Java/C++ API metadata in `hla.rti1516e.raw_api.API_METADATA`.

The Python RTI is a development/reference RTI, not a certified production RTI. Complex HLA services such as ownership negotiation, save/restore, advisory switches, and DDM routing use local-process reference semantics where noted.

## Coverage summary

| Surface | Count | Status |
|---|---:|---|
| RTIambassador services | 162 / 162 | every source-derived method has a `PythonRTIBackend` handler |
| FederateAmbassador callbacks | 55 / 55 | no-op base + recording + multiplexer helpers |
| FOM/OMT references | 1516.2 section IDs | exposed through `hla.rti1516e.spec_refs.FOM_REFERENCES` |

## Ambassador helpers

| Helper | Purpose |
|---|---|
| `FederateAmbassador` | Pythonic no-op callback base with snake_case and lowerCamelCase callback support. |
| `NullFederateAmbassador` | Explicit no-op ambassador for federates that do not need callbacks. |
| `RecordingFederateAmbassador` | Records each callback as `CallbackRecord(method_name, args, kwargs, reference)`. |
| `FederateAmbassadorMultiplexer` | Forwards one RTI callback stream to multiple ambassador objects. |

## Example section lookup

```python
from hla.rti1516e.spec_refs import method_reference
assert method_reference("connect").section == "4.2"
assert method_reference("create_federation_execution_with_mim").section == "4.5"
assert method_reference("update_attribute_values").section == "6.10"
assert method_reference("timeAdvanceGrant").section == "8.13"
```

## FOM/OMT reference anchors

| Symbol | Section | Title |
|---|---:|---|
| `omt_components` | 4 | HLA OMT components |
| `object_class_structure` | 4.2 | Object class structure table |
| `interaction_class_structure` | 4.3 | Interaction class structure table |
| `attribute_table` | 4.4 | Attribute table |
| `parameter_table` | 4.5 | Parameter table |
| `dimension_table` | 4.6 | Dimension table |
| `time_representation_table` | 4.7 | Time representation table |
| `merging_rules` | 7 | FOM module/SOM module merging rules |
| `dif` | Annex D | OMT data interchange format |
| `schema` | Annex E | OMT conformance XML Schema |

## Pure Python RTI service table

### Data Distribution Management

| Method | Section | Implementation level |
|---|---:|---|
| `subscribeInteractionClassPassivelyWithRegions` | 9.10 | behavioral/reference subset |
| `subscribeInteractionClassWithRegions` | 9.10 | behavioral/reference subset |
| `unsubscribeInteractionClassWithRegions` | 9.11 | behavioral/reference subset |
| `sendInteractionWithRegions` | 9.12 | behavioral/reference subset |
| `requestAttributeValueUpdateWithRegions` | 9.13 | behavioral/reference subset |
| `createRegion` | 9.2 | behavioral/reference subset |
| `commitRegionModifications` | 9.3 | behavioral/reference subset |
| `deleteRegion` | 9.4 | behavioral/reference subset |
| `registerObjectInstanceWithRegions` | 9.5 | behavioral/reference subset |
| `associateRegionsForUpdates` | 9.6 | behavioral/reference subset |
| `unassociateRegionsForUpdates` | 9.7 | behavioral/reference subset |
| `subscribeObjectClassAttributesPassivelyWithRegions` | 9.8 | behavioral/reference subset |
| `subscribeObjectClassAttributesWithRegions` | 9.8 | behavioral/reference subset |
| `unsubscribeObjectClassAttributesWithRegions` | 9.9 | behavioral/reference subset |

### Declaration Management

| Method | Section | Implementation level |
|---|---:|---|
| `publishObjectClassAttributes` | 5.2 | behavioral/reference subset |
| `unpublishObjectClass` | 5.3 | behavioral/reference subset |
| `unpublishObjectClassAttributes` | 5.3 | behavioral/reference subset |
| `publishInteractionClass` | 5.4 | behavioral/reference subset |
| `unpublishInteractionClass` | 5.5 | behavioral/reference subset |
| `subscribeObjectClassAttributes` | 5.6 | behavioral/reference subset |
| `subscribeObjectClassAttributesPassively` | 5.6 | behavioral/reference subset |
| `unsubscribeObjectClass` | 5.7 | behavioral/reference subset |
| `unsubscribeObjectClassAttributes` | 5.7 | behavioral/reference subset |
| `subscribeInteractionClass` | 5.8 | behavioral/reference subset |
| `subscribeInteractionClassPassively` | 5.8 | behavioral/reference subset |
| `unsubscribeInteractionClass` | 5.9 | behavioral/reference subset |

### Federation Management

| Method | Section | Implementation level |
|---|---:|---|
| `resignFederationExecution` | 4.10 | behavioral/reference subset |
| `registerFederationSynchronizationPoint` | 4.11 | behavioral/reference subset |
| `synchronizationPointAchieved` | 4.14 | behavioral/reference subset |
| `requestFederationSave` | 4.16 | behavioral/reference subset |
| `federateSaveBegun` | 4.18 | behavioral/reference subset |
| `federateSaveComplete` | 4.19 | behavioral/reference subset |
| `federateSaveNotComplete` | 4.19 | behavioral/reference subset |
| `connect` | 4.2 | behavioral/reference subset |
| `abortFederationSave` | 4.21 | behavioral/reference subset |
| `queryFederationSaveStatus` | 4.22 | behavioral/reference subset |
| `requestFederationRestore` | 4.24 | behavioral/reference subset |
| `federateRestoreComplete` | 4.28 | behavioral/reference subset |
| `federateRestoreNotComplete` | 4.28 | behavioral/reference subset |
| `disconnect` | 4.3 | behavioral/reference subset |
| `abortFederationRestore` | 4.30 | behavioral/reference subset |
| `queryFederationRestoreStatus` | 4.31 | behavioral/reference subset |
| `createFederationExecution` | 4.5 | behavioral/reference subset |
| `createFederationExecutionWithMIM` | 4.5 | behavioral/reference subset |
| `destroyFederationExecution` | 4.6 | behavioral/reference subset |
| `listFederationExecutions` | 4.7 | behavioral/reference subset |
| `joinFederationExecution` | 4.9 | behavioral/reference subset |

### Object Management

| Method | Section | Implementation level |
|---|---:|---|
| `updateAttributeValues` | 6.10 | behavioral/reference subset |
| `sendInteraction` | 6.12 | behavioral/reference subset |
| `deleteObjectInstance` | 6.14 | behavioral/reference subset |
| `localDeleteObjectInstance` | 6.16 | behavioral/reference subset |
| `requestAttributeValueUpdate` | 6.19 | behavioral/reference subset |
| `reserveObjectInstanceName` | 6.2 | behavioral/reference subset |
| `requestAttributeTransportationTypeChange` | 6.23 | validation/no-op or simplified |
| `queryAttributeTransportationType` | 6.25 | validation/no-op or simplified |
| `requestInteractionTransportationTypeChange` | 6.27 | validation/no-op or simplified |
| `queryInteractionTransportationType` | 6.29 | validation/no-op or simplified |
| `releaseObjectInstanceName` | 6.4 | behavioral/reference subset |
| `reserveMultipleObjectInstanceName` | 6.5 | behavioral/reference subset |
| `releaseMultipleObjectInstanceName` | 6.7 | behavioral/reference subset |
| `registerObjectInstance` | 6.8 | behavioral/reference subset |

### Ownership Management

| Method | Section | Implementation level |
|---|---:|---|
| `attributeOwnershipReleaseDenied` | 7.12 | behavioral/reference subset |
| `attributeOwnershipDivestitureIfWanted` | 7.13 | behavioral/reference subset |
| `cancelNegotiatedAttributeOwnershipDivestiture` | 7.14 | behavioral/reference subset |
| `cancelAttributeOwnershipAcquisition` | 7.15 | behavioral/reference subset |
| `queryAttributeOwnership` | 7.17 | behavioral/reference subset |
| `isAttributeOwnedByFederate` | 7.19 | behavioral/reference subset |
| `unconditionalAttributeOwnershipDivestiture` | 7.2 | behavioral/reference subset |
| `negotiatedAttributeOwnershipDivestiture` | 7.3 | behavioral/reference subset |
| `confirmDivestiture` | 7.6 | behavioral/reference subset |
| `attributeOwnershipAcquisition` | 7.8 | behavioral/reference subset |
| `attributeOwnershipAcquisitionIfAvailable` | 7.9 | behavioral/reference subset |

### Programming Language Mappings

| Method | Section | Implementation level |
|---|---:|---|
| `decodeAttributeHandle` | 12.2 | support/factory/query |
| `decodeDimensionHandle` | 12.2 | support/factory/query |
| `decodeFederateHandle` | 12.2 | support/factory/query |
| `decodeInteractionClassHandle` | 12.2 | support/factory/query |
| `decodeMessageRetractionHandle` | 12.2 | support/factory/query |
| `decodeObjectClassHandle` | 12.2 | support/factory/query |
| `decodeObjectInstanceHandle` | 12.2 | support/factory/query |
| `decodeParameterHandle` | 12.2 | support/factory/query |
| `decodeRegionHandle` | 12.2 | support/factory/query |

### Support Services

| Method | Section | Implementation level |
|---|---:|---|
| `getObjectInstanceName` | 10.10 | support/factory/query |
| `getAttributeHandle` | 10.11 | support/factory/query |
| `getAttributeName` | 10.12 | support/factory/query |
| `getUpdateRateValue` | 10.13 | support/factory/query |
| `getUpdateRateValueForAttribute` | 10.14 | support/factory/query |
| `getInteractionClassHandle` | 10.15 | support/factory/query |
| `getInteractionClassName` | 10.16 | support/factory/query |
| `getParameterHandle` | 10.17 | support/factory/query |
| `getParameterName` | 10.18 | support/factory/query |
| `getOrderType` | 10.19 | support/factory/query |
| `getAutomaticResignDirective` | 10.2 | support/factory/query |
| `getOrderName` | 10.20 | support/factory/query |
| `getTransportationType` | 10.21 | support/factory/query |
| `getTransportationTypeHandle` | 10.21 | support/factory/query |
| `getTransportationName` | 10.22 | support/factory/query |
| `getTransportationTypeName` | 10.22 | support/factory/query |
| `getAvailableDimensionsForClassAttribute` | 10.23 | support/factory/query |
| `getAvailableDimensionsForInteractionClass` | 10.24 | support/factory/query |
| `getDimensionHandle` | 10.25 | support/factory/query |
| `getDimensionName` | 10.26 | support/factory/query |
| `getDimensionUpperBound` | 10.27 | support/factory/query |
| `getDimensionHandleSet` | 10.28 | support/factory/query |
| `getRangeBounds` | 10.29 | behavioral/reference subset |
| `setAutomaticResignDirective` | 10.3 | validation/no-op or simplified |
| `setRangeBounds` | 10.30 | behavioral/reference subset |
| `normalizeFederateHandle` | 10.31 | support/factory/query |
| `normalizeServiceGroup` | 10.32 | support/factory/query |
| `enableObjectClassRelevanceAdvisorySwitch` | 10.33 | state flag / simplified |
| `disableObjectClassRelevanceAdvisorySwitch` | 10.34 | state flag / simplified |
| `enableAttributeRelevanceAdvisorySwitch` | 10.35 | state flag / simplified |
| `disableAttributeRelevanceAdvisorySwitch` | 10.36 | state flag / simplified |
| `enableAttributeScopeAdvisorySwitch` | 10.37 | state flag / simplified |
| `disableAttributeScopeAdvisorySwitch` | 10.38 | state flag / simplified |
| `enableInteractionRelevanceAdvisorySwitch` | 10.39 | state flag / simplified |
| `getFederateHandle` | 10.4 | support/factory/query |
| `disableInteractionRelevanceAdvisorySwitch` | 10.40 | state flag / simplified |
| `evokeCallback` | 10.41 | validation/no-op or simplified |
| `evokeMultipleCallbacks` | 10.42 | validation/no-op or simplified |
| `enableCallbacks` | 10.43 | state flag / simplified |
| `disableCallbacks` | 10.44 | state flag / simplified |
| `getAttributeHandleFactory` | 10.44 | support/factory/query |
| `getAttributeHandleSetFactory` | 10.44 | support/factory/query |
| `getAttributeHandleValueMapFactory` | 10.44 | support/factory/query |
| `getAttributeSetRegionSetPairListFactory` | 10.44 | support/factory/query |
| `getDimensionHandleFactory` | 10.44 | support/factory/query |
| `getDimensionHandleSetFactory` | 10.44 | support/factory/query |
| `getFederateHandleFactory` | 10.44 | support/factory/query |
| `getFederateHandleSetFactory` | 10.44 | support/factory/query |
| `getHLAversion` | 10.44 | support/factory/query |
| `getInteractionClassHandleFactory` | 10.44 | support/factory/query |
| `getObjectClassHandleFactory` | 10.44 | support/factory/query |
| `getObjectInstanceHandleFactory` | 10.44 | support/factory/query |
| `getParameterHandleFactory` | 10.44 | support/factory/query |
| `getParameterHandleValueMapFactory` | 10.44 | support/factory/query |
| `getRegionHandleSetFactory` | 10.44 | support/factory/query |
| `getTimeFactory` | 10.44 | support/factory/query |
| `getTransportationTypeHandleFactory` | 10.44 | support/factory/query |
| `getFederateName` | 10.5 | support/factory/query |
| `getObjectClassHandle` | 10.6 | support/factory/query |
| `getObjectClassName` | 10.7 | support/factory/query |
| `getKnownObjectClassHandle` | 10.8 | support/factory/query |
| `getObjectInstanceHandle` | 10.9 | support/factory/query |

### Time Management

| Method | Section | Implementation level |
|---|---:|---|
| `nextMessageRequest` | 8.10 | behavioral/reference subset |
| `nextMessageRequestAvailable` | 8.11 | behavioral/reference subset |
| `flushQueueRequest` | 8.12 | behavioral/reference subset |
| `enableAsynchronousDelivery` | 8.14 | state flag / simplified |
| `disableAsynchronousDelivery` | 8.15 | state flag / simplified |
| `queryGALT` | 8.16 | behavioral/reference subset |
| `queryLogicalTime` | 8.17 | behavioral/reference subset |
| `queryLITS` | 8.18 | behavioral/reference subset |
| `modifyLookahead` | 8.19 | behavioral/reference subset |
| `enableTimeRegulation` | 8.2 | behavioral/reference subset |
| `queryLookahead` | 8.20 | behavioral/reference subset |
| `retract` | 8.21 | behavioral/reference subset |
| `changeAttributeOrderType` | 8.23 | behavioral/reference subset |
| `changeInteractionOrderType` | 8.24 | behavioral/reference subset |
| `disableTimeRegulation` | 8.4 | behavioral/reference subset |
| `enableTimeConstrained` | 8.5 | behavioral/reference subset |
| `disableTimeConstrained` | 8.7 | behavioral/reference subset |
| `timeAdvanceRequest` | 8.8 | behavioral/reference subset |
| `timeAdvanceRequestAvailable` | 8.9 | behavioral/reference subset |
