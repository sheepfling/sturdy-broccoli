"""Service-report file support for the pure-Python RTI.

IEEE 1516.1-2010 §11.5 defines service reporting through MOM interactions.
This module implements an optional local JSONL audit sink that records the same
logical events for test/debug workflows without changing the MOM surface.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ServiceReportRecord:
    serial_number: int
    service_name: str
    federate_handle: str | None
    federate_name: str | None
    success: bool
    exception_name: str | None = None
    section: str | None = None
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    arguments: Mapping[str, Any] = field(default_factory=dict)
    returned: Mapping[str, Any] = field(default_factory=dict)

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str) + "\n"


class ServiceReportSink:
    """Append-only JSONL service-report sink."""

    def __init__(self, path: str | Path, *, truncate: bool = False) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if truncate:
            self.path.write_text("", encoding="utf-8")

    def write(self, record: ServiceReportRecord) -> None:
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(record.to_json_line())


def load_service_report(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


__all__ = ["ServiceReportRecord", "ServiceReportSink", "load_service_report"]
