from __future__ import annotations

from dataclasses import dataclass

from conftest import (
    REPO_ROOT,
    load_compliance_json,
    load_compliance_text,
    load_json_fixture,
)
from tests.compliance_row_models import RequirementDispositionRow
from tests.requirement_label_helpers import requirements_matrix_source_label, standard_document_titles

ROOT = REPO_ROOT
STANDARD_DOCUMENTS = standard_document_titles()
REQUIREMENTS_MATRIX_SOURCE_LABEL = requirements_matrix_source_label()
AMBIGUOUS_REQUIREMENTS_MATRIX_PHRASES = (
    "shared HLA 2010 requirements matrix",
    "shared 2010 requirements matrix",
)


@dataclass(frozen=True)
class GeneratedRequirementDispositionPolicy:
    allowed_dispositions: frozenset[str]
    disposition_fields_by_artifact: dict[str, tuple[str, ...]]
    markdown_intro_fragments_by_artifact: dict[str, tuple[str, ...]]
    backend_doc_prefixes_by_artifact: dict[str, tuple[str, ...]]
    profile_inheritance_artifacts: dict[str, dict[str, object]]
    expected_source_artifacts: dict[str, str]
    summary_disposition_field_by_artifact: dict[str, str]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> GeneratedRequirementDispositionPolicy:
        return cls(
            allowed_dispositions=frozenset(str(item) for item in payload["allowed_dispositions"]),
            disposition_fields_by_artifact={
                str(key): tuple(str(item) for item in value)
                for key, value in payload["disposition_fields_by_artifact"].items()
            },
            markdown_intro_fragments_by_artifact={
                str(key): tuple(str(item) for item in value)
                for key, value in payload["markdown_intro_fragments_by_artifact"].items()
            },
            backend_doc_prefixes_by_artifact={
                str(key): tuple(str(item) for item in value)
                for key, value in payload["backend_doc_prefixes_by_artifact"].items()
            },
            profile_inheritance_artifacts={
                str(key): value
                for key, value in payload["profile_inheritance_artifacts"].items()
            },
            expected_source_artifacts={
                str(key): str(value)
                for key, value in payload["expected_source_artifacts"].items()
            },
            summary_disposition_field_by_artifact={
                str(key): str(value)
                for key, value in payload["summary_disposition_field_by_artifact"].items()
            },
        )


POLICY = GeneratedRequirementDispositionPolicy.from_mapping(
    load_json_fixture("generated_requirement_dispositions_policy.json")
)
ALLOWED_DISPOSITIONS = POLICY.allowed_dispositions
DISPOSITION_FIELDS_BY_ARTIFACT = POLICY.disposition_fields_by_artifact
MARKDOWN_INTRO_FRAGMENTS_BY_ARTIFACT = POLICY.markdown_intro_fragments_by_artifact
BACKEND_DOC_PREFIXES_BY_ARTIFACT = POLICY.backend_doc_prefixes_by_artifact
PROFILE_INHERITANCE_ARTIFACTS = POLICY.profile_inheritance_artifacts
EXPECTED_SOURCE_ARTIFACTS = POLICY.expected_source_artifacts
SUMMARY_DISPOSITION_FIELD_BY_ARTIFACT = POLICY.summary_disposition_field_by_artifact


@dataclass(frozen=True)
class MarkdownTableRow:
    cells: dict[str, str]

    def as_dict(self) -> dict[str, str]:
        return dict(self.cells)


def _load_rows(filename: str) -> list[RequirementDispositionRow]:
    payload = load_compliance_json(filename)
    return [
        RequirementDispositionRow.from_mapping(row)
        for row in payload["rows"]
        if str(row.get("document", "")).strip() in STANDARD_DOCUMENTS
    ]


def _load_payload(filename: str) -> dict[str, object]:
    return load_compliance_json(filename)


def _load_payload_rows(filename: str) -> tuple[dict[str, object], list[RequirementDispositionRow]]:
    payload = _load_payload(filename)
    return payload, [RequirementDispositionRow.from_mapping(row) for row in payload["rows"]]


def _markdown_section_table(filename: str, heading: str) -> list[dict[str, str]]:
    lines = load_compliance_text(filename).splitlines()
    section_start = lines.index(heading) + 1
    while section_start < len(lines) and not lines[section_start].startswith("|"):
        section_start += 1
    assert section_start + 1 < len(lines), (filename, heading)

    header = [cell.strip() for cell in lines[section_start].strip("|").split("|")]
    rows: list[MarkdownTableRow] = []
    index = section_start + 2
    while index < len(lines) and lines[index].startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
        rows.append(MarkdownTableRow(dict(zip(header, cells, strict=True))))
        index += 1
    return [row.as_dict() for row in rows]


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


