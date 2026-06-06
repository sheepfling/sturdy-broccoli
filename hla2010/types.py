"""Small value objects and collection aliases for the HLA Python API scaffold.

Attribution: "Reprinted with permission from IEEE 1516.1(TM)-2010".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .handles import *
from .enums import RestoreStatus, SaveStatus


@dataclass(frozen=True)
class RangeBounds:
    lower_bound: int
    upper_bound: int


@dataclass(frozen=True)
class AttributeRegionAssociation:
    attributes: AttributeHandleSet
    regions: RegionHandleSet


@dataclass(frozen=True)
class MessageRetractionReturn:
    handle: MessageRetractionHandle
    time: Any | None = None


@dataclass(frozen=True)
class TimeQueryReturn:
    time_is_valid: bool
    time: Any | None = None


@dataclass(frozen=True)
class FederateHandleSaveStatusPair:
    federate_handle: FederateHandle
    save_status: SaveStatus


@dataclass(frozen=True)
class FederateRestoreStatus:
    pre_restore_handle: FederateHandle
    post_restore_handle: FederateHandle
    restore_status: RestoreStatus


@dataclass(frozen=True)
class FederationExecutionInformation:
    federation_execution_name: str
    logical_time_implementation_name: str | None = None


FederationExecutionInformationSet = set[FederationExecutionInformation]

__all__ = [name for name in globals() if not name.startswith("_")]
