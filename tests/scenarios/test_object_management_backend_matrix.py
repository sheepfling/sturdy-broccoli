from __future__ import annotations

import uuid
from pathlib import Path

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import OrderType, ResignAction
from hla.rti1516e.factory import create_rti_ambassador
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time
from hla.backends.inmemory import InMemoryRTIEngine
from hla.verification import (
    DeclarationManagementScenarioConfig,
    DiscoveryClassScenarioConfig,
    LocalDeleteScenarioConfig,
    NameReservationScenarioConfig,
    ObjectScopeScenarioConfig,
    OrphanObjectScenarioConfig,
    RequestAttributeValueUpdateScenarioConfig,
    TimedDeleteScenarioConfig,
    TwoFederateExchangeConfig,
    TransportationTypeScenarioConfig,
    UpdateRateScenarioConfig,
    assert_two_federate_exchange_callback_history,
    run_declaration_invalid_attribute_publication_scenario,
    run_declaration_management_scenario,
    run_declaration_unpublish_rejection_scenario,
    run_time_managed_declaration_independence_scenario,
    run_discovery_class_scenario,
    run_discovery_metadata_callback_scenario,
    run_local_delete_scenario,
    run_name_reservation_scenario,
    run_object_scope_relevance_scenario,
    run_orphan_object_lifecycle_scenario,
    run_request_attribute_value_update_routing_scenario,
    run_request_attribute_value_update_scenario,
    run_timed_delete_scenario,
    run_transportation_type_rejection_scenario,
    run_transportation_type_restore_persistence_scenario,
    run_transportation_type_scenario,
    run_two_federate_exchange_scenario,
    run_update_advisory_callback_scenario,
    run_update_rate_scenario,
    write_hierarchy_fom,
    write_update_rate_fom,
)
from tests.vendors.runtime_support import cleanup_federation


def test_python_backend_exchange_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    config = TwoFederateExchangeConfig(
        federation_name=f"python-exchange-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=f"python-object-{uuid.uuid4().hex[:8]}",
        attribute_payload=b"payload-r",
        attribute_tag=b"reflect-tag",
        interaction_payload=b"hello-r",
        interaction_tag=b"interaction-tag",
        enable_time_management=True,
        lookahead=HLAinteger64Interval(1),
        advance_time=HLAinteger64Time(8),
        timestamped_attribute_payload=b"payload-tso",
        timestamped_attribute_tag=b"reflect-tso",
        timestamped_attribute_time=HLAinteger64Time(5),
        timestamped_interaction_payload=b"hello-tso",
        timestamped_interaction_tag=b"interaction-tso",
        timestamped_interaction_time=HLAinteger64Time(6),
    )

    summary = run_two_federate_exchange_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=publisher_fed,
        subscriber_federate=subscriber_fed,
    )

    assert summary["discover"].args[2] == config.object_instance_name
    assert summary["reflect"].args[1] == {summary["subscriber_attribute"]: b"payload-r"}
    assert summary["interaction"].args[1] == {summary["subscriber_parameter"]: b"hello-r"}
    assert summary["remove"] is not None
    assert summary["remove"].args[1] == config.delete_tag

    history = assert_two_federate_exchange_callback_history(
        summary,
        publisher_federate=publisher_fed,
        subscriber_federate=subscriber_fed,
        config=config,
    )
    assert history["receive_reflect"].args[3] is OrderType.RECEIVE
    assert history["timestamp_interaction"].args[3] is OrderType.TIMESTAMP

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_discovery_metadata_callback_matrix():
    federate = RecordingFederateAmbassador()
    summary = run_discovery_metadata_callback_scenario(
        federate.discoverObjectInstance,
        federate.hasProducingFederate,
        federate.getProducingFederate,
        federate.hasSentRegions,
        federate.getSentRegions,
        federate=federate,
        object_name="python-discovery-metadata",
    )

    assert summary["discover_record"].args[2] == "python-discovery-metadata"
    assert summary["has_producing_record"].args[1] == summary["producing_federate"]
    assert summary["get_regions_record"].args[1] == summary["sent_regions"]


