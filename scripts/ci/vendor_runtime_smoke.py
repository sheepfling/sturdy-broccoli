#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]


def _usage() -> str:
    return "\n".join(
        [
            "vendor_runtime_smoke.sh: run CERTI and Pitch runtime smoke/profile checks.",
            "Profiles:",
            "- certi, certi-patched, certi-upstream, certi-compare",
            "- certi-save-restore",
            "- certi-save-restore-probe",
            "- certi-ddm",
            "- certi-ddm-probe",
            "- pitch, pitch-smoke, pitch-verify",
            "- pitch-save-restore",
            "- pitch-save-restore-probe",
            "- pitch-ddm",
            "- pitch-ddm-probe",
            "- pitch-negotiated",
            "- pitch-negotiated-probe",
            "- pitch-time-window-probe",
            "- pitch-time-window-restore-state-probe",
            "- pitch-lost-federate",
            "- pitch-lost-federate-probe",
            "- matrix",
            "- all",
        ]
    )


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("HLA2010_ENABLE_REAL_RTI_SMOKE", "1")
    env.setdefault("HLA2010_CERTI_PREFLIGHT_OK", "0")
    env.setdefault("HLA2010_PITCH_PREFLIGHT_OK", "0")
    return env


def _log(message: str) -> None:
    print(f"[{os.environ.get('HLA2010_SCRIPT_NAME', 'script')}] {message}")


def _warn(message: str) -> None:
    print(f"[{os.environ.get('HLA2010_SCRIPT_NAME', 'script')}] warning: {message}", file=sys.stderr)


def _die(message: str) -> int:
    print(f"[{os.environ.get('HLA2010_SCRIPT_NAME', 'script')}] error: {message}", file=sys.stderr)
    return 1


def _local_state_root() -> Path:
    return Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", str(ROOT / ".local")))


def _normalize_local_state_key(name: str) -> str:
    mapping = {
        "CERTI-build": "certi/patched/build",
        "CERTI-install": "certi/patched/install",
        "CERTI-upstream-source": "certi/upstream/source",
        "CERTI-upstream-build": "certi/upstream/build",
        "CERTI-upstream-install": "certi/upstream/install",
        "pitch-user-home": "pitch/user-home",
    }
    return mapping.get(name, name)


def _default_state_path(name: str) -> str:
    path = _local_state_root() / _normalize_local_state_key(name)
    return str(path) if path.exists() else ""


def _venv_dir() -> Path:
    return Path(os.environ.get("HLA2010_VENV_DIR", str(ROOT / ".venv")))


def _python_bin() -> str:
    venv_python = _venv_dir() / "bin" / "python"
    if venv_python.is_file() and os.access(venv_python, os.X_OK):
        return str(venv_python)
    python3 = shutil.which("python3")
    if python3:
        return python3
    python = shutil.which("python")
    if python:
        return python
    raise SystemExit(_die("python3 or python not found"))


