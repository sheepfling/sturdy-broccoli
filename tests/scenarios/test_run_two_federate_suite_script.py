from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "run_two_federate_suite.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("run_two_federate_suite_script", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_two_federate_suite_script_uses_workspace_wrapper(monkeypatch, capsys, tmp_path) -> None:
    module = _load_script_module()
    seen: dict[str, object] = {}

    class DummyPaths:
        def __init__(self, root: Path) -> None:
            self.summary_json = root / "summary.json"
            self.track_reports_csv = root / "track.csv"
            self.callbacks_csv = root / "callbacks.csv"
            self.report_markdown = root / "report.md"
            self.summary_svg = root / "summary.svg"
            self.timeline_svg = root / "timeline.svg"

    def fake_write_workspace_two_federate_suite_artifacts(output_dir, *, target_radar_steps: int):
        seen["output_dir"] = output_dir
        seen["target_radar_steps"] = target_radar_steps
        return DummyPaths(Path(output_dir))

    monkeypatch.setattr(
        module,
        "write_workspace_two_federate_suite_artifacts",
        fake_write_workspace_two_federate_suite_artifacts,
    )

    exit_code = module.main(
        [
            "--output-dir",
            str(tmp_path),
            "--target-radar-steps",
            "5",
        ]
    )

    assert exit_code == 0
    assert seen["output_dir"] == str(tmp_path)
    assert seen["target_radar_steps"] == 5

    lines = capsys.readouterr().out.strip().splitlines()
    assert lines == [
        str(tmp_path / "summary.json"),
        str(tmp_path / "track.csv"),
        str(tmp_path / "callbacks.csv"),
        str(tmp_path / "report.md"),
        str(tmp_path / "summary.svg"),
        str(tmp_path / "timeline.svg"),
    ]
