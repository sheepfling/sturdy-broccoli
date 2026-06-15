from __future__ import annotations

import json
import os
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest
from conftest import bootstrap_test_env, materialize_fresh_checkout
from tests.typed_json_models import (
    BackendDiscoveryOutput,
    BootstrapDoctorOutput,
    BootstrapPlanOutput,
    ComplianceArtifactOutput,
    PitchReproOutput,
    RecordedProfile,
    VendorParityArtifactsSummary,
    VendorProbePromotionReviewSummary,
    VendorRuntimeStatusSummary,
)


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class PreflightCase:
    name: str
    command: tuple[str, ...]
    cwd_factory: Callable[[Path], Path]
    artifact: str
    tool: str


@dataclass(frozen=True)
class DelegateProfileCase:
    name: str
    command: tuple[str, ...]
    profile: str
    env_factory: Callable[[Path], dict[str, str]]


@dataclass(frozen=True)
class VerifyRouteCase:
    name: str
    command: tuple[str, ...]
    cwd_factory: Callable[[Path], Path]
    returncode: int | str
    artifact: str
    tool: str
    runtime_summary: str


def _workspace_pythonpath() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    roots = data["tool"]["pytest"]["ini_options"]["pythonpath"]
    return os.pathsep.join(str(ROOT / root) for root in roots)


def _portable_path_env() -> str:
    return os.environ.get("PATH", os.defpath)


def _base_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = _workspace_pythonpath()
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
    env["PATH"] = _portable_path_env()
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


