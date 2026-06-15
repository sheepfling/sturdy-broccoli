from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from hla2010_repo_internal.verification.vendor_gap_profiles import write_vendor_gap_profile
from tests.typed_json_models import RecordedProfile, VendorGapProfile


ROOT = Path(__file__).resolve().parents[2]
PITCH_LOST_FEDERATE_OPERATOR_ARTIFACT_REFS = [
    "analysis/preflight_artifacts/pitch-preflight.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_pitch_lost_federate_gap_profile(payload: VendorGapProfile) -> None:
    assert payload.profile == "pitch-lost-federate"
    assert payload.status == "backend-split"
    assert payload.operator_state == "environment-blocked"
    assert "Docker is unreachable" in payload.blocker_summary
    assert payload.operator_artifact_refs == tuple(PITCH_LOST_FEDERATE_OPERATOR_ARTIFACT_REFS)


def _run_profile_command(tmp_path: Path, command: list[str]) -> RecordedProfile:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = os.environ.copy()
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    return RecordedProfile.from_mapping(_load_json(tmp_path / "record" / "profile.json"))


def test_write_vendor_gap_profile_emits_known_gap_summary(tmp_path: Path) -> None:
    path = write_vendor_gap_profile(tmp_path, "certi-save-restore")
    payload = VendorGapProfile.from_mapping(_load_json(path))
    assert payload.profile == "certi-save-restore"
    assert payload.classification == "known-gap"
    assert payload.vendor == "certi"
    assert payload.next_steps == (
        "./tools/certi-easy preflight",
        "./tools/certi-easy save-restore-probe",
        "./tools/certi-easy save-restore-review 5",
    )

    ddm_path = write_vendor_gap_profile(tmp_path, "pitch-ddm")
    ddm_payload = VendorGapProfile.from_mapping(_load_json(ddm_path))
    assert ddm_payload.profile == "pitch-ddm"
    assert ddm_payload.area == "ddm"
    assert ddm_payload.classification == "known-gap"
    assert ddm_payload.next_steps == (
        "./tools/pitch preflight",
        "./tools/pitch ddm-probe",
        "./tools/pitch ddm-review 5",
    )

    negotiated_path = write_vendor_gap_profile(tmp_path, "pitch-negotiated")
    negotiated_payload = VendorGapProfile.from_mapping(_load_json(negotiated_path))
    assert negotiated_payload.profile == "pitch-negotiated"
    assert negotiated_payload.area == "negotiated_ownership"
    assert negotiated_payload.status == "bridge-divergent"
    assert negotiated_payload.next_steps == (
        "./tools/pitch preflight",
        "./tools/pitch negotiated-probe",
        "./tools/pitch negotiated-review 5",
    )

    lost_federate_path = write_vendor_gap_profile(tmp_path, "pitch-lost-federate")
    lost_federate_payload = VendorGapProfile.from_mapping(_load_json(lost_federate_path))
    assert lost_federate_payload.area == "lost_federate"
    _assert_pitch_lost_federate_gap_profile(lost_federate_payload)
    assert lost_federate_payload.next_steps == (
        "./tools/pitch preflight",
        "./tools/pitch lost-federate-probe",
        "./tools/pitch lost-federate-review 5",
    )


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
    _assert_pitch_lost_federate_gap_profile(
        VendorGapProfile.from_mapping(_load_json(tmp_path / "pitch-lost-federate.json"))
    )


def test_live_pitch_lost_federate_gap_profile_tracks_operator_blockers() -> None:
    _assert_pitch_lost_federate_gap_profile(
        VendorGapProfile.from_mapping(
            _load_json(ROOT / "analysis" / "vendor_gap_profiles" / "pitch-lost-federate.json")
        )
    )


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


@pytest.mark.parametrize(
    ("command", "expected_profile"),
    (
        (["bash", "./tools/certi-easy", "save-restore"], "certi-save-restore"),
        (["bash", "./tools/pitch", "save-restore"], "pitch-save-restore"),
        (["bash", "./tools/certi-easy", "ddm"], "certi-ddm"),
        (["bash", "./tools/pitch", "ddm"], "pitch-ddm"),
        (["bash", "./tools/pitch", "negotiated"], "pitch-negotiated"),
        (["bash", "./tools/pitch", "lost-federate"], "pitch-lost-federate"),
        (["bash", "./tools/certi-easy", "save-restore-probe"], "certi-save-restore-probe"),
        (["bash", "./tools/pitch", "save-restore-probe"], "pitch-save-restore-probe"),
        (["bash", "./tools/certi-easy", "ddm-probe"], "certi-ddm-probe"),
        (["bash", "./tools/pitch", "ddm-probe"], "pitch-ddm-probe"),
        (["bash", "./tools/pitch", "negotiated-probe"], "pitch-negotiated-probe"),
        (["bash", "./tools/pitch", "lost-federate-probe"], "pitch-lost-federate-probe"),
    ),
)
def test_tool_wrappers_use_expected_gap_or_probe_profile(tmp_path: Path, command: list[str], expected_profile: str) -> None:
    payload = _run_profile_command(tmp_path, command)
    assert payload.profile == expected_profile


@pytest.mark.parametrize(
    "profile_name",
    (
        "certi-save-restore-probe",
        "certi-ddm-probe",
        "pitch-save-restore-probe",
        "pitch-ddm-probe",
        "pitch-negotiated-probe",
        "pitch-lost-federate-probe",
    ),
)
def test_vendor_green_profiles_are_reachable(tmp_path: Path, profile_name: str) -> None:
    payload = _run_profile_command(tmp_path, ["bash", "scripts/ci/vendor_green.sh", profile_name])
    assert payload.profile == profile_name
