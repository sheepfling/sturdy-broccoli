#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()
TOOL_LABEL = "./tools/certi-easy"


def _env_with_script_name(env: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(os.environ if env is None else env)
    merged.setdefault("HLA2010_SCRIPT_NAME", TOOL_LABEL)
    return merged


def _run(
    args: Sequence[str | Path],
    *,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=PROJECT_ROOT,
        env=_env_with_script_name(env),
        capture_output=capture_output,
        text=True,
        check=check,
    )


def _shell_script(path: Path, *args: str) -> list[str]:
    return [str(path), *args]


def _python_bin() -> str:
    venv_python = SCRIPT_REPO_ROOT / ".venv" / "bin" / "python"
    if venv_python.is_file() and os.access(venv_python, os.X_OK):
        return str(venv_python)
    python3 = shutil.which("python3")
    if python3:
        return python3
    python = shutil.which("python")
    if python:
        return python
    raise SystemExit("error: python3 or python not found")


def _log(message: str) -> None:
    print(f"[{TOOL_LABEL}] {message}")


def _local_state_root() -> Path:
    return Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", str(SCRIPT_REPO_ROOT / ".local")))


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


def _local_state_path(name: str) -> Path:
    return _local_state_root() / _normalize_local_state_key(name)


def _ensure_local_state_layout() -> None:
    for name in (
        "CERTI-build",
        "CERTI-install",
        "CERTI-upstream-source",
        "CERTI-upstream-build",
        "CERTI-upstream-install",
        "pitch-user-home",
    ):
        _local_state_path(name).mkdir(parents=True, exist_ok=True)


def _patched_source() -> Path:
    return Path(os.environ.get("HLA2010_CERTI_SOURCE", str(SCRIPT_REPO_ROOT / "CERTI")))


def _patched_build() -> Path:
    return Path(os.environ.get("HLA2010_CERTI_BUILD", str(_local_state_path("CERTI-build"))))


def _patched_prefix() -> Path:
    return Path(os.environ.get("HLA2010_CERTI_PREFIX", str(_local_state_path("CERTI-install"))))


def _upstream_source() -> Path:
    return Path(os.environ.get("HLA2010_CERTI_UPSTREAM_SOURCE", str(_local_state_path("CERTI-upstream-source"))))


def _upstream_build() -> Path:
    return Path(os.environ.get("HLA2010_CERTI_UPSTREAM_BUILD_ROOT", str(_local_state_path("CERTI-upstream-build"))))


def _upstream_prefix() -> Path:
    return Path(os.environ.get("HLA2010_CERTI_UPSTREAM_PREFIX", str(_local_state_path("CERTI-upstream-install"))))


def _venv_python() -> Path:
    return SCRIPT_REPO_ROOT / ".venv" / "bin" / "python"


def _preflight_artifact_dir() -> Path:
    return Path(os.environ.get("HLA2010_PREFLIGHT_ARTIFACT_DIR", str(SCRIPT_REPO_ROOT / "artifacts" / "preflight_artifacts")))


def _certi_preflight_artifact_path() -> Path:
    return _preflight_artifact_dir() / "certi-preflight.json"


def _usage() -> str:
    return "\n".join(
        [
            "Usage:",
            "  ./tools/certi-easy install",
            "  ./tools/certi-easy preflight [--json] [--json-file FILE]",
            "  ./tools/certi-easy verify-best-effort",
            "  ./tools/certi-easy doctor",
            "  ./tools/certi-easy paths",
            "  ./tools/certi-easy build [patched|upstream|all]",
            "  ./tools/certi-easy run [patched|upstream] [rtig|rtia] [args...]",
            "  ./tools/certi-easy smoke [patched|upstream|compare]",
            "  ./tools/certi-easy save-restore",
            "  ./tools/certi-easy save-restore-probe",
            "  ./tools/certi-easy save-restore-review [repeat-count]",
            "  ./tools/certi-easy ddm",
            "  ./tools/certi-easy ddm-probe",
            "  ./tools/certi-easy ddm-review [repeat-count]",
            "  ./tools/certi-easy test [patched|upstream|compare]",
            "",
            "What these mean:",
            "  install   bootstrap Python, build patched CERTI, clone/build pristine upstream CERTI",
            "  doctor    show where everything lives and whether real CERTI smoke can run here",
            "  verify-best-effort run the compare CERTI lane and treat blocked local preflight as report-only",
            "  build     rebuild one or both CERTI variants",
            "  run       launch rtig or rtia for patched or upstream CERTI",
            "  smoke     run the supported real-runtime smoke/matrix profile",
            "  save-restore report the current real-runtime save/restore gap profile",
            "  save-restore-probe run the current narrow real-runtime save/restore probe",
            "  save-restore-review run repeated review for the save/restore probe and refresh promotion/parity artifacts",
            "  ddm       report the current real-runtime DDM gap profile",
            "  ddm-probe run the current narrow real-runtime DDM probe",
            "  ddm-review run repeated review for the DDM probe and refresh promotion/parity artifacts",
            "  test      alias for smoke",
            "",
            "Simple path:",
            "  ./tools/certi-easy install",
            "  ./tools/certi-easy preflight [--json] [--json-file FILE]",
            "  ./tools/certi-easy verify-best-effort",
            "  ./tools/certi-easy doctor",
            "  ./tools/certi-easy smoke compare",
        ]
    )


def _require_venv() -> None:
    if not (_venv_python().is_file() and os.access(_venv_python(), os.X_OK)):
        raise SystemExit("error: missing .venv. Run ./tools/certi-easy install first.")


def _preflight_has_json_file(args: Sequence[str]) -> bool:
    return any(arg == "--json-file" or arg.startswith("--json-file=") for arg in args)


def _run_persisted_certi_preflight(extra_args: Sequence[str]) -> int:
    _preflight_artifact_dir().mkdir(parents=True, exist_ok=True)
    command = [_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "check_certi_preflight.py"), *extra_args]
    if not _preflight_has_json_file(extra_args):
        command.extend(["--json-file", str(_certi_preflight_artifact_path())])
    return _run(command).returncode


