from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from hla2010_repo_internal.requirements_packet import KNOWN_PACKET_PARENT_GAPS, load_imported_hla_packet

IMPORT_ROOT = Path(__file__).resolve().parents[2] / "requirements" / "imports" / "hla_1516_requirements_codebase_packet_v1_0"
LATEST_ROOT = IMPORT_ROOT / "latest"

MASTER_COLUMNS = [
    "requirement_id",
    "standard",
    "clause",
    "source_title",
    "capability",
    "feature",
    "requirement_text",
    "normative_keyword",
    "implementation_area",
    "verification_method",
    "test_id",
    "status",
    "priority",
    "source_note",
    "requirement_type",
    "parent_requirement_id",
    "source_detail",
    "service_name",
    "service_direction",
    "transport_scope",
    "mom_observable",
    "verification_notes",
]

VERIFICATION_COLUMNS = [
    "test_id",
    "requirement_id",
    "capability",
    "feature",
    "test_level",
    "transport",
    "status",
    "expected_evidence",
    "verification_notes",
]

CLAUSE_TRACKER_COLUMNS = [
    "standard",
    "clause",
    "title",
    "document_area",
    "normative_status",
    "priority",
    "detail_status_v1_0",
    "rows_in_catalog_v1_0",
    "decomposition_level",
    "next_action",
    "notes",
]

SUMMARY_COLUMNS = [
    "metric",
    "value",
    "notes",
]

CPP_API_COLUMNS = [
    "header",
    "class_or_scope",
    "clause",
    "method_name",
    "signature",
    "exceptions",
]

API_SERVICE_COLUMNS = [
    "interface",
    "direction",
    "clause",
    "service_title",
    "method_name",
    "overload_index",
    "return_type",
    "arguments",
    "exceptions",
    "signature",
]

MIM_CATALOG_COLUMNS = [
    "category",
    "path_or_owner",
    "name",
    "parent_path",
    "data_type",
    "update_type",
    "ownership",
    "sharing",
    "transportation",
    "order",
    "dimensions",
    "semantics",
]

XSD_CATALOG_COLUMNS = [
    "category",
    "schema",
    "name",
    "type_or_kind",
    "minOccurs",
    "maxOccurs",
    "ref_or_mixed",
]

WSDL_CATALOG_COLUMNS = [
    "operation",
    "input",
    "output",
]

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
    packet = load_imported_hla_packet()
    manifest = packet.manifest
    included_files = manifest.included_files
    restricted_prefix = "requirements/restricted_reference_inputs/"
    restricted_entries = [item for item in included_files if item.path.startswith(restricted_prefix)]
    committed_entries = [item for item in included_files if not item.path.startswith(restricted_prefix)]

    assert manifest.packet_name == "hla_1516_requirements_codebase_packet_v1_0"
    assert manifest.packet_version == "v1.0"
    assert len(included_files) == 47
    assert len(restricted_entries) == 5

    for item in restricted_entries:
        path = packet.resolve_manifest_path(item.path)
        assert not path.exists(), f"restricted packet asset should stay uncommitted: {path}"

    for item in committed_entries:
        path = packet.resolve_manifest_path(item.path)
        assert path.exists(), f"missing imported packet asset: {path}"
        if item.path in {"MANIFEST.json", "README.md"}:
            continue
        assert path.stat().st_size == item.bytes, f"size drift for {path}"
        assert _sha256(path) == item.sha256, f"checksum drift for {path}"


def test_imported_hla_packet_canonical_summary_matches_current_csv_rows():
    summary = load_imported_hla_packet().manifest.canonical_asset_summary

    assert _csv_row_count(LATEST_ROOT / "hla_1516_requirements_master_v1_0.csv") == summary.master_requirements_rows
    assert _csv_row_count(LATEST_ROOT / "hla_1516_verification_matrix_v1_0.csv") == summary.verification_rows
    assert _csv_row_count(LATEST_ROOT / "hla_1516_clause_tracker_v1_0.csv") == summary.clause_tracker_rows
    assert _csv_row_count(LATEST_ROOT / "hla_1516_cpp_api_catalog_v1_0.csv") == summary.cpp_api_catalog_rows


def test_imported_hla_packet_master_csv_matches_schema_contract_and_known_source_gaps():
    packet = load_imported_hla_packet()
    rows = packet.master_rows

    assert rows
    assert list(rows[0].__dataclass_fields__.keys()) == MASTER_COLUMNS

    requirement_ids = [row.requirement_id.strip() for row in rows]
    assert all(requirement_ids)
    assert len(requirement_ids) == len(set(requirement_ids))

    assert {row.standard.strip() for row in rows} == {
        "IEEE 1516-2010",
        "IEEE 1516.1-2010",
        "IEEE 1516.2-2010",
    }
    assert {row.priority.strip() for row in rows} <= {"P0", "P1", "P2", "P3"}
    assert {row.status.strip() for row in rows} == {"Draft"}
    assert {row.normative_keyword.strip() for row in rows} == {"shall"}

    parent_ids = {
        row.parent_requirement_id.strip()
        for row in rows
        if row.parent_requirement_id.strip()
    }
    missing_parent_ids = parent_ids - set(requirement_ids)
    assert missing_parent_ids == KNOWN_PACKET_PARENT_GAPS

    assert all(
        row.verification_method.strip()
        for row in rows
        if row.priority.strip() in {"P0", "P1"}
    )
    assert packet.requirements_by_id["HLA1516-FW-FW_SCOPE-001"].feature == "FW-SCOPE"
    assert packet.requirements_by_standard["IEEE 1516.1-2010"]
    assert packet.requirements_by_clause["1.1"]
    assert packet.requirements_by_capability["CAP-FW"]
    assert packet.requirements_by_feature["FW-SCOPE"]


