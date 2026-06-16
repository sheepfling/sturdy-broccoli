"""Core HLA 1516.1-2010 data records and return tuples.

Sources: Java hla/rti1516e value classes and C++ RTI/Typedefs.h structs.
"""

from __future__ import annotations

from typing import NamedTuple

from .enums import RestoreStatus, SaveStatus
from .handles import AttributeHandleSet, FederateHandle, MessageRetractionHandle, RegionHandleSet
from .logical_time import LogicalTime


class RangeBounds(NamedTuple):
    lower: int
    upper: int

    @property
    def lower_bound(self) -> int:
        return self.lower

    @property
    def upper_bound(self) -> int:
        return self.upper


class MessageRetractionReturn(NamedTuple):
    retractionHandleIsValid: bool
    handle: MessageRetractionHandle

    @property
    def retraction_handle_is_valid(self) -> bool:
        return self.retractionHandleIsValid


class FederationExecutionInformation(NamedTuple):
    federationExecutionName: str
    logicalTimeImplementationName: str

    @property
    def federation_execution_name(self) -> str:
        return self.federationExecutionName

    @property
    def logical_time_implementation_name(self) -> str:
        return self.logicalTimeImplementationName


class FederationExecutionInformationSet(set[FederationExecutionInformation]):
    pass


class FederateHandleSaveStatusPair(NamedTuple):
    handle: FederateHandle
    status: SaveStatus

    @property
    def federate_handle(self) -> FederateHandle:
        return self.handle

    @property
    def save_status(self) -> SaveStatus:
        return self.status


class FederateRestoreStatus(NamedTuple):
    preRestoreHandle: FederateHandle
    postRestoreHandle: FederateHandle
    status: RestoreStatus

    @property
    def pre_restore_handle(self) -> FederateHandle:
        return self.preRestoreHandle

    @property
    def post_restore_handle(self) -> FederateHandle:
        return self.postRestoreHandle

    @property
    def restore_status(self) -> RestoreStatus:
        return self.status


class TimeQueryReturn(NamedTuple):
    timeIsValid: bool
    time: LogicalTime | None = None

    @property
    def time_is_valid(self) -> bool:
        return self.timeIsValid


class AttributeRegionAssociation(NamedTuple):
    ahset: AttributeHandleSet
    rhset: RegionHandleSet

    @property
    def attributes(self) -> AttributeHandleSet:
        return self.ahset

    @property
    def regions(self) -> RegionHandleSet:
        return self.rhset


class SupplementalReflectInfo(NamedTuple):
    hasProducingFederateValue: bool = False
    hasSentRegionsValue: bool = False
    producingFederate: FederateHandle | None = None
    sentRegions: RegionHandleSet | None = None

    def hasProducingFederate(self) -> bool:
        return self.hasProducingFederateValue

    def hasSentRegions(self) -> bool:
        return self.hasSentRegionsValue

    def getProducingFederate(self) -> FederateHandle:
        if self.producingFederate is None:
            raise ValueError("No producing federate is present")
        return self.producingFederate

    def getSentRegions(self) -> RegionHandleSet:
        if self.sentRegions is None:
            raise ValueError("No sent regions are present")
        return self.sentRegions


class SupplementalReceiveInfo(SupplementalReflectInfo):
    pass


class SupplementalRemoveInfo(NamedTuple):
    hasProducingFederateValue: bool = False
    producingFederate: FederateHandle | None = None

    def hasProducingFederate(self) -> bool:
        return self.hasProducingFederateValue

    def getProducingFederate(self) -> FederateHandle:
        if self.producingFederate is None:
            raise ValueError("No producing federate is present")
        return self.producingFederate
