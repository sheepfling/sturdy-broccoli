from __future__ import annotations

import inspect
from pathlib import Path

from hla2010.spec import RTIambassadorSpec
from hla2010.raw_api import API_METADATA
from hla2010.spec import FederateAmbassadorSpec, lower_camel_to_snake
from hla2010_rti_backend_common import DelegatingRTIAmbassador


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_FILES = [
    ROOT / "packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/base.py",
    ROOT / "packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/recording.py",
    ROOT / "packages/hla2010-spec/src/hla2010/api.py",
    ROOT / "packages/hla2010-spec/src/hla2010/runtime_api.py",
    ROOT / "packages/hla2010-spec/src/hla2010/_spec_impl.py",
]


def test_public_runtime_adapter_does_not_mutate_abc_internals() -> None:
    violations: list[str] = []
    for path in RUNTIME_FILES:
        text = path.read_text(encoding="utf-8")
        if "__abstractmethods__" in text:
            violations.append(path.relative_to(ROOT).as_posix())

    assert not violations, "\n".join(violations)


def test_public_runtime_adapter_does_not_use_dunder_method_routing() -> None:
    violations: list[str] = []
    forbidden = (
        "def __getattribute__",
        "def __getattr__",
    )
    for path in RUNTIME_FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")

    assert not violations, "\n".join(violations)


def test_public_runtime_adapter_does_not_patch_methods_with_setattr() -> None:
    violations: list[str] = []
    forbidden = (
        "setattr(DelegatingRTIAmbassador",
        "setattr(RTIambassadorSpec",
        "setattr(FederateAmbassadorSpec",
    )
    for path in RUNTIME_FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")

    assert not violations, "\n".join(violations)


def test_delegating_runtime_adapter_does_not_rely_on_runtime_alias_mixin() -> None:
    text = (ROOT / "packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/base.py").read_text(encoding="utf-8")
    assert "PythonicRTIAmbassadorMixin" not in text


def test_runtime_api_does_not_define_a_separate_alias_mixin_class() -> None:
    text = (ROOT / "packages/hla2010-spec/src/hla2010/runtime_api.py").read_text(encoding="utf-8")
    assert "class PythonicRTIAmbassadorMixin" not in text
    assert "PythonicRTIAmbassadorMixin" not in text


def test_runtime_api_compatibility_wrapper_does_not_reexport_removed_alias_mixin() -> None:
    text = (ROOT / "packages/hla2010-spec/src/hla2010/api.py").read_text(encoding="utf-8")
    assert "PythonicRTIAmbassadorMixin" not in text


def test_typed_runtime_alias_slice_does_not_expose_varargs() -> None:
    checked_methods = (
        (RTIambassadorSpec, "connect"),
        (RTIambassadorSpec, "createFederationExecution"),
        (RTIambassadorSpec, "create_federation_execution"),
        (RTIambassadorSpec, "destroyFederationExecution"),
        (RTIambassadorSpec, "destroy_federation_execution"),
        (RTIambassadorSpec, "disconnect"),
        (RTIambassadorSpec, "getHLAversion"),
        (RTIambassadorSpec, "get_hla_version"),
        (RTIambassadorSpec, "joinFederationExecution"),
        (RTIambassadorSpec, "join_federation_execution"),
        (RTIambassadorSpec, "resignFederationExecution"),
        (RTIambassadorSpec, "resign_federation_execution"),
        (RTIambassadorSpec, "timeAdvanceRequest"),
        (RTIambassadorSpec, "time_advance_request"),
        (DelegatingRTIAmbassador, "connect"),
        (DelegatingRTIAmbassador, "createFederationExecution"),
        (DelegatingRTIAmbassador, "create_federation_execution"),
        (DelegatingRTIAmbassador, "destroyFederationExecution"),
        (DelegatingRTIAmbassador, "destroy_federation_execution"),
        (DelegatingRTIAmbassador, "disconnect"),
        (DelegatingRTIAmbassador, "getHLAversion"),
        (DelegatingRTIAmbassador, "get_hla_version"),
        (DelegatingRTIAmbassador, "joinFederationExecution"),
        (DelegatingRTIAmbassador, "join_federation_execution"),
        (DelegatingRTIAmbassador, "resignFederationExecution"),
        (DelegatingRTIAmbassador, "resign_federation_execution"),
        (DelegatingRTIAmbassador, "timeAdvanceRequest"),
        (DelegatingRTIAmbassador, "time_advance_request"),
    )
    violations: list[str] = []
    for owner, method_name in checked_methods:
        signature = inspect.signature(getattr(owner, method_name))
        for parameter in signature.parameters.values():
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                violations.append(f"{owner.__name__}.{method_name}: {parameter}")
        if signature.return_annotation in (inspect.Signature.empty, object, "object", "Any"):
            violations.append(f"{owner.__name__}.{method_name}: untyped return")

    assert not violations, "\n".join(violations)


def test_public_hla_interface_contracts_do_not_expose_varargs_or_untyped_returns() -> None:
    checked_methods: list[tuple[type[object], str]] = []
    for method_name in API_METADATA["RTIambassador"]:
        checked_methods.append((RTIambassadorSpec, method_name))
        checked_methods.append((DelegatingRTIAmbassador, method_name))
        snake_name = lower_camel_to_snake(method_name)
        if snake_name != method_name:
            checked_methods.append((RTIambassadorSpec, snake_name))
            checked_methods.append((DelegatingRTIAmbassador, snake_name))
    for method_name in API_METADATA["FederateAmbassador"]:
        checked_methods.append((FederateAmbassadorSpec, method_name))
        snake_name = lower_camel_to_snake(method_name)
        if snake_name != method_name:
            checked_methods.append((FederateAmbassadorSpec, snake_name))

    violations: list[str] = []
    for owner, method_name in checked_methods:
        method = getattr(owner, method_name, None)
        if method is None:
            violations.append(f"{owner.__name__}.{method_name}: missing")
            continue
        signature = inspect.signature(method)
        for parameter in signature.parameters.values():
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                violations.append(f"{owner.__name__}.{method_name}: {parameter}")
        if signature.return_annotation in (inspect.Signature.empty, object, "object", "Any"):
            violations.append(f"{owner.__name__}.{method_name}: untyped return")

    assert not violations, "\n".join(violations)


def test_generated_hla_interface_contract_outputs_are_current() -> None:
    import subprocess

    result = subprocess.run(
        ["python3", "scripts/generate_hla_interface_contracts.py", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
