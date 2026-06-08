from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


IMPORT_ROOT = Path(__file__).resolve().parents[2] / "requirements" / "imports" / "hla_1516_requirements_codebase_packet_v1_0"
MANIFEST_PATH = IMPORT_ROOT / "MANIFEST.json"


def _manifest_repo_relative_to_import_root(path: str) -> Path:
    if path.startswith("requirements/"):
        return IMPORT_ROOT / path.removeprefix("requirements/")
    if path.startswith("WORK_PACKET/"):
        return IMPORT_ROOT / "work_packet" / path.removeprefix("WORK_PACKET/")
    if path in {"MANIFEST.json", "README.md"}:
        return IMPORT_ROOT / path
    raise AssertionError(f"unexpected manifest path: {path}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def test_imported_hla_packet_manifest_matches_committed_assets():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    included_files = manifest["included_files"]
    restricted_prefix = "requirements/restricted_reference_inputs/"
    restricted_entries = [item for item in included_files if item["path"].startswith(restricted_prefix)]
    committed_entries = [item for item in included_files if not item["path"].startswith(restricted_prefix)]

    assert manifest["packet_name"] == "hla_1516_requirements_codebase_packet_v1_0"
    assert manifest["packet_version"] == "v1.0"
    assert len(included_files) == 47
    assert len(restricted_entries) == 5

    for item in restricted_entries:
        path = _manifest_repo_relative_to_import_root(item["path"])
        assert not path.exists(), f"restricted packet asset should stay uncommitted: {path}"

    for item in committed_entries:
        path = _manifest_repo_relative_to_import_root(item["path"])
        assert path.exists(), f"missing imported packet asset: {path}"
        if item["path"] in {"MANIFEST.json", "README.md"}:
            continue
        assert path.stat().st_size == item["bytes"], f"size drift for {path}"
        assert _sha256(path) == item["sha256"], f"checksum drift for {path}"


def test_imported_hla_packet_canonical_summary_matches_current_csv_rows():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    summary = manifest["canonical_asset_summary"]

    assert _csv_row_count(IMPORT_ROOT / "latest" / "hla_1516_requirements_master_v1_0.csv") == summary["master_requirements_rows"]
    assert _csv_row_count(IMPORT_ROOT / "latest" / "hla_1516_verification_matrix_v1_0.csv") == summary["verification_rows"]
    assert _csv_row_count(IMPORT_ROOT / "latest" / "hla_1516_clause_tracker_v1_0.csv") == summary["clause_tracker_rows"]
    assert _csv_row_count(IMPORT_ROOT / "latest" / "hla_1516_cpp_api_catalog_v1_0.csv") == summary["cpp_api_catalog_rows"]