def test_python_discovery_class_matrix(tmp_path: Path):
    hierarchy_fom = write_hierarchy_fom(tmp_path / "hierarchy-fom.xml")
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    config = DiscoveryClassScenarioConfig(
        federation_name=f"python-discovery-class-{uuid.uuid4().hex[:8]}",
        fom_modules=(hierarchy_fom,),
        object_instance_name=f"Hierarchy-{uuid.uuid4().hex[:8]}",
    )

    summary = run_discovery_class_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=RecordingFederateAmbassador(),
        subscriber_federate=RecordingFederateAmbassador(),
    )

    assert summary["discovery"].args[1] == summary["subscriber_class"]
    assert summary["reflection"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_name_reservation_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    rival = create_rti_ambassador("python", engine=engine)
    config = NameReservationScenarioConfig(
        federation_name=f"python-name-reservation-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        reserved_name=f"Reserved-{uuid.uuid4().hex[:8]}",
        multiple_names=(
            f"Reserved-A-{uuid.uuid4().hex[:4]}",
            f"Reserved-B-{uuid.uuid4().hex[:4]}",
        ),
    )

    summary = run_name_reservation_scenario(
        owner,
        rival,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        rival_federate=RecordingFederateAmbassador(),
    )

    assert summary["owner_reserved"].args == (config.reserved_name,)
    assert summary["rival_reserved_failed"].args == (config.reserved_name,)
    assert summary["rival_reserved"].args == (config.reserved_name,)
    assert summary["owner_multiple_reserved"].args[0] == set(config.multiple_names)
    assert summary["rival_multiple_reserved_failed"].args[0] == set(config.multiple_names)
    assert summary["rival_multiple_reserved"].args[0] == set(config.multiple_names)

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.NO_ACTION,
        remaining_resignations=((rival, ResignAction.NO_ACTION),),
        disconnect_rtis=(rival, owner),
    )


def test_python_backend_declaration_management_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    config = DeclarationManagementScenarioConfig(
        federation_name=f"python-declaration-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=f"python-declaration-{uuid.uuid4().hex[:8]}",
    )

    summary = run_declaration_management_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=RecordingFederateAmbassador(),
        subscriber_federate=RecordingFederateAmbassador(),
    )

    assert [record.args for record in summary["start_records"]] == [
        (summary["publisher_class"],),
        (summary["publisher_class"],),
    ]
    assert [record.args for record in summary["stop_records"]] == [
        (summary["publisher_class"],),
        (summary["publisher_class"],),
    ]
    assert [record.args for record in summary["turn_on_records"]] == [
        (summary["publisher_interaction"],),
        (summary["publisher_interaction"],),
    ]
    assert [record.args for record in summary["turn_off_records"]] == [
        (summary["publisher_interaction"],),
        (summary["publisher_interaction"],),
    ]
    assert summary["second_stop_record"] is not None
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert summary["suppressed_reflect_count"] == 1
    assert summary["suppressed_interaction_count"] == 1

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_backend_declaration_management_overload_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    config = DeclarationManagementScenarioConfig(
        federation_name=f"python-declaration-overloads-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=f"python-declaration-overloads-{uuid.uuid4().hex[:8]}",
        use_passive_object_subscription=True,
        use_passive_interaction_subscription=True,
        use_full_object_unpublish=True,
        use_full_object_unsubscribe=True,
    )

    summary = run_declaration_management_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=RecordingFederateAmbassador(),
        subscriber_federate=RecordingFederateAmbassador(),
    )

    assert [record.args for record in summary["start_records"]] == [
        (summary["publisher_class"],),
        (summary["publisher_class"],),
    ]
    assert [record.args for record in summary["stop_records"]] == [
        (summary["publisher_class"],),
    ]
    assert [record.args for record in summary["turn_on_records"]] == [
        (summary["publisher_interaction"],),
        (summary["publisher_interaction"],),
    ]
    assert [record.args for record in summary["turn_off_records"]] == [
        (summary["publisher_interaction"],),
        (summary["publisher_interaction"],),
    ]
    assert summary["second_stop_record"] is None
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}
    assert summary["suppressed_reflect_count"] == 1
    assert summary["suppressed_interaction_count"] == 1

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_backend_declaration_invalid_attribute_publication_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    config = DeclarationManagementScenarioConfig(
        federation_name=f"python-declaration-invalid-attr-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
    )

    summary = run_declaration_invalid_attribute_publication_scenario(
        publisher,
        config=config,
        publisher_federate=RecordingFederateAmbassador(),
    )

    assert summary["invalid_attribute"] != summary["publisher_attribute"]

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.NO_ACTION,
        disconnect_rtis=(publisher,),
    )


