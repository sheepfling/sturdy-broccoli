from __future__ import annotations

import json
from pathlib import Path


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

MARKDOWN_INTRO_FRAGMENTS_BY_ARTIFACT = {
    "python_requirement_disposition.md": (
        "# Python Requirement Disposition",
        "every row has an explicit generated `python` disposition.",
        "## Summary",
    ),
    "certi_requirement_disposition.md": (
        "# CERTI Requirement Disposition",
        "every row has an explicit generated `certi` disposition.",
        "## Summary",
    ),
    "certi-native_requirement_disposition.md": (
        "# certi-native Requirement Disposition",
        "every row has an explicit generated `certi-native` disposition.",
        "inherits the CERTI family-level requirement disposition",
    ),
    "certi-jpype_requirement_disposition.md": (
        "# certi-jpype Requirement Disposition",
        "every row has an explicit generated `certi-jpype` disposition.",
        "inherits the CERTI family-level requirement disposition",
    ),
    "certi-py4j_requirement_disposition.md": (
        "# certi-py4j Requirement Disposition",
        "every row has an explicit generated `certi-py4j` disposition.",
        "inherits the CERTI family-level requirement disposition",
    ),
    "pitch_requirement_disposition.md": (
        "# Pitch Requirement Disposition",
        "every row has an explicit generated `pitch` disposition.",
        "## Profile Summary",
    ),
    "pitch-jpype_requirement_disposition.md": (
        "# pitch-jpype Requirement Disposition",
        "every row has an explicit generated `pitch-jpype` disposition.",
        "inherits the Pitch family-level requirement disposition",
        "## Summary",
    ),
    "pitch-py4j_requirement_disposition.md": (
        "# pitch-py4j Requirement Disposition",
        "every row has an explicit generated `pitch-py4j` disposition.",
        "inherits the Pitch family-level requirement disposition",
        "## Summary",
    ),
    "portico_requirement_disposition.md": (
        "# Portico Requirement Disposition",
        "every row has an explicit generated `portico` disposition.",
        "classification-required` until",
    ),
    "portico-jpype_requirement_disposition.md": (
        "# portico-jpype Requirement Disposition",
        "every row has an explicit generated `portico-jpype` disposition.",
        "inherits the Portico family-level requirement disposition",
    ),
    "portico-py4j_requirement_disposition.md": (
        "# portico-py4j Requirement Disposition",
        "every row has an explicit generated `portico-py4j` disposition.",
        "inherits the Portico family-level requirement disposition",
    ),
}

BACKEND_DOC_PREFIXES_BY_ARTIFACT = {
    "python_requirement_disposition.json": (),
    "certi_requirement_disposition.json": (
        "packages/hla2010-rti-certi/docs/",
    ),
    "certi-native_requirement_disposition.json": (
        "packages/hla2010-rti-certi/docs/",
    ),
    "certi-jpype_requirement_disposition.json": (
        "packages/hla2010-rti-certi/docs/",
    ),
    "certi-py4j_requirement_disposition.json": (
        "packages/hla2010-rti-certi/docs/",
    ),
    "portico_requirement_disposition.json": (),
    "pitch-jpype_requirement_disposition.json": (
        "packages/hla2010-rti-pitch-common/docs/",
    ),
    "pitch-py4j_requirement_disposition.json": (
        "packages/hla2010-rti-pitch-common/docs/",
    ),
    "portico-jpype_requirement_disposition.json": (),
    "portico-py4j_requirement_disposition.json": (),
    "pitch_requirement_disposition.json": (
        "packages/hla2010-rti-pitch-common/docs/",
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
    "python_requirement_disposition.json": "analysis/compliance/requirements_matrix_2010.json",
    "certi_requirement_disposition.json": "analysis/compliance/requirements_matrix_2010.json",
    "certi-native_requirement_disposition.json": "analysis/compliance/certi_requirement_disposition.json",
    "certi-jpype_requirement_disposition.json": "analysis/compliance/certi_requirement_disposition.json",
    "certi-py4j_requirement_disposition.json": "analysis/compliance/certi_requirement_disposition.json",
    "pitch_requirement_disposition.json": "analysis/compliance/requirements_matrix_2010.json",
    "pitch-jpype_requirement_disposition.json": "analysis/compliance/pitch_requirement_disposition.json",
    "pitch-py4j_requirement_disposition.json": "analysis/compliance/pitch_requirement_disposition.json",
    "portico_requirement_disposition.json": "analysis/compliance/requirements_matrix_2010.json",
    "portico-jpype_requirement_disposition.json": "analysis/compliance/portico_requirement_disposition.json",
    "portico-py4j_requirement_disposition.json": "analysis/compliance/portico_requirement_disposition.json",
}

SUMMARY_DISPOSITION_FIELD_BY_ARTIFACT = {
    "pitch_requirement_disposition.json": "pitch_disposition",
}


def _load_rows(filename: str) -> list[dict[str, object]]:
    payload = json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if row.get("document")
        in {"IEEE 1516.1-2010", "IEEE 1516-2010", "IEEE 1516.2-2010"}
    ]


