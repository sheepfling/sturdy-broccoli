from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PYTHON_SOURCES = (
    ROOT / "tests",
    ROOT / "scripts",
    ROOT / "src",
    ROOT / "packages",
)
SHELL_SOURCES = (
    ROOT / "scripts",
    ROOT / "tools",
)
HARDCODED_UNIX_PATH_RE = re.compile(r'env\["PATH"\]\s*=\s*"/usr/bin:/bin"')
POSIX_MODULE_REWRITE_RE = re.compile(r'replace\((?:"/"|\'/\')\s*,\s*(?:"\."|\'\.\')\)')
ABSOLUTE_TEMP_LITERAL_RE = re.compile(r'["\']/(?:private/)?tmp/')
PURE_POSIX_PATH_ALLOWLIST = {
    ROOT / "tests" / "architecture" / "test_path_portability_policy.py",
    ROOT / "tests" / "test_root_facade_policy.py",
    ROOT / "tests" / "test_verification_harness_split_package.py",
}
ABSOLUTE_TEMP_LITERAL_ALLOWLIST = {
    ROOT / "tests" / "architecture" / "test_path_portability_policy.py",
}


def _python_files() -> list[Path]:
    files: list[Path] = []
    for root in PYTHON_SOURCES:
        files.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(files)


def _shell_files() -> list[Path]:
    files: list[Path] = []
    for root in SHELL_SOURCES:
        files.extend(path for path in root.rglob("*.sh"))
        files.extend(path for path in root.iterdir() if path.is_file() and "." not in path.name)
    return sorted(set(files))


def test_python_sources_do_not_hardcode_unix_path_literals() -> None:
    violations: list[str] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        if HARDCODED_UNIX_PATH_RE.search(text):
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)


def test_python_sources_do_not_rewrite_posix_paths_with_string_replace() -> None:
    violations: list[str] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        if POSIX_MODULE_REWRITE_RE.search(text):
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)


def test_shell_sources_do_not_hardcode_repo_tempfiles_under_tmp() -> None:
    violations: list[str] = []
    for path in _shell_files():
        text = path.read_text(encoding="utf-8")
        if "/tmp/hla2010_" in text or "TMPDIR:-/private/tmp" in text:
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)


def test_python_sources_only_use_pure_posix_path_in_allowlisted_repo_ref_helpers() -> None:
    violations: list[str] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        if "PurePosixPath" in text and path not in PURE_POSIX_PATH_ALLOWLIST:
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)


def test_python_sources_do_not_hardcode_absolute_temp_path_literals() -> None:
    violations: list[str] = []
    for path in _python_files():
        if path in ABSOLUTE_TEMP_LITERAL_ALLOWLIST:
            continue
        text = path.read_text(encoding="utf-8")
        if ABSOLUTE_TEMP_LITERAL_RE.search(text):
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)


def test_legacy_analyze_specs_tool_exposes_a_portable_cli() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "analyze_specs.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--root" in result.stdout
    assert "--output-dir" in result.stdout
    assert "--zip-path" in result.stdout