def test_python_backend_time_managed_declaration_independence_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    config = DeclarationManagementScenarioConfig(
        federation_name=f"python-declaration-time-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=f"python-declaration-time-{uuid.uuid4().hex[:8]}",
        declaration_lookahead=HLAinteger64Interval(1),
    )

    summary = run_time_managed_declaration_independence_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=RecordingFederateAmbassador(),
        subscriber_federate=RecordingFederateAmbassador(),
    )

    assert summary["time_regulation"] is not None
    assert summary["time_constrained"] is not None
    assert summary["start_record"].args == (summary["publisher_class"],)
    assert summary["turn_on_record"].args == (summary["publisher_interaction"],)
    assert summary["discover_record"].args[2] == config.object_instance_name
    assert summary["reflect_record"].args[1] == {summary["subscriber_attribute"]: config.attribute_payload}
    assert summary["interaction_record"].args[1] == {summary["subscriber_parameter"]: config.interaction_payload}

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_backend_declaration_unpublish_rejection_matrix():
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)

    def _enable_strict_object_publication(rti):
        rti.backend.config.strict_object_publication = True

    def _enable_strict_interaction_publication(rti):
        rti.backend.config.strict_interaction_publication = True

    config = DeclarationManagementScenarioConfig(
        federation_name=f"python-declaration-unpublish-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        interaction_class_name="HLAinteractionRoot.SmokeInteraction",
        parameter_name="Message",
        object_instance_name=f"python-declaration-unpublish-{uuid.uuid4().hex[:8]}",
        before_object_unpublish_rejection_probe=_enable_strict_object_publication,
        before_interaction_unpublish_rejection_probe=_enable_strict_interaction_publication,
    )

    try:
        summary = run_declaration_unpublish_rejection_scenario(
            publisher,
            config=config,
            publisher_federate=RecordingFederateAmbassador(),
        )
        assert summary["object_unpublish_error"] is not None
        assert summary["interaction_unpublish_error"] is not None
    finally:
        publisher.backend.config.strict_object_publication = False
        publisher.backend.config.strict_interaction_publication = False
        cleanup_federation(
            config.federation_name,
            destroyer=publisher,
            destroyer_resign_action=ResignAction.NO_ACTION,
            disconnect_rtis=(publisher,),
        )


def test_python_update_advisory_callback_matrix():
    federate = RecordingFederateAmbassador()
    summary = run_update_advisory_callback_scenario(
        federate.attributesInScope,
        federate.attributesOutOfScope,
        federate.provideAttributeValueUpdate,
        federate.turnUpdatesOnForObjectInstance,
        federate.turnUpdatesOffForObjectInstance,
        federate=federate,
        tag=b"python-update-advisory",
    )

    assert summary["provide_record"].args[2] == b"python-update-advisory"
    assert summary["turn_on_record"].args[2] == "HLAdefault"


def test_python_object_scope_relevance_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = ObjectScopeScenarioConfig(
        federation_name=f"python-object-scope-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"Relevance-{uuid.uuid4().hex[:8]}",
    )

    summary = run_object_scope_relevance_scenario(
        owner,
        acquirer,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert summary["initial_in_scope"].args[0] == summary["object_instance"]
    assert summary["initial_in_scope"].args[1] == {summary["observer_attribute"]}
    assert summary["out_of_scope"].args[0] == summary["object_instance"]
    assert summary["out_of_scope"].args[1] == {summary["observer_attribute"]}
    assert summary["reacquired_in_scope"].args[0] == summary["object_instance"]
    assert summary["reacquired_in_scope"].args[1] == {summary["observer_attribute"]}
    assert summary["initial_reflection"].args[0] == summary["object_instance"]
    assert summary["suppressed_reflection"] is None
    assert summary["acquired_reflection"].args[0] == summary["object_instance"]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.NO_ACTION), (observer, ResignAction.NO_ACTION)),
        disconnect_rtis=(observer, acquirer, owner),
    )


