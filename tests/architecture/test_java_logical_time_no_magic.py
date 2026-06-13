from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py",
    ROOT / "packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py",
]


def test_java_logical_time_resolution_uses_explicit_helpers() -> None:
    violations: list[str] = []
    forbidden = (
        "rti_ambassador.getTimeFactory()",
        'hasattr(factory, "makeTime")',
        'hasattr(factory, "makeInterval")',
        'getattr(value, "is_zero")',
        'getattr(value, "is_epsilon")',
    )
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
        for required in (
            "convert_python_logical_time_with_factory(",
            "invoke_java_time_factory(",
            "python_logical_time_shim_spec(",
        ):
            if required not in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: missing {required}")

    assert not violations, "\n".join(violations)
