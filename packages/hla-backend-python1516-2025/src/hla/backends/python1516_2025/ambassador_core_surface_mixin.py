"""Core ambassador shell helpers for the live 2025 Python RTI lane."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from hla.backends.common import time_management as tm
from hla.backends.common.base import snake_to_lower_camel
from hla.rti1516_2025.enums import CallbackModel, OrderType, ResignAction
from hla.rti1516_2025.exceptions import (
    FederateNotExecutionMember,
    FederateOwnsAttributes,
    OwnershipAcquisitionPending,
    RTIinternalError,
)
from hla.rti1516_2025.federate_ambassador import FederateAmbassador
from hla.rti1516_2025.handles import FederateHandle

from .callback_runtime import QueuedCallback

if TYPE_CHECKING:
    from hla.backends.common import BackendInfo
    from hla.backends.python1516_2025.runtime_state import ObjectInstanceRecord, QueuedTsoCallback


class AmbassadorCoreSurfaceMixin:
    """Common shell, state, and fallback helpers for the 2025 ambassador."""

    backend_info: BackendInfo
    _DEFAULT_LOGICAL_TIME_IMPLEMENTATION: str
    _SWITCH_DEFAULTS: dict[str, bool]
    _automatic_resign_directive: ResignAction

    def __init__(self) -> None:
        self._connected = False
        self._joined = False
        self._federation_name: str | None = None
        self._federate_name: str | None = None
        self._federate_handle: FederateHandle | None = None
        self._federate_ambassador: FederateAmbassador | None = None
        self._callback_model: CallbackModel | None = None
        self._callbacks_enabled = True
        self._evoked_callback_queue: list[QueuedCallback] = []
        self._logical_time_implementation_name = self._DEFAULT_LOGICAL_TIME_IMPLEMENTATION
        self._logical_time_factory = self._get_time_factory(self._DEFAULT_LOGICAL_TIME_IMPLEMENTATION)
        self._logical_time = self._logical_time_factory.makeInitial()
        self._lookahead = self._logical_time_factory.makeZero()
        self._time_regulation_enabled = False
        self._time_constrained_enabled = False
        self._asynchronous_delivery_enabled = False
        self._pending_time_advance: tm.TimeAdvanceRequestState | None = None
        self._switches = dict(self._SWITCH_DEFAULTS)
        self._automatic_resign_directive = ResignAction.NO_ACTION
        self._mom_report_period_seconds: float | None = None
        self._default_attribute_transportation: dict[tuple[str, str], str] = {}
        self._default_attribute_order: dict[tuple[str, str], OrderType] = {}
        self._service_report_serial_number = 0
        self._service_report_records: list[dict[str, Any]] = []
        self._known_object_classes: dict[int, str] = {}
        self._known_object_names: dict[str, int] = {}
        self._locally_deleted_objects: set[int] = set()
        self._subscribed_object_update_rates: dict[str, dict[str, float]] = {}
        self._subscribed_object_update_rate_designators: dict[str, dict[str, str]] = {}
        self._last_reflect_logical_times: dict[tuple[int, str], float] = {}
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def _verification_spawn_like(self) -> "AmbassadorCoreSurfaceMixin":
        """Create a sibling in-process ambassador for verification subroutes."""

        clone = type(self)()
        clone.backend_info = self.backend_info
        clone._logical_time_implementation_name = self._logical_time_implementation_name
        clone._logical_time_factory = self._logical_time_factory
        return clone

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def joined(self) -> bool:
        return self._joined

    def close(self) -> None:
        if self._connected:
            if self._joined:
                try:
                    self.resignFederationExecution(self._automatic_resign_directive)
                except (FederateOwnsAttributes, OwnershipAcquisitionPending):
                    self.resignFederationExecution(ResignAction.CANCEL_THEN_DELETE_THEN_DIVEST)
            self.disconnect()

    def __enter__(self) -> "AmbassadorCoreSurfaceMixin":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.close()
        return False

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name.startswith("_"):
            raise AttributeError(name)
        camel_name = snake_to_lower_camel(name)
        if camel_name != name:
            try:
                target = object.__getattribute__(self, camel_name)
            except AttributeError:
                target = None
            if callable(target):
                return lambda *args, **kwargs: target(*args, **kwargs)

        def _unsupported(*args: Any, **kwargs: Any) -> Any:
            self._record(name, *args, **kwargs)
            raise RTIinternalError(f"hla-backend-python1516-2025 does not implement IEEE 1516.1-2025 service {name}")

        return _unsupported

    def _record(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((method_name, args, dict(kwargs)))

    @staticmethod
    def _queued_tso_callback_type() -> type[QueuedTsoCallback]:
        from .runtime_state import QueuedTsoCallback as _QueuedTsoCallback

        return _QueuedTsoCallback

    def _other_member_handles(self) -> tuple[FederateHandle, ...]:
        if self._federate_handle is None:
            raise FederateNotExecutionMember("Current federate handle is not available")
        return tuple(
            handle
            for handle in self._federation_record().member_handles.values()
            if handle != self._federate_handle
        )

    @staticmethod
    def _object_instance_record_type() -> type[ObjectInstanceRecord]:
        from .runtime_state import ObjectInstanceRecord as _ObjectInstanceRecord

        return _ObjectInstanceRecord