def test_python_transportation_type_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = TransportationTypeScenarioConfig(
        federation_name=f"python-transport-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"Transport-{uuid.uuid4().hex[:8]}",
    )

    summary = run_transportation_type_scenario(
        owner,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert summary["confirm_attribute"].args == (
        summary["object_instance"],
        {summary["attribute"]},
        summary["transport"],
    )
    assert summary["report_attribute"].args == (
        summary["object_instance"],
        summary["attribute"],
        summary["transport"],
    )
    assert summary["confirm_interaction"].args == (summary["interaction"], summary["transport"])
    assert summary["report_interaction"].args[1:] == (summary["interaction"], summary["transport"])

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((observer, ResignAction.NO_ACTION),),
        disconnect_rtis=(observer, owner),
    )


def test_python_transportation_type_restore_persistence_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = TransportationTypeScenarioConfig(
        federation_name=f"python-transport-restore-{uuid.uuid4().hex[:8]}",
        fom_modules=("TargetRadarFOMmodule.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_class_name="HLAobjectRoot.Target",
        attribute_name="Position",
        second_attribute_name="RCS",
        interaction_class_name="HLAinteractionRoot.TrackReport",
        parameter_name="TrackId",
        object_instance_name=f"TransportRestore-{uuid.uuid4().hex[:8]}",
        save_name=f"TRANSPORT-SAVE-{uuid.uuid4().hex[:8]}",
    )

    summary = run_transportation_type_restore_persistence_scenario(
        owner,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert len(summary["pre_restore_reflects"]) == 2
    assert len(summary["post_restore_attribute_reports"]) >= 2
    assert len(summary["post_restore_reflects"]) == 2
    assert summary["post_restore_interaction_report"].args[1:] == (
        summary["interaction"],
        summary["best_effort_transport"],
    )

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((observer, ResignAction.NO_ACTION),),
        disconnect_rtis=(observer, owner),
    )


def test_python_transportation_type_rejection_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = TransportationTypeScenarioConfig(
        federation_name=f"python-transport-reject-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"TransportReject-{uuid.uuid4().hex[:8]}",
        save_name=f"TRANSPORT-REJECT-{uuid.uuid4().hex[:8]}",
    )

    summary = run_transportation_type_rejection_scenario(
        owner,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert summary["object_instance"] is not None
    assert summary["attribute"] is not None
    assert summary["interaction"] is not None

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((observer, ResignAction.NO_ACTION),),
        disconnect_rtis=(observer, owner),
    )


def test_python_update_rate_matrix(tmp_path: Path):
    update_rate_fom = write_update_rate_fom(tmp_path / "update-rate-fom.xml")
    engine = InMemoryRTIEngine()
    publisher = create_rti_ambassador("python", engine=engine)
    subscriber = create_rti_ambassador("python", engine=engine)
    config = UpdateRateScenarioConfig(
        federation_name=f"python-update-rate-{uuid.uuid4().hex[:8]}",
        fom_modules=(update_rate_fom,),
        logical_time_implementation_name="HLAfloat64Time",
        object_instance_name=f"Rate-{uuid.uuid4().hex[:8]}",
    )

    summary = run_update_rate_scenario(
        publisher,
        subscriber,
        config=config,
        publisher_federate=RecordingFederateAmbassador(),
        subscriber_federate=RecordingFederateAmbassador(),
    )

    assert summary["values"] == [b"t1", b"t16"]

    cleanup_federation(
        config.federation_name,
        destroyer=publisher,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((subscriber, ResignAction.NO_ACTION),),
        disconnect_rtis=(subscriber, publisher),
    )


def test_python_request_attribute_value_update_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    requester = create_rti_ambassador("python", engine=engine)
    config = RequestAttributeValueUpdateScenarioConfig(
        federation_name=f"python-ravu-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"RAVU-{uuid.uuid4().hex[:8]}",
        request_tag=b"python-ravu",
    )

    summary = run_request_attribute_value_update_scenario(
        owner,
        requester,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        requester_federate=RecordingFederateAmbassador(),
    )

    assert summary["provide_record"].args == (
        summary["object_instance"],
        {summary["owner_attribute"]},
        b"python-ravu",
    )

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((requester, ResignAction.NO_ACTION),),
        disconnect_rtis=(requester, owner),
    )


