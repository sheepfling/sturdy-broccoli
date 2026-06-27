from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "run_federation_subscriber_cli.py"
SPEC = importlib.util.spec_from_file_location("run_federation_subscriber_cli", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
main = MODULE.main


def test_runtime_observer_cli_catalog_json(capsys) -> None:
    exit_code = main(["catalog", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"providers"' in captured.out
    assert '"siso-runtime"' in captured.out


def test_runtime_observer_cli_observe_uses_shared_core(tmp_path: Path, monkeypatch, capsys) -> None:
    class _FakeSession:
        def __init__(self):
            self._calls = 0

        def live_state(self):
            self._calls += 1
            return {
                "status": "complete",
                "provider": "two-federate",
                "scenario": "workspace-two-federate",
                "backend": "python1516e",
                "story": "observer story",
                "live_metrics": {"event_count": 2},
                "inspectors": {"objects": [{"object_name": "Alpha"}], "interactions": [{"interaction_class": "Ping"}]},
                "normalized_events": [{"sequence": 1, "event_type": "scenario.phase", "phase": "suite-start"}],
            }

        def stop(self):
            return None

    class _FakeControl:
        def __init__(self, *, output_dir, default_backend=None):
            self.output_dir = output_dir
            self.default_backend = default_backend
            self.calls = []

        def start(self, *, provider, scenario, backend=None, options=None):
            self.calls.append((provider, scenario, backend, options))
            return _FakeSession()

    monkeypatch.setattr(MODULE, "RuntimeObserverControl", _FakeControl)
    exit_code = main(
        [
            "observe",
            "--provider",
            "two-federate",
            "--scenario",
            "workspace-two-federate",
            "--output-dir",
            str(tmp_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "status: complete" in captured.out
    assert "scenario: workspace-two-federate" in captured.out
