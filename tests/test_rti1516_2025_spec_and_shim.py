from __future__ import annotations

import uuid

import pytest


def test_2025_spec_package_exposes_authoritative_surface_without_replacing_2010() -> None:
    import hla.rti1516e as rti1516e
    import hla.rti1516_2025 as rti2025
    from hla.rti1516_2025.plugin import plugin as rti2025_plugin

    assert rti2025.RTIambassador is not rti1516e.RTIambassador
    assert rti2025.FederateAmbassador is not rti1516e.FederateAmbassador
    assert hasattr(rti2025, "RtiConfiguration")
    assert hasattr(rti2025, "Credentials")
    assert hasattr(rti2025, "AuthorizationResultCode")
    assert hasattr(rti2025, "InconsistentFOM")
    assert not hasattr(rti1516e, "RtiConfiguration")
    assert "grpc" in rti2025_plugin().spec.capabilities


def test_2025_spec_aliases_and_backend_discovery_are_spec_aware() -> None:
    from hla.rti import discover_rti_backends, resolve_spec

    spec = resolve_spec("hla4")
    assert spec.name == "rti1516_2025"
    assert spec.year == 2025
    assert spec.python_package == "hla.rti1516_2025"

    backends = {row.name: row for row in discover_rti_backends(spec="1516-2025")}
    assert set(backends) == {"shim"}
    assert backends["shim"].supports == ("rti1516_2025",)


def test_2025_shim_is_first_green_runtime_path() -> None:
    from hla.rti import create_rti_ambassador
    from hla.rti1516_2025.enums import AdditionalSettingsResultCode, CallbackModel
    from hla.rti1516_2025.exceptions import NotConnected, RTIinternalError

    rti = create_rti_ambassador(spec="2025", backend="shim")
    assert rti.backend_info.details["spec"] == "rti1516_2025"
    assert rti.getHLAversion() == "IEEE 1516.1-2025"

    with pytest.raises(NotConnected):
        rti.evokeCallback(0.0)

    result = rti.connect(object(), CallbackModel.HLA_EVOKED)
    assert result.additionalSettingsResultCode is AdditionalSettingsResultCode.SETTINGS_IGNORED
    assert rti.connected is True
    assert rti.evokeMultipleCallbacks(0.0, 0.1) is False

    with pytest.raises(RTIinternalError, match="publishObjectClassAttributes"):
        rti.publishObjectClassAttributes(object(), object())

    rti.disconnect()
    assert rti.connected is False


def test_2025_shim_rejects_duplicate_federation_and_federate_names() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import (
        FederateAlreadyExecutionMember,
        FederateNameAlreadyInUse,
        FederationExecutionAlreadyExists,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-join-{uuid.uuid4().hex[:8]}"
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")
    late = create_rti_ambassador(backend="shim")

    for rti in (leader, wing, late):
        rti.connect(object(), CallbackModel.HLA_EVOKED)

    leader.createFederationExecution(federationName=federation_name)
    with pytest.raises(FederationExecutionAlreadyExists):
        leader.createFederationExecution(federationName=federation_name)

    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )
    wing.joinFederationExecution(
        federateName="Wing",
        federateType="TestFederate",
        federationName=federation_name,
    )

    with pytest.raises(FederateNameAlreadyInUse):
        late.joinFederationExecution(
            federateName="Leader",
            federateType="TestFederate",
            federationName=federation_name,
        )
    with pytest.raises(FederateAlreadyExecutionMember):
        leader.joinFederationExecution(
            federateName="Leader-Again",
            federateType="TestFederate",
            federationName=federation_name,
        )

    leader.resignFederationExecution(ResignAction.NO_ACTION)
    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    late.disconnect()
    wing.disconnect()
    leader.disconnect()


def test_2010_and_2025_backend_selection_do_not_cross_wire() -> None:
    from hla.rti import create_rti_ambassador

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        create_rti_ambassador(spec="2025", backend="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        create_rti_ambassador(spec="rti1516e", backend="shim")
