from __future__ import annotations

import uuid

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import OrderType, ResignAction
from hla.runtime.factory import create_rti_ambassador
from hla.backends.inmemory import InMemoryRTIEngine
from hla.verification import (
    CallbackControlScenarioConfig,
    SupportServicesScenarioConfig,
    run_callback_control_scenario,
    run_support_factory_and_decode_scenario,
)
from tests.vendors.runtime_support import cleanup_federation


def test_python_backend_support_factory_and_decode_matrix():
    engine = InMemoryRTIEngine()
    rti = create_rti_ambassador("python", engine=engine)
    config = SupportServicesScenarioConfig(
        federation_name=f"python-support-factory-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"python-support-{uuid.uuid4().hex[:8]}",
    )

    summary = run_support_factory_and_decode_scenario(
        rti,
        config=config,
        federate=RecordingFederateAmbassador(),
    )

    assert summary["lookup_summary"]["federate_name"] == config.federate_name
    assert summary["lookup_summary"]["normalized_federate_handle"] == summary["federate_handle"]
    assert summary["lookup_summary"]["object_class_name"] == config.object_class_name
    assert summary["lookup_summary"]["attribute_name"] == config.attribute_name
    assert summary["lookup_summary"]["interaction_class_name"] == config.interaction_class_name
    assert summary["lookup_summary"]["parameter_name"] == config.parameter_name
    assert summary["lookup_summary"]["object_instance_name"] == config.object_instance_name
    assert summary["lookup_summary"]["object_instance_handle"] == summary["object_instance"]
    assert summary["lookup_summary"]["known_object_class"] == summary["object_class"]
    assert summary["lookup_summary"]["reliable_transport_name"] == "HLAreliable"
    assert summary["lookup_summary"]["best_effort_transport_name"] == "HLAbestEffort"
    assert summary["lookup_summary"]["reliable_transport_enum_name"] == "HLAreliable"
    assert summary["lookup_summary"]["best_effort_transport_enum_name"] == "HLAbestEffort"
    assert summary["lookup_summary"]["receive_order_name"] == "RECEIVE"
    assert summary["lookup_summary"]["timestamp_order_type"] is OrderType.TIMESTAMP
    assert summary["decoded_summary"]["attribute_handle"] == summary["attribute"]
    assert summary["decoded_summary"]["parameter_handle"] == summary["parameter"]
    assert summary["factory_summary"]["attribute_region_pair_list_factory"] is not None

    cleanup_federation(
        config.federation_name,
        destroyer=rti,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        disconnect_rtis=(rti,),
    )


def test_python_backend_callback_control_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    config = CallbackControlScenarioConfig(
        federation_name=f"python-callback-control-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
    )
    publisher_federate = RecordingFederateAmbassador()
    subscriber_federate = RecordingFederateAmbassador()

    summary = run_callback_control_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_federate,
        subscriber_federate=subscriber_federate,
    )

    assert summary["first_queued_while_disabled"] is True
    assert summary["first_evoke"] is False
    assert summary["first_release"] is True
    assert summary["first_delivery"].args[0] == summary["object_instance"]
    assert summary["first_delivery"].args[1] == summary["subscriber_object_class"]
    assert summary["first_delivery"].args[2] == config.object_instance_name
    assert summary["first_reflection"].args[1] == {summary["subscriber_attribute"]: config.first_payload}
    assert summary["first_reflection"].args[2] == config.first_tag
    assert summary["second_batch_queued_while_disabled"] is True
    assert summary["blocked_batch_evoke"] is False
    assert summary["batch_evoke"] is True
    assert summary["drained_tags"] == [config.second_tag, config.third_tag]
    assert summary["drained_payloads"] == [
        {summary["subscriber_attribute"]: config.second_payload},
        {summary["subscriber_attribute"]: config.third_payload},
    ]
    assert summary["post_drain"] is False

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.NO_ACTION,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )
