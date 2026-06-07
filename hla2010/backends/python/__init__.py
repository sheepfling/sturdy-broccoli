"""In-memory Python RTI backend package.

This package is the organized import surface for the pure-Python backend:
state/model types, the shared in-memory engine, file reporting helpers, the
concrete backend, and factories live in separate modules.
"""
from __future__ import annotations

from importlib import import_module
from typing import Any

CallbackEvent: Any
FederateState: Any
FederateHandleSaveStatusPair: Any
FederateRestoreStatus: Any
FederationState: Any
InMemoryRTIEngine: Any
MessageRetractionReturn: Any
PythonRTIBackend: Any
PythonRTICallbacksMixin: Any
PythonRTIConfig: Any
PythonRTIDeclarationMixin: Any
PythonRTIDdmMixin: Any
PythonRTIFederationMixin: Any
PythonRTIMomMixin: Any
PythonRTIObjectMixin: Any
PythonRTIOwnershipMixin: Any
PythonRTISaveRestoreMixin: Any
PythonRTIServiceReportFiles: Any
PythonRTITimeMixin: Any
QueuedTimeMessage: Any
RangeBounds: Any
SupplementalReflectInfo: Any
SupplementalReceiveInfo: Any
SupplementalRemoveInfo: Any
TimeAdvanceRequestState: Any
TimeQueryReturn: Any
TimedMessage: Any
create_python_ambassador: Any
create_python_backend: Any
rti_ambassador: Any

_EXPORTS = {
    "CallbackEvent": (".state", "CallbackEvent"),
    "FederateState": (".state", "FederateState"),
    "FederateHandleSaveStatusPair": (".state", "FederateHandleSaveStatusPair"),
    "FederateRestoreStatus": (".state", "FederateRestoreStatus"),
    "FederationState": (".state", "FederationState"),
    "InMemoryRTIEngine": (".engine", "InMemoryRTIEngine"),
    "MessageRetractionReturn": (".state", "MessageRetractionReturn"),
    "PythonRTIBackend": (".backend", "PythonRTIBackend"),
    "PythonRTICallbacksMixin": (".callbacks", "PythonRTICallbacksMixin"),
    "PythonRTIConfig": (".state", "PythonRTIConfig"),
    "PythonRTIDeclarationMixin": (".declaration", "PythonRTIDeclarationMixin"),
    "PythonRTIDdmMixin": (".ddm", "PythonRTIDdmMixin"),
    "PythonRTIFederationMixin": (".federation", "PythonRTIFederationMixin"),
    "PythonRTIMomMixin": (".mom", "PythonRTIMomMixin"),
    "PythonRTIObjectMixin": (".object", "PythonRTIObjectMixin"),
    "PythonRTIOwnershipMixin": (".ownership", "PythonRTIOwnershipMixin"),
    "PythonRTISaveRestoreMixin": (".save_restore", "PythonRTISaveRestoreMixin"),
    "PythonRTIServiceReportFiles": (".reporting", "PythonRTIServiceReportFiles"),
    "PythonRTITimeMixin": (".time", "PythonRTITimeMixin"),
    "QueuedTimeMessage": (".state", "QueuedTimeMessage"),
    "RangeBounds": (".state", "RangeBounds"),
    "SupplementalReflectInfo": (".state", "SupplementalReflectInfo"),
    "SupplementalReceiveInfo": (".state", "SupplementalReceiveInfo"),
    "SupplementalRemoveInfo": (".state", "SupplementalRemoveInfo"),
    "TimeAdvanceRequestState": (".state", "TimeAdvanceRequestState"),
    "TimeQueryReturn": (".state", "TimeQueryReturn"),
    "TimedMessage": (".state", "TimedMessage"),
    "create_python_ambassador": (".factory", "create_python_ambassador"),
    "create_python_backend": (".factory", "create_python_backend"),
    "rti_ambassador": (".factory", "rti_ambassador"),
}


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    module = import_module(module_name, __name__)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value

__all__ = [
    "CallbackEvent",
    "FederateState",
    "FederateHandleSaveStatusPair",
    "FederateRestoreStatus",
    "FederationState",
    "InMemoryRTIEngine",
    "MessageRetractionReturn",
    "PythonRTIBackend",
    "PythonRTICallbacksMixin",
    "PythonRTIConfig",
    "PythonRTIDeclarationMixin",
    "PythonRTIDdmMixin",
    "PythonRTIFederationMixin",
    "PythonRTIMomMixin",
    "PythonRTIObjectMixin",
    "PythonRTIOwnershipMixin",
    "PythonRTISaveRestoreMixin",
    "PythonRTIServiceReportFiles",
    "PythonRTITimeMixin",
    "QueuedTimeMessage",
    "RangeBounds",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
    "TimeAdvanceRequestState",
    "TimeQueryReturn",
    "TimedMessage",
    "create_python_ambassador",
    "create_python_backend",
    "rti_ambassador",
]
