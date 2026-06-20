from __future__ import annotations

import uuid

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import ResignAction
from hla.rti1516e.factory import create_rti_ambassador
from hla.backends.inmemory import InMemoryRTIEngine
from hla.verification import (
    NegotiatedOwnershipScenarioConfig,
    NonOwnerUpdateScenarioConfig,
    OwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    probe_negotiated_attribute_ownership_offer,
    run_attribute_ownership_scenario,
    run_attribute_ownership_query_callback_scenario,
    run_attribute_ownership_unavailable_scenario,
    run_confirm_divestiture_negotiated_scenario,
    run_non_owner_update_rejection_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_release_request_ownership_scenario,
)
from tests.vendors.runtime_support import cleanup_federation


def test_python_backend_ownership_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = OwnershipScenarioConfig(
        federation_name=f"python-ownership-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-owned-{uuid.uuid4().hex[:8]}",
    )

    summary = run_attribute_ownership_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["not_owned"].args == (summary["object_instance"], summary["owner_attribute"])
    assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
    assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
    assert summary["informed"].args[0] == summary["object_instance"]
    assert summary["informed"].args[1] == summary["owner_attribute"]
    assert summary["informed_federate_name"] == config.acquirer_name

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_negotiated_divesting_offer_probe_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = NegotiatedOwnershipScenarioConfig(
        federation_name=f"python-negotiated-offer-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-negotiated-{uuid.uuid4().hex[:8]}",
        assumption_tag=b"assume-offer",
        request_tag=b"acquire-request",
        cancel_tag=b"reacquire-request",
    )

    summary = probe_negotiated_attribute_ownership_offer(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["assumption"] is not None
    assert summary["assumption"].args == (
        summary["acquirer_object_instance"],
        {summary["acquirer_attribute"]},
        b"assume-offer",
    )
    assert summary["divestiture_confirmation"] is not None
    assert summary["divestiture_confirmation"].args[0] == summary["object_instance"]
    assert summary["owner_attribute"] in summary["divestiture_confirmation"].args[1]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_backend_negotiated_ownership_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = NegotiatedOwnershipScenarioConfig(
        federation_name=f"python-negotiated-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-negotiated-{uuid.uuid4().hex[:8]}",
        assumption_tag=b"assume-offer",
        request_tag=b"acquire-request",
        cancel_tag=b"reacquire-request",
    )

    summary = run_negotiated_attribute_ownership_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["negotiated_divestiture_supported"] is True
    assert summary["assumption"] is not None
    assert summary["release"].args == (
        summary["release_object_instance"],
        {summary["owner_attribute"]},
        b"reacquire-request",
    )
    assert summary["cancellation"].args == (
        summary["release_acquirer_object_instance"],
        {summary["acquirer_attribute"]},
    )
    assert summary["divested"] == {summary["owner_attribute"]}
    assert summary["acquired"].args[0] == summary["release_acquirer_object_instance"]
    assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
    assert summary["informed"].args[0] == summary["release_object_instance"]
    assert summary["informed"].args[1] == summary["owner_attribute"]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_backend_confirm_divestiture_negotiated_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = NegotiatedOwnershipScenarioConfig(
        federation_name=f"python-confirm-negotiated-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-confirm-negotiated-{uuid.uuid4().hex[:8]}",
        assumption_tag=b"assume-offer",
        request_tag=b"acquire-request",
        cancel_tag=b"reacquire-request",
    )

    summary = run_confirm_divestiture_negotiated_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["divestiture_confirmation"].args == (
        summary["object_instance"],
        {summary["owner_attribute"]},
        b"acquire-request",
    )
    assert summary["acquired"].args == (
        summary["acquirer_object_instance"],
        {summary["acquirer_attribute"]},
        b"confirm-tag",
    )
    assert summary["informed"].args[0] == summary["object_instance"]
    assert summary["informed"].args[1] == summary["owner_attribute"]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_backend_release_request_ownership_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = ReleaseRequestOwnershipScenarioConfig(
        federation_name=f"python-release-request-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-release-{uuid.uuid4().hex[:8]}",
        request_tag=b"acquire-request",
        owner_action="ifwanted",
    )

    summary = run_release_request_ownership_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["release"].args == (
        summary["object_instance"],
        {summary["owner_attribute"]},
        b"acquire-request",
    )
    assert summary["divested"] == {summary["owner_attribute"]}
    assert summary["acquired"].args[0] == summary["acquirer_object_instance"]
    assert summary["acquired"].args[1] == {summary["acquirer_attribute"]}
    assert summary["informed"].args[0] == summary["object_instance"]
    assert summary["informed"].args[1] == summary["owner_attribute"]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_backend_ownership_unavailable_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = OwnershipScenarioConfig(
        federation_name=f"python-ownership-unavailable-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-unavailable-{uuid.uuid4().hex[:8]}",
    )

    summary = run_attribute_ownership_unavailable_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["unavailable"].args[0] == summary["object_instance"]
    assert summary["acquirer_attribute"] in summary["unavailable"].args[1]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_backend_release_denied_ownership_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    acquirer = create_rti_ambassador("python", engine=engine)
    config = ReleaseRequestOwnershipScenarioConfig(
        federation_name=f"python-release-denied-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        acquirer_name="Acquirer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-release-denied-{uuid.uuid4().hex[:8]}",
        request_tag=b"deny-request",
        owner_action="deny",
    )

    summary = run_release_request_ownership_scenario(
        owner,
        acquirer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        acquirer_federate=RecordingFederateAmbassador(),
    )

    assert summary["release"].args == (
        summary["object_instance"],
        {summary["owner_attribute"]},
        b"deny-request",
    )
    assert summary["acquired"] is None

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((acquirer, ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES),),
        disconnect_rtis=(acquirer, owner),
    )


def test_python_backend_non_owner_update_rejection_matrix():
    engine = InMemoryRTIEngine()
    owner = create_rti_ambassador("python", engine=engine)
    observer = create_rti_ambassador("python", engine=engine)
    config = NonOwnerUpdateScenarioConfig(
        federation_name=f"python-non-owner-update-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        owner_name="Owner",
        observer_name="Observer",
        federate_type="OwnershipFederate",
        object_class_name="HLAobjectRoot.SmokeObject",
        attribute_name="Payload",
        object_instance_name=f"python-illegal-update-{uuid.uuid4().hex[:8]}",
    )

    summary = run_non_owner_update_rejection_scenario(
        owner,
        observer,
        config=config,
        owner_federate=RecordingFederateAmbassador(),
        observer_federate=RecordingFederateAmbassador(),
    )

    assert summary["failure"] is not None
    assert summary["failure_type"]

    cleanup_federation(
        config.federation_name,
        destroyer=owner,
        destroyer_resign_action=ResignAction.DELETE_OBJECTS,
        remaining_resignations=((observer, ResignAction.NO_ACTION),),
        disconnect_rtis=(observer, owner),
    )


def test_python_attribute_ownership_query_callback_matrix():
    federate = RecordingFederateAmbassador()
    summary = run_attribute_ownership_query_callback_scenario(
        federate.informAttributeOwnership,
        federate.attributeIsNotOwned,
        federate.attributeIsOwnedByRTI,
        federate=federate,
    )

    assert summary["inform_record"].args == (
        summary["object_handle"],
        summary["attribute_handle"],
        summary["owner_handle"],
    )
    assert summary["not_owned_record"].args == (
        summary["object_handle"],
        summary["attribute_handle"],
    )
    assert summary["rti_owned_record"].args == (
        summary["object_handle"],
        summary["attribute_handle"],
    )
