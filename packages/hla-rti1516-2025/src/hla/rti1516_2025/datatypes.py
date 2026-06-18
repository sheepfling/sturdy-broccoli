"""Core HLA 1516.1-2025 data records and return tuples.

Sources: Java hla/rti1516_2025/*.java value classes and C++ RTI/*.h structs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Self

from .enums import AdditionalSettingsResultCode, RestoreStatus, SaveStatus
from .handles import FederateHandle, MessageRetractionHandle
from .logical_time import LogicalTime


class RangeBounds(NamedTuple):
    lower: int
    upper: int


@dataclass(slots=True)
class RtiConfiguration:
    """Python model of Java/C++ RtiConfiguration.

    The HLA API exposes Java-style getters named ``configurationName()``,
    ``rtiAddress()``, and ``additionalSettings()``.  The stored fields are kept
    private so those method names remain callable.
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

    def configurationName(self) -> str:
        return self._configurationName

    def rtiAddress(self) -> str:
        return self._rtiAddress

    def additionalSettings(self) -> str:
        return self._additionalSettings

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


class FederationExecutionInformation(NamedTuple):
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
