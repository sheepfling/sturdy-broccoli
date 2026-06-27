"""Mechanical support-surface wrappers for the Python 2025 RTI ambassador."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol

from hla.rti1516_2025.datatypes import RangeBounds
from hla.rti1516_2025.enums import OrderType, ResignAction, ServiceGroup
from hla.rti1516_2025.handles import (
    AttributeHandle,
    AttributeHandleFactory,
    AttributeHandleSetFactory,
    AttributeHandleValueMapFactory,
    AttributeSetRegionSetPairListFactory,
    DimensionHandle,
    DimensionHandleFactory,
    DimensionHandleSetFactory,
    FederateHandle,
    FederateHandleFactory,
    FederateHandleSetFactory,
    InteractionClassHandle,
    InteractionClassHandleFactory,
    InteractionClassHandleSetFactory,
    MessageRetractionHandle,
    MessageRetractionHandleFactory,
    ObjectClassHandle,
    ObjectClassHandleFactory,
    ObjectInstanceHandle,
    ObjectInstanceHandleFactory,
    ParameterHandle,
    ParameterHandleFactory,
    ParameterHandleValueMapFactory,
    RegionHandle,
    RegionHandleFactory,
    RegionHandleSetFactory,
    TransportationTypeHandle,
    TransportationTypeHandleFactory,
)

from .support_lookup_runtime import (
    get_attribute_handle,
    get_attribute_name,
    get_available_dimensions_for_interaction_class,
    get_available_dimensions_for_object_class,
    get_dimension_handle,
    get_dimension_name,
    get_dimension_upper_bound,
    get_federate_handle,
    get_federate_name,
    get_interaction_class_handle,
    get_interaction_class_name,
    get_known_object_class_handle,
    get_object_class_handle,
    get_object_class_name,
    get_object_instance_handle,
    get_object_instance_name,
    get_order_name,
    get_order_type,
    get_parameter_handle,
    get_parameter_name,
    get_transportation_type_handle,
    get_transportation_type_name,
)
from .support_policy_runtime import (
    get_automatic_resign_directive,
    get_switch,
    normalize_service_group,
    serialize_mom_service_report,
    service_report_records_snapshot,
    set_attribute_scope_advisory_switch,
    set_automatic_resign_directive,
    set_switch,
)
from .support_services_runtime import (
    decode_attribute_handle as runtime_decode_attribute_handle,
    decode_dimension_handle as runtime_decode_dimension_handle,
    decode_federate_handle as runtime_decode_federate_handle,
    decode_interaction_class_handle as runtime_decode_interaction_class_handle,
    decode_message_retraction_handle as runtime_decode_message_retraction_handle,
    decode_object_class_handle as runtime_decode_object_class_handle,
    decode_object_instance_handle as runtime_decode_object_instance_handle,
    decode_parameter_handle as runtime_decode_parameter_handle,
    decode_region_handle as runtime_decode_region_handle,
    make_attribute_handle_factory,
    make_attribute_handle_set_factory,
    make_attribute_handle_value_map_factory,
    make_attribute_set_region_set_pair_list_factory,
    make_dimension_handle_factory,
    make_dimension_handle_set_factory,
    make_federate_handle_factory,
    make_federate_handle_set_factory,
    make_interaction_class_handle_factory,
    make_interaction_class_handle_set_factory,
    make_message_retraction_handle_factory,
    make_object_class_handle_factory,
    make_object_instance_handle_factory,
    make_parameter_handle_factory,
    make_parameter_handle_value_map_factory,
    make_region_handle_factory,
    make_region_handle_set_factory,
    make_transportation_type_handle_factory,
)
from .update_rate_runtime import get_update_rate_value

if TYPE_CHECKING:
    class _SupportSurfaceContext(Protocol):
        _default_attribute_transportation: dict[tuple[str, str], str]
        _default_attribute_order: dict[tuple[str, str], Any]
        _mom_report_period_seconds: float | None
        _logical_time_factory: Any

        def _record(self, method_name: str, *args: Any, **kwargs: Any) -> None: ...

        def _require_connected(self, method_name: str) -> None: ...

        def _require_joined(self, method_name: str) -> None: ...

        @staticmethod
        def _normalize_handle(handle: Any, expected_type: type[Any], exception_type: type[Exception]) -> int: ...

        def _object_instance_record(self, object_instance: Any) -> Any: ...

        def _attribute_name_by_handle(self, object_class_name: str, attribute: Any) -> str: ...

        def _subscribed_update_rate_for_attribute(
            self,
            federate_key: int,
            actual_class_name: str,
            attribute_name: str,
        ) -> float: ...

        def _current_federate_key(self) -> int: ...


if TYPE_CHECKING:
    class _SupportSurfaceMixinBase(_SupportSurfaceContext):
        pass
else:
    class _SupportSurfaceMixinBase:
        pass


class SupportSurfaceMixin(_SupportSurfaceMixinBase):
    """Keep the main ambassador focused on runtime semantics over API plumbing."""

    def getObjectClassHandle(self, objectClassName: str) -> ObjectClassHandle:  # noqa: N802
        self._record("getObjectClassHandle", objectClassName)
        self._require_joined("getObjectClassHandle")
        return get_object_class_handle(self, objectClassName)

    def getObjectClassName(self, objectClass: Any) -> str:  # noqa: N802
        self._record("getObjectClassName", objectClass)
        return get_object_class_name(self, objectClass)

    def getAttributeHandle(self, objectClass: Any, attributeName: str) -> AttributeHandle:  # noqa: N802
        self._record("getAttributeHandle", objectClass, attributeName)
        return get_attribute_handle(self, objectClass, attributeName)

    def getAttributeName(self, objectClass: Any, attribute: Any) -> str:  # noqa: N802
        self._record("getAttributeName", objectClass, attribute)
        return get_attribute_name(self, objectClass, attribute)

    def getInteractionClassHandle(self, interactionClassName: str) -> InteractionClassHandle:  # noqa: N802
        self._record("getInteractionClassHandle", interactionClassName)
        self._require_joined("getInteractionClassHandle")
        return get_interaction_class_handle(self, interactionClassName)

    def getInteractionClassName(self, interactionClass: Any) -> str:  # noqa: N802
        self._record("getInteractionClassName", interactionClass)
        return get_interaction_class_name(self, interactionClass)

    def getParameterHandle(self, interactionClass: Any, parameterName: str) -> ParameterHandle:  # noqa: N802
        self._record("getParameterHandle", interactionClass, parameterName)
        return get_parameter_handle(self, interactionClass, parameterName)

    def getParameterName(self, interactionClass: Any, parameter: Any) -> str:  # noqa: N802
        self._record("getParameterName", interactionClass, parameter)
        return get_parameter_name(self, interactionClass, parameter)

    def getTransportationTypeHandle(self, transportationTypeName: str) -> TransportationTypeHandle:  # noqa: N802
        self._record("getTransportationTypeHandle", transportationTypeName)
        self._require_joined("getTransportationTypeHandle")
        return get_transportation_type_handle(self, transportationTypeName)

    def getTransportationTypeName(self, transportationType: Any) -> str:  # noqa: N802
        self._record("getTransportationTypeName", transportationType)
        return get_transportation_type_name(self, transportationType)

    def getDimensionHandle(self, dimensionName: str) -> DimensionHandle:  # noqa: N802
        self._record("getDimensionHandle", dimensionName)
        self._require_joined("getDimensionHandle")
        return get_dimension_handle(self, dimensionName)

    def getDimensionName(self, dimension: Any) -> str:  # noqa: N802
        self._record("getDimensionName", dimension)
        return get_dimension_name(self, dimension)

    def getDimensionUpperBound(self, dimension: Any) -> int:  # noqa: N802
        self._record("getDimensionUpperBound", dimension)
        return get_dimension_upper_bound(self, dimension)

    def getAvailableDimensionsForObjectClass(self, objectClass: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getAvailableDimensionsForObjectClass", objectClass)
        return get_available_dimensions_for_object_class(self, objectClass)

    def getAvailableDimensionsForInteractionClass(self, interactionClass: Any) -> set[DimensionHandle]:  # noqa: N802
        self._record("getAvailableDimensionsForInteractionClass", interactionClass)
        return get_available_dimensions_for_interaction_class(self, interactionClass)

    def defaultAttributePolicySnapshot(self) -> dict[str, dict[str, str]]:  # noqa: N802
        self._record("defaultAttributePolicySnapshot")
        self._require_joined("defaultAttributePolicySnapshot")
        return {
            "transportation": {
                f"{object_class}.{attribute}": transportation
                for (object_class, attribute), transportation in sorted(self._default_attribute_transportation.items())
            },
            "order": {
                f"{object_class}.{attribute}": order.name
                for (object_class, attribute), order in sorted(self._default_attribute_order.items())
            },
        }

    def serializeMOMServiceReport(  # noqa: N802
        self,
        serviceName: str,
        *,
        success: bool = True,
        exception: str | None = None,
        arguments: Mapping[str, Any] | None = None,
        returned: Mapping[str, Any] | None = None,
        result: Any = None,
    ) -> dict[str, Any]:
        self._record(
            "serializeMOMServiceReport",
            serviceName,
            success=success,
            exception=exception,
            arguments=arguments,
            returned=returned,
            result=result,
        )
        self._require_joined("serializeMOMServiceReport")
        return serialize_mom_service_report(
            self,
            serviceName,
            success=success,
            exception=exception,
            arguments=arguments,
            returned=returned,
            result=result,
        )

    def serviceReportRecordsSnapshot(self) -> tuple[dict[str, Any], ...]:  # noqa: N802
        self._record("serviceReportRecordsSnapshot")
        self._require_joined("serviceReportRecordsSnapshot")
        return service_report_records_snapshot(self)

    def momReportPeriodSecondsSnapshot(self) -> float | None:  # noqa: N802
        self._record("momReportPeriodSecondsSnapshot")
        self._require_joined("momReportPeriodSecondsSnapshot")
        return self._mom_report_period_seconds

    def getFederateHandle(self, federateName: str) -> FederateHandle:  # noqa: N802
        self._record("getFederateHandle", federateName)
        self._require_joined("getFederateHandle")
        return get_federate_handle(self, federateName)

    def getFederateName(self, federate: Any) -> str:  # noqa: N802
        self._record("getFederateName", federate)
        self._require_joined("getFederateName")
        return get_federate_name(self, federate)

    def getKnownObjectClassHandle(self, objectInstance: Any) -> ObjectClassHandle:  # noqa: N802
        self._record("getKnownObjectClassHandle", objectInstance)
        self._require_joined("getKnownObjectClassHandle")
        return get_known_object_class_handle(self, objectInstance)

    def getObjectInstanceHandle(self, objectInstanceName: str) -> ObjectInstanceHandle:  # noqa: N802
        self._record("getObjectInstanceHandle", objectInstanceName)
        self._require_joined("getObjectInstanceHandle")
        return get_object_instance_handle(self, objectInstanceName)

    def getObjectInstanceName(self, objectInstance: Any) -> str:  # noqa: N802
        self._record("getObjectInstanceName", objectInstance)
        self._require_joined("getObjectInstanceName")
        return get_object_instance_name(self, objectInstance)

    def getOrderType(self, orderTypeName: str) -> OrderType:  # noqa: N802
        self._record("getOrderType", orderTypeName)
        self._require_joined("getOrderType")
        return get_order_type(self, orderTypeName)

    def getOrderName(self, orderType: Any) -> str:  # noqa: N802
        self._record("getOrderName", orderType)
        self._require_joined("getOrderName")
        return get_order_name(self, orderType)

    def getUpdateRateValue(self, updateRateDesignator: str) -> float:  # noqa: N802
        self._record("getUpdateRateValue", updateRateDesignator)
        self._require_joined("getUpdateRateValue")
        return get_update_rate_value(
            self,
            updateRateDesignator,
            invalid_update_rate_designator_exc=self._invalid_update_rate_designator_type(),
        )

    def getUpdateRateValueForAttribute(self, theObject: Any, theAttribute: Any) -> float:  # noqa: N802
        self._record("getUpdateRateValueForAttribute", theObject, theAttribute)
        self._require_joined("getUpdateRateValueForAttribute")
        record = self._object_instance_record(theObject)
        attribute_name = self._attribute_name_by_handle(record.object_class_name, theAttribute)
        return self._subscribed_update_rate_for_attribute(
            self._current_federate_key(),
            record.object_class_name,
            attribute_name,
        )

    def getAttributeHandleFactory(self) -> AttributeHandleFactory:  # noqa: N802
        self._record("getAttributeHandleFactory")
        self._require_connected("getAttributeHandleFactory")
        return make_attribute_handle_factory()

    def getAttributeHandleSetFactory(self) -> AttributeHandleSetFactory:  # noqa: N802
        self._record("getAttributeHandleSetFactory")
        self._require_connected("getAttributeHandleSetFactory")
        return make_attribute_handle_set_factory()

    def getAttributeHandleValueMapFactory(self) -> AttributeHandleValueMapFactory:  # noqa: N802
        self._record("getAttributeHandleValueMapFactory")
        self._require_connected("getAttributeHandleValueMapFactory")
        return make_attribute_handle_value_map_factory()

    def getAttributeSetRegionSetPairListFactory(self) -> AttributeSetRegionSetPairListFactory:  # noqa: N802
        self._record("getAttributeSetRegionSetPairListFactory")
        self._require_connected("getAttributeSetRegionSetPairListFactory")
        return make_attribute_set_region_set_pair_list_factory()

    def getDimensionHandleFactory(self) -> DimensionHandleFactory:  # noqa: N802
        self._record("getDimensionHandleFactory")
        self._require_connected("getDimensionHandleFactory")
        return make_dimension_handle_factory()

    def getDimensionHandleSetFactory(self) -> DimensionHandleSetFactory:  # noqa: N802
        self._record("getDimensionHandleSetFactory")
        self._require_connected("getDimensionHandleSetFactory")
        return make_dimension_handle_set_factory()

    def getFederateHandleFactory(self) -> FederateHandleFactory:  # noqa: N802
        self._record("getFederateHandleFactory")
        self._require_connected("getFederateHandleFactory")
        return make_federate_handle_factory()

    def getFederateHandleSetFactory(self) -> FederateHandleSetFactory:  # noqa: N802
        self._record("getFederateHandleSetFactory")
        self._require_connected("getFederateHandleSetFactory")
        return make_federate_handle_set_factory()

    def getInteractionClassHandleFactory(self) -> InteractionClassHandleFactory:  # noqa: N802
        self._record("getInteractionClassHandleFactory")
        self._require_connected("getInteractionClassHandleFactory")
        return make_interaction_class_handle_factory()

    def getInteractionClassHandleSetFactory(self) -> InteractionClassHandleSetFactory:  # noqa: N802
        self._record("getInteractionClassHandleSetFactory")
        self._require_connected("getInteractionClassHandleSetFactory")
        return make_interaction_class_handle_set_factory()

    def getObjectClassHandleFactory(self) -> ObjectClassHandleFactory:  # noqa: N802
        self._record("getObjectClassHandleFactory")
        self._require_connected("getObjectClassHandleFactory")
        return make_object_class_handle_factory()

    def getObjectInstanceHandleFactory(self) -> ObjectInstanceHandleFactory:  # noqa: N802
        self._record("getObjectInstanceHandleFactory")
        self._require_connected("getObjectInstanceHandleFactory")
        return make_object_instance_handle_factory()

    def getParameterHandleFactory(self) -> ParameterHandleFactory:  # noqa: N802
        self._record("getParameterHandleFactory")
        self._require_connected("getParameterHandleFactory")
        return make_parameter_handle_factory()

    def getParameterHandleValueMapFactory(self) -> ParameterHandleValueMapFactory:  # noqa: N802
        self._record("getParameterHandleValueMapFactory")
        self._require_connected("getParameterHandleValueMapFactory")
        return make_parameter_handle_value_map_factory()

    def getRegionHandleSetFactory(self) -> RegionHandleSetFactory:  # noqa: N802
        self._record("getRegionHandleSetFactory")
        self._require_connected("getRegionHandleSetFactory")
        return make_region_handle_set_factory()

    def getTransportationTypeHandleFactory(self) -> TransportationTypeHandleFactory:  # noqa: N802
        self._record("getTransportationTypeHandleFactory")
        self._require_connected("getTransportationTypeHandleFactory")
        return make_transportation_type_handle_factory()

    def decodeFederateHandle(self, encodedValue: bytes) -> FederateHandle:  # noqa: N802
        self._record("decodeFederateHandle", encodedValue)
        self._require_connected("decodeFederateHandle")
        return runtime_decode_federate_handle(encodedValue, self._invalid_federate_handle_type())

    def decodeObjectClassHandle(self, encodedValue: bytes) -> ObjectClassHandle:  # noqa: N802
        self._record("decodeObjectClassHandle", encodedValue)
        self._require_connected("decodeObjectClassHandle")
        return runtime_decode_object_class_handle(encodedValue, self._invalid_object_class_handle_type())

    def decodeInteractionClassHandle(self, encodedValue: bytes) -> InteractionClassHandle:  # noqa: N802
        self._record("decodeInteractionClassHandle", encodedValue)
        self._require_connected("decodeInteractionClassHandle")
        return runtime_decode_interaction_class_handle(encodedValue, self._invalid_interaction_class_handle_type())

    def decodeObjectInstanceHandle(self, encodedValue: bytes) -> ObjectInstanceHandle:  # noqa: N802
        self._record("decodeObjectInstanceHandle", encodedValue)
        self._require_connected("decodeObjectInstanceHandle")
        return runtime_decode_object_instance_handle(encodedValue, self._invalid_object_instance_handle_type())

    def decodeAttributeHandle(self, encodedValue: bytes) -> AttributeHandle:  # noqa: N802
        self._record("decodeAttributeHandle", encodedValue)
        self._require_connected("decodeAttributeHandle")
        return runtime_decode_attribute_handle(encodedValue, self._invalid_attribute_handle_type())

    def decodeParameterHandle(self, encodedValue: bytes) -> ParameterHandle:  # noqa: N802
        self._record("decodeParameterHandle", encodedValue)
        self._require_connected("decodeParameterHandle")
        return runtime_decode_parameter_handle(encodedValue, self._invalid_parameter_handle_type())

    def decodeDimensionHandle(self, encodedValue: bytes) -> DimensionHandle:  # noqa: N802
        self._record("decodeDimensionHandle", encodedValue)
        self._require_connected("decodeDimensionHandle")
        return runtime_decode_dimension_handle(encodedValue, self._invalid_dimension_handle_type())

    def decodeMessageRetractionHandle(self, encodedValue: bytes) -> MessageRetractionHandle:  # noqa: N802
        self._record("decodeMessageRetractionHandle", encodedValue)
        self._require_connected("decodeMessageRetractionHandle")
        return runtime_decode_message_retraction_handle(encodedValue, self._invalid_message_retraction_handle_type())

    def decodeRegionHandle(self, encodedValue: bytes) -> RegionHandle:  # noqa: N802
        self._record("decodeRegionHandle", encodedValue)
        self._require_connected("decodeRegionHandle")
        return runtime_decode_region_handle(encodedValue, self._invalid_region_handle_type())

    def getRegionHandleFactory(self) -> RegionHandleFactory:  # noqa: N802
        self._record("getRegionHandleFactory")
        self._require_connected("getRegionHandleFactory")
        return make_region_handle_factory()

    def getMessageRetractionHandleFactory(self) -> MessageRetractionHandleFactory:  # noqa: N802
        self._record("getMessageRetractionHandleFactory")
        self._require_connected("getMessageRetractionHandleFactory")
        return make_message_retraction_handle_factory()

    def getTimeFactory(self) -> Any:  # noqa: N802
        self._record("getTimeFactory")
        self._require_connected("getTimeFactory")
        return self._logical_time_factory

    def normalizeServiceGroup(self, serviceGroup: Any) -> int:  # noqa: N802
        self._record("normalizeServiceGroup", serviceGroup)
        self._require_joined("normalizeServiceGroup")
        return normalize_service_group(serviceGroup)

    def normalizeFederateHandle(self, federate: Any) -> int:  # noqa: N802
        self._record("normalizeFederateHandle", federate)
        self._require_joined("normalizeFederateHandle")
        return self._normalize_handle(federate, FederateHandle, self._invalid_federate_handle_type())

    def normalizeObjectClassHandle(self, objectClass: Any) -> int:  # noqa: N802
        self._record("normalizeObjectClassHandle", objectClass)
        self._require_joined("normalizeObjectClassHandle")
        return self._normalize_handle(objectClass, ObjectClassHandle, self._invalid_object_class_handle_type())

    def normalizeInteractionClassHandle(self, interactionClass: Any) -> int:  # noqa: N802
        self._record("normalizeInteractionClassHandle", interactionClass)
        self._require_joined("normalizeInteractionClassHandle")
        return self._normalize_handle(
            interactionClass,
            InteractionClassHandle,
            self._invalid_interaction_class_handle_type(),
        )

    def normalizeObjectInstanceHandle(self, objectInstance: Any) -> int:  # noqa: N802
        self._record("normalizeObjectInstanceHandle", objectInstance)
        self._require_joined("normalizeObjectInstanceHandle")
        return self._normalize_handle(
            objectInstance,
            ObjectInstanceHandle,
            self._invalid_object_instance_handle_type(),
        )

    def getObjectClassRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getObjectClassRelevanceAdvisorySwitch")
        return get_switch(self, "getObjectClassRelevanceAdvisorySwitch", "object_class_relevance_advisory")

    def setObjectClassRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setObjectClassRelevanceAdvisorySwitch", value)
        set_switch(self, "setObjectClassRelevanceAdvisorySwitch", "object_class_relevance_advisory", value)

    def enable_object_class_relevance_advisory_switch(self) -> None:
        self.setObjectClassRelevanceAdvisorySwitch(True)

    def disable_object_class_relevance_advisory_switch(self) -> None:
        self.setObjectClassRelevanceAdvisorySwitch(False)

    def getAttributeRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getAttributeRelevanceAdvisorySwitch")
        return get_switch(self, "getAttributeRelevanceAdvisorySwitch", "attribute_relevance_advisory")

    def setAttributeRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setAttributeRelevanceAdvisorySwitch", value)
        set_switch(self, "setAttributeRelevanceAdvisorySwitch", "attribute_relevance_advisory", value)

    def getAttributeScopeAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getAttributeScopeAdvisorySwitch")
        return get_switch(self, "getAttributeScopeAdvisorySwitch", "attribute_scope_advisory")

    def setAttributeScopeAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setAttributeScopeAdvisorySwitch", value)
        set_attribute_scope_advisory_switch(self, value)

    def enable_attribute_scope_advisory_switch(self) -> None:
        self.setAttributeScopeAdvisorySwitch(True)

    def disable_attribute_scope_advisory_switch(self) -> None:
        self.setAttributeScopeAdvisorySwitch(False)

    def getInteractionRelevanceAdvisorySwitch(self) -> bool:  # noqa: N802
        self._record("getInteractionRelevanceAdvisorySwitch")
        return get_switch(self, "getInteractionRelevanceAdvisorySwitch", "interaction_relevance_advisory")

    def setInteractionRelevanceAdvisorySwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setInteractionRelevanceAdvisorySwitch", value)
        set_switch(self, "setInteractionRelevanceAdvisorySwitch", "interaction_relevance_advisory", value)

    def enable_interaction_relevance_advisory_switch(self) -> None:
        self.setInteractionRelevanceAdvisorySwitch(True)

    def disable_interaction_relevance_advisory_switch(self) -> None:
        self.setInteractionRelevanceAdvisorySwitch(False)

    def getConveyRegionDesignatorSetsSwitch(self) -> bool:  # noqa: N802
        self._record("getConveyRegionDesignatorSetsSwitch")
        return get_switch(self, "getConveyRegionDesignatorSetsSwitch", "convey_region_designator_sets")

    def setConveyRegionDesignatorSetsSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setConveyRegionDesignatorSetsSwitch", value)
        set_switch(self, "setConveyRegionDesignatorSetsSwitch", "convey_region_designator_sets", value)

    def getAutomaticResignDirective(self) -> ResignAction:  # noqa: N802
        self._record("getAutomaticResignDirective")
        self._require_joined("getAutomaticResignDirective")
        return get_automatic_resign_directive(self)

    def setAutomaticResignDirective(self, value: ResignAction) -> None:  # noqa: N802
        self._record("setAutomaticResignDirective", value)
        self._require_joined("setAutomaticResignDirective")
        set_automatic_resign_directive(self, value)

    def getServiceReportingSwitch(self) -> bool:  # noqa: N802
        self._record("getServiceReportingSwitch")
        return get_switch(self, "getServiceReportingSwitch", "service_reporting")

    def setServiceReportingSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setServiceReportingSwitch", value)
        set_switch(self, "setServiceReportingSwitch", "service_reporting", value)

    def getExceptionReportingSwitch(self) -> bool:  # noqa: N802
        self._record("getExceptionReportingSwitch")
        return get_switch(self, "getExceptionReportingSwitch", "exception_reporting")

    def setExceptionReportingSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setExceptionReportingSwitch", value)
        set_switch(self, "setExceptionReportingSwitch", "exception_reporting", value)

    def getSendServiceReportsToFileSwitch(self) -> bool:  # noqa: N802
        self._record("getSendServiceReportsToFileSwitch")
        return get_switch(self, "getSendServiceReportsToFileSwitch", "send_service_reports_to_file")

    def setSendServiceReportsToFileSwitch(self, value: bool) -> None:  # noqa: N802
        self._record("setSendServiceReportsToFileSwitch", value)
        set_switch(self, "setSendServiceReportsToFileSwitch", "send_service_reports_to_file", value)

    def getAutoProvideSwitch(self) -> bool:  # noqa: N802
        self._record("getAutoProvideSwitch")
        return get_switch(self, "getAutoProvideSwitch", "auto_provide")

    def getDelaySubscriptionEvaluationSwitch(self) -> bool:  # noqa: N802
        self._record("getDelaySubscriptionEvaluationSwitch")
        return get_switch(self, "getDelaySubscriptionEvaluationSwitch", "delay_subscription_evaluation")

    def getAdvisoriesUseKnownClassSwitch(self) -> bool:  # noqa: N802
        self._record("getAdvisoriesUseKnownClassSwitch")
        return get_switch(self, "getAdvisoriesUseKnownClassSwitch", "advisories_use_known_class")

    def getAllowRelaxedDDMSwitch(self) -> bool:  # noqa: N802
        self._record("getAllowRelaxedDDMSwitch")
        return get_switch(self, "getAllowRelaxedDDMSwitch", "allow_relaxed_ddm")

    def getNonRegulatedGrantSwitch(self) -> bool:  # noqa: N802
        self._record("getNonRegulatedGrantSwitch")
        return get_switch(self, "getNonRegulatedGrantSwitch", "non_regulated_grant")

    def getHLAversion(self) -> str:  # noqa: N802
        self._record("getHLAversion")
        return "IEEE 1516.1-2025"

    @staticmethod
    def _invalid_federate_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidFederateHandle

        return InvalidFederateHandle

    @staticmethod
    def _invalid_object_class_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidObjectClassHandle

        return InvalidObjectClassHandle

    @staticmethod
    def _invalid_interaction_class_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidInteractionClassHandle

        return InvalidInteractionClassHandle

    @staticmethod
    def _invalid_object_instance_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidObjectInstanceHandle

        return InvalidObjectInstanceHandle

    @staticmethod
    def _invalid_attribute_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidAttributeHandle

        return InvalidAttributeHandle

    @staticmethod
    def _invalid_parameter_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidParameterHandle

        return InvalidParameterHandle

    @staticmethod
    def _invalid_dimension_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidDimensionHandle

        return InvalidDimensionHandle

    @staticmethod
    def _invalid_message_retraction_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidMessageRetractionHandle

        return InvalidMessageRetractionHandle

    @staticmethod
    def _invalid_region_handle_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidRegion

        return InvalidRegion

    @staticmethod
    def _invalid_update_rate_designator_type() -> type[Exception]:
        from hla.rti1516_2025.exceptions import InvalidUpdateRateDesignator

        return InvalidUpdateRateDesignator
