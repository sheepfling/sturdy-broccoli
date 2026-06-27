"""Core ownership-transfer helpers for the in-memory Python RTI backend."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol

from hla.rti1516e import handles as hla_handles
from hla.rti1516e.exceptions import (
    AttributeNotDefined,
    AttributeNotOwned,
    NoAcquisitionPending,
)
from hla.rti1516e.handles import AttributeHandle, FederateHandle

from .state import FederationState, ObjectInstance

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState


class _OwnershipCoreContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: "FederateState"

    def _deliver(self, target: "FederateState", method_name: str, *args: Any) -> None: ...


if TYPE_CHECKING:
    class _OwnershipCoreMixinBase(_OwnershipCoreContext):
        pass
else:
    class _OwnershipCoreMixinBase:
        pass


class PythonRTIOwnershipCoreMixin(_OwnershipCoreMixinBase):
    """Ownership validation, candidate tracking, and transfer helpers."""

    def _owned_attributes_or_raise(
        self,
        instance: ObjectInstance,
        attributes: Iterable[AttributeHandle],
    ) -> set[AttributeHandle]:
        attrs = set(attributes)
        for attr in attrs:
            try:
                self.engine.attribute_name(instance.class_handle, attr)
            except AttributeNotDefined:
                if attr not in instance.attribute_owners and attr not in instance.attributes:
                    raise
            owner = instance.attribute_owners.get(attr, instance.owner)
            if owner != self.state.handle:
                raise AttributeNotOwned(repr(attr))
        return attrs

    @staticmethod
    def _attribute_candidates(
        instance: ObjectInstance,
        attr: AttributeHandle,
    ) -> set[FederateHandle]:
        return instance.attribute_candidates.setdefault(attr, set())

    @staticmethod
    def _attribute_has_candidates(instance: ObjectInstance, attr: AttributeHandle) -> bool:
        return bool(instance.attribute_candidates.get(attr))

    @staticmethod
    def _attribute_is_divesting(instance: ObjectInstance, attr: AttributeHandle) -> bool:
        return attr in instance.attribute_divesting

    @staticmethod
    def _attribute_is_available_for_immediate_acquisition(
        instance: ObjectInstance,
        attr: AttributeHandle,
    ) -> bool:
        owner = instance.attribute_owners.get(attr, instance.owner)
        return owner is None

    @staticmethod
    def _pop_first_candidate(
        instance: ObjectInstance,
        attr: AttributeHandle,
    ) -> FederateHandle:
        candidates = instance.attribute_candidates.get(attr, set())
        if not candidates:
            raise NoAcquisitionPending(repr(attr))
        candidate = min(candidates, key=lambda handle: int(handle.value))
        candidates.remove(candidate)
        if not candidates:
            instance.attribute_candidates.pop(attr, None)
        return candidate

    def _deliver_to_federate_handle(
        self,
        federation: FederationState,
        federate_handle: FederateHandle,
        method_name: str,
        *args: Any,
    ) -> None:
        self._deliver(federation.federates[federate_handle], method_name, *args)

    def _complete_immediate_attribute_transfer(
        self,
        federation: FederationState,
        instance: ObjectInstance,
        attr: AttributeHandle,
        new_owner: FederateHandle,
        *,
        old_owner: FederateHandle | None,
        acquisition_tag: bytes,
        notify_previous_owner: bool,
    ) -> None:
        instance.attribute_owners[attr] = new_owner
        instance.attribute_divesting.discard(attr)
        candidates = instance.attribute_candidates.get(attr)
        if candidates is not None:
            candidates.discard(new_owner)
            if not candidates:
                instance.attribute_candidates.pop(attr, None)
        self._deliver_to_federate_handle(
            federation,
            new_owner,
            "attributeOwnershipAcquisitionNotification",
            instance.handle,
            hla_handles.AttributeHandleSet({attr}),
            bytes(acquisition_tag),
        )
        if notify_previous_owner and old_owner is not None:
            self._deliver_to_federate_handle(
                federation,
                old_owner,
                "requestDivestitureConfirmation",
                instance.handle,
                hla_handles.AttributeHandleSet({attr}),
                bytes(acquisition_tag),
            )
