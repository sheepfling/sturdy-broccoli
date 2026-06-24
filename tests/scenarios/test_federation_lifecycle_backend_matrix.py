from __future__ import annotations

import uuid

from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.exceptions import (
    AlreadyConnected,
    CouldNotOpenFDD,
    ErrorReadingFDD,
    FederateIsExecutionMember,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InconsistentFDD,
)
from hla.runtime.factory import create_rti_ambassador
from hla.backends.inmemory import InMemoryRTIEngine, PythonRTIConfig
from hla.verification import (
    FederationLifecycleScenarioConfig,
    run_fom_integrity_negative_scenario,
    run_fom_module_visibility_scenario,
    run_multi_module_fom_visibility_scenario,
    run_federation_lifecycle_negative_scenario,
    run_federation_lifecycle_scenario,
    run_federation_listing_scenario,
    run_multi_participation_scenario,
)


def test_python_backend_federation_lifecycle_matrix():
    rti = create_rti_ambassador("python1516e")
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-lifecycle-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_federation_lifecycle_scenario(
        rti,
        config=config,
        federate=RecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["federate_handle"] is not None


def test_python_backend_federation_lifecycle_with_mim_matrix():
    rti = create_rti_ambassador("python1516e")
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-lifecycle-mim-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        use_mim_create=True,
    )

    summary = run_federation_lifecycle_scenario(
        rti,
        config=config,
        federate=RecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["use_mim_create"] is True


def test_python_backend_federation_listing_matrix():
    rti = create_rti_ambassador("python1516e")
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-listing-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_federation_listing_scenario(
        rti,
        config=config,
        federate=RecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["report"].method_name == "reportFederationExecutions"


def test_python_backend_fom_module_visibility_matrix():
    rti = create_rti_ambassador("python1516e")
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-fom-visibility-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_fom_module_visibility_scenario(
        rti,
        config=config,
        federate=RecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["federate_handle"] is not None


def test_python_backend_federation_lifecycle_negative_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python1516e", engine=engine)
    wing = create_rti_ambassador("python1516e", engine=engine)
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-lifecycle-negative-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
    )

    summary = run_federation_lifecycle_negative_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["already_connected"], AlreadyConnected)
    assert isinstance(summary["duplicate_create"], FederationExecutionAlreadyExists)
    assert isinstance(summary["disconnect_while_joined"], FederateIsExecutionMember)
    assert isinstance(summary["destroy_with_joined"], FederatesCurrentlyJoined)
    assert isinstance(summary["destroy_missing"], FederationExecutionDoesNotExist)


def test_python_backend_multi_participation_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador("python1516e", engine=engine)
    wing = create_rti_ambassador("python1516e", engine=engine)
    shadow = create_rti_ambassador("python1516e", engine=engine)
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-multi-participation-{uuid.uuid4().hex[:8]}",
        secondary_federation_name=f"python-multi-participation-secondary-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        logical_time_implementation_name="HLAinteger64Time",
        federate_name="Leader",
        second_federate_name="Wing",
        secondary_federate_name="Shadow",
    )

    summary = run_multi_participation_scenario(
        leader,
        wing,
        shadow,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        shadow_federate=RecordingFederateAmbassador(),
    )

    assert summary["primary_federation_name"] == config.federation_name
    assert summary["secondary_federation_name"] == config.secondary_federation_name
    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None
    assert summary["shadow_handle"] is not None


def test_python_backend_fom_integrity_negative_matrix():
    engine = InMemoryRTIEngine()
    leader = create_rti_ambassador(
        "python",
        engine=engine,
        config=PythonRTIConfig(name="python-fom-negative-leader", strict_fom_loading=True),
    )
    wing = create_rti_ambassador(
        "python",
        engine=engine,
        config=PythonRTIConfig(name="python-fom-negative-wing", strict_fom_loading=True),
    )
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-fom-negative-{uuid.uuid4().hex[:8]}",
        fom_modules=("resource:VendorSmokeFOM.xml",),
        federate_name="Leader",
        second_federate_name="Wing",
        federate_type="LifecycleType",
    )

    summary = run_fom_integrity_negative_scenario(
        leader,
        wing,
        config=config,
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
    )

    assert isinstance(summary["create_missing"], CouldNotOpenFDD)
    assert isinstance(summary["create_bad"], ErrorReadingFDD)
    assert isinstance(summary["create_inconsistent"], InconsistentFDD)
    assert isinstance(summary["join_missing"], CouldNotOpenFDD)
    assert isinstance(summary["join_bad"], ErrorReadingFDD)
    assert isinstance(summary["join_inconsistent"], InconsistentFDD)
    assert summary["leader_handle"] is not None
    assert summary["wing_handle"] is not None


def test_python_backend_multi_module_fom_visibility_matrix():
    rti = create_rti_ambassador("python1516e")
    config = FederationLifecycleScenarioConfig(
        federation_name=f"python-fom-multi-{uuid.uuid4().hex[:8]}",
        federate_name="Leader",
        federate_type="LifecycleType",
    )

    summary = run_multi_module_fom_visibility_scenario(
        rti,
        config=config,
        federate=RecordingFederateAmbassador(),
    )

    assert summary["federation_name"] == config.federation_name
    assert summary["federate_handle"] is not None
