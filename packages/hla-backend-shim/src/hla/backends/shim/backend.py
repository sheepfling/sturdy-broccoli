"""IEEE 1516.1-2025 RTI shim backend."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from hla.rti.plugin_api import BackendRequest
from hla.rti1516_2025.datatypes import ConfigurationResult
from hla.rti1516_2025.enums import AdditionalSettingsResultCode, CallbackModel, ResignAction
from hla.rti1516_2025.exceptions import AlreadyConnected, FederateNotExecutionMember, NotConnected, RTIinternalError
from hla.rti1516_2025.federate_ambassador import FederateAmbassador


@dataclass(frozen=True, slots=True)
class ShimBackendInfo:
    name: str = "shim-2025"
    kind: str = "shim/2025"
    version: str = "0.13.0"
    details: dict[str, Any] = field(default_factory=lambda: {"spec": "rti1516_2025"})


class Shim2025RTIAmbassador:
    """Minimal 2025 RTI ambassador for factory and adapter development."""

    backend_info = ShimBackendInfo()

    def __init__(self) -> None:
        self._connected = False
        self._joined = False
        self._federate_ambassador: FederateAmbassador | None = None
        self._callback_model: CallbackModel | None = None
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def joined(self) -> bool:
        return self._joined

    def connect(
        self,
        federateAmbassador: FederateAmbassador,
        callbackModel: CallbackModel,
        configuration: Any | None = None,
        credentials: Any | None = None,
    ) -> ConfigurationResult:
        self._record("connect", federateAmbassador, callbackModel, configuration, credentials)
        if self._connected:
            raise AlreadyConnected("2025 shim RTI ambassador is already connected")
        self._connected = True
        self._federate_ambassador = federateAmbassador
        self._callback_model = callbackModel
        return ConfigurationResult(
            configurationUsed=configuration is not None,
            addressUsed=False,
            additionalSettingsResultCode=AdditionalSettingsResultCode.SETTINGS_IGNORED,
            message="hla-backend-shim accepted the 2025 connection request",
        )

    def disconnect(self) -> None:
        self._record("disconnect")
        if not self._connected:
            raise NotConnected("2025 shim RTI ambassador is not connected")
        self._connected = False
        self._joined = False
        self._federate_ambassador = None
        self._callback_model = None

    def createFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("createFederationExecution", *args, **kwargs)

    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("destroyFederationExecution", *args, **kwargs)

    def joinFederationExecution(self, *args: Any, **kwargs: Any):  # noqa: N802
        self._record("joinFederationExecution", *args, **kwargs)
        self._require_connected("joinFederationExecution")
        self._joined = True
        return None

    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        self._record("resignFederationExecution", resignAction)
        self._require_joined("resignFederationExecution")
        self._joined = False

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:  # noqa: N802
        self._record("evokeCallback", approximateMinimumTimeInSeconds)
        self._require_connected("evokeCallback")
        return False

    def evokeMultipleCallbacks(  # noqa: N802
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:
        self._record("evokeMultipleCallbacks", approximateMinimumTimeInSeconds, approximateMaximumTimeInSeconds)
        self._require_connected("evokeMultipleCallbacks")
        return False

    def enableCallbacks(self) -> None:  # noqa: N802
        self._record("enableCallbacks")
        self._require_connected("enableCallbacks")

    def disableCallbacks(self) -> None:  # noqa: N802
        self._record("disableCallbacks")
        self._require_connected("disableCallbacks")

    def getHLAversion(self) -> str:  # noqa: N802
        self._record("getHLAversion")
        return "IEEE 1516.1-2025"

    def close(self) -> None:
        if self._connected:
            self.disconnect()

    def __enter__(self) -> "Shim2025RTIAmbassador":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.close()
        return False

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name.startswith("_"):
            raise AttributeError(name)

        def _unsupported(*args: Any, **kwargs: Any) -> Any:
            self._record(name, *args, **kwargs)
            raise RTIinternalError(f"hla-backend-shim does not implement IEEE 1516.1-2025 service {name}")

        return _unsupported

    def _record(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((method_name, args, dict(kwargs)))

    def _require_connected(self, method_name: str) -> None:
        if not self._connected:
            raise NotConnected(f"Cannot call {method_name} before connect")

    def _require_joined(self, method_name: str) -> None:
        self._require_connected(method_name)
        if not self._joined:
            raise FederateNotExecutionMember(f"Cannot call {method_name} before joinFederationExecution")


class Shim2025Backend:
    """Factory-facing backend wrapper that returns a 2025-native ambassador."""

    info = ShimBackendInfo()

    def __init__(self, request: BackendRequest):
        self.request = request

    def create_rti_ambassador(self) -> Shim2025RTIAmbassador:
        return Shim2025RTIAmbassador()


def create_shim_backend(request: BackendRequest) -> Shim2025Backend:
    if request.spec.name != "rti1516_2025":
        raise ValueError(f"shim backend only supports rti1516_2025, not {request.spec.name!r}")
    return Shim2025Backend(request)


__all__ = ["Shim2025Backend", "Shim2025RTIAmbassador", "create_shim_backend"]
