"""Federation/bootstrap helper semantics for the dedicated Python 2025 lane."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.exceptions import (
    CouldNotCreateLogicalTimeFactory,
    CouldNotOpenFOM,
    CouldNotOpenMIM,
    ErrorReadingFOM,
    ErrorReadingMIM,
    InconsistentFOM,
    InvalidCredentials,
    InvalidFOM,
    InvalidMIM,
    RTIinternalError,
    Unauthorized,
    UnsupportedCallbackModel,
)


def extract_federation_name(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    federation_name = kwargs.get("federationName")
    if federation_name is None:
        federation_name = kwargs.get("federation_name")
    if federation_name is None:
        if len(args) >= 3:
            federation_name = args[2]
        elif len(args) >= 2:
            federation_name = args[1]
        elif args:
            federation_name = args[0]
    if not isinstance(federation_name, str) or not federation_name:
        raise RTIinternalError("2025 Python RTI ambassador requires a federation name")
    return federation_name


def extract_create_federation_name(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    federation_name = kwargs.get("federationName")
    if federation_name is None:
        federation_name = kwargs.get("federation_name")
    if federation_name is None and args:
        federation_name = args[0]
    if not isinstance(federation_name, str) or not federation_name:
        raise RTIinternalError("2025 Python RTI ambassador requires a federation name")
    return federation_name


def extract_join_names(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[str, str | None]:
    federation_name = extract_federation_name(args, kwargs)
    federate_name = kwargs.get("federateName")
    if federate_name is None:
        federate_name = kwargs.get("federate_name")
    if federate_name is None and len(args) >= 3:
        federate_name = args[0]
    if federate_name is not None and not isinstance(federate_name, str):
        raise RTIinternalError("2025 Python RTI ambassador requires federateName to be a string when provided")
    return federation_name, federate_name


def extract_federate_type(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    federate_type = kwargs.get("federateType")
    if federate_type is None:
        federate_type = kwargs.get("federate_type")
    if federate_type is None and len(args) >= 2:
        federate_type = args[1]
    if not isinstance(federate_type, str) or not federate_type:
        raise RTIinternalError("2025 Python RTI ambassador requires federateType to be a non-empty string")
    return federate_type


def extract_logical_time_implementation_name(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    supported_logical_time_implementations: frozenset[str],
    default_logical_time_implementation: str,
) -> str:
    value = kwargs.get("logicalTimeImplementationName")
    if value is None:
        value = kwargs.get("logical_time_implementation_name")
    if value is None and len(args) >= 4:
        value = args[3]
    if value is None and len(args) == 3 and not isinstance(args[2], (list, tuple, set, frozenset)):
        value = args[2]
    if value is None:
        return default_logical_time_implementation
    if not isinstance(value, str):
        raise RTIinternalError("2025 Python RTI ambassador requires logicalTimeImplementationName to be a string")
    if value not in supported_logical_time_implementations:
        raise CouldNotCreateLogicalTimeFactory(value)
    return value


def extract_fom_sources(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    *,
    with_mim: bool,
) -> tuple[Any, ...]:
    fom_module = kwargs.get("fomModule")
    fom_modules = kwargs.get("fomModules")
    if fom_module is not None and fom_modules is not None:
        raise InvalidFOM("Use either fomModule or fomModules, not both")
    if fom_module is not None:
        return (fom_module,)
    if fom_modules is not None:
        return normalize_module_sources(fom_modules)
    if with_mim:
        if len(args) >= 2:
            return normalize_module_sources(args[1])
        return ()
    if len(args) >= 2:
        return normalize_module_sources(args[1])
    return ()


def extract_mim_source(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any | None:
    mim_source = kwargs.get("mimModule")
    if mim_source is None:
        mim_source = kwargs.get("mim_module")
    if mim_source is None and len(args) >= 3:
        mim_source = args[2]
    return mim_source


def extract_additional_fom_modules(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any, ...]:
    additional = kwargs.get("additionalFomModules")
    if additional is None:
        additional = kwargs.get("additional_fom_modules")
    if additional is None and len(args) >= 4:
        additional = args[3]
    if additional is None:
        return ()
    return normalize_module_sources(additional)


def normalize_module_sources(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray, memoryview, Path)):
        return (value,)
    return tuple(value)


def coerce_callback_model(value: Any) -> CallbackModel:
    try:
        if isinstance(value, CallbackModel):
            return value
        member_name = getattr(value, "name", "")
        if member_name in CallbackModel.__members__:
            return CallbackModel[member_name]
        return CallbackModel(value)
    except Exception as exc:
        raise UnsupportedCallbackModel(repr(value)) from exc


def validate_credentials(credentials: Any | None) -> None:
    if credentials is None:
        return
    credential_type = getattr(credentials, "type", None)
    credential_data = getattr(credentials, "data", None)
    if not isinstance(credential_type, str) or credential_data is None:
        raise InvalidCredentials("Credentials must expose type and data fields")
    if credential_type == "HLAnoCredentials":
        if bytes(credential_data) != b"":
            raise InvalidCredentials("HLAnoCredentials must not carry credential bytes")
        return
    if credential_type == "HLAplainTextPassword":
        auth_module = import_module("hla.rti1516_2025.auth")
        try:
            password = auth_module.HLAplainTextPassword(bytes(credential_data)).decode()
        except Exception as exc:
            raise InvalidCredentials("Encoded HLAplainTextPassword is malformed") from exc
        if not password:
            raise InvalidCredentials("HLAplainTextPassword cannot be empty")
        if password == "bad":
            raise InvalidCredentials("Credential provider rejected HLAplainTextPassword")
        return
    if not credential_type.strip():
        raise InvalidCredentials("Custom credentials must declare a non-empty type")
    if not isinstance(credential_data, (bytes, bytearray, memoryview)):
        raise Unauthorized("Custom credentials must provide byte payloads")


def resolve_fom_modules(sources: tuple[Any, ...], *, mim: bool) -> tuple[Any, ...]:
    fom = import_module("hla.rti1516e.fom")
    try:
        modules = fom.FOMResolver(require_local_parse=True).resolve_many(sources)
        if not mim:
            validation = import_module("hla.rti1516_2025.validation")
            issues = validation.validate_fom_modules(modules)
            if issues:
                raise InvalidFOM(issues[0].message)
        return modules
    except fom.FOMResolutionError as exc:
        kind = getattr(exc, "kind", "open")
        if mim:
            if kind == "read":
                raise ErrorReadingMIM(str(exc)) from exc
            raise CouldNotOpenMIM(str(exc)) from exc
        if kind == "read":
            raise ErrorReadingFOM(str(exc)) from exc
        raise CouldNotOpenFOM(str(exc)) from exc
    except InvalidFOM:
        raise
    except Exception as exc:
        if mim:
            raise InvalidMIM(str(exc)) from exc
        raise InvalidFOM(str(exc)) from exc


def merge_fom_modules(modules: tuple[Any, ...], *, mim_module: Any) -> Any:
    fom = import_module("hla.rti1516e.fom")
    try:
        return fom.merge_fom_modules(modules, mim_module=mim_module)
    except fom.FOMMergeError as exc:
        raise InconsistentFOM(str(exc)) from exc


def standard_mim_module() -> Any:
    fom = import_module("hla.rti1516e.fom")
    return fom.standard_mim_module()


def get_time_factory(name: str) -> Any:
    time = import_module("hla.rti1516_2025.time")
    return time.get_logical_time_factory(name)


def select_logical_time_implementation(backend: Any, name: str) -> None:
    backend._logical_time_implementation_name = name
    backend._logical_time_factory = get_time_factory(name)
    backend._logical_time = backend._logical_time_factory.makeInitial()
    backend._lookahead = backend._logical_time_factory.makeZero()
    backend._time_regulation_enabled = False
    backend._time_constrained_enabled = False
    backend._last_reflect_logical_times.clear()


__all__ = [
    "coerce_callback_model",
    "extract_additional_fom_modules",
    "extract_create_federation_name",
    "extract_federate_type",
    "extract_federation_name",
    "extract_fom_sources",
    "extract_join_names",
    "extract_logical_time_implementation_name",
    "extract_mim_source",
    "get_time_factory",
    "merge_fom_modules",
    "normalize_module_sources",
    "resolve_fom_modules",
    "select_logical_time_implementation",
    "standard_mim_module",
    "validate_credentials",
]
