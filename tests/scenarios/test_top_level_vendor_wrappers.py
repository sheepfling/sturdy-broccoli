from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _base_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")
    env["HLA2010_CERTI_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(tmp_path / "missing-certi-upstream-prefix")
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(tmp_path / "missing-certi-upstream-build")
    env["HLA2010_PITCH_HOME"] = str(tmp_path / "missing-pitch-home")
    env["PATH"] = "/usr/bin:/bin"
    return env


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


def test_root_vendor_wrappers_removed_and_tools_wrappers_present() -> None:
    assert not (ROOT / "certi-easy").exists()
    assert not (ROOT / "pitch").exists()
    assert (ROOT / "tools" / "certi-easy").is_file()
    assert (ROOT / "tools" / "pitch").is_file()


def _make_certi_runnable_env(tmp_path: Path) -> dict[str, str]:
    env = _base_env(tmp_path)
    patched_prefix = tmp_path / "certi-patched-prefix"
    patched_build = tmp_path / "certi-patched-build"
    upstream_prefix = tmp_path / "certi-upstream-prefix"
    upstream_build = tmp_path / "certi-upstream-build"
    for prefix in (patched_prefix, upstream_prefix):
        (prefix / "bin").mkdir(parents=True, exist_ok=True)
        (prefix / "bin" / "rtig").write_text("", encoding="utf-8")
    for build_root in (patched_build, upstream_build):
        (build_root / "libRTI" / "ieee1516-2010").mkdir(parents=True, exist_ok=True)
    env["HLA2010_CERTI_PREFIX"] = str(patched_prefix)
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(patched_prefix)
    env["HLA2010_CERTI_BUILD_ROOT"] = str(patched_build)
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(patched_build)
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(upstream_prefix)
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(upstream_build)
    env["HLA2010_CERTI_PREFLIGHT_ASSUME_LOOPBACK_OK"] = "1"
    return env


def test_certi_easy_top_level_wrapper_runs_preflight(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "./tools/certi-easy", "preflight"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"


def test_pitch_top_level_wrapper_runs_preflight(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", "./tools/pitch", "preflight"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"


def test_certi_easy_top_level_wrapper_runs_smoke_compare(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _make_certi_runnable_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "smoke", "compare"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "certi-compare"


def test_pitch_top_level_wrapper_runs_smoke(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = subprocess.run(
        ["bash", "./tools/pitch", "smoke"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads((tmp_path / "record" / "profile.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "pitch-smoke"


def test_certi_easy_top_level_wrapper_runs_known_gap_route(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
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


def test_pitch_top_level_wrapper_runs_probe_route(tmp_path: Path) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = _base_env(tmp_path)
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
