from __future__ import annotations

import uuid
from pathlib import Path

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

    def federateResigned(self, reasonForResignDescription) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("federateResigned", (reasonForResignDescription,)))

    def timeRegulationEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeRegulationEnabled", (time,)))

    def timeConstrainedEnabled(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeConstrainedEnabled", (time,)))

    def timeAdvanceGrant(self, time) -> None:  # noqa: N802, ANN001
        self.callbacks.append(("timeAdvanceGrant", (time,)))

    def last_callback(self, method_name: str) -> tuple[object, ...] | None:
        for recorded_name, args in reversed(self.callbacks):
            if recorded_name == method_name:
                return args
        return None


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004")
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


@pytest.mark.requirements("HLA2025-REQ-001")
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


@pytest.mark.requirements("HLA2025-REQ-002", "HLA2025-FI-005", "HLA2025-FI-006")
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


@pytest.mark.requirements("HLA2025-FI-005")
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

    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
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


@pytest.mark.requirements("HLA2025-NEW-003", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_reports_federate_resigned_callback_with_reason_context() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-resign-{uuid.uuid4().hex[:8]}"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")

    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="ResigningFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    rti.resignFederationExecution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)

    resigned = federate.last_callback("federateResigned")
    assert resigned is not None
    reason = resigned[0]
    assert "federateName=ResigningFederate" in reason
    assert f"federationName={federation_name}" in reason
    assert "resignAction=UNCONDITIONALLY_DIVEST_ATTRIBUTES" in reason

    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-NEW-005", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_normalizes_typed_handles_and_rejects_wrong_handle_family() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction, ServiceGroup
    from hla.rti1516_2025.exceptions import (
        InvalidFederateHandle,
        InvalidInteractionClassHandle,
        InvalidObjectClassHandle,
        InvalidObjectInstanceHandle,
        InvalidServiceGroup,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.handles import (
        FederateHandle,
        InteractionClassHandle,
        ObjectClassHandle,
        ObjectInstanceHandle,
    )

    federation_name = f"shim-normalize-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")

    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    federate_handle = rti.joinFederationExecution(
        federateName="Normalizer",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert isinstance(federate_handle, FederateHandle)
    assert rti.normalizeFederateHandle(federate_handle) == federate_handle.value
    assert rti.normalizeServiceGroup(ServiceGroup.SUPPORT_SERVICES) == int(ServiceGroup.SUPPORT_SERVICES)
    assert rti.normalizeObjectClassHandle(ObjectClassHandle(11)) == 11
    assert rti.normalizeInteractionClassHandle(InteractionClassHandle(12)) == 12
    assert rti.normalizeObjectInstanceHandle(ObjectInstanceHandle(13)) == 13

    with pytest.raises(InvalidFederateHandle):
        rti.normalizeFederateHandle(ObjectClassHandle(1))
    with pytest.raises(InvalidObjectClassHandle):
        rti.normalizeObjectClassHandle(FederateHandle(1))
    with pytest.raises(InvalidInteractionClassHandle):
        rti.normalizeInteractionClassHandle(ObjectInstanceHandle(1))
    with pytest.raises(InvalidObjectInstanceHandle):
        rti.normalizeObjectInstanceHandle(InteractionClassHandle(1))
    with pytest.raises(InvalidServiceGroup):
        rti.normalizeServiceGroup("not-a-service-group")

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-MOD-008", "HLA2025-RET-001", "HLA2025-FI-001", "HLA2025-FI-005")
def test_2025_shim_supports_explicit_switch_inquiry_and_control_model() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import RTIinternalError
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-switch-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    rti.joinFederationExecution(
        federateName="SwitchFederate",
        federateType="TestFederate",
        federationName=federation_name,
    )

    assert rti.getObjectClassRelevanceAdvisorySwitch() is False
    assert rti.getAttributeRelevanceAdvisorySwitch() is False
    assert rti.getAttributeScopeAdvisorySwitch() is False
    assert rti.getInteractionRelevanceAdvisorySwitch() is False
    assert rti.getConveyRegionDesignatorSetsSwitch() is True
    assert rti.getServiceReportingSwitch() is False
    assert rti.getExceptionReportingSwitch() is True
    assert rti.getSendServiceReportsToFileSwitch() is False
    assert rti.getAutoProvideSwitch() is True
    assert rti.getDelaySubscriptionEvaluationSwitch() is False
    assert rti.getAdvisoriesUseKnownClassSwitch() is True
    assert rti.getAllowRelaxedDDMSwitch() is False
    assert rti.getNonRegulatedGrantSwitch() is False

    rti.setObjectClassRelevanceAdvisorySwitch(True)
    rti.setAttributeRelevanceAdvisorySwitch(True)
    rti.setAttributeScopeAdvisorySwitch(True)
    rti.setInteractionRelevanceAdvisorySwitch(True)
    rti.setConveyRegionDesignatorSetsSwitch(False)
    rti.setServiceReportingSwitch(True)
    rti.setExceptionReportingSwitch(False)
    rti.setSendServiceReportsToFileSwitch(True)

    assert rti.getObjectClassRelevanceAdvisorySwitch() is True
    assert rti.getAttributeRelevanceAdvisorySwitch() is True
    assert rti.getAttributeScopeAdvisorySwitch() is True
    assert rti.getInteractionRelevanceAdvisorySwitch() is True
    assert rti.getConveyRegionDesignatorSetsSwitch() is False
    assert rti.getServiceReportingSwitch() is True
    assert rti.getExceptionReportingSwitch() is False
    assert rti.getSendServiceReportsToFileSwitch() is True

    with pytest.raises(RTIinternalError, match="requires a bool"):
        rti.setServiceReportingSwitch("yes")
    with pytest.raises(RTIinternalError, match="does not implement"):
        rti.enableObjectClassRelevanceAdvisorySwitch()

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-NEW-002", "HLA2025-FI-001", "HLA2025-FI-005")
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
        fomModule="TargetRadarFOMmodule.xml",
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


@pytest.mark.requirements("HLA2025-FI-005", "HLA2025-FI-006")
def test_2025_shim_validates_callback_model_and_credentials_at_connect() -> None:
    from hla.rti1516_2025.auth import HLAplainTextPassword
    from hla.rti1516_2025.datatypes import Credentials
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import InvalidCredentials, UnsupportedCallbackModel
    from hla.rti1516_2025.factory import create_rti_ambassador

    rti = create_rti_ambassador(backend="shim")
    with pytest.raises(UnsupportedCallbackModel):
        rti.connect(object(), 99)

    with pytest.raises(InvalidCredentials, match="cannot be empty"):
        rti.connect(object(), CallbackModel.HLA_EVOKED, credentials=HLAplainTextPassword(""))

    with pytest.raises(InvalidCredentials, match="rejected"):
        rti.connect(object(), CallbackModel.HLA_EVOKED, credentials=HLAplainTextPassword("bad"))

    rti.connect(object(), CallbackModel.HLA_IMMEDIATE, credentials=Credentials("Proto2025Bearer", b"token"))
    assert rti.connected is True
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FR-001", "HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-FI-009")
def test_2025_shim_requires_valid_fom_modules_and_default_logical_time() -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import CouldNotCreateLogicalTimeFactory, InvalidFOM
    from hla.rti1516_2025.factory import create_rti_ambassador

    federation_name = f"shim-fom-{uuid.uuid4().hex[:8]}"
    rti = create_rti_ambassador(backend="shim")
    rti.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(InvalidFOM, match="At least one FOM module"):
        rti.createFederationExecution(federationName=f"{federation_name}-missing-fom")

    with pytest.raises(CouldNotCreateLogicalTimeFactory, match="NoSuchTimeFactory"):
        rti.createFederationExecution(
            federationName=f"{federation_name}-bad-time",
            fomModule="TargetRadarFOMmodule.xml",
            logicalTimeImplementationName="NoSuchTimeFactory",
        )

    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    reporter = Recording2025FederateAmbassador()
    observer = create_rti_ambassador(backend="shim")
    observer.connect(reporter, CallbackModel.HLA_EVOKED)
    observer.listFederationExecutions()

    execution_report = reporter.last_callback("reportFederationExecutions")
    assert execution_report is not None
    assert any(
        row.federationExecutionName == federation_name
        and row.logicalTimeImplementationName == "HLAinteger64Time"
        for row in execution_report[0]
    )

    rti.destroyFederationExecution(federationName=federation_name)
    observer.disconnect()
    rti.disconnect()


@pytest.mark.requirements("HLA2025-FI-005", "HLA2025-FI-008", "HLA2025-OMT-007")
def test_2025_shim_rejects_invalid_join_fom_modules_and_destroy_while_joined(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import DesignatorIsHLAstandardMIM, ErrorReadingFOM, FederatesCurrentlyJoined
    from hla.rti1516_2025.factory import create_rti_ambassador

    broken_fom = tmp_path / "BrokenProto2025.xml"
    broken_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Broken Proto2025</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>BrokenEntity</name>
        <attribute><name>BadField</name><dataType>DoesNotExist</dataType></attribute>
      </objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )

    federation_name = f"shim-join-fom-{uuid.uuid4().hex[:8]}"
    leader = create_rti_ambassador(backend="shim")
    wing = create_rti_ambassador(backend="shim")
    leader.connect(object(), CallbackModel.HLA_EVOKED)
    wing.connect(object(), CallbackModel.HLA_EVOKED)

    with pytest.raises(DesignatorIsHLAstandardMIM):
        leader.createFederationExecutionWithMIM(
            federationName=f"{federation_name}-bad-mim",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule="HLAstandardMIM",
        )

    leader.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
    )
    leader.joinFederationExecution(
        federateName="Leader",
        federateType="TestFederate",
        federationName=federation_name,
    )

    with pytest.raises(ErrorReadingFOM):
        wing.joinFederationExecution(
            federateName="Wing",
            federateType="TestFederate",
            federationName=federation_name,
            additionalFomModules=[broken_fom],
        )

    with pytest.raises(FederatesCurrentlyJoined):
        leader.destroyFederationExecution(federationName=federation_name)

    leader.disconnect()
    wing.disconnect()


@pytest.mark.requirements("HLA2025-MOD-002", "HLA2025-MOD-003", "HLA2025-FI-008", "HLA2025-OMT-007")
def test_2025_shim_distinguishes_fom_mim_open_read_invalid_and_merge_errors(tmp_path: Path) -> None:
    from hla.rti1516_2025.enums import CallbackModel
    from hla.rti1516_2025.exceptions import (
        CouldNotOpenFOM,
        CouldNotOpenMIM,
        ErrorReadingFOM,
        ErrorReadingMIM,
        InconsistentFOM,
        InvalidFOM,
        InvalidMIM,
    )
    from hla.rti1516_2025.factory import create_rti_ambassador

    def write_module(path: Path, name: str, representation: str) -> Path:
        path.write_text(
            f"""<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>SharedType</name><representation>{representation}</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
""",
            encoding="utf-8",
        )
        return path

    rti = create_rti_ambassador(backend="shim")
    rti.connect(Recording2025FederateAmbassador(), CallbackModel.HLA_EVOKED)

    with pytest.raises(CouldNotOpenFOM):
        rti.createFederationExecution(
            federationName=f"missing-fom-{uuid.uuid4().hex[:8]}",
            fomModule=tmp_path / "missing-fom.xml",
        )
    with pytest.raises(CouldNotOpenMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"missing-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=tmp_path / "missing-mim.xml",
        )

    bad_fom = tmp_path / "bad-fom.xml"
    bad_fom.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingFOM):
        rti.createFederationExecution(
            federationName=f"bad-fom-{uuid.uuid4().hex[:8]}",
            fomModule=bad_fom,
        )

    bad_mim = tmp_path / "bad-mim.xml"
    bad_mim.write_text("<not-an-object-model/>", encoding="utf-8")
    with pytest.raises(ErrorReadingMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"bad-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=bad_mim,
        )

    invalid_name_fom = tmp_path / "invalid-name-fom.xml"
    invalid_name_fom.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Invalid Name FOM</name><type>FOM</type></modelIdentification>
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass><name>hlaReservedUserClass</name></objectClass>
    </objectClass>
  </objects>
