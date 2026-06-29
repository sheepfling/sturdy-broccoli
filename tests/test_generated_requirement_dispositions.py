from __future__ import annotations

import json
from pathlib import Path

from compliance_helpers import (
    IEEE_1516_1_2010,
    IEEE_1516_2_2010,
    compliance_document_key,
    compliance_section_key,
    is_1516_1_2010_row,
    is_1516_2_2010_row,
)

ROOT = Path(__file__).resolve().parents[1]
COMPLIANCE_DIR = ROOT / "analysis" / "compliance"

ALLOWED_DISPOSITIONS = {
    "verified",
    "blocked",
    "vendor-divergent",
    "not-applicable",
    "classification-required",
    "not-yet-tested",
}

DISPOSITION_FIELDS_BY_ARTIFACT = {
    "python_requirement_disposition.json": ("runtime_disposition",),
    "certi_requirement_disposition.json": ("runtime_disposition",),
    "certi-native_requirement_disposition.json": ("runtime_disposition",),
    "certi-jpype_requirement_disposition.json": ("runtime_disposition",),
    "certi-py4j_requirement_disposition.json": ("runtime_disposition",),
    "portico_requirement_disposition.json": ("runtime_disposition",),
    "pitch-jpype_requirement_disposition.json": ("runtime_disposition",),
    "pitch-py4j_requirement_disposition.json": ("runtime_disposition",),
    "portico-jpype_requirement_disposition.json": ("runtime_disposition",),
    "portico-py4j_requirement_disposition.json": ("runtime_disposition",),
    "pitch_requirement_disposition.json": (
        "pitch_disposition",
        "pitch_jpype_disposition",
        "pitch_py4j_disposition",
    ),
}

MARKDOWN_HEADING_BY_ARTIFACT = {
    "python_requirement_disposition.md": (
        "# Python Requirement Disposition",
    ),
    "certi_requirement_disposition.md": (
        "# CERTI Requirement Disposition",
    ),
    "certi-native_requirement_disposition.md": (
        "# certi-native Requirement Disposition",
    ),
    "certi-jpype_requirement_disposition.md": (
        "# certi-jpype Requirement Disposition",
    ),
    "certi-py4j_requirement_disposition.md": (
        "# certi-py4j Requirement Disposition",
    ),
    "pitch_requirement_disposition.md": (
        "# Pitch Requirement Disposition",
    ),
    "pitch-jpype_requirement_disposition.md": (
        "# pitch-jpype Requirement Disposition",
    ),
    "pitch-py4j_requirement_disposition.md": (
        "# pitch-py4j Requirement Disposition",
    ),
    "portico_requirement_disposition.md": (
        "# Portico Requirement Disposition",
    ),
    "portico-jpype_requirement_disposition.md": (
        "# portico-jpype Requirement Disposition",
    ),
    "portico-py4j_requirement_disposition.md": (
        "# portico-py4j Requirement Disposition",
    ),
}

BACKEND_DOC_PREFIXES_BY_ARTIFACT = {
    "python_requirement_disposition.json": (),
    "certi_requirement_disposition.json": (
        "packages/hla-backend-certi/docs/",
    ),
    "certi-native_requirement_disposition.json": (
        "packages/hla-backend-certi/docs/",
    ),
    "certi-jpype_requirement_disposition.json": (
        "packages/hla-backend-certi/docs/",
    ),
    "certi-py4j_requirement_disposition.json": (
        "packages/hla-backend-certi/docs/",
    ),
    "portico_requirement_disposition.json": (),
    "pitch-jpype_requirement_disposition.json": (
        "packages/hla-vendor-pitch/docs/",
    ),
    "pitch-py4j_requirement_disposition.json": (
        "packages/hla-vendor-pitch/docs/",
    ),
    "portico-jpype_requirement_disposition.json": (),
    "portico-py4j_requirement_disposition.json": (),
    "pitch_requirement_disposition.json": (
        "packages/hla-vendor-pitch/docs/",
    ),
}