def _make_fake_pitch_home(path: Path) -> Path:
    (path / "lib").mkdir(parents=True, exist_ok=True)
    (path / "lib" / "prtifull.jar").write_text("", encoding="utf-8")
    (path / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin").mkdir(parents=True, exist_ok=True)
    (path / ".install4j" / "jre.bundle" / "Contents" / "Home" / "bin" / "java").write_text("", encoding="utf-8")
    return path


def _run_tool(
    cwd: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_preflight_artifact(tmp_path: Path, filename: str, tool_name: str) -> None:
    artifact_path = tmp_path / "preflight" / filename
    assert artifact_path.exists()
    assert _load_json(artifact_path)["tool"] == tool_name


def _assert_recorded_profile(tmp_path: Path, expected_profile: str) -> None:
    payload = RecordedProfile.from_mapping(_load_json(tmp_path / "record" / "profile.json"))
    assert payload.profile == expected_profile


def test_root_vendor_wrappers_removed_and_tools_wrappers_present() -> None:
    assert not (ROOT / "certi-easy").exists()
    assert not (ROOT / "pitch").exists()
    assert not (ROOT / "compliance").exists()
    assert not (ROOT / "two-federate").exists()
    assert not (ROOT / "bootstrap").exists()
    assert not (ROOT / "test").exists()
    assert not (ROOT / "vendor-green").exists()
    assert (ROOT / "tools" / "bootstrap").is_file()
    assert (ROOT / "tools" / "test").is_file()
    assert (ROOT / "tools" / "python").is_file()
    assert (ROOT / "tools" / "certi-easy").is_file()
    assert (ROOT / "tools" / "pitch").is_file()
    assert (ROOT / "tools" / "vendor-green").is_file()
    assert (ROOT / "tools" / "compliance").is_file()
    assert (ROOT / "tools" / "two-federate").is_file()


def test_shell_workspace_pythonpath_matches_pyproject_pythonpath() -> None:
    result = subprocess.run(
        [
            "bash",
            "-lc",
            f"ROOT_DIR='{ROOT!s}'; source \"$ROOT_DIR/scripts/lib/shell.sh\"; hla2010_shell_workspace_pythonpath",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == _workspace_pythonpath()


def test_compliance_top_level_wrapper_prints_help() -> None:
    result = subprocess.run(
        ["bash", "./tools/compliance", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/compliance generate" in result.stdout
    assert "./tools/compliance discover --show-backlog" in result.stdout


def test_fom_overview_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "fom-overview"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "fom-overview"),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    json_files = sorted(output_dir.glob("*.json"))
    md_files = sorted(output_dir.glob("*.md"))
    assert len(json_files) == 1
    assert len(md_files) == 1


def test_rti_options_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    doc_path = docs_dir / "rti_options_and_test_matrix.md"
    doc_path.write_text(
        "<!-- GENERATED_BACKEND_ALIASES_START -->\nold\n<!-- GENERATED_BACKEND_ALIASES_END -->\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "rti-options"), "generate"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    text = doc_path.read_text(encoding="utf-8")
    assert "Pure Python" in text
    assert "Pitch" in text


def test_package_deps_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)
    for package_dir in (ROOT / "packages").iterdir():
        if not package_dir.is_dir():
            continue
        target = packages_dir / package_dir.name
        target.mkdir(parents=True, exist_ok=True)
        (target / "pyproject.toml").write_text(
            (package_dir / "pyproject.toml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "package-deps"), "generate"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    doc_path = tmp_path / "docs" / "package_dependency_tree.md"
    assert doc_path.exists()
    assert "`hla2010-spec` is the single true root package." in doc_path.read_text(encoding="utf-8")


def test_package_deps_top_level_wrapper_check_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)
    for package_dir in (ROOT / "packages").iterdir():
        if not package_dir.is_dir():
            continue
        target = packages_dir / package_dir.name
        target.mkdir(parents=True, exist_ok=True)
        (target / "pyproject.toml").write_text(
            (package_dir / "pyproject.toml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    generate = subprocess.run(
        ["bash", str(ROOT / "tools" / "package-deps"), "generate"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert generate.returncode == 0, generate.stderr

    check = subprocess.run(
        ["bash", str(ROOT / "tools" / "package-deps"), "check"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr
    assert "package dependency tree artifacts are current" in check.stdout


def test_package_deps_top_level_wrapper_runs_inside_fresh_checkout(tmp_path: Path) -> None:
    fresh_root = materialize_fresh_checkout(tmp_path / "fresh-checkout")
    result = subprocess.run(
        ["bash", "./tools/package-deps", "check"],
        cwd=fresh_root,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "package dependency tree artifacts are current" in result.stdout


def test_compliance_top_level_wrapper_generate_bootstraps_workspace_pythonpath(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "compliance"), "generate"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "analysis" / "compliance" / "requirements_matrix_2010.json"
    assert summary_path.exists()
    payload = ComplianceArtifactOutput.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert payload.summary.row_count is not None and payload.summary.row_count > 0


def test_compliance_top_level_wrapper_generate_runs_inside_fresh_checkout(tmp_path: Path) -> None:
    fresh_root = materialize_fresh_checkout(tmp_path / "fresh-checkout")
    result = subprocess.run(
        ["bash", "./tools/compliance", "generate"],
        cwd=fresh_root,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = fresh_root / "analysis" / "compliance" / "requirements_matrix_2010.json"
    assert summary_path.exists()
    payload = ComplianceArtifactOutput.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert payload.summary.row_count is not None and payload.summary.row_count > 0


def test_compliance_top_level_wrapper_discover_refresh_bootstraps_workspace_pythonpath(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "compliance"),
            "discover",
            "--project-root",
            str(tmp_path),
            "--backend",
            "pitch-jpype",
            "--format",
            "json",
            "--refresh",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = BackendDiscoveryOutput.from_mapping(json.loads(result.stdout))
    assert payload.catalog.summary.backend_count == 1
    assert payload.catalog.backends[0].backend_id == "pitch-jpype"
    assert (tmp_path / "analysis" / "compliance" / "requirements_matrix_2010.json").exists()


def test_vendor_parity_top_level_wrapper_runs_with_default_args(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "vendor-parity")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "analysis" / "vendor_parity_artifacts" / "vendor_parity_artifacts_summary.json"
    manifest_path = tmp_path / "analysis" / "vendor_parity_artifacts" / "vendor_parity_artifacts_manifest.csv"
    report_path = tmp_path / "analysis" / "vendor_parity_artifacts" / "vendor_parity_artifacts_report.md"
    assert summary_path.exists()
    assert manifest_path.exists()
    assert report_path.exists()


def test_vendor_state_top_level_wrapper_classify_bootstraps_source_checkout(tmp_path: Path) -> None:
    preflight_dir = tmp_path / "preflight"
    preflight_dir.mkdir(parents=True, exist_ok=True)
    (preflight_dir / "certi-preflight.json").write_text(
        json.dumps(
            {
                "tool": "certi-preflight",
                "environment": "ready",
                "result": "ok",
                "checks": [],
                "next_steps": [],
            }
        ),
        encoding="utf-8",
    )
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "vendor-state"),
            "classify",
            "--artifact-dir",
            str(preflight_dir),
            "--output-dir",
            str(tmp_path / "runtime-status"),
            "--lane",
            "vendor-green",
            "--vendor",
            "certi",
            "--json",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.stdout.strip(), result.stderr
    payload = VendorRuntimeStatusSummary.from_mapping(json.loads(result.stdout))
    assert result.returncode == int(payload.exit_code or 0)
    assert payload.suite_name == "vendor-runtime-status"
    assert (tmp_path / "runtime-status" / "vendor_runtime_status_summary.json").exists()


def test_vendor_parity_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", "")}
    result = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            str(ROOT / "scripts" / "run_vendor_parity_artifacts.py"),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "analysis" / "vendor_parity_artifacts" / "vendor_parity_artifacts_summary.json"
    assert summary_path.exists()
    payload = VendorParityArtifactsSummary.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert payload.suite_name == "vendor-parity-artifacts"


def test_generate_compliance_artifacts_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", "")}
    result = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            str(ROOT / "scripts" / "generate_compliance_artifacts.py"),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "analysis" / "compliance" / "requirements_matrix_2010.json"
    assert summary_path.exists()
    payload = ComplianceArtifactOutput.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert payload.summary.row_count is not None and payload.summary.row_count > 0


def test_discover_backend_compliance_script_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", "")}
    generate = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            str(ROOT / "scripts" / "generate_compliance_artifacts.py"),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert generate.returncode == 0, generate.stderr

    result = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            str(ROOT / "scripts" / "discover_backend_compliance.py"),
            "--project-root",
            str(tmp_path),
            "--backend",
            "pitch-jpype",
            "--format",
            "json",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = BackendDiscoveryOutput.from_mapping(json.loads(result.stdout))
    assert payload.catalog.summary.backend_count == 1


def test_discover_backend_compliance_script_refresh_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", "")}
    result = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            str(ROOT / "scripts" / "discover_backend_compliance.py"),
            "--project-root",
            str(tmp_path),
            "--backend",
            "pitch-jpype",
            "--format",
            "json",
            "--refresh",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = BackendDiscoveryOutput.from_mapping(json.loads(result.stdout))
    assert payload.catalog.summary.backend_count == 1
    assert (tmp_path / "analysis" / "compliance" / "requirements_matrix_2010.json").exists()


def test_discover_backend_compliance_surfaces_portico_disposition_only_profiles(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", "")}
    result = subprocess.run(
        [
            os.environ.get("PYTHON", "python3"),
            str(ROOT / "scripts" / "discover_backend_compliance.py"),
            "--project-root",
            str(tmp_path),
            "--backend",
            "portico-jpype",
            "--format",
            "json",
            "--refresh",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = BackendDiscoveryOutput.from_mapping(json.loads(result.stdout))
    assert payload.catalog.summary.backend_count == 1
    backend = payload.catalog.backends[0]
    assert backend.backend_id == "portico-jpype"
    assert backend.backend_family == "vendor-portico-java-bridge"
    assert backend.matrices_present == ("requirement-disposition",)
    assert backend.status_counts["not-applicable"] > 0


def test_vendor_probe_review_promotion_review_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "vendor-probe-review"),
            "promotion-review",
            "--output-dir",
            str(tmp_path / "promotion-review"),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = tmp_path / "promotion-review" / "vendor_probe_promotion_review_summary.json"
    assert summary_path.exists()
    payload = VendorProbePromotionReviewSummary.from_mapping(json.loads(summary_path.read_text(encoding="utf-8")))
    assert payload.suite_name == "vendor-probe-promotion-review"


def test_bootstrap_top_level_wrapper_prints_help() -> None:
    result = subprocess.run(
        ["bash", "./tools/bootstrap", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/bootstrap python" in result.stdout
    assert "./tools/bootstrap doctor" in result.stdout
    assert "./tools/bootstrap python plan" in result.stdout
    assert "./tools/bootstrap python plan-json" in result.stdout


def test_bootstrap_top_level_wrapper_forwards_python_plan_json() -> None:
    result = subprocess.run(
        ["bash", "./tools/bootstrap", "python", "plan-json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "HLA2010_BOOTSTRAP_EXTRAS": "test"},
    )

    assert result.returncode == 0, result.stderr
    payload = BootstrapPlanOutput.from_mapping(json.loads(result.stdout))
    assert payload.extras == "test"
    assert payload.profile == "core"
    assert "packages/hla2010-spec" in payload.workspace_packages
    assert "packages/hla2010-rti-python" in payload.workspace_packages


def test_bootstrap_top_level_wrapper_doctor_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "bootstrap"), "doctor", "--json"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.stdout.strip(), result.stderr
    payload = BootstrapDoctorOutput.from_mapping(json.loads(result.stdout))
    assert payload.repo_root == str(tmp_path)
    assert payload.check("repo_root").status == "fail"
    assert payload.summary in {"fail", "warn"}


def test_bootstrap_and_test_top_level_wrappers_run_inside_fresh_checkout(tmp_path: Path) -> None:
    fresh_root = materialize_fresh_checkout(tmp_path / "fresh-checkout")
    bootstrap = subprocess.run(
        ["bash", "./tools/bootstrap", "python"],
        cwd=fresh_root,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert bootstrap.returncode == 0, bootstrap.stderr

    result = subprocess.run(
        ["bash", "./tools/test", "tests/architecture/test_package_graph_artifacts.py::test_package_deps_check_passes"],
        cwd=fresh_root,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_test_top_level_wrapper_prints_help() -> None:
    result = subprocess.run(
        ["bash", "./tools/test", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/test" in result.stdout
    assert "tests/test_operator_surface_policy.py" in result.stdout


def test_vendor_green_top_level_wrapper_prints_help() -> None:
    result = subprocess.run(
        ["bash", "./tools/vendor-green", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/vendor-green matrix" in result.stdout
    assert "./tools/vendor-green certi" in result.stdout
    assert "./tools/vendor-green pitch" in result.stdout


def test_two_federate_top_level_wrapper_prints_help() -> None:
    result = subprocess.run(
        ["bash", "./tools/two-federate", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/two-federate" in result.stdout
    assert "--target-radar-steps 6" in result.stdout
    assert "--output-dir analysis/my_two_federate_suite" in result.stdout


def test_two_federate_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "two-federate"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "two-federate"),
            "--output-dir",
            str(output_dir),
            "--target-radar-steps",
            "2",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "two_federate_suite_summary.json").exists()
    assert (output_dir / "two_federate_suite_report.md").exists()


def test_target_radar_matrix_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "target-radar-matrix"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "target-radar"),
            "matrix",
            "--output-dir",
            str(output_dir),
            "--backend",
            "python",
            "--steps",
            "2",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "target_radar_backend_matrix_summary.json").exists()
    assert (output_dir / "target_radar_backend_matrix_report.md").exists()


def test_target_radar_proof_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "target-radar-proof"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "target-radar"),
            "proof",
            "--output-dir",
            str(output_dir),
            "--backend",
            "python",
            "--proof-backend",
            "python",
            "--steps",
            "2",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (output_dir / "target_radar_proof_summary.json").exists()
    assert (output_dir / "target_radar_proof_report.md").exists()


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


PREFLIGHT_CASES = [
    PreflightCase("certi_in_repo", ("./tools/certi-easy", "preflight"), lambda tmp_path: ROOT, "certi-preflight.json", "certi-preflight"),
    PreflightCase("certi_outside_repo", (str(ROOT / "tools" / "certi-easy"), "preflight"), lambda tmp_path: tmp_path, "certi-preflight.json", "certi-preflight"),
    PreflightCase("pitch_in_repo", ("./tools/pitch", "preflight"), lambda tmp_path: ROOT, "pitch-preflight.json", "pitch-preflight"),
    PreflightCase("pitch_outside_repo", (str(ROOT / "tools" / "pitch"), "preflight"), lambda tmp_path: tmp_path, "pitch-preflight.json", "pitch-preflight"),
]


@pytest.mark.parametrize("case", PREFLIGHT_CASES, ids=lambda case: case.name)
def test_vendor_wrapper_preflight_routes_emit_expected_artifacts(
    tmp_path: Path, case: PreflightCase
) -> None:
    result = _run_tool(
        case.cwd_factory(tmp_path),
        *case.command,
        env=_base_env(tmp_path),
    )

    assert result.returncode != 0
    _assert_preflight_artifact(tmp_path, case.artifact, case.tool)


def test_certi_easy_top_level_wrapper_help_lists_best_effort_verify() -> None:
    result = subprocess.run(
        ["bash", "./tools/certi-easy", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/certi-easy verify-best-effort" in result.stdout


def test_pitch_top_level_wrapper_help_lists_best_effort_routes() -> None:
    result = subprocess.run(
        ["bash", "./tools/pitch", "help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/pitch smoke-best-effort" in result.stdout
    assert "./tools/pitch verify-best-effort" in result.stdout
    assert "./tools/pitch native-local-probe" in result.stdout


def test_pitch_top_level_wrapper_crc_macos_repro_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    pitch_home = _make_fake_pitch_home(tmp_path / "fake-pitch-home")
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "pitch"),
            "crc-macos-repro",
            "--pitch-home",
            str(pitch_home),
            "--timeout",
            "0.1",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = PitchReproOutput.from_mapping(json.loads(result.stdout))
    assert payload.pitch_home == str(pitch_home)
    assert payload.launcher_mode == "raw"
    assert payload.has_key("opened_8989")


def test_pitch_top_level_wrapper_crc_docker_repro_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    pitch_home = _make_fake_pitch_home(tmp_path / "fake-pitch-home")
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "pitch"),
            "crc-docker-repro",
            "--pitch-home",
            str(pitch_home),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = PitchReproOutput.from_mapping(json.loads(result.stdout))
    assert payload.pitch_home == str(pitch_home)
    assert payload.has_key("docker_info_exit_code")
    assert payload.has_key("opened_8989")


def test_pitch_top_level_wrapper_native_local_probe_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    pitch_home = _make_fake_pitch_home(tmp_path / "fake-pitch-home")
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "pitch"),
            "native-local-probe",
            "--pitch-home",
            str(pitch_home),
            "--timeout",
            "0.1",
            "--bridge",
            "none",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = PitchReproOutput.from_mapping(json.loads(result.stdout))
    assert payload.pitch_home == str(pitch_home)
    assert payload.has_key("crc")
    assert payload.has_key("fedpro")
    assert payload.has_key("designator")


DELEGATE_PROFILE_CASES = [
    DelegateProfileCase("certi_smoke_compare", ("./tools/certi-easy", "smoke", "compare"), "certi-compare", _make_certi_runnable_env),
    DelegateProfileCase("pitch_smoke", ("./tools/pitch", "smoke"), "pitch-smoke", _base_env),
    DelegateProfileCase("certi_ddm", ("./tools/certi-easy", "ddm"), "certi-ddm", _base_env),
    DelegateProfileCase("pitch_negotiated_probe", ("./tools/pitch", "negotiated-probe"), "pitch-negotiated-probe", _base_env),
]


@pytest.mark.parametrize("case", DELEGATE_PROFILE_CASES, ids=lambda case: case.name)
def test_vendor_wrappers_route_delegate_profiles(
    tmp_path: Path, case: DelegateProfileCase
) -> None:
    delegate = tmp_path / "vendor_green_delegate.py"
    _write_vendor_green_delegate(delegate)
    env = case.env_factory(tmp_path)
    env["HLA2010_VENDOR_GREEN_DELEGATE"] = str(delegate)
    env["HLA2010_TEST_RECORD_DIR"] = str(tmp_path / "record")

    result = _run_tool(ROOT, *case.command, env=env)

    assert result.returncode == 0
    _assert_recorded_profile(tmp_path, case.profile)


BEST_EFFORT_AND_VERIFY_CASES = [
    VerifyRouteCase("certi_verify_best_effort_in_repo", ("./tools/certi-easy", "verify-best-effort"), lambda tmp_path: ROOT, 0, "certi-preflight.json", "certi-preflight", "runtime-status/vendor_green_certi_compare/vendor_runtime_status_summary.json"),
    VerifyRouteCase("certi_verify_best_effort_outside_repo", (str(ROOT / "tools" / "certi-easy"), "verify-best-effort"), lambda tmp_path: tmp_path, 0, "certi-preflight.json", "certi-preflight", "runtime-status/vendor_green_certi_compare/vendor_runtime_status_summary.json"),
    VerifyRouteCase("pitch_verify_best_effort_in_repo", ("./tools/pitch", "verify-best-effort"), lambda tmp_path: ROOT, 0, "pitch-preflight.json", "pitch-preflight", "runtime-status/vendor_green_pitch_verify/vendor_runtime_status_summary.json"),
    VerifyRouteCase("pitch_verify_best_effort_outside_repo", (str(ROOT / "tools" / "pitch"), "verify-best-effort"), lambda tmp_path: tmp_path, 0, "pitch-preflight.json", "pitch-preflight", "runtime-status/vendor_green_pitch_verify/vendor_runtime_status_summary.json"),
    VerifyRouteCase("pitch_verify_outside_repo", (str(ROOT / "tools" / "pitch"), "verify"), lambda tmp_path: tmp_path, "nonzero", "pitch-preflight.json", "pitch-preflight", "runtime-status/vendor_green_pitch_verify/vendor_runtime_status_summary.json"),
]


@pytest.mark.parametrize("case", BEST_EFFORT_AND_VERIFY_CASES, ids=lambda case: case.name)
def test_vendor_wrapper_verify_routes_emit_runtime_status(
    tmp_path: Path, case: VerifyRouteCase
) -> None:
    result = _run_tool(
        case.cwd_factory(tmp_path),
        *case.command,
        env=_base_env(tmp_path),
    )

    if case.returncode == "nonzero":
        assert result.returncode != 0
    else:
        assert result.returncode == case.returncode
    _assert_preflight_artifact(tmp_path, case.artifact, case.tool)
    assert (tmp_path / case.runtime_summary).exists()
