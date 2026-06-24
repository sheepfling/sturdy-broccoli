"""Traceability references for the HLA 1516.1-2010 Python work.

The project keeps the implementation small, but every RTI/Federate ambassador
service is linked to the corresponding IEEE 1516.1-2010 service clause where the
source API metadata exposes a service number.  FOM parsing references point at
IEEE 1516.2-2010 OMT clauses.

The values here are section identifiers and titles only.  They are intended for
engineering traceability and should not be treated as a replacement for the IEEE
standards.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SpecReference:
    document: str
    section: str
    title: str
    service_group: str | None = None
    note: str | None = None

    @property
    def label(self) -> str:
        group = f" ({self.service_group})" if self.service_group else ""
        return f"{self.document} §{self.section} {self.title}{group}"

    def as_markdown_anchor(self) -> str:
        anchor = self.section.lower().replace(".", "-").replace(" ", "-")
        return f"[{self.document} §{self.section}](#{anchor}) — {self.title}"


IEEE_1516_1_2010 = "IEEE 1516.1-2010 (2010 edition)"
IEEE_1516_2_2010 = "IEEE 1516.2-2010 (2010 edition)"


SERVICE_AREAS: dict[str, SpecReference] = {
    "federation_management": SpecReference(IEEE_1516_1_2010, "4", "Federation management"),
    "declaration_management": SpecReference(IEEE_1516_1_2010, "5", "Declaration management"),
    "object_management": SpecReference(IEEE_1516_1_2010, "6", "Object management"),
    "ownership_management": SpecReference(IEEE_1516_1_2010, "7", "Ownership management"),
    "time_management": SpecReference(IEEE_1516_1_2010, "8", "Time management"),
    "data_distribution_management": SpecReference(IEEE_1516_1_2010, "9", "Data distribution management"),
    "support_services": SpecReference(IEEE_1516_1_2010, "10", "Support services"),
    "mom": SpecReference(IEEE_1516_1_2010, "11", "Management object model"),
    "language_mappings": SpecReference(IEEE_1516_1_2010, "12", "Programming language mappings"),
}

FOM_REFERENCES: dict[str, SpecReference] = {
    "omt_components": SpecReference(IEEE_1516_2_2010, "4", "HLA OMT components"),
    "object_model_identification": SpecReference(IEEE_1516_2_2010, "4.1", "Object model identification"),
    "object_class_structure": SpecReference(IEEE_1516_2_2010, "4.2", "Object class structure table"),
    "interaction_class_structure": SpecReference(IEEE_1516_2_2010, "4.3", "Interaction class structure table"),
    "attribute_table": SpecReference(IEEE_1516_2_2010, "4.4", "Attribute table"),
    "parameter_table": SpecReference(IEEE_1516_2_2010, "4.5", "Parameter table"),
    "dimension_table": SpecReference(IEEE_1516_2_2010, "4.6", "Dimension table"),
    "time_representation_table": SpecReference(IEEE_1516_2_2010, "4.7", "Time representation table"),
    "user_supplied_tag_table": SpecReference(IEEE_1516_2_2010, "4.8", "User-supplied tag table"),
    "synchronization_table": SpecReference(IEEE_1516_2_2010, "4.9", "Synchronization table"),
    "transportation_type_table": SpecReference(IEEE_1516_2_2010, "4.10", "Transportation type table"),
    "update_rate_table": SpecReference(IEEE_1516_2_2010, "4.11", "Update rate table"),
    "switches_table": SpecReference(IEEE_1516_2_2010, "4.12", "Switches table"),
    "datatype_table": SpecReference(IEEE_1516_2_2010, "4.13", "Datatype tables"),
    "notes_table": SpecReference(IEEE_1516_2_2010, "4.14", "Notes table"),
    "lexicon": SpecReference(IEEE_1516_2_2010, "5", "FOM/SOM lexicon"),
    "conformance": SpecReference(IEEE_1516_2_2010, "6", "Conformance"),
    "merging_rules": SpecReference(IEEE_1516_2_2010, "7", "FOM module/SOM module merging rules"),
    "dif": SpecReference(IEEE_1516_2_2010, "Annex D", "OMT data interchange format"),
    "schema": SpecReference(IEEE_1516_2_2010, "Annex E", "OMT conformance XML Schema"),
}

_METHOD_REFERENCE_DATA: dict[str, tuple[str, str, str]] = {'abortFederationRestore': ('4.30', 'Federation Management', 'Abort Federation Restore service'),
 'abortFederationSave': ('4.21', 'Federation Management', 'Abort Federation Save service'),
 'announceSynchronizationPoint': ('4.13', 'Federation Management', 'Announce Synchronization Point service'),
 'associateRegionsForUpdates': ('9.6', 'Data Distribution Management', 'Associate Regions For Updates service'),
 'attributeIsNotOwned': ('7.18', 'Ownership Management', 'Inform Attribute Ownership service'),
 'attributeIsOwnedByRTI': ('7.18', 'Ownership Management', 'Inform Attribute Ownership service'),
 'attributeOwnershipAcquisition': ('7.8', 'Ownership Management', 'Attribute Ownership Acquisition service'),
 'attributeOwnershipAcquisitionIfAvailable': ('7.9',
                                              'Ownership Management',
                                              'Attribute Ownership Acquisition If Available service'),
 'attributeOwnershipAcquisitionNotification': ('7.7',
                                               'Ownership Management',
                                               'Attribute Ownership Acquisition Notification service'),
 'attributeOwnershipDivestitureIfWanted': ('7.13',
                                           'Ownership Management',
                                           'Attribute Ownership Divestiture If Wanted service'),
 'attributeOwnershipReleaseDenied': ('7.12', 'Ownership Management', 'Attribute Ownership Release Denied service'),
 'attributeOwnershipUnavailable': ('7.10', 'Ownership Management', 'Attribute Ownership Unavailable service'),
 'attributesInScope': ('6.17', 'Object Management', 'Attributes In Scope service'),
 'attributesOutOfScope': ('6.18', 'Object Management', 'Attributes Out Of Scope service'),
 'cancelAttributeOwnershipAcquisition': ('7.15',
                                         'Ownership Management',
                                         'Cancel Attribute Ownership Acquisition service'),
 'cancelNegotiatedAttributeOwnershipDivestiture': ('7.14',
                                                   'Ownership Management',
                                                   'Cancel Negotiated Attribute Ownership Divestiture service'),
 'changeAttributeOrderType': ('8.23', 'Time Management', 'Change Attribute Order Type service'),
 'changeInteractionOrderType': ('8.24', 'Time Management', 'Change Interaction Order Type service'),
 'commitRegionModifications': ('9.3', 'Data Distribution Management', 'Commit Region Modifications service'),
 'confirmAttributeOwnershipAcquisitionCancellation': ('7.16',
                                                      'Ownership Management',
                                                      'Confirm Attribute Ownership Acquisition Cancellation service'),
 'confirmAttributeTransportationTypeChange': ('6.24',
                                              'Object Management',
                                              'Confirm Attribute Transportation Type Change service'),
 'confirmDivestiture': ('7.6', 'Ownership Management', 'Confirm Divestiture service'),
 'confirmInteractionTransportationTypeChange': ('6.28',
                                                'Object Management',
                                                'Confirm Interaction Transportation Type Change service'),
 'connect': ('4.2', 'Federation Management', 'Connect service'),
 'connectionLost': ('4.4', 'Federation Management', 'Connection Lost service'),
 'createFederationExecution': ('4.5', 'Federation Management', 'Create Federation Execution service'),
 'createFederationExecutionWithMIM': ('4.5', 'Federation Management', 'Create Federation Execution service'),
 'createRegion': ('9.2', 'Data Distribution Management', 'Create Region service'),
 'decodeAttributeHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeDimensionHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeFederateHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeInteractionClassHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeMessageRetractionHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeObjectClassHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeObjectInstanceHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeParameterHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'decodeRegionHandle': ('12.2', 'Programming Language Mappings', 'Designators'),
 'deleteObjectInstance': ('6.14', 'Object Management', 'Delete Object Instance service'),
 'deleteRegion': ('9.4', 'Data Distribution Management', 'Delete Region service'),
 'destroyFederationExecution': ('4.6', 'Federation Management', 'Destroy Federation Execution service'),
 'disableAsynchronousDelivery': ('8.15', 'Time Management', 'Disable Asynchronous Delivery service'),
 'disableAttributeRelevanceAdvisorySwitch': ('10.36',
                                             'Support Services',
                                             'Disable Attribute Relevance Advisory Switch service'),
 'disableAttributeScopeAdvisorySwitch': ('10.38',
                                         'Support Services',
                                         'Disable Attribute Scope Advisory Switch service'),
 'disableCallbacks': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'disableInteractionRelevanceAdvisorySwitch': ('10.40',
                                               'Support Services',
                                               'Disable Interaction Relevance Advisory Switch service'),
 'disableObjectClassRelevanceAdvisorySwitch': ('10.34',
                                               'Support Services',
                                               'Disable Object Class Relevance Advisory Switch service'),
 'disableTimeConstrained': ('8.7', 'Time Management', 'Disable Time Constrained service'),
 'disableTimeRegulation': ('8.4', 'Time Management', 'Disable Time Regulation service'),
 'disconnect': ('4.3', 'Federation Management', 'Disconnect service'),
 'discoverObjectInstance': ('6.9', 'Object Management', 'Discover Object Instance service'),
 'enableAsynchronousDelivery': ('8.14', 'Time Management', 'Enable Asynchronous Delivery service'),
 'enableAttributeRelevanceAdvisorySwitch': ('10.35',
                                            'Support Services',
                                            'Enable Attribute Relevance Advisory Switch service'),
 'enableAttributeScopeAdvisorySwitch': ('10.37', 'Support Services', 'Enable Attribute Scope Advisory Switch service'),
 'enableCallbacks': ('10.43', 'Support Services', 'Enable Callbacks service'),
 'enableInteractionRelevanceAdvisorySwitch': ('10.39',
                                              'Support Services',
                                              'Enable Interaction Relevance Advisory Switch service'),
 'enableObjectClassRelevanceAdvisorySwitch': ('10.33',
                                              'Support Services',
                                              'Enable Object Class Relevance Advisory Switch service'),
 'enableTimeConstrained': ('8.5', 'Time Management', 'Enable Time Constrained service'),
 'enableTimeRegulation': ('8.2', 'Time Management', 'Enable Time Regulation service'),
 'evokeCallback': ('10.41', 'Support Services', 'Evoke Callback service'),
 'evokeMultipleCallbacks': ('10.42', 'Support Services', 'Evoke Multiple Callbacks service'),
 'federateRestoreComplete': ('4.28', 'Federation Management', 'Federate Restore Complete service'),
 'federateRestoreNotComplete': ('4.28', 'Federation Management', 'Federate Restore Complete service'),
 'federateSaveBegun': ('4.18', 'Federation Management', 'Federate Save Begun service'),
 'federateSaveComplete': ('4.19', 'Federation Management', 'Federate Save Complete service'),
 'federateSaveNotComplete': ('4.19', 'Federation Management', 'Federate Save Complete service'),
 'federationNotRestored': ('4.29', 'Federation Management', 'Federation Restored service'),
 'federationNotSaved': ('4.20', 'Federation Management', 'Federation Saved service'),
 'federationRestoreBegun': ('4.26', 'Federation Management', 'Federation Restore Begun service'),
 'federationRestoreStatusResponse': ('4.32', 'Federation Management', 'Federation Restore Status Response service'),
 'federationRestored': ('4.29', 'Federation Management', 'Federation Restored service'),
 'federationSaveStatusResponse': ('4.23', 'Federation Management', 'Federation Save Status Response service'),
 'federationSaved': ('4.20', 'Federation Management', 'Federation Saved service'),
 'federationSynchronized': ('4.15', 'Federation Management', 'Federation Synchronized service'),
 'flushQueueRequest': ('8.12', 'Time Management', 'Flush Queue Request service'),
 'getAttributeHandle': ('10.11', 'Support Services', 'Get Attribute Handle service'),
 'getAttributeHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getAttributeHandleSetFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getAttributeHandleValueMapFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getAttributeName': ('10.12', 'Support Services', 'Get Attribute Name service'),
 'getAttributeSetRegionSetPairListFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getAutomaticResignDirective': ('10.2', 'Support Services', 'Get Automatic Resign Directive service'),
 'getAvailableDimensionsForClassAttribute': ('10.23',
                                             'Support Services',
                                             'Get Available Dimensions For Class Attribute service'),
 'getAvailableDimensionsForInteractionClass': ('10.24',
                                               'Support Services',
                                               'Get Available Dimensions For Interaction Class service'),
 'getDimensionHandle': ('10.25', 'Support Services', 'Get Dimension Handle service'),
 'getDimensionHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getDimensionHandleSet': ('10.28', 'Support Services', 'Get Dimension Handle Set service'),
 'getDimensionHandleSetFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getDimensionName': ('10.26', 'Support Services', 'Get Dimension Name service'),
 'getDimensionUpperBound': ('10.27', 'Support Services', 'Get Dimension Upper Bound service'),
 'getFederateHandle': ('10.4', 'Support Services', 'Get Federate Handle service'),
 'getFederateHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getFederateHandleSetFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getFederateName': ('10.5', 'Support Services', 'Get Federate Name service'),
 'getHLAversion': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getInteractionClassHandle': ('10.15', 'Support Services', 'Get Interaction Class Handle service'),
 'getInteractionClassHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getInteractionClassName': ('10.16', 'Support Services', 'Get Interaction Class Name service'),
 'getKnownObjectClassHandle': ('10.8', 'Support Services', 'Get Known Object Class Handle service'),
 'getObjectClassHandle': ('10.6', 'Support Services', 'Get Object Class Handle service'),
 'getObjectClassHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getObjectClassName': ('10.7', 'Support Services', 'Get Object Class Name service'),
 'getObjectInstanceHandle': ('10.9', 'Support Services', 'Get Object Instance Handle service'),
 'getObjectInstanceHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getObjectInstanceName': ('10.10', 'Support Services', 'Get Object Instance Name service'),
 'getMessageRetractionHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getOrderName': ('10.20', 'Support Services', 'Get Order Name service'),
 'getOrderType': ('10.19', 'Support Services', 'Get Order Type service'),
 'getParameterHandle': ('10.17', 'Support Services', 'Get Parameter Handle service'),
 'getParameterHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getParameterHandleValueMapFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getParameterName': ('10.18', 'Support Services', 'Get Parameter Name service'),
 'getRegionHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getProducingFederate': ('6.9', 'Object Management', 'Discover Object Instance service'),
 'getRangeBounds': ('10.29', 'Support Services', 'Get Range Bounds service'),
 'getRegionHandleSetFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getSentRegions': ('6.9', 'Object Management', 'Discover Object Instance service'),
 'getTimeFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getTransportationName': ('10.22', 'Support Services', 'Get Transportation Type Name service'),
 'getTransportationType': ('10.21', 'Support Services', 'Get Transportation Type Handle service'),
 'getTransportationTypeHandle': ('10.21', 'Support Services', 'Get Transportation Type Handle service'),
 'getTransportationTypeHandleFactory': ('10.44', 'Support Services', 'Disable Callbacks service'),
 'getTransportationTypeName': ('10.22', 'Support Services', 'Get Transportation Type Name service'),
 'getUpdateRateValue': ('10.13', 'Support Services', 'Get Update Rate Value service'),
 'getUpdateRateValueForAttribute': ('10.14', 'Support Services', 'Get Update Rate Value For Attribute service'),
 'hasProducingFederate': ('6.9', 'Object Management', 'Discover Object Instance service'),
 'hasSentRegions': ('6.9', 'Object Management', 'Discover Object Instance service'),
 'informAttributeOwnership': ('7.18', 'Ownership Management', 'Inform Attribute Ownership service'),
 'initiateFederateRestore': ('4.27', 'Federation Management', 'Initiate Federate Restore service'),
 'initiateFederateSave': ('4.17', 'Federation Management', 'Initiate Federate Save service'),
 'isAttributeOwnedByFederate': ('7.19', 'Ownership Management', 'Is Attribute Owned By Federate service'),
 'joinFederationExecution': ('4.9', 'Federation Management', 'Join Federation Execution service'),
 'listFederationExecutions': ('4.7', 'Federation Management', 'List Federation Executions service'),
 'localDeleteObjectInstance': ('6.16', 'Object Management', 'Local Delete Object Instance service'),
 'modifyLookahead': ('8.19', 'Time Management', 'Modify Lookahead service'),
 'multipleObjectInstanceNameReservationFailed': ('6.6',
                                                 'Object Management',
                                                 'Multiple Object Instance Names Reserved service'),
 'multipleObjectInstanceNameReservationSucceeded': ('6.6',
                                                    'Object Management',
                                                    'Multiple Object Instance Names Reserved service'),
 'negotiatedAttributeOwnershipDivestiture': ('7.3',
                                             'Ownership Management',
                                             'Negotiated Attribute Ownership Divestiture service'),
 'nextMessageRequest': ('8.10', 'Time Management', 'Next Message Request service'),
 'nextMessageRequestAvailable': ('8.11', 'Time Management', 'Next Message Request Available service'),
 'normalizeFederateHandle': ('10.31', 'Support Services', 'Normalize Federate Handle service'),
 'normalizeServiceGroup': ('10.32', 'Support Services', 'Normalize Service Group service'),
 'objectInstanceNameReservationFailed': ('6.3', 'Object Management', 'Object Instance Name Reserved service'),
 'objectInstanceNameReservationSucceeded': ('6.3', 'Object Management', 'Object Instance Name Reserved service'),
 'provideAttributeValueUpdate': ('6.20', 'Object Management', 'Provide Attribute Value Update service'),
 'publishInteractionClass': ('5.4', 'Declaration Management', 'Publish Interaction Class service'),
 'publishObjectClassAttributes': ('5.2', 'Declaration Management', 'Publish Object Class Attributes service'),
 'queryAttributeOwnership': ('7.17', 'Ownership Management', 'Query Attribute Ownership service'),
 'queryAttributeTransportationType': ('6.25', 'Object Management', 'Query Attribute Transportation Type service'),
 'queryFederationRestoreStatus': ('4.31', 'Federation Management', 'Query Federation Restore Status service'),
 'queryFederationSaveStatus': ('4.22', 'Federation Management', 'Query Federation Save Status service'),
 'queryGALT': ('8.16', 'Time Management', 'Query GALT service'),
 'queryInteractionTransportationType': ('6.29', 'Object Management', 'Query Interaction Transportation Type service'),
 'queryLITS': ('8.18', 'Time Management', 'Query LITS service'),
 'queryLogicalTime': ('8.17', 'Time Management', 'Query Logical Time service'),
 'queryLookahead': ('8.20', 'Time Management', 'Query Lookahead service'),
 'receiveInteraction': ('6.13', 'Object Management', 'Receive Interaction service'),
 'reflectAttributeValues': ('6.11', 'Object Management', 'Reflect Attribute Values service'),
 'registerFederationSynchronizationPoint': ('4.11',
                                            'Federation Management',
                                            'Register Federation Synchronization Point service'),
 'registerObjectInstance': ('6.8', 'Object Management', 'Register Object Instance service'),
 'registerObjectInstanceWithRegions': ('9.5',
                                       'Data Distribution Management',
                                       'Register Object Instance With Regions service'),
 'releaseMultipleObjectInstanceName': ('6.7', 'Object Management', 'Release Multiple Object Instance Names service'),
 'releaseObjectInstanceName': ('6.4', 'Object Management', 'Release Object Instance Name service'),
 'removeObjectInstance': ('6.15', 'Object Management', 'Remove Object Instance service'),
 'reportAttributeTransportationType': ('6.26', 'Object Management', 'Report Attribute Transportation Type service'),
 'reportFederationExecutions': ('4.8', 'Federation Management', 'Report Federation Executions service'),
 'reportInteractionTransportationType': ('6.30', 'Object Management', 'Report Interaction Transportation Type service'),
 'requestAttributeOwnershipAssumption': ('7.4',
                                         'Ownership Management',
                                         'Request Attribute Ownership Assumption service'),
 'requestAttributeOwnershipRelease': ('7.11', 'Ownership Management', 'Request Attribute Ownership Release service'),
 'requestAttributeTransportationTypeChange': ('6.23',
                                              'Object Management',
                                              'Request Attribute Transportation Type Change service'),
 'requestAttributeValueUpdate': ('6.19', 'Object Management', 'Request Attribute Value Update service'),
 'requestAttributeValueUpdateWithRegions': ('9.13',
                                            'Data Distribution Management',
                                            'Request Attribute Value Update With Regions service'),
 'requestDivestitureConfirmation': ('7.5', 'Ownership Management', 'Request Divestiture Confirmation service'),
 'requestFederationRestore': ('4.24', 'Federation Management', 'Request Federation Restore service'),
 'requestFederationRestoreFailed': ('4.25', 'Federation Management', 'Confirm Federation Restoration Request service'),
 'requestFederationRestoreSucceeded': ('4.25',
                                       'Federation Management',
                                       'Confirm Federation Restoration Request service'),
 'requestFederationSave': ('4.16', 'Federation Management', 'Request Federation Save service'),
 'requestInteractionTransportationTypeChange': ('6.27',
                                                'Object Management',
                                                'Request Interaction Transportation Type Change service'),
 'requestRetraction': ('8.22', 'Time Management', 'Request Retraction service'),
 'reserveMultipleObjectInstanceName': ('6.5', 'Object Management', 'Reserve Multiple Object Instance Names service'),
 'reserveObjectInstanceName': ('6.2', 'Object Management', 'Reserve Object Instance Name service'),
 'resignFederationExecution': ('4.10', 'Federation Management', 'Resign Federation Execution service'),
 'retract': ('8.21', 'Time Management', 'Retract service'),
 'sendInteraction': ('6.12', 'Object Management', 'Send Interaction service'),
 'sendInteractionWithRegions': ('9.12', 'Data Distribution Management', 'Send Interaction With Regions service'),
 'setAutomaticResignDirective': ('10.3', 'Support Services', 'Set Automatic Resign Directive service'),
 'setRangeBounds': ('10.30', 'Support Services', 'Set Range Bounds service'),
 'startRegistrationForObjectClass': ('5.10', 'Declaration Management', 'Start Registration For Object Class service'),
 'stopRegistrationForObjectClass': ('5.11', 'Declaration Management', 'Stop Registration For Object Class service'),
 'subscribeInteractionClass': ('5.8', 'Declaration Management', 'Subscribe Interaction Class service'),
 'subscribeInteractionClassPassively': ('5.8', 'Declaration Management', 'Subscribe Interaction Class service'),
 'subscribeInteractionClassPassivelyWithRegions': ('9.10',
                                                   'Data Distribution Management',
                                                   'Subscribe Interaction Class With Regions service'),
 'subscribeInteractionClassWithRegions': ('9.10',
                                          'Data Distribution Management',
                                          'Subscribe Interaction Class With Regions service'),
 'subscribeObjectClassAttributes': ('5.6', 'Declaration Management', 'Subscribe Object Class Attributes service'),
 'subscribeObjectClassAttributesPassively': ('5.6',
                                             'Declaration Management',
                                             'Subscribe Object Class Attributes service'),
 'subscribeObjectClassAttributesPassivelyWithRegions': ('9.8',
                                                        'Data Distribution Management',
                                                        'Subscribe Object Class Attributes With Regions service'),
 'subscribeObjectClassAttributesWithRegions': ('9.8',
                                               'Data Distribution Management',
                                               'Subscribe Object Class Attributes With Regions service'),
 'synchronizationPointAchieved': ('4.14', 'Federation Management', 'Synchronization Point Achieved service'),
 'synchronizationPointRegistrationFailed': ('4.12',
                                            'Federation Management',
                                            'Confirm Synchronization Point Registration service'),
 'synchronizationPointRegistrationSucceeded': ('4.12',
                                               'Federation Management',
                                               'Confirm Synchronization Point Registration service'),
 'timeAdvanceGrant': ('8.13', 'Time Management', 'Time Advance Grant service'),
 'timeAdvanceRequest': ('8.8', 'Time Management', 'Time Advance Request service'),
 'timeAdvanceRequestAvailable': ('8.9', 'Time Management', 'Time Advance Request Available service'),
 'timeConstrainedEnabled': ('8.6', 'Time Management', 'Time Constrained Enabled service'),
 'timeRegulationEnabled': ('8.3', 'Time Management', 'Time Regulation Enabled service'),
 'turnInteractionsOff': ('5.13', 'Declaration Management', 'Turn Interactions Off service'),
 'turnInteractionsOn': ('5.12', 'Declaration Management', 'Turn Interactions On service'),
 'turnUpdatesOffForObjectInstance': ('6.22', 'Object Management', 'Turn Updates Off For Object Instance service'),
 'turnUpdatesOnForObjectInstance': ('6.21', 'Object Management', 'Turn Updates On For Object Instance service'),
 'unassociateRegionsForUpdates': ('9.7', 'Data Distribution Management', 'Unassociate Regions For Updates service'),
 'unconditionalAttributeOwnershipDivestiture': ('7.2',
                                                'Ownership Management',
                                                'Unconditional Attribute Ownership Divestiture service'),
 'unpublishInteractionClass': ('5.5', 'Declaration Management', 'Unpublish Interaction Class service'),
 'unpublishObjectClass': ('5.3', 'Declaration Management', 'Unpublish Object Class Attributes service'),
 'unpublishObjectClassAttributes': ('5.3', 'Declaration Management', 'Unpublish Object Class Attributes service'),
 'unsubscribeInteractionClass': ('5.9', 'Declaration Management', 'Unsubscribe Interaction Class service'),
 'unsubscribeInteractionClassWithRegions': ('9.11',
                                            'Data Distribution Management',
                                            'Unsubscribe Interaction Class With Regions service'),
 'unsubscribeObjectClass': ('5.7', 'Declaration Management', 'Unsubscribe Object Class Attributes service'),
 'unsubscribeObjectClassAttributes': ('5.7', 'Declaration Management', 'Unsubscribe Object Class Attributes service'),
 'unsubscribeObjectClassAttributesWithRegions': ('9.9',
                                                 'Data Distribution Management',
                                                 'Unsubscribe Object Class Attributes With Regions service'),
 'updateAttributeValues': ('6.10', 'Object Management', 'Update Attribute Values service')}

METHOD_REFERENCES: dict[str, SpecReference] = {
    method: SpecReference(IEEE_1516_1_2010, section, title, group)
    for method, (section, group, title) in _METHOD_REFERENCE_DATA.items()
}


def snake_to_lower_camel(name: str) -> str:
    parts = name.split("_")
    if not parts:
        return name
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def method_reference(method_name: str) -> SpecReference | None:
    """Return the spec reference for a lowerCamelCase or snake_case API method.

    The generated Java API names occasionally contain all-capital acronyms
    such as ``MIM``.  After the normal snake_case conversion, fall back to a
    case-insensitive lookup so Python aliases retain the same section link.
    """
    direct = METHOD_REFERENCES.get(method_name)
    if direct is not None:
        return direct
    camel = snake_to_lower_camel(method_name)
    converted = METHOD_REFERENCES.get(camel)
    if converted is not None:
        return converted
    lowered = camel.lower()
    for key, ref in METHOD_REFERENCES.items():
        if key.lower() == lowered:
            return ref
    return None


def method_label(method_name: str) -> str:
    ref = method_reference(method_name)
    return ref.label if ref else "unmapped HLA service"


def iter_method_references(prefixes: Iterable[str] | None = None):
    prefixes_tuple = tuple(prefixes or ())
    for method in sorted(METHOD_REFERENCES):
        if not prefixes_tuple or method.startswith(prefixes_tuple):
            yield method, METHOD_REFERENCES[method]


__all__ = [
    "FOM_REFERENCES",
    "METHOD_REFERENCES",
    "SERVICE_AREAS",
    "SpecReference",
    "iter_method_references",
    "method_label",
    "method_reference",
    "snake_to_lower_camel",
]
