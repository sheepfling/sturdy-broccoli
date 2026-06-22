from __future__ import annotations

import pytest

_PROVIDER_ROUTES = ("python2025",)
_PYTHON2025_PROVIDER_ALIASES = ("python2025", "python-2025", "python-2025-backend")


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004")
@pytest.mark.parametrize("provider", _PROVIDER_ROUTES)
def test_hla_factory_registry_composes_2025_helpers_without_ambassador_ownership(provider: str) -> None:
    from hla.rti import HlaFactoryRegistry
    from hla.rti1516_2025 import BasicEncoderFactory, CallbackModel
    from hla.rti1516_2025.auth import HLAnoCredentials

    factory = HlaFactoryRegistry.get("ieee1516e-2025", provider=provider)
    codecs = factory.encoding_registry()
    auth = factory.auth_provider({"credentials": HLAnoCredentials()})
    capabilities = factory.edition_capabilities()

    assert isinstance(codecs, BasicEncoderFactory)
    assert auth.authorize(HLAnoCredentials()) is True
    assert capabilities.spec_name == "rti1516_2025"
    assert capabilities.provider == provider
    assert capabilities.encoding == "hla.rti1516_2025.BasicEncoderFactory"
    assert "fedpro" in capabilities.capabilities

    rti = factory.create_rti_ambassador(auth=auth)
    assert rti.backend_info.details["spec"] == "rti1516_2025"
    assert "encoding_registry" not in vars(rti)
    assert "auth_provider" not in vars(rti)
    rti.connect(factory.create_federate_ambassador_proxy(), CallbackModel.HLA_EVOKED)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003", "HLA2025-FI-004", "HLA2025-MIL-001")
@pytest.mark.parametrize("provider", _PROVIDER_ROUTES)
def test_hla_factory_registry_strips_composition_only_options_before_2025_backend_creation(provider: str) -> None:
    from hla.rti import HlaFactoryRegistry
    from hla.rti1516_2025 import CallbackModel
    from hla.rti1516_2025.auth import HLAnoCredentials

    factory = HlaFactoryRegistry.get("ieee1516e-2025", provider=provider)
    codecs = factory.encoding_registry()
    auth = factory.auth_provider({"credentials": HLAnoCredentials()})

    rti = factory.create_rti_ambassador(
        auth=auth,
        auth_provider=auth,
        encoding_registry=codecs,
    )

    assert rti.backend_info.details["spec"] == "rti1516_2025"
    assert "encoding_registry" not in vars(rti)
    assert "auth_provider" not in vars(rti)
    assert "auth" not in vars(rti)
    rti.connect(factory.create_federate_ambassador_proxy(), CallbackModel.HLA_EVOKED)
    rti.disconnect()


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FR-001", "HLA2025-OMT-002")
@pytest.mark.parametrize("provider", _PROVIDER_ROUTES)
def test_2025_version_local_factory_uses_same_composition_layer(provider: str) -> None:
    from hla.rti1516_2025.factory import create_hla_factory
    from hla.rti1516_2025.foms import scenario_fom_paths

    factory = create_hla_factory(provider=provider)
    assert factory.spec.name == "rti1516_2025"
    assert factory.provider == provider
    result = factory.load_fom(scenario_fom_paths("message-test"))

    assert result.status == "validated"
    assert result.repository is not None
    assert result.repository.has("Proto2025Verdict")
    assert any(entry == "modules=2" for entry in result.diagnostics)


@pytest.mark.requirements("HLA2025-OMT-005", "HLA2025-OMT-006")
@pytest.mark.parametrize("provider", _PROVIDER_ROUTES)
def test_2025_factory_can_run_strict_identification_validation_on_packaged_foms(provider: str) -> None:
    from hla.rti1516_2025.factory import create_hla_factory
    from hla.rti1516_2025.foms import scenario_fom_paths

    factory = create_hla_factory(provider=provider)
    result = factory.load_fom(
        scenario_fom_paths("message-test"),
        strict_identification=True,
    )

    assert result.status == "validated"
    assert result.strict_identification is True
    assert result.validation_issues == ()
    assert any(entry == "strict_identification=true" for entry in result.diagnostics)


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FI-003")
def test_2025_version_local_factory_defaults_to_python2025_provider() -> None:
    from hla.rti1516_2025.factory import create_hla_factory, create_rti_ambassador

    factory = create_hla_factory()
    assert factory.provider == "python2025"

    default_rti = create_rti_ambassador()
    explicit_rti = create_rti_ambassador(backend="python2025")

    assert type(default_rti) is type(explicit_rti)
    assert default_rti.backend_info.details["spec"] == "rti1516_2025"
    assert explicit_rti.backend_info.details["spec"] == "rti1516_2025"


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-BND-003")
@pytest.mark.parametrize("backend_name", _PYTHON2025_PROVIDER_ALIASES)
def test_2025_version_local_factory_accepts_hosted_transport_creation_on_python2025_lane(backend_name: str) -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador
    from hla.backends.python2025.hosted_fedpro import FedPro2025RTIAmbassador

    rti = create_rti_ambassador(backend=backend_name, transport={"kind": "grpc", "target": "127.0.0.1:15164"})

    assert isinstance(rti, FedPro2025RTIAmbassador)
    assert rti.backend_info.details["provider"] == "python2025"
    assert rti.backend_info.details["implementation_lane"] == "hla-backend-python2025"
    assert rti.backend_info.details["counts_as_python_2025_rti"] is True
    rti.close()


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-MIL-003")
def test_2025_version_local_factory_rejects_legacy_shim_provider_name() -> None:
    from hla.rti1516_2025.factory import create_hla_factory, create_rti_ambassador

    with pytest.raises(ValueError, match="Unknown RTI provider: 'shim'"):
        create_hla_factory(provider="shim")

    with pytest.raises(ValueError, match="Unknown RTI backend kind: 'shim'"):
        create_rti_ambassador(backend="shim")


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-BND-003")
def test_2025_version_local_factory_rejects_unknown_backend_specific_options() -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador

    with pytest.raises(
        ValueError,
        match="unsupported backend option\\(s\\) for backend='python2025': engine",
    ):
        create_rti_ambassador(engine="not-supported-for-2025")


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-BND-003")
@pytest.mark.parametrize("provider", _PROVIDER_ROUTES)
def test_2025_direct_factory_rejects_composition_only_options_without_hla_factory_layer(provider: str) -> None:
    from hla.rti1516_2025.factory import create_rti_ambassador

    with pytest.raises(
        ValueError,
        match=rf"unsupported backend option\(s\) for backend='{provider}': auth",
    ):
        create_rti_ambassador(backend=provider, auth=object())


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_hla_factory_rejects_mismatched_spec_provider_combinations() -> None:
    from hla.rti import HlaFactoryRegistry

    with pytest.raises(ValueError, match="does not support HLA spec 'rti1516_2025'"):
        HlaFactoryRegistry.get("2025", provider="inmemory")

    with pytest.raises(ValueError, match="Unknown RTI provider: 'shim'"):
        HlaFactoryRegistry.get("rti1516e", provider="shim")
