from __future__ import annotations

from pathlib import Path


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
