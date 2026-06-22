from __future__ import annotations

from hla.backends.common import RecordingFederateAmbassador
from hla.foms.target_radar._internal.target_radar_2025_adapter import TargetRadar2025RTIAdapter
from hla.rti1516e.handles import (
    FederateHandle as FederateHandle2010,
    InteractionClassHandle as InteractionClassHandle2010,
    ObjectInstanceHandle as ObjectInstanceHandle2010,
    ParameterHandle as ParameterHandle2010,
    TransportationTypeHandle as TransportationTypeHandle2010,
)
from hla.rti1516_2025.handles import (
    FederateHandle,
    InteractionClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)


def test_recording_federate_ambassador_captures_directed_interaction_callbacks_through_2025_adapter_bridge() -> None:
    federate = RecordingFederateAmbassador()
    bridge = TargetRadar2025RTIAdapter._wrap_federate_ambassador(federate)

    getattr(bridge, "receiveDirectedInteraction")(
        InteractionClassHandle(400),
        ObjectInstanceHandle(1000),
        {ParameterHandle(500): b"TRACK"},
        b"directed-tag",
        TransportationTypeHandle(1),
        FederateHandle(2),
    )

    callback = federate.last_callback("receiveDirectedInteraction")
    assert callback is not None
    assert callback.args == (
        InteractionClassHandle2010(400),
        ObjectInstanceHandle2010(1000),
        {ParameterHandle2010(500): b"TRACK"},
        b"directed-tag",
        TransportationTypeHandle2010(1),
        FederateHandle2010(2),
    )


def test_recording_federate_ambassador_records_2025_extra_callbacks_through_camel_and_snake_names() -> None:
    federate = RecordingFederateAmbassador()
    callback_names = (
        "receiveDirectedInteraction",
        "hasProducingFederate",
        "getProducingFederate",
        "hasSentRegions",
        "getSentRegions",
    )

    for method_name in callback_names:
        snake_name = "".join(
            (f"_{char.lower()}" if char.isupper() else char)
            for char in method_name
        ).lstrip("_")
        federate.clear()

        getattr(federate, method_name)("camel")
        camel_record = federate.last_callback()
        assert camel_record is not None
        assert camel_record.method_name == method_name
        assert camel_record.args == ("camel",)

        getattr(federate, snake_name)("snake")
        snake_record = federate.last_callback()
        assert snake_record is not None
        assert snake_record.method_name == method_name
        assert snake_record.args == ("snake",)
