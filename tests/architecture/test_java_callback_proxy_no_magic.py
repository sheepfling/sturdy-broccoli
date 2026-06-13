from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_shim_runtime.py",
    ROOT / "packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_shim_backend.py",
    ROOT / "packages/hla2010-rti-certi/src/hla2010_rti_certi/certi_java/adapter.py",
]


def test_java_proxy_callback_paths_do_not_use_runtime_getattr_lookup() -> None:
    violations: list[str] = []
    forbidden = (
        "getattr(self.federate, method_name)",
        "getattr(self._java_proxy, method_name)",
    )
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")

    assert not violations, "\n".join(violations)
