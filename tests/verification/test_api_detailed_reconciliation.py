from __future__ import annotations

import csv
import re
import zipfile
from collections import Counter
from pathlib import Path

from hla.verification.repo_internal.requirements import load_2010_reconciliation_rows

try:
    from reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources
except ModuleNotFoundError:
    from tests.reconciliation_truth_sources import assert_rows_do_not_use_closeout_truth_sources


ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION_PATH = ROOT / "requirements" / "2010" / "hla1516_1_api_detailed_reconciliation.csv"
CPP_API_ZIP = ROOT / "specs" / "ieee-1516-2010" / "hla_specs" / "1516.1-2010_downloads" / "IEEE1516-2010_C++_API.zip"
PROMOTED_CPP_CLASS_CLUSTER = {
    "HLA1516.1-CPP-12_12-DATAELEMENT-258",
    "HLA1516.1-CPP-12_12-ENCODABLEDATATYPE-254",
    "HLA1516.1-CPP-12_12-ENCODABLEDATATYPE-255",
    "HLA1516.1-CPP-12_12-ENCODEREXCEPTION-259",
    "HLA1516.1-CPP-12_12-EXCEPTION-213",
    "HLA1516.1-CPP-12_12-FEDERATERESTORESTATUS-240",
    "HLA1516.1-CPP-12_12-FEDERATIONEXECUTIONINFORMATION-241",
    "HLA1516.1-CPP-12_12-HANDLEKIND-216",
    "HLA1516.1-CPP-12_12-HANDLEKIND-218",
    "HLA1516.1-CPP-12_12-HANDLEKIND-220",
    "HLA1516.1-CPP-12_12-HLAFIXEDARRAY-262",
    "HLA1516.1-CPP-12_12-HLAFIXEDARRAYIMPLEMENTATION-261",
    "HLA1516.1-CPP-12_12-HLAFIXEDRECORD-265",
    "HLA1516.1-CPP-12_12-HLAFIXEDRECORDIMPLEMENTATION-264",
    "HLA1516.1-CPP-12_12-HLAFLOAT64INTERVAL-276",
    "HLA1516.1-CPP-12_12-HLAFLOAT64INTERVAL-279",
    "HLA1516.1-CPP-12_12-HLAFLOAT64INTERVAL-281",
    "HLA1516.1-CPP-12_12-HLAFLOAT64INTERVALIMPL-275",
    "HLA1516.1-CPP-12_12-HLAFLOAT64TIME-278",
    "HLA1516.1-CPP-12_12-HLAFLOAT64TIME-280",
    "HLA1516.1-CPP-12_12-HLAFLOAT64TIMEIMPL-277",
    "HLA1516.1-CPP-12_12-HLAINTEGER64INTERVAL-284",
    "HLA1516.1-CPP-12_12-HLAINTEGER64INTERVAL-287",
    "HLA1516.1-CPP-12_12-HLAINTEGER64INTERVAL-289",
    "HLA1516.1-CPP-12_12-HLAINTEGER64INTERVALIMPL-283",
    "HLA1516.1-CPP-12_12-HLAINTEGER64TIME-286",
    "HLA1516.1-CPP-12_12-HLAINTEGER64TIME-288",
    "HLA1516.1-CPP-12_12-HLAINTEGER64TIMEIMPL-285",
    "HLA1516.1-CPP-12_12-HLALOGICALTIMEFACTORYFACTORY-229",
    "HLA1516.1-CPP-12_12-HLAOPAQUEDATA-268",
    "HLA1516.1-CPP-12_12-HLAOPAQUEDATAIMPLEMENTATION-267",
    "HLA1516.1-CPP-12_12-HLAVARIABLEARRAY-271",
    "HLA1516.1-CPP-12_12-HLAVARIABLEARRAYIMPLEMENTATION-270",
    "HLA1516.1-CPP-12_12-HLAVARIANTRECORD-274",
    "HLA1516.1-CPP-12_12-HLAVARIANTRECORDIMPLEMENTATION-273",
    "HLA1516.1-CPP-12_12-LOGICALTIME-223",
    "HLA1516.1-CPP-12_12-LOGICALTIME-231",
    "HLA1516.1-CPP-12_12-LOGICALTIMEINTERVAL-224",
    "HLA1516.1-CPP-12_12-LOGICALTIMEINTERVAL-232",
    "HLA1516.1-CPP-12_12-RANGEBOUNDS-238",
    "HLA1516.1-CPP-12_12-SUPPLEMENTALRECEIVEINFO-243",
    "HLA1516.1-CPP-12_12-SUPPLEMENTALREFLECTINFO-242",
    "HLA1516.1-CPP-12_12-SUPPLEMENTALREMOVEINFO-244",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-225",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-249",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-256",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-257",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-260",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-263",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-266",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-269",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-272",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATAFRIEND-251",
    "HLA1516.1-CPP-12_12-VARIABLELENGTHDATAIMPLEMENTATION-247",
}


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _typed_rows_by_id() -> dict[str, object]:
    return {
        row.source_requirement_id: row
        for row in load_2010_reconciliation_rows(
            ROOT,
            "requirements/2010/hla1516_1_api_detailed_reconciliation.csv",
            "docs/requirements/ieee-1516-2010/api_binding_bounded_family.md",
        )
    }


