from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER_PATH = ROOT / "packages/hla2010-rti-certi/src/hla2010_rti_certi/certi_java/adapter.py"


def test_certi_java_shim_does_not_use_dunder_routing() -> None:
    text = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "def __getattr__" not in text
    assert "def __getattribute__" not in text


def test_certi_java_shim_does_not_patch_public_methods_with_setattr() -> None:
    text = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "setattr(CERTIJavaRTIShim" not in text
