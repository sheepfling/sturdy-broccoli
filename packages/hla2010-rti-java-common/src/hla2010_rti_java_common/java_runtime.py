"""Shared Java runtime discovery helpers."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _candidate_java_homes() -> list[Path]:
    candidates: list[Path] = []
    for key in ("JAVA_HOME", "JDK_HOME"):
        value = os.environ.get(key)
        if value:
            candidates.append(Path(value).expanduser())

    try:
        import jdk4py

        java_home = getattr(jdk4py, "JAVA_HOME", None)
        if java_home:
            candidates.append(Path(str(java_home)).expanduser())
    except Exception:
        pass

    java_home_helper = Path("/usr/libexec/java_home")
    if os.name == "posix" and java_home_helper.exists():
        try:
            completed = subprocess.run(
                [str(java_home_helper)],
                capture_output=True,
                check=False,
                text=True,
            )
            output = completed.stdout.strip()
            if completed.returncode == 0 and output:
                candidates.append(Path(output))
        except Exception:
            pass

    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            deduped.append(resolved)
            seen.add(resolved)
    return deduped


def discover_java_home() -> Path | None:
    """Return a usable Java home, preferring explicit env vars then jdk4py."""
    for home in _candidate_java_homes():
        if (home / "bin" / "java").exists():
            return home
    return None


def ensure_java_home() -> Path | None:
    """Populate ``JAVA_HOME``/``JDK_HOME`` when a runtime can be discovered."""
    home = discover_java_home()
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


__all__ = ["discover_java_home", "discover_java_tool", "ensure_java_home"]
