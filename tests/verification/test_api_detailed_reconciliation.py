from __future__ import annotations

import csv
import zipfile
from collections import Counter
from pathlib import Path


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "2010"
    / "hla1516_1_api_detailed_reconciliation.csv"
)
CPP_API_ZIP = (
    Path(__file__).resolve().parents[2]
    / "specs"
    / "ieee-1516-2010"
    / "hla_specs"
    / "1516.1-2010_downloads"
    / "IEEE1516-2010_C++_API.zip"
)


def _read_rows() -> list[dict[str, str]]:
    with RECONCILIATION_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_api_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 614
    assert Counter(row["current_status"] for row in rows) == Counter(
        {"partial": 385, "mapped": 229}
    )
    assert Counter((row["reconciliation_kind"], row["current_status"]) for row in rows) == Counter(
        {
            ("WSDL_OP", "partial"): 308,
            ("CPP_METHOD", "mapped"): 211,
            ("CPP_CLASS", "partial"): 71,
            ("CPP_CLASS", "mapped"): 8,
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


def test_selected_cpp_catalog_rows_are_declared_in_the_official_2010_cpp_api_headers() -> None:
    with zipfile.ZipFile(CPP_API_ZIP) as zf:
        header_texts = {
            "RTIambassadorFactory.h": zf.read("cpp/src/RTI/RTIambassadorFactory.h").decode(
                "utf-8", errors="ignore"
            ),
            "NullFederateAmbassador.h": zf.read("cpp/src/RTI/NullFederateAmbassador.h").decode(
                "utf-8", errors="ignore"
            ),
            "LogicalTimeFactory.h": zf.read("cpp/src/RTI/LogicalTimeFactory.h").decode(
                "utf-8", errors="ignore"
            ),
            "HLAfloat64TimeFactory.h": zf.read(
                "cpp/src/RTI/time/HLAfloat64TimeFactory.h"
            ).decode("utf-8", errors="ignore"),
            "HLAinteger64TimeFactory.h": zf.read(
                "cpp/src/RTI/time/HLAinteger64TimeFactory.h"
            ).decode("utf-8", errors="ignore"),
            "LogicalTime.h": zf.read("cpp/src/RTI/LogicalTime.h").decode(
                "utf-8", errors="ignore"
            ),
        }

    assert "class RTI_EXPORT RTIambassador" in header_texts["RTIambassadorFactory.h"]
    assert "class RTI_EXPORT RTIambassadorFactory" in header_texts["RTIambassadorFactory.h"]
    assert "class RTI_EXPORT NullFederateAmbassador" in header_texts[
        "NullFederateAmbassador.h"
    ]
    assert "class RTI_EXPORT LogicalTimeFactory" in header_texts[
        "LogicalTimeFactory.h"
    ]
    assert "class RTI_EXPORT HLAfloat64TimeFactory" in header_texts[
        "HLAfloat64TimeFactory.h"
    ]
    assert "class RTI_EXPORT HLAinteger64TimeFactory" in header_texts[
        "HLAinteger64TimeFactory.h"
    ]
    assert "class RTI_EXPORT LogicalTime" in header_texts["LogicalTime.h"]
    assert "class LogicalTimeInterval;" in header_texts["LogicalTime.h"]