def _stringify_nonverified_row(
    row: RequirementDispositionRow,
    disposition_field: str,
) -> dict[str, str]:
    return {
        "Document": row.document,
        "Clause": row.clause_root,
        "Requirement": row.identifier,
        "Disposition": row.disposition_for(disposition_field),
        "Kind": row.kind,
        "Title": row.title,
    }


def _stringify_pitch_family_subset_row(row: RequirementDispositionRow) -> dict[str, str]:
    return {
        "Document": row.document,
        "Clause": row.clause_root,
        "Requirement": row.identifier,
        "Kind": row.kind,
        "Applicability": row.applicability,
        "Title": row.title,
    }


def _stringify_pitch_backend_split_row(row: RequirementDispositionRow) -> dict[str, str]:
    return {
        "Document": row.document,
        "Clause": row.clause_root,
        "Requirement": row.identifier,
        "Family": row.pitch_disposition,
        "Pitch JPype": row.pitch_jpype_disposition,
        "Pitch Py4J": row.pitch_py4j_disposition,
    }


def _count_dispositions(rows: list[RequirementDispositionRow], field_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.disposition_for(field_name)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _clause_summary_from_rows(
    rows: list[RequirementDispositionRow],
    field_name: str,
) -> dict[str, dict[str, int]]:
    observed: dict[str, dict[str, int]] = {}
    for row in rows:
        clause_key = row.clause_key
        disposition = row.disposition_for(field_name)
        observed.setdefault(clause_key, {})
        observed[clause_key][disposition] = observed[clause_key].get(disposition, 0) + 1
    for counts in observed.values():
        counts["total"] = sum(counts.values())
    return observed


def test_generated_requirement_disposition_artifacts_use_only_allowed_states() -> None:
    failures: list[str] = []

    for filename, fields in DISPOSITION_FIELDS_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        for field in fields:
            for row in rows:
                value = row.disposition_for(field)
                if not value:
                    failures.append(f"{filename}: {row.requirement_id} missing {field}")
                elif value not in ALLOWED_DISPOSITIONS:
                    failures.append(
                        f"{filename}: {row.requirement_id} has invalid {field}={value!r}"
                    )

    assert not failures, "\n".join(failures)


def test_generated_requirement_disposition_artifacts_keep_explicit_backend_coverage() -> None:
    for filename, fields in DISPOSITION_FIELDS_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        assert rows, filename
        for field in fields:
            values = {row.disposition_for(field) for row in rows}
            assert values <= ALLOWED_DISPOSITIONS, (filename, field, values)
            assert values, (filename, field)


def test_generated_requirement_disposition_artifacts_do_not_leak_foreign_backend_docs() -> None:
    failures: list[str] = []

    for filename, allowed_prefixes in BACKEND_DOC_PREFIXES_BY_ARTIFACT.items():
        rows = _load_rows(filename)
        for row in rows:
            for ref_text in row.evidence_refs:
                if "/docs/" not in ref_text:
                    continue
                if not any(ref_text.startswith(prefix) for prefix in allowed_prefixes):
                    failures.append(
                        f"{filename}: {row.requirement_id} has foreign evidence ref {ref_text}"
                    )

    assert not failures, "\n".join(failures)


def test_generated_requirement_disposition_markdown_packets_keep_explicit_generated_intros() -> None:
    for filename, fragments in MARKDOWN_INTRO_FRAGMENTS_BY_ARTIFACT.items():
        text = load_compliance_text(filename)
        for fragment in fragments:
            assert fragment in text, (filename, fragment)


def test_generated_requirement_disposition_artifacts_use_edition_qualified_matrix_labels() -> None:
    for filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        payload, rows = _load_payload_rows(filename)
        markdown_filename = filename.replace(".json", ".md")
        markdown_text = load_compliance_text(markdown_filename)

        assert REQUIREMENTS_MATRIX_SOURCE_LABEL in markdown_text, markdown_filename
        for phrase in AMBIGUOUS_REQUIREMENTS_MATRIX_PHRASES:
            assert phrase not in markdown_text, (markdown_filename, phrase)

        summary_source = str(payload.get("summary", {}).get("source_artifact", "")).strip()
        assert summary_source == EXPECTED_SOURCE_ARTIFACTS[filename], filename

        for row in rows:
            note = row.notes.strip()
            if "requirements matrix" not in note:
                continue
            assert REQUIREMENTS_MATRIX_SOURCE_LABEL in note, (filename, row.requirement_id, note)
            for phrase in AMBIGUOUS_REQUIREMENTS_MATRIX_PHRASES:
                assert phrase not in note, (filename, row.requirement_id, phrase)


def test_generated_requirement_disposition_markdown_summary_tables_match_json_packets() -> None:
    for json_filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        markdown_filename = json_filename.replace(".json", ".md")
        payload = _load_payload(json_filename)
        summary = payload["summary"]

        if json_filename == "pitch_requirement_disposition.json":
            expected_profile_rows = [
                _stringify_disposition_counts(profile_name, payload["summary"]["profile_disposition_counts"][profile_name])
                for profile_name in ("pitch-jpype", "pitch-py4j")
            ]
            assert _markdown_section_table(markdown_filename, "## Profile Summary") == expected_profile_rows
            assert _markdown_section_table(markdown_filename, "## Clause Summary") == _stringify_summary_counts(
                summary["clause_summary"]
            )
            for profile_name in ("pitch-jpype", "pitch-py4j"):
                assert _markdown_section_table(markdown_filename, f"### {profile_name}") == _stringify_summary_counts(
                    summary["profile_clause_summary"][profile_name]
                )
            continue

        assert _markdown_section_table(markdown_filename, "## Summary") == _stringify_summary_counts(
            summary["clause_summary"]
        )


def test_generated_requirement_disposition_markdown_row_tables_match_json_packets() -> None:
    for json_filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        markdown_filename = json_filename.replace(".json", ".md")
        _payload, rows = _load_payload_rows(json_filename)

        if json_filename == "pitch_requirement_disposition.json":
            pitch_section_cases = (
                ("## Backend-Split Rows", lambda row: row.pitch_jpype_disposition != row.pitch_py4j_disposition, _stringify_pitch_backend_split_row),
                ("## Not Yet Tested Rows", lambda row: row.pitch_disposition == "not-yet-tested", _stringify_pitch_family_subset_row),
                (
                    "## Classification Required Rows",
                    lambda row: row.pitch_disposition == "classification-required",
                    _stringify_pitch_family_subset_row,
                ),
            )
            for heading, predicate, render_row in pitch_section_cases:
                assert _markdown_section_table(markdown_filename, heading) == [
                    render_row(row) for row in rows if predicate(row)
                ]
            continue

        expected_nonverified_rows = [
            _stringify_nonverified_row(row, "runtime_disposition")
            for row in rows
            if row.runtime_disposition != "verified"
        ]
        assert _markdown_section_table(markdown_filename, "## Non-Verified Rows") == expected_nonverified_rows


def test_generated_requirement_disposition_summary_metadata_matches_rows() -> None:
    for filename, expected_source_artifact in EXPECTED_SOURCE_ARTIFACTS.items():
        payload, rows = _load_payload_rows(filename)
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
            for value, count in _count_dispositions(rows, field).items():
                actual_counts[value] = actual_counts.get(value, 0) + count

        assert dict(sorted(actual_counts.items())) == summary_counts, filename


def test_generated_profile_requirement_disposition_artifacts_inherit_family_rows() -> None:
    for family_filename, config in PROFILE_INHERITANCE_ARTIFACTS.items():
        family_rows = _load_rows(family_filename)
        assert family_rows, family_filename
        family_index = {row.requirement_id: row for row in family_rows}

        default_disposition_field = config.get("family_disposition_field")
        default_evidence_field = config.get("family_evidence_field")
        disposition_field_by_profile = config.get("family_disposition_field_by_profile", {})
        evidence_field_by_profile = config.get("family_evidence_field_by_profile", {})

        for profile_filename in config["profiles"]:
            profile_rows = _load_rows(profile_filename)
            assert {row.requirement_id for row in profile_rows} == set(family_index), profile_filename

            disposition_field = disposition_field_by_profile.get(profile_filename, default_disposition_field)
            evidence_field = evidence_field_by_profile.get(profile_filename, default_evidence_field)
            assert disposition_field is not None, profile_filename
            assert evidence_field is not None, profile_filename

            profile_payload = load_compliance_json(profile_filename)
            assert profile_payload["summary"]["source_artifact"].endswith(family_filename), profile_filename

            for row in profile_rows:
                family_row = family_index[row.requirement_id]
                assert row.runtime_disposition == family_row.disposition_for(disposition_field), (
                    profile_filename,
                    row.requirement_id,
                )
                assert row.evidence_refs == family_row.evidence_refs_for(evidence_field), (
                    profile_filename,
                    row.requirement_id,
                )
                assert row.notes == family_row.notes, (profile_filename, row.requirement_id)


def test_generated_requirement_disposition_clause_summaries_match_row_level_counts() -> None:
    for filename in DISPOSITION_FIELDS_BY_ARTIFACT:
        payload, rows = _load_payload_rows(filename)
        summary = payload["summary"]

        if filename == "pitch_requirement_disposition.json":
            assert _clause_summary_from_rows(rows, "pitch_disposition") == summary["clause_summary"], filename

            profile_clause_summary = summary["profile_clause_summary"]
            for profile_name, field in (
                ("pitch-jpype", "pitch_jpype_disposition"),
                ("pitch-py4j", "pitch_py4j_disposition"),
            ):
                assert _clause_summary_from_rows(rows, field) == profile_clause_summary[profile_name], (
                    filename,
                    profile_name,
                )
            continue

        assert _clause_summary_from_rows(rows, "runtime_disposition") == summary["clause_summary"], filename
