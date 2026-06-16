"""Factory and decode support helpers for the in-memory Python RTI backend."""

from __future__ import annotations

from hla.rti1516e import handles as hla_handles
from hla.rti1516e.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    MessageRetractionHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
)

from .support_control import PythonRTISupportControlMixin


class PythonRTISupportFactoriesMixin(PythonRTISupportControlMixin):
    """Handle factories and decode helpers."""

    def _svc_getAttributeHandleFactory(self) -> hla_handles.AttributeHandleFactory:
        self._require_joined()
        return hla_handles.AttributeHandleFactory()

    def _svc_getAttributeHandleSetFactory(self) -> hla_handles.AttributeHandleSetFactory:
        self._require_joined()
        return hla_handles.AttributeHandleSetFactory()

    def _svc_getAttributeHandleValueMapFactory(self) -> hla_handles.AttributeHandleValueMapFactory:
        self._require_joined()
        return hla_handles.AttributeHandleValueMapFactory()

    def _svc_getAttributeSetRegionSetPairListFactory(
        self,
    ) -> hla_handles.AttributeSetRegionSetPairListFactory:
        self._require_joined()
        return hla_handles.AttributeSetRegionSetPairListFactory()

    def _svc_getDimensionHandleFactory(self) -> hla_handles.DimensionHandleFactory:
        self._require_joined()
        return hla_handles.DimensionHandleFactory()

    def _svc_getDimensionHandleSetFactory(self) -> hla_handles.DimensionHandleSetFactory:
        self._require_joined()
        return hla_handles.DimensionHandleSetFactory()

    def _svc_getFederateHandleFactory(self) -> hla_handles.FederateHandleFactory:
        self._require_joined()
        return hla_handles.FederateHandleFactory()

    def _svc_getFederateHandleSetFactory(self) -> hla_handles.FederateHandleSetFactory:
        self._require_joined()
        return hla_handles.FederateHandleSetFactory()

    def _svc_getInteractionClassHandleFactory(self) -> hla_handles.InteractionClassHandleFactory:
        self._require_joined()
        return hla_handles.InteractionClassHandleFactory()

    def _svc_getObjectClassHandleFactory(self) -> hla_handles.ObjectClassHandleFactory:
        self._require_joined()
        return hla_handles.ObjectClassHandleFactory()

    def _svc_getObjectInstanceHandleFactory(self) -> hla_handles.ObjectInstanceHandleFactory:
        self._require_joined()
        return hla_handles.ObjectInstanceHandleFactory()

    def _svc_getParameterHandleFactory(self) -> hla_handles.ParameterHandleFactory:
        self._require_joined()
        return hla_handles.ParameterHandleFactory()

    def _svc_getParameterHandleValueMapFactory(self) -> hla_handles.ParameterHandleValueMapFactory:
        self._require_joined()
        return hla_handles.ParameterHandleValueMapFactory()

    def _svc_getRegionHandleSetFactory(self) -> hla_handles.RegionHandleSetFactory:
        self._require_joined()
        return hla_handles.RegionHandleSetFactory()

    def _svc_getTransportationTypeHandleFactory(
        self,
    ) -> hla_handles.TransportationTypeHandleFactory:
        self._require_joined()
        return hla_handles.TransportationTypeHandleFactory()

    def _svc_decodeMessageRetractionHandle(self, buffer: bytes) -> MessageRetractionHandle:
        return MessageRetractionHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeFederateHandle(self, buffer: bytes) -> FederateHandle:
        return FederateHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeObjectClassHandle(self, buffer: bytes) -> ObjectClassHandle:
        return ObjectClassHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeAttributeHandle(self, buffer: bytes) -> AttributeHandle:
        return AttributeHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeObjectInstanceHandle(self, buffer: bytes) -> ObjectInstanceHandle:
        return ObjectInstanceHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeInteractionClassHandle(self, buffer: bytes) -> InteractionClassHandle:
        return InteractionClassHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeParameterHandle(self, buffer: bytes) -> ParameterHandle:
        return ParameterHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeDimensionHandle(self, buffer: bytes) -> DimensionHandle:
        return DimensionHandle.decode(buffer)  # type: ignore[return-value]

    def _svc_decodeRegionHandle(self, buffer: bytes) -> RegionHandle:
        return RegionHandle.decode(buffer)  # type: ignore[return-value]
