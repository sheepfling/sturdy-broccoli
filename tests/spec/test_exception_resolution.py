from __future__ import annotations

from hla2010.exceptions import (
    FederationExecutionDoesNotExist,
    RTIinternalError,
    resolve_rti_exception_type,
)


def test_resolve_rti_exception_type_returns_named_hla_exception() -> None:
    assert resolve_rti_exception_type("FederationExecutionDoesNotExist") is FederationExecutionDoesNotExist


def test_resolve_rti_exception_type_falls_back_to_internal_error() -> None:
    assert resolve_rti_exception_type("NotARealHLAException") is RTIinternalError
