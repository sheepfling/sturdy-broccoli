"""Shared NDJSON event stream writer for runtime observer lanes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        decoded = value.decode("utf-8", errors="replace").rstrip("\x00")
        if decoded and all(character.isprintable() for character in decoded):
            return decoded
        return value.hex()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return _jsonable(value.as_dict())
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(getattr(value, key)) for key in value.__dataclass_fields__}
    return repr(value)


class RuntimeEventStreamWriter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")
        self._sequence = 0

    def emit(self, event: Mapping[str, Any]) -> None:
        self._sequence += 1
        payload = {"sequence": self._sequence, **_jsonable(dict(event))}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


__all__ = ["RuntimeEventStreamWriter"]
