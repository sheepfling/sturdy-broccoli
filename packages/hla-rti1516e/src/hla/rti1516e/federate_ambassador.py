from __future__ import annotations

import re
from typing import Protocol


def lower_camel_to_snake(name: str) -> str:
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()

class FederateAmbassador(Protocol):
    """Runtime protocol surface. Strict overloads live in the .pyi stub and SOURCE_TRACE.md."""

    def connectionLost(self, *args, **kwargs) -> None:
        ...

    def reportFederationExecutions(self, *args, **kwargs) -> None:
        ...

    def synchronizationPointRegistrationSucceeded(self, *args, **kwargs) -> None:
        ...

    def synchronizationPointRegistrationFailed(self, *args, **kwargs) -> None:
        ...

    def announceSynchronizationPoint(self, *args, **kwargs) -> None:
        ...

    def federationSynchronized(self, *args, **kwargs) -> None:
        ...

    def initiateFederateSave(self, *args, **kwargs) -> None:
        ...

    def federationSaved(self, *args, **kwargs) -> None:
        ...

    def federationNotSaved(self, *args, **kwargs) -> None:
        ...

    def federationSaveStatusResponse(self, *args, **kwargs) -> None:
        ...

    def requestFederationRestoreSucceeded(self, *args, **kwargs) -> None:
        ...

    def requestFederationRestoreFailed(self, *args, **kwargs) -> None:
        ...

    def federationRestoreBegun(self, *args, **kwargs) -> None:
        ...

    def initiateFederateRestore(self, *args, **kwargs) -> None:
        ...

    def federationRestored(self, *args, **kwargs) -> None:
        ...

    def federationNotRestored(self, *args, **kwargs) -> None:
        ...

    def federationRestoreStatusResponse(self, *args, **kwargs) -> None:
        ...

    def startRegistrationForObjectClass(self, *args, **kwargs) -> None:
        ...

    def stopRegistrationForObjectClass(self, *args, **kwargs) -> None:
        ...

    def turnInteractionsOn(self, *args, **kwargs) -> None:
        ...

    def turnInteractionsOff(self, *args, **kwargs) -> None:
        ...

    def objectInstanceNameReservationSucceeded(self, *args, **kwargs) -> None:
        ...

    def objectInstanceNameReservationFailed(self, *args, **kwargs) -> None:
        ...

    def multipleObjectInstanceNameReservationSucceeded(self, *args, **kwargs) -> None:
        ...

    def multipleObjectInstanceNameReservationFailed(self, *args, **kwargs) -> None:
        ...

    def discoverObjectInstance(self, *args, **kwargs) -> None:
        ...

    def reflectAttributeValues(self, *args, **kwargs) -> None:
        ...

    def receiveInteraction(self, *args, **kwargs) -> None:
        ...

    def removeObjectInstance(self, *args, **kwargs) -> None:
        ...

    def attributesInScope(self, *args, **kwargs) -> None:
        ...

    def attributesOutOfScope(self, *args, **kwargs) -> None:
        ...

    def provideAttributeValueUpdate(self, *args, **kwargs) -> None:
        ...

    def turnUpdatesOnForObjectInstance(self, *args, **kwargs) -> None:
        ...

    def turnUpdatesOffForObjectInstance(self, *args, **kwargs) -> None:
        ...

    def confirmAttributeTransportationTypeChange(self, *args, **kwargs) -> None:
        ...

    def reportAttributeTransportationType(self, *args, **kwargs) -> None:
        ...

    def confirmInteractionTransportationTypeChange(self, *args, **kwargs) -> None:
        ...

    def reportInteractionTransportationType(self, *args, **kwargs) -> None:
        ...

    def requestAttributeOwnershipAssumption(self, *args, **kwargs) -> None:
        ...

    def requestDivestitureConfirmation(self, *args, **kwargs) -> None:
        ...

    def attributeOwnershipAcquisitionNotification(self, *args, **kwargs) -> None:
        ...

    def attributeOwnershipUnavailable(self, *args, **kwargs) -> None:
        ...

    def requestAttributeOwnershipRelease(self, *args, **kwargs) -> None:
        ...

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args, **kwargs) -> None:
        ...

    def informAttributeOwnership(self, *args, **kwargs) -> None:
        ...

    def attributeIsNotOwned(self, *args, **kwargs) -> None:
        ...

    def attributeIsOwnedByRTI(self, *args, **kwargs) -> None:
        ...

    def timeRegulationEnabled(self, *args, **kwargs) -> None:
        ...

    def timeConstrainedEnabled(self, *args, **kwargs) -> None:
        ...

    def timeAdvanceGrant(self, *args, **kwargs) -> None:
        ...

    def requestRetraction(self, *args, **kwargs) -> None:
        ...

class UnimplementedFederateAmbassador(FederateAmbassador):

    def connectionLost(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def reportFederationExecutions(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def synchronizationPointRegistrationSucceeded(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def synchronizationPointRegistrationFailed(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def announceSynchronizationPoint(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationSynchronized(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def initiateFederateSave(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationSaved(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationNotSaved(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationSaveStatusResponse(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestFederationRestoreSucceeded(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestFederationRestoreFailed(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationRestoreBegun(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def initiateFederateRestore(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationRestored(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationNotRestored(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def federationRestoreStatusResponse(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def startRegistrationForObjectClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def stopRegistrationForObjectClass(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def turnInteractionsOn(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def turnInteractionsOff(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def objectInstanceNameReservationSucceeded(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def objectInstanceNameReservationFailed(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def multipleObjectInstanceNameReservationSucceeded(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def multipleObjectInstanceNameReservationFailed(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def discoverObjectInstance(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def reflectAttributeValues(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def receiveInteraction(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def removeObjectInstance(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributesInScope(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributesOutOfScope(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def provideAttributeValueUpdate(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def turnUpdatesOnForObjectInstance(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def turnUpdatesOffForObjectInstance(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def confirmAttributeTransportationTypeChange(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def reportAttributeTransportationType(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def confirmInteractionTransportationTypeChange(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def reportInteractionTransportationType(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestAttributeOwnershipAssumption(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestDivestitureConfirmation(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeOwnershipAcquisitionNotification(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeOwnershipUnavailable(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestAttributeOwnershipRelease(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def confirmAttributeOwnershipAcquisitionCancellation(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def informAttributeOwnership(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeIsNotOwned(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def attributeIsOwnedByRTI(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def timeRegulationEnabled(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def timeConstrainedEnabled(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def timeAdvanceGrant(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def requestRetraction(self, *args, **kwargs) -> None:
        raise NotImplementedError()


class NullFederateAmbassador(FederateAmbassador):
    """No-op federate callback sink matching the standard NullFederateAmbassador shape."""

    def __getattribute__(self, name: str):
        attr = super().__getattribute__(name)
        if name.startswith("__"):
            return attr

        owner_attr = getattr(type(self), name, None)
        base_attr = getattr(NullFederateAmbassador, name, None)
        if owner_attr is not None and owner_attr is not base_attr:
            return attr

        snake_name = lower_camel_to_snake(name)
        if snake_name != name:
            snake_attr = getattr(type(self), snake_name, None)
            base_snake_attr = getattr(NullFederateAmbassador, snake_name, None)
            if snake_attr is not None and snake_attr is not base_snake_attr:
                return object.__getattribute__(self, snake_name)

        return attr

    def __getattr__(self, name: str):
        def _callback(*args, **kwargs) -> None:
            return None

        return _callback
