from __future__ import annotations

from collections import Counter
from pathlib import Path

from tests.verification.reconciliation_helpers import read_csv_rows, rows_by_id, status_counts


RECONCILIATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "requirements"
    / "reference"
    / "hla1516_1_ddm_detailed_reconciliation.csv"
)


def _read_rows() -> list[dict[str, str]]:
    return read_csv_rows(RECONCILIATION_PATH)


def test_ddm_detailed_reconciliation_has_expected_shape():
    rows = _read_rows()

    assert len(rows) == 223
    assert status_counts(rows) == Counter(
        {"mapped": 177, "partial": 46}
    )
    assert {row["source_packet_file"] for row in rows} == {
        "hla_1516_requirements_master_v1_0.csv"
    }


def test_ddm_detailed_reconciliation_spot_checks_key_rows():
    rows = rows_by_id(_read_rows())

    assert rows["HLA1516.1-DDM-OVERVIEW-012"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-OVERVIEW-012"]["reconciliation_kind"] == "OVW"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001"]["reconciliation_kind"] == "RTI_API"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"]["current_status"] == "partial"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-EXC"]["reconciliation_kind"] == "EXC_API"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-MOM"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-MOM"]["reconciliation_kind"] == "MOM_TRACE"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-RET"]["reconciliation_kind"] == "RET"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-SIG"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-RTIAPI-001-SIG"]["reconciliation_kind"] == "SIG"
    assert rows["HLA1516.1-DDM-9_5-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_5-001"]["reconciliation_kind"] == "SVC"
    assert rows["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_2-CREATEREGION-TEST-001"]["reconciliation_kind"] == "TEST"
    assert rows["HLA1516.1-DDM-9_12-RTIAPI-002-RET"]["current_status"] == "mapped"
    assert rows["HLA1516.1-DDM-9_12-RTIAPI-002-RET"]["reconciliation_kind"] == "RET"
