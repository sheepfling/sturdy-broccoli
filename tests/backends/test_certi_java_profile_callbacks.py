from __future__ import annotations

import pytest

from hla2010_rti_certi.certi_java.adapter import _CERTIJavaFederateAdapter
from hla2010_rti_certi.certi_java.runtime import CERTIJavaValueConverter
from hla2010.enums import OrderType
from hla2010.handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)
from hla2010_rti_java_common.java_shim_backend import ShimJavaBridge
from hla2010_rti_java_common.java_shim_types import (
    JavaAttributeHandle,
    JavaByteArray,
    JavaInteractionClassHandle,
    JavaObjectClassHandle,
    JavaObjectInstanceHandle,
    JavaParameterHandle,
    JavaTransportationTypeHandle,
)
from hla2010.time import HLAfloat64Time


class _RecordingProxy:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def __getattr__(self, name: str):
        def _record(*args: object) -> None:
            self.calls.append((name, args))

        return _record


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_certi_java_federate_adapter_forwards_discover_and_reflect_callbacks(profile: str):
    proxy = _RecordingProxy()
    adapter = _CERTIJavaFederateAdapter(proxy)

    adapter.discoverObjectInstance(ObjectInstanceHandle(7), ObjectClassHandle(3), "DemoObject")
    adapter.reflectAttributeValues(
        ObjectInstanceHandle(7),
        {AttributeHandle(11): b"payload"},
        b"reflect-tag",
        OrderType.RECEIVE,
        TransportationTypeHandle(1),
    )
    adapter.receiveInteraction(
        InteractionClassHandle(13),
        {ParameterHandle(17): b"hello"},
        b"interaction-tag",
        OrderType.TIMESTAMP,
        TransportationTypeHandle(1),
        HLAfloat64Time(6.0),
        OrderType.RECEIVE,
    )
    adapter.timeAdvanceGrant(HLAfloat64Time(8.0))

    assert [name for name, _args in proxy.calls] == [
        "discoverObjectInstance",
        "reflectAttributeValues",
        "receiveInteraction",
        "timeAdvanceGrant",
    ]

    discover_args = proxy.calls[0][1]
    assert isinstance(discover_args[0], JavaObjectInstanceHandle)
    assert isinstance(discover_args[1], JavaObjectClassHandle)
    assert discover_args[2] == "DemoObject"

    reflect_args = proxy.calls[1][1]
    assert isinstance(reflect_args[0], JavaObjectInstanceHandle)
    reflect_handle, reflect_payload = next(iter(reflect_args[1].items()))
    assert isinstance(reflect_handle, JavaAttributeHandle)
    assert reflect_handle.value == 11
    assert isinstance(reflect_payload, JavaByteArray)
    assert reflect_payload.value == b"payload"
    assert isinstance(reflect_args[2], JavaByteArray)
    assert reflect_args[2].value == b"reflect-tag"
    assert str(reflect_args[3]) == "OrderType.RECEIVE"
    assert isinstance(reflect_args[4], JavaTransportationTypeHandle)

    interaction_args = proxy.calls[2][1]
    assert isinstance(interaction_args[0], JavaInteractionClassHandle)
    interaction_handle, interaction_payload = next(iter(interaction_args[1].items()))
    assert isinstance(interaction_handle, JavaParameterHandle)
    assert interaction_handle.value == 17
    assert isinstance(interaction_payload, JavaByteArray)
    assert interaction_payload.value == b"hello"
    assert isinstance(interaction_args[2], JavaByteArray)
    assert interaction_args[2].value == b"interaction-tag"
    assert str(interaction_args[3]) == "OrderType.TIMESTAMP"
    assert isinstance(interaction_args[4], JavaTransportationTypeHandle)
    assert interaction_args[5].value == 6.0
    assert str(interaction_args[6]) == "OrderType.RECEIVE"

    grant_args = proxy.calls[3][1]
    assert grant_args[0].value == 8.0


