"""Enumerations derived from the public IEEE 1516.1-2010 Java/C++ API files.

"""
from __future__ import annotations

from enum import Enum, auto


class CallbackModel(Enum):
    HLA_IMMEDIATE = auto()
    HLA_EVOKED = auto()

class OrderType(Enum):
    RECEIVE = 1
    TIMESTAMP = 2

class ResignAction(Enum):
    UNCONDITIONALLY_DIVEST_ATTRIBUTES = auto()
    DELETE_OBJECTS = auto()
    CANCEL_PENDING_OWNERSHIP_ACQUISITIONS = auto()
    DELETE_OBJECTS_THEN_DIVEST = auto()
    CANCEL_THEN_DELETE_THEN_DIVEST = auto()
    NO_ACTION = auto()

class RestoreFailureReason(Enum):
    RTI_UNABLE_TO_RESTORE = auto()
    FEDERATE_REPORTED_FAILURE_DURING_RESTORE = auto()
    FEDERATE_RESIGNED_DURING_RESTORE = auto()
    RTI_DETECTED_FAILURE_DURING_RESTORE = auto()
    RESTORE_ABORTED = auto()

class RestoreStatus(Enum):
    NO_RESTORE_IN_PROGRESS = auto()
    FEDERATE_RESTORE_REQUEST_PENDING = auto()
    FEDERATE_WAITING_FOR_RESTORE_TO_BEGIN = auto()
    FEDERATE_PREPARED_TO_RESTORE = auto()
    FEDERATE_RESTORING = auto()
    FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE = auto()

class SaveFailureReason(Enum):
    RTI_UNABLE_TO_SAVE = auto()
    FEDERATE_REPORTED_FAILURE_DURING_SAVE = auto()
    FEDERATE_RESIGNED_DURING_SAVE = auto()
    RTI_DETECTED_FAILURE_DURING_SAVE = auto()
    SAVE_TIME_CANNOT_BE_HONORED = auto()
    SAVE_ABORTED = auto()

class SaveStatus(Enum):
    NO_SAVE_IN_PROGRESS = auto()
    FEDERATE_INSTRUCTED_TO_SAVE = auto()
    FEDERATE_SAVING = auto()
    FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE = auto()

class ServiceGroup(Enum):
    FEDERATION_MANAGEMENT = auto()
    DECLARATION_MANAGEMENT = auto()
    OBJECT_MANAGEMENT = auto()
    OWNERSHIP_MANAGEMENT = auto()
    TIME_MANAGEMENT = auto()
    DATA_DISTRIBUTION_MANAGEMENT = auto()
    SUPPORT_SERVICES = auto()

class SynchronizationPointFailureReason(Enum):
    SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE = auto()
    SYNCHRONIZATION_SET_MEMBER_NOT_JOINED = auto()

class TransportationType(Enum):
    RELIABLE = 1
    BEST_EFFORT = 2

__all__ = [
    "CallbackModel",
    "OrderType",
    "ResignAction",
    "RestoreFailureReason",
    "RestoreStatus",
    "SaveFailureReason",
    "SaveStatus",
    "ServiceGroup",
    "SynchronizationPointFailureReason",
    "TransportationType",
]
