from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = ROOT / "packages/hla-backend-inmemory/src/hla/backends/inmemory/backend.py"


def test_python_rti_backend_does_not_lookup_service_handlers_by_name_convention() -> None:
    text = BACKEND_PATH.read_text(encoding="utf-8")
    assert 'getattr(self, f"_svc_{invocation.method_name}"' not in text
    assert '"_svc_{invocation.method_name}"' not in text
