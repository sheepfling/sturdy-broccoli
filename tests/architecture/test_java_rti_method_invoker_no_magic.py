from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_shim_backend.py",
    ROOT / "packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py",
    ROOT / "packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py",
]


def test_java_rti_bridge_calls_do_not_use_runtime_getattr_lookup() -> None:
    violations: list[str] = []
    forbidden = ("getattr(obj, method_name)(*args)",)
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
        if "invoke_java_rti_method(" not in text:
            violations.append(f"{path.relative_to(ROOT).as_posix()}: missing invoke_java_rti_method")

    assert not violations, "\n".join(violations)
