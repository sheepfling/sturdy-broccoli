"""Shared FOM inventory lookup helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from hla.verification.repo_internal.siso_corpus import discover_siso_inventory_entries


@dataclass(frozen=True, slots=True)
class FOMInventoryRecord:
    id: str
    path: str
    edition_class: str
    load_mode: str
    baseline_kind: str
    scenario_family: str
    notes: str
    tags: tuple[str, ...] = ()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


@lru_cache(maxsize=1)
def _inventory_records() -> tuple[FOMInventoryRecord, ...]:
    inventory_path = _repo_root() / "docs" / "fom-examples" / "fom_inventory.json"
    payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    entries = list(payload["entries"])
    entries.extend(discover_siso_inventory_entries())
    return tuple(FOMInventoryRecord(**entry) for entry in entries)


def inventory_records() -> tuple[FOMInventoryRecord, ...]:
    return _inventory_records()


def inventory_records_by_family() -> dict[str, tuple[FOMInventoryRecord, ...]]:
    grouped: dict[str, list[FOMInventoryRecord]] = {}
    for record in _inventory_records():
        grouped.setdefault(record.scenario_family, []).append(record)
    return {family: tuple(records) for family, records in grouped.items()}


def default_load_set_records(records: tuple[FOMInventoryRecord, ...]) -> tuple[FOMInventoryRecord, ...]:
    if not records:
        return ()
    load_mode = records[0].load_mode
    if load_mode == "ordered-family":
        return records
    if load_mode == "base-plus-extension":
        all_records = _inventory_records()
        base = next((record for record in all_records if record.id == "repo-2025-proto-base"), None)
        extension_records = tuple(record for record in records if record.id != "repo-2025-proto-base")
        if records[0].scenario_family == "proto2025-v0.1":
            return (base,) if base is not None else records
        if base is not None and extension_records:
            return (base, *extension_records)
        return records
    return records


def default_load_set_for_family(scenario_family: str) -> tuple[FOMInventoryRecord, ...]:
    grouped = inventory_records_by_family()
    records = grouped.get(scenario_family)
    if records is None:
        raise KeyError(f"Unknown FOM scenario family {scenario_family!r}")
    return default_load_set_records(records)


@lru_cache(maxsize=1)
def _inventory_indexes() -> tuple[dict[str, FOMInventoryRecord], dict[str, FOMInventoryRecord]]:
    repo_root = _repo_root()
    by_absolute: dict[str, FOMInventoryRecord] = {}
    by_basename: dict[str, FOMInventoryRecord] = {}
    for record in _inventory_records():
        absolute = str((repo_root / record.path).resolve())
        by_absolute[absolute] = record
        by_basename.setdefault(Path(record.path).name, record)
    return by_absolute, by_basename


def lookup_fom_inventory(path_or_source: str | Path | Any, *, year: int | None = None) -> FOMInventoryRecord | None:
    """Return the classified inventory row for a repo-known FOM XML path or source."""

    candidate = Path(str(path_or_source))
    by_absolute, by_basename = _inventory_indexes()
    resolved = str(candidate.resolve()) if candidate.exists() else None
    if resolved and resolved in by_absolute:
        return by_absolute[resolved]

    by_name = by_basename.get(candidate.name)
    if by_name is not None:
        return by_name

    if candidate.name == "HLAstandardMIM-2025.xml" or (year == 2025 and candidate.name == "HLAstandardMIM.xml"):
        return FOMInventoryRecord(
            id="external-2025-standard-mim",
            path=str(candidate),
            edition_class="2025",
            load_mode="standalone",
            baseline_kind="external",
            scenario_family="standard-mim",
            notes="External 2025 standard MIM extracted from the official 1516.2-2025 archive for round-trip coverage.",
        )

    if year == 2025:
        return FOMInventoryRecord(
            id=f"external-2025-{candidate.stem or 'module'}",
            path=str(candidate),
            edition_class="2025",
            load_mode="standalone",
            baseline_kind="external",
            scenario_family="unclassified-2025",
            notes="Unclassified 2025 FOM source inferred from the active round-trip year.",
        )
    if year == 2010:
        return FOMInventoryRecord(
            id=f"external-2010-{candidate.stem or 'module'}",
            path=str(candidate),
            edition_class="2010",
            load_mode="standalone",
            baseline_kind="external",
            scenario_family="unclassified-2010",
            notes="Unclassified 2010 FOM source inferred from the active round-trip year.",
        )
    return None


__all__ = [
    "FOMInventoryRecord",
    "default_load_set_for_family",
    "default_load_set_records",
    "inventory_records",
    "inventory_records_by_family",
    "lookup_fom_inventory",
]
