from __future__ import annotations

import math
from pathlib import Path

import pytest
from hla.rti import HlaFactoryRegistry
from hla.rti1516_2025.auth import HLAnoCredentials, HLAplainTextPassword
from hla.rti1516_2025.datatypes import Credentials
from hla.rti1516_2025.exceptions import InvalidCredentials
from hla.rti1516_2025.foms import FomTypeRepository, encoding_smoke_fom_path
from hla.rti1516e.fom import FOMResolver


@pytest.mark.requirements("HLA-X-2025-FI-003", "HLA-X-2025-FI-004")
def test_factory_returns_matching_encoding_and_auth_contexts() -> None:
    factory = HlaFactoryRegistry.get("ieee1516e-2025", provider="shim")

    encoding = factory.create_encoding_context(transport="inproc")
    auth = factory.create_authentication_context({"mode": "NoAuth"}, transport="inproc")
    runtime = factory.create_runtime_context(auth_config={"mode": "NoAuth"}, transport="inproc")

    assert encoding.edition == "rti1516_2025"
    assert auth.edition == "rti1516_2025"
    assert runtime.edition == "rti1516_2025"
    assert runtime.encoding_context.registry.has("HLAinteger32BE")
    assert isinstance(auth.credentials(), HLAnoCredentials)
    assert runtime.capability_report()["auth"]["supports_standard_credentials"] is True


@pytest.mark.requirements("ENC-001", "ENC-004", "HLA-X-2025-OMT-002")
def test_encoding_context_exposes_fom_type_repository_and_capabilities() -> None:
    path = encoding_smoke_fom_path()
    encoding = HlaFactoryRegistry.get("2025", provider="shim").create_encoding_context(
        transport="inproc",
        fom_modules=[path],
    )
    report = encoding.capability_report()

    assert isinstance(encoding.repository, FomTypeRepository)
    assert encoding.repository.has("TrackState")
    assert encoding.repository.attribute_type("HLAobjectRoot.Track", "State") == "TrackState"
    assert encoding.repository.parameter_type("HLAinteractionRoot.TrackReport", "Contact") == "SensorContact"
    assert report["repository"]["status"] == "loaded"
    assert "TrackState" in report["repository"]["datatypes"]
    assert report["registry"]["supports_extendable_variant_record"] is True


@pytest.mark.requirements("HLA-X-2025-FI-004")
def test_encoding_registry_resolves_required_builtin_codecs_and_rejects_unknowns() -> None:
    registry = HlaFactoryRegistry.get("2025", provider="shim").encoding_registry()
    required = {
        "HLAASCIIchar",
        "HLAASCIIstring",
        "HLAboolean",
        "HLAbyte",
        "HLAfloat32BE",
        "HLAfloat32LE",
        "HLAfloat64BE",
        "HLAfloat64LE",
        "HLAinteger16BE",
        "HLAinteger16LE",
        "HLAinteger32BE",
        "HLAinteger32LE",
        "HLAinteger64BE",
        "HLAinteger64LE",
        "HLAunsignedInteger16BE",
        "HLAunsignedInteger32BE",
        "HLAunsignedInteger64BE",
        "HLAopaqueData",
        "HLAunicodeString",
        "HLAfixedArray",
        "HLAvariableArray",
        "HLAfixedRecord",
        "HLAvariantRecord",
        "HLAextendableVariantRecord",
    }

    assert required <= set(registry.registered_codecs())
    assert registry.get("HLAinteger32BE")(1).toByteArray() == bytes.fromhex("00000001")
    with pytest.raises(KeyError, match="Unknown or unsupported"):
        registry.get("HLAxDefinitelyNotAStandardCodec")


@pytest.mark.requirements("HLA-X-2025-FI-004")
@pytest.mark.parametrize(
    ("codec", "value", "expected_hex"),
    [
        ("HLAinteger16BE", -32768, "8000"),
        ("HLAinteger16LE", 1, "0100"),
        ("HLAinteger32BE", 2147483647, "7fffffff"),
        ("HLAinteger32LE", -1, "ffffffff"),
        ("HLAinteger64BE", 1, "0000000000000001"),
        ("HLAunsignedInteger64BE", 18446744073709551615, "ffffffffffffffff"),
        ("HLAfloat32BE", 1.0, "3f800000"),
        ("HLAfloat64BE", -2.5, "c004000000000000"),
    ],
)
def test_primitive_codecs_match_imported_golden_vectors(codec: str, value: int | float, expected_hex: str) -> None:
    registry = HlaFactoryRegistry.get("2025", provider="shim").encoding_registry()
    encoded = registry.get(codec)(value).toByteArray()
    assert encoded.hex() == expected_hex
    decoded = registry.get(codec)().decode(encoded).getValue()
    if isinstance(value, float):
        assert math.isclose(decoded, value)
    else:
        assert decoded == value