PROFILE_INHERITANCE_ARTIFACTS = {
    "certi_requirement_disposition.json": {
        "profiles": (
            "certi-native_requirement_disposition.json",
            "certi-jpype_requirement_disposition.json",
            "certi-py4j_requirement_disposition.json",
        ),
        "family_disposition_field": "runtime_disposition",
        "family_evidence_field": "evidence_refs",
    },
    "pitch_requirement_disposition.json": {
        "profiles": (
            "pitch-jpype_requirement_disposition.json",
            "pitch-py4j_requirement_disposition.json",
        ),
        "family_disposition_field_by_profile": {
            "pitch-jpype_requirement_disposition.json": "pitch_jpype_disposition",
            "pitch-py4j_requirement_disposition.json": "pitch_py4j_disposition",
        },
        "family_evidence_field_by_profile": {
            "pitch-jpype_requirement_disposition.json": "pitch_jpype_evidence_refs",
            "pitch-py4j_requirement_disposition.json": "pitch_py4j_evidence_refs",
        },
    },
    "portico_requirement_disposition.json": {
        "profiles": (
            "portico-jpype_requirement_disposition.json",
            "portico-py4j_requirement_disposition.json",
        ),
        "family_disposition_field": "runtime_disposition",
        "family_evidence_field": "evidence_refs",
    },
}

EXPECTED_SOURCE_ARTIFACTS = {
    "python_requirement_disposition.json": "requirements/2010/backend_resolution.json",
    "certi_requirement_disposition.json": "requirements/2010/backend_resolution.json",
    "certi-native_requirement_disposition.json": "analysis/compliance/certi_requirement_disposition.json",
    "certi-jpype_requirement_disposition.json": "analysis/compliance/certi_requirement_disposition.json",
    "certi-py4j_requirement_disposition.json": "analysis/compliance/certi_requirement_disposition.json",
    "pitch_requirement_disposition.json": "analysis/compliance/requirements_matrix_2010.json",
    "pitch-jpype_requirement_disposition.json": "analysis/compliance/pitch_requirement_disposition.json",
    "pitch-py4j_requirement_disposition.json": "analysis/compliance/pitch_requirement_disposition.json",
    "portico_requirement_disposition.json": "requirements/2010/backend_resolution.json",
    "portico-jpype_requirement_disposition.json": "analysis/compliance/portico_requirement_disposition.json",
    "portico-py4j_requirement_disposition.json": "analysis/compliance/portico_requirement_disposition.json",
}

MATRIX_SOURCED_DISPOSITION_ARTIFACTS = {
    "pitch_requirement_disposition.json",
}

BACKEND_RESOLUTION_SOURCED_DISPOSITION_ARTIFACTS = {
    "python_requirement_disposition.json",
    "certi_requirement_disposition.json",
    "portico_requirement_disposition.json",
}

SUMMARY_DISPOSITION_FIELD_BY_ARTIFACT = {
    "pitch_requirement_disposition.json": "pitch_disposition",
}

ALLOWED_REQUIREMENT_DOCUMENTS = {
    IEEE_1516_1_2010,
    IEEE_1516_2_2010,
    "IEEE 1516-2010",
    "multi-section",
}


def _load_rows(filename: str) -> list[dict[str, object]]:
    payload = json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row)
        or is_1516_2_2010_row(row)
        or row.get("document") in {"IEEE 1516-2010", "multi-section"}
    ]


def _load_payload(filename: str) -> dict[str, object]:
    return json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))


def _row_clause_key(row: dict[str, object]) -> str:
    document = compliance_document_key(row.get("document"))
    clause_root = str(row.get("clause_root", "")).strip()
    if clause_root.lower() == "unknown":
        clause_root = ""
    section_ref = f"{document} §{clause_root}" if clause_root else f"{document} unknown"
    return compliance_section_key(section_ref)


def _normalized_clause_summary(
    summary_counts: dict[str, dict[str, int]],
) -> dict[str, dict[str, int]]:
    return {
        compliance_section_key(section_ref): counts
        for section_ref, counts in summary_counts.items()
    }


def test_generated_requirement_disposition_artifacts_use_only_allowed_states() -> None:
    failures: list[str] = []

    for filename, fields in DISPOSITION_FIELDS_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        for field in fields:
            for row in rows:
                value = str(row.get(field, "")).strip()
                if not value:
                    failures.append(
                        f"{filename}: {row.get('requirement_id')} missing {field}"
                    )
                elif value not in ALLOWED_DISPOSITIONS:
                    failures.append(
                        f"{filename}: {row.get('requirement_id')} has invalid {field}={value!r}"
                    )

    assert not failures, "\n".join(failures)


def test_generated_requirement_disposition_artifacts_keep_explicit_backend_coverage() -> None:
    for filename, fields in DISPOSITION_FIELDS_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        assert rows, filename
        for field in fields:
            values = {str(row.get(field, "")).strip() for row in rows}
            assert values <= ALLOWED_DISPOSITIONS, (filename, field, values)
            assert values, (filename, field)


