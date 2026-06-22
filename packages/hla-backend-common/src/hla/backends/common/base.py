"""Backend-neutral RTI adapter plumbing."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Mapping, MutableMapping

from hla.rti1516e.exceptions import CallNotAllowedFromWithinCallback, RTIexception, RTIinternalError
from hla.rti1516e.raw_api import API_METADATA
from hla.rti1516e import NullFederateAmbassador, RTIambassador

RTI_METHOD_NAMES: tuple[str, ...] = tuple(API_METADATA["RTIambassador"].keys())
CALLBACK_METHOD_NAMES: tuple[str, ...] = tuple(API_METADATA["FederateAmbassador"].keys())

_CAMEL_WORD_RE = re.compile(r"(?<!^)(?=[A-Z])")


def lower_camel_to_snake(name: str) -> str:
    """Convert a source HLA lowerCamelCase method name to snake_case."""
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def snake_to_lower_camel(name: str) -> str:
    """Convert a snake_case method name to lowerCamelCase."""
    parts = name.split("_")
    if not parts:
        return name
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


_RTI_METHOD_BY_SNAKE: dict[str, str] = {
    lower_camel_to_snake(method_name): method_name
    for method_name in RTI_METHOD_NAMES
}


@dataclass(frozen=True)
class Invocation:
    """A backend-neutral RTI service invocation."""

    method_name: str
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = field(default_factory=dict)
    overloads: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class BackendInfo:
    """Descriptive information exposed by a backend."""

    name: str
    kind: str = "generic"
    version: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)


class BackendUnavailableError(RTIinternalError):
    """Raised when an optional backend dependency or runtime is unavailable."""


class BackendConversionError(RTIinternalError):
    """Raised when an adapter cannot convert a value across a backend boundary."""


class UnsupportedBackendService(RTIinternalError):
    """Raised when a backend cannot provide a requested HLA service."""


class RTIBackend(ABC):
    """Small interface implemented by concrete RTI backends."""

    info: BackendInfo

    def start(self) -> "RTIBackend":
        return self

    @abstractmethod
    def invoke(self, invocation: Invocation) -> Any:
        raise NotImplementedError

    def adapt_federate_ambassador(self, ambassador: NullFederateAmbassador) -> Any:
        return ambassador

    def close(self) -> None:
        return None

    def translate_exception(self, exc: BaseException, invocation: Invocation) -> RTIexception:
        if isinstance(exc, RTIexception):
            return exc
        return RTIinternalError(
            f"{self.__class__.__name__} failed during {invocation.method_name}: {exc}",
            cause=exc,
        )


class _SplitRuntimeRTIAmbassador(RTIambassador):
    """Split-package runtime facade with Pythonic snake_case aliases."""

    def __getattribute__(self, name: str) -> Any:
        try:
            attr = super().__getattribute__(name)
        except AttributeError:
            method_name = _RTI_METHOD_BY_SNAKE.get(name)
            if method_name is None:
                raise
            return lambda *args, **kwargs: getattr(self, method_name)(*args, **kwargs)

        if name == "__class__":
            return attr

        method_name = _RTI_METHOD_BY_SNAKE.get(name)
        if method_name is None:
            return attr

        owner_attr = getattr(type(self), name, None)
        base_attr = getattr(RTIambassador, name, None)
        if owner_attr is not None and owner_attr is not base_attr:
            return attr

        return lambda *args, **kwargs: getattr(self, method_name)(*args, **kwargs)


_SplitRuntimeRTIAmbassador.__abstractmethods__ = frozenset()


class DelegatingRTIAmbassador(_SplitRuntimeRTIAmbassador):
    """Concrete RTIambassador that delegates every service to an ``RTIBackend``."""

    def __init__(self, backend: RTIBackend, *, start: bool = True):
        self.backend = backend
        if start:
            self.backend.start()

    @property
    def backend_info(self) -> BackendInfo:
        return getattr(self.backend, "info", BackendInfo(name=self.backend.__class__.__name__))

    def _invoke(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        if method_name not in API_METADATA["RTIambassador"]:
            raise UnsupportedBackendService(f"Unknown RTIambassador service: {method_name}")
        state = getattr(self.backend, "state", None)
        if state is not None and getattr(state, "in_callback", False):
            raise CallNotAllowedFromWithinCallback("Cannot invoke RTI services from within a callback")

        adapted_args = tuple(args)
        if method_name == "connect" and adapted_args:
            first = adapted_args[0]
            adapted_args = (self.backend.adapt_federate_ambassador(first), *adapted_args[1:])

        invocation = Invocation(
            method_name=method_name,
            args=adapted_args,
            kwargs=dict(kwargs),
            overloads=tuple(API_METADATA["RTIambassador"].get(method_name, ())),
        )
        try:
            return self.backend.invoke(invocation)
        except RTIexception:
            raise
        except BaseException as exc:
            raise self.backend.translate_exception(exc, invocation) from exc

    def close(self) -> None:
        self.backend.close()

    def __enter__(self) -> "DelegatingRTIAmbassador":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.close()
        return False

    def connect(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service connect to the configured backend. Spec reference: IEEE 1516.1-2010 §4.2 Connect service (Federation Management)."""
        return self._invoke("connect", *args, **kwargs)

    def disconnect(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disconnect to the configured backend. Spec reference: IEEE 1516.1-2010 §4.3 Disconnect service (Federation Management)."""
        return self._invoke("disconnect", *args, **kwargs)

    def createFederationExecution(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service createFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.5 Create Federation Execution service (Federation Management)."""
        return self._invoke("createFederationExecution", *args, **kwargs)

    def destroyFederationExecution(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service destroyFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.6 Destroy Federation Execution service (Federation Management)."""
        return self._invoke("destroyFederationExecution", *args, **kwargs)

    def listFederationExecutions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service listFederationExecutions to the configured backend. Spec reference: IEEE 1516.1-2010 §4.7 List Federation Executions service (Federation Management)."""
        return self._invoke("listFederationExecutions", *args, **kwargs)

    def joinFederationExecution(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service joinFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.9 Join Federation Execution service (Federation Management)."""
        return self._invoke("joinFederationExecution", *args, **kwargs)

    def resignFederationExecution(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service resignFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.10 Resign Federation Execution service (Federation Management)."""
        return self._invoke("resignFederationExecution", *args, **kwargs)

    def registerFederationSynchronizationPoint(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service registerFederationSynchronizationPoint to the configured backend. Spec reference: IEEE 1516.1-2010 §4.11 Register Federation Synchronization Point service (Federation Management)."""
        return self._invoke("registerFederationSynchronizationPoint", *args, **kwargs)

    def synchronizationPointAchieved(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service synchronizationPointAchieved to the configured backend. Spec reference: IEEE 1516.1-2010 §4.14 Synchronization Point Achieved service (Federation Management)."""
        return self._invoke("synchronizationPointAchieved", *args, **kwargs)

    def requestFederationSave(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service requestFederationSave to the configured backend. Spec reference: IEEE 1516.1-2010 §4.16 Request Federation Save service (Federation Management)."""
        return self._invoke("requestFederationSave", *args, **kwargs)

    def federateSaveBegun(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service federateSaveBegun to the configured backend. Spec reference: IEEE 1516.1-2010 §4.18 Federate Save Begun service (Federation Management)."""
        return self._invoke("federateSaveBegun", *args, **kwargs)

    def federateSaveComplete(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service federateSaveComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.19 Federate Save Complete service (Federation Management)."""
        return self._invoke("federateSaveComplete", *args, **kwargs)

    def federateSaveNotComplete(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service federateSaveNotComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.19 Federate Save Complete service (Federation Management)."""
        return self._invoke("federateSaveNotComplete", *args, **kwargs)

    def abortFederationSave(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service abortFederationSave to the configured backend. Spec reference: IEEE 1516.1-2010 §4.21 Abort Federation Save service (Federation Management)."""
        return self._invoke("abortFederationSave", *args, **kwargs)

    def queryFederationSaveStatus(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryFederationSaveStatus to the configured backend. Spec reference: IEEE 1516.1-2010 §4.22 Query Federation Save Status service (Federation Management)."""
        return self._invoke("queryFederationSaveStatus", *args, **kwargs)

    def requestFederationRestore(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service requestFederationRestore to the configured backend. Spec reference: IEEE 1516.1-2010 §4.24 Request Federation Restore service (Federation Management)."""
        return self._invoke("requestFederationRestore", *args, **kwargs)

    def federateRestoreComplete(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service federateRestoreComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.28 Federate Restore Complete service (Federation Management)."""
        return self._invoke("federateRestoreComplete", *args, **kwargs)

    def federateRestoreNotComplete(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service federateRestoreNotComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.28 Federate Restore Complete service (Federation Management)."""
        return self._invoke("federateRestoreNotComplete", *args, **kwargs)

    def abortFederationRestore(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service abortFederationRestore to the configured backend. Spec reference: IEEE 1516.1-2010 §4.30 Abort Federation Restore service (Federation Management)."""
        return self._invoke("abortFederationRestore", *args, **kwargs)

    def queryFederationRestoreStatus(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryFederationRestoreStatus to the configured backend. Spec reference: IEEE 1516.1-2010 §4.31 Query Federation Restore Status service (Federation Management)."""
        return self._invoke("queryFederationRestoreStatus", *args, **kwargs)

    def publishObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service publishObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.2 Publish Object Class Attributes service (Declaration Management)."""
        return self._invoke("publishObjectClassAttributes", *args, **kwargs)

    def unpublishObjectClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unpublishObjectClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.3 Unpublish Object Class Attributes service (Declaration Management)."""
        return self._invoke("unpublishObjectClass", *args, **kwargs)

    def unpublishObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unpublishObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.3 Unpublish Object Class Attributes service (Declaration Management)."""
        return self._invoke("unpublishObjectClassAttributes", *args, **kwargs)

    def publishInteractionClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service publishInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.4 Publish Interaction Class service (Declaration Management)."""
        return self._invoke("publishInteractionClass", *args, **kwargs)

    def unpublishInteractionClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unpublishInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.5 Unpublish Interaction Class service (Declaration Management)."""
        return self._invoke("unpublishInteractionClass", *args, **kwargs)

    def subscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.6 Subscribe Object Class Attributes service (Declaration Management)."""
        return self._invoke("subscribeObjectClassAttributes", *args, **kwargs)

    def subscribeObjectClassAttributesPassively(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributesPassively to the configured backend. Spec reference: IEEE 1516.1-2010 §5.6 Subscribe Object Class Attributes service (Declaration Management)."""
        return self._invoke("subscribeObjectClassAttributesPassively", *args, **kwargs)

    def unsubscribeObjectClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unsubscribeObjectClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.7 Unsubscribe Object Class Attributes service (Declaration Management)."""
        return self._invoke("unsubscribeObjectClass", *args, **kwargs)

    def unsubscribeObjectClassAttributes(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unsubscribeObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.7 Unsubscribe Object Class Attributes service (Declaration Management)."""
        return self._invoke("unsubscribeObjectClassAttributes", *args, **kwargs)

    def subscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.8 Subscribe Interaction Class service (Declaration Management)."""
        return self._invoke("subscribeInteractionClass", *args, **kwargs)

    def subscribeInteractionClassPassively(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClassPassively to the configured backend. Spec reference: IEEE 1516.1-2010 §5.8 Subscribe Interaction Class service (Declaration Management)."""
        return self._invoke("subscribeInteractionClassPassively", *args, **kwargs)

    def unsubscribeInteractionClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unsubscribeInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.9 Unsubscribe Interaction Class service (Declaration Management)."""
        return self._invoke("unsubscribeInteractionClass", *args, **kwargs)

    def reserveObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service reserveObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.2 Reserve Object Instance Name service (Object Management)."""
        return self._invoke("reserveObjectInstanceName", *args, **kwargs)

    def releaseObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service releaseObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.4 Release Object Instance Name service (Object Management)."""
        return self._invoke("releaseObjectInstanceName", *args, **kwargs)

    def reserveMultipleObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service reserveMultipleObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.5 Reserve Multiple Object Instance Names service (Object Management)."""
        return self._invoke("reserveMultipleObjectInstanceName", *args, **kwargs)

    def releaseMultipleObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service releaseMultipleObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.7 Release Multiple Object Instance Names service (Object Management)."""
        return self._invoke("releaseMultipleObjectInstanceName", *args, **kwargs)

    def registerObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service registerObjectInstance to the configured backend. Spec reference: IEEE 1516.1-2010 §6.8 Register Object Instance service (Object Management)."""
        return self._invoke("registerObjectInstance", *args, **kwargs)

    def updateAttributeValues(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service updateAttributeValues to the configured backend. Spec reference: IEEE 1516.1-2010 §6.10 Update Attribute Values service (Object Management)."""
        return self._invoke("updateAttributeValues", *args, **kwargs)

    def sendInteraction(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service sendInteraction to the configured backend. Spec reference: IEEE 1516.1-2010 §6.12 Send Interaction service (Object Management)."""
        return self._invoke("sendInteraction", *args, **kwargs)

    def deleteObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service deleteObjectInstance to the configured backend. Spec reference: IEEE 1516.1-2010 §6.14 Delete Object Instance service (Object Management)."""
        return self._invoke("deleteObjectInstance", *args, **kwargs)

    def localDeleteObjectInstance(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service localDeleteObjectInstance to the configured backend. Spec reference: IEEE 1516.1-2010 §6.16 Local Delete Object Instance service (Object Management)."""
        return self._invoke("localDeleteObjectInstance", *args, **kwargs)

    def requestAttributeValueUpdate(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service requestAttributeValueUpdate to the configured backend. Spec reference: IEEE 1516.1-2010 §6.19 Request Attribute Value Update service (Object Management)."""
        return self._invoke("requestAttributeValueUpdate", *args, **kwargs)

    def requestAttributeTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service requestAttributeTransportationTypeChange to the configured backend. Spec reference: IEEE 1516.1-2010 §6.23 Request Attribute Transportation Type Change service (Object Management)."""
        return self._invoke("requestAttributeTransportationTypeChange", *args, **kwargs)

    def queryAttributeTransportationType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryAttributeTransportationType to the configured backend. Spec reference: IEEE 1516.1-2010 §6.25 Query Attribute Transportation Type service (Object Management)."""
        return self._invoke("queryAttributeTransportationType", *args, **kwargs)

    def requestInteractionTransportationTypeChange(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service requestInteractionTransportationTypeChange to the configured backend. Spec reference: IEEE 1516.1-2010 §6.27 Request Interaction Transportation Type Change service (Object Management)."""
        return self._invoke("requestInteractionTransportationTypeChange", *args, **kwargs)

    def queryInteractionTransportationType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryInteractionTransportationType to the configured backend. Spec reference: IEEE 1516.1-2010 §6.29 Query Interaction Transportation Type service (Object Management)."""
        return self._invoke("queryInteractionTransportationType", *args, **kwargs)

    def unconditionalAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unconditionalAttributeOwnershipDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.2 Unconditional Attribute Ownership Divestiture service (Ownership Management)."""
        return self._invoke("unconditionalAttributeOwnershipDivestiture", *args, **kwargs)

    def negotiatedAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service negotiatedAttributeOwnershipDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.3 Negotiated Attribute Ownership Divestiture service (Ownership Management)."""
        return self._invoke("negotiatedAttributeOwnershipDivestiture", *args, **kwargs)

    def confirmDivestiture(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service confirmDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.6 Confirm Divestiture service (Ownership Management)."""
        return self._invoke("confirmDivestiture", *args, **kwargs)

    def attributeOwnershipAcquisition(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipAcquisition to the configured backend. Spec reference: IEEE 1516.1-2010 §7.8 Attribute Ownership Acquisition service (Ownership Management)."""
        return self._invoke("attributeOwnershipAcquisition", *args, **kwargs)

    def attributeOwnershipAcquisitionIfAvailable(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipAcquisitionIfAvailable to the configured backend. Spec reference: IEEE 1516.1-2010 §7.9 Attribute Ownership Acquisition If Available service (Ownership Management)."""
        return self._invoke("attributeOwnershipAcquisitionIfAvailable", *args, **kwargs)

    def attributeOwnershipReleaseDenied(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipReleaseDenied to the configured backend. Spec reference: IEEE 1516.1-2010 §7.12 Attribute Ownership Release Denied service (Ownership Management)."""
        return self._invoke("attributeOwnershipReleaseDenied", *args, **kwargs)

    def attributeOwnershipDivestitureIfWanted(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipDivestitureIfWanted to the configured backend. Spec reference: IEEE 1516.1-2010 §7.13 Attribute Ownership Divestiture If Wanted service (Ownership Management)."""
        return self._invoke("attributeOwnershipDivestitureIfWanted", *args, **kwargs)

    def cancelNegotiatedAttributeOwnershipDivestiture(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service cancelNegotiatedAttributeOwnershipDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.14 Cancel Negotiated Attribute Ownership Divestiture service (Ownership Management)."""
        return self._invoke("cancelNegotiatedAttributeOwnershipDivestiture", *args, **kwargs)

    def cancelAttributeOwnershipAcquisition(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service cancelAttributeOwnershipAcquisition to the configured backend. Spec reference: IEEE 1516.1-2010 §7.15 Cancel Attribute Ownership Acquisition service (Ownership Management)."""
        return self._invoke("cancelAttributeOwnershipAcquisition", *args, **kwargs)

    def queryAttributeOwnership(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryAttributeOwnership to the configured backend. Spec reference: IEEE 1516.1-2010 §7.17 Query Attribute Ownership service (Ownership Management)."""
        return self._invoke("queryAttributeOwnership", *args, **kwargs)

    def isAttributeOwnedByFederate(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service isAttributeOwnedByFederate to the configured backend. Spec reference: IEEE 1516.1-2010 §7.19 Is Attribute Owned By Federate service (Ownership Management)."""
        return self._invoke("isAttributeOwnedByFederate", *args, **kwargs)

    def enableTimeRegulation(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableTimeRegulation to the configured backend. Spec reference: IEEE 1516.1-2010 §8.2 Enable Time Regulation service (Time Management)."""
        return self._invoke("enableTimeRegulation", *args, **kwargs)

    def disableTimeRegulation(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableTimeRegulation to the configured backend. Spec reference: IEEE 1516.1-2010 §8.4 Disable Time Regulation service (Time Management)."""
        return self._invoke("disableTimeRegulation", *args, **kwargs)

    def enableTimeConstrained(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableTimeConstrained to the configured backend. Spec reference: IEEE 1516.1-2010 §8.5 Enable Time Constrained service (Time Management)."""
        return self._invoke("enableTimeConstrained", *args, **kwargs)

    def disableTimeConstrained(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableTimeConstrained to the configured backend. Spec reference: IEEE 1516.1-2010 §8.7 Disable Time Constrained service (Time Management)."""
        return self._invoke("disableTimeConstrained", *args, **kwargs)

    def timeAdvanceRequest(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service timeAdvanceRequest to the configured backend. Spec reference: IEEE 1516.1-2010 §8.8 Time Advance Request service (Time Management)."""
        return self._invoke("timeAdvanceRequest", *args, **kwargs)

    def timeAdvanceRequestAvailable(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service timeAdvanceRequestAvailable to the configured backend. Spec reference: IEEE 1516.1-2010 §8.9 Time Advance Request Available service (Time Management)."""
        return self._invoke("timeAdvanceRequestAvailable", *args, **kwargs)

    def nextMessageRequest(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service nextMessageRequest to the configured backend. Spec reference: IEEE 1516.1-2010 §8.10 Next Message Request service (Time Management)."""
        return self._invoke("nextMessageRequest", *args, **kwargs)

    def nextMessageRequestAvailable(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service nextMessageRequestAvailable to the configured backend. Spec reference: IEEE 1516.1-2010 §8.11 Next Message Request Available service (Time Management)."""
        return self._invoke("nextMessageRequestAvailable", *args, **kwargs)

    def flushQueueRequest(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service flushQueueRequest to the configured backend. Spec reference: IEEE 1516.1-2010 §8.12 Flush Queue Request service (Time Management)."""
        return self._invoke("flushQueueRequest", *args, **kwargs)

    def enableAsynchronousDelivery(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableAsynchronousDelivery to the configured backend. Spec reference: IEEE 1516.1-2010 §8.14 Enable Asynchronous Delivery service (Time Management)."""
        return self._invoke("enableAsynchronousDelivery", *args, **kwargs)

    def disableAsynchronousDelivery(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableAsynchronousDelivery to the configured backend. Spec reference: IEEE 1516.1-2010 §8.15 Disable Asynchronous Delivery service (Time Management)."""
        return self._invoke("disableAsynchronousDelivery", *args, **kwargs)

    def queryGALT(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryGALT to the configured backend. Spec reference: IEEE 1516.1-2010 §8.16 Query GALT service (Time Management)."""
        return self._invoke("queryGALT", *args, **kwargs)

    def queryLogicalTime(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryLogicalTime to the configured backend. Spec reference: IEEE 1516.1-2010 §8.17 Query Logical Time service (Time Management)."""
        return self._invoke("queryLogicalTime", *args, **kwargs)

    def queryLITS(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryLITS to the configured backend. Spec reference: IEEE 1516.1-2010 §8.18 Query LITS service (Time Management)."""
        return self._invoke("queryLITS", *args, **kwargs)

    def modifyLookahead(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service modifyLookahead to the configured backend. Spec reference: IEEE 1516.1-2010 §8.19 Modify Lookahead service (Time Management)."""
        return self._invoke("modifyLookahead", *args, **kwargs)

    def queryLookahead(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service queryLookahead to the configured backend. Spec reference: IEEE 1516.1-2010 §8.20 Query Lookahead service (Time Management)."""
        return self._invoke("queryLookahead", *args, **kwargs)

    def retract(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service retract to the configured backend. Spec reference: IEEE 1516.1-2010 §8.21 Retract service (Time Management)."""
        return self._invoke("retract", *args, **kwargs)

    def changeAttributeOrderType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service changeAttributeOrderType to the configured backend. Spec reference: IEEE 1516.1-2010 §8.23 Change Attribute Order Type service (Time Management)."""
        return self._invoke("changeAttributeOrderType", *args, **kwargs)

    def changeInteractionOrderType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service changeInteractionOrderType to the configured backend. Spec reference: IEEE 1516.1-2010 §8.24 Change Interaction Order Type service (Time Management)."""
        return self._invoke("changeInteractionOrderType", *args, **kwargs)

    def createRegion(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service createRegion to the configured backend. Spec reference: IEEE 1516.1-2010 §9.2 Create Region service (Data Distribution Management)."""
        return self._invoke("createRegion", *args, **kwargs)

    def commitRegionModifications(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service commitRegionModifications to the configured backend. Spec reference: IEEE 1516.1-2010 §9.3 Commit Region Modifications service (Data Distribution Management)."""
        return self._invoke("commitRegionModifications", *args, **kwargs)

    def deleteRegion(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service deleteRegion to the configured backend. Spec reference: IEEE 1516.1-2010 §9.4 Delete Region service (Data Distribution Management)."""
        return self._invoke("deleteRegion", *args, **kwargs)

    def registerObjectInstanceWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service registerObjectInstanceWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.5 Register Object Instance With Regions service (Data Distribution Management)."""
        return self._invoke("registerObjectInstanceWithRegions", *args, **kwargs)

    def associateRegionsForUpdates(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service associateRegionsForUpdates to the configured backend. Spec reference: IEEE 1516.1-2010 §9.6 Associate Regions For Updates service (Data Distribution Management)."""
        return self._invoke("associateRegionsForUpdates", *args, **kwargs)

    def unassociateRegionsForUpdates(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unassociateRegionsForUpdates to the configured backend. Spec reference: IEEE 1516.1-2010 §9.7 Unassociate Regions For Updates service (Data Distribution Management)."""
        return self._invoke("unassociateRegionsForUpdates", *args, **kwargs)

    def subscribeObjectClassAttributesWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributesWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.8 Subscribe Object Class Attributes With Regions service (Data Distribution Management)."""
        return self._invoke("subscribeObjectClassAttributesWithRegions", *args, **kwargs)

    def subscribeObjectClassAttributesPassivelyWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributesPassivelyWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.8 Subscribe Object Class Attributes With Regions service (Data Distribution Management)."""
        return self._invoke("subscribeObjectClassAttributesPassivelyWithRegions", *args, **kwargs)

    def unsubscribeObjectClassAttributesWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unsubscribeObjectClassAttributesWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.9 Unsubscribe Object Class Attributes With Regions service (Data Distribution Management)."""
        return self._invoke("unsubscribeObjectClassAttributesWithRegions", *args, **kwargs)

    def subscribeInteractionClassWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClassWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.10 Subscribe Interaction Class With Regions service (Data Distribution Management)."""
        return self._invoke("subscribeInteractionClassWithRegions", *args, **kwargs)

    def subscribeInteractionClassPassivelyWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClassPassivelyWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.10 Subscribe Interaction Class With Regions service (Data Distribution Management)."""
        return self._invoke("subscribeInteractionClassPassivelyWithRegions", *args, **kwargs)

    def unsubscribeInteractionClassWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service unsubscribeInteractionClassWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.11 Unsubscribe Interaction Class With Regions service (Data Distribution Management)."""
        return self._invoke("unsubscribeInteractionClassWithRegions", *args, **kwargs)

    def sendInteractionWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service sendInteractionWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.12 Send Interaction With Regions service (Data Distribution Management)."""
        return self._invoke("sendInteractionWithRegions", *args, **kwargs)

    def requestAttributeValueUpdateWithRegions(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service requestAttributeValueUpdateWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.13 Request Attribute Value Update With Regions service (Data Distribution Management)."""
        return self._invoke("requestAttributeValueUpdateWithRegions", *args, **kwargs)

    def getAutomaticResignDirective(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAutomaticResignDirective to the configured backend. Spec reference: IEEE 1516.1-2010 §10.2 Get Automatic Resign Directive service (Support Services)."""
        return self._invoke("getAutomaticResignDirective", *args, **kwargs)

    def setAutomaticResignDirective(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service setAutomaticResignDirective to the configured backend. Spec reference: IEEE 1516.1-2010 §10.3 Set Automatic Resign Directive service (Support Services)."""
        return self._invoke("setAutomaticResignDirective", *args, **kwargs)

    def getFederateHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getFederateHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.4 Get Federate Handle service (Support Services)."""
        return self._invoke("getFederateHandle", *args, **kwargs)

    def getFederateName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getFederateName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.5 Get Federate Name service (Support Services)."""
        return self._invoke("getFederateName", *args, **kwargs)

    def getObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getObjectClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.6 Get Object Class Handle service (Support Services)."""
        return self._invoke("getObjectClassHandle", *args, **kwargs)

    def getObjectClassName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getObjectClassName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.7 Get Object Class Name service (Support Services)."""
        return self._invoke("getObjectClassName", *args, **kwargs)

    def getKnownObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getKnownObjectClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.8 Get Known Object Class Handle service (Support Services)."""
        return self._invoke("getKnownObjectClassHandle", *args, **kwargs)

    def getObjectInstanceHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getObjectInstanceHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.9 Get Object Instance Handle service (Support Services)."""
        return self._invoke("getObjectInstanceHandle", *args, **kwargs)

    def getObjectInstanceName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.10 Get Object Instance Name service (Support Services)."""
        return self._invoke("getObjectInstanceName", *args, **kwargs)

    def getAttributeHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.11 Get Attribute Handle service (Support Services)."""
        return self._invoke("getAttributeHandle", *args, **kwargs)

    def getAttributeName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAttributeName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.12 Get Attribute Name service (Support Services)."""
        return self._invoke("getAttributeName", *args, **kwargs)

    def getUpdateRateValue(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getUpdateRateValue to the configured backend. Spec reference: IEEE 1516.1-2010 §10.13 Get Update Rate Value service (Support Services)."""
        return self._invoke("getUpdateRateValue", *args, **kwargs)

    def getUpdateRateValueForAttribute(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getUpdateRateValueForAttribute to the configured backend. Spec reference: IEEE 1516.1-2010 §10.14 Get Update Rate Value For Attribute service (Support Services)."""
        return self._invoke("getUpdateRateValueForAttribute", *args, **kwargs)

    def getInteractionClassHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getInteractionClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.15 Get Interaction Class Handle service (Support Services)."""
        return self._invoke("getInteractionClassHandle", *args, **kwargs)

    def getInteractionClassName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getInteractionClassName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.16 Get Interaction Class Name service (Support Services)."""
        return self._invoke("getInteractionClassName", *args, **kwargs)

    def getParameterHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getParameterHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.17 Get Parameter Handle service (Support Services)."""
        return self._invoke("getParameterHandle", *args, **kwargs)

    def getParameterName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getParameterName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.18 Get Parameter Name service (Support Services)."""
        return self._invoke("getParameterName", *args, **kwargs)

    def getOrderType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getOrderType to the configured backend. Spec reference: IEEE 1516.1-2010 §10.19 Get Order Type service (Support Services)."""
        return self._invoke("getOrderType", *args, **kwargs)

    def getOrderName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getOrderName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.20 Get Order Name service (Support Services)."""
        return self._invoke("getOrderName", *args, **kwargs)

    def getTransportationTypeHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getTransportationTypeHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.21 Get Transportation Type Handle service (Support Services)."""
        return self._invoke("getTransportationTypeHandle", *args, **kwargs)

    def getTransportationTypeName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getTransportationTypeName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.22 Get Transportation Type Name service (Support Services)."""
        return self._invoke("getTransportationTypeName", *args, **kwargs)

    def getAvailableDimensionsForClassAttribute(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAvailableDimensionsForClassAttribute to the configured backend. Spec reference: IEEE 1516.1-2010 §10.23 Get Available Dimensions For Class Attribute service (Support Services)."""
        return self._invoke("getAvailableDimensionsForClassAttribute", *args, **kwargs)

    def getAvailableDimensionsForInteractionClass(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAvailableDimensionsForInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §10.24 Get Available Dimensions For Interaction Class service (Support Services)."""
        return self._invoke("getAvailableDimensionsForInteractionClass", *args, **kwargs)

    def getDimensionHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.25 Get Dimension Handle service (Support Services)."""
        return self._invoke("getDimensionHandle", *args, **kwargs)

    def getDimensionName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getDimensionName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.26 Get Dimension Name service (Support Services)."""
        return self._invoke("getDimensionName", *args, **kwargs)

    def getDimensionUpperBound(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getDimensionUpperBound to the configured backend. Spec reference: IEEE 1516.1-2010 §10.27 Get Dimension Upper Bound service (Support Services)."""
        return self._invoke("getDimensionUpperBound", *args, **kwargs)

    def getDimensionHandleSet(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandleSet to the configured backend. Spec reference: IEEE 1516.1-2010 §10.28 Get Dimension Handle Set service (Support Services)."""
        return self._invoke("getDimensionHandleSet", *args, **kwargs)

    def getRangeBounds(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getRangeBounds to the configured backend. Spec reference: IEEE 1516.1-2010 §10.29 Get Range Bounds service (Support Services)."""
        return self._invoke("getRangeBounds", *args, **kwargs)

    def setRangeBounds(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service setRangeBounds to the configured backend. Spec reference: IEEE 1516.1-2010 §10.30 Set Range Bounds service (Support Services)."""
        return self._invoke("setRangeBounds", *args, **kwargs)

    def normalizeFederateHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service normalizeFederateHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.31 Normalize Federate Handle service (Support Services)."""
        return self._invoke("normalizeFederateHandle", *args, **kwargs)

    def normalizeServiceGroup(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service normalizeServiceGroup to the configured backend. Spec reference: IEEE 1516.1-2010 §10.32 Normalize Service Group service (Support Services)."""
        return self._invoke("normalizeServiceGroup", *args, **kwargs)

    def enableObjectClassRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableObjectClassRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.33 Enable Object Class Relevance Advisory Switch service (Support Services)."""
        return self._invoke("enableObjectClassRelevanceAdvisorySwitch", *args, **kwargs)

    def disableObjectClassRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableObjectClassRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.34 Disable Object Class Relevance Advisory Switch service (Support Services)."""
        return self._invoke("disableObjectClassRelevanceAdvisorySwitch", *args, **kwargs)

    def enableAttributeRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableAttributeRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.35 Enable Attribute Relevance Advisory Switch service (Support Services)."""
        return self._invoke("enableAttributeRelevanceAdvisorySwitch", *args, **kwargs)

    def disableAttributeRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableAttributeRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.36 Disable Attribute Relevance Advisory Switch service (Support Services)."""
        return self._invoke("disableAttributeRelevanceAdvisorySwitch", *args, **kwargs)

    def enableAttributeScopeAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableAttributeScopeAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.37 Enable Attribute Scope Advisory Switch service (Support Services)."""
        return self._invoke("enableAttributeScopeAdvisorySwitch", *args, **kwargs)

    def disableAttributeScopeAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableAttributeScopeAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.38 Disable Attribute Scope Advisory Switch service (Support Services)."""
        return self._invoke("disableAttributeScopeAdvisorySwitch", *args, **kwargs)

    def enableInteractionRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableInteractionRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.39 Enable Interaction Relevance Advisory Switch service (Support Services)."""
        return self._invoke("enableInteractionRelevanceAdvisorySwitch", *args, **kwargs)

    def disableInteractionRelevanceAdvisorySwitch(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableInteractionRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.40 Disable Interaction Relevance Advisory Switch service (Support Services)."""
        return self._invoke("disableInteractionRelevanceAdvisorySwitch", *args, **kwargs)

    def evokeCallback(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service evokeCallback to the configured backend. Spec reference: IEEE 1516.1-2010 §10.41 Evoke Callback service (Support Services)."""
        return self._invoke("evokeCallback", *args, **kwargs)

    def evokeMultipleCallbacks(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service evokeMultipleCallbacks to the configured backend. Spec reference: IEEE 1516.1-2010 §10.42 Evoke Multiple Callbacks service (Support Services)."""
        return self._invoke("evokeMultipleCallbacks", *args, **kwargs)

    def enableCallbacks(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service enableCallbacks to the configured backend. Spec reference: IEEE 1516.1-2010 §10.43 Enable Callbacks service (Support Services)."""
        return self._invoke("enableCallbacks", *args, **kwargs)

    def disableCallbacks(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service disableCallbacks to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("disableCallbacks", *args, **kwargs)

    def getAttributeHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getAttributeHandleFactory", *args, **kwargs)

    def getAttributeHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getAttributeHandleSetFactory", *args, **kwargs)

    def getAttributeHandleValueMapFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandleValueMapFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getAttributeHandleValueMapFactory", *args, **kwargs)

    def getAttributeSetRegionSetPairListFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getAttributeSetRegionSetPairListFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getAttributeSetRegionSetPairListFactory", *args, **kwargs)

    def getDimensionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getDimensionHandleFactory", *args, **kwargs)

    def getDimensionHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getDimensionHandleSetFactory", *args, **kwargs)

    def getFederateHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getFederateHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getFederateHandleFactory", *args, **kwargs)

    def getFederateHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getFederateHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getFederateHandleSetFactory", *args, **kwargs)

    def getInteractionClassHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getInteractionClassHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getInteractionClassHandleFactory", *args, **kwargs)

    def getObjectClassHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getObjectClassHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getObjectClassHandleFactory", *args, **kwargs)

    def getObjectInstanceHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getObjectInstanceHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getObjectInstanceHandleFactory", *args, **kwargs)

    def getParameterHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getParameterHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getParameterHandleFactory", *args, **kwargs)

    def getParameterHandleValueMapFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getParameterHandleValueMapFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getParameterHandleValueMapFactory", *args, **kwargs)

    def getRegionHandleSetFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getRegionHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getRegionHandleSetFactory", *args, **kwargs)

    def getRegionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getRegionHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010/2025 support-factory surface."""
        return self._invoke("getRegionHandleFactory", *args, **kwargs)

    def getMessageRetractionHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getMessageRetractionHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010/2025 support-factory surface."""
        return self._invoke("getMessageRetractionHandleFactory", *args, **kwargs)

    def getTransportationTypeHandleFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getTransportationTypeHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getTransportationTypeHandleFactory", *args, **kwargs)

    def getHLAversion(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getHLAversion to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getHLAversion", *args, **kwargs)

    def getTimeFactory(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getTimeFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 Disable Callbacks service (Support Services)."""
        return self._invoke("getTimeFactory", *args, **kwargs)

    def createFederationExecutionWithMIM(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service createFederationExecutionWithMIM to the configured backend. Spec reference: IEEE 1516.1-2010 §4.5 Create Federation Execution service (Federation Management)."""
        return self._invoke("createFederationExecutionWithMIM", *args, **kwargs)

    def getTransportationType(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getTransportationType to the configured backend. Spec reference: IEEE 1516.1-2010 §10.21 Get Transportation Type Handle service (Support Services)."""
        return self._invoke("getTransportationType", *args, **kwargs)

    def getTransportationName(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service getTransportationName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.22 Get Transportation Type Name service (Support Services)."""
        return self._invoke("getTransportationName", *args, **kwargs)

    def decodeFederateHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeFederateHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeFederateHandle", *args, **kwargs)

    def decodeObjectClassHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeObjectClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeObjectClassHandle", *args, **kwargs)

    def decodeInteractionClassHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeInteractionClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeInteractionClassHandle", *args, **kwargs)

    def decodeObjectInstanceHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeObjectInstanceHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeObjectInstanceHandle", *args, **kwargs)

    def decodeAttributeHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeAttributeHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeAttributeHandle", *args, **kwargs)

    def decodeParameterHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeParameterHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeParameterHandle", *args, **kwargs)

    def decodeDimensionHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeDimensionHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeDimensionHandle", *args, **kwargs)

    def decodeMessageRetractionHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeMessageRetractionHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeMessageRetractionHandle", *args, **kwargs)

    def decodeRegionHandle(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
        """Delegate HLA RTI service decodeRegionHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §12.2 Designators (Programming Language Mappings)."""
        return self._invoke("decodeRegionHandle", *args, **kwargs)


class RecordingBackend(RTIBackend):
    """Tiny backend for tests and examples."""

    def __init__(self, results: Mapping[str, Any] | None = None):
        self.info = BackendInfo(name="recording", kind="test")
        self.results: MutableMapping[str, Any] = dict(results or {})
        self.calls: list[Invocation] = []
        self.started = False
        self.closed = False

    def start(self) -> "RecordingBackend":
        self.started = True
        return self

    def invoke(self, invocation: Invocation) -> Any:
        self.calls.append(invocation)
        result = self.results.get(invocation.method_name)
        if callable(result):
            return result(invocation)
        return result

    def close(self) -> None:
        self.closed = True


def make_rti_ambassador(backend: RTIBackend, *, start: bool = True) -> DelegatingRTIAmbassador:
    """Create a backend-backed RTIambassador."""
    return DelegatingRTIAmbassador(backend, start=start)


__all__ = [
    "BackendConversionError",
    "BackendInfo",
    "BackendUnavailableError",
    "CALLBACK_METHOD_NAMES",
    "DelegatingRTIAmbassador",
    "Invocation",
    "RTIBackend",
    "RTI_METHOD_NAMES",
    "RecordingBackend",
    "UnsupportedBackendService",
    "lower_camel_to_snake",
    "make_rti_ambassador",
    "snake_to_lower_camel",
]
