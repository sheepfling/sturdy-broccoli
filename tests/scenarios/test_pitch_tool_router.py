from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_recorder(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
rows = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
rows.append({"argv": sys.argv[1:]})
record_path.parent.mkdir(parents=True, exist_ok=True)
record_path.write_text(json.dumps(rows, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_pitch_python_router_help_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_pitch_tool.py"), "help"],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/pitch verify-best-effort" in result.stdout
    assert "./tools/pitch fom-smoke" in result.stdout


def test_pitch_python_router_review_route_delegates_without_preflight_wrapper(tmp_path: Path) -> None:
    recorder = tmp_path / "review_recorder.py"
    _write_recorder(recorder)
    env = os.environ.copy()
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record" / "rows.json")
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = str(recorder)
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f"{sys.executable} {recorder}"
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f"{sys.executable} {recorder}"

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_pitch_tool.py"), "negotiated-review", "7"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    rows = json.loads((tmp_path / "record" / "rows.json").read_text(encoding="utf-8"))
    assert rows == [
        {"argv": ["pitch-negotiated-probe", "7"]},
        {"argv": []},
        {"argv": []},
    ]