def test_generated_requirement_disposition_artifacts_remain_2010_scoped() -> None:
    foreign_tokens = ("2025", "rti1516_2025", "hla2025")

    for filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        payload = _load_payload(filename)
        for row in payload["rows"]:
            requirement_id = row.get("requirement_id") or row.get("matrix_id")
            document = compliance_document_key(row.get("document"))
            assert document in ALLOWED_REQUIREMENT_DOCUMENTS, (
                filename,
                requirement_id,
                row.get("document"),
            )

            scoped_fields = (
                row.get("document", ""),
                row.get("section_ref", ""),
                row.get("requirement_id", ""),
                row.get("matrix_id", ""),
                row.get("package", ""),
                row.get("backend", ""),
            )
            scoped_text = " ".join(str(value) for value in scoped_fields)
            for token in foreign_tokens:
                assert token not in scoped_text, (filename, requirement_id, token)


def test_generated_requirement_disposition_artifacts_do_not_leak_foreign_backend_docs() -> None:
    failures: list[str] = []

    for filename, allowed_prefixes in BACKEND_DOC_PREFIXES_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        for row in rows:
            for ref in row.get("evidence_refs", []):
                ref_text = str(ref)
                if not ref_text.startswith("packages/") or "/docs/" not in ref_text:
                    continue
                if not any(ref_text.startswith(prefix) for prefix in allowed_prefixes):
                    failures.append(
                        f"{filename}: {row.get('requirement_id')} has foreign evidence ref {ref_text}"
                    )

    assert not failures, "\n".join(failures)


def test_generated_requirement_disposition_markdown_packets_exist_as_operator_artifacts() -> None:
    for filename, fragments in MARKDOWN_HEADING_BY_ARTIFACT.items():
        text = (COMPLIANCE_DIR / filename).read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (filename, fragment)


def test_generated_requirement_disposition_markdown_packets_reference_generated_json_artifacts() -> None:
    for json_filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        markdown_filename = json_filename.replace(".json", ".md")
        text = (COMPLIANCE_DIR / markdown_filename).read_text(encoding="utf-8")

        assert "explicit generated" in text, markdown_filename

        if json_filename == "pitch_requirement_disposition.json":
            assert "## Profile Summary" in text, markdown_filename
            assert "## Clause Summary" in text, markdown_filename
            assert "## Backend-Split Rows" in text, markdown_filename
            continue

        assert "## Summary" in text, markdown_filename


def test_pitch_canonical_requirement_disposition_packet_is_leaf_only_and_backend_resolution_sourced() -> None:
    payload = _load_payload("pitch_requirement_disposition_canonical.json")
    summary = payload["summary"]
    rows = payload["rows"]
    rows_by_id = {row["requirement_id"] or row["matrix_id"]: row for row in rows}

    assert summary["row_count"] == 880
    assert summary["source_artifact"] == "requirements/2010/backend_resolution.json"
    assert summary["source_artifact_class"] == "backend-resolution"
    assert summary["canonical_requirement_artifact"] == "requirements/2010/canonical_requirements.json"
    assert "AREA-1516.1-4" not in rows_by_id
    assert "REQ-SAVE-RESTORE-001" not in rows_by_id
    assert "REQ-OMT-PARSE-001" not in rows_by_id
    assert rows_by_id["HLA1516.1-FM-4.1.5-001"]["pitch_disposition"] == "blocked"
    assert (
        "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md"
        in rows_by_id["HLA1516.1-FM-4.1.5-001"]["evidence_refs"]
    )


def test_generated_requirement_disposition_summary_metadata_matches_rows() -> None:
    for filename, expected_source_artifact in EXPECTED_SOURCE_ARTIFACTS.items():
        payload = json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))
        rows = payload["rows"]
        summary = payload["summary"]

        assert summary["row_count"] == len(rows), filename
        assert summary["source_artifact"] == expected_source_artifact, filename
        if filename in MATRIX_SOURCED_DISPOSITION_ARTIFACTS:
            assert summary["source_artifact_class"] == "projection", filename
            assert summary["canonical_requirement_artifact"] == "requirements/2010/canonical_requirements.json", filename
            assert summary["canonical_backend_resolution_artifact"] == "requirements/2010/backend_resolution.json", filename
            assert summary["projection_rollup_artifact"] == "requirements/2010/canonical_projection_rows.json", filename
        if filename in BACKEND_RESOLUTION_SOURCED_DISPOSITION_ARTIFACTS:
            assert summary["source_artifact_class"] == "backend-resolution", filename
            assert summary["canonical_requirement_artifact"] == "requirements/2010/canonical_requirements.json", filename

        if "backend" in summary:
            expected_backend = filename.removesuffix("_requirement_disposition.json")
            assert summary["backend"] == expected_backend, filename

        disposition_fields = (
            SUMMARY_DISPOSITION_FIELD_BY_ARTIFACT[filename],
        ) if filename in SUMMARY_DISPOSITION_FIELD_BY_ARTIFACT else DISPOSITION_FIELDS_BY_ARTIFACT[filename]
        summary_counts = summary["disposition_counts"]
        actual_counts: dict[str, int] = {}
        for field in disposition_fields:
            for row in rows:
                value = str(row.get(field, "")).strip()
                actual_counts[value] = actual_counts.get(value, 0) + 1

        assert dict(sorted(actual_counts.items())) == summary_counts, filename


