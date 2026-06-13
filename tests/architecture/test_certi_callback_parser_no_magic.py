from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CALLBACKS_PATH = ROOT / "packages/hla2010-rti-certi/src/hla2010_rti_certi/certi/callbacks.py"


def test_certi_callback_parser_does_not_use_runtime_getattr_dispatch() -> None:
    text = CALLBACKS_PATH.read_text(encoding="utf-8")
    assert 'getattr(ambassador, "' not in text
    assert "invoke_federate_callback(" in text
