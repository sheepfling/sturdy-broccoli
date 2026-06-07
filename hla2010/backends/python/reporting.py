"""Service-report file support for the Python RTI backend."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ... import mom as hla_mom
from .state import FederateState, FederationState


def _is_non_string_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, frozenset)) and not isinstance(value, (str, bytes, bytearray))


def _enum_name(value: Any) -> str:
    name_attr = getattr(value, "name", None)
    if isinstance(name_attr, str):
        return name_attr
    if callable(name_attr):
        try:
            return str(name_attr())
        except Exception:
            pass
    return str(value)


class PythonRTIServiceReportFiles:
    def __init__(self, *, directory: str | None = None) -> None:
        self.directory = directory

    def report_directory(self) -> Path:
        raw = self.directory or os.environ.get("HLA2010_SERVICE_REPORT_DIR")
        if raw:
            directory = Path(raw)
        else:
            root = Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", "/private/tmp/hla-2010"))
            directory = root / "service_reports"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def ensure_file(self, federation: FederationState, federate: FederateState) -> str:
        if federate.service_report_file is None:
            federate.service_report_file = str(self._report_path(federation, federate))
        return federate.service_report_file

    def json_safe(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except UnicodeDecodeError:
                return value.hex()
        if isinstance(value, Mapping):
            return {str(self.json_safe(k)): self.json_safe(v) for k, v in value.items()}
        if _is_non_string_sequence(value):
            return [self.json_safe(v) for v in value]
        if hasattr(value, "value"):
            return {"type": value.__class__.__name__, "value": getattr(value, "value")}
        return str(value)

    def write_record(self, federation: FederationState, federate: FederateState, record: Mapping[str, Any]) -> None:
        path = federate.service_report_file or self.ensure_file(federation, federate)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(self.json_safe(record), sort_keys=True, separators=(",", ":")))
            fh.write("\n")

    def write_initial_record(self, federation: FederationState, federate: FederateState) -> None:
        self.ensure_file(federation, federate)
        initial = {
            "recordType": "ServiceReportInitialRecord",
            "specSection": "1516.1-2010 §11.5.2",
            "timestampUTC": datetime.now(timezone.utc).isoformat(),
            "connect": {
                "callbackModel": _enum_name(federate.callback_model),
                "localSettingsDesignator": federate.local_settings_designator or "",
            },
            "federation": {
                "name": federation.name,
                "logicalTimeImplementation": federation.time_factory.get_name(),
                "mimDesignator": federation.mim_module.name if federation.mim_module else hla_mom.STANDARD_MIM_NAME,
                "fomModules": [module.uri for module in federation.fom_modules],
            },
            "federate": {
                "handle": getattr(federate.handle, "value", None),
                "name": federate.name,
                "type": federate.federate_type,
            },
        }
        self.write_record(federation, federate, initial)
        federate.service_report_initial_record_written = True

    def _report_path(self, federation: FederationState, federate: FederateState) -> Path:
        safe_federation = self._safe_name(federation.name)
        safe_name = self._safe_name(federate.name or f"federate-{federate.backend_id}")
        handle_value = getattr(federate.handle, "value", federate.backend_id)
        return self.report_directory() / f"{safe_federation}_{safe_name}_{handle_value}.service-report.jsonl"

    @staticmethod
    def _safe_name(value: str) -> str:
        return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


__all__ = ["PythonRTIServiceReportFiles"]
