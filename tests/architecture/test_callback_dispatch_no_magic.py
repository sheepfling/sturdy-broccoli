from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "packages/hla2010-spec/src/hla2010/ambassadors.py",
    ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/callbacks.py",
    ROOT / "packages/hla2010-rti-java-common/src/hla2010_rti_java_common/java_common.py",
]


def test_core_callback_dispatch_does_not_use_runtime_getattr_lookup() -> None:
    forbidden = (
        "getattr(ambassador, method_name)",
        "getattr(target.ambassador, method_name)",
        "getattr(self.ambassador, method_name)",
    )
    violations: list[str] = []
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")

    assert not violations, "\n".join(violations)