def _load_payload(filename: str) -> dict[str, object]:
    return json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))


def _row_clause_key(row: dict[str, object]) -> str:
    document = str(row.get("document", "")).strip()
    clause_root = str(row.get("clause_root", "")).strip()
    if clause_root.lower() == "unknown":
        clause_root = ""
    return f"{document} §{clause_root}" if clause_root else f"{document} unknown"


def _markdown_section_table(filename: str, heading: str) -> list[dict[str, str]]:
    lines = (COMPLIANCE_DIR / filename).read_text(encoding="utf-8").splitlines()
    section_start = lines.index(heading) + 1
    while section_start < len(lines) and not lines[section_start].startswith("|"):
        section_start += 1
    assert section_start + 1 < len(lines), (filename, heading)

    header = [cell.strip() for cell in lines[section_start].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    index = section_start + 2
    while index < len(lines) and lines[index].startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
        rows.append(dict(zip(header, cells, strict=True)))
        index += 1
    return rows


def _stringify_summary_counts(summary_counts: dict[str, dict[str, int]]) -> list[dict[str, str]]:
    return [
        {
            "Document clause": clause_key,
            "Total": str(counts["total"]),
            "Verified": str(counts.get("verified", 0)),
            "Blocked": str(counts.get("blocked", 0)),
            "Vendor divergent": str(counts.get("vendor-divergent", 0)),
            "Not yet tested": str(counts.get("not-yet-tested", 0)),
            "Not applicable": str(counts.get("not-applicable", 0)),
            "Classification required": str(counts.get("classification-required", 0)),
        }
        for clause_key, counts in summary_counts.items()
    ]


def _stringify_disposition_counts(name: str, counts: dict[str, int]) -> dict[str, str]:
    return {
        "Pitch backend": name,
        "Verified": str(counts.get("verified", 0)),
        "Blocked": str(counts.get("blocked", 0)),
        "Vendor divergent": str(counts.get("vendor-divergent", 0)),
        "Not yet tested": str(counts.get("not-yet-tested", 0)),
        "Not applicable": str(counts.get("not-applicable", 0)),
        "Classification required": str(counts.get("classification-required", 0)),
    }


def _stringify_nonverified_row(row: dict[str, object], disposition_field: str) -> dict[str, str]:
    return {
        "Document": str(row.get("document", "")),
        "Clause": str(row.get("clause_root", "")),
        "Requirement": str(row.get("requirement_id") or row.get("matrix_id", "")),
        "Disposition": str(row.get(disposition_field, "")),
        "Kind": str(row.get("kind", "")),
        "Title": str(row.get("title", "")),
    }


def _stringify_pitch_family_subset_row(row: dict[str, object]) -> dict[str, str]:
    return {
        "Document": str(row.get("document", "")),
        "Clause": str(row.get("clause_root", "")),
        "Requirement": str(row.get("requirement_id") or row.get("matrix_id", "")),
        "Kind": str(row.get("kind", "")),
        "Applicability": str(row.get("applicability", "")),
        "Title": str(row.get("title", "")),
    }


def _stringify_pitch_backend_split_row(row: dict[str, object]) -> dict[str, str]:
    return {
        "Document": str(row.get("document", "")),
        "Clause": str(row.get("clause_root", "")),
        "Requirement": str(row.get("requirement_id") or row.get("matrix_id", "")),
        "Family": str(row.get("pitch_disposition", "")),
        "Pitch JPype": str(row.get("pitch_jpype_disposition", "")),
        "Pitch Py4J": str(row.get("pitch_py4j_disposition", "")),
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


def test_generated_requirement_disposition_artifacts_do_not_leak_foreign_backend_docs() -> None:
    failures: list[str] = []

    for filename, allowed_prefixes in BACKEND_DOC_PREFIXES_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        for row in rows:
            for ref in row.get("evidence_refs", []):
                ref_text = str(ref)
                if "/docs/" not in ref_text:
                    continue
                if not any(ref_text.startswith(prefix) for prefix in allowed_prefixes):
                    failures.append(
                        f"{filename}: {row.get('requirement_id')} has foreign evidence ref {ref_text}"
                    )

    assert not failures, "\n".join(failures)


def test_generated_requirement_disposition_markdown_packets_keep_explicit_generated_intros() -> None:
    for filename, fragments in MARKDOWN_INTRO_FRAGMENTS_BY_ARTIFACT.items():
        text = (COMPLIANCE_DIR / filename).read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, (filename, fragment)


def test_generated_requirement_disposition_markdown_summary_tables_match_json_packets() -> None:
    for json_filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        markdown_filename = json_filename.replace(".json", ".md")
        payload = _load_payload(json_filename)
        summary = payload["summary"]

        if json_filename == "pitch_requirement_disposition.json":
            expected_profile_rows = [
                _stringify_disposition_counts(
                    "pitch-jpype",
                    payload["summary"]["profile_disposition_counts"]["pitch-jpype"],
                ),
                _stringify_disposition_counts(
                    "pitch-py4j",
                    payload["summary"]["profile_disposition_counts"]["pitch-py4j"],
                ),
            ]
            assert _markdown_section_table(markdown_filename, "## Profile Summary") == expected_profile_rows
            assert _markdown_section_table(markdown_filename, "## Clause Summary") == _stringify_summary_counts(
                summary["clause_summary"]
            )
            assert _markdown_section_table(markdown_filename, "### pitch-jpype") == _stringify_summary_counts(
                summary["profile_clause_summary"]["pitch-jpype"]
            )
            assert _markdown_section_table(markdown_filename, "### pitch-py4j") == _stringify_summary_counts(
                summary["profile_clause_summary"]["pitch-py4j"]
            )
            continue

        assert _markdown_section_table(markdown_filename, "## Summary") == _stringify_summary_counts(
            summary["clause_summary"]
        )


def test_generated_requirement_disposition_markdown_row_tables_match_json_packets() -> None:
    for json_filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        markdown_filename = json_filename.replace(".json", ".md")
        payload = _load_payload(json_filename)
        rows = payload["rows"]

        if json_filename == "pitch_requirement_disposition.json":
            expected_backend_split_rows = [
                _stringify_pitch_backend_split_row(row)
                for row in rows
                if row.get("pitch_jpype_disposition") != row.get("pitch_py4j_disposition")
            ]
            assert _markdown_section_table(markdown_filename, "## Backend-Split Rows") == expected_backend_split_rows

            expected_not_yet_tested_rows = [
                _stringify_pitch_family_subset_row(row)
                for row in rows
                if row.get("pitch_disposition") == "not-yet-tested"
            ]
            assert _markdown_section_table(markdown_filename, "## Not Yet Tested Rows") == expected_not_yet_tested_rows

            expected_classification_required_rows = [
                _stringify_pitch_family_subset_row(row)
                for row in rows
                if row.get("pitch_disposition") == "classification-required"
            ]
            assert _markdown_section_table(
                markdown_filename,
                "## Classification Required Rows",
            ) == expected_classification_required_rows
            continue

        expected_nonverified_rows = [
            _stringify_nonverified_row(row, "runtime_disposition")
            for row in rows
            if row.get("runtime_disposition") != "verified"
        ]
        assert _markdown_section_table(markdown_filename, "## Non-Verified Rows") == expected_nonverified_rows


def test_generated_requirement_disposition_summary_metadata_matches_rows() -> None:
    for filename, expected_source_artifact in EXPECTED_SOURCE_ARTIFACTS.items():
        payload = json.loads((COMPLIANCE_DIR / filename).read_text(encoding="utf-8"))
        rows = payload["rows"]
        summary = payload["summary"]

        assert summary["row_count"] == len(rows), filename
        assert summary["source_artifact"] == expected_source_artifact, filename

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
            assert family_counts == summary["clause_summary"], filename

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
                assert observed == profile_clause_summary[profile_name], (filename, profile_name)
            continue

        observed: dict[str, dict[str, int]] = {}
        for row in rows:
            clause_key = _row_clause_key(row)
            disposition = str(row["runtime_disposition"])
            observed.setdefault(clause_key, {})
            observed[clause_key][disposition] = observed[clause_key].get(disposition, 0) + 1
        for counts in observed.values():
            counts["total"] = sum(counts.values())
        assert observed == summary["clause_summary"], filename
