# Generated from specs/hla2010_api.json.
# Do not edit by hand. Run python3 scripts/generate_hla_interface_contracts.py generate.
"""Source-named and Pythonic HLA 1516.1-2010 API contracts.

Java lowerCamelCase method names remain the canonical HLA service names.
Each RTI service and federate callback also exposes the matching Python
snake_case alias with snake_case parameter names.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from os import PathLike
import re
from typing import Callable, TypeAlias

from .enums import (
    CallbackModel,
    OrderType,
    ResignAction,
    RestoreFailureReason,
    SaveFailureReason,
    ServiceGroup,
    SynchronizationPointFailureReason,
    TransportationType,
)
from .handles import (
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
from .time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time, LogicalTimeFactory
from .types import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformationSet,
    MessageRetractionReturn,
    RangeBounds,
    TimeQueryReturn,
)
from .spec_refs import method_reference
from .spec_sources import method_source_summary

LogicalTimeLike: TypeAlias = HLAfloat64Time | HLAinteger64Time | float | int
LogicalTimeIntervalLike: TypeAlias = HLAfloat64Interval | HLAinteger64Interval | float | int
LogicalTimeFactoryLike: TypeAlias = LogicalTimeFactory[HLAinteger64Time | HLAfloat64Time, HLAinteger64Interval | HLAfloat64Interval]
URLLike: TypeAlias = str | PathLike[str]
FomModuleLike: TypeAlias = URLLike | Sequence[URLLike]
VariableLengthDataLike: TypeAlias = bytes | bytearray | memoryview

@dataclass(frozen=True)
class SupplementalReceiveInfo:
    producing_federate: FederateHandle | None = None
    sent_regions: RegionHandleSet | None = None

@dataclass(frozen=True)
class SupplementalReflectInfo:
    producing_federate: FederateHandle | None = None
    sent_regions: RegionHandleSet | None = None

@dataclass(frozen=True)
class SupplementalRemoveInfo:
    producing_federate: FederateHandle | None = None
    sent_regions: RegionHandleSet | None = None


def lower_camel_to_snake(name: str) -> str:
    """Convert a lowerCamelCase HLA method name to snake_case."""
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def _method_doc(method_name: str) -> str:
    ref = method_reference(method_name)
    source_summary = method_source_summary(method_name)
    snake_name = lower_camel_to_snake(method_name)
    doc_parts = [f"{method_name} / {snake_name}"]
    if ref is not None:
        doc_parts.append(f"IEEE reference: {ref.label}.")
    if source_summary:
        doc_parts.append(f"Sources: {source_summary}.")
    return " ".join(doc_parts)


def _service_metadata(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_name = method_name  # type: ignore[attr-defined]
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name)
        return method

    return _decorate


def _callback(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def _decorate(method: Callable[..., object]) -> Callable[..., object]:
        method.spec_name = method_name  # type: ignore[attr-defined]
        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]
        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]
        method.__doc__ = _method_doc(method_name)
        return method

    return _decorate


class RTIambassadorSpec(ABC):
    """Source-named abstract contract for an HLA RTI ambassador."""

    @_service_metadata("abortFederationRestore")
    @abstractmethod
    def abortFederationRestore(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("abortFederationRestore")
    def abort_federation_restore(self) -> None:
        return self.abortFederationRestore()

    @_service_metadata("abortFederationSave")
    @abstractmethod
    def abortFederationSave(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("abortFederationSave")
    def abort_federation_save(self) -> None:
        return self.abortFederationSave()

    @_service_metadata("associateRegionsForUpdates")
    @abstractmethod
    def associateRegionsForUpdates(
        self,
        theObject: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("associateRegionsForUpdates")
    def associate_regions_for_updates(
        self,
        the_object: ObjectInstanceHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
    ) -> None:
        return self.associateRegionsForUpdates(the_object, attributes_and_regions)

    @_service_metadata("attributeOwnershipAcquisition")
    @abstractmethod
    def attributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipAcquisition")
    def attribute_ownership_acquisition(
        self,
        the_object: ObjectInstanceHandle,
        desired_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return self.attributeOwnershipAcquisition(the_object, desired_attributes, user_supplied_tag)

    @_service_metadata("attributeOwnershipAcquisitionIfAvailable")
    @abstractmethod
    def attributeOwnershipAcquisitionIfAvailable(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipAcquisitionIfAvailable")
    def attribute_ownership_acquisition_if_available(
        self,
        the_object: ObjectInstanceHandle,
        desired_attributes: AttributeHandleSet,
    ) -> None:
        return self.attributeOwnershipAcquisitionIfAvailable(the_object, desired_attributes)

    @_service_metadata("attributeOwnershipDivestitureIfWanted")
    @abstractmethod
    def attributeOwnershipDivestitureIfWanted(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> AttributeHandleSet:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipDivestitureIfWanted")
    def attribute_ownership_divestiture_if_wanted(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> AttributeHandleSet:
        return self.attributeOwnershipDivestitureIfWanted(the_object, the_attributes)

    @_service_metadata("attributeOwnershipReleaseDenied")
    @abstractmethod
    def attributeOwnershipReleaseDenied(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("attributeOwnershipReleaseDenied")
    def attribute_ownership_release_denied(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return self.attributeOwnershipReleaseDenied(the_object, the_attributes)

    @_service_metadata("cancelAttributeOwnershipAcquisition")
    @abstractmethod
    def cancelAttributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("cancelAttributeOwnershipAcquisition")
    def cancel_attribute_ownership_acquisition(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return self.cancelAttributeOwnershipAcquisition(the_object, the_attributes)

    @_service_metadata("cancelNegotiatedAttributeOwnershipDivestiture")
    @abstractmethod
    def cancelNegotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("cancelNegotiatedAttributeOwnershipDivestiture")
    def cancel_negotiated_attribute_ownership_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return self.cancelNegotiatedAttributeOwnershipDivestiture(the_object, the_attributes)

    @_service_metadata("changeAttributeOrderType")
    @abstractmethod
    def changeAttributeOrderType(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theType: OrderType,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("changeAttributeOrderType")
    def change_attribute_order_type(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        the_type: OrderType,
    ) -> None:
        return self.changeAttributeOrderType(the_object, the_attributes, the_type)

    @_service_metadata("changeInteractionOrderType")
    @abstractmethod
    def changeInteractionOrderType(self, theClass: InteractionClassHandle, theType: OrderType) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("changeInteractionOrderType")
    def change_interaction_order_type(self, the_class: InteractionClassHandle, the_type: OrderType) -> None:
        return self.changeInteractionOrderType(the_class, the_type)

    @_service_metadata("commitRegionModifications")
    @abstractmethod
    def commitRegionModifications(self, regions: RegionHandleSet) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("commitRegionModifications")
    def commit_region_modifications(self, regions: RegionHandleSet) -> None:
        return self.commitRegionModifications(regions)

    @_service_metadata("confirmDivestiture")
    @abstractmethod
    def confirmDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("confirmDivestiture")
    def confirm_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return self.confirmDivestiture(the_object, the_attributes, user_supplied_tag)

    @_service_metadata("connect")
    @abstractmethod
    def connect(
        self,
        federateReference: FederateAmbassadorSpec,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createFederationExecution")
    @abstractmethod
    def createFederationExecution(
        self,
        federationExecutionName: str,
        fomModules: Sequence[URLLike],
        mimModule: URLLike | None = None,
        logicalTimeImplementationName: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createFederationExecution")
    def create_federation_execution(
        self,
        federation_execution_name: str,
        fom_modules: FomModuleLike,
        *,
        mim_module: URLLike | None = None,
        logical_time_implementation_name: str | None = None,
    ) -> None:
        args: tuple[object, ...] = (federation_execution_name, fom_modules)
        if mim_module is not None:
            args = (*args, mim_module)
        if logical_time_implementation_name is not None:
            args = (*args, logical_time_implementation_name)
        return self.createFederationExecution(*args)

    @_service_metadata("createFederationExecutionWithMIM")
    @abstractmethod
    def createFederationExecutionWithMIM(
        self,
        federationExecutionName: str,
        fomModules: Sequence[URLLike],
        mimModule: str,
        logicalTimeImplementationName: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createFederationExecutionWithMIM")
    def create_federation_execution_with_mim(
        self,
        federation_execution_name: str,
        fom_modules: Sequence[URLLike],
        mim_module: str,
        logical_time_implementation_name: str | None = None,
    ) -> None:
        args: tuple[object, ...] = (federation_execution_name, fom_modules, mim_module)
        if logical_time_implementation_name is not None:
            args = (*args, logical_time_implementation_name)
        return self.createFederationExecutionWithMIM(*args)

    @_service_metadata("createRegion")
    @abstractmethod
    def createRegion(self, dimensions: DimensionHandleSet) -> RegionHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("createRegion")
    def create_region(self, dimensions: DimensionHandleSet) -> RegionHandle:
        return self.createRegion(dimensions)

    @_service_metadata("decodeAttributeHandle")
    @abstractmethod
    def decodeAttributeHandle(self, encodedValue: VariableLengthDataLike) -> AttributeHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeAttributeHandle")
    def decode_attribute_handle(self, encoded_value: VariableLengthDataLike) -> AttributeHandle:
        return self.decodeAttributeHandle(encoded_value)

    @_service_metadata("decodeDimensionHandle")
    @abstractmethod
    def decodeDimensionHandle(self, encodedValue: VariableLengthDataLike) -> DimensionHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeDimensionHandle")
    def decode_dimension_handle(self, encoded_value: VariableLengthDataLike) -> DimensionHandle:
        return self.decodeDimensionHandle(encoded_value)

    @_service_metadata("decodeFederateHandle")
    @abstractmethod
    def decodeFederateHandle(self, encodedValue: VariableLengthDataLike) -> FederateHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeFederateHandle")
    def decode_federate_handle(self, encoded_value: VariableLengthDataLike) -> FederateHandle:
        return self.decodeFederateHandle(encoded_value)

    @_service_metadata("decodeInteractionClassHandle")
    @abstractmethod
    def decodeInteractionClassHandle(self, encodedValue: VariableLengthDataLike) -> InteractionClassHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeInteractionClassHandle")
    def decode_interaction_class_handle(self, encoded_value: VariableLengthDataLike) -> InteractionClassHandle:
        return self.decodeInteractionClassHandle(encoded_value)

    @_service_metadata("decodeMessageRetractionHandle")
    @abstractmethod
    def decodeMessageRetractionHandle(
        self,
        encodedValue: VariableLengthDataLike,
    ) -> MessageRetractionHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeMessageRetractionHandle")
    def decode_message_retraction_handle(self, encoded_value: VariableLengthDataLike) -> MessageRetractionHandle:
        return self.decodeMessageRetractionHandle(encoded_value)

    @_service_metadata("decodeObjectClassHandle")
    @abstractmethod
    def decodeObjectClassHandle(self, encodedValue: VariableLengthDataLike) -> ObjectClassHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeObjectClassHandle")
    def decode_object_class_handle(self, encoded_value: VariableLengthDataLike) -> ObjectClassHandle:
        return self.decodeObjectClassHandle(encoded_value)

    @_service_metadata("decodeObjectInstanceHandle")
    @abstractmethod
    def decodeObjectInstanceHandle(self, encodedValue: VariableLengthDataLike) -> ObjectInstanceHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeObjectInstanceHandle")
    def decode_object_instance_handle(self, encoded_value: VariableLengthDataLike) -> ObjectInstanceHandle:
        return self.decodeObjectInstanceHandle(encoded_value)

    @_service_metadata("decodeParameterHandle")
    @abstractmethod
    def decodeParameterHandle(self, encodedValue: VariableLengthDataLike) -> ParameterHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeParameterHandle")
    def decode_parameter_handle(self, encoded_value: VariableLengthDataLike) -> ParameterHandle:
        return self.decodeParameterHandle(encoded_value)

    @_service_metadata("decodeRegionHandle")
    @abstractmethod
    def decodeRegionHandle(self, encodedValue: VariableLengthDataLike) -> RegionHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("decodeRegionHandle")
    def decode_region_handle(self, encoded_value: VariableLengthDataLike) -> RegionHandle:
        return self.decodeRegionHandle(encoded_value)

    @_service_metadata("deleteObjectInstance")
    @abstractmethod
    def deleteObjectInstance(
        self,
        objectHandle: ObjectInstanceHandle,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("deleteObjectInstance")
    def delete_object_instance(
        self,
        object_handle: ObjectInstanceHandle,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        args: tuple[object, ...] = (object_handle, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self.deleteObjectInstance(*args)

    @_service_metadata("deleteRegion")
    @abstractmethod
    def deleteRegion(self, theRegion: RegionHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("deleteRegion")
    def delete_region(self, the_region: RegionHandle) -> None:
        return self.deleteRegion(the_region)

    @_service_metadata("destroyFederationExecution")
    @abstractmethod
    def destroyFederationExecution(self, federationExecutionName: str) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("destroyFederationExecution")
    def destroy_federation_execution(self, federation_execution_name: str) -> None:
        return self.destroyFederationExecution(federation_execution_name)

    @_service_metadata("disableAsynchronousDelivery")
    @abstractmethod
    def disableAsynchronousDelivery(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableAsynchronousDelivery")
    def disable_asynchronous_delivery(self) -> None:
        return self.disableAsynchronousDelivery()

    @_service_metadata("disableAttributeRelevanceAdvisorySwitch")
    @abstractmethod
    def disableAttributeRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableAttributeRelevanceAdvisorySwitch")
    def disable_attribute_relevance_advisory_switch(self) -> None:
        return self.disableAttributeRelevanceAdvisorySwitch()

    @_service_metadata("disableAttributeScopeAdvisorySwitch")
    @abstractmethod
    def disableAttributeScopeAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableAttributeScopeAdvisorySwitch")
    def disable_attribute_scope_advisory_switch(self) -> None:
        return self.disableAttributeScopeAdvisorySwitch()

    @_service_metadata("disableCallbacks")
    @abstractmethod
    def disableCallbacks(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableCallbacks")
    def disable_callbacks(self) -> None:
        return self.disableCallbacks()

    @_service_metadata("disableInteractionRelevanceAdvisorySwitch")
    @abstractmethod
    def disableInteractionRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableInteractionRelevanceAdvisorySwitch")
    def disable_interaction_relevance_advisory_switch(self) -> None:
        return self.disableInteractionRelevanceAdvisorySwitch()

    @_service_metadata("disableObjectClassRelevanceAdvisorySwitch")
    @abstractmethod
    def disableObjectClassRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableObjectClassRelevanceAdvisorySwitch")
    def disable_object_class_relevance_advisory_switch(self) -> None:
        return self.disableObjectClassRelevanceAdvisorySwitch()

    @_service_metadata("disableTimeConstrained")
    @abstractmethod
    def disableTimeConstrained(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableTimeConstrained")
    def disable_time_constrained(self) -> None:
        return self.disableTimeConstrained()

    @_service_metadata("disableTimeRegulation")
    @abstractmethod
    def disableTimeRegulation(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("disableTimeRegulation")
    def disable_time_regulation(self) -> None:
        return self.disableTimeRegulation()

    @_service_metadata("disconnect")
    @abstractmethod
    def disconnect(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAsynchronousDelivery")
    @abstractmethod
    def enableAsynchronousDelivery(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAsynchronousDelivery")
    def enable_asynchronous_delivery(self) -> None:
        return self.enableAsynchronousDelivery()

    @_service_metadata("enableAttributeRelevanceAdvisorySwitch")
    @abstractmethod
    def enableAttributeRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAttributeRelevanceAdvisorySwitch")
    def enable_attribute_relevance_advisory_switch(self) -> None:
        return self.enableAttributeRelevanceAdvisorySwitch()

    @_service_metadata("enableAttributeScopeAdvisorySwitch")
    @abstractmethod
    def enableAttributeScopeAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableAttributeScopeAdvisorySwitch")
    def enable_attribute_scope_advisory_switch(self) -> None:
        return self.enableAttributeScopeAdvisorySwitch()

    @_service_metadata("enableCallbacks")
    @abstractmethod
    def enableCallbacks(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableCallbacks")
    def enable_callbacks(self) -> None:
        return self.enableCallbacks()

    @_service_metadata("enableInteractionRelevanceAdvisorySwitch")
    @abstractmethod
    def enableInteractionRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableInteractionRelevanceAdvisorySwitch")
    def enable_interaction_relevance_advisory_switch(self) -> None:
        return self.enableInteractionRelevanceAdvisorySwitch()

    @_service_metadata("enableObjectClassRelevanceAdvisorySwitch")
    @abstractmethod
    def enableObjectClassRelevanceAdvisorySwitch(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableObjectClassRelevanceAdvisorySwitch")
    def enable_object_class_relevance_advisory_switch(self) -> None:
        return self.enableObjectClassRelevanceAdvisorySwitch()

    @_service_metadata("enableTimeConstrained")
    @abstractmethod
    def enableTimeConstrained(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableTimeConstrained")
    def enable_time_constrained(self) -> None:
        return self.enableTimeConstrained()

    @_service_metadata("enableTimeRegulation")
    @abstractmethod
    def enableTimeRegulation(self, theLookahead: LogicalTimeIntervalLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("enableTimeRegulation")
    def enable_time_regulation(self, the_lookahead: LogicalTimeIntervalLike) -> None:
        return self.enableTimeRegulation(the_lookahead)

    @_service_metadata("evokeCallback")
    @abstractmethod
    def evokeCallback(self, approximateMinimumTimeInSeconds: float) -> bool:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("evokeCallback")
    def evoke_callback(self, approximate_minimum_time_in_seconds: float) -> bool:
        return self.evokeCallback(approximate_minimum_time_in_seconds)

    @_service_metadata("evokeMultipleCallbacks")
    @abstractmethod
    def evokeMultipleCallbacks(
        self,
        approximateMinimumTimeInSeconds: float,
        approximateMaximumTimeInSeconds: float,
    ) -> bool:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("evokeMultipleCallbacks")
    def evoke_multiple_callbacks(
        self,
        approximate_minimum_time_in_seconds: float,
        approximate_maximum_time_in_seconds: float,
    ) -> bool:
        return self.evokeMultipleCallbacks(approximate_minimum_time_in_seconds, approximate_maximum_time_in_seconds)

    @_service_metadata("federateRestoreComplete")
    @abstractmethod
    def federateRestoreComplete(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateRestoreComplete")
    def federate_restore_complete(self) -> None:
        return self.federateRestoreComplete()

    @_service_metadata("federateRestoreNotComplete")
    @abstractmethod
    def federateRestoreNotComplete(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateRestoreNotComplete")
    def federate_restore_not_complete(self) -> None:
        return self.federateRestoreNotComplete()

    @_service_metadata("federateSaveBegun")
    @abstractmethod
    def federateSaveBegun(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateSaveBegun")
    def federate_save_begun(self) -> None:
        return self.federateSaveBegun()

    @_service_metadata("federateSaveComplete")
    @abstractmethod
    def federateSaveComplete(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateSaveComplete")
    def federate_save_complete(self) -> None:
        return self.federateSaveComplete()

    @_service_metadata("federateSaveNotComplete")
    @abstractmethod
    def federateSaveNotComplete(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("federateSaveNotComplete")
    def federate_save_not_complete(self) -> None:
        return self.federateSaveNotComplete()

    @_service_metadata("flushQueueRequest")
    @abstractmethod
    def flushQueueRequest(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("flushQueueRequest")
    def flush_queue_request(self, the_time: LogicalTimeLike) -> None:
        return self.flushQueueRequest(the_time)

    @_service_metadata("getAttributeHandle")
    @abstractmethod
    def getAttributeHandle(self, whichClass: ObjectClassHandle, theName: str) -> AttributeHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandle")
    def get_attribute_handle(self, which_class: ObjectClassHandle, the_name: str) -> AttributeHandle:
        return self.getAttributeHandle(which_class, the_name)

    @_service_metadata("getAttributeHandleFactory")
    @abstractmethod
    def getAttributeHandleFactory(self) -> AttributeHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandleFactory")
    def get_attribute_handle_factory(self) -> AttributeHandleFactory:
        return self.getAttributeHandleFactory()

    @_service_metadata("getAttributeHandleSetFactory")
    @abstractmethod
    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandleSetFactory")
    def get_attribute_handle_set_factory(self) -> AttributeHandleSetFactory:
        return self.getAttributeHandleSetFactory()

    @_service_metadata("getAttributeHandleValueMapFactory")
    @abstractmethod
    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeHandleValueMapFactory")
    def get_attribute_handle_value_map_factory(self) -> AttributeHandleValueMapFactory:
        return self.getAttributeHandleValueMapFactory()

    @_service_metadata("getAttributeName")
    @abstractmethod
    def getAttributeName(self, whichClass: ObjectClassHandle, theHandle: AttributeHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeName")
    def get_attribute_name(self, which_class: ObjectClassHandle, the_handle: AttributeHandle) -> str:
        return self.getAttributeName(which_class, the_handle)

    @_service_metadata("getAttributeSetRegionSetPairListFactory")
    @abstractmethod
    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAttributeSetRegionSetPairListFactory")
    def get_attribute_set_region_set_pair_list_factory(self) -> AttributeSetRegionSetPairListFactory:
        return self.getAttributeSetRegionSetPairListFactory()

    @_service_metadata("getAutomaticResignDirective")
    @abstractmethod
    def getAutomaticResignDirective(self) -> ResignAction:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAutomaticResignDirective")
    def get_automatic_resign_directive(self) -> ResignAction:
        return self.getAutomaticResignDirective()

    @_service_metadata("getAvailableDimensionsForClassAttribute")
    @abstractmethod
    def getAvailableDimensionsForClassAttribute(
        self,
        whichClass: ObjectClassHandle,
        theHandle: AttributeHandle,
    ) -> DimensionHandleSet:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAvailableDimensionsForClassAttribute")
    def get_available_dimensions_for_class_attribute(
        self,
        which_class: ObjectClassHandle,
        the_handle: AttributeHandle,
    ) -> DimensionHandleSet:
        return self.getAvailableDimensionsForClassAttribute(which_class, the_handle)

    @_service_metadata("getAvailableDimensionsForInteractionClass")
    @abstractmethod
    def getAvailableDimensionsForInteractionClass(
        self,
        theHandle: InteractionClassHandle,
    ) -> DimensionHandleSet:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getAvailableDimensionsForInteractionClass")
    def get_available_dimensions_for_interaction_class(self, the_handle: InteractionClassHandle) -> DimensionHandleSet:
        return self.getAvailableDimensionsForInteractionClass(the_handle)

    @_service_metadata("getDimensionHandle")
    @abstractmethod
    def getDimensionHandle(self, theName: str) -> DimensionHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandle")
    def get_dimension_handle(self, the_name: str) -> DimensionHandle:
        return self.getDimensionHandle(the_name)

    @_service_metadata("getDimensionHandleFactory")
    @abstractmethod
    def getDimensionHandleFactory(self) -> DimensionHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandleFactory")
    def get_dimension_handle_factory(self) -> DimensionHandleFactory:
        return self.getDimensionHandleFactory()

    @_service_metadata("getDimensionHandleSet")
    @abstractmethod
    def getDimensionHandleSet(self, region: RegionHandle) -> DimensionHandleSet:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandleSet")
    def get_dimension_handle_set(self, region: RegionHandle) -> DimensionHandleSet:
        return self.getDimensionHandleSet(region)

    @_service_metadata("getDimensionHandleSetFactory")
    @abstractmethod
    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionHandleSetFactory")
    def get_dimension_handle_set_factory(self) -> DimensionHandleSetFactory:
        return self.getDimensionHandleSetFactory()

    @_service_metadata("getDimensionName")
    @abstractmethod
    def getDimensionName(self, theHandle: DimensionHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionName")
    def get_dimension_name(self, the_handle: DimensionHandle) -> str:
        return self.getDimensionName(the_handle)

    @_service_metadata("getDimensionUpperBound")
    @abstractmethod
    def getDimensionUpperBound(self, theHandle: DimensionHandle) -> int:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getDimensionUpperBound")
    def get_dimension_upper_bound(self, the_handle: DimensionHandle) -> int:
        return self.getDimensionUpperBound(the_handle)

    @_service_metadata("getFederateHandle")
    @abstractmethod
    def getFederateHandle(self, theName: str) -> FederateHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateHandle")
    def get_federate_handle(self, the_name: str) -> FederateHandle:
        return self.getFederateHandle(the_name)

    @_service_metadata("getFederateHandleFactory")
    @abstractmethod
    def getFederateHandleFactory(self) -> FederateHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateHandleFactory")
    def get_federate_handle_factory(self) -> FederateHandleFactory:
        return self.getFederateHandleFactory()

    @_service_metadata("getFederateHandleSetFactory")
    @abstractmethod
    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateHandleSetFactory")
    def get_federate_handle_set_factory(self) -> FederateHandleSetFactory:
        return self.getFederateHandleSetFactory()

    @_service_metadata("getFederateName")
    @abstractmethod
    def getFederateName(self, theHandle: FederateHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getFederateName")
    def get_federate_name(self, the_handle: FederateHandle) -> str:
        return self.getFederateName(the_handle)

    @_service_metadata("getHLAversion")
    @abstractmethod
    def getHLAversion(self) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getHLAversion")
    def get_hla_version(self) -> str:
        return self.getHLAversion()

    @_service_metadata("getInteractionClassHandle")
    @abstractmethod
    def getInteractionClassHandle(self, theName: str) -> InteractionClassHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getInteractionClassHandle")
    def get_interaction_class_handle(self, the_name: str) -> InteractionClassHandle:
        return self.getInteractionClassHandle(the_name)

    @_service_metadata("getInteractionClassHandleFactory")
    @abstractmethod
    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getInteractionClassHandleFactory")
    def get_interaction_class_handle_factory(self) -> InteractionClassHandleFactory:
        return self.getInteractionClassHandleFactory()

    @_service_metadata("getInteractionClassName")
    @abstractmethod
    def getInteractionClassName(self, theHandle: InteractionClassHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getInteractionClassName")
    def get_interaction_class_name(self, the_handle: InteractionClassHandle) -> str:
        return self.getInteractionClassName(the_handle)

    @_service_metadata("getKnownObjectClassHandle")
    @abstractmethod
    def getKnownObjectClassHandle(self, theObject: ObjectInstanceHandle) -> ObjectClassHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getKnownObjectClassHandle")
    def get_known_object_class_handle(self, the_object: ObjectInstanceHandle) -> ObjectClassHandle:
        return self.getKnownObjectClassHandle(the_object)

    @_service_metadata("getObjectClassHandle")
    @abstractmethod
    def getObjectClassHandle(self, theName: str) -> ObjectClassHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectClassHandle")
    def get_object_class_handle(self, the_name: str) -> ObjectClassHandle:
        return self.getObjectClassHandle(the_name)

    @_service_metadata("getObjectClassHandleFactory")
    @abstractmethod
    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectClassHandleFactory")
    def get_object_class_handle_factory(self) -> ObjectClassHandleFactory:
        return self.getObjectClassHandleFactory()

    @_service_metadata("getObjectClassName")
    @abstractmethod
    def getObjectClassName(self, theHandle: ObjectClassHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectClassName")
    def get_object_class_name(self, the_handle: ObjectClassHandle) -> str:
        return self.getObjectClassName(the_handle)

    @_service_metadata("getObjectInstanceHandle")
    @abstractmethod
    def getObjectInstanceHandle(self, theName: str) -> ObjectInstanceHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectInstanceHandle")
    def get_object_instance_handle(self, the_name: str) -> ObjectInstanceHandle:
        return self.getObjectInstanceHandle(the_name)

    @_service_metadata("getObjectInstanceHandleFactory")
    @abstractmethod
    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectInstanceHandleFactory")
    def get_object_instance_handle_factory(self) -> ObjectInstanceHandleFactory:
        return self.getObjectInstanceHandleFactory()

    @_service_metadata("getObjectInstanceName")
    @abstractmethod
    def getObjectInstanceName(self, theHandle: ObjectInstanceHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getObjectInstanceName")
    def get_object_instance_name(self, the_handle: ObjectInstanceHandle) -> str:
        return self.getObjectInstanceName(the_handle)

    @_service_metadata("getOrderName")
    @abstractmethod
    def getOrderName(self, theType: OrderType) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getOrderName")
    def get_order_name(self, the_type: OrderType) -> str:
        return self.getOrderName(the_type)

    @_service_metadata("getOrderType")
    @abstractmethod
    def getOrderType(self, theName: str) -> OrderType:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getOrderType")
    def get_order_type(self, the_name: str) -> OrderType:
        return self.getOrderType(the_name)

    @_service_metadata("getParameterHandle")
    @abstractmethod
    def getParameterHandle(self, whichClass: InteractionClassHandle, theName: str) -> ParameterHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterHandle")
    def get_parameter_handle(self, which_class: InteractionClassHandle, the_name: str) -> ParameterHandle:
        return self.getParameterHandle(which_class, the_name)

    @_service_metadata("getParameterHandleFactory")
    @abstractmethod
    def getParameterHandleFactory(self) -> ParameterHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterHandleFactory")
    def get_parameter_handle_factory(self) -> ParameterHandleFactory:
        return self.getParameterHandleFactory()

    @_service_metadata("getParameterHandleValueMapFactory")
    @abstractmethod
    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterHandleValueMapFactory")
    def get_parameter_handle_value_map_factory(self) -> ParameterHandleValueMapFactory:
        return self.getParameterHandleValueMapFactory()

    @_service_metadata("getParameterName")
    @abstractmethod
    def getParameterName(self, whichClass: InteractionClassHandle, theHandle: ParameterHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getParameterName")
    def get_parameter_name(self, which_class: InteractionClassHandle, the_handle: ParameterHandle) -> str:
        return self.getParameterName(which_class, the_handle)

    @_service_metadata("getRangeBounds")
    @abstractmethod
    def getRangeBounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getRangeBounds")
    def get_range_bounds(self, region: RegionHandle, dimension: DimensionHandle) -> RangeBounds:
        return self.getRangeBounds(region, dimension)

    @_service_metadata("getRegionHandleSetFactory")
    @abstractmethod
    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getRegionHandleSetFactory")
    def get_region_handle_set_factory(self) -> RegionHandleSetFactory:
        return self.getRegionHandleSetFactory()

    @_service_metadata("getTimeFactory")
    @abstractmethod
    def getTimeFactory(self) -> LogicalTimeFactoryLike:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTimeFactory")
    def get_time_factory(self) -> LogicalTimeFactoryLike:
        return self.getTimeFactory()

    @_service_metadata("getTransportationName")
    @abstractmethod
    def getTransportationName(self, transportationType: TransportationType) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationName")
    def get_transportation_name(self, transportation_type: TransportationType) -> str:
        return self.getTransportationName(transportation_type)

    @_service_metadata("getTransportationType")
    @abstractmethod
    def getTransportationType(self, transportationName: str) -> TransportationType:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationType")
    def get_transportation_type(self, transportation_name: str) -> TransportationType:
        return self.getTransportationType(transportation_name)

    @_service_metadata("getTransportationTypeHandle")
    @abstractmethod
    def getTransportationTypeHandle(self, theName: str) -> TransportationTypeHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationTypeHandle")
    def get_transportation_type_handle(self, the_name: str) -> TransportationTypeHandle:
        return self.getTransportationTypeHandle(the_name)

    @_service_metadata("getTransportationTypeHandleFactory")
    @abstractmethod
    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationTypeHandleFactory")
    def get_transportation_type_handle_factory(self) -> TransportationTypeHandleFactory:
        return self.getTransportationTypeHandleFactory()

    @_service_metadata("getTransportationTypeName")
    @abstractmethod
    def getTransportationTypeName(self, theHandle: TransportationTypeHandle) -> str:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getTransportationTypeName")
    def get_transportation_type_name(self, the_handle: TransportationTypeHandle) -> str:
        return self.getTransportationTypeName(the_handle)

    @_service_metadata("getUpdateRateValue")
    @abstractmethod
    def getUpdateRateValue(self, updateRateDesignator: str) -> float:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getUpdateRateValue")
    def get_update_rate_value(self, update_rate_designator: str) -> float:
        return self.getUpdateRateValue(update_rate_designator)

    @_service_metadata("getUpdateRateValueForAttribute")
    @abstractmethod
    def getUpdateRateValueForAttribute(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> float:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("getUpdateRateValueForAttribute")
    def get_update_rate_value_for_attribute(
        self,
        the_object: ObjectInstanceHandle,
        the_attribute: AttributeHandle,
    ) -> float:
        return self.getUpdateRateValueForAttribute(the_object, the_attribute)

    @_service_metadata("isAttributeOwnedByFederate")
    @abstractmethod
    def isAttributeOwnedByFederate(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> bool:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("isAttributeOwnedByFederate")
    def is_attribute_owned_by_federate(self, the_object: ObjectInstanceHandle, the_attribute: AttributeHandle) -> bool:
        return self.isAttributeOwnedByFederate(the_object, the_attribute)

    @_service_metadata("joinFederationExecution")
    @abstractmethod
    def joinFederationExecution(
        self,
        federateName: str,
        federateType: str,
        federationExecutionName: str | None = None,
        additionalFomModules: Sequence[URLLike] | None = None,
    ) -> FederateHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("joinFederationExecution")
    def join_federation_execution(
        self,
        federate_type: str,
        federation_execution_name: str,
        *,
        federate_name: str | None = None,
        additional_fom_modules: Sequence[URLLike] | None = None,
    ) -> FederateHandle:
        if federate_name is None:
            args: tuple[object, ...] = (federate_type, federation_execution_name)
        else:
            args = (federate_name, federate_type, federation_execution_name)
        if additional_fom_modules is not None:
            args = (*args, additional_fom_modules)
        return self.joinFederationExecution(*args)

    @_service_metadata("listFederationExecutions")
    @abstractmethod
    def listFederationExecutions(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("listFederationExecutions")
    def list_federation_executions(self) -> None:
        return self.listFederationExecutions()

    @_service_metadata("localDeleteObjectInstance")
    @abstractmethod
    def localDeleteObjectInstance(self, objectHandle: ObjectInstanceHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("localDeleteObjectInstance")
    def local_delete_object_instance(self, object_handle: ObjectInstanceHandle) -> None:
        return self.localDeleteObjectInstance(object_handle)

    @_service_metadata("modifyLookahead")
    @abstractmethod
    def modifyLookahead(self, theLookahead: LogicalTimeIntervalLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("modifyLookahead")
    def modify_lookahead(self, the_lookahead: LogicalTimeIntervalLike) -> None:
        return self.modifyLookahead(the_lookahead)

    @_service_metadata("negotiatedAttributeOwnershipDivestiture")
    @abstractmethod
    def negotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("negotiatedAttributeOwnershipDivestiture")
    def negotiated_attribute_ownership_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return self.negotiatedAttributeOwnershipDivestiture(the_object, the_attributes, user_supplied_tag)

    @_service_metadata("nextMessageRequest")
    @abstractmethod
    def nextMessageRequest(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("nextMessageRequest")
    def next_message_request(self, the_time: LogicalTimeLike) -> None:
        return self.nextMessageRequest(the_time)

    @_service_metadata("nextMessageRequestAvailable")
    @abstractmethod
    def nextMessageRequestAvailable(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("nextMessageRequestAvailable")
    def next_message_request_available(self, the_time: LogicalTimeLike) -> None:
        return self.nextMessageRequestAvailable(the_time)

    @_service_metadata("normalizeFederateHandle")
    @abstractmethod
    def normalizeFederateHandle(self, federateHandle: FederateHandle) -> int:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("normalizeFederateHandle")
    def normalize_federate_handle(self, federate_handle: FederateHandle) -> int:
        return self.normalizeFederateHandle(federate_handle)

    @_service_metadata("normalizeServiceGroup")
    @abstractmethod
    def normalizeServiceGroup(self, group: ServiceGroup) -> int:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("normalizeServiceGroup")
    def normalize_service_group(self, group: ServiceGroup) -> int:
        return self.normalizeServiceGroup(group)

    @_service_metadata("publishInteractionClass")
    @abstractmethod
    def publishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("publishInteractionClass")
    def publish_interaction_class(self, the_interaction: InteractionClassHandle) -> None:
        return self.publishInteractionClass(the_interaction)

    @_service_metadata("publishObjectClassAttributes")
    @abstractmethod
    def publishObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("publishObjectClassAttributes")
    def publish_object_class_attributes(self, the_class: ObjectClassHandle, attribute_list: AttributeHandleSet) -> None:
        return self.publishObjectClassAttributes(the_class, attribute_list)

    @_service_metadata("queryAttributeOwnership")
    @abstractmethod
    def queryAttributeOwnership(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryAttributeOwnership")
    def query_attribute_ownership(self, the_object: ObjectInstanceHandle, the_attribute: AttributeHandle) -> None:
        return self.queryAttributeOwnership(the_object, the_attribute)

    @_service_metadata("queryAttributeTransportationType")
    @abstractmethod
    def queryAttributeTransportationType(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryAttributeTransportationType")
    def query_attribute_transportation_type(
        self,
        the_object: ObjectInstanceHandle,
        the_attribute: AttributeHandle,
    ) -> None:
        return self.queryAttributeTransportationType(the_object, the_attribute)

    @_service_metadata("queryFederationRestoreStatus")
    @abstractmethod
    def queryFederationRestoreStatus(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryFederationRestoreStatus")
    def query_federation_restore_status(self) -> None:
        return self.queryFederationRestoreStatus()

    @_service_metadata("queryFederationSaveStatus")
    @abstractmethod
    def queryFederationSaveStatus(self) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryFederationSaveStatus")
    def query_federation_save_status(self) -> None:
        return self.queryFederationSaveStatus()

    @_service_metadata("queryGALT")
    @abstractmethod
    def queryGALT(self) -> TimeQueryReturn:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryGALT")
    def query_galt(self) -> TimeQueryReturn:
        return self.queryGALT()

    @_service_metadata("queryInteractionTransportationType")
    @abstractmethod
    def queryInteractionTransportationType(
        self,
        theFederateOrInteraction: FederateHandle | InteractionClassHandle,
        theInteraction: InteractionClassHandle | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryInteractionTransportationType")
    def query_interaction_transportation_type(
        self,
        the_interaction: InteractionClassHandle,
        the_federate: FederateHandle | None = None,
    ) -> None:
        if the_federate is None:
            return self.queryInteractionTransportationType(the_interaction)
        return self.queryInteractionTransportationType(the_federate, the_interaction)

    @_service_metadata("queryLITS")
    @abstractmethod
    def queryLITS(self) -> TimeQueryReturn:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryLITS")
    def query_lits(self) -> TimeQueryReturn:
        return self.queryLITS()

    @_service_metadata("queryLogicalTime")
    @abstractmethod
    def queryLogicalTime(self) -> LogicalTimeLike:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryLogicalTime")
    def query_logical_time(self) -> LogicalTimeLike:
        return self.queryLogicalTime()

    @_service_metadata("queryLookahead")
    @abstractmethod
    def queryLookahead(self) -> LogicalTimeIntervalLike:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("queryLookahead")
    def query_lookahead(self) -> LogicalTimeIntervalLike:
        return self.queryLookahead()

    @_service_metadata("registerFederationSynchronizationPoint")
    @abstractmethod
    def registerFederationSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: VariableLengthDataLike,
        synchronizationSet: FederateHandleSet | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("registerFederationSynchronizationPoint")
    def register_federation_synchronization_point(
        self,
        synchronization_point_label: str,
        user_supplied_tag: VariableLengthDataLike,
        synchronization_set: FederateHandleSet | None = None,
    ) -> None:
        args: tuple[object, ...] = (synchronization_point_label, user_supplied_tag)
        if synchronization_set is not None:
            args = (*args, synchronization_set)
        return self.registerFederationSynchronizationPoint(*args)

    @_service_metadata("registerObjectInstance")
    @abstractmethod
    def registerObjectInstance(
        self,
        theClass: ObjectClassHandle,
        theObjectName: str | None = None,
    ) -> ObjectInstanceHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("registerObjectInstance")
    def register_object_instance(
        self,
        the_class: ObjectClassHandle,
        the_object_name: str | None = None,
    ) -> ObjectInstanceHandle:
        args: tuple[object, ...] = (the_class,)
        if the_object_name is not None:
            args = (*args, the_object_name)
        return self.registerObjectInstance(*args)

    @_service_metadata("registerObjectInstanceWithRegions")
    @abstractmethod
    def registerObjectInstanceWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        theObject: str | None = None,
    ) -> ObjectInstanceHandle:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("registerObjectInstanceWithRegions")
    def register_object_instance_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        the_object: str | None = None,
    ) -> ObjectInstanceHandle:
        args: tuple[object, ...] = (the_class, attributes_and_regions)
        if the_object is not None:
            args = (*args, the_object)
        return self.registerObjectInstanceWithRegions(*args)

    @_service_metadata("releaseMultipleObjectInstanceName")
    @abstractmethod
    def releaseMultipleObjectInstanceName(self, theObjectNames: set[str]) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("releaseMultipleObjectInstanceName")
    def release_multiple_object_instance_name(self, the_object_names: set[str]) -> None:
        return self.releaseMultipleObjectInstanceName(the_object_names)

    @_service_metadata("releaseObjectInstanceName")
    @abstractmethod
    def releaseObjectInstanceName(self, theObjectInstanceName: str) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("releaseObjectInstanceName")
    def release_object_instance_name(self, the_object_instance_name: str) -> None:
        return self.releaseObjectInstanceName(the_object_instance_name)

    @_service_metadata("requestAttributeTransportationTypeChange")
    @abstractmethod
    def requestAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theType: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestAttributeTransportationTypeChange")
    def request_attribute_transportation_type_change(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        the_type: TransportationTypeHandle,
    ) -> None:
        return self.requestAttributeTransportationTypeChange(the_object, the_attributes, the_type)

    @_service_metadata("requestAttributeValueUpdate")
    @abstractmethod
    def requestAttributeValueUpdate(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestAttributeValueUpdate")
    def request_attribute_value_update(
        self,
        target: ObjectInstanceHandle | ObjectClassHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return self.requestAttributeValueUpdate(target, the_attributes, user_supplied_tag)

    @_service_metadata("requestAttributeValueUpdateWithRegions")
    @abstractmethod
    def requestAttributeValueUpdateWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestAttributeValueUpdateWithRegions")
    def request_attribute_value_update_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return self.requestAttributeValueUpdateWithRegions(the_class, attributes_and_regions, user_supplied_tag)

    @_service_metadata("requestFederationRestore")
    @abstractmethod
    def requestFederationRestore(self, label: str) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestFederationRestore")
    def request_federation_restore(self, label: str) -> None:
        return self.requestFederationRestore(label)

    @_service_metadata("requestFederationSave")
    @abstractmethod
    def requestFederationSave(self, label: str, theTime: LogicalTimeLike | None = None) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestFederationSave")
    def request_federation_save(self, label: str, the_time: LogicalTimeLike | None = None) -> None:
        args: tuple[object, ...] = (label,)
        if the_time is not None:
            args = (*args, the_time)
        return self.requestFederationSave(*args)

    @_service_metadata("requestInteractionTransportationTypeChange")
    @abstractmethod
    def requestInteractionTransportationTypeChange(
        self,
        theClass: InteractionClassHandle,
        theType: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("requestInteractionTransportationTypeChange")
    def request_interaction_transportation_type_change(
        self,
        the_class: InteractionClassHandle,
        the_type: TransportationTypeHandle,
    ) -> None:
        return self.requestInteractionTransportationTypeChange(the_class, the_type)

    @_service_metadata("reserveMultipleObjectInstanceName")
    @abstractmethod
    def reserveMultipleObjectInstanceName(self, theObjectNames: set[str]) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("reserveMultipleObjectInstanceName")
    def reserve_multiple_object_instance_name(self, the_object_names: set[str]) -> None:
        return self.reserveMultipleObjectInstanceName(the_object_names)

    @_service_metadata("reserveObjectInstanceName")
    @abstractmethod
    def reserveObjectInstanceName(self, theObjectName: str) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("reserveObjectInstanceName")
    def reserve_object_instance_name(self, the_object_name: str) -> None:
        return self.reserveObjectInstanceName(the_object_name)

    @_service_metadata("resignFederationExecution")
    @abstractmethod
    def resignFederationExecution(self, resignAction: ResignAction) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("resignFederationExecution")
    def resign_federation_execution(self, resign_action: ResignAction) -> None:
        return self.resignFederationExecution(resign_action)

    @_service_metadata("retract")
    @abstractmethod
    def retract(self, theHandle: MessageRetractionHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("sendInteraction")
    @abstractmethod
    def sendInteraction(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("sendInteraction")
    def send_interaction(
        self,
        the_interaction: InteractionClassHandle,
        the_parameters: ParameterHandleValueMap,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_interaction, the_parameters, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self.sendInteraction(*args)

    @_service_metadata("sendInteractionWithRegions")
    @abstractmethod
    def sendInteractionWithRegions(
        self,
        theInteraction: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        regions: RegionHandleSet,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("sendInteractionWithRegions")
    def send_interaction_with_regions(
        self,
        the_interaction: InteractionClassHandle,
        the_parameters: ParameterHandleValueMap,
        regions: RegionHandleSet,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_interaction, the_parameters, regions, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self.sendInteractionWithRegions(*args)

    @_service_metadata("setAutomaticResignDirective")
    @abstractmethod
    def setAutomaticResignDirective(self, resignAction: ResignAction) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("setAutomaticResignDirective")
    def set_automatic_resign_directive(self, resign_action: ResignAction) -> None:
        return self.setAutomaticResignDirective(resign_action)

    @_service_metadata("setRangeBounds")
    @abstractmethod
    def setRangeBounds(self, region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("setRangeBounds")
    def set_range_bounds(self, region: RegionHandle, dimension: DimensionHandle, bounds: RangeBounds) -> None:
        return self.setRangeBounds(region, dimension, bounds)

    @_service_metadata("subscribeInteractionClass")
    @abstractmethod
    def subscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClass")
    def subscribe_interaction_class(self, the_class: InteractionClassHandle) -> None:
        return self.subscribeInteractionClass(the_class)

    @_service_metadata("subscribeInteractionClassPassively")
    @abstractmethod
    def subscribeInteractionClassPassively(self, theClass: InteractionClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClassPassively")
    def subscribe_interaction_class_passively(self, the_class: InteractionClassHandle) -> None:
        return self.subscribeInteractionClassPassively(the_class)

    @_service_metadata("subscribeInteractionClassPassivelyWithRegions")
    @abstractmethod
    def subscribeInteractionClassPassivelyWithRegions(
        self,
        theClass: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClassPassivelyWithRegions")
    def subscribe_interaction_class_passively_with_regions(
        self,
        the_class: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:
        return self.subscribeInteractionClassPassivelyWithRegions(the_class, regions)

    @_service_metadata("subscribeInteractionClassWithRegions")
    @abstractmethod
    def subscribeInteractionClassWithRegions(
        self,
        theClass: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeInteractionClassWithRegions")
    def subscribe_interaction_class_with_regions(
        self,
        the_class: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:
        return self.subscribeInteractionClassWithRegions(the_class, regions)

    @_service_metadata("subscribeObjectClassAttributes")
    @abstractmethod
    def subscribeObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributes")
    def subscribe_object_class_attributes(
        self,
        the_class: ObjectClassHandle,
        attribute_list: AttributeHandleSet,
        update_rate_designator: str | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_class, attribute_list)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self.subscribeObjectClassAttributes(*args)

    @_service_metadata("subscribeObjectClassAttributesPassively")
    @abstractmethod
    def subscribeObjectClassAttributesPassively(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributesPassively")
    def subscribe_object_class_attributes_passively(
        self,
        the_class: ObjectClassHandle,
        attribute_list: AttributeHandleSet,
        update_rate_designator: str | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_class, attribute_list)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self.subscribeObjectClassAttributesPassively(*args)

    @_service_metadata("subscribeObjectClassAttributesPassivelyWithRegions")
    @abstractmethod
    def subscribeObjectClassAttributesPassivelyWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributesPassivelyWithRegions")
    def subscribe_object_class_attributes_passively_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        update_rate_designator: str | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_class, attributes_and_regions)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self.subscribeObjectClassAttributesPassivelyWithRegions(*args)

    @_service_metadata("subscribeObjectClassAttributesWithRegions")
    @abstractmethod
    def subscribeObjectClassAttributesWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("subscribeObjectClassAttributesWithRegions")
    def subscribe_object_class_attributes_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
        update_rate_designator: str | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_class, attributes_and_regions)
        if update_rate_designator is not None:
            args = (*args, update_rate_designator)
        return self.subscribeObjectClassAttributesWithRegions(*args)

    @_service_metadata("synchronizationPointAchieved")
    @abstractmethod
    def synchronizationPointAchieved(
        self,
        synchronizationPointLabel: str,
        successIndicator: bool | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("synchronizationPointAchieved")
    def synchronization_point_achieved(
        self,
        synchronization_point_label: str,
        success_indicator: bool | None = None,
    ) -> None:
        args: tuple[object, ...] = (synchronization_point_label,)
        if success_indicator is not None:
            args = (*args, success_indicator)
        return self.synchronizationPointAchieved(*args)

    @_service_metadata("timeAdvanceRequest")
    @abstractmethod
    def timeAdvanceRequest(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("timeAdvanceRequest")
    def time_advance_request(self, the_time: LogicalTimeLike) -> None:
        return self.timeAdvanceRequest(the_time)

    @_service_metadata("timeAdvanceRequestAvailable")
    @abstractmethod
    def timeAdvanceRequestAvailable(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("timeAdvanceRequestAvailable")
    def time_advance_request_available(self, the_time: LogicalTimeLike) -> None:
        return self.timeAdvanceRequestAvailable(the_time)

    @_service_metadata("unassociateRegionsForUpdates")
    @abstractmethod
    def unassociateRegionsForUpdates(
        self,
        theObject: ObjectInstanceHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unassociateRegionsForUpdates")
    def unassociate_regions_for_updates(
        self,
        the_object: ObjectInstanceHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
    ) -> None:
        return self.unassociateRegionsForUpdates(the_object, attributes_and_regions)

    @_service_metadata("unconditionalAttributeOwnershipDivestiture")
    @abstractmethod
    def unconditionalAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unconditionalAttributeOwnershipDivestiture")
    def unconditional_attribute_ownership_divestiture(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return self.unconditionalAttributeOwnershipDivestiture(the_object, the_attributes)

    @_service_metadata("unpublishInteractionClass")
    @abstractmethod
    def unpublishInteractionClass(self, theInteraction: InteractionClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unpublishInteractionClass")
    def unpublish_interaction_class(self, the_interaction: InteractionClassHandle) -> None:
        return self.unpublishInteractionClass(the_interaction)

    @_service_metadata("unpublishObjectClass")
    @abstractmethod
    def unpublishObjectClass(self, theClass: ObjectClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unpublishObjectClass")
    def unpublish_object_class(self, the_class: ObjectClassHandle) -> None:
        return self.unpublishObjectClass(the_class)

    @_service_metadata("unpublishObjectClassAttributes")
    @abstractmethod
    def unpublishObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unpublishObjectClassAttributes")
    def unpublish_object_class_attributes(self, the_class: ObjectClassHandle, attribute_list: AttributeHandleSet) -> None:
        return self.unpublishObjectClassAttributes(the_class, attribute_list)

    @_service_metadata("unsubscribeInteractionClass")
    @abstractmethod
    def unsubscribeInteractionClass(self, theClass: InteractionClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeInteractionClass")
    def unsubscribe_interaction_class(self, the_class: InteractionClassHandle) -> None:
        return self.unsubscribeInteractionClass(the_class)

    @_service_metadata("unsubscribeInteractionClassWithRegions")
    @abstractmethod
    def unsubscribeInteractionClassWithRegions(
        self,
        theClass: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeInteractionClassWithRegions")
    def unsubscribe_interaction_class_with_regions(
        self,
        the_class: InteractionClassHandle,
        regions: RegionHandleSet,
    ) -> None:
        return self.unsubscribeInteractionClassWithRegions(the_class, regions)

    @_service_metadata("unsubscribeObjectClass")
    @abstractmethod
    def unsubscribeObjectClass(self, theClass: ObjectClassHandle) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeObjectClass")
    def unsubscribe_object_class(self, the_class: ObjectClassHandle) -> None:
        return self.unsubscribeObjectClass(the_class)

    @_service_metadata("unsubscribeObjectClassAttributes")
    @abstractmethod
    def unsubscribeObjectClassAttributes(
        self,
        theClass: ObjectClassHandle,
        attributeList: AttributeHandleSet,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeObjectClassAttributes")
    def unsubscribe_object_class_attributes(
        self,
        the_class: ObjectClassHandle,
        attribute_list: AttributeHandleSet,
    ) -> None:
        return self.unsubscribeObjectClassAttributes(the_class, attribute_list)

    @_service_metadata("unsubscribeObjectClassAttributesWithRegions")
    @abstractmethod
    def unsubscribeObjectClassAttributesWithRegions(
        self,
        theClass: ObjectClassHandle,
        attributesAndRegions: AttributeSetRegionSetPairList,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("unsubscribeObjectClassAttributesWithRegions")
    def unsubscribe_object_class_attributes_with_regions(
        self,
        the_class: ObjectClassHandle,
        attributes_and_regions: AttributeSetRegionSetPairList,
    ) -> None:
        return self.unsubscribeObjectClassAttributesWithRegions(the_class, attributes_and_regions)

    @_service_metadata("updateAttributeValues")
    @abstractmethod
    def updateAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleValueMap,
        userSuppliedTag: VariableLengthDataLike,
        theTime: LogicalTimeLike | None = None,
    ) -> None:  # noqa: N802
        raise NotImplementedError

    @_service_metadata("updateAttributeValues")
    def update_attribute_values(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleValueMap,
        user_supplied_tag: VariableLengthDataLike,
        the_time: LogicalTimeLike | None = None,
    ) -> None:
        args: tuple[object, ...] = (the_object, the_attributes, user_supplied_tag)
        if the_time is not None:
            args = (*args, the_time)
        return self.updateAttributeValues(*args)


class FederateAmbassadorSpec:
    """No-op federate callback prototype with Java names and Python aliases."""

    @_callback("announceSynchronizationPoint")
    def announce_synchronization_point(
        self,
        synchronization_point_label: str,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return None

    @_callback("announceSynchronizationPoint")
    def announceSynchronizationPoint(
        self,
        synchronizationPointLabel: str,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        return self.announce_synchronization_point(synchronizationPointLabel, userSuppliedTag)

    @_callback("attributeIsNotOwned")
    def attribute_is_not_owned(self, the_object: ObjectInstanceHandle, the_attribute: AttributeHandle) -> None:
        return None

    @_callback("attributeIsNotOwned")
    def attributeIsNotOwned(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:  # noqa: N802
        return self.attribute_is_not_owned(theObject, theAttribute)

    @_callback("attributeIsOwnedByRTI")
    def attribute_is_owned_by_rti(self, the_object: ObjectInstanceHandle, the_attribute: AttributeHandle) -> None:
        return None

    @_callback("attributeIsOwnedByRTI")
    def attributeIsOwnedByRTI(self, theObject: ObjectInstanceHandle, theAttribute: AttributeHandle) -> None:  # noqa: N802
        return self.attribute_is_owned_by_rti(theObject, theAttribute)

    @_callback("attributeOwnershipAcquisitionNotification")
    def attribute_ownership_acquisition_notification(
        self,
        the_object: ObjectInstanceHandle,
        secured_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return None

    @_callback("attributeOwnershipAcquisitionNotification")
    def attributeOwnershipAcquisitionNotification(
        self,
        theObject: ObjectInstanceHandle,
        securedAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        return self.attribute_ownership_acquisition_notification(theObject, securedAttributes, userSuppliedTag)

    @_callback("attributeOwnershipUnavailable")
    def attribute_ownership_unavailable(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return None

    @_callback("attributeOwnershipUnavailable")
    def attributeOwnershipUnavailable(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        return self.attribute_ownership_unavailable(theObject, theAttributes)

    @_callback("attributesInScope")
    def attributes_in_scope(self, the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet) -> None:
        return None

    @_callback("attributesInScope")
    def attributesInScope(self, theObject: ObjectInstanceHandle, theAttributes: AttributeHandleSet) -> None:  # noqa: N802
        return self.attributes_in_scope(theObject, theAttributes)

    @_callback("attributesOutOfScope")
    def attributes_out_of_scope(self, the_object: ObjectInstanceHandle, the_attributes: AttributeHandleSet) -> None:
        return None

    @_callback("attributesOutOfScope")
    def attributesOutOfScope(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        return self.attributes_out_of_scope(theObject, theAttributes)

    @_callback("confirmAttributeOwnershipAcquisitionCancellation")
    def confirm_attribute_ownership_acquisition_cancellation(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return None

    @_callback("confirmAttributeOwnershipAcquisitionCancellation")
    def confirmAttributeOwnershipAcquisitionCancellation(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        return self.confirm_attribute_ownership_acquisition_cancellation(theObject, theAttributes)

    @_callback("confirmAttributeTransportationTypeChange")
    def confirm_attribute_transportation_type_change(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        the_transportation: TransportationTypeHandle,
    ) -> None:
        return None

    @_callback("confirmAttributeTransportationTypeChange")
    def confirmAttributeTransportationTypeChange(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        theTransportation: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        return self.confirm_attribute_transportation_type_change(theObject, theAttributes, theTransportation)

    @_callback("confirmInteractionTransportationTypeChange")
    def confirm_interaction_transportation_type_change(
        self,
        the_interaction: InteractionClassHandle,
        the_transportation: TransportationTypeHandle,
    ) -> None:
        return None

    @_callback("confirmInteractionTransportationTypeChange")
    def confirmInteractionTransportationTypeChange(
        self,
        theInteraction: InteractionClassHandle,
        theTransportation: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        return self.confirm_interaction_transportation_type_change(theInteraction, theTransportation)

    @_callback("connectionLost")
    def connection_lost(self, fault_description: str) -> None:
        return None

    @_callback("connectionLost")
    def connectionLost(self, faultDescription: str) -> None:  # noqa: N802
        return self.connection_lost(faultDescription)

    @_callback("discoverObjectInstance")
    def discover_object_instance(
        self,
        the_object: ObjectInstanceHandle,
        the_object_class: ObjectClassHandle,
        object_name: str,
        producing_federate: FederateHandle | None = None,
    ) -> None:
        return None

    @_callback("discoverObjectInstance")
    def discoverObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theObjectClass: ObjectClassHandle,
        objectName: str,
        producingFederate: FederateHandle | None = None,
    ) -> None:  # noqa: N802
        args: tuple[object, ...] = (theObject, theObjectClass, objectName)
        if producingFederate is not None:
            args = (*args, producingFederate)
        return self.discover_object_instance(*args)

    @_callback("federationNotRestored")
    def federation_not_restored(self, reason: RestoreFailureReason) -> None:
        return None

    @_callback("federationNotRestored")
    def federationNotRestored(self, reason: RestoreFailureReason) -> None:  # noqa: N802
        return self.federation_not_restored(reason)

    @_callback("federationNotSaved")
    def federation_not_saved(self, reason: SaveFailureReason) -> None:
        return None

    @_callback("federationNotSaved")
    def federationNotSaved(self, reason: SaveFailureReason) -> None:  # noqa: N802
        return self.federation_not_saved(reason)

    @_callback("federationRestoreBegun")
    def federation_restore_begun(self) -> None:
        return None

    @_callback("federationRestoreBegun")
    def federationRestoreBegun(self) -> None:  # noqa: N802
        return self.federation_restore_begun()

    @_callback("federationRestoreStatusResponse")
    def federation_restore_status_response(self, response: Sequence[FederateRestoreStatus]) -> None:
        return None

    @_callback("federationRestoreStatusResponse")
    def federationRestoreStatusResponse(self, response: Sequence[FederateRestoreStatus]) -> None:  # noqa: N802
        return self.federation_restore_status_response(response)

    @_callback("federationRestored")
    def federation_restored(self) -> None:
        return None

    @_callback("federationRestored")
    def federationRestored(self) -> None:  # noqa: N802
        return self.federation_restored()

    @_callback("federationSaveStatusResponse")
    def federation_save_status_response(self, response: Sequence[FederateHandleSaveStatusPair]) -> None:
        return None

    @_callback("federationSaveStatusResponse")
    def federationSaveStatusResponse(self, response: Sequence[FederateHandleSaveStatusPair]) -> None:  # noqa: N802
        return self.federation_save_status_response(response)

    @_callback("federationSaved")
    def federation_saved(self) -> None:
        return None

    @_callback("federationSaved")
    def federationSaved(self) -> None:  # noqa: N802
        return self.federation_saved()

    @_callback("federationSynchronized")
    def federation_synchronized(self, synchronization_point_label: str, failed_to_sync_set: FederateHandleSet) -> None:
        return None

    @_callback("federationSynchronized")
    def federationSynchronized(
        self,
        synchronizationPointLabel: str,
        failedToSyncSet: FederateHandleSet,
    ) -> None:  # noqa: N802
        return self.federation_synchronized(synchronizationPointLabel, failedToSyncSet)

    @_callback("getProducingFederate")
    def get_producing_federate(self) -> FederateHandle:
        return None

    @_callback("getProducingFederate")
    def getProducingFederate(self) -> FederateHandle:  # noqa: N802
        return self.get_producing_federate()

    @_callback("getSentRegions")
    def get_sent_regions(self) -> RegionHandleSet:
        return None

    @_callback("getSentRegions")
    def getSentRegions(self) -> RegionHandleSet:  # noqa: N802
        return self.get_sent_regions()

    @_callback("hasProducingFederate")
    def has_producing_federate(self) -> bool:
        return None

    @_callback("hasProducingFederate")
    def hasProducingFederate(self) -> bool:  # noqa: N802
        return self.has_producing_federate()

    @_callback("hasSentRegions")
    def has_sent_regions(self) -> bool:
        return None

    @_callback("hasSentRegions")
    def hasSentRegions(self) -> bool:  # noqa: N802
        return self.has_sent_regions()

    @_callback("informAttributeOwnership")
    def inform_attribute_ownership(
        self,
        the_object: ObjectInstanceHandle,
        the_attribute: AttributeHandle,
        the_owner: FederateHandle,
    ) -> None:
        return None

    @_callback("informAttributeOwnership")
    def informAttributeOwnership(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
        theOwner: FederateHandle,
    ) -> None:  # noqa: N802
        return self.inform_attribute_ownership(theObject, theAttribute, theOwner)

    @_callback("initiateFederateRestore")
    def initiate_federate_restore(self, label: str, federate_name: str, federate_handle: FederateHandle) -> None:
        return None

    @_callback("initiateFederateRestore")
    def initiateFederateRestore(
        self,
        label: str,
        federateName: str,
        federateHandle: FederateHandle,
    ) -> None:  # noqa: N802
        return self.initiate_federate_restore(label, federateName, federateHandle)

    @_callback("initiateFederateSave")
    def initiate_federate_save(self, label: str, time: LogicalTimeLike | None = None) -> None:
        return None

    @_callback("initiateFederateSave")
    def initiateFederateSave(self, label: str, time: LogicalTimeLike | None = None) -> None:  # noqa: N802
        args: tuple[object, ...] = (label,)
        if time is not None:
            args = (*args, time)
        return self.initiate_federate_save(*args)

    @_callback("multipleObjectInstanceNameReservationFailed")
    def multiple_object_instance_name_reservation_failed(self, object_names: set[str]) -> None:
        return None

    @_callback("multipleObjectInstanceNameReservationFailed")
    def multipleObjectInstanceNameReservationFailed(self, objectNames: set[str]) -> None:  # noqa: N802
        return self.multiple_object_instance_name_reservation_failed(objectNames)

    @_callback("multipleObjectInstanceNameReservationSucceeded")
    def multiple_object_instance_name_reservation_succeeded(self, object_names: set[str]) -> None:
        return None

    @_callback("multipleObjectInstanceNameReservationSucceeded")
    def multipleObjectInstanceNameReservationSucceeded(self, objectNames: set[str]) -> None:  # noqa: N802
        return self.multiple_object_instance_name_reservation_succeeded(objectNames)

    @_callback("objectInstanceNameReservationFailed")
    def object_instance_name_reservation_failed(self, object_name: str) -> None:
        return None

    @_callback("objectInstanceNameReservationFailed")
    def objectInstanceNameReservationFailed(self, objectName: str) -> None:  # noqa: N802
        return self.object_instance_name_reservation_failed(objectName)

    @_callback("objectInstanceNameReservationSucceeded")
    def object_instance_name_reservation_succeeded(self, object_name: str) -> None:
        return None

    @_callback("objectInstanceNameReservationSucceeded")
    def objectInstanceNameReservationSucceeded(self, objectName: str) -> None:  # noqa: N802
        return self.object_instance_name_reservation_succeeded(objectName)

    @_callback("provideAttributeValueUpdate")
    def provide_attribute_value_update(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return None

    @_callback("provideAttributeValueUpdate")
    def provideAttributeValueUpdate(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        return self.provide_attribute_value_update(theObject, theAttributes, userSuppliedTag)

    @_callback("receiveInteraction")
    def receive_interaction(
        self,
        interaction_class: InteractionClassHandle,
        the_parameters: ParameterHandleValueMap,
        user_supplied_tag: VariableLengthDataLike,
        sent_ordering: OrderType,
        the_transport: TransportationTypeHandle,
        the_time: LogicalTimeLike | None = None,
        received_ordering: OrderType | None = None,
        retraction_handle: MessageRetractionHandle | None = None,
        receive_info: SupplementalReceiveInfo | None = None,
    ) -> None:
        return None

    @_callback("receiveInteraction")
    def receiveInteraction(
        self,
        interactionClass: InteractionClassHandle,
        theParameters: ParameterHandleValueMap,
        userSuppliedTag: VariableLengthDataLike,
        sentOrdering: OrderType,
        theTransport: TransportationTypeHandle,
        theTime: LogicalTimeLike | None = None,
        receivedOrdering: OrderType | None = None,
        retractionHandle: MessageRetractionHandle | None = None,
        receiveInfo: SupplementalReceiveInfo | None = None,
    ) -> None:  # noqa: N802
        return self.receive_interaction(
            interactionClass,
            theParameters,
            userSuppliedTag,
            sentOrdering,
            theTransport,
            theTime,
            receivedOrdering,
            retractionHandle,
            receiveInfo,
        )

    @_callback("reflectAttributeValues")
    def reflect_attribute_values(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleValueMap,
        user_supplied_tag: VariableLengthDataLike,
        sent_ordering: OrderType,
        the_transport: TransportationTypeHandle,
        the_time: LogicalTimeLike | None = None,
        received_ordering: OrderType | None = None,
        retraction_handle: MessageRetractionHandle | None = None,
        reflect_info: SupplementalReflectInfo | None = None,
    ) -> None:
        return None

    @_callback("reflectAttributeValues")
    def reflectAttributeValues(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleValueMap,
        userSuppliedTag: VariableLengthDataLike,
        sentOrdering: OrderType,
        theTransport: TransportationTypeHandle,
        theTime: LogicalTimeLike | None = None,
        receivedOrdering: OrderType | None = None,
        retractionHandle: MessageRetractionHandle | None = None,
        reflectInfo: SupplementalReflectInfo | None = None,
    ) -> None:  # noqa: N802
        return self.reflect_attribute_values(
            theObject,
            theAttributes,
            userSuppliedTag,
            sentOrdering,
            theTransport,
            theTime,
            receivedOrdering,
            retractionHandle,
            reflectInfo,
        )

    @_callback("removeObjectInstance")
    def remove_object_instance(
        self,
        the_object: ObjectInstanceHandle,
        user_supplied_tag: VariableLengthDataLike,
        sent_ordering: OrderType,
        the_time: LogicalTimeLike | None = None,
        received_ordering: OrderType | None = None,
        retraction_handle: MessageRetractionHandle | None = None,
        remove_info: SupplementalRemoveInfo | None = None,
    ) -> None:
        return None

    @_callback("removeObjectInstance")
    def removeObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        userSuppliedTag: VariableLengthDataLike,
        sentOrdering: OrderType,
        theTime: LogicalTimeLike | None = None,
        receivedOrdering: OrderType | None = None,
        retractionHandle: MessageRetractionHandle | None = None,
        removeInfo: SupplementalRemoveInfo | None = None,
    ) -> None:  # noqa: N802
        return self.remove_object_instance(
            theObject,
            userSuppliedTag,
            sentOrdering,
            theTime,
            receivedOrdering,
            retractionHandle,
            removeInfo,
        )

    @_callback("reportAttributeTransportationType")
    def report_attribute_transportation_type(
        self,
        the_object: ObjectInstanceHandle,
        the_attribute: AttributeHandle,
        the_transportation: TransportationTypeHandle,
    ) -> None:
        return None

    @_callback("reportAttributeTransportationType")
    def reportAttributeTransportationType(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
        theTransportation: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        return self.report_attribute_transportation_type(theObject, theAttribute, theTransportation)

    @_callback("reportFederationExecutions")
    def report_federation_executions(
        self,
        the_federation_execution_information_set: FederationExecutionInformationSet,
    ) -> None:
        return None

    @_callback("reportFederationExecutions")
    def reportFederationExecutions(
        self,
        theFederationExecutionInformationSet: FederationExecutionInformationSet,
    ) -> None:  # noqa: N802
        return self.report_federation_executions(theFederationExecutionInformationSet)

    @_callback("reportInteractionTransportationType")
    def report_interaction_transportation_type(
        self,
        the_federate: FederateHandle,
        the_interaction: InteractionClassHandle,
        the_transportation: TransportationTypeHandle,
    ) -> None:
        return None

    @_callback("reportInteractionTransportationType")
    def reportInteractionTransportationType(
        self,
        theFederate: FederateHandle,
        theInteraction: InteractionClassHandle,
        theTransportation: TransportationTypeHandle,
    ) -> None:  # noqa: N802
        return self.report_interaction_transportation_type(theFederate, theInteraction, theTransportation)

    @_callback("requestAttributeOwnershipAssumption")
    def request_attribute_ownership_assumption(
        self,
        the_object: ObjectInstanceHandle,
        offered_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return None

    @_callback("requestAttributeOwnershipAssumption")
    def requestAttributeOwnershipAssumption(
        self,
        theObject: ObjectInstanceHandle,
        offeredAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        return self.request_attribute_ownership_assumption(theObject, offeredAttributes, userSuppliedTag)

    @_callback("requestAttributeOwnershipRelease")
    def request_attribute_ownership_release(
        self,
        the_object: ObjectInstanceHandle,
        candidate_attributes: AttributeHandleSet,
        user_supplied_tag: VariableLengthDataLike,
    ) -> None:
        return None

    @_callback("requestAttributeOwnershipRelease")
    def requestAttributeOwnershipRelease(
        self,
        theObject: ObjectInstanceHandle,
        candidateAttributes: AttributeHandleSet,
        userSuppliedTag: VariableLengthDataLike,
    ) -> None:  # noqa: N802
        return self.request_attribute_ownership_release(theObject, candidateAttributes, userSuppliedTag)

    @_callback("requestDivestitureConfirmation")
    def request_divestiture_confirmation(
        self,
        the_object: ObjectInstanceHandle,
        offered_attributes: AttributeHandleSet,
    ) -> None:
        return None

    @_callback("requestDivestitureConfirmation")
    def requestDivestitureConfirmation(
        self,
        theObject: ObjectInstanceHandle,
        offeredAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        return self.request_divestiture_confirmation(theObject, offeredAttributes)

    @_callback("requestFederationRestoreFailed")
    def request_federation_restore_failed(self, label: str) -> None:
        return None

    @_callback("requestFederationRestoreFailed")
    def requestFederationRestoreFailed(self, label: str) -> None:  # noqa: N802
        return self.request_federation_restore_failed(label)

    @_callback("requestFederationRestoreSucceeded")
    def request_federation_restore_succeeded(self, label: str) -> None:
        return None

    @_callback("requestFederationRestoreSucceeded")
    def requestFederationRestoreSucceeded(self, label: str) -> None:  # noqa: N802
        return self.request_federation_restore_succeeded(label)

    @_callback("requestRetraction")
    def request_retraction(self, the_handle: MessageRetractionHandle) -> None:
        return None

    @_callback("requestRetraction")
    def requestRetraction(self, theHandle: MessageRetractionHandle) -> None:  # noqa: N802
        return self.request_retraction(theHandle)

    @_callback("startRegistrationForObjectClass")
    def start_registration_for_object_class(self, the_class: ObjectClassHandle) -> None:
        return None

    @_callback("startRegistrationForObjectClass")
    def startRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:  # noqa: N802
        return self.start_registration_for_object_class(theClass)

    @_callback("stopRegistrationForObjectClass")
    def stop_registration_for_object_class(self, the_class: ObjectClassHandle) -> None:
        return None

    @_callback("stopRegistrationForObjectClass")
    def stopRegistrationForObjectClass(self, theClass: ObjectClassHandle) -> None:  # noqa: N802
        return self.stop_registration_for_object_class(theClass)

    @_callback("synchronizationPointRegistrationFailed")
    def synchronization_point_registration_failed(
        self,
        synchronization_point_label: str,
        reason: SynchronizationPointFailureReason,
    ) -> None:
        return None

    @_callback("synchronizationPointRegistrationFailed")
    def synchronizationPointRegistrationFailed(
        self,
        synchronizationPointLabel: str,
        reason: SynchronizationPointFailureReason,
    ) -> None:  # noqa: N802
        return self.synchronization_point_registration_failed(synchronizationPointLabel, reason)

    @_callback("synchronizationPointRegistrationSucceeded")
    def synchronization_point_registration_succeeded(self, synchronization_point_label: str) -> None:
        return None

    @_callback("synchronizationPointRegistrationSucceeded")
    def synchronizationPointRegistrationSucceeded(self, synchronizationPointLabel: str) -> None:  # noqa: N802
        return self.synchronization_point_registration_succeeded(synchronizationPointLabel)

    @_callback("timeAdvanceGrant")
    def time_advance_grant(self, the_time: LogicalTimeLike) -> None:
        return None

    @_callback("timeAdvanceGrant")
    def timeAdvanceGrant(self, theTime: LogicalTimeLike) -> None:  # noqa: N802
        return self.time_advance_grant(theTime)

    @_callback("timeConstrainedEnabled")
    def time_constrained_enabled(self, time: LogicalTimeLike) -> None:
        return None

    @_callback("timeConstrainedEnabled")
    def timeConstrainedEnabled(self, time: LogicalTimeLike) -> None:  # noqa: N802
        return self.time_constrained_enabled(time)

    @_callback("timeRegulationEnabled")
    def time_regulation_enabled(self, time: LogicalTimeLike) -> None:
        return None

    @_callback("timeRegulationEnabled")
    def timeRegulationEnabled(self, time: LogicalTimeLike) -> None:  # noqa: N802
        return self.time_regulation_enabled(time)

    @_callback("turnInteractionsOff")
    def turn_interactions_off(self, the_handle: InteractionClassHandle) -> None:
        return None

    @_callback("turnInteractionsOff")
    def turnInteractionsOff(self, theHandle: InteractionClassHandle) -> None:  # noqa: N802
        return self.turn_interactions_off(theHandle)

    @_callback("turnInteractionsOn")
    def turn_interactions_on(self, the_handle: InteractionClassHandle) -> None:
        return None

    @_callback("turnInteractionsOn")
    def turnInteractionsOn(self, theHandle: InteractionClassHandle) -> None:  # noqa: N802
        return self.turn_interactions_on(theHandle)

    @_callback("turnUpdatesOffForObjectInstance")
    def turn_updates_off_for_object_instance(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
    ) -> None:
        return None

    @_callback("turnUpdatesOffForObjectInstance")
    def turnUpdatesOffForObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
    ) -> None:  # noqa: N802
        return self.turn_updates_off_for_object_instance(theObject, theAttributes)

    @_callback("turnUpdatesOnForObjectInstance")
    def turn_updates_on_for_object_instance(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: AttributeHandleSet,
        update_rate_designator: str | None = None,
    ) -> None:
        return None

    @_callback("turnUpdatesOnForObjectInstance")
    def turnUpdatesOnForObjectInstance(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: AttributeHandleSet,
        updateRateDesignator: str | None = None,
    ) -> None:  # noqa: N802
        args: tuple[object, ...] = (theObject, theAttributes)
        if updateRateDesignator is not None:
            args = (*args, updateRateDesignator)
        return self.turn_updates_on_for_object_instance(*args)

RTIAmbassadorSpec = RTIambassadorSpec
NullFederateAmbassadorSpec = FederateAmbassadorSpec

__all__ = [
    "FederateAmbassadorSpec",
    "NullFederateAmbassadorSpec",
    "RTIAmbassadorSpec",
    "RTIambassadorSpec",
    "SupplementalReceiveInfo",
    "SupplementalReflectInfo",
    "SupplementalRemoveInfo",
    "lower_camel_to_snake",
]
