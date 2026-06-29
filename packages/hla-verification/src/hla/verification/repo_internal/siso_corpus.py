"""Optional SISO DataFiles corpus discovery and inventory generation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

DEFAULT_HIGH_VALUE_SISO_FAMILIES = {
    "siso-rpr-2.0",
    "siso-rpr-3.0",
    "siso-link-16",
    "siso-space-fom",
    "siso-standard-mim",
    "siso-u-fom",
}


@dataclass(frozen=True, slots=True)
class SISOInventoryEntry:
    id: str
    path: str
    edition_class: str
    load_mode: str
    baseline_kind: str
    scenario_family: str
    tags: tuple[str, ...]
    notes: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def tracked_siso_baseline_root(repo_root: Path | None = None) -> Path:
    base_root = repo_root if repo_root is not None else _repo_root()
    return base_root / "third_party" / "fom_baseline" / "siso"


def siso_download_root(repo_root: Path | None = None) -> Path:
    base_root = repo_root if repo_root is not None else _repo_root()
    return Path(os.environ.get("HLA_SISO_DOWNLOAD_ROOT", base_root / "artifacts" / "siso_downloads"))


def siso_inventory_json_path(download_root: Path | None = None, *, repo_root: Path | None = None) -> Path:
    return (Path(download_root) if download_root is not None else siso_download_root(repo_root)) / "siso_inventory.json"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "module"


def _safe_extract_member(archive: zipfile.ZipFile, member: zipfile.ZipInfo, target_root: Path) -> Path:
    member_path = Path(member.filename)
    destination = (target_root / member_path).resolve()
    target_root_resolved = target_root.resolve()
    if target_root_resolved not in destination.parents and destination != target_root_resolved:
        raise ValueError(f"Refusing to extract unsafe archive member {member.filename!r}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(member) as source:
        destination.write_bytes(source.read())
    return destination


def _archive_stamp(archive_path: Path) -> str:
    stat = archive_path.stat()
    return f"{stat.st_mtime_ns}:{stat.st_size}"


def _is_metadata_path(path: Path) -> bool:
    return "__MACOSX" in path.parts or any(part.startswith("._") for part in path.parts)


def _content_digest(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _clear_tree(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        try:
            if path.is_dir() and not path.is_symlink():
                path.rmdir()
            else:
                path.unlink()
        except FileNotFoundError:
            continue
        except OSError:
            continue
    try:
        root.rmdir()
    except OSError:
        pass


def _extract_archive(archive_path: Path, expanded_root: Path) -> Path:
    target_root = expanded_root / archive_path.stem
    marker = target_root / ".archive-stamp"
    stamp = _archive_stamp(archive_path)
    if marker.exists() and marker.read_text(encoding="utf-8").strip() == stamp:
        return target_root
    if target_root.exists():
        _clear_tree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            if member.is_dir() or _is_metadata_path(Path(member.filename)):
                continue
            try:
                _safe_extract_member(archive, member, target_root)
            except (OSError, ValueError):
                continue
    marker.write_text(stamp + "\n", encoding="utf-8")
    return target_root


def _family_and_edition(*, archive_name: str, member_name: str) -> tuple[str, str]:
    subject = f"{archive_name} {member_name}".lower()

    if "rpr" in subject:
        if any(token in subject for token in ("2025", "3.0", "3_0", "3-0")):
            return "siso-rpr-3.0", "2025"
        if any(token in subject for token in ("2015", "2.0", "2_0", "2-0")):
            return "siso-rpr-2.0", "2010"
        return "siso-rpr", "2010"

    if "space" in subject:
        return "siso-space-fom", "2025" if "2025" in subject else "2010"

    if "link16" in subject or "link-16" in subject or "link_16" in subject:
        return "siso-link-16", "2010"

    if "u-fom" in subject or "ufom" in subject:
        return "siso-u-fom", "2010"

    if "msdl" in subject:
        return "siso-msdl", "2010"

    if "c2sim" in subject:
        return "siso-c2sim", "2010"

    if "gdl" in subject or "gfl" in subject:
        return "siso-gdl-gfl", "2010"

    if "cbml" in subject:
        return "siso-cbml", "2010"

    if "omt" in subject:
        return "siso-omt", "2010"

    if "mim" in subject or "standardmim" in subject or "hlastandardmim" in subject:
        return "siso-standard-mim", "2010" if "2010" in subject or "evolved" in subject else "2025"

    if "1516" in subject:
        return "siso-ieee-1516", "2025" if "2025" in subject else "2010"

    return _slugify(archive_name), "2010"


def _tags_for_family(scenario_family: str, edition_class: str, *, member_name: str) -> tuple[str, ...]:
    tags: list[str] = ["parser-stress", "third-party"]
    if scenario_family.startswith("siso-rpr"):
        tags.extend(["rpr", "high-value"])
    elif scenario_family == "siso-space-fom":
        tags.extend(["space", "high-value"])
    elif scenario_family == "siso-link-16":
        tags.extend(["link-16", "high-value"])
    elif scenario_family == "siso-u-fom":
        tags.extend(["u-fom", "high-value"])
    elif scenario_family == "siso-msdl":
        tags.extend(["msdl", "medium-value"])
    elif scenario_family == "siso-c2sim":
        tags.extend(["c2sim", "medium-value"])
    elif scenario_family == "siso-gdl-gfl":
        tags.extend(["gdl", "gfl", "medium-value"])
    elif scenario_family == "siso-cbml":
        tags.extend(["cbml", "medium-value"])
    elif scenario_family == "siso-omt":
        tags.extend(["omt", "medium-value"])
    elif scenario_family == "siso-standard-mim":
        tags.extend(["mim", "high-value"])
    elif scenario_family == "siso-ieee-1516":
        tags.extend(["ieee-1516", "supporting-doc"])
    else:
        tags.append("other")

    if edition_class == "2025":
        tags.append("2025")
    else:
        tags.append("2010")

    lower_member = member_name.lower()
    if any(token in lower_member for token in ("annex b", "informative", "read me", "readme", "doc", "guide", "manual")):
        tags.append("supporting-doc")
    return tuple(dict.fromkeys(tags))


def is_high_value_siso_family(scenario_family: str) -> bool:
    return scenario_family in DEFAULT_HIGH_VALUE_SISO_FAMILIES


def is_default_scope_record(record: Any) -> bool:
    scenario_family = str(getattr(record, "scenario_family", ""))
    if not scenario_family.startswith("siso-"):
        return True
    return is_high_value_siso_family(scenario_family)


def _entry_from_path(
    path: Path,
    *,
    repo_root: Path,
    archive_name: str | None = None,
    member_name: str | None = None,
) -> SISOInventoryEntry:
    family, edition_class = _family_and_edition(archive_name=archive_name or path.stem, member_name=member_name or path.name)
    tags = _tags_for_family(family, edition_class, member_name=member_name or path.name)
    load_mode = "ordered-family"
    notes = "Expanded from the SISO DataFiles corpus."
    if archive_name and member_name:
        notes = f"Expanded from SISO archive {archive_name} member {member_name}."
    elif archive_name:
        notes = f"Discovered from SISO archive {archive_name}."
    try:
        relative_path = str(path.relative_to(repo_root))
    except ValueError:
        relative_path = str(path.resolve())
    return SISOInventoryEntry(
        id=f"siso-{_slugify(family)}-{_slugify(path.stem)}",
        path=relative_path,
        edition_class=edition_class,
        load_mode=load_mode,
        baseline_kind="third-party",
        scenario_family=family,
        tags=tags,
        notes=notes,
    )


def _entry_priority(entry: Mapping[str, Any]) -> tuple[int, str]:
    family = str(entry["scenario_family"])
    name = Path(str(entry["path"])).name.lower()

    if family == "siso-space-fom":
        if "datatypes" in name:
            return (0, name)
        if "environment" in name:
            return (1, name)
        if "switch" in name:
            return (2, name)
        if "management" in name:
            return (3, name)
        if "entity" in name:
            return (4, name)
        return (50, name)

    if family == "siso-u-fom":
        if "enumeration" in name:
            return (0, name)
        if "base" in name:
            return (1, name)
        if "module" in name:
            return (2, name)
        if "merged" in name:
            return (3, name)
        return (50, name)

    if family.startswith("siso-rpr"):
        if "foundation" in name:
            return (0, name)
        if "enumeration" in name:
            return (1, name)
        if "base" in name:
            return (2, name)
        if "physical" in name:
            return (3, name)
        if "logistics" in name:
            return (4, name)
        if "minefield" in name:
            return (5, name)
        if "switch" in name:
            return (6, name)
        if "der" in name:
            return (7, name)
        if "warfare" in name:
            return (8, name)
        if "communication" in name:
            return (9, name)
        if "siman" in name:
            return (10, name)
        if "ua" in name:
            return (11, name)
        if name.endswith("io_v3.0.xml") or " io " in f" {name} ":
            return (12, name)
        if "aggregate" in name:
            return (13, name)
        if "link_16" in name or "link-16" in name:
            return (14, name)
        if "link_11" in name or "link-11" in name:
            return (15, name)
        if "merged" in name:
            return (90, name)
        return (50, name)

    if family == "siso-standard-mim":
        return (0, name)

    return (50, name)


def discover_siso_inventory_entries(download_root: Path | None = None, *, repo_root: Path | None = None) -> tuple[dict[str, Any], ...]:
    """Return optional SISO inventory rows discovered under the local download root."""

    repo_root = Path(repo_root) if repo_root is not None else _repo_root()
    configured_root = Path(download_root) if download_root is not None else siso_download_root(repo_root)
    root = configured_root
    if not root.exists() and download_root is None:
        root = tracked_siso_baseline_root(repo_root)
    if not root.exists():
        return ()

    expanded_root = root / "_expanded"
    entries: list[SISOInventoryEntry] = []
    seen_digests: set[str] = set()

    for archive_path in sorted(root.rglob("*.zip")):
        if expanded_root in archive_path.parents:
            continue
        if _is_metadata_path(archive_path.relative_to(root)):
            continue
        extracted_root = _extract_archive(archive_path, expanded_root)
        xml_files = tuple(
            path
            for path in extracted_root.rglob("*.xml")
            if path.is_file() and not _is_metadata_path(path.relative_to(extracted_root))
        )
        if not xml_files:
            continue
        for xml_path in xml_files:
            if not xml_path.exists():
                continue
            try:
                digest = _content_digest(xml_path)
            except FileNotFoundError:
                continue
            if digest in seen_digests:
                continue
            seen_digests.add(digest)
            entries.append(
                _entry_from_path(
                    xml_path,
                    repo_root=repo_root,
                    archive_name=archive_path.name,
                    member_name=str(xml_path.relative_to(extracted_root)),
                )
            )

    for xml_path in sorted(root.rglob("*.xml")):
        if expanded_root in xml_path.parents:
            continue
        if _is_metadata_path(xml_path.relative_to(root)):
            continue
        if not xml_path.exists():
            continue
        try:
            digest = _content_digest(xml_path)
        except FileNotFoundError:
            continue
        if digest in seen_digests:
            continue
        seen_digests.add(digest)
        archive_name = str(xml_path.parent.relative_to(root)) if xml_path.parent != root else xml_path.stem
        entries.append(_entry_from_path(xml_path, repo_root=repo_root, archive_name=archive_name))

    deduped: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            continue
        seen_paths.add(entry.path)
        deduped.append(asdict(entry))
    deduped.sort(key=_entry_priority)
    return tuple(deduped)


def render_siso_inventory_markdown(entries: Iterable[Mapping[str, Any]]) -> str:
    rows = list(entries)
    if not rows:
        return "\n".join(
            [
                "# SISO DataFiles Inventory",
                "",
                "No SISO downloads were discovered under the local download root.",
                "",
            ]
        )

    lines = [
        "# SISO DataFiles Inventory",
        "",
        "Generated from the local SISO download cache.",
        "",
        "| ID | Edition | Load Mode | Baseline | Scenario Family | Tags | Path |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in rows:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(entry["id"]),
                    str(entry["edition_class"]),
                    str(entry["load_mode"]),
                    str(entry["baseline_kind"]),
                    str(entry["scenario_family"]),
                    ", ".join(str(tag) for tag in entry.get("tags", ())),
                    str(entry["path"]),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def write_siso_inventory(
    output_root: str | Path | None = None,
    *,
    download_root: Path | None = None,
    repo_root: Path | None = None,
) -> tuple[Path, Path, tuple[dict[str, Any], ...]]:
    repo_root = Path(repo_root) if repo_root is not None else _repo_root()
    root = Path(output_root) if output_root is not None else (download_root if download_root is not None else siso_download_root(repo_root))
    root.mkdir(parents=True, exist_ok=True)
    entries = discover_siso_inventory_entries(download_root=download_root or root, repo_root=repo_root)
    payload = {"schema_version": 1, "entries": list(entries)}
    json_path = root / "siso_inventory.json"
    md_path = root / "siso_inventory.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_siso_inventory_markdown(entries), encoding="utf-8")
    return json_path, md_path, entries


__all__ = [
    "DEFAULT_HIGH_VALUE_SISO_FAMILIES",
    "SISOInventoryEntry",
    "discover_siso_inventory_entries",
    "is_default_scope_record",
    "is_high_value_siso_family",
    "render_siso_inventory_markdown",
    "siso_download_root",
    "tracked_siso_baseline_root",
    "siso_inventory_json_path",
    "write_siso_inventory",
]
