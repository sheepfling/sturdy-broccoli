from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import RequirementArtifactSurvey, RequirementArtifactSurveyEntry

SURVEY_REL = "requirements/normalized/row_shape_survey.json"

_SCOPED_ROOTS = (
    "requirements",
    "docs/requirements",
    "docs/evidence/spec2025",
)


def _classify_csv(path: str, header: list[str]) -> tuple[str, str, str]:
    path_lower = path.lower()
    header_set = set(header)
    if "/history/" in path_lower or "docs/evidence/hla2010_python_verification_evidence" in path_lower:
        return "historical", "historical packet or evidence archive", _edition_for_path(path)
    if path.startswith("requirements/2010/"):
        if path == "requirements/2010/canonical_requirements.csv":
            return "canonical-requirement", "normalized canonical export", "2010"
        if path == "requirements/2010/backend_resolution.csv":
            return "backend-resolution", "canonical backend-resolution companion surface", "2010"
        if path.endswith("traceability_matrix.csv") or "priority_backend_resolution" in path_lower:
            return "projection", "2010 generated or bounded projection surface downstream of canonical truth", "2010"
        if "detailed_reconciliation" in path_lower:
            return "mapping-bridge", "2010 mapping bridge from imported or legacy requirement rows onto canonical repo claims", "2010"
        if (
            "clause_" in path_lower
            or "priority_clauses" in path_lower
            or path.endswith("hla1516_1_federate_interface.csv")
            or path.endswith("hla1516_2_omt.csv")
            or path.endswith("hla1516_framework_rules.csv")
            or path.endswith("hla_1516_master_harmonization_index_v1_0.csv")
            or path.endswith("hla_1516_packet_hookup_status_v1_0.csv")
        ):
            return "import-history", "2010 imported or packet-derived historical requirement ledger retained for audit and reconstruction", "2010"
    if {"packet_requirement_id", "curated_requirement_id"} <= header_set:
        return "requirement-mapping", "2010 detailed reconciliation bridge shape", "2010"
    if path.endswith("hla_2025_requirement_disposition_ledger.csv"):
        return "historical", "legacy row-shaped 2025 closeout projection", "2025"
    if path.endswith("canonical_requirements.csv"):
        return "canonical-requirement", "normalized canonical export", _edition_for_path(path)
    if path.endswith("hla_2025_harmonization_worklist.csv"):
        return "grouped-view", "2025 grouped closeout worklist", "2025"
    if (
        ("backend_resolution" in path_lower and not path.startswith("requirements/2010/"))
        or "pitch_202x" in path_lower
        or path.endswith("hla_2025_fi_binding_surface_matrix.csv")
    ):
        return "backend-resolution", "backend or binding resolution companion surface", _edition_for_path(path)
    if "executable_test" in path_lower or {"executable_test_id", "parent_requirement_id"} <= header_set:
        return "executable-verification", "executable verification backlog or packet", "2025"
    if path.endswith("traceability_matrix.csv") or "verification_matrix" in path_lower:
        return "executable-verification", "traceability or verification packet projection", _edition_for_path(path)
    if "requirements_master" in path_lower or {"requirement_id", "standard", "clause", "requirement_text"} <= header_set:
        return "imported-requirement", "imported packet requirement catalog", _edition_for_path(path)
    if "clause_tracker" in path_lower or path.endswith("requirements_summary_v1_0.csv"):
        return "grouped-view", "imported packet summary or tracker", _edition_for_path(path)
    return "historical", "unclassified machine-readable requirement artifact retained for audit", _edition_for_path(path)


def _classify_json(path: str, payload: Any) -> tuple[str, str, str]:
    path_lower = path.lower()
    if "/history/" in path_lower or "docs/evidence/hla2010_python_verification_evidence" in path_lower:
        return "historical", "historical packet or evidence archive", _edition_for_path(path)
    if path.startswith("requirements/2010/"):
        if path.endswith("backend_resolution.json"):
            return "backend-resolution", "canonical backend-resolution companion surface", "2010"
        if path.endswith("canonical_row_triage.json"):
            return "projection", "2010 canonical row normalization triage projection over canonical truth", "2010"
        if path.endswith("canonical_projection_rows.json"):
            return "projection", "2010 demoted rollup projection over canonical truth", "2010"
    if path.endswith("canonical_row_triage.json"):
        return "grouped-view", "2010 canonical row normalization triage view", "2010"
    if path.endswith("canonical_projection_rows.json"):
        return "grouped-view", "2010 demoted rollup projection over canonical truth", "2010"
    if path.endswith("canonical_requirements.json"):
        return "canonical-requirement", "normalized canonical export", _edition_for_path(path)
    if path.endswith("traceability_matrix.json"):
        return "executable-verification", "derived traceability projection", _edition_for_path(path)
    if path.endswith("hla_2025_requirement_disposition_ledger.json"):
        return "historical", "json projection of legacy 2025 closeout ledger", "2025"
    if path.endswith("hla_2025_requirement_coverage_rollup.json"):
        return "grouped-view", "coverage rollup summary", "2025"
    if path.endswith("requirements.json"):
        return "grouped-view", "requirements registry and imported packet inventory", _edition_for_path(path)
    return "historical", "unclassified machine-readable requirement artifact retained for audit", _edition_for_path(path)


def _edition_for_path(path: str) -> str:
    if "/2010/" in path or "1516e" in path.lower():
        return "2010"
    if "/2025/" in path or "1516-2025" in path.lower() or "spec2025" in path.lower():
        return "2025"
    return "cross-edition"


def _candidate_paths(project_root: Path) -> list[Path]:
    candidates: list[Path] = []
    for scoped_root in _SCOPED_ROOTS:
        root = project_root / scoped_root
        if not root.exists():
            continue
        candidates.extend(path for path in root.rglob("*") if path.suffix in {".csv", ".json"} and path.is_file())
    return sorted({path.resolve() for path in candidates})


def survey_requirement_artifacts(project_root: Path) -> RequirementArtifactSurvey:
    entries: list[RequirementArtifactSurveyEntry] = []
    for path in _candidate_paths(project_root):
        rel_path = str(path.relative_to(project_root))
        if path.suffix == ".csv":
            with path.open(newline="", encoding="utf-8") as handle:
                header = next(csv.reader(handle), [])
            family, basis, edition = _classify_csv(rel_path, header)
            fields = tuple(header)
            fmt = "csv"
        else:
            payload = json.loads(path.read_text(encoding="utf-8"))
            family, basis, edition = _classify_json(rel_path, payload)
            if isinstance(payload, dict):
                fields = tuple(str(key) for key in payload.keys())
            elif isinstance(payload, list) and payload and isinstance(payload[0], dict):
                fields = tuple(str(key) for key in payload[0].keys())
            else:
                fields = ()
            fmt = "json"
        entries.append(
            RequirementArtifactSurveyEntry(
                path=rel_path,
                format=fmt,
                edition=edition,
                family=family,
                classification_basis=basis,
                fields=fields,
            )
        )
    return RequirementArtifactSurvey(
        artifact="requirement-row-shape-survey",
        scoped_roots=_SCOPED_ROOTS,
        entry_count=len(entries),
        entries=tuple(entries),
    )


def write_requirement_artifact_survey(project_root: Path, output_path: Path | None = None) -> Path:
    target = output_path if output_path is not None else project_root / SURVEY_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = survey_requirement_artifacts(project_root).to_mapping()
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
