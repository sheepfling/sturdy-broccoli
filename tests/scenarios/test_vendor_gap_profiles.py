from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification.vendor_gap_profiles import write_vendor_gap_profile


ROOT = Path(__file__).resolve().parents[2]


def test_write_vendor_gap_profile_emits_known_gap_summary(tmp_path: Path) -> None:
    path = write_vendor_gap_profile(tmp_path, "certi-save-restore")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-save-restore"
    assert payload["classification"] == "known-gap"
    assert payload["vendor"] == "certi"
    assert payload["next_steps"] == [
        "./tools/certi-easy preflight",
        "./tools/certi-easy save-restore-probe",
        "./tools/certi-easy save-restore-review 5",
    ]

    ddm_path = write_vendor_gap_profile(tmp_path, "pitch-ddm")
    ddm_payload = json.loads(ddm_path.read_text(encoding="utf-8"))
    assert ddm_payload["profile"] == "pitch-ddm"
    assert ddm_payload["area"] == "ddm"
    assert ddm_payload["classification"] == "known-gap"
    assert ddm_payload["next_steps"] == [
        "./tools/pitch preflight",
        "./tools/pitch ddm-probe",
        "./tools/pitch ddm-review 5",
    ]

    negotiated_path = write_vendor_gap_profile(tmp_path, "pitch-negotiated")
    negotiated_payload = json.loads(negotiated_path.read_text(encoding="utf-8"))
    assert negotiated_payload["profile"] == "pitch-negotiated"
    assert negotiated_payload["area"] == "negotiated_ownership"
    assert negotiated_payload["status"] == "bridge-divergent"
    assert negotiated_payload["next_steps"] == [
        "./tools/pitch preflight",
        "./tools/pitch negotiated-probe",
        "./tools/pitch negotiated-review 5",
    ]

    lost_federate_path = write_vendor_gap_profile(tmp_path, "pitch-lost-federate")
    lost_federate_payload = json.loads(lost_federate_path.read_text(encoding="utf-8"))
    assert lost_federate_payload["profile"] == "pitch-lost-federate"
    assert lost_federate_payload["area"] == "lost_federate"
    assert lost_federate_payload["status"] == "backend-split"
    assert lost_federate_payload["operator_state"] == "environment-blocked"
    assert "Docker is unreachable" in lost_federate_payload["blocker_summary"]
    assert lost_federate_payload["operator_artifact_refs"] == [
        "analysis/preflight_artifacts/pitch-preflight.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    ]
    assert lost_federate_payload["next_steps"] == [
        "./tools/pitch preflight",
        "./tools/pitch lost-federate-probe",
        "./tools/pitch lost-federate-review 5",
    ]


def test_write_vendor_gap_profile_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", "")}
    result = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            "scripts/write_vendor_gap_profile.py",
            "--profile",
            "pitch-lost-federate",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads((tmp_path / "pitch-lost-federate.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-lost-federate"
    assert payload["operator_state"] == "environment-blocked"


def test_live_pitch_lost_federate_gap_profile_tracks_operator_blockers() -> None:
    payload = json.loads(
        (ROOT / "analysis" / "vendor_gap_profiles" / "pitch-lost-federate.json").read_text(encoding="utf-8")
    )

    assert payload["profile"] == "pitch-lost-federate"
    assert payload["status"] == "backend-split"
    assert payload["operator_state"] == "environment-blocked"
    assert "Docker is unreachable" in payload["blocker_summary"]
    assert payload["operator_artifact_refs"] == [
        "analysis/preflight_artifacts/pitch-preflight.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
        "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    ]


def _write_vendor_green_delegate(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

profile = sys.argv[1]
out_dir = Path(os.environ["HLA2010_TEST_RECORD_DIR"])
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "profile.json").write_text(json.dumps({"profile": profile}) + "\\n", encoding="utf-8")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_certi_easy_save_restore_uses_known_gap_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "save-restore"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-save-restore"


def test_pitch_save_restore_uses_known_gap_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "save-restore"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-save-restore"


def test_certi_easy_ddm_uses_known_gap_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "ddm"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-ddm"


def test_pitch_ddm_uses_known_gap_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "ddm"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-ddm"


def test_pitch_ddm_probe_uses_probe_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-ddm-probe"


def test_pitch_negotiated_uses_known_gap_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "negotiated"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-negotiated"


def test_pitch_lost_federate_uses_known_gap_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "lost-federate"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-lost-federate"


def test_vendor_green_certi_save_restore_probe_profile_is_reachable(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "certi-save-restore-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-save-restore-probe"


def test_certi_easy_save_restore_probe_uses_probe_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "save-restore-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-save-restore-probe"


def test_pitch_save_restore_probe_uses_probe_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "save-restore-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-save-restore-probe"


def test_vendor_green_pitch_save_restore_probe_profile_is_reachable(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch-save-restore-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-save-restore-probe"


def test_vendor_green_pitch_ddm_probe_profile_is_reachable(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch-ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-ddm-probe"


def test_pitch_negotiated_probe_uses_probe_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "negotiated-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-negotiated-probe"


def test_vendor_green_pitch_negotiated_probe_profile_is_reachable(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch-negotiated-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-negotiated-probe"


def test_pitch_lost_federate_probe_uses_probe_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "lost-federate-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-lost-federate-probe"


def test_vendor_green_pitch_lost_federate_probe_profile_is_reachable(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "pitch-lost-federate-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-lost-federate-probe"


def test_certi_easy_ddm_probe_uses_probe_profile(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-ddm-probe"


def test_vendor_green_certi_ddm_probe_profile_is_reachable(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "scripts/ci/vendor_green.sh", "certi-ddm-probe"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-ddm-probe"
