"""Helpers for rendering portable paths inside generated verification artifacts."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
_TMPDIR = Path(tempfile.gettempdir()).resolve()
_TMP_ROOT_STRINGS = tuple(
    dict.fromkeys(
        [
            str(_TMPDIR),
            tempfile.gettempdir(),
            "/tmp",
            "/private/tmp",
            "/var/tmp",
        ]
        + (
            [f"/private{_TMPDIR}"]
            if str(_TMPDIR).startswith("/var/")
            else []
        )
    )
)
_ABSOLUTE_PATH_RE = re.compile(
    r"(?P<path>(?:[A-Za-z]:[\\/]|/)[^\s`\"')\]]+)"
)


def render_path(value: Path | str) -> str:
    path = Path(value).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        pass
    for root_string in _TMP_ROOT_STRINGS:
        root = Path(root_string)
        try:
            return f"<tmp>/{resolved.relative_to(root).as_posix()}"
        except ValueError:
            continue
    return resolved.as_posix()


def sanitize_text(text: str) -> str:
    rendered = text.replace(str(REPO_ROOT), "<repo>")
    rendered = rendered.replace(str(REPO_ROOT.as_posix()), "<repo>")

    def _rewrite(match: re.Match[str]) -> str:
        candidate = match.group("path")
        if candidate == "<repo>":
            return candidate
        if candidate.startswith("<tmp>/"):
            return candidate
        if candidate.startswith("<repo>/"):
            return candidate
        if os.name == "nt" and re.fullmatch(r"[A-Za-z]:[\\/]", candidate):
            return candidate
        return render_path(candidate)

    return _ABSOLUTE_PATH_RE.sub(_rewrite, rendered)


def jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return sanitize_text(value) if isinstance(value, str) else value
    if isinstance(value, Path):
        return render_path(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {key: jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return sanitize_text(repr(value))


__all__ = ["REPO_ROOT", "jsonable", "render_path", "sanitize_text"]
