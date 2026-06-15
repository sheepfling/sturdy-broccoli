from __future__ import annotations

import contextlib
import importlib
import json
import os
import shutil
import subprocess
import socket
import sys
import tomllib
from pathlib import Path
from typing import Any, Callable

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = REPO_ROOT / "tests"
FIXTURES_ROOT = TESTS_ROOT / "fixtures"
COMPLIANCE_ROOT = REPO_ROOT / "analysis" / "compliance"
TRACEABILITY_ROOT = REPO_ROOT / "analysis" / "traceability"


def _resolve_repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def read_repo_text(path: str | Path) -> str:
    return _resolve_repo_path(path).read_text(encoding="utf-8")


def load_json_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES_ROOT / name).read_text(encoding="utf-8"))


def load_compliance_json(name: str) -> dict[str, Any]:
    return json.loads((COMPLIANCE_ROOT / name).read_text(encoding="utf-8"))


def load_compliance_text(name: str) -> str:
    return (COMPLIANCE_ROOT / name).read_text(encoding="utf-8")


def load_traceability_json(name: str) -> dict[str, Any]:
    return json.loads((TRACEABILITY_ROOT / name).read_text(encoding="utf-8"))


def load_traceability_text(name: str) -> str:
    return (TRACEABILITY_ROOT / name).read_text(encoding="utf-8")


def bootstrap_test_env() -> dict[str, str]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "HLA2010_BOOTSTRAP_EXTRAS": "test",
    }
    for name in ("TMPDIR", "TMP", "TEMP"):
        value = os.environ.get(name)
        if value:
            env[name] = value
    return env


def workspace_python_env() -> dict[str, str]:
    env = os.environ.copy()
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = [str(REPO_ROOT / rel) for rel in pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]]
    env["PYTHONPATH"] = os.pathsep.join([*source_roots, env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    return env


def workspace_python_bin() -> Path:
    return Path(sys.executable)


def materialize_fresh_checkout(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        text=False,
        check=True,
    )
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative_path = Path(raw_path.decode("utf-8"))
        if "__pycache__" in relative_path.parts or relative_path.suffix in {".pyc", ".pyo"}:
            continue
        source = REPO_ROOT / relative_path
        if not source.exists():
            continue
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
            continue
        shutil.copy2(source, target)
    return destination


def ensure_bootstrapped_python_workspace() -> Path:
    python_bin = REPO_ROOT / ".venv" / "bin" / "python"
    check = subprocess.run(
        [
            str(python_bin),
            "-c",
            (
                "import hla2010;"
                "import hla2010.spec;"
                "import hla2010_rti_backend_common;"
                "import hla2010_rti_python;"
                "import hla2010_fom_target_radar;"
                "import hla2010_fom_minimal_demo"
            ),
        ],
        cwd=REPO_ROOT,
        env=bootstrap_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode != 0:
        subprocess.run(
            ["bash", "./tools/bootstrap", "python"],
            cwd=REPO_ROOT,
            env=bootstrap_test_env(),
            capture_output=True,
            text=True,
            check=True,
        )
    return python_bin


def _can_bind_loopback_server() -> bool:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind(("127.0.0.1", 0))
        except OSError:
            return False
    return True


_LOOPBACK_SERVER_AVAILABLE = _can_bind_loopback_server()


SOURCE_CHECKOUT_PLUGIN_MODULES = (
    "hla2010_rti_python.plugin",
    "hla2010_rti_java_jpype.plugin",
    "hla2010_rti_java_py4j.plugin",
    "hla2010_rti_pitch_jpype.plugin",
    "hla2010_rti_pitch_py4j.plugin",
    "hla2010_rti_portico.plugin",
    "hla2010_rti_certi.certi.plugin",
)


def _register_source_checkout_backend_plugins() -> None:
    from hla2010_rti_runtime_common import register_backend_plugin

    for module_name in SOURCE_CHECKOUT_PLUGIN_MODULES:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            if exc.name == module_name or module_name.startswith(f"{exc.name}."):
                continue
            raise
        for plugin in getattr(module, "backend_plugins", lambda: ())():
            register_backend_plugin(plugin)


def pytest_configure(config: pytest.Config) -> None:
    _register_source_checkout_backend_plugins()
    config.addinivalue_line(
        "markers",
        "requires_loopback_server: requires permission to bind a local loopback TCP port",
    )
    config.addinivalue_line(
        "markers",
        "requirements(*requirement_ids): explicit requirement IDs covered by the test",
    )


def pytest_runtest_setup(item: pytest.Item) -> None:
    if "requires_loopback_server" in item.keywords and not _LOOPBACK_SERVER_AVAILABLE:
        pytest.skip("loopback server sockets are unavailable in this environment")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def tests_root() -> Path:
    return TESTS_ROOT


@pytest.fixture(scope="session")
def fixture_json_loader() -> Callable[[str], dict[str, Any]]:
    return load_json_fixture


@pytest.fixture(scope="session")
def compliance_json_loader() -> Callable[[str], dict[str, Any]]:
    return load_compliance_json


@pytest.fixture(scope="session")
def compliance_text_loader() -> Callable[[str], str]:
    return load_compliance_text


@pytest.fixture(scope="session")
def traceability_json_loader() -> Callable[[str], dict[str, Any]]:
    return load_traceability_json


@pytest.fixture(scope="session")
def traceability_text_loader() -> Callable[[str], str]:
    return load_traceability_text


@pytest.fixture(scope="session")
def repo_text_reader() -> Callable[[str | Path], str]:
    return read_repo_text
