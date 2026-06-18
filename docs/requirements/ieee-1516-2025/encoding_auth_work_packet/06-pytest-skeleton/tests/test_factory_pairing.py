from __future__ import annotations

import pytest

from workspace_auth import AuthConfig
from workspace_runtime import HlaRuntimeFactory


def test_runtime_context_contains_rti_encoding_and_auth() -> None:
    factory = HlaRuntimeFactory.select(edition='1516-2025', provider='fake', transport='inproc')
    runtime = factory.create_runtime_context(auth_config=AuthConfig(mode='NoAuth'))

    assert runtime.rti_ambassador is not None
    assert runtime.encoding_context is not None
    assert runtime.authentication_context is not None
    assert runtime.edition == '1516-2025'
####


def test_incompatible_auth_fails_at_factory() -> None:
    factory = HlaRuntimeFactory.select(edition='1516e-2010', provider='fake', transport='inproc')

    with pytest.raises(Exception, match='unsupported|2010|credentials'):
        factory.create_runtime_context(auth_config=AuthConfig(mode='PlainTextPassword', password='secret'))
    ####
####


def test_bad_auth_fails_before_federation_created() -> None:
    factory = HlaRuntimeFactory.select(edition='1516-2025', provider='fake', transport='inproc')
    runtime = factory.create_runtime_context(auth_config=AuthConfig(mode='PlainTextPassword', password='bad'))

    with pytest.raises(Exception, match='InvalidCredentials|Unauthorized'):
        runtime.connect()
    ####

    assert runtime.rti_ambassador.calls.count('createFederationExecution') == 0
    assert runtime.rti_ambassador.calls.count('joinFederationExecution') == 0
####
