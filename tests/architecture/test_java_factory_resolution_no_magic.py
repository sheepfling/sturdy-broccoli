from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/runtime.py",
    ROOT / "packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/runtime.py",
]


def test_java_factory_resolution_does_not_use_runtime_lookup_in_bridge_interfaces() -> None:
    violations: list[str] = []
    forbidden = (
        'getattr(rti_ambassador, factory_method)()',
        'getattr(collection, "add", None)',
    )
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
        for required in (
            "create_java_factory_collection(",
            "append_java_collection_value(",
            "java_handle_set_factory_method(",
            "java_handle_value_map_factory_method(",
            "put_java_map_entry(",
        ):
            if required not in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: missing {required}")

    assert not violations, "\n".join(violations)