def test_imported_hla_packet_verification_matrix_has_required_columns_and_live_requirement_refs():
    packet = load_imported_hla_packet()
    master_rows = packet.master_rows
    verification_rows = packet.verification_rows
    requirement_ids = {row.requirement_id.strip() for row in master_rows}

    assert verification_rows
    assert list(verification_rows[0].__dataclass_fields__.keys()) == VERIFICATION_COLUMNS

    test_ids = [row.test_id.strip() for row in verification_rows]
    assert all(test_ids)
    assert {row.transport.strip() for row in verification_rows} <= {"static", "native", "grpc", "rest"}
    assert {row.status.strip() for row in verification_rows} == {"planned"}
    assert all(row.requirement_id.strip() in requirement_ids for row in verification_rows)

    covered_requirement_ids = {row.requirement_id.strip() for row in verification_rows}
    missing_p0_p1 = sorted(
        row.requirement_id.strip()
        for row in master_rows
        if row.priority.strip() in {"P0", "P1"} and row.requirement_id.strip() not in covered_requirement_ids
    )
    assert missing_p0_p1 == []
    assert packet.verification_by_requirement_id["HLA1516-FW-FW_SCOPE-001"]
    sample_test_id = verification_rows[0].test_id.strip()
    assert packet.verification_by_test_id[sample_test_id]


def test_imported_hla_packet_clause_tracker_covers_major_standard_areas():
    rows = load_imported_hla_packet().clause_tracker_rows

    assert rows
    assert list(rows[0].__dataclass_fields__.keys()) == CLAUSE_TRACKER_COLUMNS

    assert {row.standard.strip() for row in rows} == {
        "IEEE 1516-2010",
        "IEEE 1516.1-2010",
        "IEEE 1516.2-2010",
    }
    assert {row.priority.strip() for row in rows} <= {"P0", "P1", "P2", "P3"}
    assert {row.normative_status.strip() for row in rows} <= {"normative", "informative"}
    assert {row.decomposition_level.strip() for row in rows} <= {
        "clause + service + artifact",
        "tracked/no direct rows",
    }

    tracker_pairs = {(row.standard.strip(), row.clause.strip()) for row in rows}
    assert {
        ("IEEE 1516-2010", "5"),
        ("IEEE 1516-2010", "6"),
        ("IEEE 1516.1-2010", "4"),
        ("IEEE 1516.1-2010", "5"),
        ("IEEE 1516.1-2010", "6"),
        ("IEEE 1516.1-2010", "7"),
        ("IEEE 1516.1-2010", "8"),
        ("IEEE 1516.1-2010", "9"),
        ("IEEE 1516.1-2010", "10"),
        ("IEEE 1516.1-2010", "11"),
        ("IEEE 1516.2-2010", "4"),
        ("IEEE 1516.2-2010", "5"),
        ("IEEE 1516.2-2010", "6"),
        ("IEEE 1516.2-2010", "7"),
    } <= tracker_pairs


def test_imported_hla_packet_loader_covers_remaining_canonical_csv_families():
    packet = load_imported_hla_packet()

    assert packet.summary_rows
    assert list(packet.summary_rows[0].__dataclass_fields__.keys()) == SUMMARY_COLUMNS
    assert len(packet.summary_rows) == 9
    assert packet.summary_by_metric["Total requirement rows"].value == "4003"
    assert packet.summary_by_metric["C++ API catalog rows"].value == "290"

    assert packet.delta_rows
    assert packet.clauses5_11_detailed_rows
    assert packet.clause6_11_detailed_rows
    assert packet.omt_xml_detailed_rows
    assert len(packet.delta_rows) == 1445
    assert len(packet.clauses5_11_detailed_rows) == 1257
    assert len(packet.clause6_11_detailed_rows) == 1223
    assert len(packet.omt_xml_detailed_rows) == 1292
    assert packet.delta_rows[0].requirement_id.startswith("HLA")
    assert packet.clauses5_11_detailed_rows[0].standard == "IEEE 1516.1-2010"
    assert packet.omt_xml_detailed_rows[-1].standard == "IEEE 1516.2-2010"

    assert packet.cpp_api_rows
    assert list(packet.cpp_api_rows[0].__dataclass_fields__.keys()) == CPP_API_COLUMNS
    assert len(packet.cpp_api_rows) == 290
    assert packet.cpp_api_by_clause["4.2"][0].method_name == "connect"

    assert packet.api_service_catalog_rows
    assert list(packet.api_service_catalog_rows[0].__dataclass_fields__.keys()) == API_SERVICE_COLUMNS
    assert len(packet.api_service_catalog_rows) == 215
    assert packet.api_service_catalog_by_clause["4.2"][0].method_name == "connect"

    assert packet.mim_catalog_rows
    assert list(packet.mim_catalog_rows[0].__dataclass_fields__.keys()) == MIM_CATALOG_COLUMNS
    assert len(packet.mim_catalog_rows) == 288
    assert any(row.name == "HLAfederate" for row in packet.mim_catalog_rows)

    assert packet.xsd_catalog_rows
    assert list(packet.xsd_catalog_rows[0].__dataclass_fields__.keys()) == XSD_CATALOG_COLUMNS
    assert len(packet.xsd_catalog_rows) == 1269
    assert any(row.name == "objectClass" for row in packet.xsd_catalog_rows)

    assert packet.wsdl_catalog_rows
    assert list(packet.wsdl_catalog_rows[0].__dataclass_fields__.keys()) == WSDL_CATALOG_COLUMNS
    assert len(packet.wsdl_catalog_rows) == 308
    assert any(row.operation == "createFederationExecution" for row in packet.wsdl_catalog_rows)