def test_python_request_attribute_value_update_routing_matrix():
    engine = InMemoryRTIEngine()
    owner_a = create_rti_ambassador("python", engine=engine)
    owner_b = create_rti_ambassador("python", engine=engine)
    requester = create_rti_ambassador("python", engine=engine)
    config = RequestAttributeValueUpdateScenarioConfig(
        federation_name=f"python-ravu-routing-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"python-RAVU-{uuid.uuid4().hex[:8]}",
        request_tag=b"object-only",
    )

    summary = run_request_attribute_value_update_routing_scenario(
        owner_a,
        owner_b,
        requester,
        config=config,
        owner_a_federate=RecordingFederateAmbassador(),
        owner_b_federate=RecordingFederateAmbassador(),
        requester_federate=RecordingFederateAmbassador(),
    )

    assert summary["object_target_provide_a"].args == (summary["object_a"], {summary["requester_attribute"]}, b"object-only")
    assert summary["object_target_provide_b"] is None
    assert summary["class_target_provide_a"].args == (summary["object_a"], {summary["requester_attribute"]}, b"class-wide")
    assert summary["class_target_provide_b"].args == (summary["object_b"], {summary["requester_attribute"]}, b"class-wide")

    cleanup_federation(
        config.federation_name,
        destroyer=owner_a,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((owner_b, ResignAction.DELETE_OBJECTS), (requester, ResignAction.NO_ACTION)),
        disconnect_rtis=(requester, owner_b, owner_a),
    )


def test_python_orphan_object_lifecycle_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    late = create_rti_ambassador("python", engine=engine)
    config = OrphanObjectScenarioConfig(
        federation_name=f"python-orphan-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"python-Orphan-{uuid.uuid4().hex[:8]}",
    )

    summary = run_orphan_object_lifecycle_scenario(
        owner,
        observer,
        late,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
        late_federate=RecordingFederateAmbassador(),
    )

    assert summary["late_discovery"].args[0] == summary["object_instance"]
    assert summary["observer_remove"] is None
    assert summary["late_remove"].args[0] == summary["object_instance"]
    assert summary["late_remove"].args[1] == config.delete_tag

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.NO_ACTION,
        remaining_resignations=((observer, ResignAction.NO_ACTION), (late, ResignAction.NO_ACTION)),
        disconnect_rtis=(late, observer, owner),
    )


def test_python_timed_delete_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = TimedDeleteScenarioConfig(
        federation_name=f"python-timed-delete-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"python-TimedDelete-{uuid.uuid4().hex[:8]}",
    )

    summary = run_timed_delete_scenario(
        owner,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert summary["remove_before_grant"] is None
    assert summary["remove_after_grant"].args[0] == summary["object_instance"]
    assert summary["remove_after_grant"].args[1] == config.delete_tag

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.NO_ACTION,
        remaining_resignations=((observer, ResignAction.NO_ACTION),),
        disconnect_rtis=(observer, owner),
    )


def test_python_local_delete_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = LocalDeleteScenarioConfig(
        federation_name=f"python-local-delete-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        object_instance_name=f"LocalDelete-{uuid.uuid4().hex[:8]}",
    )

    summary = run_local_delete_scenario(
        owner,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert summary["discovery"].args[0] == summary["object_instance"]
    assert summary["reflection"].args[0] == summary["object_instance"]
    assert summary["reflection"].args[1] == {summary["observer_attribute"]: config.rediscover_payload}

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((observer, ResignAction.NO_ACTION),),
        disconnect_rtis=(observer, owner),
    )
