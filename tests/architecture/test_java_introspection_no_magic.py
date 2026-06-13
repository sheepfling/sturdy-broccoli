from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_common.py",
    ROOT / "packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py",
    ROOT / "packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py",
]


def test_java_introspection_uses_shared_helpers() -> None:
    violations: list[str] = []
    forbidden = (
        'getattr(obj, "getClass", None)',
        'getattr(class_info, "getName", None)',
        'getattr(class_info, "getSimpleName", None)',
        'getattr(exc, "javaClass", None)',
        'getattr(exc, "java_exception", None)',
        'getattr(obj, "_get_field", None)',
    )
    for path in FILES[1:]:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
    common_text = FILES[0].read_text(encoding="utf-8")
    for required in (
        "java_runtime_full_class_name(",
        "java_runtime_simple_class_name(",
        "java_runtime_public_field(",
        "jpype_exception_class_name(",
        "py4j_exception_class_name(",
        "py4j_exception_message(",
    ):
        if required not in common_text:
            violations.append(f"{FILES[0].relative_to(ROOT).as_posix()}: missing {required}")

    assert not violations, "\n".join(violations)
