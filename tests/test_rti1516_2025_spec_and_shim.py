from __future__ import annotations

import uuid

import pytest


class Recording2025FederateAmbassador:
    def __init__(self) -> None:
        self.callbacks: list[tuple[str, tuple[object, ...]]] = []

    def reportFederationExecutions(self, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutions", (report,)))

    def reportFederationExecutionMembers(self, federationName, report) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionMembers", (federationName, report)))

    def reportFederationExecutionDoesNotExist(self, federationName) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("reportFederationExecutionDoesNotExist", (federationName,)))

    def last_callback(self, method_name: str) -> tuple[object, ...] | None:
        for recorded_name, args in reversed(self.callbacks):
            if recorded_name == method_name:
                return args
        return None


@pytest.mark.requirements("HLA-X-2025-REQ-001", "HLA-X-2025-FI-003", "HLA-X-2025-FI-004")
def test_2025_spec_package_exposes_authoritative_surface_without_replacing_2010() -> None:
    import hla.rti1516_2025 as rti2025
    import hla.rti1516e as rti1516e
    from hla.rti1516_2025.plugin import plugin as rti2025_plugin

    assert rti2025.RTIambassador is not rti1516e.RTIambassador
    assert rti2025.FederateAmbassador is not rti1516e.FederateAmbassador
    assert hasattr(rti2025, "RtiConfiguration")
    assert hasattr(rti2025, "Credentials")
    assert hasattr(rti2025, "AuthorizationResultCode")
    assert hasattr(rti2025, "InconsistentFOM")
    assert not hasattr(rti1516e, "RtiConfiguration")
    assert "grpc" in rti2025_plugin().spec.capabilities


@pytest.mark.requirements("HLA-X-2025-REQ-001")
def test_2025_spec_aliases_and_backend_discovery_are_spec_aware() -> None:
    from hla.rti import discover_rti_backends, resolve_spec

    spec = resolve_spec("hla4")
    assert spec.name == "rti1516_2025"
    assert spec.year == 2025
    assert spec.python_package == "hla.rti1516_2025"

    backends = {row.name: row for row in discover_rti_backends(spec="1516-2025")}
    assert set(backends) == {
        "cpp-shim-grpc",
        "cpp-shim-pybind",
        "cpp-2025-sdk-grpc",
        "cpp-2025-sdk-pybind",
        "cpp-standard-2025-grpc",
        "cpp-standard-2025-pybind",
        "java-2025-jpype",
        "java-2025-py4j",
        "java-shim-jpype",
        "java-shim-py4j",
        "java-standard-2025-jpype",
        "java-standard-2025-py4j",
        "shim",
    }
    assert backends["shim"].supports == ("rti1516_2025",)
    assert backends["java-shim-jpype"].supports == ("rti1516e", "rti1516_2025")
    assert backends["java-shim-py4j"].supports == ("rti1516e", "rti1516_2025")
    assert backends["cpp-shim-pybind"].supports == ("rti1516e", "rti1516_2025")
    assert backends["cpp-shim-grpc"].supports == ("rti1516e", "rti1516_2025")
    assert backends["java-standard-2025-jpype"].supports == ("rti1516_2025",)
    assert backends["java-standard-2025-py4j"].supports == ("rti1516_2025",)
    assert backends["cpp-standard-2025-pybind"].supports == ("rti1516_2025",)
    assert backends["cpp-standard-2025-grpc"].supports == ("rti1516_2025",)
    assert backends["cpp-2025-sdk-pybind"].supports == ("rti1516_2025",)
    assert backends["cpp-2025-sdk-grpc"].supports == ("rti1516_2025",)
    assert backends["java-2025-jpype"].supports == ("rti1516_2025",)
    assert backends["java-2025-py4j"].supports == ("rti1516_2025",)


@pytest.mark.requirements("HLA-X-2025-REQ-002", "HLA-X-2025-FI-005", "HLA-X-2025-FI-006")
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


@pytest.mark.requirements("HLA-X-2025-FI-005")
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


@pytest.mark.requirements("HLA2025-NEW-002", "HLA-X-2025-FI-001", "HLA-X-2025-FI-005")
def test_2025_shim_reports_federation_executions_and_members() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-report-{uuid.uuid4().hex[:8]}"
    leader_fed = Recording2025FederateAmbassador()
    wing_fed = Recording2025FederateAmbassador()
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")

    leader.connect(leader_fed, CallbackModel.HLA_EVOKED)
    wing.connect(wing_fed, CallbackModel.HLA_EVOKED)
    leader.createFederationExecution(
        federationName=federation_name,
        logicalTimeImplementationName="HLAinteger64Time",
    )

    leader.listFederationExecutions()
    execution_report = leader_fed.last_callback("reportFederationExecutions")
    assert execution_report is not None
    executions = execution_report[0]
    assert any(
        row.federationExecutionName == federation_name
        and row.logicalTimeImplementationName == "HLAinteger64Time"
        for row in executions
    )

    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )
    wing.joinFederationExecution(
        federateName="Wing",
        federateType="Observer",
        federationName=federation_name,
    )

    leader.listFederationExecutionMembers(federation_name)
    members_report = leader_fed.last_callback("reportFederationExecutionMembers")
    assert members_report is not None
    assert members_report[0] == federation_name
    assert {(row.federateName, row.federateType) for row in members_report[1]} == {
        ("Leader", "TestFederate"),
        ("Wing", "Observer"),
    }

    leader.listFederationExecutionMembers(f"{federation_name}-missing")
    missing_report = leader_fed.last_callback("reportFederationExecutionDoesNotExist")
    assert missing_report == (f"{federation_name}-missing",)

    leader.resignFederationExecution(ResignAction.NO_ACTION)
    wing.resignFederationExecution(ResignAction.NO_ACTION)
    leader.destroyFederationExecution(federationName=federation_name)
    wing.disconnect()
    leader.disconnect()


@pytest.mark.requirements("HLA-X-2025-REQ-001", "HLA-X-2025-REQ-002")
def test_2010_and_2025_backend_selection_do_not_cross_wire() -> None:
    from hla.rti import create_rti_ambassador

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        create_rti_ambassador(spec="2025", backend="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        create_rti_ambassador(spec="rti1516e", backend="shim")
