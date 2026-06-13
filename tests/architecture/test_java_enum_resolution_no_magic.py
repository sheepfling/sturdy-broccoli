from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py",
    ROOT / "packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py",
]


def test_java_enum_resolution_does_not_walk_members_by_name() -> None:
    violations: list[str] = []
    forbidden = (
        "return getattr(enum_class, member_name)",
        "for part in enum_class_name.split(\".\")",
        "return getattr(current, member_name)",
    )
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
        if "invoke_java_enum_constant(" not in text:
            violations.append(f"{path.relative_to(ROOT).as_posix()}: missing invoke_java_enum_constant")

    assert not violations, "\n".join(violations)
