from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from tests.typed_json_models import LabeledRecordedCall


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
    payload = [
        LabeledRecordedCall.from_mapping(row)
        for row in json.loads((tmp_path / "record.json").read_text(encoding="utf-8"))
    ]
    assert payload == [
        LabeledRecordedCall(label="stability", argv=("pitch-negotiated-probe", "5")),
        LabeledRecordedCall(label="promotion", argv=()),
        LabeledRecordedCall(label="parity", argv=()),
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