def _emit_certi_runtime_reports(profile: str = "certi") -> None:
    _run([str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "emit_vendor_runtime_reports.sh"), "vendor-green", profile])


def _variant_or_default(raw: str = "all") -> str:
    if raw in {"patched", "upstream", "all", "compare"}:
        return raw
    raise SystemExit(f"error: unknown CERTI variant '{raw}'")


def _show_paths() -> None:
    print(
        "\n".join(
            [
                "CERTI paths",
                f"  patched source : {_patched_source()}",
                f"  patched build  : {_patched_build()}",
                f"  patched install: {_patched_prefix()}",
                f"  upstream source: {_upstream_source()}",
                f"  upstream build : {_upstream_build()}",
                f"  upstream install: {_upstream_prefix()}",
                f"  python venv    : {SCRIPT_REPO_ROOT / '.venv'}",
            ]
        )
    )


def _run_python_bootstrap() -> int:
    _log("bootstrapping python")
    return _run([str(SCRIPT_REPO_ROOT / "scripts" / "bootstrap_python.sh")]).returncode


def _run_build(variant: str) -> int:
    normalized = _variant_or_default(variant)
    _log(f"CERTI build variant={normalized}")
    if normalized == "patched":
        return _run([str(SCRIPT_REPO_ROOT / "scripts" / "rebuild_certi.sh")]).returncode
    if normalized == "upstream":
        return _run([str(SCRIPT_REPO_ROOT / "scripts" / "rebuild_certi_upstream.sh")]).returncode
    status = _run([str(SCRIPT_REPO_ROOT / "scripts" / "rebuild_certi.sh")]).returncode
    if status != 0:
        return status
    return _run([str(SCRIPT_REPO_ROOT / "scripts" / "rebuild_certi_upstream.sh")]).returncode


def _run_install() -> int:
    status = _run_python_bootstrap()
    if status != 0:
        return status
    return _run_build("all")


