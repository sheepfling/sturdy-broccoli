"""Core HLA 1516.1-2025 data records and return tuples.

Sources: Java hla/rti1516_2025/*.java value classes and C++ RTI/*.h structs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple
from typing_extensions import Self

from .enums import AdditionalSettingsResultCode, RestoreStatus, SaveStatus
from .handles import FederateHandle, MessageRetractionHandle, RegionHandleSet
from .logical_time import LogicalTime


class _CallableString(str):
    def __call__(self) -> str:
        return str(self)


class RangeBounds(NamedTuple):
    lower: int
    upper: int


@dataclass(slots=True)
class RtiConfiguration:
    """Python model of Java/C++ RtiConfiguration.

    The HLA API exposes property-style camelCase accessors. They return callable
    strings so older call-style usage still produces the underlying value.
    """

    _configurationName: str = ""
    _rtiAddress: str = ""
    _additionalSettings: str = ""

    @staticmethod
    def createConfiguration() -> "RtiConfiguration":
        return RtiConfiguration()

    def withConfigurationName(self, configurationName: str) -> Self:
        self._configurationName = configurationName
        return self

    def withRtiAddress(self, rtiAddress: str) -> Self:
        self._rtiAddress = rtiAddress
        return self

    def withAdditionalSettings(self, additionalSettings: str) -> Self:
        self._additionalSettings = additionalSettings
        return self

    @property
    def configurationName(self) -> _CallableString:
        return _CallableString(self._configurationName)

    @property
    def rtiAddress(self) -> _CallableString:
        return _CallableString(self._rtiAddress)

    @property
    def additionalSettings(self) -> _CallableString:
        return _CallableString(self._additionalSettings)

    @property
    def configuration_name(self) -> str:
        return self._configurationName

    @property
    def rti_address(self) -> str:
        return self._rtiAddress

    @property
    def additional_settings(self) -> str:
        return self._additionalSettings


class Credentials(NamedTuple):
    type: str
    data: bytes


class ConfigurationResult(NamedTuple):
    configurationUsed: bool
    addressUsed: bool
    additionalSettingsResultCode: AdditionalSettingsResultCode
    message: str

    @property
    def additionalSettingsResult(self) -> AdditionalSettingsResultCode:
        """C++ field spelling compatibility alias."""
        return self.additionalSettingsResultCode


class MessageRetractionReturn(NamedTuple):
    retractionHandleIsValid: bool
    handle: MessageRetractionHandle


@dataclass(frozen=True, slots=True)
class FederationExecutionInformation:
    federationExecutionName: str
    logicalTimeImplementationName: str

    @property
    def logicalTimeImplementation(self) -> str:
        """Backward-compatible alias used by the first supplied Python draft."""
        return self.logicalTimeImplementationName


class FederationExecutionInformationSet(set[FederationExecutionInformation]):
    pass


class FederationExecutionMemberInformation(NamedTuple):
    federateName: str
    federateType: str


class FederationExecutionMemberInformationSet(set[FederationExecutionMemberInformation]):
    pass


class FederateHandleSaveStatusPair(NamedTuple):
    handle: FederateHandle
    status: SaveStatus


class FederateRestoreStatus(NamedTuple):
    preRestoreHandle: FederateHandle
    postRestoreHandle: FederateHandle
    status: RestoreStatus


class TimeQueryReturn(NamedTuple):
    timeIsValid: bool
    time: LogicalTime | None = None


class SupplementalReflectInfo(NamedTuple):
    """Bridge-internal callback payload model for Java-backed 2025 routes.

    The public 2025 Python callback surface flattens these fields directly into
    callback signatures, so this type intentionally remains importable from the
    datatypes module without being promoted at the package root.
    """

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
