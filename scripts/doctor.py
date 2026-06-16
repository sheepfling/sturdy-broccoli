#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path.cwd()
LOCAL_STATE_ROOT = Path(
    os.environ.get("HLA2010_LOCAL_STATE_ROOT", str(REPO_ROOT / ".local"))
)
MIN_PYTHON = (3, 10)


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


def local_state_path(*parts: str) -> Path:
    return LOCAL_STATE_ROOT.joinpath(*parts)


@dataclass
class Check:
    name: str
    status: str
    summary: str
    detail: str | None = None


def status_rank(status: str) -> int:
    return {"ok": 0, "warn": 1, "fail": 2}.get(status, 2)


def format_version_info(version_info: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version_info)


def detect_python_bin() -> Path:
    configured = os.environ.get("HLA2010_PYTHON")
    if configured:
        resolved = shutil.which(configured)
        if resolved:
            return Path(resolved)
    venv_python = REPO_ROOT / ".venv/bin/python"
    if venv_python.exists():
        return venv_python
    resolved = shutil.which("python3") or shutil.which("python")
    if resolved:
        return Path(resolved)
    return Path("python3")


def run_python_probe(python_bin: Path) -> tuple[dict[str, object], str | None]:
    script = """
from __future__ import annotations
import importlib
import json
import shutil
import sys

modules = {
    "hla2010": "hla2010",
    "hla2010_spec": "hla.rti1516e.spec",
    "hla.backends.inmemory": "hla.backends.inmemory",
    "pytest": "pytest",
    "jpype1": "jpype",
    "py4j": "py4j",
}
payload = {
    "executable": sys.executable,
    "version": ".".join(str(part) for part in sys.version_info[:3]),
    "modules": {},
    "executables": {
        "ruff": shutil.which("ruff") is not None,
        "pyright": shutil.which("pyright") is not None,
    },
}
for name, module in modules.items():
    try:
        importlib.import_module(module)
    except Exception:
        payload["modules"][name] = False
    else:
        payload["modules"][name] = True
print(json.dumps(payload))
""".strip()
    try:
        completed = subprocess.run(
            [str(python_bin), "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return {}, str(exc)
    return json.loads(completed.stdout), None


def check_repo_root() -> Check:
    required = [
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "src/hla2010",
        REPO_ROOT / "scripts/bootstrap_python.sh",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required if not path.exists()]
    if missing:
        return Check("repo_root", "fail", "repo layout incomplete", f"missing: {', '.join(missing)}")
    return Check("repo_root", "ok", "repo layout looks correct", str(REPO_ROOT))


def check_python_runtime(python_bin: Path) -> Check:
    if not python_bin.exists():
        return Check("python_runtime", "fail", "python not found", "set HLA2010_PYTHON or install python3")
    version_info = sys.version_info[:3] if Path(sys.executable) == python_bin else None
    if version_info is None:
        probe, error = run_python_probe(python_bin)
        if error:
            return Check("python_runtime", "fail", "python probe failed", error)
        version_text = str(probe.get("version", "unknown"))
        parts = tuple(int(piece) for piece in version_text.split(".")[:3] if piece.isdigit())
        version_info = (parts + (0, 0, 0))[:3]
    if version_info < MIN_PYTHON:
        return Check(
            "python_runtime",
            "fail",
            f"python {format_version_info(version_info)} is too old",
            f"requires >= {format_version_info(MIN_PYTHON)}",
        )
    return Check(
        "python_runtime",
        "ok",
        f"python {format_version_info(version_info)} available",
        str(python_bin),
    )


def check_venv() -> Check:
    repo_venv = REPO_ROOT / ".venv"
    venv_python = repo_venv / "bin/python"
    if not repo_venv.exists():
        return Check("venv", "fail", ".venv missing", "run ./tools/bootstrap python")
    if not venv_python.exists():
        return Check("venv", "fail", ".venv exists but has no python", "rerun ./tools/bootstrap python")
    detail = str(repo_venv)
    if repo_venv.is_symlink():
        detail = f"{repo_venv} -> {repo_venv.resolve()}"
    return Check("venv", "ok", ".venv is ready", detail)


def check_workspace_imports(venv_python: Path) -> Check:
    if not venv_python.exists():
        return Check("workspace_imports", "fail", "workspace import probe unavailable", "missing .venv/bin/python")
    probe, error = run_python_probe(venv_python)
    if error:
        return Check("workspace_imports", "fail", "workspace import probe failed", error)
    modules = probe.get("modules", {})
    if not isinstance(modules, dict):
        return Check("workspace_imports", "fail", "workspace import probe malformed")
    required = (
        ("hla2010", "hla2010"),
        ("hla2010_spec", "hla.rti1516e.spec"),
        ("hla.backends.inmemory", "hla.backends.inmemory"),
    )
    missing = [display_name for key, display_name in required if not bool(modules.get(key))]
    if missing:
        return Check(
            "workspace_imports",
            "fail",
            "workspace packages are not importable in .venv",
            f"missing: {', '.join(missing)}; rerun ./tools/bootstrap python",
        )
    return Check("workspace_imports", "ok", "workspace packages import from .venv", str(probe.get("executable", venv_python)))


def check_qa_tools(venv_python: Path) -> Check:
    if not venv_python.exists():
        return Check("qa_tools", "warn", "qa tool probe skipped", "missing .venv/bin/python")
    probe, error = run_python_probe(venv_python)
    if error:
        return Check("qa_tools", "warn", "qa tool probe failed", error)
    modules = probe.get("modules", {})
    executables = probe.get("executables", {})
    pytest_ready = isinstance(modules, dict) and bool(modules.get("pytest"))
    ruff_ready = isinstance(executables, dict) and bool(executables.get("ruff"))
    pyright_ready = isinstance(executables, dict) and bool(executables.get("pyright"))
    if pytest_ready and ruff_ready and pyright_ready:
        return Check("qa_tools", "ok", "pytest, ruff, and pyright are available")
    missing: list[str] = []
    if not pytest_ready:
        missing.append("pytest")
    if not ruff_ready:
        missing.append("ruff")
    if not pyright_ready:
        missing.append("pyright")
    return Check(
        "qa_tools",
        "warn",
        "optional QA tools are incomplete",
        "missing: " + ", ".join(missing) + "; add HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python",
    )


def check_java_bridge_extras(venv_python: Path) -> Check:
    if not venv_python.exists():
        return Check("java_bridge_extras", "warn", "java bridge probe skipped", "missing .venv/bin/python")
    probe, error = run_python_probe(venv_python)
    if error:
        return Check("java_bridge_extras", "warn", "java bridge probe failed", error)
    modules = probe.get("modules", {})
    jpype_ready = isinstance(modules, dict) and bool(modules.get("jpype1"))
    py4j_ready = isinstance(modules, dict) and bool(modules.get("py4j"))
    if jpype_ready and py4j_ready:
        return Check("java_bridge_extras", "ok", "jpype1 and py4j are installed")
    present: list[str] = []
    missing: list[str] = []
    for name, ready in (("jpype1", jpype_ready), ("py4j", py4j_ready)):
        (present if ready else missing).append(name)
    summary = "bridge extras are partial" if present else "bridge extras are not installed"
    detail = f"present: {', '.join(present) if present else 'none'}; missing: {', '.join(missing)}"
    if missing == ["jpype1", "py4j"]:
        detail += "; add HLA2010_BOOTSTRAP_EXTRAS=java ./tools/bootstrap python if needed"
    return Check("java_bridge_extras", "warn", summary, detail)


def check_certi_state() -> Check:
    source_dir = REPO_ROOT / "CERTI"
    patched_rtig = local_state_path("certi", "patched", "install", "bin", "rtig")
    upstream_rtig = local_state_path("certi", "upstream", "install", "bin", "rtig")
    if patched_rtig.exists() or upstream_rtig.exists():
        built: list[str] = []
        if patched_rtig.exists():
            built.append("patched")
        if upstream_rtig.exists():
            built.append("upstream")
        return Check("certi", "ok", "CERTI install artifacts present", ", ".join(built))
    if source_dir.exists():
        return Check("certi", "warn", "CERTI source tree present but install artifacts missing", "run ./tools/certi-easy preflight or ./tools/bootstrap certi when needed")
    return Check("certi", "warn", "CERTI runtime not prepared", "optional; use only for real CERTI paths")


def check_pitch_state() -> Check:
    manual_dir = REPO_ROOT / "third_party/pitch/PITCH-prti1516e-manual"
    zip_file = REPO_ROOT / "third_party/pitch/HLA_PITCH_linux.zip"
    docker_bin = shutil.which("docker")
    if manual_dir.exists():
        detail = str(manual_dir)
        if docker_bin:
            detail += f"; docker={docker_bin}"
        return Check("pitch", "ok", "Pitch runtime bundle present", detail)
    if zip_file.exists():
        detail = str(zip_file)
        if docker_bin:
            detail += f"; docker={docker_bin}"
        return Check("pitch", "warn", "Pitch zip is present but not extracted", detail)
    if docker_bin:
        return Check("pitch", "warn", "Pitch runtime bundle missing", f"docker={docker_bin}; add vendor bundle before using ./tools/pitch")
    return Check("pitch", "warn", "Pitch runtime and Docker are unavailable", "optional; only needed for Pitch routes")


def next_steps(checks: list[Check]) -> list[str]:
    by_name = {check.name: check for check in checks}
    steps: list[str] = []
    if by_name["python_runtime"].status == "fail":
        steps.append(f"install or select Python >= {format_version_info(MIN_PYTHON)}")
        return steps
    if by_name["venv"].status == "fail" or by_name["workspace_imports"].status == "fail":
        steps.append("./tools/bootstrap python")
        steps.append("source .venv/bin/activate")
        return steps
    steps.append("source .venv/bin/activate")
    if by_name["qa_tools"].status != "ok":
        steps.append("HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python")
    if by_name["java_bridge_extras"].status != "ok":
        steps.append("HLA2010_BOOTSTRAP_EXTRAS=java ./tools/bootstrap python")
    if by_name["certi"].status != "ok":
        steps.append("./tools/certi-easy preflight")
    if by_name["pitch"].status != "ok":
        steps.append("./tools/pitch preflight")
    return steps


def summary_status(checks: list[Check]) -> str:
    worst = max(status_rank(check.status) for check in checks)
    return {0: "ok", 1: "warn", 2: "fail"}[worst]


def main() -> int:
    parser = argparse.ArgumentParser(description="Workspace setup and prerequisite doctor")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    python_bin = detect_python_bin()
    venv_python = REPO_ROOT / ".venv/bin/python"
    checks = [
        check_repo_root(),
        check_python_runtime(python_bin),
        check_venv(),
        check_workspace_imports(venv_python),
        check_qa_tools(venv_python),
        check_java_bridge_extras(venv_python),
        check_certi_state(),
        check_pitch_state(),
    ]
    payload = {
        "repo_root": str(REPO_ROOT),
        "local_state_root": str(LOCAL_STATE_ROOT),
        "summary": summary_status(checks),
        "checks": [asdict(check) for check in checks],
        "next_steps": next_steps(checks),
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"repo: {payload['repo_root']}")
        print(f"local state: {payload['local_state_root']}")
        print(f"summary: {payload['summary']}")
        print()
        for check in checks:
            print(f"[{check.status}] {check.name}: {check.summary}")
            if check.detail:
                print(f"  {check.detail}")
        print()
        print("next steps:")
        for step in payload["next_steps"]:
            print(f"  - {step}")

    return 1 if payload["summary"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
