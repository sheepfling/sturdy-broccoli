from __future__ import annotations

import pytest

from workspace_auth import AuthConfig
from workspace_runtime import HlaRuntimeFactory


def test_factory_returns_matching_authentication_context(fake_runtime_config: dict[str, object]) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    auth = factory.create_authentication_context(AuthConfig(mode='NoAuth'))

    assert auth.edition == fake_runtime_config['edition']
    assert auth.provider == fake_runtime_config['provider']
    assert auth.credential_provider is not None
####


def test_no_auth_provider_returns_hla_no_credentials_for_2025() -> None:
    factory = HlaRuntimeFactory.select(edition='1516-2025', provider='fake', transport='inproc')
    auth = factory.create_authentication_context(AuthConfig(mode='NoAuth'))

    credentials = auth.credential_provider.get_credentials()

    assert credentials.type == 'HLAnoCredentials'
    assert credentials.data == b''
####


def test_2010_profile_rejects_standard_credentials() -> None:
    factory = HlaRuntimeFactory.select(edition='1516e-2010', provider='fake', transport='inproc')

    with pytest.raises(Exception, match='2010|standard credentials|unsupported'):
        factory.create_authentication_context(AuthConfig(mode='PlainTextPassword', password='secret'))
    ####
####


def test_secret_redaction_in_repr_logs_and_evidence() -> None:
    factory = HlaRuntimeFactory.select(edition='1516-2025', provider='fake', transport='inproc')
    auth = factory.create_authentication_context(AuthConfig(mode='PlainTextPassword', password='secret-value'))

    assert 'secret-value' not in repr(auth)
    assert 'secret-value' not in auth.credential_provider.redact().model_dump_json()
####