def _show_doctor() -> int:
    _show_paths()
    print()
    print("Patched CERTI install:")
    patched_rtig = _patched_prefix() / "bin" / "rtig"
    if patched_rtig.is_file():
        print(f"  ok: {patched_rtig}")
    else:
        print("  missing: patched rtig not built yet")
    print("Upstream CERTI install:")
    upstream_rtig = _upstream_prefix() / "bin" / "rtig"
    if upstream_rtig.is_file():
        print(f"  ok: {upstream_rtig}")
    else:
        print("  missing: upstream rtig not built yet")
    print()

    summary = _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "check_certi_preflight.py"), "--json"], capture_output=True)
    preflight = _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "check_certi_preflight.py")], capture_output=True)
    if summary.stdout.strip():
        payload = json.loads(summary.stdout)
        environment = payload.get("environment", "unknown")
        result = payload.get("result", "unknown")
        next_steps = payload.get("next_steps") or []
        if "will skip" in result and len(next_steps) > 1:
            next_step = next_steps[1]
        elif next_steps:
            next_step = next_steps[0]
        else:
            next_step = "./tools/certi-easy preflight"
        print(f"environment: {environment}")
        print(f"result: {result}")
        print(f"next step: {next_step}")
    return preflight.returncode


def _run_variant_binary(variant: str, binary: str, args: Sequence[str]) -> int:
    preflight = _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "check_certi_preflight.py")])
    if preflight.returncode != 0:
        return preflight.returncode
    env = _env_with_script_name()
    if variant == "patched":
        env["HLA2010_CERTI_PREFIX"] = str(_patched_prefix())
    elif variant == "upstream":
        env["HLA2010_CERTI_PREFIX"] = str(_upstream_prefix())
    else:
        raise SystemExit("error: run requires patched or upstream")
    return _run([str(SCRIPT_REPO_ROOT / "scripts" / "run_certi_local.sh"), binary, *args], env=env).returncode


def _run_smoke(profile: str) -> int:
    normalized = profile or "compare"
    _require_venv()
    preflight_status = _run_persisted_certi_preflight(())
    if preflight_status != 0:
        mapped = {
            "patched": "certi-patched",
            "upstream": "certi-upstream",
            "compare": "certi-compare",
        }.get(normalized, "certi")
        _emit_certi_runtime_reports(mapped)
        return preflight_status
    _log(f"CERTI smoke profile={normalized}")
    if normalized == "patched":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-patched"]).returncode
    if normalized == "upstream":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-upstream"]).returncode
    if normalized == "compare":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-compare"]).returncode
    raise SystemExit("error: smoke requires patched, upstream, or compare")


def _run_best_effort_certi_profile(profile: str) -> int:
    status = _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_runtime_smoke.py"), profile]).returncode
    _emit_certi_runtime_reports(profile)
    return status


def _run_probe_review(profile: str, repeat_count: str) -> int:
    return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "run_vendor_probe_review.py"), profile, repeat_count]).returncode


def main(argv: list[str]) -> int:
    _ensure_local_state_layout()
    command = argv[1] if len(argv) > 1 else "help"

    if command in {"help", "-h", "--help"}:
        print(_usage())
        return 0
    if command == "preflight":
        status = _run_persisted_certi_preflight(argv[2:])
        _emit_certi_runtime_reports()
        return status
    if command == "install":
        return _run_install()
    if command == "doctor":
        return _show_doctor()
    if command == "paths":
        _show_paths()
        return 0
    if command == "build":
        return _run_build(argv[2] if len(argv) > 2 else "all")
    if command == "run":
        if len(argv) < 4:
            raise SystemExit("error: usage: ./tools/certi-easy run [patched|upstream] [rtig|rtia] [args...]")
        return _run_variant_binary(argv[2], argv[3], argv[4:])
    if command in {"smoke", "test"}:
        return _run_smoke(argv[2] if len(argv) > 2 else "compare")
    if command == "verify-best-effort":
        return _run_best_effort_certi_profile("certi-compare")
    if command == "save-restore":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-save-restore"]).returncode
    if command == "save-restore-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-save-restore-probe"]).returncode
    if command == "save-restore-review":
        return _run_probe_review("certi-save-restore-probe", argv[2] if len(argv) > 2 else "5")
    if command == "ddm":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-ddm"]).returncode
    if command == "ddm-probe":
        return _run([_python_bin(), str(SCRIPT_REPO_ROOT / "scripts" / "ci" / "vendor_green.py"), "certi-ddm-probe"]).returncode
    if command == "ddm-review":
        return _run_probe_review("certi-ddm-probe", argv[2] if len(argv) > 2 else "5")

    print(_usage())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
