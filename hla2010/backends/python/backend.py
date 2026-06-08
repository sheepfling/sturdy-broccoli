"""Concrete in-memory Python RTI backend implementation."""
from __future__ import annotations

from typing import Any

from ... import time_management as tm
from ...exceptions import (
    FederateNotExecutionMember,
    NotConnected,
    RTIexception,
)
from ...fom import FOMCatalog, FOMResolver
from ...service_reporting import ServiceReportSink
from ...time import LogicalTimeFactory
from ..base import BackendInfo, Invocation, RTIBackend, UnsupportedBackendService
from ..java_common import resolve_java_arguments
from .callbacks import PythonRTICallbacksMixin
from .ddm import PythonRTIDdmMixin
from .declaration import PythonRTIDeclarationMixin
from .engine import InMemoryRTIEngine
from .federation import PythonRTIFederationMixin
from .fom_helpers import PythonRTIFomMixin
from .mom import PythonRTIMomMixin
from .object import PythonRTIObjectMixin
from .ownership import PythonRTIOwnershipMixin
from .reporting import PythonRTIServiceReportFiles
from .save_restore import PythonRTISaveRestoreMixin
from .state import (
    MOM_TEXT_ENCODING,
    FederateState,
    FederationState,
    PythonRTIConfig,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
)
from .subscriptions import PythonRTISubscriptionMixin
from .support import PythonRTISupportMixin
from .time import PythonRTITimeMixin


def _enum_name(value: Any) -> str:
    name_attr = getattr(value, "name", None)
    if isinstance(name_attr, str):
        return name_attr
    if callable(name_attr):
        try:
            return str(name_attr())
        except Exception:
            pass
    return str(value)


def _as_mom_bytes(value: Any) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return str(value).encode(MOM_TEXT_ENCODING)


def _handle_value(value: Any) -> str:
    return str(getattr(value, "value", value))


class PythonRTIBackend(
    PythonRTIFomMixin,
    PythonRTIFederationMixin,
    PythonRTISaveRestoreMixin,
    PythonRTICallbacksMixin,
    PythonRTISubscriptionMixin,
    PythonRTIDeclarationMixin,
    PythonRTIObjectMixin,
    PythonRTIMomMixin,
    PythonRTIOwnershipMixin,
    PythonRTITimeMixin,
    PythonRTIDdmMixin,
    PythonRTISupportMixin,
    RTIBackend,
):
    """A dependency-free RTIBackend implemented entirely in Python."""

    def __init__(
        self,
        *,
        engine: InMemoryRTIEngine | None = None,
        config: PythonRTIConfig | None = None,
        federate_state: FederateState | None = None,
    ) -> None:
        self.engine = engine or InMemoryRTIEngine()
        self.config = config or PythonRTIConfig(name=self.engine.name)
        self.fom_resolver = (
            FOMResolver(
                base_paths=tuple(self.config.fom_search_paths),
                require_local_parse=(self.config.require_fom_parse or self.config.strict_fom_loading),
            )
            if (self.config.fom_search_paths or self.config.require_fom_parse or self.config.strict_fom_loading)
            else self.engine.fom_resolver
        )
        self.state = federate_state or self.engine.new_federate_state()
        setattr(self.state, "backend", self)
        self.delivered_callback_count = 0
        self.service_report_sink = (
            ServiceReportSink(self.config.service_report_file, truncate=self.config.service_report_file_truncate)
            if self.config.service_report_file
            else None
        )
        self.service_report_files = PythonRTIServiceReportFiles(directory=self.config.service_report_directory)
        self.info = BackendInfo(
            name=self.config.name,
            kind="python/in-memory",
            version=self.config.version,
            details={"engine": self.engine.name, "backend_id": self.state.backend_id},
        )

    def invoke(self, invocation: Invocation) -> Any:
        service = getattr(self, f"_svc_{invocation.method_name}", None)
        if service is None:
            raise UnsupportedBackendService(f"Python in-memory RTI does not yet implement {invocation.method_name}")
        args = resolve_java_arguments(invocation)
        try:
            result = service(*args)
        except RTIexception as exc:
            self._report_service_invocation(invocation.method_name, success=False, exception_name=exc.__class__.__name__, args=args)
            raise
        except Exception as exc:
            self._report_service_invocation(invocation.method_name, success=False, exception_name=exc.__class__.__name__, args=args)
            raise
        self._report_service_invocation(invocation.method_name, success=True, exception_name="", args=args, result=result)
        return result

    def pending_callback_count(self) -> int:
        return len(self.state.queue)

    def current_fom_catalog(self) -> FOMCatalog:
        federation = self._require_joined()
        return federation.fom_catalog

    def current_fom_summary(self) -> dict[str, Any]:
        return self._current_fom_summary()

    def close(self) -> None:
        try:
            if self.state.connected and self.state.handle is not None:
                from ...enums import ResignAction

                self._svc_resignFederationExecution(ResignAction.NO_ACTION)
            if self.state.connected:
                self._svc_disconnect()
        except Exception:
            pass

    def _enum_name(self, value: Any) -> str:
        return _enum_name(value)

    def _require_connected(self) -> None:
        if not self.state.connected:
            raise NotConnected("RTI ambassador is not connected")

    def _require_joined(self) -> FederationState:
        self._require_connected()
        federation = self.state.federation
        if self.state.handle is None or federation is None:
            raise FederateNotExecutionMember("Federate has not joined a federation execution")
        return federation

    def _federate_name(self, state: FederateState | None = None) -> str:
        state = state or self.state
        return state.name or f"Federate-{state.backend_id}"

    def _enforce_fom_names(self, federation: FederationState) -> bool:
        return bool(self.config.strict_fom_lookup and federation.fom_catalog.modules)

    def _time_factory(self) -> LogicalTimeFactory[Any, Any]:
        federation = self.state.federation
        if federation is not None:
            return federation.time_factory
        return self.engine.time_factories.get(self.config.default_logical_time_implementation_name)

    def _time_lt(self, a: Any, b: Any) -> bool:
        return tm.time_lt(a, b)

    def _time_le(self, a: Any, b: Any) -> bool:
        return tm.time_le(a, b)

    def _queued_tso_messages(self, federation: FederationState, fed: FederateState):
        return tm.queued_tso_messages(federation, fed)

    def _compute_grant_decision(self, federation: FederationState, fed: FederateState, request: Any, **kwargs: Any):
        return tm.compute_grant_decision(federation, fed, request, **kwargs)

    def _scheduled_save_time_reached(self, fed: FederateState, save_time: Any, *, next_grant_time: Any | None = None) -> bool:
        return tm.scheduled_save_time_reached(fed, save_time, next_grant_time=next_grant_time)

__all__ = [
    "PythonRTIBackend",
    "InMemoryRTIEngine",
    "PythonRTIConfig",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
]