@pytest.mark.requirements("HLA-X-2025-FI-003")
def test_auth_context_supports_2025_credentials_and_rejects_2010_standard_credentials() -> None:
    factory_2025 = HlaFactoryRegistry.get("2025", provider="shim")
    password_auth = factory_2025.create_authentication_context(
        {"mode": "PlainTextPassword", "password": "secret-value"}
    )
    credential = password_auth.credentials()

    assert isinstance(credential, HLAplainTextPassword)
    assert HLAplainTextPassword(credential.data).decode() == "secret-value"
    assert "secret-value" not in repr(password_auth)
    assert password_auth.capability_report()["credential"]["data"] == "<redacted:HLAplainTextPassword>"

    factory_2010 = HlaFactoryRegistry.get("rti1516e", provider="inmemory")
    with pytest.raises(ValueError, match="unsupported for the 1516e-2010 profile"):
        factory_2010.create_authentication_context({"mode": "PlainTextPassword", "password": "secret"})


@pytest.mark.requirements("AUTH-002", "AUTH-003", "AUTH-005")
def test_auth_context_supports_custom_typed_bytes_and_rejects_empty_password() -> None:
    factory = HlaFactoryRegistry.get("2025", provider="shim")
    custom_auth = factory.create_authentication_context(
        {"mode": "CustomTypedBytes", "credential_type": "HLAxBearerToken", "data": b"safe-test-token"}
    )

    credential = custom_auth.credentials()
    assert isinstance(credential, Credentials)
    assert credential.type == "HLAxBearerToken"
    assert credential.data == b"safe-test-token"
    assert custom_auth.capability_report()["credential"]["data"] == "<redacted:HLAxBearerToken>"

    with pytest.raises(InvalidCredentials, match="cannot be empty"):
        factory.create_authentication_context({"mode": "PlainTextPassword", "password": ""})


@pytest.mark.requirements("HLA-X-2025-FI-003", "HLA-X-2025-FI-005")
def test_invalid_credentials_fail_before_rti_connection() -> None:
    runtime = HlaFactoryRegistry.get("2025", provider="shim").create_runtime_context(
        auth_config={"mode": "PlainTextPassword", "password": "bad"}
    )

    with pytest.raises(InvalidCredentials):
        runtime.connect()
    assert getattr(runtime.rti_ambassador, "calls", []).count("connect") == 0


@pytest.mark.requirements("AUTH-001", "AUTH-005", "ENC-001")
def test_runtime_context_writes_redacted_encoding_auth_evidence(tmp_path) -> None:
    runtime = HlaFactoryRegistry.get("2025", provider="shim").create_runtime_context(
        auth_config={"mode": "PlainTextPassword", "password": "secret-value"},
        fom_modules=[encoding_smoke_fom_path()],
    )

    artifacts = runtime.write_evidence(tmp_path)
    encoding_report = Path(artifacts["encoding_capabilities"]).read_text(encoding="utf-8")
    auth_report = Path(artifacts["auth_capabilities"]).read_text(encoding="utf-8")
    runtime_report = Path(artifacts["runtime_matrix"]).read_text(encoding="utf-8")

    assert "TrackState" in encoding_report
    assert "HLAplainTextPassword" in auth_report
    assert "secret-value" not in auth_report
    assert "secret-value" not in runtime_report


@pytest.mark.requirements("AUTH-004", "HLA-X-2025-REQ-001", "HLA-X-2025-REQ-002")
def test_2010_profile_does_not_gain_2025_auth_or_repository_surface() -> None:
    import hla.rti1516e as rti1516e

    factory = HlaFactoryRegistry.get("rti1516e", provider="inmemory")
    encoding = factory.create_encoding_context()
    auth = factory.create_authentication_context({"mode": "NoAuth"})

    assert encoding.edition == "rti1516e"
    assert encoding.repository is None
    assert auth.supports_standard_credentials is False
    assert auth.credentials() is None
    assert auth.capability_report()["allowed_auth_modes"] == ["NoAuth"]
    assert not hasattr(rti1516e, "Credentials")


@pytest.mark.requirements("HLA-X-2025-OMT-002", "HLA-X-2025-OMT-006")
def test_encoding_smoke_fom_resolves_expected_datatype_graph() -> None:
    path = encoding_smoke_fom_path()
    assert Path(path).name == "EncodingSmokeTest-2025.xml"

    module = FOMResolver().resolve(path)

    assert module.simple_datatypes["TrackId"].representation == "HLAinteger32BE"
    assert module.simple_datatypes["Latitude"].representation == "HLAfloat64BE"
    assert [enum.name for enum in module.enumerated_datatypes["SensorKind"].enumerators] == [
        "Radar",
        "Iff",
        "Passive",
    ]
    assert module.array_datatypes["TrackHistory"].data_type == "Position"
    assert module.array_datatypes["FixedFourTrackIds"].cardinality == "4"
    assert [(field.name, field.data_type) for field in module.fixed_record_datatypes["TrackState"].fields] == [
        ("Id", "TrackId"),
        ("Where", "Position"),
        ("Name", "HLAunicodeString"),
    ]
    assert module.variant_record_datatypes["SensorContact"].data_type == "SensorKind"
