"""Summary row and JSON normalization helpers for the two-federate suite."""
from __future__ import annotations

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from hla2010.ambassadors import CallbackRecord


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, CallbackRecord):
        return {
            "method_name": value.method_name,
            "snake_name": value.snake_name,
            "args": [_jsonable(item) for item in value.args],
            "kwargs": {key: _jsonable(item) for key, item in value.kwargs.items()},
            "reference": value.reference.label if value.reference else None,
        }
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return _jsonable(value.as_dict())
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(_jsonable(key)): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_jsonable(item) for item in value)
    if hasattr(value, "value"):
        return {"type": type(value).__name__, "value": _jsonable(value.value)}
    return repr(value)


def _callback_rows(role: str, records: list[CallbackRecord], *, profile: str = "python", scenario: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        rows.append(
            {
                "profile": profile,
                "scenario": scenario,
                "role": role,
                "index": index,
                "method_name": record.method_name,
                "snake_name": record.snake_name,
                "reference": record.reference.label if record.reference else "",
                "args_json": json.dumps([_jsonable(item) for item in record.args], sort_keys=True),
            }
        )
    return rows


def _save_restore_rows(*, summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "scenario": "save_restore",
            "backend": "python/in-memory",
            "callbacks": len(summary["save_restore"]["left_callbacks"]) + len(summary["save_restore"]["right_callbacks"]),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "federationSaved and restore callbacks with restored logical time",
        }
    ]


def _ddm_rows(*, summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "scenario": "ddm",
            "backend": "python/in-memory",
            "callbacks": len(summary["ddm"]["receiver_callbacks"]),
            "artifacts": ["typed summary", "callback timeline"],
            "key_outcome": "region-filtered timestamped delivery",
        }
    ]


def _profile_summary_rows(profile: str, profile_summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = list(profile_summary["scenario_rows"])
    if profile == "python":
        rows.extend(_save_restore_rows(summary=profile_summary))
        rows.extend(_ddm_rows(summary=profile_summary))
    return rows


__all__ = [
    "_callback_rows",
    "_jsonable",
    "_profile_summary_rows",
]