</objectModel>
""",
        encoding="utf-8",
    )
    with pytest.raises(InvalidFOM, match="reserved"):
        rti.createFederationExecution(
            federationName=f"invalid-fom-{uuid.uuid4().hex[:8]}",
            fomModule=invalid_name_fom,
        )

    with pytest.raises(InvalidMIM):
        rti.createFederationExecutionWithMIM(
            federationName=f"invalid-mim-{uuid.uuid4().hex[:8]}",
            fomModules=["TargetRadarFOMmodule.xml"],
            mimModule=None,
        )

    conflict_a = write_module(tmp_path / "conflict-a.xml", "Conflict A", "HLAinteger32BE")
    conflict_b = write_module(tmp_path / "conflict-b.xml", "Conflict B", "HLAinteger64BE")
    with pytest.raises(InconsistentFOM, match="Conflicting simple datatype definition"):
        rti.createFederationExecution(
            federationName=f"conflicting-fom-{uuid.uuid4().hex[:8]}",
            fomModules=[conflict_a, conflict_b],
        )

    rti.disconnect()


@pytest.mark.requirements("HLA2025-FR-010", "HLA2025-FI-005", "HLA2025-FI-009")
def test_2025_shim_uses_selected_logical_time_factory_for_queries_and_grants() -> None:
    from hla.rti1516_2025.enums import CallbackModel, ResignAction
    from hla.rti1516_2025.exceptions import TimeRegulationIsNotEnabled
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.rti1516_2025.time import HLAfloat64Interval, HLAfloat64Time

    federation_name = f"shim-time-{uuid.uuid4().hex[:8]}"
    federate = Recording2025FederateAmbassador()
    rti = create_rti_ambassador(backend="shim")
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    rti.createFederationExecution(
        federationName=federation_name,
        fomModule="TargetRadarFOMmodule.xml",
        logicalTimeImplementationName="HLAfloat64Time",
    )
    rti.joinFederationExecution(
        federateName="Clock",
        federateType="TestFederate",
        federationName=federation_name,
    )

    time_factory = rti.getTimeFactory()
    assert time_factory.getName() == "HLAfloat64Time"
    assert rti.queryLogicalTime() == HLAfloat64Time(0.0)
    assert rti.queryGALT().timeIsValid is True
    assert rti.queryGALT().time == HLAfloat64Time(0.0)
    assert rti.queryLITS().time == HLAfloat64Time(0.0)

    with pytest.raises(TimeRegulationIsNotEnabled):
        rti.queryLookahead()

    rti.enableTimeRegulation(HLAfloat64Interval(0.5))
    rti.enableTimeConstrained()
    assert rti.queryLookahead() == HLAfloat64Interval(0.5)
    rti.modifyLookahead(HLAfloat64Interval(0.25))
    assert rti.queryLookahead() == HLAfloat64Interval(0.25)

    rti.timeAdvanceRequest(HLAfloat64Time(12.5))
    assert rti.queryLogicalTime() == HLAfloat64Time(12.5)
    assert federate.last_callback("timeRegulationEnabled") == (HLAfloat64Time(0.0),)
    assert federate.last_callback("timeConstrainedEnabled") == (HLAfloat64Time(0.0),)
    assert federate.last_callback("timeAdvanceGrant") == (HLAfloat64Time(12.5),)

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution(federationName=federation_name)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_2010_and_2025_backend_selection_do_not_cross_wire() -> None:
    from hla.rti import create_rti_ambassador

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        create_rti_ambassador(spec="2025", backend="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        create_rti_ambassador(spec="rti1516e", backend="shim")
