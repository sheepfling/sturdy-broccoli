from __future__ import annotations

import pytest


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004")
def test_hla_factory_registry_composes_2025_helpers_without_ambassador_ownership() -> None:
    from hla.rti import HlaFactoryRegistry
    from hla.rti1516_2025 import BasicEncoderFactory, CallbackModel
    from hla.rti1516_2025.auth import HLAnoCredentials

    factory = HlaFactoryRegistry.get("ieee1516e-2025", provider="shim")
    codecs = factory.encoding_registry()
    auth = factory.auth_provider({"credentials": HLAnoCredentials()})
    capabilities = factory.edition_capabilities()

    assert isinstance(codecs, BasicEncoderFactory)
    assert auth.authorize(HLAnoCredentials()) is True
    assert capabilities.spec_name == "rti1516_2025"
    assert capabilities.provider == "shim"
    assert capabilities.encoding == "hla.rti1516_2025.BasicEncoderFactory"
    assert "fedpro" in capabilities.capabilities

    rti = factory.create_rti_ambassador(auth=auth)
    assert rti.backend_info.details["spec"] == "rti1516_2025"
    assert "encoding_registry" not in vars(rti)
    assert "auth_provider" not in vars(rti)
    rti.connect(factory.create_federate_ambassador_proxy(), CallbackModel.HLA_EVOKED)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FR-001", "HLA2025-OMT-002")
def test_2025_version_local_factory_uses_same_composition_layer() -> None:
    from hla.rti1516_2025.factory import create_hla_factory
    from hla.rti1516_2025.foms import scenario_fom_paths

    factory = create_hla_factory(provider="shim")
    assert factory.spec.name == "rti1516_2025"
    assert factory.provider == "shim"
    result = factory.load_fom(scenario_fom_paths("message-test"))

    assert result.status == "validated"
    assert result.repository is not None
    assert result.repository.has("Proto2025Verdict")
    assert any(entry == "modules=2" for entry in result.diagnostics)


@pytest.mark.requirements("HLA2025-OMT-005", "HLA2025-OMT-006")
def test_2025_factory_can_run_strict_identification_validation_on_packaged_foms() -> None:
    from hla.rti1516_2025.factory import create_hla_factory
    from hla.rti1516_2025.foms import scenario_fom_paths

    factory = create_hla_factory(provider="shim")
    result = factory.load_fom(
        scenario_fom_paths("message-test"),
        strict_identification=True,
    )

    assert result.status == "validated"
    assert result.strict_identification is True
    assert result.validation_issues == ()
    assert any(entry == "strict_identification=true" for entry in result.diagnostics)


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_hla_factory_rejects_mismatched_spec_provider_combinations() -> None:
    from hla.rti import HlaFactoryRegistry

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        HlaFactoryRegistry.get("2025", provider="inmemory")

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516e'"):
        HlaFactoryRegistry.get("rti1516e", provider="shim")
