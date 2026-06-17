"""Shared Java runtime discovery helpers."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _append_candidate(candidates: list[tuple[str, Path]], source: str, value: str | os.PathLike[str] | None) -> None:
    if value:
        candidates.append((source, Path(value).expanduser()))


def _candidate_java_homes() -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = []
    for key in ("JAVA_HOME", "JDK_HOME"):
        _append_candidate(candidates, key, os.environ.get(key))

    try:
        import jdk4py

        java_home = getattr(jdk4py, "JAVA_HOME", None)
        if java_home:
            _append_candidate(candidates, "jdk4py.JAVA_HOME", str(java_home))
    except Exception:
        pass

    try:
        completed = subprocess.run(
            ["/usr/libexec/java_home"],
            capture_output=True,
            check=False,
            text=True,
        )
        output = completed.stdout.strip()
        if completed.returncode == 0 and output:
            _append_candidate(candidates, "/usr/libexec/java_home", output)
    except Exception:
        pass

    deduped: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for source, candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            deduped.append((source, resolved))
            seen.add(resolved)
    return deduped


def discover_java_home() -> Path | None:
    """Return a usable Java home from env vars, jdk4py, or `/usr/libexec/java_home`."""
    for _, home in _candidate_java_homes():
        if (home / "bin" / "java").exists():
            return home
    return None


def discover_java_home_with_source() -> tuple[Path | None, str | None]:
    """Return a usable Java home and the discovery source used to find it."""
    for source, home in _candidate_java_homes():
        if (home / "bin" / "java").exists():
            return home, source
    direct = shutil.which("java")
    if direct:
        resolved = Path(direct).resolve()
        java_home = resolved.parent.parent
        if (java_home / "bin" / "java").exists():
            return java_home, "PATH"
    return None, None


def ensure_java_home() -> Path | None:
    """Populate ``JAVA_HOME``/``JDK_HOME`` when a runtime can be discovered."""
    home, _ = discover_java_home_with_source()
    if home is None:
        return None
    os.environ.setdefault("JAVA_HOME", str(home))
    os.environ.setdefault("JDK_HOME", str(home))
    return home


def discover_java_tool(tool_name: str) -> str | None:
    """Return a Java tool path from PATH or the discovered Java home."""
    home = ensure_java_home()
    if home is not None:
        tool = home / "bin" / tool_name
        if tool.exists():
            return str(tool)
    direct = shutil.which(tool_name)
    if direct:
        return direct
    return direct


__all__ = ["discover_java_home", "discover_java_home_with_source", "discover_java_tool", "ensure_java_home"]
