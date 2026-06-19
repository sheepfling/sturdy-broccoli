from __future__ import annotations

import json
import subprocess
from pathlib import Path

from hla.verification.repo_internal.fom_validate import build_fom_validation, write_fom_validation, write_fom_validation_html


OMT_2025_SCHEMA = Path("docs/requirements/ieee-1516-2025/encoding_auth_work_packet/09-standards-subset/IEEE1516-OMT-2025.xsd")

STRICT_OMT_2025_FIXTURE = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2025">
  <modelIdentification><name>Schema Valid Probe</name><type>FOM</type><version>1.0</version><modificationDate>2026-06-18</modificationDate><securityClassification>Unclassified</securityClassification><applicationDomain>Training</applicationDomain><description>Probe.</description><poc><pocType>Sponsor</pocType><pocName>Test</pocName></poc><reference><type>URL</type><identification>https://example.invalid/ref</identification></reference></modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name><sharing>Neither</sharing><semantics>Root</semantics><attribute><name>Status</name><dataType>HLAunicodeString</dataType><updateType>Static</updateType><valueRequired>true</valueRequired><ownership>NoTransfer</ownership><sharing>PublishSubscribe</sharing><transportation>HLAreliable</transportation><order>Receive</order><semantics>Status</semantics></attribute></objectClass></objects>
  <interactions><interactionClass><name>HLAinteractionRoot</name><sharing>Neither</sharing><transportation>HLAreliable</transportation><order>Receive</order><semantics>Root</semantics><parameter><name>Message</name><dataType>HLAunicodeString</dataType><semantics>Message</semantics></parameter></interactionClass></interactions>
  <dimensions><dimension><name>RoutingSpace</name><inputDataTypes><dataType>RouteEnum</dataType></inputDataTypes><inputDataDescription>Route</inputDataDescription><upperBound>1</upperBound><normalization>None</normalization><outputDataSemantics>None</outputDataSemantics><value>[0..1)</value></dimension></dimensions>
  <synchronizations><synchronizationPoint><label>Ready</label><dataType>HLAunicodeString</dataType><capability>RegisterAchieve</capability><semantics>Ready</semantics></synchronizationPoint></synchronizations>
  <transportations><transportation><name>HLAreliable</name><reliable>Yes</reliable><semantics>Reliable</semantics></transportation></transportations>
  <switches><automaticResignAction resignAction="NoAction"/></switches>
  <updateRates><updateRate><name>DefaultRate</name><rate>1</rate><semantics>Rate</semantics></updateRate></updateRates>
  <dataTypes><basicDataRepresentations><basicData><name>HLAinteger32BE</name><size>32</size><interpretation>integer</interpretation><endian>Big</endian><encoding>HLAinteger32BE</encoding></basicData><basicData><name>HLAunicodeString</name><size>0</size><interpretation>string</interpretation><endian>Big</endian><encoding>HLAunicodeString</encoding></basicData></basicDataRepresentations><simpleDataTypes><simpleData><name>RouteSimple</name><representation>HLAinteger32BE</representation><semantics>Route</semantics></simpleData></simpleDataTypes><referenceDataTypes><referenceDataType><name>StatusRef</name><representation>HLAunicodeString</representation><referenceClass>HLAobjectRoot</referenceClass><referencedAttribute>Status</referencedAttribute><semantics>Status ref</semantics></referenceDataType></referenceDataTypes><enumeratedDataTypes><enumeratedData><name>RouteEnum</name><representation>HLAinteger32BE</representation><semantics>Route enum</semantics><enumerator><name>A</name><value>0</value></enumerator></enumeratedData></enumeratedDataTypes><arrayDataTypes></arrayDataTypes><fixedRecordDataTypes><fixedRecordData><name>FixedPayload</name><encoding>HLAfixedRecord</encoding><semantics>Fixed</semantics><field><name>FieldA</name><dataType>HLAunicodeString</dataType><semantics>Field</semantics></field></fixedRecordData></fixedRecordDataTypes><variantRecordDataTypes><variantRecordData><name>VariantPayload</name><discriminant>Kind</discriminant><dataType>RouteEnum</dataType><alternative><enumerator>A</enumerator><name>Text</name><dataType>HLAunicodeString</dataType><semantics>Text</semantics></alternative><encoding>HLAvariantRecord</encoding><semantics>Variant</semantics></variantRecordData></variantRecordDataTypes></dataTypes>
