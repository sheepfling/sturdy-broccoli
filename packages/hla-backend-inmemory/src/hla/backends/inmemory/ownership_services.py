"""Ownership-management service entrypoints for the in-memory Python RTI backend."""
from __future__ import annotations

from typing import Iterable

from hla.rti1516e import handles as hla_handles
from hla.rti1516e.exceptions import (
    AttributeAcquisitionWasNotRequested,
    AttributeAlreadyBeingAcquired,
    AttributeAlreadyBeingDivested,
    AttributeAlreadyOwned,
    AttributeDivestitureWasNotRequested,
    AttributeNotPublished,
    FederateOwnsAttributes,
    ObjectClassNotPublished,
    NoAcquisitionPending,
)
from hla.rti1516e.handles import AttributeHandle, ObjectInstanceHandle

from .ownership_core import PythonRTIOwnershipCoreMixin
from .state import RTI_FEDERATE_HANDLE


class PythonRTIOwnershipServicesMixin(PythonRTIOwnershipCoreMixin):
    """Public ownership-management services."""

    def _svc_unconditionalAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        for attr in self._owned_attributes_or_raise(instance, theAttributes):
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_has_candidates(instance, attr):
                new_owner = self._pop_first_candidate(instance, attr)
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    new_owner,
                    old_owner=old_owner,
                    acquisition_tag=b"",
                    notify_previous_owner=False,
                )
            else:
                instance.attribute_owners[attr] = None
                instance.attribute_divesting.discard(attr)

    def _svc_negotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
        userSuppliedTag: bytes,
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = self._owned_attributes_or_raise(instance, theAttributes)
        for attr in attrs:
            if self._attribute_is_divesting(instance, attr):
                raise AttributeAlreadyBeingDivested(repr(attr))

        for attr in attrs:
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_has_candidates(instance, attr):
                new_owner = self._pop_first_candidate(instance, attr)
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    new_owner,
                    old_owner=old_owner,
                    acquisition_tag=bytes(userSuppliedTag),
                    notify_previous_owner=True,
                )
                continue

            instance.attribute_divesting.add(attr)
            for federate in list(federation.federates.values()):
                if federate is not self.state:
                    self._deliver(
                        federate,
                        "requestAttributeOwnershipAssumption",
                        theObject,
                        hla_handles.AttributeHandleSet({attr}),
                        bytes(userSuppliedTag),
                    )

    def _svc_confirmDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        confirmedAttributes: Iterable[AttributeHandle],
        userSuppliedTag: bytes,
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        for attr in self._owned_attributes_or_raise(instance, confirmedAttributes):
            if not self._attribute_is_divesting(instance, attr):
                raise AttributeDivestitureWasNotRequested(repr(attr))
            if not self._attribute_has_candidates(instance, attr):
                raise NoAcquisitionPending(repr(attr))
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            new_owner = self._pop_first_candidate(instance, attr)
            self._complete_immediate_attribute_transfer(
                federation,
                instance,
                attr,
                new_owner,
                old_owner=old_owner,
                acquisition_tag=bytes(userSuppliedTag),
                notify_previous_owner=False,
            )

    def _svc_attributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: Iterable[AttributeHandle],
        userSuppliedTag: bytes,
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = set(desiredAttributes)
        assert self.state.handle is not None
        if instance.class_handle not in self.state.published_objects:
            raise ObjectClassNotPublished(repr(instance.class_handle))
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner == self.state.handle:
                raise FederateOwnsAttributes(repr(attr))
            if self.state.handle in instance.attribute_candidates.get(attr, set()):
                raise AttributeAlreadyBeingAcquired(repr(attr))
            if self.config.strict_object_publication:
                published = self.state.published_objects.get(instance.class_handle, set())
                if attr not in published:
                    raise AttributeNotPublished(repr(attr))

        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_is_available_for_immediate_acquisition(instance, attr):
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    self.state.handle,
                    old_owner=owner,
                    acquisition_tag=bytes(userSuppliedTag),
                    notify_previous_owner=self._attribute_is_divesting(instance, attr),
                )
            else:
                candidates = self._attribute_candidates(instance, attr)
                candidates.discard(self.state.handle)
                candidates.add(self.state.handle)
                if owner is not None:
                    self._deliver_to_federate_handle(
                        federation,
                        owner,
                        "requestAttributeOwnershipRelease",
                        theObject,
                        hla_handles.AttributeHandleSet({attr}),
                        bytes(userSuppliedTag),
                    )

    def _svc_attributeOwnershipAcquisitionIfAvailable(
        self,
        theObject: ObjectInstanceHandle,
        desiredAttributes: Iterable[AttributeHandle],
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = set(desiredAttributes)
        unavailable: set[AttributeHandle] = set()
        assert self.state.handle is not None
        if instance.class_handle not in self.state.published_objects:
            raise ObjectClassNotPublished(repr(instance.class_handle))
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner == self.state.handle:
                raise FederateOwnsAttributes(repr(attr))
            if self.state.handle in instance.attribute_candidates.get(attr, set()):
                raise AttributeAlreadyBeingAcquired(repr(attr))
            if self.config.strict_object_publication:
                published = self.state.published_objects.get(instance.class_handle, set())
                if attr not in published:
                    raise AttributeNotPublished(repr(attr))

        for attr in attrs:
            owner = instance.attribute_owners.get(attr, instance.owner)
            if self._attribute_is_available_for_immediate_acquisition(instance, attr):
                self._complete_immediate_attribute_transfer(
                    federation,
                    instance,
                    attr,
                    self.state.handle,
                    old_owner=owner,
                    acquisition_tag=b"",
                    notify_previous_owner=self._attribute_is_divesting(instance, attr),
                )
            else:
                self._attribute_candidates(instance, attr).add(self.state.handle)
                unavailable.add(attr)
        if unavailable:
            self._deliver(
                self.state,
                "attributeOwnershipUnavailable",
                theObject,
                hla_handles.AttributeHandleSet(unavailable),
            )

    def _svc_attributeOwnershipReleaseDenied(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        for attr in self._owned_attributes_or_raise(instance, theAttributes):
            instance.attribute_candidates.pop(attr, None)

    def _svc_attributeOwnershipDivestitureIfWanted(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> hla_handles.AttributeHandleSet:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        divested = self._owned_attributes_or_raise(instance, theAttributes)
        for attr in divested:
            if not self._attribute_has_candidates(instance, attr):
                raise NoAcquisitionPending(repr(attr))
        for attr in divested:
            old_owner = instance.attribute_owners.get(attr, instance.owner)
            new_owner = self._pop_first_candidate(instance, attr)
            self._complete_immediate_attribute_transfer(
                federation,
                instance,
                attr,
                new_owner,
                old_owner=old_owner,
                acquisition_tag=b"",
                notify_previous_owner=False,
            )
        return hla_handles.AttributeHandleSet(divested)

    def _svc_cancelNegotiatedAttributeOwnershipDivestiture(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        for attr in self._owned_attributes_or_raise(instance, theAttributes):
            if not self._attribute_is_divesting(instance, attr):
                raise AttributeDivestitureWasNotRequested(repr(attr))
            instance.attribute_divesting.discard(attr)

    def _svc_cancelAttributeOwnershipAcquisition(
        self,
        theObject: ObjectInstanceHandle,
        theAttributes: Iterable[AttributeHandle],
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        attrs = set(theAttributes)
        assert self.state.handle is not None
        for attr in attrs:
            self.engine.attribute_name(instance.class_handle, attr)
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner == self.state.handle:
                raise AttributeAlreadyOwned(repr(attr))
            if self.state.handle not in instance.attribute_candidates.get(attr, set()):
                raise AttributeAcquisitionWasNotRequested(repr(attr))
        for attr in attrs:
            candidates = instance.attribute_candidates.get(attr)
            if candidates is not None:
                candidates.discard(self.state.handle)
                if not candidates:
                    instance.attribute_candidates.pop(attr, None)
        self._deliver(
            self.state,
            "confirmAttributeOwnershipAcquisitionCancellation",
            theObject,
            hla_handles.AttributeHandleSet(attrs),
        )

    def _svc_queryAttributeOwnership(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> None:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.attribute_name(instance.class_handle, theAttribute)
        owner = instance.attribute_owners.get(theAttribute, instance.owner)
        if owner is None:
            self._deliver(self.state, "attributeIsNotOwned", theObject, theAttribute)
        elif owner == RTI_FEDERATE_HANDLE:
            self._deliver(self.state, "attributeIsOwnedByRTI", theObject, theAttribute)
        else:
            self._deliver(
                self.state,
                "informAttributeOwnership",
                theObject,
                theAttribute,
                owner,
            )

    def _svc_isAttributeOwnedByFederate(
        self,
        theObject: ObjectInstanceHandle,
        theAttribute: AttributeHandle,
    ) -> bool:
        federation, instance = self._find_object(theObject)
        self._ensure_no_save_or_restore_in_progress(federation)
        self.engine.attribute_name(instance.class_handle, theAttribute)
        return instance.attribute_owners.get(theAttribute, instance.owner) == self.state.handle