def _split_refs(refs: str) -> list[str]:
    return [item.strip() for item in refs.split(";") if item.strip()]


def test_api_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 614
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"partial": 331, "mapped": 283}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("WSDL_OP", "partial"): 308,
            ("CPP_METHOD", "mapped"): 211,
            ("CPP_CLASS", "partial"): 17,
            ("CPP_CLASS", "mapped"): 62,
            ("CLAUSE12_13_DETAIL", "partial"): 6,
            ("CLAUSE12_13_DETAIL", "mapped"): 10,
        }
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_api_detailed_reconciliation_spot_checks_key_rows():
    rows = {row["packet_requirement_id"]: row for row in _read_rows()}

    assert rows["HLA1516.1-CPP-4_2-CONNECT-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-4_2-CONNECT-001"]["curated_requirement_id"] == "HLA1516.1-FM-001"
    assert (
        rows["HLA1516.1-CPP-4_2-CONNECT-001"]["current_test_id"]
        == "tests/verification/test_spec_traceability_all_methods.py::test_all_generated_ambassador_methods_are_section_mapped;tests/verification/test_requirements_ledger_v013.py::test_requirements_ledger_covers_generated_api_surface"
    )
    assert rows["HLA1516.1-API_MAPPING_OVERVIEW-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_REFLECT_METHODS-008"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_RECEIVE_METHODS-009"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_REMOVE_METHODS-010"]["current_status"] == "mapped"
    assert rows["HLA1516.1-API_DESIGNATORS-002"]["current_status"] == "mapped"
    assert "test_api_designator_metadata_preserves_standard_designator_types_across_java_and_cpp_bindings" in rows[
        "HLA1516.1-API_DESIGNATORS-002"
    ]["current_test_id"]
    assert "local-settings, logical-time, FOM-module, and update-rate designators" in rows[
        "HLA1516.1-API_DESIGNATORS-002"
    ]["notes"]
    assert rows["HLA1516.1-CPP-12_12-RTIAMBASSADOR-234"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-NULLFEDERATEAMBASSADOR-233"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-RTIAMBASSADORFACTORY-237"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-LOGICALTIMEFACTORY-228"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-HLAFLOAT64TIMEFACTORY-282"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-HLAINTEGER64TIMEFACTORY-290"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-LOGICALTIME-222"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-LOGICALTIMEINTERVAL-221"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-DATAELEMENT-258"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-ENCODEREXCEPTION-259"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-HLAVARIANTRECORD-274"]["current_status"] == "mapped"
    assert rows["HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-249"]["current_status"] == "mapped"
    assert "test_selected_cpp_catalog_rows_are_declared_in_the_official_2010_cpp_api_headers" in rows[
        "HLA1516.1-CPP-12_12-RTIAMBASSADOR-234"
    ]["current_test_id"]
    assert rows["HLA1516.1-API_CPP-012"]["current_status"] == "partial"
    assert rows["HLA1516.1-API_WSDL-013"]["current_status"] == "partial"
    assert rows["HLA1516.1-WSDL-OP-001"]["current_status"] == "partial"
    assert rows["HLA1516.1-API_CPP-012"]["notes"].startswith(
        "Canonical residual disposition:"
    )
    assert "broader imported C++ header/class catalog claim remains intentionally partial" in rows[
        "HLA1516.1-API_CPP-012"
    ]["notes"]
    assert "declares RTIambassador in RTIambassadorFactory.h" in rows[
        "HLA1516.1-CPP-12_12-RTIAMBASSADOR-234"
    ]["notes"]
    assert "declares DataElement in DataElement.h" in rows[
        "HLA1516.1-CPP-12_12-DATAELEMENT-258"
    ]["notes"]
    assert "declares VariableLengthData in VariableLengthData.h" in rows[
        "HLA1516.1-CPP-12_12-VARIABLELENGTHDATA-249"
    ]["notes"]
    assert "broader Web Services binding claim remains intentionally partial" in rows[
        "HLA1516.1-API_WSDL-013"
    ]["notes"]
    assert "operation-level Web Services binding row remains intentionally partial" in rows[
        "HLA1516.1-WSDL-OP-001"
    ]["notes"]
    assert (
        rows["HLA1516.1-WSDL-OP-001"]["current_test_id"]
        == "tests/verification/test_imported_hla_packet_v1_0.py::test_imported_packet_extended_catalog_families_match_expected_shape"
    )


