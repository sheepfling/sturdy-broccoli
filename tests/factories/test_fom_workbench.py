from __future__ import annotations

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from hla.verification.repo_internal.fom_workbench import (
    apply_repo_owned_fom_edits,
    build_fom_workbench_snapshot,
    write_fom_workbench_html,
    write_fom_workbench_snapshot,
)


def test_fom_workbench_snapshot_groups_families_and_precomputes_default_load_sets(tmp_path: Path) -> None:
    snapshot = build_fom_workbench_snapshot()
    assert snapshot.schema_version == 1
    assert snapshot.capabilities["display"] is True
    assert snapshot.capabilities["inspect"] is True
    assert snapshot.capabilities["search"] is True
    assert snapshot.capabilities["edit"] is True
    assert snapshot.capabilities["overlay"] is True

    by_family = {row.scenario_family: row for row in snapshot.families}

    target_radar = by_family["target-radar"]
    assert target_radar.load_mode == "standalone"
    assert target_radar.parse_status == "ok"
    assert target_radar.edition_classes == ("cross-edition",)
    assert target_radar.default_load_set_ids == ("repo-cross-target-radar",)

    proto_message = by_family["proto2025-message-test"]
    assert proto_message.load_mode == "base-plus-extension"
    assert proto_message.parse_status == "ok"
    assert proto_message.default_load_set_ids == (
        "repo-2025-proto-base",
        "repo-2025-proto-message-test",
    )
    assert proto_message.object_class_count > 0
    assert proto_message.interaction_class_count > 0

    rpr = by_family["rpr-normative"]
    assert rpr.load_mode == "ordered-family"
    assert rpr.parse_status == "ok"
    assert len(rpr.default_load_set_ids) == 14
    assert rpr.object_classes
    assert rpr.interaction_classes
    assert rpr.datatype_names
    assert rpr.validation_command == "./tools/fom-validate --family rpr-normative --html"
    assert rpr.validation_html_path is None

    assert any(row.source_name == "target-radar" and row.kind == "object" for row in snapshot.search_index)
    assert any(row.source_name == "proto2025-message-test" and row.kind == "interaction" for row in snapshot.search_index)
    assert any(row.parent_name for row in snapshot.search_index if row.kind in {"object", "interaction"})
    assert any(len(row.lineage) > 1 for row in snapshot.search_index if row.kind in {"object", "interaction"})

    diff = next(
        row
        for row in snapshot.diffs
        if {row.left_family, row.right_family} == {"target-radar", "proto2025-message-test"}
    )
    assert diff.comparable is True
    assert diff.only_left_object_classes or diff.only_right_object_classes

    json_path = write_fom_workbench_snapshot(
        output_dir=tmp_path / "workbench",
        custom_load_sets={
            "custom-target-plus-demo": ("repo-cross-target-radar", "repo-2010-demo"),
            "custom-proto-message": ("repo-2025-proto-base", "repo-2025-proto-message-test"),
        },
        diff_specs=(("custom-target-plus-demo", "custom-proto-message"),),
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert any(row["scenario_family"] == "target-radar" for row in payload["families"])
    assert any(row["kind"] == "object" for row in payload["search_index"])
    assert any({row["left_family"], row["right_family"]} == {"target-radar", "proto2025-message-test"} for row in payload["diffs"])
    assert any(row["name"] == "custom-target-plus-demo" for row in payload["custom_load_sets"])
    assert any({row["left_family"], row["right_family"]} == {"custom-target-plus-demo", "custom-proto-message"} for row in payload["diffs"])
    target_radar_payload = next(row for row in payload["families"] if row["scenario_family"] == "target-radar")
    assert target_radar_payload["validation_command"] == "./tools/fom-validate --family target-radar --html"
    assert target_radar_payload["validation_html_path"] == "validation_packets/target-radar/fom_validation_report.html"
    assert (tmp_path / "workbench" / target_radar_payload["validation_html_path"]).exists()
    custom_payload = next(row for row in payload["custom_load_sets"] if row["name"] == "custom-target-plus-demo")
    assert custom_payload["validation_command"].startswith("./tools/fom-validate ")
    assert custom_payload["validation_html_path"] == "validation_packets/custom-target-plus-demo/fom_validation_report.html"
    assert (tmp_path / "workbench" / custom_payload["validation_html_path"]).exists()

    html_path = write_fom_workbench_html(
        output_dir=tmp_path / "workbench",
        custom_load_sets={
            "custom-target-plus-demo": ("repo-cross-target-radar", "repo-2010-demo"),
            "custom-proto-message": ("repo-2025-proto-base", "repo-2025-proto-message-test"),
        },
        diff_specs=(("custom-target-plus-demo", "custom-proto-message"),),
    )
    html_text = html_path.read_text(encoding="utf-8")
    assert "FOM Workbench Snapshot" in html_text
    assert "Search Merged Names" in html_text
    assert "Overlay / Diff" in html_text
    assert "Node Drill-Down" in html_text
    assert "Guarded Edit Flow" in html_text
    assert "Custom Load Set Builder" in html_text
    assert "save in browser" in html_text
    assert "export saved sets" in html_text
    assert "import saved sets" in html_text
    assert "hla2010-fom-workbench-custom-load-sets.json" in html_text
    assert "hla2010-fom-workbench-custom-load-sets" in html_text
    assert "custom-target-plus-demo" in html_text
    assert "open HTML validation packet" in html_text
    assert "validation_packets/target-radar/fom_validation_report.html" in html_text
    assert "validation_packets/custom-target-plus-demo/fom_validation_report.html" in html_text
    assert '<option value="custom-load-set">custom load sets</option>' in html_text


def test_tools_fom_workbench_writes_snapshot_artifact(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "fom-workbench"
    subprocess.run(
        [
            "bash",
            "tools/fom-workbench",
            "--output-dir",
            str(output_dir),
            "--html",
            "--custom-load-set",
            "custom-target-plus-demo=repo-cross-target-radar,repo-2010-demo",
            "--custom-load-set",
            "custom-proto-message=repo-2025-proto-base,repo-2025-proto-message-test",
            "--diff",
            "custom-target-plus-demo:custom-proto-message",
        ],
        cwd=repo_root,
        check=True,
    )
    payload = json.loads((output_dir / "fom_workbench_snapshot.json").read_text(encoding="utf-8"))
    assert payload["title"] == "FOM Workbench Snapshot"
    assert any(entry["scenario_family"] == "proto2025-message-test" for entry in payload["entries"])
    assert any(row["name"] == "custom-target-plus-demo" for row in payload["custom_load_sets"])
    html_text = (output_dir / "fom_workbench.html").read_text(encoding="utf-8")
    assert "Catalog" in html_text
    assert "Inspect" in html_text
    assert "Overlay / Diff" in html_text
    assert "Guarded Edit Flow" in html_text
    assert "Custom Load Set Builder" in html_text
    assert "export saved sets" in html_text
    assert (output_dir / "validation_packets" / "target-radar" / "fom_validation_report.html").exists()
    assert (output_dir / "validation_packets" / "custom-target-plus-demo" / "fom_validation_report.html").exists()


def test_repo_owned_fom_edit_flow_writes_copy_and_rejects_third_party(tmp_path: Path) -> None:
    edited = apply_repo_owned_fom_edits(
        "repo-2010-demo",
        description="Workbench edited description",
        add_keywords=("workbench", "edited"),
        add_notes=("N9: workbench note",),
        output_path=tmp_path / "edited-demo.xml",
    )
    root = ET.fromstring(edited.read_text(encoding="utf-8"))
    namespace = root.tag.partition("}")[0].lstrip("{")
    qname = lambda local: f"{{{namespace}}}{local}" if namespace else local
    model_identification = next(child for child in list(root) if child.tag == qname("modelIdentification"))
    keywords = [child.text for child in list(model_identification) if child.tag == qname("keyword")]
    description = next(child.text for child in list(model_identification) if child.tag == qname("description"))
    notes = next(child for child in list(root) if child.tag == qname("notes"))
    note_semantics = [child.findtext(qname("semantics")) for child in list(notes) if child.tag == qname("note")]
    assert description == "Workbench edited description"
    assert "workbench" in keywords
    assert "edited" in keywords
    assert "workbench note" in note_semantics

    with pytest.raises(ValueError, match="not repo-owned"):
        apply_repo_owned_fom_edits(
            "third-party-portico-testfom",
            description="Should fail",
            output_path=tmp_path / "blocked.xml",
        )
