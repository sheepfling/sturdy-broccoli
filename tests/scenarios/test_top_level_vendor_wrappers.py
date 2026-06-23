from __future__ import annotations

import json
import os
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _workspace_pythonpath() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    roots = data["tool"]["pytest"]["ini_options"]["pythonpath"]
    return os.pathsep.join(str(ROOT / root) for root in roots)


def _base_env(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    for name in (
        "HLA2010_PITCH_CRC_MODE",
        "HLA2010_PITCH_CRC_PORT",
        "HLA2010_PITCH_DOCKER_NAME",
        "HLA2010_PITCH_FEDPRO_PORT",
        "HLA2010_PITCH_USER_HOME",
    ):
        env.pop(name, None)
    env["PYTHONPATH"] = _workspace_pythonpath()
    env["HLA2010_PREFLIGHT_ARTIFACT_DIR"] = str(tmp_path / "preflight")
    env["HLA2010_VENDOR_RUNTIME_STATUS_DIR"] = str(tmp_path / "runtime-status")
    env["HLA2010_VENDOR_PARITY_ARTIFACT_DIR"] = str(tmp_path / "parity")
    env["HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE"] = "0"
    env["HLA2010_CERTI_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_PATCHED_PREFIX"] = str(tmp_path / "missing-certi-prefix")
    env["HLA2010_CERTI_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = str(tmp_path / "missing-certi-build")
    env["HLA2010_CERTI_UPSTREAM_PREFIX"] = str(tmp_path / "missing-certi-upstream-prefix")
    env["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = str(tmp_path / "missing-certi-upstream-build")
    env["HLA2010_PITCH_HOME"] = str(tmp_path / "missing-pitch-home")
    env["PATH"] = os.pathsep.join(("/usr/bin", "/bin"))
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


def test_fom_roundtrip_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "fom-roundtrip"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-roundtrip"),
            "2010",
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


def test_fom_validate_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "fom-validation"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-validate"),
            "TargetRadarFOMmodule.xml",
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


def test_fom_validate_top_level_wrapper_supports_family_html_mode(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "fom-validation-family"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-validate"),
            "--family",
            "rpr-normative",
            "--html",
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
    assert (output_dir / "fom_validation_report.json").exists()
    assert (output_dir / "fom_validation_report.md").exists()
    assert (output_dir / "fom_validation_report.html").exists()


def test_fom_workbench_top_level_wrapper_writes_snapshot_and_html(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "fom-workbench"
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "tools" / "fom-workbench"),
            "--html",
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
    assert (output_dir / "fom_workbench_snapshot.json").exists()
    assert (output_dir / "fom_workbench.html").exists()


def test_fom_stress_top_level_wrapper_writes_artifacts(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "fom-stress"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-stress"),
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
    assert (output_dir / "fom_stress_report.json").exists()
    assert (output_dir / "fom_stress_report.md").exists()


def test_rti_options_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    doc_path = ROOT / "docs" / "rti_options_and_test_matrix.md"
    original = doc_path.read_text(encoding="utf-8")
    doc_path.write_text(
        "<!-- GENERATED_BACKEND_ALIASES_START -->\nold\n<!-- GENERATED_BACKEND_ALIASES_END -->\n",
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            ["bash", str(ROOT / "tools" / "rti-options"), "generate"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        text = doc_path.read_text(encoding="utf-8")
        assert "Pure Python" in text
        assert "Pitch" in text
    finally:
        doc_path.write_text(original, encoding="utf-8")


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
    doc_text = doc_path.read_text(encoding="utf-8")
    assert "`hla-rti1516e` and `hla-rti1516-2025` are sibling versioned spec packages." in doc_text
    assert "`hla-rti-core` is the cross-version discovery and factory package." in doc_text
    assert "`hla-transport-grpc` already carries the bounded 2025 FedPro transport/client/server surface alongside the older 2010-hosted route." in doc_text


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
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["summary"]["row_count"] > 0


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
    payload = json.loads(result.stdout)
    assert payload["catalog"]["summary"]["backend_count"] == 1
    assert payload["catalog"]["backends"][0]["backend_id"] == "pitch-jpype"
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
    payload = json.loads(result.stdout)
    assert result.returncode == int(payload["exit_code"])
    assert payload["suite_name"] == "vendor-runtime-status"
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
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "vendor-parity-artifacts"


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
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["summary"]["row_count"] > 0


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
    payload = json.loads(result.stdout)
    assert payload["catalog"]["summary"]["backend_count"] == 1


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
    payload = json.loads(result.stdout)
    assert payload["catalog"]["summary"]["backend_count"] == 1
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
    payload = json.loads(result.stdout)
    assert payload["catalog"]["summary"]["backend_count"] == 1
    backend = payload["catalog"]["backends"][0]
    assert backend["backend_id"] == "portico-jpype"
    assert backend["backend_family"] == "vendor-portico-java-bridge"
    assert backend["matrices_present"] == ["requirement-disposition"]
    assert backend["status_counts"]["not-applicable"] > 0


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
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["suite_name"] == "vendor-probe-promotion-review"


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
    payload = json.loads(result.stdout)
    assert payload["extras"] == "test"
    assert payload["profile"] == "core"
    assert "packages/hla-rti1516e" in payload["workspace_packages"]
    assert "packages/hla-backend-inmemory" in payload["workspace_packages"]


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
    payload = json.loads(result.stdout)
    checks = {row["name"]: row for row in payload["checks"]}
    assert payload["repo_root"] == str(tmp_path)
    assert checks["repo_root"]["status"] == "fail"
    assert payload["summary"] in {"fail", "warn"}


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


def test_certi_easy_top_level_wrapper_preflight_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "certi-easy"), "preflight"],
        cwd=tmp_path,
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


def test_pitch_top_level_wrapper_preflight_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = _base_env(tmp_path)
    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "pitch"), "preflight"],
        cwd=tmp_path,
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
    payload = json.loads(result.stdout)
    assert payload["pitch_home"] == str(pitch_home)
    assert payload["launcher_mode"] == "raw"
    assert "opened_8989" in payload


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
    payload = json.loads(result.stdout)
    assert payload["pitch_home"] == str(pitch_home)
    assert "docker_info_exit_code" in payload
    assert "opened_8989" in payload


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


def test_certi_easy_top_level_wrapper_runs_verify_best_effort(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/certi-easy", "verify-best-effort"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_certi_compare" / "vendor_runtime_status_summary.json"
    assert runtime_summary.exists()


def test_certi_easy_top_level_wrapper_verify_best_effort_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "certi-easy"), "verify-best-effort"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    artifact_path = tmp_path / "preflight" / "certi-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "certi-preflight"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_certi_compare" / "vendor_runtime_status_summary.json"
    assert runtime_summary.exists()


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


def test_pitch_top_level_wrapper_runs_verify_best_effort(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", "./tools/pitch", "verify-best-effort"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_pitch_verify" / "vendor_runtime_status_summary.json"
    assert runtime_summary.exists()


def test_pitch_top_level_wrapper_verify_best_effort_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "pitch"), "verify-best-effort"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    artifact_path = tmp_path / "preflight" / "pitch-preflight.json"
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["tool"] == "pitch-preflight"
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_pitch_verify" / "vendor_runtime_status_summary.json"
    assert runtime_summary.exists()


def test_pitch_top_level_wrapper_verify_is_reachable_from_outside_repo(tmp_path: Path) -> None:
    env = _base_env(tmp_path)

    result = subprocess.run(
        ["bash", str(ROOT / "tools" / "pitch"), "verify"],
        cwd=tmp_path,
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
    runtime_summary = tmp_path / "runtime-status" / "vendor_green_pitch_verify" / "vendor_runtime_status_summary.json"
    assert runtime_summary.exists()


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
