from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_delegate(path: Path, label: str) -> None:
    path.write_text(
        f"""#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

record_path = Path(os.environ["HLA2010_TEST_RECORD_FILE"])
records = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
records.append({{"label": "{label}", "argv": sys.argv[1:]}})
record_path.write_text(json.dumps(records, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_vendor_probe_review_runs_stability_review_and_parity_refresh(tmp_path: Path) -> None:
    stability = tmp_path / "stability.py"
    promotion = tmp_path / "promotion.py"
    parity = tmp_path / "parity.py"
    _write_delegate(stability, "stability")
    _write_delegate(promotion, "promotion")
    _write_delegate(parity, "parity")
    env = os.environ.copy()
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = str(stability)
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f"python3 {promotion}"
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f"python3 {parity}"
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_review.sh", "pitch-negotiated-probe", "5"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert payload == [
        {"label": "stability", "argv": ["pitch-negotiated-probe", "5"]},
        {"label": "promotion", "argv": []},
        {"label": "parity", "argv": []},
    ]


def test_vendor_probe_review_stops_after_failed_stability_stage(tmp_path: Path) -> None:
    stability = tmp_path / "stability.py"
    promotion = tmp_path / "promotion.py"
    parity = tmp_path / "parity.py"
    _write_delegate(promotion, "promotion")
    _write_delegate(parity, "parity")
    stability.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations
raise SystemExit(7)
""",
        encoding="utf-8",
    )
    stability.chmod(0o755)
    env = os.environ.copy()
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = str(stability)
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f"python3 {promotion}"
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f"python3 {parity}"
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_review.sh", "pitch-negotiated-probe", "5"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 7
    assert not (tmp_path / "record.json").exists()


def test_vendor_probe_review_runs_non_executable_shell_stability_helper(tmp_path: Path) -> None:
    stability = tmp_path / "stability.sh"
    promotion = tmp_path / "promotion.py"
    parity = tmp_path / "parity.py"
    stability.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
python3 "$HLA2010_TEST_STABILITY_HELPER" "$1" "$2"
""",
        encoding="utf-8",
    )
    helper = tmp_path / "stability_helper.py"
    _write_delegate(helper, "stability")
    _write_delegate(promotion, "promotion")
    _write_delegate(parity, "parity")
    env = os.environ.copy()
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = str(stability)
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f"python3 {promotion}"
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f"python3 {parity}"
    env["HLA2010_TEST_STABILITY_HELPER"] = str(helper)
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_review.sh", "pitch-time-window-restore-state-probe", "5"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert payload == [
        {"label": "stability", "argv": ["pitch-time-window-restore-state-probe", "5"]},
        {"label": "promotion", "argv": []},
        {"label": "parity", "argv": []},
    ]


def test_vendor_probe_review_supports_space_containing_python_command_overrides(tmp_path: Path) -> None:
    helper_dir = tmp_path / "helper dir"
    helper_dir.mkdir(parents=True, exist_ok=True)
    stability = helper_dir / "stability.py"
    promotion = helper_dir / "promotion.py"
    parity = helper_dir / "parity.py"
    _write_delegate(stability, "stability")
    _write_delegate(promotion, "promotion")
    _write_delegate(parity, "parity")
    env = os.environ.copy()
    env["HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD"] = f'python3 "{stability}"'
    env["HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD"] = f'python3 "{promotion}"'
    env["HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD"] = f'python3 "{parity}"'
    env["HLA2010_TEST_RECORD_FILE"] = str(tmp_path / "record.json")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_probe_review.sh", "pitch-time-window-probe", "5"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    assert payload == [
        {"label": "stability", "argv": ["pitch-time-window-probe", "5"]},
        {"label": "promotion", "argv": []},
        {"label": "parity", "argv": []},
    ]
