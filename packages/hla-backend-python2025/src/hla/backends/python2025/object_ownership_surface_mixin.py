"""Object management, transportation, and ownership surface wrappers."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.handles import AttributeHandle

from .interaction_runtime import (
    query_interaction_transportation_type,
    request_interaction_transportation_type_change,
    send_directed_interaction,
    send_interaction,
    send_interaction_with_regions,
)
from .object_instance_runtime import (
    delete_object_instance,
    local_delete_object_instance,
    register_object_instance,
    request_attribute_value_update,
    update_attribute_values,
)
from .object_region_runtime import (
    query_attribute_transportation_type,
    request_attribute_transportation_type_change,
)
from .ownership_runtime import (
    attribute_ownership_acquisition,
    attribute_ownership_acquisition_if_available,
    attribute_ownership_divestiture_if_wanted,
    attribute_ownership_release_denied,
    cancel_attribute_ownership_acquisition,
    cancel_negotiated_attribute_ownership_divestiture,
    confirm_divestiture,
    is_attribute_owned_by_federate,
    negotiated_attribute_ownership_divestiture,
    query_attribute_ownership,
    unconditional_attribute_ownership_divestiture,
)


class ObjectOwnershipSurfaceMixin:
    """Move mechanical object and ownership service wrappers out of the main class body."""

    def registerObjectInstance(  # noqa: N802
        self,
        objectClass: Any,
        objectInstanceName: str | None = None,
    ):
        self._record("registerObjectInstance", objectClass, objectInstanceName)
        self._require_joined("registerObjectInstance")
        return register_object_instance(self, objectClass, objectInstanceName)

    def updateAttributeValues(  # noqa: N802
        self,
        objectInstance: Any,
        attributeValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("updateAttributeValues", objectInstance, attributeValues, userSuppliedTag, time)
        self._require_joined("updateAttributeValues")
        return update_attribute_values(self, objectInstance, attributeValues, userSuppliedTag, time)

    def sendInteraction(  # noqa: N802
        self,
        interactionClass: Any,
        parameterValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendInteraction", interactionClass, parameterValues, userSuppliedTag, time)
        self._require_joined("sendInteraction")
        return send_interaction(self, interactionClass, parameterValues, userSuppliedTag, time)

    def sendInteractionWithRegions(  # noqa: N802
        self,
        interactionClass: Any,
        parameterValues: Mapping[Any, bytes],
        regions: Any,
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendInteractionWithRegions", interactionClass, parameterValues, regions, userSuppliedTag, time)
        self._require_joined("sendInteractionWithRegions")
        return send_interaction_with_regions(self, interactionClass, parameterValues, regions, userSuppliedTag, time)

    def sendDirectedInteraction(  # noqa: N802
        self,
        interactionClass: Any,
        objectInstance: Any,
        parameterValues: Mapping[Any, bytes],
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("sendDirectedInteraction", interactionClass, objectInstance, parameterValues, userSuppliedTag, time)
        self._require_joined("sendDirectedInteraction")
        return send_directed_interaction(self, interactionClass, objectInstance, parameterValues, userSuppliedTag, time)

    def deleteObjectInstance(  # noqa: N802
        self,
        objectInstance: Any,
        userSuppliedTag: bytes,
        time: Any | None = None,
    ) -> Any | None:
        self._record("deleteObjectInstance", objectInstance, userSuppliedTag, time)
        self._require_joined("deleteObjectInstance")
        return delete_object_instance(self, objectInstance, userSuppliedTag, time)

    def localDeleteObjectInstance(self, objectInstance: Any) -> None:  # noqa: N802
        self._record("localDeleteObjectInstance", objectInstance)
        self._require_joined("localDeleteObjectInstance")
        local_delete_object_instance(self, objectInstance)

    def requestAttributeValueUpdate(self, objectClassOrInstance: Any, attributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self._record("requestAttributeValueUpdate", objectClassOrInstance, attributes, userSuppliedTag)
        self._require_joined("requestAttributeValueUpdate")
        request_attribute_value_update(self, objectClassOrInstance, attributes, userSuppliedTag)

    def requestAttributeTransportationTypeChange(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        transportationType: Any,
    ) -> None:
        self._record("requestAttributeTransportationTypeChange", objectInstance, attributes, transportationType)
        self._require_joined("requestAttributeTransportationTypeChange")
        self._require_no_save_or_restore("requestAttributeTransportationTypeChange")
        request_attribute_transportation_type_change(self, objectInstance, attributes, transportationType)

    def queryAttributeTransportationType(self, objectInstance: Any, attribute: Any) -> None:  # noqa: N802
        self._record("queryAttributeTransportationType", objectInstance, attribute)
        self._require_joined("queryAttributeTransportationType")
        self._require_no_save_or_restore("queryAttributeTransportationType")
        query_attribute_transportation_type(self, objectInstance, attribute)

    def requestInteractionTransportationTypeChange(self, interactionClass: Any, transportationType: Any) -> None:  # noqa: N802
        self._record("requestInteractionTransportationTypeChange", interactionClass, transportationType)
        self._require_joined("requestInteractionTransportationTypeChange")
        self._require_no_save_or_restore("requestInteractionTransportationTypeChange")
        request_interaction_transportation_type_change(self, interactionClass, transportationType)

    def queryInteractionTransportationType(self, federate: Any, interactionClass: Any) -> None:  # noqa: N802
        self._record("queryInteractionTransportationType", federate, interactionClass)
        self._require_joined("queryInteractionTransportationType")
        self._require_no_save_or_restore("queryInteractionTransportationType")
        query_interaction_transportation_type(self, federate, interactionClass)

    def query_interaction_transportation_type(self, interaction_class: Any, federate: Any | None = None) -> None:
        if federate is None:
            federate = self._current_federate_handle()
        self.queryInteractionTransportationType(federate, interaction_class)

    def unconditionalAttributeOwnershipDivestiture(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("unconditionalAttributeOwnershipDivestiture", objectInstance, attributes, userSuppliedTag)
        self._require_joined("unconditionalAttributeOwnershipDivestiture")
        unconditional_attribute_ownership_divestiture(self, objectInstance, attributes, userSuppliedTag)

    def unconditional_attribute_ownership_divestiture(
        self,
        object_instance: Any,
        attributes: Any,
        user_supplied_tag: bytes = b"",
    ) -> None:
        self.unconditionalAttributeOwnershipDivestiture(object_instance, attributes, user_supplied_tag)

    def negotiatedAttributeOwnershipDivestiture(  # noqa: N802
        self,
        objectInstance: Any,
        attributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("negotiatedAttributeOwnershipDivestiture", objectInstance, attributes, userSuppliedTag)
        self._require_joined("negotiatedAttributeOwnershipDivestiture")
        negotiated_attribute_ownership_divestiture(self, objectInstance, attributes, userSuppliedTag)

    def negotiated_attribute_ownership_divestiture(
        self,
        object_instance: Any,
        attributes: Any,
        user_supplied_tag: bytes = b"",
    ) -> None:
        self.negotiatedAttributeOwnershipDivestiture(object_instance, attributes, user_supplied_tag)

    def confirmDivestiture(self, objectInstance: Any, confirmedAttributes: Any, userSuppliedTag: bytes) -> None:  # noqa: N802
        self._record("confirmDivestiture", objectInstance, confirmedAttributes, userSuppliedTag)
        self._require_joined("confirmDivestiture")
        confirm_divestiture(self, objectInstance, confirmedAttributes, userSuppliedTag)

    def confirm_divestiture(
        self,
        object_instance: Any,
        confirmed_attributes: Any,
        user_supplied_tag: bytes = b"",
    ) -> None:
        self.confirmDivestiture(object_instance, confirmed_attributes, user_supplied_tag)

    def attributeOwnershipAcquisition(  # noqa: N802
        self,
        objectInstance: Any,
        desiredAttributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("attributeOwnershipAcquisition", objectInstance, desiredAttributes, userSuppliedTag)
        self._require_joined("attributeOwnershipAcquisition")
        attribute_ownership_acquisition(self, objectInstance, desiredAttributes, userSuppliedTag)

    def attribute_ownership_acquisition(
        self,
        object_instance: Any,
        desired_attributes: Any,
        user_supplied_tag: bytes = b"",
    ) -> None:
        self.attributeOwnershipAcquisition(object_instance, desired_attributes, user_supplied_tag)

    def attributeOwnershipAcquisitionIfAvailable(  # noqa: N802
        self,
        objectInstance: Any,
        desiredAttributes: Any,
        userSuppliedTag: bytes,
    ) -> None:
        self._record("attributeOwnershipAcquisitionIfAvailable", objectInstance, desiredAttributes, userSuppliedTag)
        self._require_joined("attributeOwnershipAcquisitionIfAvailable")
        attribute_ownership_acquisition_if_available(self, objectInstance, desiredAttributes, userSuppliedTag)

    def attribute_ownership_acquisition_if_available(
        self,
        object_instance: Any,
        desired_attributes: Any,
        user_supplied_tag: bytes = b"",
    ) -> None:
        self.attributeOwnershipAcquisitionIfAvailable(object_instance, desired_attributes, user_supplied_tag)

    def attributeOwnershipReleaseDenied(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("attributeOwnershipReleaseDenied", objectInstance, attributes)
        self._require_joined("attributeOwnershipReleaseDenied")
        attribute_ownership_release_denied(self, objectInstance, attributes)

    def attribute_ownership_release_denied(self, object_instance: Any, attributes: Any) -> None:
        self.attributeOwnershipReleaseDenied(object_instance, attributes)

    def attributeOwnershipDivestitureIfWanted(self, objectInstance: Any, attributes: Any) -> set[AttributeHandle]:  # noqa: N802
        self._record("attributeOwnershipDivestitureIfWanted", objectInstance, attributes)
        self._require_joined("attributeOwnershipDivestitureIfWanted")
        return attribute_ownership_divestiture_if_wanted(self, objectInstance, attributes)

    def attribute_ownership_divestiture_if_wanted(self, object_instance: Any, attributes: Any) -> set[AttributeHandle]:
        return self.attributeOwnershipDivestitureIfWanted(object_instance, attributes)

    def cancelNegotiatedAttributeOwnershipDivestiture(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("cancelNegotiatedAttributeOwnershipDivestiture", objectInstance, attributes)
        self._require_joined("cancelNegotiatedAttributeOwnershipDivestiture")
        cancel_negotiated_attribute_ownership_divestiture(self, objectInstance, attributes)

    def cancel_negotiated_attribute_ownership_divestiture(self, object_instance: Any, attributes: Any) -> None:
        self.cancelNegotiatedAttributeOwnershipDivestiture(object_instance, attributes)

    def cancelAttributeOwnershipAcquisition(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("cancelAttributeOwnershipAcquisition", objectInstance, attributes)
        self._require_joined("cancelAttributeOwnershipAcquisition")
        cancel_attribute_ownership_acquisition(self, objectInstance, attributes)

    def cancel_attribute_ownership_acquisition(self, object_instance: Any, attributes: Any) -> None:
        self.cancelAttributeOwnershipAcquisition(object_instance, attributes)

    def queryAttributeOwnership(self, objectInstance: Any, attributes: Any) -> None:  # noqa: N802
        self._record("queryAttributeOwnership", objectInstance, attributes)
        self._require_joined("queryAttributeOwnership")
        query_attribute_ownership(self, objectInstance, attributes)

    def query_attribute_ownership(self, object_instance: Any, attributes: Any) -> None:
        normalized_attributes = attributes
        try:
            iter(attributes)
        except TypeError:
            normalized_attributes = {attributes}
        self.queryAttributeOwnership(object_instance, normalized_attributes)

    def isAttributeOwnedByFederate(self, objectInstance: Any, attribute: Any) -> bool:  # noqa: N802
        self._record("isAttributeOwnedByFederate", objectInstance, attribute)
        self._require_joined("isAttributeOwnedByFederate")
        return is_attribute_owned_by_federate(self, objectInstance, attribute)

    def is_attribute_owned_by_federate(self, object_instance: Any, attribute: Any) -> bool:
        return self.isAttributeOwnedByFederate(object_instance, attribute)