def test_generated_profile_requirement_disposition_artifacts_inherit_family_rows() -> None:
    for family_filename, config in PROFILE_INHERITANCE_ARTIFACTS.items():
        family_rows = _load_rows(family_filename)
        assert family_rows, family_filename
        family_index = {str(row["requirement_id"]): row for row in family_rows}

        default_disposition_field = config.get("family_disposition_field")
        default_evidence_field = config.get("family_evidence_field")
        disposition_field_by_profile = config.get("family_disposition_field_by_profile", {})
        evidence_field_by_profile = config.get("family_evidence_field_by_profile", {})

        for profile_filename in config["profiles"]:
            profile_rows = _load_rows(profile_filename)
            assert {str(row["requirement_id"]) for row in profile_rows} == set(family_index), profile_filename

            disposition_field = disposition_field_by_profile.get(profile_filename, default_disposition_field)
            evidence_field = evidence_field_by_profile.get(profile_filename, default_evidence_field)
            assert disposition_field is not None, profile_filename
            assert evidence_field is not None, profile_filename

            profile_payload = json.loads((COMPLIANCE_DIR / profile_filename).read_text(encoding="utf-8"))
            assert profile_payload["summary"]["source_artifact"].endswith(family_filename), profile_filename

            for row in profile_rows:
                requirement_id = str(row["requirement_id"])
                family_row = family_index[requirement_id]
                assert row.get("runtime_disposition") == family_row.get(disposition_field), (
                    profile_filename,
                    requirement_id,
                )
                assert tuple(row.get("evidence_refs", ())) == tuple(family_row.get(evidence_field, ())), (
                    profile_filename,
                    requirement_id,
                )
                assert str(row.get("notes", "")) == str(family_row.get("notes", "")), (
                    profile_filename,
                    requirement_id,
                )


def test_generated_requirement_disposition_clause_summaries_match_row_level_counts() -> None:
    for filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        payload = json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))
        rows = payload["rows"]
        summary = payload["summary"]

        if filename == "pitch_requirement_disposition.json":
            family_counts: dict[str, dict[str, int]] = {}
            for row in rows:
                clause_key = _row_clause_key(row)
                disposition = str(row["pitch_disposition"])
                family_counts.setdefault(clause_key, {})
                family_counts[clause_key][disposition] = family_counts[clause_key].get(disposition, 0) + 1
            for counts in family_counts.values():
                counts["total"] = sum(counts.values())
            assert family_counts == _normalized_clause_summary(summary["clause_summary"]), filename

            profile_clause_summary = summary["profile_clause_summary"]
            profile_fields = {
                "pitch-jpype": "pitch_jpype_disposition",
                "pitch-py4j": "pitch_py4j_disposition",
            }
            for profile_name, field in profile_fields.items():
                observed: dict[str, dict[str, int]] = {}
                for row in rows:
                    clause_key = _row_clause_key(row)
                    disposition = str(row[field])
                    observed.setdefault(clause_key, {})
                    observed[clause_key][disposition] = observed[clause_key].get(disposition, 0) + 1
                for counts in observed.values():
                    counts["total"] = sum(counts.values())
                assert observed == _normalized_clause_summary(profile_clause_summary[profile_name]), (
                    filename,
                    profile_name,
                )
            continue

        observed: dict[str, dict[str, int]] = {}
        for row in rows:
            clause_key = _row_clause_key(row)
            disposition = str(row["runtime_disposition"])
            observed.setdefault(clause_key, {})
            observed[clause_key][disposition] = observed[clause_key].get(disposition, 0) + 1
        for counts in observed.values():
            counts["total"] = sum(counts.values())
        assert observed == _normalized_clause_summary(summary["clause_summary"]), filename
