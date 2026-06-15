"""Backend-neutral RTI adapter plumbing."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from os import PathLike
from types import TracebackType
from typing import Any, Mapping, MutableMapping, TypeAlias

from hla2010._spec_impl import SupplementalReceiveInfo, SupplementalReflectInfo, SupplementalRemoveInfo
from hla2010.enums import (
    CallbackModel,
    OrderType,
    ResignAction,
    RestoreFailureReason,
    SaveFailureReason,
    ServiceGroup,
    SynchronizationPointFailureReason,
    TransportationType,
)
from hla2010.exceptions import CallNotAllowedFromWithinCallback, RTIexception, RTIinternalError
from hla2010.handles import (
    AttributeHandle,
    AttributeHandleFactory,
    AttributeHandleSet,
    AttributeHandleSetFactory,
    AttributeHandleValueMap,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairList,
    AttributeSetRegionSetPairListFactory,
    DimensionHandle,
    DimensionHandleFactory,
    DimensionHandleSet,
    DimensionHandleSetFactory,
    FederateHandle,
    FederateHandleFactory,
    FederateHandleSet,
    FederateHandleSetFactory,
    InteractionClassHandle,
    InteractionClassHandleFactory,
    InteractionClassHandleSet,
    MessageRetractionHandle,
    MessageRetractionHandleFactory,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMap,
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleSet,
    RegionHandleSetFactory,
    TransportationTypeHandle,
    TransportationTypeHandleFactory,
)
from hla2010.raw_api import API_METADATA
from hla2010.spec import FederateAmbassadorSpec, RTIambassadorSpec
from hla2010.time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time, LogicalTimeFactory
from hla2010.types import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformationSet,
    MessageRetractionReturn,
    RangeBounds,
    TimeQueryReturn,
)

LogicalTimeLike: TypeAlias = HLAfloat64Time | HLAinteger64Time | float | int
LogicalTimeIntervalLike: TypeAlias = HLAfloat64Interval | HLAinteger64Interval | float | int
LogicalTimeFactoryLike: TypeAlias = LogicalTimeFactory[HLAinteger64Time | HLAfloat64Time, HLAinteger64Interval | HLAfloat64Interval]
URLLike: TypeAlias = str | PathLike[str]
FomModuleLike: TypeAlias = URLLike | Sequence[URLLike]
VariableLengthDataLike: TypeAlias = bytes | bytearray | memoryview

RTI_METHOD_NAMES: tuple[str, ...] = tuple(API_METADATA["RTIambassador"].keys())
CALLBACK_METHOD_NAMES: tuple[str, ...] = tuple(API_METADATA["FederateAmbassador"].keys())


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

    def start(self) -> RTIBackend:
        return self

    @abstractmethod
    def invoke(self, invocation: Invocation) -> Any:
        raise NotImplementedError

    def adapt_federate_ambassador(self, ambassador: FederateAmbassadorSpec) -> Any:
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


class DelegatingRTIAmbassador(RTIambassadorSpec):
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
            if isinstance(first, FederateAmbassadorSpec):
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

    def __enter__(self) -> DelegatingRTIAmbassador:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.close()
        return False

    # BEGIN GENERATED RTI SERVICE METHODS
    def abortFederationRestore(self) -> None:  # noqa: N802
        """Delegate HLA RTI service abortFederationRestore to the configured backend. Spec reference: IEEE 1516.1-2010 §4.30 (Federation Management)."""
        return self._invoke("abortFederationRestore")

    def abort_federation_restore(self) -> None:
        """Delegate the Pythonic RTI service alias to abortFederationRestore."""
        return self.abortFederationRestore()

    def abortFederationSave(self) -> None:  # noqa: N802
        """Delegate HLA RTI service abortFederationSave to the configured backend. Spec reference: IEEE 1516.1-2010 §4.21 (Federation Management)."""
        return self._invoke("abortFederationSave")

    def abort_federation_save(self) -> None:
        """Delegate the Pythonic RTI service alias to abortFederationSave."""
        return self.abortFederationSave()

    def associateRegionsForUpdates(
        self,
        theObject: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service associateRegionsForUpdates to the configured backend. Spec reference: IEEE 1516.1-2010 §9.6 (Data Distribution Management)."""
        return self._invoke("associateRegionsForUpdates", theObject, attributesAndRegions)

    def associate_regions_for_updates(
        self,
        the_object: ObjectInstanceHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
    ) -> None:
        """Delegate the Pythonic RTI service alias to associateRegionsForUpdates."""
        return self.associateRegionsForUpdates(the_object, attributes_and_regions)

    def attributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipAcquisition to the configured backend. Spec reference: IEEE 1516.1-2010 §7.8 (Ownership Management)."""
        return self._invoke("attributeOwnershipAcquisition", theObject, desiredAttributes, userSuppliedTag)

    def attribute_ownership_acquisition(
        self,
        the_object: ObjectInstanceHandle,
        desired_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        """Delegate the Pythonic RTI service alias to attributeOwnershipAcquisition."""
        return self.attributeOwnershipAcquisition(the_object, desired_attributes, user_supplied_tag)

    def attributeOwnershipAcquisitionIfAvailable(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipAcquisitionIfAvailable to the configured backend. Spec reference: IEEE 1516.1-2010 §7.9 (Ownership Management)."""
        return self._invoke("attributeOwnershipAcquisitionIfAvailable", theObject, desiredAttributes)

    def attribute_ownership_acquisition_if_available(
        self,
        the_object: ObjectInstanceHandle,
        desired_attributes: AttributeHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to attributeOwnershipAcquisitionIfAvailable."""
        return self.attributeOwnershipAcquisitionIfAvailable(the_object, desired_attributes)

    def attributeOwnershipDivestitureIfWanted(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> AttributeHandleSet:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipDivestitureIfWanted to the configured backend. Spec reference: IEEE 1516.1-2010 §7.13 (Ownership Management)."""
        return self._invoke("attributeOwnershipDivestitureIfWanted", theObject, theAttributes)

    def attribute_ownership_divestiture_if_wanted(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> AttributeHandleSet:
        """Delegate the Pythonic RTI service alias to attributeOwnershipDivestitureIfWanted."""
        return self.attributeOwnershipDivestitureIfWanted(the_object, the_attributes)

    def attributeOwnershipReleaseDenied(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service attributeOwnershipReleaseDenied to the configured backend. Spec reference: IEEE 1516.1-2010 §7.12 (Ownership Management)."""
        return self._invoke("attributeOwnershipReleaseDenied", theObject, theAttributes)

    def attribute_ownership_release_denied(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to attributeOwnershipReleaseDenied."""
        return self.attributeOwnershipReleaseDenied(the_object, the_attributes)

    def cancelAttributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service cancelAttributeOwnershipAcquisition to the configured backend. Spec reference: IEEE 1516.1-2010 §7.15 (Ownership Management)."""
        return self._invoke("cancelAttributeOwnershipAcquisition", theObject, theAttributes)

    def cancel_attribute_ownership_acquisition(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to cancelAttributeOwnershipAcquisition."""
        return self.cancelAttributeOwnershipAcquisition(the_object, the_attributes)

    def cancelNegotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service cancelNegotiatedAttributeOwnershipDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.14 (Ownership Management)."""
        return self._invoke("cancelNegotiatedAttributeOwnershipDivestiture", theObject, theAttributes)

    def cancel_negotiated_attribute_ownership_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to cancelNegotiatedAttributeOwnershipDivestiture."""
        return self.cancelNegotiatedAttributeOwnershipDivestiture(the_object, the_attributes)

    def changeAttributeOrderType(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theType: OrderType,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service changeAttributeOrderType to the configured backend. Spec reference: IEEE 1516.1-2010 §8.23 (Time Management)."""
        return self._invoke("changeAttributeOrderType", theObject, theAttributes, theType)

    def change_attribute_order_type(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        the_type: OrderType,
    ) -> None:
        """Delegate the Pythonic RTI service alias to changeAttributeOrderType."""
        return self.changeAttributeOrderType(the_object, the_attributes, the_type)

    def changeInteractionOrderType(self, theClass: InteractionClassHandle, theType: OrderType) -> None:  # noqa: N802
        """Delegate HLA RTI service changeInteractionOrderType to the configured backend. Spec reference: IEEE 1516.1-2010 §8.24 (Time Management)."""
        return self._invoke("changeInteractionOrderType", theClass, theType)

    def change_interaction_order_type(self, the_class: InteractionClassHandle, the_type: OrderType) -> None:
        """Delegate the Pythonic RTI service alias to changeInteractionOrderType."""
        return self.changeInteractionOrderType(the_class, the_type)

    def commitRegionModifications(self, regions: RegionHandleSet) -> None:  # noqa: N802
        """Delegate HLA RTI service commitRegionModifications to the configured backend. Spec reference: IEEE 1516.1-2010 §9.3 (Data Distribution Management)."""
        return self._invoke("commitRegionModifications", regions)

    def commit_region_modifications(self, regions: RegionHandleSet) -> None:
        """Delegate the Pythonic RTI service alias to commitRegionModifications."""
        return self.commitRegionModifications(regions)

    def confirmDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service confirmDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.6 (Ownership Management)."""
        return self._invoke("confirmDivestiture", theObject, theAttributes, userSuppliedTag)

    def confirm_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        """Delegate the Pythonic RTI service alias to confirmDivestiture."""
        return self.confirmDivestiture(the_object, the_attributes, user_supplied_tag)

    def connect(
        self,
        federateReference: FederateAmbassadorSpec,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service connect to the configured backend. Spec reference: IEEE 1516.1-2010 §4.2 (Federation Management)."""
        args: tuple[object, ...] = (federateReference, callbackModel)
        if localSettingsDesignator is not None:
            args = (*args, localSettingsDesignator)
        return self._invoke("connect", *args)

    def createFederationExecution(
        self,
        federationExecutionName: str,
        fomModules: Sequence[URLLike],
        mimModule: URLLike | None = None,
        logicalTimeImplementationName: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service createFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.5 (Federation Management)."""
        args: tuple[object, ...] = (federationExecutionName, fomModules)
        if mimModule is not None:
            args = (*args, mimModule)
        if logicalTimeImplementationName is not None:
            args = (*args, logicalTimeImplementationName)
        return self._invoke("createFederationExecution", *args)

    def create_federation_execution(
        self,
        federation_execution_name: str,
        fom_modules: FomModuleLike,
        *,
        mim_module: URLLike | None = None,
        logical_time_implementation_name: str | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to createFederationExecution."""
        args: tuple[object, ...] = (federation_execution_name, fom_modules)
        if mim_module is not None:
            args = (*args, mim_module)
        if logical_time_implementation_name is not None:
            args = (*args, logical_time_implementation_name)
        return self._invoke("createFederationExecution", *args)

    def createFederationExecutionWithMIM(
        self,
        federationExecutionName: str,
        fomModules: Sequence[URLLike],
        mimModule: str,
        logicalTimeImplementationName: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service createFederationExecutionWithMIM to the configured backend."""
        args: tuple[object, ...] = (federationExecutionName, fomModules, mimModule)
        if logicalTimeImplementationName is not None:
            args = (*args, logicalTimeImplementationName)
        return self._invoke("createFederationExecutionWithMIM", *args)

    def create_federation_execution_with_mim(
        self,
        federation_execution_name: str,
        fom_modules: Sequence[URLLike],
        mim_module: str,
        logical_time_implementation_name: str | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to createFederationExecutionWithMIM."""
        args: tuple[object, ...] = (federation_execution_name, fom_modules, mim_module)
        if logical_time_implementation_name is not None:
            args = (*args, logical_time_implementation_name)
        return self._invoke("createFederationExecutionWithMIM", *args)

    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle:  # noqa: N802
        """Delegate HLA RTI service createRegion to the configured backend. Spec reference: IEEE 1516.1-2010 §9.2 (Data Distribution Management)."""
        return self._invoke("createRegion", dimensions)

    def create_region(self, dimensions: DimensionHandleSet) -> RegionHandle:
        """Delegate the Pythonic RTI service alias to createRegion."""
        return self.createRegion(dimensions)

    def decodeAttributeHandle(self, encodedValue: VariableLengthDataLike) -> AttributeHandle:  # noqa: N802
        """Delegate HLA RTI service decodeAttributeHandle to the configured backend."""
        return self._invoke("decodeAttributeHandle", encodedValue)

    def decode_attribute_handle(self, encoded_value: VariableLengthDataLike) -> AttributeHandle:
        """Delegate the Pythonic RTI service alias to decodeAttributeHandle."""
        return self.decodeAttributeHandle(encoded_value)

    def decodeDimensionHandle(self, encodedValue: VariableLengthDataLike) -> DimensionHandle:  # noqa: N802
        """Delegate HLA RTI service decodeDimensionHandle to the configured backend."""
        return self._invoke("decodeDimensionHandle", encodedValue)

    def decode_dimension_handle(self, encoded_value: VariableLengthDataLike) -> DimensionHandle:
        """Delegate the Pythonic RTI service alias to decodeDimensionHandle."""
        return self.decodeDimensionHandle(encoded_value)

    def decodeFederateHandle(self, encodedValue: VariableLengthDataLike) -> FederateHandle:  # noqa: N802
        """Delegate HLA RTI service decodeFederateHandle to the configured backend."""
        return self._invoke("decodeFederateHandle", encodedValue)

    def decode_federate_handle(self, encoded_value: VariableLengthDataLike) -> FederateHandle:
        """Delegate the Pythonic RTI service alias to decodeFederateHandle."""
        return self.decodeFederateHandle(encoded_value)

    def decodeInteractionClassHandle(self, encodedValue: VariableLengthDataLike) -> InteractionClassHandle:  # noqa: N802
        """Delegate HLA RTI service decodeInteractionClassHandle to the configured backend."""
        return self._invoke("decodeInteractionClassHandle", encodedValue)

    def decode_interaction_class_handle(self, encoded_value: VariableLengthDataLike) -> InteractionClassHandle:
        """Delegate the Pythonic RTI service alias to decodeInteractionClassHandle."""
        return self.decodeInteractionClassHandle(encoded_value)

    def decodeMessageRetractionHandle(
        self,
        encodedValue: VariableLengthDataLike,
    ) -> MessageRetractionHandle:  # noqa: N802
        """Delegate HLA RTI service decodeMessageRetractionHandle to the configured backend."""
        return self._invoke("decodeMessageRetractionHandle", encodedValue)

    def decode_message_retraction_handle(self, encoded_value: VariableLengthDataLike) -> MessageRetractionHandle:
        """Delegate the Pythonic RTI service alias to decodeMessageRetractionHandle."""
        return self.decodeMessageRetractionHandle(encoded_value)

    def decodeObjectClassHandle(self, encodedValue: VariableLengthDataLike) -> ObjectClassHandle:  # noqa: N802
        """Delegate HLA RTI service decodeObjectClassHandle to the configured backend."""
        return self._invoke("decodeObjectClassHandle", encodedValue)

    def decode_object_class_handle(self, encoded_value: VariableLengthDataLike) -> ObjectClassHandle:
        """Delegate the Pythonic RTI service alias to decodeObjectClassHandle."""
        return self.decodeObjectClassHandle(encoded_value)

    def decodeObjectInstanceHandle(self, encodedValue: VariableLengthDataLike) -> ObjectInstanceHandle:  # noqa: N802
        """Delegate HLA RTI service decodeObjectInstanceHandle to the configured backend."""
        return self._invoke("decodeObjectInstanceHandle", encodedValue)

    def decode_object_instance_handle(self, encoded_value: VariableLengthDataLike) -> ObjectInstanceHandle:
        """Delegate the Pythonic RTI service alias to decodeObjectInstanceHandle."""
        return self.decodeObjectInstanceHandle(encoded_value)

    def decodeParameterHandle(self, encodedValue: VariableLengthDataLike) -> ParameterHandle:  # noqa: N802
        """Delegate HLA RTI service decodeParameterHandle to the configured backend."""
        return self._invoke("decodeParameterHandle", encodedValue)

    def decode_parameter_handle(self, encoded_value: VariableLengthDataLike) -> ParameterHandle:
        """Delegate the Pythonic RTI service alias to decodeParameterHandle."""
        return self.decodeParameterHandle(encoded_value)

    def decodeRegionHandle(self, encodedValue: VariableLengthDataLike) -> RegionHandle:  # noqa: N802
        """Delegate HLA RTI service decodeRegionHandle to the configured backend."""
        return self._invoke("decodeRegionHandle", encodedValue)

    def decode_region_handle(self, encoded_value: VariableLengthDataLike) -> RegionHandle:
        """Delegate the Pythonic RTI service alias to decodeRegionHandle."""
        return self.decodeRegionHandle(encoded_value)

    def deleteObjectInstance(
        self,
        objectHandle: ObjectInstanceHandle,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service deleteObjectInstance to the configured backend. Spec reference: IEEE 1516.1-2010 §6.14 (Object Management)."""
        args: tuple[object, ...] = (objectHandle, userSuppliedTag)
        if theTime is not None:
            args = (*args, theTime)
        return self._invoke("deleteObjectInstance", *args)

    def delete_object_instance(
        self,
        object_handle: ObjectInstanceHandle,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to deleteObjectInstance."""
        args: tuple[object, ...] = (object_handle, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self._invoke("deleteObjectInstance", *args)

    def deleteRegion(self, theRegion: RegionHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service deleteRegion to the configured backend. Spec reference: IEEE 1516.1-2010 §9.4 (Data Distribution Management)."""
        return self._invoke("deleteRegion", theRegion)

    def delete_region(self, the_region: RegionHandle) -> None:
        """Delegate the Pythonic RTI service alias to deleteRegion."""
        return self.deleteRegion(the_region)

    def destroyFederationExecution(self, federationExecutionName: str) -> None:  # noqa: N802
        """Delegate HLA RTI service destroyFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.6 (Federation Management)."""
        return self._invoke("destroyFederationExecution", federationExecutionName)

    def destroy_federation_execution(self, federation_execution_name: str) -> None:
        """Delegate the Pythonic RTI service alias to destroyFederationExecution."""
        return self.destroyFederationExecution(federation_execution_name)

    def disableAsynchronousDelivery(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableAsynchronousDelivery to the configured backend. Spec reference: IEEE 1516.1-2010 §8.15 (Time Management)."""
        return self._invoke("disableAsynchronousDelivery")

    def disable_asynchronous_delivery(self) -> None:
        """Delegate the Pythonic RTI service alias to disableAsynchronousDelivery."""
        return self.disableAsynchronousDelivery()

    def disableAttributeRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableAttributeRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.36 (Support Services)."""
        return self._invoke("disableAttributeRelevanceAdvisorySwitch")

    def disable_attribute_relevance_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to disableAttributeRelevanceAdvisorySwitch."""
        return self.disableAttributeRelevanceAdvisorySwitch()

    def disableAttributeScopeAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableAttributeScopeAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.38 (Support Services)."""
        return self._invoke("disableAttributeScopeAdvisorySwitch")

    def disable_attribute_scope_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to disableAttributeScopeAdvisorySwitch."""
        return self.disableAttributeScopeAdvisorySwitch()

    def disableCallbacks(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableCallbacks to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("disableCallbacks")

    def disable_callbacks(self) -> None:
        """Delegate the Pythonic RTI service alias to disableCallbacks."""
        return self.disableCallbacks()

    def disableInteractionRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableInteractionRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.40 (Support Services)."""
        return self._invoke("disableInteractionRelevanceAdvisorySwitch")

    def disable_interaction_relevance_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to disableInteractionRelevanceAdvisorySwitch."""
        return self.disableInteractionRelevanceAdvisorySwitch()

    def disableObjectClassRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableObjectClassRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.34 (Support Services)."""
        return self._invoke("disableObjectClassRelevanceAdvisorySwitch")

    def disable_object_class_relevance_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to disableObjectClassRelevanceAdvisorySwitch."""
        return self.disableObjectClassRelevanceAdvisorySwitch()

    def disableTimeConstrained(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableTimeConstrained to the configured backend. Spec reference: IEEE 1516.1-2010 §8.7 (Time Management)."""
        return self._invoke("disableTimeConstrained")

    def disable_time_constrained(self) -> None:
        """Delegate the Pythonic RTI service alias to disableTimeConstrained."""
        return self.disableTimeConstrained()

    def disableTimeRegulation(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disableTimeRegulation to the configured backend. Spec reference: IEEE 1516.1-2010 §8.4 (Time Management)."""
        return self._invoke("disableTimeRegulation")

    def disable_time_regulation(self) -> None:
        """Delegate the Pythonic RTI service alias to disableTimeRegulation."""
        return self.disableTimeRegulation()

    def disconnect(self) -> None:  # noqa: N802
        """Delegate HLA RTI service disconnect to the configured backend. Spec reference: IEEE 1516.1-2010 §4.3 (Federation Management)."""
        return self._invoke("disconnect")

    def enableAsynchronousDelivery(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableAsynchronousDelivery to the configured backend. Spec reference: IEEE 1516.1-2010 §8.14 (Time Management)."""
        return self._invoke("enableAsynchronousDelivery")

    def enable_asynchronous_delivery(self) -> None:
        """Delegate the Pythonic RTI service alias to enableAsynchronousDelivery."""
        return self.enableAsynchronousDelivery()

    def enableAttributeRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableAttributeRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.35 (Support Services)."""
        return self._invoke("enableAttributeRelevanceAdvisorySwitch")

    def enable_attribute_relevance_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to enableAttributeRelevanceAdvisorySwitch."""
        return self.enableAttributeRelevanceAdvisorySwitch()

    def enableAttributeScopeAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableAttributeScopeAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.37 (Support Services)."""
        return self._invoke("enableAttributeScopeAdvisorySwitch")

    def enable_attribute_scope_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to enableAttributeScopeAdvisorySwitch."""
        return self.enableAttributeScopeAdvisorySwitch()

    def enableCallbacks(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableCallbacks to the configured backend. Spec reference: IEEE 1516.1-2010 §10.43 (Support Services)."""
        return self._invoke("enableCallbacks")

    def enable_callbacks(self) -> None:
        """Delegate the Pythonic RTI service alias to enableCallbacks."""
        return self.enableCallbacks()

    def enableInteractionRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableInteractionRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.39 (Support Services)."""
        return self._invoke("enableInteractionRelevanceAdvisorySwitch")

    def enable_interaction_relevance_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to enableInteractionRelevanceAdvisorySwitch."""
        return self.enableInteractionRelevanceAdvisorySwitch()

    def enableObjectClassRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableObjectClassRelevanceAdvisorySwitch to the configured backend. Spec reference: IEEE 1516.1-2010 §10.33 (Support Services)."""
        return self._invoke("enableObjectClassRelevanceAdvisorySwitch")

    def enable_object_class_relevance_advisory_switch(self) -> None:
        """Delegate the Pythonic RTI service alias to enableObjectClassRelevanceAdvisorySwitch."""
        return self.enableObjectClassRelevanceAdvisorySwitch()

    def enableTimeConstrained(self) -> None:  # noqa: N802
        """Delegate HLA RTI service enableTimeConstrained to the configured backend. Spec reference: IEEE 1516.1-2010 §8.5 (Time Management)."""
        return self._invoke("enableTimeConstrained")

    def enable_time_constrained(self) -> None:
        """Delegate the Pythonic RTI service alias to enableTimeConstrained."""
        return self.enableTimeConstrained()

    def enableTimeRegulation(self, theLookahead: LogicalTimeIntervalLike) -> None:  # noqa: N802
        """Delegate HLA RTI service enableTimeRegulation to the configured backend. Spec reference: IEEE 1516.1-2010 §8.2 (Time Management)."""
        return self._invoke("enableTimeRegulation", theLookahead)

    def enable_time_regulation(self, the_lookahead: LogicalTimeIntervalLike) -> None:
        """Delegate the Pythonic RTI service alias to enableTimeRegulation."""
        return self.enableTimeRegulation(the_lookahead)

    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:  # noqa: N802
        """Delegate HLA RTI service evokeCallback to the configured backend. Spec reference: IEEE 1516.1-2010 §10.41 (Support Services)."""
        return self._invoke("evokeCallback", approximateMinimumTimeInSeconds)

    def evoke_callback(self, approximate_minimum_time_in_seconds: float) -> bool:
        """Delegate the Pythonic RTI service alias to evokeCallback."""
        return self.evokeCallback(approximate_minimum_time_in_seconds)

    def evokeMultipleCallbacks(
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:  # noqa: N802
        """Delegate HLA RTI service evokeMultipleCallbacks to the configured backend. Spec reference: IEEE 1516.1-2010 §10.42 (Support Services)."""
        return self._invoke("evokeMultipleCallbacks", approximateMinimumTimeInSeconds, approximateMaximumTimeInSeconds)

    def evoke_multiple_callbacks(
        self,
        approximate_minimum_time_in_seconds: float,
        approximate_maximum_time_in_seconds: float,
    ) -> bool:
        """Delegate the Pythonic RTI service alias to evokeMultipleCallbacks."""
        return self.evokeMultipleCallbacks(approximate_minimum_time_in_seconds, approximate_maximum_time_in_seconds)

    def federateRestoreComplete(self) -> None:  # noqa: N802
        """Delegate HLA RTI service federateRestoreComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.28 (Federation Management)."""
        return self._invoke("federateRestoreComplete")

    def federate_restore_complete(self) -> None:
        """Delegate the Pythonic RTI service alias to federateRestoreComplete."""
        return self.federateRestoreComplete()

    def federateRestoreNotComplete(self) -> None:  # noqa: N802
        """Delegate HLA RTI service federateRestoreNotComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.28 (Federation Management)."""
        return self._invoke("federateRestoreNotComplete")

    def federate_restore_not_complete(self) -> None:
        """Delegate the Pythonic RTI service alias to federateRestoreNotComplete."""
        return self.federateRestoreNotComplete()

    def federateSaveBegun(self) -> None:  # noqa: N802
        """Delegate HLA RTI service federateSaveBegun to the configured backend. Spec reference: IEEE 1516.1-2010 §4.18 (Federation Management)."""
        return self._invoke("federateSaveBegun")

    def federate_save_begun(self) -> None:
        """Delegate the Pythonic RTI service alias to federateSaveBegun."""
        return self.federateSaveBegun()

    def federateSaveComplete(self) -> None:  # noqa: N802
        """Delegate HLA RTI service federateSaveComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.19 (Federation Management)."""
        return self._invoke("federateSaveComplete")

    def federate_save_complete(self) -> None:
        """Delegate the Pythonic RTI service alias to federateSaveComplete."""
        return self.federateSaveComplete()

    def federateSaveNotComplete(self) -> None:  # noqa: N802
        """Delegate HLA RTI service federateSaveNotComplete to the configured backend. Spec reference: IEEE 1516.1-2010 §4.19 (Federation Management)."""
        return self._invoke("federateSaveNotComplete")

    def federate_save_not_complete(self) -> None:
        """Delegate the Pythonic RTI service alias to federateSaveNotComplete."""
        return self.federateSaveNotComplete()

    def flushQueueRequest(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        """Delegate HLA RTI service flushQueueRequest to the configured backend. Spec reference: IEEE 1516.1-2010 §8.12 (Time Management)."""
        return self._invoke("flushQueueRequest", theTime)

    def flush_queue_request(self, the_time: LogicalTimeLike) -> None:
        """Delegate the Pythonic RTI service alias to flushQueueRequest."""
        return self.flushQueueRequest(the_time)

    def getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.11 (Support Services)."""
        return self._invoke("getAttributeHandle", whichClass, theName)

    def get_attribute_handle(self, which_class: ObjectClassHandle, the_name: str) -> AttributeHandle:
        """Delegate the Pythonic RTI service alias to getAttributeHandle."""
        return self.getAttributeHandle(which_class, the_name)

    def getAttributeHandleFactory(self) -> AttributeHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getAttributeHandleFactory")

    def get_attribute_handle_factory(self) -> AttributeHandleFactory:
        """Delegate the Pythonic RTI service alias to getAttributeHandleFactory."""
        return self.getAttributeHandleFactory()

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getAttributeHandleSetFactory")

    def get_attribute_handle_set_factory(self) -> AttributeHandleSetFactory:
        """Delegate the Pythonic RTI service alias to getAttributeHandleSetFactory."""
        return self.getAttributeHandleSetFactory()

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:  # noqa: N802
        """Delegate HLA RTI service getAttributeHandleValueMapFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getAttributeHandleValueMapFactory")

    def get_attribute_handle_value_map_factory(self) -> AttributeHandleValueMapFactory:
        """Delegate the Pythonic RTI service alias to getAttributeHandleValueMapFactory."""
        return self.getAttributeHandleValueMapFactory()

    def getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getAttributeName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.12 (Support Services)."""
        return self._invoke("getAttributeName", whichClass, theHandle)

    def get_attribute_name(self, which_class: ObjectClassHandle, the_handle: AttributeHandle) -> str:
        """Delegate the Pythonic RTI service alias to getAttributeName."""
        return self.getAttributeName(which_class, the_handle)

    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:  # noqa: N802
        """Delegate HLA RTI service getAttributeSetRegionSetPairListFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getAttributeSetRegionSetPairListFactory")

    def get_attribute_set_region_set_pair_list_factory(self) -> AttributeSetRegionSetPairListFactory:
        """Delegate the Pythonic RTI service alias to getAttributeSetRegionSetPairListFactory."""
        return self.getAttributeSetRegionSetPairListFactory()

    def getAutomaticResignDirective(self) -> ResignAction:  # noqa: N802
        """Delegate HLA RTI service getAutomaticResignDirective to the configured backend. Spec reference: IEEE 1516.1-2010 §10.2 (Support Services)."""
        return self._invoke("getAutomaticResignDirective")

    def get_automatic_resign_directive(self) -> ResignAction:
        """Delegate the Pythonic RTI service alias to getAutomaticResignDirective."""
        return self.getAutomaticResignDirective()

    def getAvailableDimensionsForClassAttribute(
        self,
        whichClass: ObjectClassHandle,
        theHandle: AttributeHandle,
    ) -> DimensionHandleSet:  # noqa: N802
        """Delegate HLA RTI service getAvailableDimensionsForClassAttribute to the configured backend. Spec reference: IEEE 1516.1-2010 §10.23 (Support Services)."""
        return self._invoke("getAvailableDimensionsForClassAttribute", whichClass, theHandle)

    def get_available_dimensions_for_class_attribute(
        self,
        which_class: ObjectClassHandle,
        the_handle: AttributeHandle,
    ) -> DimensionHandleSet:
        """Delegate the Pythonic RTI service alias to getAvailableDimensionsForClassAttribute."""
        return self.getAvailableDimensionsForClassAttribute(which_class, the_handle)

    def getAvailableDimensionsForInteractionClass(
        self,
        theHandle: InteractionClassHandle,
    ) -> DimensionHandleSet:  # noqa: N802
        """Delegate HLA RTI service getAvailableDimensionsForInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §10.24 (Support Services)."""
        return self._invoke("getAvailableDimensionsForInteractionClass", theHandle)

    def get_available_dimensions_for_interaction_class(self, the_handle: InteractionClassHandle) -> DimensionHandleSet:
        """Delegate the Pythonic RTI service alias to getAvailableDimensionsForInteractionClass."""
        return self.getAvailableDimensionsForInteractionClass(the_handle)

    def getDimensionHandle(self, theName: str) -> DimensionHandle:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.25 (Support Services)."""
        return self._invoke("getDimensionHandle", theName)

    def get_dimension_handle(self, the_name: str) -> DimensionHandle:
        """Delegate the Pythonic RTI service alias to getDimensionHandle."""
        return self.getDimensionHandle(the_name)

    def getDimensionHandleFactory(self) -> DimensionHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getDimensionHandleFactory")

    def get_dimension_handle_factory(self) -> DimensionHandleFactory:
        """Delegate the Pythonic RTI service alias to getDimensionHandleFactory."""
        return self.getDimensionHandleFactory()

    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandleSet to the configured backend. Spec reference: IEEE 1516.1-2010 §10.28 (Support Services)."""
        return self._invoke("getDimensionHandleSet", region)

    def get_dimension_handle_set(self, region: RegionHandle) -> DimensionHandleSet:
        """Delegate the Pythonic RTI service alias to getDimensionHandleSet."""
        return self.getDimensionHandleSet(region)

    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:  # noqa: N802
        """Delegate HLA RTI service getDimensionHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getDimensionHandleSetFactory")

    def get_dimension_handle_set_factory(self) -> DimensionHandleSetFactory:
        """Delegate the Pythonic RTI service alias to getDimensionHandleSetFactory."""
        return self.getDimensionHandleSetFactory()

    def getDimensionName(self, theHandle: DimensionHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getDimensionName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.26 (Support Services)."""
        return self._invoke("getDimensionName", theHandle)

    def get_dimension_name(self, the_handle: DimensionHandle) -> str:
        """Delegate the Pythonic RTI service alias to getDimensionName."""
        return self.getDimensionName(the_handle)

    def getDimensionUpperBound(self, theHandle: DimensionHandle) -> int:  # noqa: N802
        """Delegate HLA RTI service getDimensionUpperBound to the configured backend. Spec reference: IEEE 1516.1-2010 §10.27 (Support Services)."""
        return self._invoke("getDimensionUpperBound", theHandle)

    def get_dimension_upper_bound(self, the_handle: DimensionHandle) -> int:
        """Delegate the Pythonic RTI service alias to getDimensionUpperBound."""
        return self.getDimensionUpperBound(the_handle)

    def getFederateHandle(self, theName: str) -> FederateHandle:  # noqa: N802
        """Delegate HLA RTI service getFederateHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.4 (Support Services)."""
        return self._invoke("getFederateHandle", theName)

    def get_federate_handle(self, the_name: str) -> FederateHandle:
        """Delegate the Pythonic RTI service alias to getFederateHandle."""
        return self.getFederateHandle(the_name)

    def getFederateHandleFactory(self) -> FederateHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getFederateHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getFederateHandleFactory")

    def get_federate_handle_factory(self) -> FederateHandleFactory:
        """Delegate the Pythonic RTI service alias to getFederateHandleFactory."""
        return self.getFederateHandleFactory()

    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:  # noqa: N802
        """Delegate HLA RTI service getFederateHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getFederateHandleSetFactory")

    def get_federate_handle_set_factory(self) -> FederateHandleSetFactory:
        """Delegate the Pythonic RTI service alias to getFederateHandleSetFactory."""
        return self.getFederateHandleSetFactory()

    def getFederateName(self, theHandle: FederateHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getFederateName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.5 (Support Services)."""
        return self._invoke("getFederateName", theHandle)

    def get_federate_name(self, the_handle: FederateHandle) -> str:
        """Delegate the Pythonic RTI service alias to getFederateName."""
        return self.getFederateName(the_handle)

    def getHLAversion(self) -> str:  # noqa: N802
        """Delegate HLA RTI service getHLAversion to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getHLAversion")

    def get_hla_version(self) -> str:
        """Delegate the Pythonic RTI service alias to getHLAversion."""
        return self.getHLAversion()

    def getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:  # noqa: N802
        """Delegate HLA RTI service getInteractionClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.15 (Support Services)."""
        return self._invoke("getInteractionClassHandle", theName)

    def get_interaction_class_handle(self, the_name: str) -> InteractionClassHandle:
        """Delegate the Pythonic RTI service alias to getInteractionClassHandle."""
        return self.getInteractionClassHandle(the_name)

    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getInteractionClassHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getInteractionClassHandleFactory")

    def get_interaction_class_handle_factory(self) -> InteractionClassHandleFactory:
        """Delegate the Pythonic RTI service alias to getInteractionClassHandleFactory."""
        return self.getInteractionClassHandleFactory()

    def getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getInteractionClassName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.16 (Support Services)."""
        return self._invoke("getInteractionClassName", theHandle)

    def get_interaction_class_name(self, the_handle: InteractionClassHandle) -> str:
        """Delegate the Pythonic RTI service alias to getInteractionClassName."""
        return self.getInteractionClassName(the_handle)

    def getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:  # noqa: N802
        """Delegate HLA RTI service getKnownObjectClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.8 (Support Services)."""
        return self._invoke("getKnownObjectClassHandle", theObject)

    def get_known_object_class_handle(self, the_object: ObjectInstanceHandle) -> ObjectClassHandle:
        """Delegate the Pythonic RTI service alias to getKnownObjectClassHandle."""
        return self.getKnownObjectClassHandle(the_object)

    def getObjectClassHandle(self, theName: str) -> ObjectClassHandle:  # noqa: N802
        """Delegate HLA RTI service getObjectClassHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.6 (Support Services)."""
        return self._invoke("getObjectClassHandle", theName)

    def get_object_class_handle(self, the_name: str) -> ObjectClassHandle:
        """Delegate the Pythonic RTI service alias to getObjectClassHandle."""
        return self.getObjectClassHandle(the_name)

    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getObjectClassHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getObjectClassHandleFactory")

    def get_object_class_handle_factory(self) -> ObjectClassHandleFactory:
        """Delegate the Pythonic RTI service alias to getObjectClassHandleFactory."""
        return self.getObjectClassHandleFactory()

    def getObjectClassName(self, theHandle: ObjectClassHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getObjectClassName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.7 (Support Services)."""
        return self._invoke("getObjectClassName", theHandle)

    def get_object_class_name(self, the_handle: ObjectClassHandle) -> str:
        """Delegate the Pythonic RTI service alias to getObjectClassName."""
        return self.getObjectClassName(the_handle)

    def getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:  # noqa: N802
        """Delegate HLA RTI service getObjectInstanceHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.9 (Support Services)."""
        return self._invoke("getObjectInstanceHandle", theName)

    def get_object_instance_handle(self, the_name: str) -> ObjectInstanceHandle:
        """Delegate the Pythonic RTI service alias to getObjectInstanceHandle."""
        return self.getObjectInstanceHandle(the_name)

    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getObjectInstanceHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getObjectInstanceHandleFactory")

    def get_object_instance_handle_factory(self) -> ObjectInstanceHandleFactory:
        """Delegate the Pythonic RTI service alias to getObjectInstanceHandleFactory."""
        return self.getObjectInstanceHandleFactory()

    def getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.10 (Support Services)."""
        return self._invoke("getObjectInstanceName", theHandle)

    def get_object_instance_name(self, the_handle: ObjectInstanceHandle) -> str:
        """Delegate the Pythonic RTI service alias to getObjectInstanceName."""
        return self.getObjectInstanceName(the_handle)

    def getOrderName(self, theType: OrderType) -> str:  # noqa: N802
        """Delegate HLA RTI service getOrderName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.20 (Support Services)."""
        return self._invoke("getOrderName", theType)

    def get_order_name(self, the_type: OrderType) -> str:
        """Delegate the Pythonic RTI service alias to getOrderName."""
        return self.getOrderName(the_type)

    def getOrderType(self, theName: str) -> OrderType:  # noqa: N802
        """Delegate HLA RTI service getOrderType to the configured backend. Spec reference: IEEE 1516.1-2010 §10.19 (Support Services)."""
        return self._invoke("getOrderType", theName)

    def get_order_type(self, the_name: str) -> OrderType:
        """Delegate the Pythonic RTI service alias to getOrderType."""
        return self.getOrderType(the_name)

    def getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:  # noqa: N802
        """Delegate HLA RTI service getParameterHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.17 (Support Services)."""
        return self._invoke("getParameterHandle", whichClass, theName)

    def get_parameter_handle(self, which_class: InteractionClassHandle, the_name: str) -> ParameterHandle:
        """Delegate the Pythonic RTI service alias to getParameterHandle."""
        return self.getParameterHandle(which_class, the_name)

    def getParameterHandleFactory(self) -> ParameterHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getParameterHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getParameterHandleFactory")

    def get_parameter_handle_factory(self) -> ParameterHandleFactory:
        """Delegate the Pythonic RTI service alias to getParameterHandleFactory."""
        return self.getParameterHandleFactory()

    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:  # noqa: N802
        """Delegate HLA RTI service getParameterHandleValueMapFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getParameterHandleValueMapFactory")

    def get_parameter_handle_value_map_factory(self) -> ParameterHandleValueMapFactory:
        """Delegate the Pythonic RTI service alias to getParameterHandleValueMapFactory."""
        return self.getParameterHandleValueMapFactory()

    def getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getParameterName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.18 (Support Services)."""
        return self._invoke("getParameterName", whichClass, theHandle)

    def get_parameter_name(self, which_class: InteractionClassHandle, the_handle: ParameterHandle) -> str:
        """Delegate the Pythonic RTI service alias to getParameterName."""
        return self.getParameterName(which_class, the_handle)

    def getRangeBounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:  # noqa: N802
        """Delegate HLA RTI service getRangeBounds to the configured backend. Spec reference: IEEE 1516.1-2010 §10.29 (Support Services)."""
        return self._invoke("getRangeBounds", region, dimension)

    def get_range_bounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:
        """Delegate the Pythonic RTI service alias to getRangeBounds."""
        return self.getRangeBounds(region, dimension)

    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:  # noqa: N802
        """Delegate HLA RTI service getRegionHandleSetFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getRegionHandleSetFactory")

    def get_region_handle_set_factory(self) -> RegionHandleSetFactory:
        """Delegate the Pythonic RTI service alias to getRegionHandleSetFactory."""
        return self.getRegionHandleSetFactory()

    def getTimeFactory(self) -> LogicalTimeFactoryLike:  # noqa: N802
        """Delegate HLA RTI service getTimeFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getTimeFactory")

    def get_time_factory(self) -> LogicalTimeFactoryLike:
        """Delegate the Pythonic RTI service alias to getTimeFactory."""
        return self.getTimeFactory()

    def getTransportationName(self, transportationType: TransportationType) -> str:  # noqa: N802
        """Delegate HLA RTI service getTransportationName to the configured backend."""
        return self._invoke("getTransportationName", transportationType)

    def get_transportation_name(self, transportation_type: TransportationType) -> str:
        """Delegate the Pythonic RTI service alias to getTransportationName."""
        return self.getTransportationName(transportation_type)

    def getTransportationType(self, transportationName: str) -> TransportationType:  # noqa: N802
        """Delegate HLA RTI service getTransportationType to the configured backend."""
        return self._invoke("getTransportationType", transportationName)

    def get_transportation_type(self, transportation_name: str) -> TransportationType:
        """Delegate the Pythonic RTI service alias to getTransportationType."""
        return self.getTransportationType(transportation_name)

    def getTransportationTypeHandle(self, theName: str) -> TransportationTypeHandle:  # noqa: N802
        """Delegate HLA RTI service getTransportationTypeHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.21 (Support Services)."""
        return self._invoke("getTransportationTypeHandle", theName)

    def get_transportation_type_handle(self, the_name: str) -> TransportationTypeHandle:
        """Delegate the Pythonic RTI service alias to getTransportationTypeHandle."""
        return self.getTransportationTypeHandle(the_name)

    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:  # noqa: N802
        """Delegate HLA RTI service getTransportationTypeHandleFactory to the configured backend. Spec reference: IEEE 1516.1-2010 §10.44 (Support Services)."""
        return self._invoke("getTransportationTypeHandleFactory")

    def get_transportation_type_handle_factory(self) -> TransportationTypeHandleFactory:
        """Delegate the Pythonic RTI service alias to getTransportationTypeHandleFactory."""
        return self.getTransportationTypeHandleFactory()

    def getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:  # noqa: N802
        """Delegate HLA RTI service getTransportationTypeName to the configured backend. Spec reference: IEEE 1516.1-2010 §10.22 (Support Services)."""
        return self._invoke("getTransportationTypeName", theHandle)

    def get_transportation_type_name(self, the_handle: TransportationTypeHandle) -> str:
        """Delegate the Pythonic RTI service alias to getTransportationTypeName."""
        return self.getTransportationTypeName(the_handle)

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:  # noqa: N802
        """Delegate HLA RTI service getUpdateRateValue to the configured backend. Spec reference: IEEE 1516.1-2010 §10.13 (Support Services)."""
        return self._invoke("getUpdateRateValue", updateRateDesignator)

    def get_update_rate_value(self, update_rate_designator: str) -> float:
        """Delegate the Pythonic RTI service alias to getUpdateRateValue."""
        return self.getUpdateRateValue(update_rate_designator)

    def getUpdateRateValueForAttribute(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> float:  # noqa: N802
        """Delegate HLA RTI service getUpdateRateValueForAttribute to the configured backend. Spec reference: IEEE 1516.1-2010 §10.14 (Support Services)."""
        return self._invoke("getUpdateRateValueForAttribute", theObject, theAttribute)

    def get_update_rate_value_for_attribute(
        self,
        the_object: ObjectInstanceHandle,
        the_attribute: AttributeHandle,
    ) -> float:
        """Delegate the Pythonic RTI service alias to getUpdateRateValueForAttribute."""
        return self.getUpdateRateValueForAttribute(the_object, the_attribute)

    def isAttributeOwnedByFederate(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> bool:  # noqa: N802
        """Delegate HLA RTI service isAttributeOwnedByFederate to the configured backend. Spec reference: IEEE 1516.1-2010 §7.19 (Ownership Management)."""
        return self._invoke("isAttributeOwnedByFederate", theObject, theAttribute)

    def is_attribute_owned_by_federate(self, the_object: ObjectInstanceHandle, the_attribute: AttributeHandle) -> bool:
        """Delegate the Pythonic RTI service alias to isAttributeOwnedByFederate."""
        return self.isAttributeOwnedByFederate(the_object, the_attribute)

    def joinFederationExecution(
        self,
        federateName: str,
        federateType: str,
        federationExecutionName: str | None = None,
        additionalFomModules: Sequence[URLLike] | None = None,
    ) -> FederateHandle:  # noqa: N802
        """Delegate HLA RTI service joinFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.9 (Federation Management)."""
        args: tuple[object, ...] = (federateName, federateType)
        if federationExecutionName is not None:
            args = (*args, federationExecutionName)
        if additionalFomModules is not None:
            args = (*args, additionalFomModules)
        return self._invoke("joinFederationExecution", *args)

    def join_federation_execution(
        self,
        federate_type: str,
        federation_execution_name: str,
        *,
        federate_name: str | None = None,
        additional_fom_modules: Sequence[URLLike] | None = None,
    ) -> FederateHandle:
        """Delegate the Pythonic RTI service alias to joinFederationExecution."""
        if federate_name is None:
            args: tuple[object, ...] = (federate_type, federation_execution_name)
        else:
            args = (federate_name, federate_type, federation_execution_name)
        if additional_fom_modules is not None:
            args = (*args, additional_fom_modules)
        return self._invoke("joinFederationExecution", *args)

    def listFederationExecutions(self) -> None:  # noqa: N802
        """Delegate HLA RTI service listFederationExecutions to the configured backend. Spec reference: IEEE 1516.1-2010 §4.7 (Federation Management)."""
        return self._invoke("listFederationExecutions")

    def list_federation_executions(self) -> None:
        """Delegate the Pythonic RTI service alias to listFederationExecutions."""
        return self.listFederationExecutions()

    def localDeleteObjectInstance(self, objectHandle: ObjectInstanceHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service localDeleteObjectInstance to the configured backend. Spec reference: IEEE 1516.1-2010 §6.16 (Object Management)."""
        return self._invoke("localDeleteObjectInstance", objectHandle)

    def local_delete_object_instance(self, object_handle: ObjectInstanceHandle) -> None:
        """Delegate the Pythonic RTI service alias to localDeleteObjectInstance."""
        return self.localDeleteObjectInstance(object_handle)

    def modifyLookahead(self, theLookahead: LogicalTimeIntervalLike) -> None:  # noqa: N802
        """Delegate HLA RTI service modifyLookahead to the configured backend. Spec reference: IEEE 1516.1-2010 §8.19 (Time Management)."""
        return self._invoke("modifyLookahead", theLookahead)

    def modify_lookahead(self, the_lookahead: LogicalTimeIntervalLike) -> None:
        """Delegate the Pythonic RTI service alias to modifyLookahead."""
        return self.modifyLookahead(the_lookahead)

    def negotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service negotiatedAttributeOwnershipDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.3 (Ownership Management)."""
        return self._invoke("negotiatedAttributeOwnershipDivestiture", theObject, theAttributes, userSuppliedTag)

    def negotiated_attribute_ownership_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        """Delegate the Pythonic RTI service alias to negotiatedAttributeOwnershipDivestiture."""
        return self.negotiatedAttributeOwnershipDivestiture(the_object, the_attributes, user_supplied_tag)

    def nextMessageRequest(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        """Delegate HLA RTI service nextMessageRequest to the configured backend. Spec reference: IEEE 1516.1-2010 §8.10 (Time Management)."""
        return self._invoke("nextMessageRequest", theTime)

    def next_message_request(self, the_time: LogicalTimeLike) -> None:
        """Delegate the Pythonic RTI service alias to nextMessageRequest."""
        return self.nextMessageRequest(the_time)

    def nextMessageRequestAvailable(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        """Delegate HLA RTI service nextMessageRequestAvailable to the configured backend. Spec reference: IEEE 1516.1-2010 §8.11 (Time Management)."""
        return self._invoke("nextMessageRequestAvailable", theTime)

    def next_message_request_available(self, the_time: LogicalTimeLike) -> None:
        """Delegate the Pythonic RTI service alias to nextMessageRequestAvailable."""
        return self.nextMessageRequestAvailable(the_time)

    def normalizeFederateHandle(self, federateHandle: FederateHandle) -> int:  # noqa: N802
        """Delegate HLA RTI service normalizeFederateHandle to the configured backend. Spec reference: IEEE 1516.1-2010 §10.31 (Support Services)."""
        return self._invoke("normalizeFederateHandle", federateHandle)

    def normalize_federate_handle(self, federate_handle: FederateHandle) -> int:
        """Delegate the Pythonic RTI service alias to normalizeFederateHandle."""
        return self.normalizeFederateHandle(federate_handle)

    def normalizeServiceGroup(self, group: ServiceGroup) -> int:  # noqa: N802
        """Delegate HLA RTI service normalizeServiceGroup to the configured backend. Spec reference: IEEE 1516.1-2010 §10.32 (Support Services)."""
        return self._invoke("normalizeServiceGroup", group)

    def normalize_service_group(self, group: ServiceGroup) -> int:
        """Delegate the Pythonic RTI service alias to normalizeServiceGroup."""
        return self.normalizeServiceGroup(group)

    def publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service publishInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.4 (Declaration Management)."""
        return self._invoke("publishInteractionClass", theInteraction)

    def publish_interaction_class(self, the_interaction: InteractionClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to publishInteractionClass."""
        return self.publishInteractionClass(the_interaction)

    def publishObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service publishObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.2 (Declaration Management)."""
        return self._invoke("publishObjectClassAttributes", theClass, attributeList)

    def publish_object_class_attributes(self, the_class: ObjectClassHandle, attribute_list: AttributeHandleSet) -> None:
        """Delegate the Pythonic RTI service alias to publishObjectClassAttributes."""
        return self.publishObjectClassAttributes(the_class, attribute_list)

    def queryAttributeOwnership(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service queryAttributeOwnership to the configured backend. Spec reference: IEEE 1516.1-2010 §7.17 (Ownership Management)."""
        return self._invoke("queryAttributeOwnership", theObject, theAttribute)

    def query_attribute_ownership(self, the_object: ObjectInstanceHandle, the_attribute: AttributeHandle) -> None:
        """Delegate the Pythonic RTI service alias to queryAttributeOwnership."""
        return self.queryAttributeOwnership(the_object, the_attribute)

    def queryAttributeTransportationType(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service queryAttributeTransportationType to the configured backend. Spec reference: IEEE 1516.1-2010 §6.25 (Object Management)."""
        return self._invoke("queryAttributeTransportationType", theObject, theAttribute)

    def query_attribute_transportation_type(
        self,
        the_object: ObjectInstanceHandle,
        the_attribute: AttributeHandle,
    ) -> None:
        """Delegate the Pythonic RTI service alias to queryAttributeTransportationType."""
        return self.queryAttributeTransportationType(the_object, the_attribute)

    def queryFederationRestoreStatus(self) -> None:  # noqa: N802
        """Delegate HLA RTI service queryFederationRestoreStatus to the configured backend. Spec reference: IEEE 1516.1-2010 §4.31 (Federation Management)."""
        return self._invoke("queryFederationRestoreStatus")

    def query_federation_restore_status(self) -> None:
        """Delegate the Pythonic RTI service alias to queryFederationRestoreStatus."""
        return self.queryFederationRestoreStatus()

    def queryFederationSaveStatus(self) -> None:  # noqa: N802
        """Delegate HLA RTI service queryFederationSaveStatus to the configured backend. Spec reference: IEEE 1516.1-2010 §4.22 (Federation Management)."""
        return self._invoke("queryFederationSaveStatus")

    def query_federation_save_status(self) -> None:
        """Delegate the Pythonic RTI service alias to queryFederationSaveStatus."""
        return self.queryFederationSaveStatus()

    def queryGALT(self) -> TimeQueryReturn:  # noqa: N802
        """Delegate HLA RTI service queryGALT to the configured backend. Spec reference: IEEE 1516.1-2010 §8.16 (Time Management)."""
        return self._invoke("queryGALT")

    def query_galt(self) -> TimeQueryReturn:
        """Delegate the Pythonic RTI service alias to queryGALT."""
        return self.queryGALT()

    def queryInteractionTransportationType(
        self,
        theFederateOrInteraction: FederateHandle | InteractionClassHandle,
        theInteraction: InteractionClassHandle | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service queryInteractionTransportationType to the configured backend. Spec reference: IEEE 1516.1-2010 §6.29 (Object Management)."""
        if theInteraction is None:
            return self._invoke("queryInteractionTransportationType", theFederateOrInteraction)
        return self._invoke("queryInteractionTransportationType", theFederateOrInteraction, theInteraction)

    def query_interaction_transportation_type(
        self,
        the_interaction: InteractionClassHandle,
        the_federate: FederateHandle | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to queryInteractionTransportationType."""
        if the_federate is None:
            return self._invoke("queryInteractionTransportationType", the_interaction)
        return self._invoke("queryInteractionTransportationType", the_federate, the_interaction)

    def queryLITS(self) -> TimeQueryReturn:  # noqa: N802
        """Delegate HLA RTI service queryLITS to the configured backend. Spec reference: IEEE 1516.1-2010 §8.18 (Time Management)."""
        return self._invoke("queryLITS")

    def query_lits(self) -> TimeQueryReturn:
        """Delegate the Pythonic RTI service alias to queryLITS."""
        return self.queryLITS()

    def queryLogicalTime(self) -> LogicalTimeLike:  # noqa: N802
        """Delegate HLA RTI service queryLogicalTime to the configured backend. Spec reference: IEEE 1516.1-2010 §8.17 (Time Management)."""
        return self._invoke("queryLogicalTime")

    def query_logical_time(self) -> LogicalTimeLike:
        """Delegate the Pythonic RTI service alias to queryLogicalTime."""
        return self.queryLogicalTime()

    def queryLookahead(self) -> LogicalTimeIntervalLike:  # noqa: N802
        """Delegate HLA RTI service queryLookahead to the configured backend. Spec reference: IEEE 1516.1-2010 §8.20 (Time Management)."""
        return self._invoke("queryLookahead")

    def query_lookahead(self) -> LogicalTimeIntervalLike:
        """Delegate the Pythonic RTI service alias to queryLookahead."""
        return self.queryLookahead()

    def registerFederationSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: VariableLengthDataLike,
        synchronizationSet: FederateHandleSet | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service registerFederationSynchronizationPoint to the configured backend. Spec reference: IEEE 1516.1-2010 §4.11 (Federation Management)."""
        args: tuple[object, ...] = (synchronizationPointLabel, userSuppliedTag)
        if synchronizationSet is not None:
            args = (*args, synchronizationSet)
        return self._invoke("registerFederationSynchronizationPoint", *args)

    def register_federation_synchronization_point(
        self,
        synchronization_point_label: str,
        user_supplied_tag: VariableLengthDataLike,
        synchronization_set: FederateHandleSet | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to registerFederationSynchronizationPoint."""
        args: tuple[object, ...] = (synchronization_point_label, user_supplied_tag)
        if synchronization_set is not None:
            args = (*args, synchronization_set)
        return self._invoke("registerFederationSynchronizationPoint", *args)

    def registerObjectInstance(
        self,
        theClass: ObjectClassHandle,
        theObjectName: str | None = None,
    ) -> ObjectInstanceHandle:  # noqa: N802
        """Delegate HLA RTI service registerObjectInstance to the configured backend. Spec reference: IEEE 1516.1-2010 §6.8 (Object Management)."""
        args: tuple[object, ...] = (theClass,)
        if theObjectName is not None:
            args = (*args, theObjectName)
        return self._invoke("registerObjectInstance", *args)

    def register_object_instance(
        self,
        the_class: ObjectClassHandle,
        the_object_name: str | None = None,
    ) -> ObjectInstanceHandle:
        """Delegate the Pythonic RTI service alias to registerObjectInstance."""
        args: tuple[object, ...] = (the_class,)
        if the_object_name is not None:
            args = (*args, the_object_name)
        return self._invoke("registerObjectInstance", *args)

    def registerObjectInstanceWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        theObject: str | None = None,
    ) -> ObjectInstanceHandle:  # noqa: N802
        """Delegate HLA RTI service registerObjectInstanceWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.5 (Data Distribution Management)."""
        args: tuple[object, ...] = (theClass, attributesAndRegions)
        if theObject is not None:
            args = (*args, theObject)
        return self._invoke("registerObjectInstanceWithRegions", *args)

    def register_object_instance_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        the_object: str | None = None,
    ) -> ObjectInstanceHandle:
        """Delegate the Pythonic RTI service alias to registerObjectInstanceWithRegions."""
        args: tuple[object, ...] = (the_class, attributes_and_regions)
        if the_object is not None:
            args = (*args, the_object)
        return self._invoke("registerObjectInstanceWithRegions", *args)

    def releaseMultipleObjectInstanceName(self, theObjectNames: set[str]) -> None:  # noqa: N802
        """Delegate HLA RTI service releaseMultipleObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.7 (Object Management)."""
        return self._invoke("releaseMultipleObjectInstanceName", theObjectNames)

    def release_multiple_object_instance_name(self, the_object_names: set[str]) -> None:
        """Delegate the Pythonic RTI service alias to releaseMultipleObjectInstanceName."""
        return self.releaseMultipleObjectInstanceName(the_object_names)

    def releaseObjectInstanceName(self, theObjectInstanceName: str) -> None:  # noqa: N802
        """Delegate HLA RTI service releaseObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.4 (Object Management)."""
        return self._invoke("releaseObjectInstanceName", theObjectInstanceName)

    def release_object_instance_name(self, the_object_instance_name: str) -> None:
        """Delegate the Pythonic RTI service alias to releaseObjectInstanceName."""
        return self.releaseObjectInstanceName(the_object_instance_name)

    def requestAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theType: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service requestAttributeTransportationTypeChange to the configured backend. Spec reference: IEEE 1516.1-2010 §6.23 (Object Management)."""
        return self._invoke("requestAttributeTransportationTypeChange", theObject, theAttributes, theType)

    def request_attribute_transportation_type_change(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        the_type: TransportationTypeHandle,
    ) -> None:
        """Delegate the Pythonic RTI service alias to requestAttributeTransportationTypeChange."""
        return self.requestAttributeTransportationTypeChange(the_object, the_attributes, the_type)

    def requestAttributeValueUpdate(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service requestAttributeValueUpdate to the configured backend. Spec reference: IEEE 1516.1-2010 §6.19 (Object Management)."""
        return self._invoke("requestAttributeValueUpdate", theObject, theAttributes, userSuppliedTag)

    def request_attribute_value_update(
        self,
        target: ObjectInstanceHandle | ObjectClassHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        """Delegate the Pythonic RTI service alias to requestAttributeValueUpdate."""
        return self._invoke("requestAttributeValueUpdate", target, the_attributes, user_supplied_tag)

    def requestAttributeValueUpdateWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service requestAttributeValueUpdateWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.13 (Data Distribution Management)."""
        return self._invoke("requestAttributeValueUpdateWithRegions", theClass, attributesAndRegions, userSuppliedTag)

    def request_attribute_value_update_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        """Delegate the Pythonic RTI service alias to requestAttributeValueUpdateWithRegions."""
        return self.requestAttributeValueUpdateWithRegions(the_class, attributes_and_regions, user_supplied_tag)

    def requestFederationRestore(self, label: str) -> None:  # noqa: N802
        """Delegate HLA RTI service requestFederationRestore to the configured backend. Spec reference: IEEE 1516.1-2010 §4.24 (Federation Management)."""
        return self._invoke("requestFederationRestore", label)

    def request_federation_restore(self, label: str) -> None:
        """Delegate the Pythonic RTI service alias to requestFederationRestore."""
        return self.requestFederationRestore(label)

    def requestFederationSave(self, label: str, theTime: LogicalTimeLike | None = None) -> None:  # noqa: N802
        """Delegate HLA RTI service requestFederationSave to the configured backend. Spec reference: IEEE 1516.1-2010 §4.16 (Federation Management)."""
        args: tuple[object, ...] = (label,)
        if theTime is not None:
            args = (*args, theTime)
        return self._invoke("requestFederationSave", *args)

    def request_federation_save(self, label: str, the_time: LogicalTimeLike | None = None) -> None:
        """Delegate the Pythonic RTI service alias to requestFederationSave."""
        args: tuple[object, ...] = (label,)
        if the_time is not None:
            args = (*args, the_time)
        return self._invoke("requestFederationSave", *args)

    def requestInteractionTransportationTypeChange(
        self,
        theClass: InteractionClassHandle,
        theType: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service requestInteractionTransportationTypeChange to the configured backend. Spec reference: IEEE 1516.1-2010 §6.27 (Object Management)."""
        return self._invoke("requestInteractionTransportationTypeChange", theClass, theType)

    def request_interaction_transportation_type_change(
        self,
        the_class: InteractionClassHandle,
        the_type: TransportationTypeHandle,
    ) -> None:
        """Delegate the Pythonic RTI service alias to requestInteractionTransportationTypeChange."""
        return self.requestInteractionTransportationTypeChange(the_class, the_type)

    def reserveMultipleObjectInstanceName(self, theObjectNames: set[str]) -> None:  # noqa: N802
        """Delegate HLA RTI service reserveMultipleObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.5 (Object Management)."""
        return self._invoke("reserveMultipleObjectInstanceName", theObjectNames)

    def reserve_multiple_object_instance_name(self, the_object_names: set[str]) -> None:
        """Delegate the Pythonic RTI service alias to reserveMultipleObjectInstanceName."""
        return self.reserveMultipleObjectInstanceName(the_object_names)

    def reserveObjectInstanceName(self, theObjectName: str) -> None:  # noqa: N802
        """Delegate HLA RTI service reserveObjectInstanceName to the configured backend. Spec reference: IEEE 1516.1-2010 §6.2 (Object Management)."""
        return self._invoke("reserveObjectInstanceName", theObjectName)

    def reserve_object_instance_name(self, the_object_name: str) -> None:
        """Delegate the Pythonic RTI service alias to reserveObjectInstanceName."""
        return self.reserveObjectInstanceName(the_object_name)

    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        """Delegate HLA RTI service resignFederationExecution to the configured backend. Spec reference: IEEE 1516.1-2010 §4.10 (Federation Management)."""
        return self._invoke("resignFederationExecution", resignAction)

    def resign_federation_execution(self, resign_action: ResignAction) -> None:
        """Delegate the Pythonic RTI service alias to resignFederationExecution."""
        return self.resignFederationExecution(resign_action)

    def retract(self, theHandle: MessageRetractionHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service retract to the configured backend. Spec reference: IEEE 1516.1-2010 §8.21 (Time Management)."""
        return self._invoke("retract", theHandle)

    def sendInteraction(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service sendInteraction to the configured backend. Spec reference: IEEE 1516.1-2010 §6.12 (Object Management)."""
        args: tuple[object, ...] = (theInteraction, theParameters, userSuppliedTag)
        if theTime is not None:
            args = (*args, theTime)
        return self._invoke("sendInteraction", *args)

    def send_interaction(
        self,
        the_interaction: InteractionClassHandle,
        the_parameters: ParameterHandleValueMap,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to sendInteraction."""
        args: tuple[object, ...] = (the_interaction, the_parameters, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self._invoke("sendInteraction", *args)

    def sendInteractionWithRegions(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        regions: RegionHandleSet,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service sendInteractionWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.12 (Data Distribution Management)."""
        args: tuple[object, ...] = (theInteraction, theParameters, regions, userSuppliedTag)
        if theTime is not None:
            args = (*args, theTime)
        return self._invoke("sendInteractionWithRegions", *args)

    def send_interaction_with_regions(
        self,
        the_interaction: InteractionClassHandle,
        the_parameters: ParameterHandleValueMap,
        regions: RegionHandleSet,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to sendInteractionWithRegions."""
        args: tuple[object, ...] = (the_interaction, the_parameters, regions, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self._invoke("sendInteractionWithRegions", *args)

    def setAutomaticResignDirective(self, resignAction: ResignAction) -> None:  # noqa: N802
        """Delegate HLA RTI service setAutomaticResignDirective to the configured backend. Spec reference: IEEE 1516.1-2010 §10.3 (Support Services)."""
        return self._invoke("setAutomaticResignDirective", resignAction)

    def set_automatic_resign_directive(self, resign_action: ResignAction) -> None:
        """Delegate the Pythonic RTI service alias to setAutomaticResignDirective."""
        return self.setAutomaticResignDirective(resign_action)

    def setRangeBounds(self, region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds) -> None:  # noqa: N802
        """Delegate HLA RTI service setRangeBounds to the configured backend. Spec reference: IEEE 1516.1-2010 §10.30 (Support Services)."""
        return self._invoke("setRangeBounds", region, dimension, bounds)

    def set_range_bounds(self, region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds) -> None:
        """Delegate the Pythonic RTI service alias to setRangeBounds."""
        return self.setRangeBounds(region, dimension, bounds)

    def subscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.8 (Declaration Management)."""
        return self._invoke("subscribeInteractionClass", theClass)

    def subscribe_interaction_class(self, the_class: InteractionClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to subscribeInteractionClass."""
        return self.subscribeInteractionClass(the_class)

    def subscribeInteractionClassPassively(self, theClass: InteractionClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClassPassively to the configured backend. Spec reference: IEEE 1516.1-2010 §5.8 (Declaration Management)."""
        return self._invoke("subscribeInteractionClassPassively", theClass)

    def subscribe_interaction_class_passively(self, the_class: InteractionClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to subscribeInteractionClassPassively."""
        return self.subscribeInteractionClassPassively(the_class)

    def subscribeInteractionClassPassivelyWithRegions(
        self,
        theClass: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClassPassivelyWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.10 (Data Distribution Management)."""
        return self._invoke("subscribeInteractionClassPassivelyWithRegions", theClass, regions)

    def subscribe_interaction_class_passively_with_regions(
        self,
        the_class: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to subscribeInteractionClassPassivelyWithRegions."""
        return self.subscribeInteractionClassPassivelyWithRegions(the_class, regions)

    def subscribeInteractionClassWithRegions(
        self,
        theClass: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeInteractionClassWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.10 (Data Distribution Management)."""
        return self._invoke("subscribeInteractionClassWithRegions", theClass, regions)

    def subscribe_interaction_class_with_regions(
        self,
        the_class: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to subscribeInteractionClassWithRegions."""
        return self.subscribeInteractionClassWithRegions(the_class, regions)

    def subscribeObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.6 (Declaration Management)."""
        args: tuple[object, ...] = (theClass, attributeList)
        if updateRateDesignator is not None:
            args = (*args, updateRateDesignator)
        return self._invoke("subscribeObjectClassAttributes", *args)

    def subscribe_object_class_attributes(
        self,
        the_class: ObjectClassHandle,
        attribute_list: AttributeHandleSet,
        update_rate_designator: str | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to subscribeObjectClassAttributes."""
        args: tuple[object, ...] = (the_class, attribute_list)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self._invoke("subscribeObjectClassAttributes", *args)

    def subscribeObjectClassAttributesPassively(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributesPassively to the configured backend. Spec reference: IEEE 1516.1-2010 §5.6 (Declaration Management)."""
        args: tuple[object, ...] = (theClass, attributeList)
        if updateRateDesignator is not None:
            args = (*args, updateRateDesignator)
        return self._invoke("subscribeObjectClassAttributesPassively", *args)

    def subscribe_object_class_attributes_passively(
        self,
        the_class: ObjectClassHandle,
        attribute_list: AttributeHandleSet,
        update_rate_designator: str | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to subscribeObjectClassAttributesPassively."""
        args: tuple[object, ...] = (the_class, attribute_list)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self._invoke("subscribeObjectClassAttributesPassively", *args)

    def subscribeObjectClassAttributesPassivelyWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributesPassivelyWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.8 (Data Distribution Management)."""
        args: tuple[object, ...] = (theClass, attributesAndRegions)
        if updateRateDesignator is not None:
            args = (*args, updateRateDesignator)
        return self._invoke("subscribeObjectClassAttributesPassivelyWithRegions", *args)

    def subscribe_object_class_attributes_passively_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        update_rate_designator: str | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to subscribeObjectClassAttributesPassivelyWithRegions."""
        args: tuple[object, ...] = (the_class, attributes_and_regions)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self._invoke("subscribeObjectClassAttributesPassivelyWithRegions", *args)

    def subscribeObjectClassAttributesWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service subscribeObjectClassAttributesWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.8 (Data Distribution Management)."""
        args: tuple[object, ...] = (theClass, attributesAndRegions)
        if updateRateDesignator is not None:
            args = (*args, updateRateDesignator)
        return self._invoke("subscribeObjectClassAttributesWithRegions", *args)

    def subscribe_object_class_attributes_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        update_rate_designator: str | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to subscribeObjectClassAttributesWithRegions."""
        args: tuple[object, ...] = (the_class, attributes_and_regions)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self._invoke("subscribeObjectClassAttributesWithRegions", *args)

    def synchronizationPointAchieved(
        self,
        synchronizationPointLabel: str,
        successIndicator: bool | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service synchronizationPointAchieved to the configured backend. Spec reference: IEEE 1516.1-2010 §4.14 (Federation Management)."""
        args: tuple[object, ...] = (synchronizationPointLabel,)
        if successIndicator is not None:
            args = (*args, successIndicator)
        return self._invoke("synchronizationPointAchieved", *args)

    def synchronization_point_achieved(
        self,
        synchronization_point_label: str,
        success_indicator: bool | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to synchronizationPointAchieved."""
        args: tuple[object, ...] = (synchronization_point_label,)
        if success_indicator is not None:
            args = (*args, success_indicator)
        return self._invoke("synchronizationPointAchieved", *args)

    def timeAdvanceRequest(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        """Delegate HLA RTI service timeAdvanceRequest to the configured backend. Spec reference: IEEE 1516.1-2010 §8.8 (Time Management)."""
        return self._invoke("timeAdvanceRequest", theTime)

    def time_advance_request(self, the_time: LogicalTimeLike) -> None:
        """Delegate the Pythonic RTI service alias to timeAdvanceRequest."""
        return self.timeAdvanceRequest(the_time)

    def timeAdvanceRequestAvailable(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        """Delegate HLA RTI service timeAdvanceRequestAvailable to the configured backend. Spec reference: IEEE 1516.1-2010 §8.9 (Time Management)."""
        return self._invoke("timeAdvanceRequestAvailable", theTime)

    def time_advance_request_available(self, the_time: LogicalTimeLike) -> None:
        """Delegate the Pythonic RTI service alias to timeAdvanceRequestAvailable."""
        return self.timeAdvanceRequestAvailable(the_time)

    def unassociateRegionsForUpdates(
        self,
        theObject: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service unassociateRegionsForUpdates to the configured backend. Spec reference: IEEE 1516.1-2010 §9.7 (Data Distribution Management)."""
        return self._invoke("unassociateRegionsForUpdates", theObject, attributesAndRegions)

    def unassociate_regions_for_updates(
        self,
        the_object: ObjectInstanceHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
    ) -> None:
        """Delegate the Pythonic RTI service alias to unassociateRegionsForUpdates."""
        return self.unassociateRegionsForUpdates(the_object, attributes_and_regions)

    def unconditionalAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service unconditionalAttributeOwnershipDivestiture to the configured backend. Spec reference: IEEE 1516.1-2010 §7.2 (Ownership Management)."""
        return self._invoke("unconditionalAttributeOwnershipDivestiture", theObject, theAttributes)

    def unconditional_attribute_ownership_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to unconditionalAttributeOwnershipDivestiture."""
        return self.unconditionalAttributeOwnershipDivestiture(the_object, the_attributes)

    def unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service unpublishInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.5 (Declaration Management)."""
        return self._invoke("unpublishInteractionClass", theInteraction)

    def unpublish_interaction_class(self, the_interaction: InteractionClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to unpublishInteractionClass."""
        return self.unpublishInteractionClass(the_interaction)

    def unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service unpublishObjectClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.3 (Declaration Management)."""
        return self._invoke("unpublishObjectClass", theClass)

    def unpublish_object_class(self, the_class: ObjectClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to unpublishObjectClass."""
        return self.unpublishObjectClass(the_class)

    def unpublishObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service unpublishObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.3 (Declaration Management)."""
        return self._invoke("unpublishObjectClassAttributes", theClass, attributeList)

    def unpublish_object_class_attributes(self, the_class: ObjectClassHandle, attribute_list: AttributeHandleSet) -> None:
        """Delegate the Pythonic RTI service alias to unpublishObjectClassAttributes."""
        return self.unpublishObjectClassAttributes(the_class, attribute_list)

    def unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service unsubscribeInteractionClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.9 (Declaration Management)."""
        return self._invoke("unsubscribeInteractionClass", theClass)

    def unsubscribe_interaction_class(self, the_class: InteractionClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to unsubscribeInteractionClass."""
        return self.unsubscribeInteractionClass(the_class)

    def unsubscribeInteractionClassWithRegions(
        self,
        theClass: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service unsubscribeInteractionClassWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.11 (Data Distribution Management)."""
        return self._invoke("unsubscribeInteractionClassWithRegions", theClass, regions)

    def unsubscribe_interaction_class_with_regions(
        self,
        the_class: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to unsubscribeInteractionClassWithRegions."""
        return self.unsubscribeInteractionClassWithRegions(the_class, regions)

    def unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:  # noqa: N802
        """Delegate HLA RTI service unsubscribeObjectClass to the configured backend. Spec reference: IEEE 1516.1-2010 §5.7 (Declaration Management)."""
        return self._invoke("unsubscribeObjectClass", theClass)

    def unsubscribe_object_class(self, the_class: ObjectClassHandle) -> None:
        """Delegate the Pythonic RTI service alias to unsubscribeObjectClass."""
        return self.unsubscribeObjectClass(the_class)

    def unsubscribeObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service unsubscribeObjectClassAttributes to the configured backend. Spec reference: IEEE 1516.1-2010 §5.7 (Declaration Management)."""
        return self._invoke("unsubscribeObjectClassAttributes", theClass, attributeList)

    def unsubscribe_object_class_attributes(
        self,
        the_class: ObjectClassHandle,
        attribute_list: AttributeHandleSet,
    ) -> None:
        """Delegate the Pythonic RTI service alias to unsubscribeObjectClassAttributes."""
        return self.unsubscribeObjectClassAttributes(the_class, attribute_list)

    def unsubscribeObjectClassAttributesWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service unsubscribeObjectClassAttributesWithRegions to the configured backend. Spec reference: IEEE 1516.1-2010 §9.9 (Data Distribution Management)."""
        return self._invoke("unsubscribeObjectClassAttributesWithRegions", theClass, attributesAndRegions)

    def unsubscribe_object_class_attributes_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
    ) -> None:
        """Delegate the Pythonic RTI service alias to unsubscribeObjectClassAttributesWithRegions."""
        return self.unsubscribeObjectClassAttributesWithRegions(the_class, attributes_and_regions)

    def updateAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleValueMap,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        """Delegate HLA RTI service updateAttributeValues to the configured backend. Spec reference: IEEE 1516.1-2010 §6.10 (Object Management)."""
        args: tuple[object, ...] = (theObject, theAttributes, userSuppliedTag)
        if theTime is not None:
            args = (*args, theTime)
        return self._invoke("updateAttributeValues", *args)

    def update_attribute_values(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleValueMap,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        """Delegate the Pythonic RTI service alias to updateAttributeValues."""
        args: tuple[object, ...] = (the_object, the_attributes, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self._invoke("updateAttributeValues", *args)

    # END GENERATED RTI SERVICE METHODS

class RecordingBackend(RTIBackend):
    """Tiny backend for tests and examples."""

    def __init__(self, results: Mapping[str, Any] | None = None):
        self.info = BackendInfo(name="recording", kind="test")
        self.results: MutableMapping[str, Any] = dict(results or {})
        self.calls: list[Invocation] = []
        self.started = False
        self.closed = False

    def start(self) -> RecordingBackend:
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
