from __future__ import annotations

import csv
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path.cwd()
REQUIREMENTS_ROOT = REPO_ROOT / "requirements"
RECONCILIATION_ROOT = REQUIREMENTS_ROOT / "2010"
OUTPUT_PATHS = (
    REQUIREMENTS_ROOT / "hla_1516_master_harmonization_index_v1_0.csv",
    RECONCILIATION_ROOT / "hla_1516_master_harmonization_index_v1_0.csv",
)


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.requirements_packet import load_imported_hla_packet

FIELDNAMES = [
    "master_requirement_id",
    "standard",
    "clause",
    "capability",
    "feature",
    "master_requirement_type",
    "harmonization_status",
    "harmonization_source_file",
    "curated_requirement_id",
    "current_test_id",
    "implementation_area",
    "notes",
]

RECONCILIATION_PRECEDENCE = {
    "hla1516_2_omt_xml_detailed_reconciliation.csv": 0,
    "hla1516_2_omt_detailed_reconciliation.csv": 1,
}


def _unreconciled_source_hint(row: object) -> str:
    standard = row.standard.strip()
    clause = row.clause.strip()
    if standard == "IEEE 1516-2010":
        if clause.startswith("12"):
            return "hla1516_clause_12_save_restore.csv"
        return "hla1516_framework_rules.csv"
    if standard == "IEEE 1516.1-2010":
        return "hla1516_1_federate_interface.csv"
    if standard == "IEEE 1516.2-2010":
        return "hla1516_2_priority_omt.csv"
    return ""


def build_index_rows() -> list[dict[str, str]]:
    packet = load_imported_hla_packet(REPO_ROOT)
    bridge_lookup: dict[str, dict[str, str]] = {}
    bridge_precedence: dict[str, int] = {}
    for path in sorted(RECONCILIATION_ROOT.glob("*detailed_reconciliation.csv")):
        precedence = RECONCILIATION_PRECEDENCE.get(path.name, 0)
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                packet_requirement_id = row.get("packet_requirement_id", "").strip()
                if not packet_requirement_id:
                    continue
                existing_precedence = bridge_precedence.get(packet_requirement_id, -1)
                if precedence < existing_precedence:
                    continue
                bridge_lookup[packet_requirement_id] = {
                    "harmonization_status": row["current_status"].strip(),
                    "harmonization_source_file": path.name,
                    "curated_requirement_id": row.get("curated_requirement_id", "").strip(),
                    "current_test_id": row.get("current_test_id", "").strip(),
                    "notes": row.get("notes", "").strip(),
                }
                bridge_precedence[packet_requirement_id] = precedence

    rows: list[dict[str, str]] = []
    for row in packet.master_rows:
        bridge = bridge_lookup.get(row.requirement_id)
        if bridge is None:
            rows.append(
                {
                    "master_requirement_id": row.requirement_id,
                    "standard": row.standard,
                    "clause": row.clause,
                    "capability": row.capability,
                    "feature": row.feature,
                    "master_requirement_type": row.requirement_type,
                    "harmonization_status": "unreconciled",
                    "harmonization_source_file": _unreconciled_source_hint(row),
                    "curated_requirement_id": "",
                    "current_test_id": "",
                    "implementation_area": row.implementation_area,
                    "notes": "No packet-to-curated detailed reconciliation row exists yet for this imported master requirement.",
                }
            )
            continue
        rows.append(
            {
                "master_requirement_id": row.requirement_id,
                "standard": row.standard,
                "clause": row.clause,
                "capability": row.capability,
                "feature": row.feature,
                "master_requirement_type": row.requirement_type,
                "harmonization_status": bridge["harmonization_status"],
                "harmonization_source_file": bridge["harmonization_source_file"],
                "curated_requirement_id": bridge["curated_requirement_id"],
                "current_test_id": bridge["current_test_id"],
                "implementation_area": row.implementation_area,
                "notes": bridge["notes"],
            }
        )
    return rows


def write_index() -> None:
    rows = build_index_rows()
    for output_path in OUTPUT_PATHS:
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    write_index()