def _ensure_python_test_env() -> None:
    if (_venv_dir() / "bin" / "activate").is_file():
        return
    if os.environ.get("HLA2010_VENDOR_AUTO_BOOTSTRAP_PYTHON", "1") != "1":
        raise SystemExit(
            _die(
                f"python test environment is missing at {_venv_dir()}; "
                "set HLA2010_VENDOR_AUTO_BOOTSTRAP_PYTHON=1 or run ./tools/bootstrap python"
            )
        )
    _warn(f"python test environment missing at {_venv_dir()}; bootstrapping repo virtualenv")
    result = subprocess.run([str(ROOT / "scripts" / "bootstrap_python.sh")], cwd=ROOT, env=_env(), check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    if not (_venv_dir() / "bin" / "activate").is_file():
        raise SystemExit(_die(f"bootstrap did not produce {_venv_dir() / 'bin' / 'activate'}"))


def _terminate_process_tree(pid: int, sig: signal.Signals) -> None:
    try:
        children = subprocess.run(
            ["pgrep", "-P", str(pid)],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        children = None
    if children and children.returncode == 0:
        for line in children.stdout.splitlines():
            if line.strip():
                _terminate_process_tree(int(line.strip()), sig)
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass


def _run_pytest(args: Sequence[str]) -> int:
    _ensure_python_test_env()
    timeout_seconds = int(os.environ.get("HLA2010_VENDOR_PYTEST_TIMEOUT_SECONDS", "300"))
    command = [_python_bin(), "-m", "pytest", *args]
    if timeout_seconds == 0:
        return subprocess.run(command, cwd=ROOT, env=_env(), check=False).returncode
    process = subprocess.Popen(command, cwd=ROOT, env=_env())
    deadline = time.monotonic() + timeout_seconds
    while True:
        status = process.poll()
        if status is not None:
            return status
        if time.monotonic() >= deadline:
            print(
                f"vendor pytest timed out after {timeout_seconds} seconds: {' '.join(command)}",
                file=sys.stderr,
            )
            _terminate_process_tree(process.pid, signal.SIGTERM)
            time.sleep(5)
            _terminate_process_tree(process.pid, signal.SIGKILL)
            process.wait()
            return 124
        time.sleep(0.2)


def _preflight_artifact_dir() -> Path:
    return Path(os.environ.get("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(ROOT / "artifacts" / "preflight_artifacts")))


def _preflight_artifact_path(vendor: str) -> Path:
    return _preflight_artifact_dir() / f"{vendor}-preflight.json"


def _ensure_preflight_artifact_dir() -> None:
    _preflight_artifact_dir().mkdir(parents=True, exist_ok=True)


def _log_preflight_summary(vendor: str, artifact_path: Path) -> None:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    environment = payload.get("environment", "unknown")
    result = payload.get("result", "unknown")
    next_step = payload.get("next_step")
    if next_step is None:
        next_steps = payload.get("next_steps") or []
        next_step = next_steps[0] if next_steps else None
    print(f"[{vendor} preflight] artifact: {artifact_path}")
    print(f"[{vendor} preflight] environment: {environment}")
    print(f"[{vendor} preflight] result: {result}")
    if next_step:
        print(f"[{vendor} preflight] next step: {next_step}")


def _handle_blocked_preflight(vendor: str, artifact_path: Path, status: int) -> int:
    _log_preflight_summary(vendor, artifact_path)
    if os.environ.get("HLA2010_VENDOR_PREFLIGHT_STRICT", "0") == "1":
        _warn(f"{vendor} preflight blocked in strict mode; failing vendor runtime smoke")
        return status
    _warn(f"{vendor} preflight blocked; skipping runtime smoke for this vendor")
    return 2


def _emit_known_gap_profile(profile: str) -> None:
    output_dir = Path(os.environ.get("HLA2010_VENDOR_GAP_PROFILE_DIR", str(ROOT / "artifacts" / "vendor_gap_profiles")))
    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            _python_bin(),
            str(ROOT / "scripts" / "write_vendor_gap_profile.py"),
            "--profile",
            profile,
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        env=_env(),
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _run_certi_preflight() -> int:
    _ensure_preflight_artifact_dir()
    artifact_path = _preflight_artifact_path("certi")
    result = subprocess.run(
        [str(ROOT / "scripts" / "check_certi_preflight.sh"), "--json-file", str(artifact_path)],
        cwd=ROOT,
        env=_env(),
        check=False,
    )
    if result.returncode == 0:
        _log_preflight_summary("certi", artifact_path)
        return 0
    return _handle_blocked_preflight("certi", artifact_path, result.returncode)


def _run_pitch_preflight() -> int:
    _ensure_preflight_artifact_dir()
    artifact_path = _preflight_artifact_path("pitch")
    result = subprocess.run(
        [str(ROOT / "scripts" / "check_pitch_preflight.sh"), "--json-file", str(artifact_path)],
        cwd=ROOT,
        env=_env(),
        check=False,
    )
    if result.returncode == 0:
        _log_preflight_summary("pitch", artifact_path)
        _apply_pitch_preflight_runtime_env(artifact_path)
        return 0
    return _handle_blocked_preflight("pitch", artifact_path, result.returncode)


def _apply_pitch_preflight_runtime_env(artifact_path: Path) -> None:
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    ports = payload.get("ports") or {}
    runtime = payload.get("runtime") or {}
    crc = ports.get("crc") or {}
    fedpro = ports.get("fedpro") or {}
    if "port" in crc:
        os.environ["HLA2010_PITCH_CRC_PORT"] = str(crc["port"])
    if "port" in fedpro:
        os.environ["HLA2010_PITCH_FEDPRO_PORT"] = str(fedpro["port"])
    if runtime.get("container_name"):
        os.environ["HLA2010_PITCH_DOCKER_NAME"] = str(runtime["container_name"])


def _guard_vendor_preflight(vendor: str) -> int:
    if vendor == "certi":
        status = _run_certi_preflight()
        if status == 0:
            os.environ["HLA2010_CERTI_PREFLIGHT_OK"] = "1"
        return status
    if vendor == "pitch":
        status = _run_pitch_preflight()
        if status == 0:
            os.environ["HLA2010_PITCH_PREFLIGHT_OK"] = "1"
        return status
    raise SystemExit(_die(f"unknown vendor preflight guard: {vendor}"))


def _default_pitch_home() -> str:
    env_home = os.environ.get("HLA2010_PITCH_HOME")
    if env_home and Path(env_home).is_dir():
        return env_home
    bundled = ROOT / "third_party" / "pitch" / "PITCH-prti1516e-manual"
    if bundled.is_dir():
        return str(bundled)
    extracted = ROOT / "third_party" / "pitch" / "HLA_PITCH_linux" / "PITCH-prti1516e-manual"
    if extracted.is_dir():
        return str(extracted)
    return ""


def _require_runtime_prefix(label: str, path: str) -> None:
    if not path or not (Path(path) / "bin" / "rtig").is_file():
        raise SystemExit(f"{label} is required")


def _require_pitch_home() -> None:
    pitch_home = os.environ.get("HLA2010_PITCH_HOME") or _default_pitch_home()
    os.environ["HLA2010_PITCH_HOME"] = pitch_home
    if not pitch_home:
        raise SystemExit("Pitch runtime bundle is required")


def _setup_pitch_runtime_env() -> None:
    _require_pitch_home()
    if "HLA2010_PITCH_USER_HOME" not in os.environ:
        result = subprocess.run(
            [str(ROOT / "scripts" / "setup_pitch_state.sh")],
            cwd=ROOT,
            env=_env(),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        os.environ["HLA2010_PITCH_USER_HOME"] = result.stdout.strip()
    os.environ.setdefault("HLA2010_PITCH_CRC_MODE", "docker")
    os.environ.setdefault("HLA2010_PITCH_DOCKER_BUILD", "0")


def _run_certi_promoted_smoke_tests() -> int:
    status = _run_pytest(["-q", "tests/vendors/test_real_vendor_runtime_smoke.py", "-k", "certi_real_lifecycle_smoke or certi_real_exchange_smoke"])
    if status != 0:
        return status
    status = _run_pytest(
        [
            "-q",
            "tests/transport/test_grpc_transport_certi_server.py::test_grpc_transport_can_host_certi_exchange_end_to_end",
        ]
    )
    if status != 0:
        return status
    _log("CERTI gRPC exchange is promoted; CERTI gRPC synchronization/ownership remain probe-only")
    return 0


def _handle_skip(status: int) -> int:
    return 0 if status == 2 else status


def _run_certi_patched() -> int:
    _log("vendor runtime smoke: certi patched")
    status = _guard_vendor_preflight("certi")
    if status != 0:
        return _handle_skip(status)
    patched_prefix = os.environ.get("HLA2010_CERTI_PATCHED_PREFIX") or os.environ.get("HLA2010_CERTI_PREFIX") or _default_state_path("CERTI-install")
    patched_build = os.environ.get("HLA2010_CERTI_PATCHED_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_BUILD_ROOT") or _default_state_path("CERTI-build")
    os.environ["HLA2010_CERTI_PATCHED_PREFIX"] = patched_prefix
    os.environ["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = patched_build
    os.environ["HLA2010_CERTI_PREFIX"] = patched_prefix
    os.environ["HLA2010_CERTI_BUILD_ROOT"] = patched_build
    _require_runtime_prefix("patched CERTI install prefix", patched_prefix)
    status = _run_certi_promoted_smoke_tests()
    if status == 0:
        _log("CERTI extended native and gRPC sync/ownership matrices remain probe-only")
    return status


def _run_certi_upstream() -> int:
    _log("vendor runtime smoke: certi upstream")
    status = _guard_vendor_preflight("certi")
    if status != 0:
        return _handle_skip(status)
    upstream_prefix = os.environ.get("HLA2010_CERTI_UPSTREAM_PREFIX") or _default_state_path("CERTI-upstream-install")
    upstream_build = os.environ.get("HLA2010_CERTI_UPSTREAM_BUILD_ROOT") or _default_state_path("CERTI-upstream-build")
    os.environ["HLA2010_CERTI_UPSTREAM_PREFIX"] = upstream_prefix
    os.environ["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = upstream_build
    _require_runtime_prefix("upstream CERTI install prefix", upstream_prefix)
    return _run_pytest(
        [
            "-q",
            "tests/vendors/test_certi_real_backend_time_matrix.py",
            "tests/vendors/test_certi_real_backend_ownership_matrix.py",
            "-k",
            "test_certi_upstream_time_query_and_fqr_baseline or "
            "test_certi_upstream_queued_fqr_baseline or "
            "test_certi_upstream_negotiated_ownership_baseline or "
            "test_certi_upstream_release_request_branch_baseline",
        ]
    )


def _run_certi_compare() -> int:
    _log("vendor runtime smoke: certi compare")
    status = _guard_vendor_preflight("certi")
    if status != 0:
        return _handle_skip(status)
    upstream_prefix = os.environ.get("HLA2010_CERTI_UPSTREAM_PREFIX") or _default_state_path("CERTI-upstream-install")
    upstream_build = os.environ.get("HLA2010_CERTI_UPSTREAM_BUILD_ROOT") or _default_state_path("CERTI-upstream-build")
    patched_prefix = os.environ.get("HLA2010_CERTI_PATCHED_PREFIX") or os.environ.get("HLA2010_CERTI_PREFIX") or _default_state_path("CERTI-install")
    patched_build = os.environ.get("HLA2010_CERTI_PATCHED_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_BUILD_ROOT") or _default_state_path("CERTI-build")
    os.environ["HLA2010_CERTI_UPSTREAM_PREFIX"] = upstream_prefix
    os.environ["HLA2010_CERTI_UPSTREAM_BUILD_ROOT"] = upstream_build
    os.environ["HLA2010_CERTI_PATCHED_PREFIX"] = patched_prefix
    os.environ["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = patched_build
    _require_runtime_prefix("upstream CERTI install prefix", upstream_prefix)
    _require_runtime_prefix("patched CERTI install prefix", patched_prefix)
    return _run_pytest(
        [
            "-q",
            "tests/vendors/test_certi_real_backend_time_matrix.py",
            "tests/vendors/test_certi_real_backend_ownership_matrix.py",
            "-k",
            "test_certi_upstream_time_query_and_fqr_baseline or "
            "test_certi_patched_time_query_and_fqr_baseline or "
            "test_certi_upstream_queued_fqr_baseline or "
            "test_certi_patched_queued_fqr_baseline or "
            "test_certi_upstream_negotiated_ownership_baseline or "
            "test_certi_upstream_release_request_branch_baseline or "
            "test_certi_patched_release_request_branch_baseline",
        ]
    )


def _run_certi_probe(profile: str, marker: str, test_filter: str) -> int:
    _log(marker)
    status = _guard_vendor_preflight("certi")
    if status != 0:
        return _handle_skip(status)
    patched_prefix = os.environ.get("HLA2010_CERTI_PATCHED_PREFIX") or os.environ.get("HLA2010_CERTI_PREFIX") or _default_state_path("CERTI-install")
    patched_build = os.environ.get("HLA2010_CERTI_PATCHED_BUILD_ROOT") or os.environ.get("HLA2010_CERTI_BUILD_ROOT") or _default_state_path("CERTI-build")
    os.environ["HLA2010_CERTI_PATCHED_PREFIX"] = patched_prefix
    os.environ["HLA2010_CERTI_PATCHED_BUILD_ROOT"] = patched_build
    os.environ["HLA2010_CERTI_PREFIX"] = patched_prefix
    os.environ["HLA2010_CERTI_BUILD_ROOT"] = patched_build
    _require_runtime_prefix("patched CERTI install prefix", patched_prefix)
    return _run_pytest(["-q", "tests/vendors/test_real_vendor_runtime_smoke.py", "-k", test_filter])


def _run_pitch_smoke(profile: str) -> int:
    _log("vendor runtime smoke: pitch")
    status = _guard_vendor_preflight("pitch")
    if status != 0:
        return _handle_skip(status)
    _setup_pitch_runtime_env()
    if profile in {"pitch", "pitch-smoke"}:
        status = _run_pytest(
            [
                "-q",
                "tests/vendors/test_real_vendor_runtime_smoke.py",
                "-k",
                "pitch_java_real_lifecycle_smoke or "
                "pitch_java_real_exchange_smoke or "
                "pitch_java_real_vendor_encoder_proof or "
                "pitch_native_202x_vendor_auth_and_encoder_proof",
            ]
        )
        if status != 0:
            return status
    if profile in {"pitch", "pitch-verify"}:
        status = _run_pytest(["-q", "tests/vendors/test_pitch_real_backend_matrix.py"])
        if status != 0:
            return status
    return 0


def _run_pitch_probe(marker: str, test_filter: str) -> int:
    _log(marker)
    status = _guard_vendor_preflight("pitch")
    if status != 0:
        return _handle_skip(status)
    _setup_pitch_runtime_env()
    return _run_pytest(["-q", "tests/vendors/test_pitch_real_backend_matrix.py", "-k", test_filter])


def _run_pitch_runtime_probe(marker: str, test_filter: str) -> int:
    _log(marker)
    status = _guard_vendor_preflight("pitch")
    if status != 0:
        return _handle_skip(status)
    _setup_pitch_runtime_env()
    return _run_pytest(["-q", "tests/vendors/test_real_vendor_runtime_smoke.py", "-k", test_filter])


def _known_gap(profile: str, message: str) -> int:
    _emit_known_gap_profile(profile)
    _warn(message)
    return 3


def _run_matrix() -> int:
    _log("vendor runtime smoke: matrix")
    status = main(["vendor_runtime_smoke.py", "certi"])
    if status != 0:
        return status
    return main(["vendor_runtime_smoke.py", "pitch"])


def _run_all() -> int:
    _log("vendor runtime smoke: all")
    certi_status = _guard_vendor_preflight("certi")
    if certi_status not in {0, 2}:
        return certi_status
    certi_ready = certi_status == 0
    pitch_status = _guard_vendor_preflight("pitch")
    if pitch_status not in {0, 2}:
        return pitch_status
    pitch_ready = pitch_status == 0
    if not certi_ready and not pitch_ready:
        _warn("no runnable vendor runtime remained after preflight; skipping smoke file")
        return 0
    if certi_ready and pitch_ready:
        status = _run_pytest(["-q", "tests/vendors/test_real_vendor_runtime_smoke.py", "-k", "pitch or certi_real_lifecycle_smoke or certi_real_exchange_smoke"])
        if status != 0:
            return status
        return _run_pytest(
            [
                "-q",
                "tests/transport/test_grpc_transport_certi_server.py::test_grpc_transport_can_host_certi_exchange_end_to_end",
            ]
        )
    if certi_ready:
        return _run_certi_promoted_smoke_tests()
    _setup_pitch_runtime_env()
    return _run_pytest(["-q", "tests/vendors/test_real_vendor_runtime_smoke.py", "-k", "pitch"])


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] in {"-h", "--help", "help"}:
        print(_usage())
        return 0

    profile = argv[1] if len(argv) > 1 else "all"
    os.environ.update(_env())

    if profile in {"certi", "certi-patched"}:
        return _run_certi_patched()
    if profile == "certi-upstream":
        return _run_certi_upstream()
    if profile == "certi-compare":
        return _run_certi_compare()
    if profile == "certi-save-restore":
        _log("vendor runtime profile: certi save/restore")
        status = _guard_vendor_preflight("certi")
        if status != 0:
            return _handle_skip(status)
        return _known_gap("certi-save-restore", "CERTI real-runtime save/restore remains a known unpromoted gap in this workspace")
    if profile == "certi-save-restore-probe":
        return _run_certi_probe(profile, "vendor runtime profile: certi save/restore probe", "certi_real_save_restore_smoke")
    if profile == "certi-ddm":
        _log("vendor runtime profile: certi DDM")
        status = _guard_vendor_preflight("certi")
        if status != 0:
            return _handle_skip(status)
        return _known_gap("certi-ddm", "CERTI real-runtime DDM remains a known unpromoted gap in this workspace")
    if profile == "certi-ddm-probe":
        return _run_certi_probe(profile, "vendor runtime profile: certi DDM probe", "certi_real_ddm_smoke")
    if profile in {"pitch", "pitch-smoke", "pitch-verify"}:
        return _run_pitch_smoke(profile)
    if profile == "pitch-save-restore":
        _log("vendor runtime profile: pitch save/restore")
        status = _guard_vendor_preflight("pitch")
        if status != 0:
            return _handle_skip(status)
        return _known_gap("pitch-save-restore", "Pitch real-runtime save/restore remains a known unpromoted gap in this workspace")
    if profile == "pitch-save-restore-probe":
        return _run_pitch_runtime_probe("vendor runtime profile: pitch save/restore probe", "pitch_java_real_save_restore_smoke")
    if profile == "pitch-ddm":
        _log("vendor runtime profile: pitch DDM")
        status = _guard_vendor_preflight("pitch")
        if status != 0:
            return _handle_skip(status)
        return _known_gap("pitch-ddm", "Pitch real-runtime DDM remains a known unpromoted gap in this workspace")
    if profile == "pitch-ddm-probe":
        return _run_pitch_runtime_probe("vendor runtime profile: pitch DDM probe", "pitch_java_real_ddm_smoke")
    if profile == "pitch-negotiated":
        _log("vendor runtime profile: pitch negotiated ownership")
        status = _guard_vendor_preflight("pitch")
        if status != 0:
            return _handle_skip(status)
        return _known_gap("pitch-negotiated", "Pitch real-runtime negotiated ownership remains a known bridge-divergent unpromoted gap in this workspace")
    if profile == "pitch-negotiated-probe":
        return _run_pitch_probe(
            "vendor runtime profile: pitch negotiated ownership probe",
            "pitch_negotiated_divesting_offer_probe or pitch_release_request_owned_attribute_probe",
        )
    if profile == "pitch-time-window-probe":
        return _run_pitch_probe("vendor runtime profile: pitch time-window future-exclusion probe", "pitch_time_window_future_exclusion_matrix")
    if profile == "pitch-time-window-restore-state-probe":
        return _run_pitch_probe("vendor runtime profile: pitch time-window restore-state probe", "pitch_time_window_restore_state_matrix")
    if profile == "pitch-lost-federate":
        _log("vendor runtime profile: pitch lost federate")
        status = _guard_vendor_preflight("pitch")
        if status != 0:
            return _handle_skip(status)
        return _known_gap(
            "pitch-lost-federate",
            "Pitch real-runtime lost-federate parity remains blocked at the family level; use the JPype/Py4J probe route to gather promotion evidence",
        )
    if profile == "pitch-lost-federate-probe":
        os.environ.setdefault("HLA2010_PITCH_CRC_HEARTBEAT_ENABLE", "true")
        os.environ.setdefault("HLA2010_PITCH_CRC_HEARTBEAT_INTERVAL", "1")
        os.environ.setdefault("HLA2010_PITCH_CRC_HEARTBEAT_ACTION", "resign")
        os.environ.setdefault("HLA2010_PITCH_LRC_PEER_HEARTBEAT_INTERVAL_MILLIS", "1000")
        os.environ.setdefault("HLA2010_PITCH_FEDPRO_TIMEOUT_HEART_SECONDS", "5")
        os.environ.setdefault("HLA2010_PITCH_FEDPRO_TIMEOUT_PURGE_SECONDS", "15")
        return _run_pitch_probe("vendor runtime profile: pitch lost federate probe", "pitch_backend_lost_federate_mom_matrix")
    if profile == "matrix":
        return _run_matrix()
    if profile == "all":
        return _run_all()

    print(
        "usage: "
        "vendor_runtime_smoke.sh "
        "[certi|certi-patched|certi-upstream|certi-compare|certi-save-restore|certi-save-restore-probe|certi-ddm|certi-ddm-probe|"
        "pitch|pitch-smoke|pitch-verify|pitch-save-restore|pitch-save-restore-probe|pitch-ddm|pitch-ddm-probe|"
        "pitch-negotiated|pitch-negotiated-probe|pitch-time-window-probe|pitch-time-window-restore-state-probe|"
        "pitch-lost-federate|pitch-lost-federate-probe|matrix|all]",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
