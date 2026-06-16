from __future__ import annotations

import uuid

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import OrderType, ResignAction
from hla.rti1516e.factory import create_rti_ambassador
from hla.backends.inmemory import InMemoryRTIEngine
from hla.verification import (
    SupportServicesScenarioConfig,
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