def test_api_partial_rows_carry_explicit_canonical_residual_dispositions() -> None:
    for row in _read_rows():
        if row["current_status"] != "partial":
            continue
        assert row["notes"].startswith("Canonical residual disposition:"), row[
            "packet_requirement_id"
        ]


def test_api_rows_preserve_typed_evidence_refs() -> None:
    typed_rows = _typed_rows_by_id()
    for row in _read_rows():
        references = _split_refs(row["current_test_id"])
        assert typed_rows[row["packet_requirement_id"]].evidence_refs == tuple(references)


def test_selected_cpp_catalog_cluster_rows_are_declared_in_the_official_2010_cpp_api_headers() -> None:
    with zipfile.ZipFile(CPP_API_ZIP) as zf:
        names = set(zf.namelist())
        header_texts = {
            name: zf.read(name).decode("utf-8", errors="ignore")
            for name in names
            if name.endswith(".h")
        }

    rows = {row["packet_requirement_id"]: row for row in _read_rows()}
    for packet_id in PROMOTED_CPP_CLASS_CLUSTER:
        row = rows[packet_id]
        match = row["requirement_text"].split("`")
        token = match[1]
        header = match[3]
        member = next(name for name in header_texts if name.endswith(f"/{header}"))
        text = header_texts[member]
        pattern = re.compile(
            rf"\b(class|struct)\s+(RTI_EXPORT\s+)?{re.escape(token)}\b|\btypedef\b[^\n;]*\b{re.escape(token)}\b"
        )
        assert pattern.search(text), packet_id
        assert row["current_status"] == "mapped"
        assert (
            row["current_test_id"]
            == "tests/verification/test_api_detailed_reconciliation.py::test_selected_cpp_catalog_cluster_rows_are_declared_in_the_official_2010_cpp_api_headers"
        )


def test_api_rows_do_not_use_plan_or_closeout_packets_as_truth_sources() -> None:
    assert_rows_do_not_use_closeout_truth_sources(_read_rows())
