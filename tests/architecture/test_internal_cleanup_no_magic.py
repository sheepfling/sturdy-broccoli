from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET_RADAR_FACTORY_PATH = (
    ROOT
    / "packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/scenarios/target_radar_factory.py"
)
TARGET_RADAR_SCENARIO_PATH = (
    ROOT
    / "packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/scenarios/target_radar.py"
)
PYTHON_BACKEND_PATH = ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/backend.py"
PYTHON_STATE_PATH = ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/state.py"
CERTI_SUPPORT_PATH = ROOT / "tests/vendors/certi_real_backend_matrix_support.py"


def test_target_radar_factory_uses_explicit_factory_object_and_no_close_monkeypatch() -> None:
    text = TARGET_RADAR_FACTORY_PATH.read_text(encoding="utf-8")
    assert "class TargetRadarFactory" in text
    assert "def make_rti" in text
    assert 'setattr(rti, "close"' not in text


def test_target_radar_scenario_supports_explicit_factory_cleanup() -> None:
    text = TARGET_RADAR_SCENARIO_PATH.read_text(encoding="utf-8")
    assert "class RoleBasedRtiFactory" in text
    assert "def _close_factory" in text


def test_python_backend_uses_explicit_state_backend_field() -> None:
    backend_text = PYTHON_BACKEND_PATH.read_text(encoding="utf-8")
    state_text = PYTHON_STATE_PATH.read_text(encoding="utf-8")
    assert 'setattr(self.state, "backend", self)' not in backend_text
    assert "self.state.backend = self" in backend_text
    assert "backend: Any | None = None" in state_text


def test_certi_support_exports_explicit_names() -> None:
    text = CERTI_SUPPORT_PATH.read_text(encoding="utf-8")
    assert "__all__ = [" in text
    assert "__all__ = [name for name in globals()" not in text
