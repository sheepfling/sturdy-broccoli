from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/service_adapter.py",
    ROOT / "packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_common.py",
]


def test_bridge_exception_translation_uses_explicit_resolver() -> None:
    forbidden = (
        '__import__("hla2010.exceptions"',
        "getattr(hla_exceptions, simple_name, None)",
    )
    violations: list[str] = []
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
        if "resolve_rti_exception_type(" not in text:
            violations.append(f"{path.relative_to(ROOT).as_posix()}: missing resolve_rti_exception_type")

    assert not violations, "\n".join(violations)
