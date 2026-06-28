"""Callback control and asynchronous-delivery services for the Python RTI backend."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import (
    AsynchronousDeliveryAlreadyDisabled,
    AsynchronousDeliveryAlreadyEnabled,
    CallNotAllowedFromWithinCallback,
    FederateInternalError,
)
from .state import CallbackEvent, FederateState, FederationState

if TYPE_CHECKING:
    from .state import PythonRTIConfig


class _CallbacksContext(Protocol):
    config: "PythonRTIConfig"
    state: FederateState
    delivered_callback_count: int

    def _require_connected(self) -> None: ...

    def _require_joined(self) -> FederationState: ...

    def _ensure_no_save_or_restore_in_progress(self, federation: FederationState) -> None: ...

    def _refresh_mom_federate_object(
        self,
        federation: FederationState,
        federate: FederateState,
        *,
        notify: bool,
    ) -> None: ...

    def _finalize_connection_lost_disconnect(self, federate: FederateState) -> None: ...


if TYPE_CHECKING:
    class _CallbacksMixinBase(_CallbacksContext):
        pass
else:
    class _CallbacksMixinBase:
        pass


class PythonRTICallbacksMixin(_CallbacksMixinBase):
    def _deliver(self, target: FederateState, method_name: str, *args: Any) -> None:
        if target.ambassador is None:
            return
        if target.callback_model is CallbackModel.HLA_IMMEDIATE and self.config.immediate_callbacks_inline:
            self._invoke_callback(target, method_name, args)
        else:
            target.queue.append(CallbackEvent(method_name, tuple(args)))

    def _invoke_callback(self, target: FederateState, method_name: str, args: tuple[Any, ...]) -> None:
        if target.ambassador is None:
            return
        if target.in_callback:
            raise CallNotAllowedFromWithinCallback("Nested callback invocation is not allowed")
        try:
            target.in_callback = True
            getattr(target.ambassador, method_name)(*args)
            self.delivered_callback_count += 1
            target.callback_counts[method_name] = target.callback_counts.get(method_name, 0) + 1
            target.recent_callbacks.append(method_name)
            if len(target.recent_callbacks) > 16:
                del target.recent_callbacks[:-16]
        except FederateInternalError:
            raise
        except BaseException as exc:
            raise FederateInternalError(f"Python FederateAmbassador.{method_name} failed: {exc}", cause=exc) from exc
        finally:
            target.in_callback = False
        if method_name == "connectionLost" and target.disconnect_pending_after_connection_lost:
            self._finalize_connection_lost_disconnect(target)

    def _svc_enableCallbacks(self) -> None:
        self._require_connected()
        federation = self.state.federation
        if federation is not None:
            self._ensure_no_save_or_restore_in_progress(federation)
        self.state.callbacks_enabled = True

    def _svc_disableCallbacks(self) -> None:
        self._require_connected()
        federation = self.state.federation
        if federation is not None:
            self._ensure_no_save_or_restore_in_progress(federation)
        self.state.callbacks_enabled = False

    def _svc_evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:
        self._require_connected()
        if self.state.in_callback:
            raise CallNotAllowedFromWithinCallback("Cannot evoke callbacks from within a callback")
        if not self.state.callbacks_enabled or not self.state.queue:
            return False
        event = self.state.queue.popleft()
        self._invoke_callback(self.state, event.method_name, event.args)
        return bool(self.state.queue)

    def _svc_evokeMultipleCallbacks(self, approximateMinimumTimeInSeconds: float, approximateMaximumTimeInSeconds: float) -> bool:
        self._require_connected()
        if self.state.in_callback:
            raise CallNotAllowedFromWithinCallback("Cannot evoke callbacks from within a callback")
        delivered = False
        while self.state.callbacks_enabled and self.state.queue:
            event = self.state.queue.popleft()
            self._invoke_callback(self.state, event.method_name, event.args)
            delivered = True
        return delivered

    def _svc_enableAsynchronousDelivery(self) -> None:
        federation: FederationState = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if self.state.asynchronous_delivery_enabled:
            raise AsynchronousDeliveryAlreadyEnabled("Asynchronous delivery is already enabled")
        self.state.asynchronous_delivery_enabled = True
        self._refresh_mom_federate_object(federation, self.state, notify=True)

    def _svc_disableAsynchronousDelivery(self) -> None:
        federation: FederationState = self._require_joined()
        self._ensure_no_save_or_restore_in_progress(federation)
        if not self.state.asynchronous_delivery_enabled:
            raise AsynchronousDeliveryAlreadyDisabled("Asynchronous delivery is already disabled")
        self.state.asynchronous_delivery_enabled = False
        self._refresh_mom_federate_object(federation, self.state, notify=True)


__all__ = ["PythonRTICallbacksMixin"]
