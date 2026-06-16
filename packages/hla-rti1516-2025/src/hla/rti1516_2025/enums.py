"""IEEE 1516.1-2025 enum models with explicit stable integer values.

Sources: Java enum files and C++ RTI/Enums.h; AuthorizationResultCode from auth/AuthorizationResult.
"""

from __future__ import annotations

from enum import IntEnum


class AdditionalSettingsResultCode(IntEnum):
    SETTINGS_IGNORED = 0
    SETTINGS_FAILED_TO_PARSE = 1
    SETTINGS_APPLIED = 2


class CallbackModel(IntEnum):
    HLA_IMMEDIATE = 0
    HLA_EVOKED = 1


class OrderType(IntEnum):
    RECEIVE = 1
    TIMESTAMP = 2


class ResignAction(IntEnum):
    UNCONDITIONALLY_DIVEST_ATTRIBUTES = 0
    DELETE_OBJECTS = 1
    CANCEL_PENDING_OWNERSHIP_ACQUISITIONS = 2
    DELETE_OBJECTS_THEN_DIVEST = 3
    CANCEL_THEN_DELETE_THEN_DIVEST = 4
    NO_ACTION = 5


class RestoreFailureReason(IntEnum):
    RTI_UNABLE_TO_RESTORE = 0
    FEDERATE_REPORTED_FAILURE_DURING_RESTORE = 1
    FEDERATE_RESIGNED_DURING_RESTORE = 2
    RTI_DETECTED_FAILURE_DURING_RESTORE = 3
    RESTORE_ABORTED = 4


class RestoreStatus(IntEnum):
    NO_RESTORE_IN_PROGRESS = 0
    FEDERATE_RESTORE_REQUEST_PENDING = 1
    FEDERATE_WAITING_FOR_RESTORE_TO_BEGIN = 2
    FEDERATE_PREPARED_TO_RESTORE = 3
    FEDERATE_RESTORING = 4
    FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE = 5


class SaveFailureReason(IntEnum):
    RTI_UNABLE_TO_SAVE = 0
    FEDERATE_REPORTED_FAILURE_DURING_SAVE = 1
    FEDERATE_RESIGNED_DURING_SAVE = 2
    RTI_DETECTED_FAILURE_DURING_SAVE = 3
    SAVE_TIME_CANNOT_BE_HONORED = 4
    SAVE_ABORTED = 5


class SaveStatus(IntEnum):
    NO_SAVE_IN_PROGRESS = 0
    FEDERATE_INSTRUCTED_TO_SAVE = 1
    FEDERATE_SAVING = 2
    FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE = 3


class ServiceGroup(IntEnum):
    FEDERATION_MANAGEMENT = 0
    DECLARATION_MANAGEMENT = 1
    OBJECT_MANAGEMENT = 2
    OWNERSHIP_MANAGEMENT = 3
    TIME_MANAGEMENT = 4
    DATA_DISTRIBUTION_MANAGEMENT = 5
    SUPPORT_SERVICES = 6


class SynchronizationPointFailureReason(IntEnum):
    SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE = 0
    SYNCHRONIZATION_SET_MEMBER_NOT_JOINED = 1


class AuthorizationResultCode(IntEnum):
    AUTHORIZED = 0
    UNAUTHORIZED = 1
    INVALID_CREDENTIALS = 2
    AUTHORIZATION_ERROR = 3


# The new draft used this shorter name. Keep it as an alias while making the
# Java/C++ role explicit with AuthorizationResultCode.
AuthorizationCode = AuthorizationResultCode