def test_certi_java_federate_adapter_forwards_remove_and_ownership_callbacks():
    proxy = _RecordingProxy()
    adapter = _CERTIJavaFederateAdapter(proxy)

    adapter.removeObjectInstance(
        ObjectInstanceHandle(21),
        b"remove-tag",
        OrderType.RECEIVE,
        object(),
    )
    adapter.requestAttributeOwnershipAssumption(
        ObjectInstanceHandle(21),
        {AttributeHandle(31), AttributeHandle(32)},
        b"offer-tag",
    )
    adapter.attributeOwnershipAcquisitionNotification(
        ObjectInstanceHandle(21),
        {AttributeHandle(31)},
        b"acquired-tag",
    )
    adapter.attributeOwnershipUnavailable(
        ObjectInstanceHandle(21),
        {AttributeHandle(32)},
    )
    adapter.requestAttributeOwnershipRelease(
        ObjectInstanceHandle(21),
        {AttributeHandle(33)},
        b"release-tag",
    )
    adapter.requestDivestitureConfirmation(
        ObjectInstanceHandle(21),
        {AttributeHandle(34)},
    )
    adapter.confirmAttributeOwnershipAcquisitionCancellation(
        ObjectInstanceHandle(21),
        {AttributeHandle(35)},
    )
    adapter.attributeIsNotOwned(
        ObjectInstanceHandle(21),
        AttributeHandle(36),
    )
    adapter.informAttributeOwnership(
        ObjectInstanceHandle(21),
        AttributeHandle(37),
        FederateHandle(41),
    )

    assert [name for name, _args in proxy.calls] == [
        "removeObjectInstance",
        "requestAttributeOwnershipAssumption",
        "attributeOwnershipAcquisitionNotification",
        "attributeOwnershipUnavailable",
        "requestAttributeOwnershipRelease",
        "requestDivestitureConfirmation",
        "confirmAttributeOwnershipAcquisitionCancellation",
        "attributeIsNotOwned",
        "informAttributeOwnership",
    ]

    remove_args = proxy.calls[0][1]
    assert isinstance(remove_args[0], JavaObjectInstanceHandle)
    assert remove_args[0].value == 21
    assert isinstance(remove_args[1], JavaByteArray)
    assert remove_args[1].value == b"remove-tag"
    assert str(remove_args[2]) == "OrderType.RECEIVE"

    request_args = proxy.calls[1][1]
    assert isinstance(request_args[0], JavaObjectInstanceHandle)
    assert {item.value for item in request_args[1]} == {31, 32}
    assert isinstance(request_args[2], JavaByteArray)
    assert request_args[2].value == b"offer-tag"

    acquired_args = proxy.calls[2][1]
    assert isinstance(acquired_args[0], JavaObjectInstanceHandle)
    assert {item.value for item in acquired_args[1]} == {31}
    assert isinstance(acquired_args[2], JavaByteArray)
    assert acquired_args[2].value == b"acquired-tag"

    unavailable_args = proxy.calls[3][1]
    assert isinstance(unavailable_args[0], JavaObjectInstanceHandle)
    assert {item.value for item in unavailable_args[1]} == {32}

    release_args = proxy.calls[4][1]
    assert isinstance(release_args[0], JavaObjectInstanceHandle)
    assert {item.value for item in release_args[1]} == {33}
    assert isinstance(release_args[2], JavaByteArray)
    assert release_args[2].value == b"release-tag"

    divest_args = proxy.calls[5][1]
    assert isinstance(divest_args[0], JavaObjectInstanceHandle)
    assert {item.value for item in divest_args[1]} == {34}

    cancelled_args = proxy.calls[6][1]
    assert isinstance(cancelled_args[0], JavaObjectInstanceHandle)
    assert {item.value for item in cancelled_args[1]} == {35}

    not_owned_args = proxy.calls[7][1]
    assert isinstance(not_owned_args[0], JavaObjectInstanceHandle)
    assert isinstance(not_owned_args[1], JavaAttributeHandle)
    assert not_owned_args[1].value == 36

    informed_args = proxy.calls[8][1]
    assert isinstance(informed_args[0], JavaObjectInstanceHandle)
    assert isinstance(informed_args[1], JavaAttributeHandle)
    assert informed_args[1].value == 37
    assert informed_args[2].value == 41


def test_certi_java_federate_adapter_forwards_synchronization_callbacks():
    proxy = _RecordingProxy()
    adapter = _CERTIJavaFederateAdapter(proxy)

    adapter.announceSynchronizationPoint("READY", b"sync-tag")
    adapter.federationSynchronized("READY", True)

    assert [name for name, _args in proxy.calls] == [
        "announceSynchronizationPoint",
        "federationSynchronized",
    ]

    announce_args = proxy.calls[0][1]
    assert announce_args[0] == "READY"
    assert isinstance(announce_args[1], JavaByteArray)
    assert announce_args[1].value == b"sync-tag"

    sync_args = proxy.calls[1][1]
    assert sync_args == ("READY", True)


def test_certi_java_value_converter_preserves_numeric_handles():
    converter = CERTIJavaValueConverter(ShimJavaBridge("jpype"))

    object_class = ObjectClassHandle(5)
    attribute = AttributeHandle(7)
    interaction = InteractionClassHandle(9)
    parameter = ParameterHandle(11)
    instance = ObjectInstanceHandle(13)
    transport = TransportationTypeHandle(1)

    assert converter.to_backend(object_class, expected_type_name="ObjectClassHandle").value == 5
    assert converter.to_backend(attribute, expected_type_name="AttributeHandle").value == 7
    assert converter.to_backend(interaction, expected_type_name="InteractionClassHandle").value == 9
    assert converter.to_backend(parameter, expected_type_name="ParameterHandle").value == 11
    assert converter.to_backend(instance, expected_type_name="ObjectInstanceHandle").value == 13
    assert converter.to_backend(transport, expected_type_name="TransportationTypeHandle").value == 1

    assert converter.from_backend(JavaObjectClassHandle(5), expected_type_name="ObjectClassHandle") == object_class
    assert converter.from_backend(JavaAttributeHandle(7), expected_type_name="AttributeHandle") == attribute
    assert converter.from_backend(JavaInteractionClassHandle(9), expected_type_name="InteractionClassHandle") == interaction
    assert converter.from_backend(JavaParameterHandle(11), expected_type_name="ParameterHandle") == parameter
    assert converter.from_backend(JavaObjectInstanceHandle(13), expected_type_name="ObjectInstanceHandle") == instance
    assert converter.from_backend(JavaTransportationTypeHandle(1), expected_type_name="TransportationTypeHandle") == transport
