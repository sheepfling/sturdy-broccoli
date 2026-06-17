"""IEEE 1516.1-2025 RTI shim backend."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from hla.rti.plugin_api import BackendRequest
from hla.rti1516_2025.datatypes import (
    ConfigurationResult,
    FederationExecutionInformation,
    FederationExecutionInformationSet,
    FederationExecutionMemberInformation,
    FederationExecutionMemberInformationSet,
)
from hla.rti1516_2025.enums import AdditionalSettingsResultCode, CallbackModel, ResignAction
from hla.rti1516_2025.exceptions import (
    AlreadyConnected,
    FederateAlreadyExecutionMember,
    FederateNameAlreadyInUse,
    FederateNotExecutionMember,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    NotConnected,
    RTIinternalError,
)
from hla.rti1516_2025.federate_ambassador import FederateAmbassador


@dataclass(slots=True)
class _FederationRecord:
    logical_time_implementation_name: str = ""
    members: dict[str, str] = field(default_factory=dict)


_FEDERATION_REGISTRY: dict[str, _FederationRecord] = {}


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
        self._federation_name: str | None = None
        self._federate_name: str | None = None
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
        self._release_join()
        self._connected = False
        self._joined = False
        self._federation_name = None
        self._federate_name = None
        self._federate_ambassador = None
        self._callback_model = None

    def createFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("createFederationExecution", *args, **kwargs)
        federation_name = self._extract_federation_name(args, kwargs)
        if federation_name in _FEDERATION_REGISTRY:
            raise FederationExecutionAlreadyExists(federation_name)
        _FEDERATION_REGISTRY[federation_name] = _FederationRecord(
            logical_time_implementation_name=self._extract_logical_time_implementation_name(args, kwargs)
        )

    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> None:  # noqa: N802
        self._record("destroyFederationExecution", *args, **kwargs)
        federation_name = self._extract_federation_name(args, kwargs)
        federation = _FEDERATION_REGISTRY.get(federation_name)
        if federation is None:
            raise FederationExecutionDoesNotExist(federation_name)
        if federation.members:
            raise RTIinternalError(f"Cannot destroy federation {federation_name!r} while members remain joined")
        del _FEDERATION_REGISTRY[federation_name]

    def listFederationExecutions(self) -> None:  # noqa: N802
        self._record("listFederationExecutions")
        self._require_connected("listFederationExecutions")
        report = FederationExecutionInformationSet(
            FederationExecutionInformation(
                federationExecutionName=federation_name,
                logicalTimeImplementationName=record.logical_time_implementation_name,
            )
            for federation_name, record in sorted(_FEDERATION_REGISTRY.items())
        )
        self._deliver_callback("reportFederationExecutions", report)

    def listFederationExecutionMembers(self, federationName: str) -> None:  # noqa: N802
        self._record("listFederationExecutionMembers", federationName)
        self._require_connected("listFederationExecutionMembers")
        federation = _FEDERATION_REGISTRY.get(federationName)
        if federation is None:
            self._deliver_callback("reportFederationExecutionDoesNotExist", federationName)
            return
        report = FederationExecutionMemberInformationSet(
            FederationExecutionMemberInformation(federateName=name, federateType=federate_type)
            for name, federate_type in sorted(federation.members.items())
        )
        self._deliver_callback("reportFederationExecutionMembers", federationName, report)

    def joinFederationExecution(self, *args: Any, **kwargs: Any):  # noqa: N802
        self._record("joinFederationExecution", *args, **kwargs)
        self._require_connected("joinFederationExecution")
        federation_name, federate_name = self._extract_join_names(args, kwargs)
        federation = _FEDERATION_REGISTRY.get(federation_name)
        if federation is None:
            raise FederationExecutionDoesNotExist(federation_name)
        if self._joined:
            raise FederateAlreadyExecutionMember("2025 shim RTI ambassador is already joined")
        if federate_name is not None and federate_name in federation.members:
            raise FederateNameAlreadyInUse(federate_name)
        federate_type = self._extract_federate_type(args, kwargs)
        if federate_name is not None:
            federation.members[federate_name] = federate_type
        self._federation_name = federation_name
        self._federate_name = federate_name
        self._joined = True
        return None

    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        self._record("resignFederationExecution", resignAction)
        self._require_joined("resignFederationExecution")
        self._release_join()
        self._joined = False
        self._federation_name = None
        self._federate_name = None

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

    def _deliver_callback(self, method_name: str, *args: Any) -> None:
        if self._federate_ambassador is None:
            raise RTIinternalError(f"Cannot deliver {method_name} without a connected federate ambassador")
        callback = getattr(self._federate_ambassador, method_name, None)
        if callback is None:
            raise RTIinternalError(f"Connected federate ambassador does not implement {method_name}")
        callback(*args)

    def _require_connected(self, method_name: str) -> None:
        if not self._connected:
            raise NotConnected(f"Cannot call {method_name} before connect")

    def _require_joined(self, method_name: str) -> None:
        self._require_connected(method_name)
        if not self._joined:
            raise FederateNotExecutionMember(f"Cannot call {method_name} before joinFederationExecution")

    def _extract_federation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federation_name = kwargs.get("federationName")
        if federation_name is None:
            federation_name = kwargs.get("federation_name")
        if federation_name is None:
            if len(args) >= 3:
                federation_name = args[2]
            elif len(args) >= 2:
                federation_name = args[1]
            elif args:
                federation_name = args[0]
        if not isinstance(federation_name, str) or not federation_name:
            raise RTIinternalError("2025 shim RTI ambassador requires a federation name")
        return federation_name

    def _extract_join_names(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[str, str | None]:
        federation_name = self._extract_federation_name(args, kwargs)
        federate_name = kwargs.get("federateName")
        if federate_name is None:
            federate_name = kwargs.get("federate_name")
        if federate_name is None and len(args) >= 3:
            federate_name = args[0]
        if federate_name is not None and not isinstance(federate_name, str):
            raise RTIinternalError("2025 shim RTI ambassador requires federateName to be a string when provided")
        return federation_name, federate_name

    def _extract_federate_type(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        federate_type = kwargs.get("federateType")
        if federate_type is None:
            federate_type = kwargs.get("federate_type")
        if federate_type is None and len(args) >= 2:
            federate_type = args[1]
        if not isinstance(federate_type, str) or not federate_type:
            raise RTIinternalError("2025 shim RTI ambassador requires federateType to be a non-empty string")
        return federate_type

    def _extract_logical_time_implementation_name(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        value = kwargs.get("logicalTimeImplementationName")
        if value is None:
            value = kwargs.get("logical_time_implementation_name")
        if value is None and len(args) >= 4:
            value = args[3]
        if value is None:
            return ""
        if not isinstance(value, str):
            raise RTIinternalError("2025 shim RTI ambassador requires logicalTimeImplementationName to be a string")
        return value

    def _release_join(self) -> None:
        if self._federation_name is None or self._federate_name is None:
            return
        federation = _FEDERATION_REGISTRY.get(self._federation_name)
        if federation is not None:
            federation.members.pop(self._federate_name, None)


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
