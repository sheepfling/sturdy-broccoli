from __future__ import annotations

import json
import subprocess
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord, inventory_records
from hla.verification.repo_internal.fom_workbench import (
    apply_repo_owned_fom_edits,
    build_fom_workbench_snapshot,
    write_fom_workbench_html,
    write_fom_workbench_snapshot,
)


CONFLICTING_2010_LOAD_SET_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>SharedType</name><representation>{representation}</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
"""


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
    assert target_radar.catalog_status == "ok"
    assert target_radar.validation_verdict is None
    assert target_radar.validation_issue_count == 0
    assert target_radar.validation_issue_groups == ()
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
    assert target_radar_payload["validation_verdict"] == "conforming"
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
    assert "FOM Explorer" in html_text
    assert "FOM Workbench snapshot and tool routes remain valid." in html_text
    assert "FOM Workbench Snapshot" in html_text
    assert ">Search<" in html_text
    assert ">Diff<" in html_text
    assert ">Conflict<" in html_text
    assert ">Validation<" in html_text
    assert "Node Drill-Down" in html_text
    assert ">Repair<" in html_text
    assert "Custom Load Set Builder" in html_text
    assert 'id="selection-summary"' in html_text
    assert 'id="workspace-tabs"' in html_text
    assert "one active task at a time" in html_text
    assert "Overview" in html_text
    assert "Conflict" in html_text
    assert "Validation" in html_text
    assert "Repair" in html_text
    assert "No symbol pinned." in html_text
    assert "ownership:" in html_text
    assert "Conflict state" in html_text
    assert "Validation state" in html_text
    assert "Datatype normalization" in html_text
    assert "Object deltas" in html_text
    assert "Investigate Symbol" in html_text
    assert "Open Validation Report" in html_text
    assert "Operator commands" in html_text
    assert "open validation HTML" in html_text
    assert "Copy Repair Command" in html_text
    assert 'id="recent-selections"' in html_text
    assert 'id="recent-comparisons"' in html_text
    assert "likely clean" in html_text
    assert "move up" in html_text
    assert "move down" in html_text
    assert "all statuses" in html_text
    assert "all edition scopes" in html_text
    assert "Edition scope" in html_text
    assert "save set" in html_text
    assert "export sets" in html_text
    assert "import sets" in html_text
    assert "hla2010-fom-workbench-custom-load-sets.json" in html_text
    assert "hla2010-fom-workbench-custom-load-sets" in html_text
    assert "custom-target-plus-demo" in html_text
    assert "validation_packets/target-radar/fom_validation_report.html" in html_text
    assert "validation_packets/custom-target-plus-demo/fom_validation_report.html" in html_text
    assert '<option value="custom-load-set">custom load sets</option>' in html_text
    assert 'id="workspace-focus-controls"' in html_text
    assert 'id="workspace-focus-filter"' in html_text
    assert 'id="workspace-focus-advanced"' in html_text
    assert 'data-focus-kind="object"' in html_text
    assert 'data-focus-kind="changed"' in html_text
    assert 'id="focus-kind-select"' in html_text
    assert 'id="focus-save-preset"' in html_text
    assert "Advanced focus" in html_text
    assert "kind:object owner:repo-owned changed:true" in html_text


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
    assert "Overview" in html_text
    assert "Diff" in html_text
    assert "Repair" in html_text
    assert "ownership:" in html_text
    assert "Operator commands" in html_text
    assert "Recent Selections" in html_text
    assert "Custom Load Set Builder" in html_text
    assert "export sets" in html_text
    assert (output_dir / "validation_packets" / "target-radar" / "fom_validation_report.html").exists()
    assert (output_dir / "validation_packets" / "custom-target-plus-demo" / "fom_validation_report.html").exists()


def test_fom_workbench_custom_load_set_surfaces_merge_failure_guidance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    suffix = uuid.uuid4().hex[:8]
    first_name = f"merge-conflict-a-{suffix}.xml"
    second_name = f"merge-conflict-b-{suffix}.xml"
    first = repo_root / first_name
    second = repo_root / second_name
    first.write_text(CONFLICTING_2010_LOAD_SET_TEMPLATE.format(name="A", representation="HLAinteger32BE"), encoding="utf-8")
    second.write_text(CONFLICTING_2010_LOAD_SET_TEMPLATE.format(name="B", representation="HLAinteger64BE"), encoding="utf-8")
    try:
        base_records = inventory_records()
        monkeypatch.setattr(
            "hla.verification.repo_internal.fom_workbench.inventory_records",
            lambda: base_records
            + (
                FOMInventoryRecord(
                    id="merge-conflict-a",
                    path=first_name,
                    edition_class="2010",
                    load_mode="standalone",
                    baseline_kind="repo-owned",
                    scenario_family="merge-conflict",
                    notes="synthetic conflict fixture a",
                ),
                FOMInventoryRecord(
                    id="merge-conflict-b",
                    path=second_name,
                    edition_class="2010",
                    load_mode="standalone",
                    baseline_kind="repo-owned",
                    scenario_family="merge-conflict",
                    notes="synthetic conflict fixture b",
                ),
            ),
        )
        snapshot = build_fom_workbench_snapshot(
            custom_load_sets={"conflict-set": ("merge-conflict-a", "merge-conflict-b")},
            diff_specs=(("conflict-set", "target-radar"),),
        )
        html_path = write_fom_workbench_html(
            output_dir=tmp_path / "workbench-conflict",
            custom_load_sets={"conflict-set": ("merge-conflict-a", "merge-conflict-b")},
            diff_specs=(("conflict-set", "target-radar"),),
        )
        html_text = html_path.read_text(encoding="utf-8")
    finally:
        first.unlink(missing_ok=True)
        second.unlink(missing_ok=True)

    row = next(item for item in snapshot.custom_load_sets if item.name == "conflict-set")
    assert row.parse_status == "error"
    assert row.parse_error_kind == "merge"
    assert row.catalog_status == "merge-failed"
    assert row.validation_verdict is None
    assert row.validation_issue_groups == ()
    assert "Conflicting simple datatype definition" in (row.parse_error or "")
    assert "Unify the duplicate datatype definition" in row.recommended_next_step
    assert row.merge_conflict_kind == "simple datatype"
    assert row.merge_conflict_symbol == "SharedType"
    assert row.merge_conflict_members == ("A", "B")
    assert row.merge_conflict_member_details == (
        {
            "member": "A",
            "entry_id": "merge-conflict-a",
            "entry_path": first_name,
            "baseline_kind": "repo-owned",
            "symbol": "SharedType",
            "declaration": {
                "category": "simple",
                "representation": "HLAinteger32BE",
                "units": None,
                "resolution": None,
                "accuracy": None,
                "semantics": None,
            },
        },
        {
            "member": "B",
            "entry_id": "merge-conflict-b",
            "entry_path": second_name,
            "baseline_kind": "repo-owned",
            "symbol": "SharedType",
            "declaration": {
                "category": "simple",
                "representation": "HLAinteger64BE",
                "units": None,
                "resolution": None,
                "accuracy": None,
                "semantics": None,
            },
        },
    )
    diff = next(item for item in snapshot.diffs if {item.left_family, item.right_family} == {"conflict-set", "target-radar"})
    assert diff.comparable is False
    assert diff.left_parse_error_kind == "merge"
    assert "Conflicting simple datatype definition" in (diff.left_parse_error or "")
    assert "Unify the duplicate datatype definition" in (diff.left_recommended_next_step or "")
    assert diff.left_merge_conflict_kind == "simple datatype"
    assert diff.left_merge_conflict_symbol == "SharedType"
    assert diff.left_merge_conflict_members == ("A", "B")
    assert diff.left_merge_conflict_member_details == row.merge_conflict_member_details
    assert ">Conflict<" in html_text
    assert "Ownership mix" in html_text
    assert "Prepare Repair" in html_text
    assert "merge_conflict_symbol" in html_text
    assert "open in search" in html_text
    assert "--set-simple-datatype-representation" in html_text


def test_fom_workbench_custom_load_set_preserves_order_in_snapshot_command(tmp_path: Path) -> None:
    json_path = write_fom_workbench_snapshot(
        output_dir=tmp_path / "ordered-workbench",
        custom_load_sets={
            "ordered-demo": ("repo-cross-target-radar", "repo-2010-demo"),
        },
        diff_specs=(("ordered-demo", "target-radar"),),
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    row = next(item for item in payload["custom_load_sets"] if item["name"] == "ordered-demo")
    assert row["member_ids"] == ["repo-cross-target-radar", "repo-2010-demo"]
    assert row["validation_command"].startswith("./tools/fom-validate ")


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


def test_repo_owned_fom_edit_flow_updates_simple_datatype_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    suffix = uuid.uuid4().hex[:8]
    source_name = f"editable-simple-datatype-{suffix}.xml"
    source_path = repo_root / source_name
    source_path.write_text(
        CONFLICTING_2010_LOAD_SET_TEMPLATE.format(name="Editable", representation="HLAinteger32BE"),
        encoding="utf-8",
    )
    try:
        base_records = inventory_records()
        monkeypatch.setattr(
            "hla.verification.repo_internal.fom_workbench.inventory_records",
            lambda: base_records
            + (
                FOMInventoryRecord(
                    id="editable-simple-datatype",
                    path=source_name,
                    edition_class="2010",
                    load_mode="standalone",
                    baseline_kind="repo-owned",
                    scenario_family="editable-simple-datatype",
                    notes="synthetic editable datatype fixture",
                ),
            ),
        )
        edited = apply_repo_owned_fom_edits(
            "editable-simple-datatype",
            set_simple_datatype_representations=(("SharedType", "HLAinteger64BE"),),
            set_simple_datatype_semantics=(("SharedType", "Aligned semantics"),),
            output_path=tmp_path / "edited-simple-datatype.xml",
        )
        root = ET.fromstring(edited.read_text(encoding="utf-8"))
        namespace = root.tag.partition("}")[0].lstrip("{")
        qname = lambda local: f"{{{namespace}}}{local}" if namespace else local
        simple_data = next(node for node in root.findall(f".//{qname('simpleData')}") if node.findtext(qname('name')) == "SharedType")
        assert simple_data.findtext(qname("representation")) == "HLAinteger64BE"
        assert simple_data.findtext(qname("semantics")) == "Aligned semantics"
    finally:
        source_path.unlink(missing_ok=True)
