from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_fom_inventory_view import render_inventory_markdown


REPO_ROOT = Path(__file__).resolve().parents[2]
FOM_INVENTORY = REPO_ROOT / "docs" / "fom-examples" / "fom_inventory.json"
FOM_INVENTORY_MD = REPO_ROOT / "docs" / "fom-examples" / "fom_inventory.md"
ALLOWED_EDITION_CLASSES = {"2010", "2025", "cross-edition"}
ALLOWED_LOAD_MODES = {"standalone", "base-plus-extension", "ordered-family"}
ALLOWED_BASELINE_KINDS = {"repo-owned", "third-party"}


def test_fom_inventory_manifest_has_valid_schema_and_existing_paths() -> None:
    payload = json.loads(FOM_INVENTORY.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    entries = payload["entries"]
    assert isinstance(entries, list)
    assert entries

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for entry in entries:
        assert set(entry) >= {
            "id",
            "path",
            "edition_class",
            "load_mode",
            "baseline_kind",
            "scenario_family",
            "notes",
        }
        assert entry["id"] not in seen_ids
        seen_ids.add(entry["id"])
        assert entry["path"] not in seen_paths
        seen_paths.add(entry["path"])

        assert entry["edition_class"] in ALLOWED_EDITION_CLASSES
        assert entry["load_mode"] in ALLOWED_LOAD_MODES
        assert entry["baseline_kind"] in ALLOWED_BASELINE_KINDS
        assert entry["scenario_family"]
        assert entry["notes"]

        path = REPO_ROOT / entry["path"]
        assert path.exists(), entry["path"]


def test_fom_inventory_records_expected_edition_split_and_modes() -> None:
    entries = json.loads(FOM_INVENTORY.read_text(encoding="utf-8"))["entries"]
    by_id = {entry["id"]: entry for entry in entries}

    assert by_id["repo-2010-standard-mim"]["edition_class"] == "2010"
    assert by_id["repo-2010-standard-mim"]["load_mode"] == "standalone"

    assert by_id["repo-cross-target-radar"]["edition_class"] == "cross-edition"
    assert by_id["repo-cross-target-radar"]["scenario_family"] == "target-radar"

    for entry_id in (
        "repo-2025-proto-base",
        "repo-2025-proto-message-test",
        "repo-2025-proto-space-lite",
        "repo-2025-proto-time-mgmt-test",
        "repo-2025-encoding-auth-smoke",
    ):
        assert by_id[entry_id]["edition_class"] == "2025"
        assert by_id[entry_id]["baseline_kind"] == "repo-owned"

    assert by_id["repo-2025-proto-base"]["load_mode"] == "base-plus-extension"
    assert by_id["repo-2025-proto-message-test"]["load_mode"] == "base-plus-extension"
    assert by_id["third-party-netn-merged-with-rpr"]["baseline_kind"] == "third-party"
    assert by_id["third-party-netn-merged-with-rpr"]["load_mode"] == "ordered-family"


def test_fom_inventory_2025_and_cross_edition_entries_match_contents_or_notes() -> None:
    entries = json.loads(FOM_INVENTORY.read_text(encoding="utf-8"))["entries"]

    for entry in entries:
        path = REPO_ROOT / entry["path"]
        contents = path.read_text(encoding="utf-8")
        if entry["edition_class"] == "2025":
            assert "2025" in path.name or "IEEE1516-2025" in contents
        if entry["edition_class"] == "cross-edition":
            assert "cross-edition" in entry["notes"]
            assert "2010" in contents or "IEEE1516-2010" in contents


def test_fom_inventory_markdown_view_is_regenerated_from_json_inventory() -> None:
    assert FOM_INVENTORY_MD.read_text(encoding="utf-8") == render_inventory_markdown()