</objectModel>
"""


def test_build_fom_validation_auto_detects_2010_path_for_cross_edition_target_radar() -> None:
    report = build_fom_validation(["TargetRadarFOMmodule.xml"])
    row = report.source_reports[0]
    assert row.effective_edition == "2010"
    assert row.inventory_edition_class == "cross-edition"
    assert row.profile == "dif"
    assert row.passed is True
    assert row.verdict in {"conforming", "partially-conforming"}


def test_build_fom_validation_reports_conforming_2025_fixture(tmp_path: Path) -> None:
    source = tmp_path / "valid-2025.xml"
    source.write_text(STRICT_OMT_2025_FIXTURE, encoding="utf-8")

    report = build_fom_validation([source], edition="2025", strict_identification=True)
    row = report.source_reports[0]
    assert row.effective_edition == "2025"
    assert row.schema_valid is True
    assert row.parsed is True
    assert row.semantic_valid is True
    assert row.verdict == "conforming"
    assert row.passed is True
    assert row.issues == ()


def test_fom_validate_tool_returns_nonzero_and_writes_issue_report_for_invalid_2025_xml(tmp_path: Path) -> None:
    source = tmp_path / "invalid-2025.xml"
    source.write_text(
        STRICT_OMT_2025_FIXTURE.replace("<type>FOM</type>", "<type>BadModel</type>", 1),
        encoding="utf-8",
    )
    output_dir = tmp_path / "fom-validation"
    repo_root = Path(__file__).resolve().parents[2]

    result = subprocess.run(
        [
            str(repo_root / "tools" / "fom-validate"),
            str(source),
            "--edition",
            "2025",
            "--schema",
            str(repo_root / OMT_2025_SCHEMA),
            "--output-dir",
            str(output_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads((output_dir / "fom_validation_report.json").read_text(encoding="utf-8"))
    row = payload["source_reports"][0]
    assert row["effective_edition"] == "2025"
    assert row["schema_valid"] is False
    assert row["passed"] is False
    assert row["verdict"] == "nonconforming"
    assert any(issue["requirement"] == "HLA2025-OMT-CV-020" for issue in row["issues"])


def test_write_fom_validation_writes_json_and_markdown(tmp_path: Path) -> None:
    json_path, md_path, report = write_fom_validation(
        ["TargetRadarFOMmodule.xml"],
        output_dir=tmp_path / "out",
    )
    assert json_path.exists()
    assert md_path.exists()
    assert report.source_reports[0].passed is True
    text = md_path.read_text(encoding="utf-8")
    assert "# FOM Validation Report" in text
    assert "Effective Edition" in text
    assert "Recommended next step" in text


def test_build_fom_validation_adds_explicit_multi_source_load_set_report() -> None:
    report = build_fom_validation(["DemoFOMmodule.xml", "TargetRadarFOMmodule.xml"])
    assert len(report.load_set_reports) == 1
    row = report.load_set_reports[0]
    assert row.name == "explicit-load-set"
    assert row.kind == "explicit"
    assert row.effective_edition == "2010"
    assert row.parsed is True
    assert row.passed is True
    assert len(row.source_paths) == 2


def test_build_fom_validation_adds_family_load_set_report() -> None:
    report = build_fom_validation([], families=["rpr-normative"])
    assert report.families == ("rpr-normative",)
    assert len(report.load_set_reports) == 1
    row = report.load_set_reports[0]
    assert row.name == "rpr-normative"
    assert row.kind == "family"
    assert row.load_mode == "ordered-family"
    assert row.parsed is True
    assert row.passed is True
    assert len(row.source_paths) > 2


def test_write_fom_validation_html_writes_browser_report(tmp_path: Path) -> None:
    html_path = write_fom_validation_html(
        [],
        output_dir=tmp_path / "html",
        families=["rpr-normative"],
        title="Validator HTML",
    )
    assert html_path.exists()
    text = html_path.read_text(encoding="utf-8")
    assert "<title>Validator HTML | FOM Validate</title>" in text
    assert "load_set_reports" in text
    assert "Source reports" in text


def test_write_fom_validation_html_renders_member_side_by_side_diff_for_multi_module_load_set(tmp_path: Path) -> None:
    html_path = write_fom_validation_html(
        ["DemoFOMmodule.xml", "TargetRadarFOMmodule.xml"],
        output_dir=tmp_path / "html-diff",
        title="Validator Multi",
    )
    text = html_path.read_text(encoding="utf-8")
    assert "Side-by-Side Member Tree Diff" in text
    assert "loadset-left" in text
    assert "loadset-right" in text
    assert "Shared Objects" in text
