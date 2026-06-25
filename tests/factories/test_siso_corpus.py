from __future__ import annotations

import json
import zipfile
from pathlib import Path

from hla.verification.repo_internal import fom_inventory as fom_inventory_module
from hla.verification.repo_internal.fom_inventory import inventory_records
from hla.verification.repo_internal.siso_corpus import discover_siso_inventory_entries, is_default_scope_record, write_siso_inventory


def _make_sample_archive(archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("Annex_A_Files_Normative/RPR-Foundation_v3.0.xml", "<FOM/>")
        archive.writestr("Annex_A_Files_Normative/RPR-Base_v3.0.xml", "<FOM/>")
        archive.writestr("Annex_A_Files_Normative/RPR-Base_v3.0 copy.xml", "<FOM/>")
        archive.writestr("__MACOSX/Annex_A_Files_Normative/._RPR-Base_v3.0.xml", "<FOM/>")


def test_discover_siso_inventory_entries_expands_zip_archives(tmp_path: Path) -> None:
    repo_root = tmp_path
    download_root = repo_root / "artifacts" / "siso_downloads"
    _make_sample_archive(download_root / "SISO-STD-001-1-2025-RPR.zip")

    entries = discover_siso_inventory_entries(download_root=download_root, repo_root=repo_root)

    assert len(entries) == 1
    assert {entry["scenario_family"] for entry in entries} == {"siso-rpr-3.0"}
    assert {entry["edition_class"] for entry in entries} == {"2025"}
    assert all(entry["baseline_kind"] == "third-party" for entry in entries)
    assert all(entry["path"].startswith("artifacts/siso_downloads/_expanded/") for entry in entries)
    assert all("rpr" in entry["tags"] for entry in entries)
    assert all("high-value" in entry["tags"] for entry in entries)


def test_write_siso_inventory_emits_json_and_markdown(tmp_path: Path) -> None:
    repo_root = tmp_path
    download_root = repo_root / "artifacts" / "siso_downloads"
    _make_sample_archive(download_root / "SISO-STD-001-1-2025-RPR.zip")

    json_path, md_path, entries = write_siso_inventory(download_root=download_root, repo_root=repo_root)

    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert len(payload["entries"]) == 1
    md_text = md_path.read_text(encoding="utf-8")
    assert "SISO DataFiles Inventory" in md_text
    assert "| Tags |" in md_text
    assert len(entries) == 1


def test_inventory_records_include_discovered_siso_entries(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path
    download_root = repo_root / "artifacts" / "siso_downloads"
    _make_sample_archive(download_root / "SISO-STD-001-1-2025-RPR.zip")
    monkeypatch.setenv("HLA_SISO_DOWNLOAD_ROOT", str(download_root))

    fom_inventory_module._inventory_records.cache_clear()
    records = inventory_records()
    fom_inventory_module._inventory_records.cache_clear()

    assert any(record.scenario_family == "siso-rpr-3.0" for record in records)


def test_discover_siso_inventory_entries_skips_archive_metadata(tmp_path: Path) -> None:
    repo_root = tmp_path
    download_root = repo_root / "artifacts" / "siso_downloads"
    _make_sample_archive(download_root / "SISO-STD-001-1-2025-RPR.zip")

    entries = discover_siso_inventory_entries(download_root=download_root, repo_root=repo_root)

    assert all("__MACOSX" not in entry["path"] for entry in entries)
    assert all("/._" not in entry["path"] for entry in entries)


def test_default_scope_keeps_only_high_value_siso_families() -> None:
    from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord

    assert is_default_scope_record(
        FOMInventoryRecord(
            id="rpr",
            path="x",
            edition_class="2010",
            load_mode="ordered-family",
            baseline_kind="third-party",
            scenario_family="siso-rpr-2.0",
            notes="",
            tags=("high-value", "rpr"),
        )
    )
    assert not is_default_scope_record(
        FOMInventoryRecord(
            id="cbml",
            path="x",
            edition_class="2010",
            load_mode="ordered-family",
            baseline_kind="third-party",
            scenario_family="siso-cbml",
            notes="",
            tags=("medium-value", "cbml"),
        )
    )


def test_discover_siso_inventory_entries_classifies_link16_underscore_variant(tmp_path: Path) -> None:
    repo_root = tmp_path
    download_root = repo_root / "artifacts" / "siso_downloads"
    (download_root / "Link_16_v2.0.xml").parent.mkdir(parents=True, exist_ok=True)
    (download_root / "Link_16_v2.0.xml").write_text("<objectModel/>", encoding="utf-8")

    entries = discover_siso_inventory_entries(download_root=download_root, repo_root=repo_root)

    assert len(entries) == 1
    assert entries[0]["scenario_family"] == "siso-link-16"
    assert "high-value" in entries[0]["tags"]
