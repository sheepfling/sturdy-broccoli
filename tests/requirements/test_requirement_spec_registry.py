from __future__ import annotations

from hla2010_repo_internal.requirements_source import (
    edition_qualified_requirement_document_title,
    format_requirement_clause_key,
    format_requirement_section_ref,
    match_requirement_spec_prefix,
    requirement_active_bindings,
    requirement_document_matches_alias,
    requirement_document_matches_binding,
    requirement_document_title_for_alias,
    requirement_document_title_for_binding,
    validate_requirement_document_registry,
)
from hla2010_repo_internal.conformance import build_service_conformance_matrix


def _sample_source() -> dict[str, object]:
    return {
        "requirement_id_registry": {
            "active_bindings": {
                "framework_rules": "HLA1516-2010",
                "federate_interface": "HLA1516.1-2025",
                "omt": "HLA1516.2-2010",
            },
            "specs": [
                {
                    "spec_id": "HLA1516-2010",
                    "legacy_requirement_prefix": "HLA1516",
                    "document_title": "IEEE 1516-2010 (2010 edition)",
                    "edition_year": 2010,
                },
                {
                    "spec_id": "HLA1516.1-2025",
                    "legacy_requirement_prefix": "HLA1516.1",
                    "document_title": "IEEE 1516.1-2025",
                    "edition_year": 2025,
                },
                {
                    "spec_id": "HLA1516.2-2010",
                    "legacy_requirement_prefix": "HLA1516.2",
                    "document_title": "IEEE 1516.2-2010 (2010 edition)",
                    "edition_year": 2010,
                },
            ],
        }
    }


def test_match_requirement_spec_prefix_supports_current_legacy_ids() -> None:
    assert match_requirement_spec_prefix("HLA1516.1-TM-8.8-001") == ("HLA1516.1", "TM")


def test_match_requirement_spec_prefix_supports_edition_aware_ids_from_source_data() -> None:
    source = _sample_source()
    assert match_requirement_spec_prefix("HLA1516.1-2025-TM-8.8-001", source) == ("HLA1516.1-2025", "TM")


def test_match_requirement_spec_prefix_prefers_longer_edition_prefixes_over_legacy_aliases() -> None:
    source = _sample_source()
    assert match_requirement_spec_prefix("HLA1516.1-2025-FM-4.2-001", source) == ("HLA1516.1-2025", "FM")


def test_requirement_active_bindings_expose_current_repo_editions() -> None:
    source = _sample_source()
    bindings = requirement_active_bindings(source)
    assert bindings["federate_interface"] == "HLA1516.1-2025"
    assert bindings["framework_rules"] == "HLA1516-2010"


def test_requirement_document_title_lookups_resolve_spec_aliases_and_bindings() -> None:
    source = _sample_source()
    assert requirement_document_title_for_alias("HLA1516.1-2025", source) == "IEEE 1516.1-2025"
    assert requirement_document_title_for_alias("HLA1516.2", source) == "IEEE 1516.2-2010 (2010 edition)"
    assert requirement_document_title_for_binding("federate_interface", source) == "IEEE 1516.1-2025"


def test_format_requirement_section_ref_uses_document_and_unmapped_fallback() -> None:
    assert format_requirement_section_ref("IEEE 1516.1-2025", "8.8") == "IEEE 1516.1-2025 §8.8"
    assert format_requirement_section_ref("IEEE 1516.1-2025", "") == "unmapped"


def test_requirement_document_match_helpers_follow_aliases_and_active_bindings() -> None:
    source = _sample_source()
    assert requirement_document_matches_alias("IEEE 1516.2-2010 (2010 edition)", "HLA1516.2", source)
    assert requirement_document_matches_binding("IEEE 1516.1-2025", "federate_interface", source)
    assert not requirement_document_matches_binding("IEEE 1516.2-2010 (2010 edition)", "federate_interface", source)


def test_format_requirement_clause_key_uses_standard_section_or_unknown_suffix() -> None:
    assert format_requirement_clause_key("IEEE 1516.1-2025", "8") == "IEEE 1516.1-2025 §8"
    assert format_requirement_clause_key("IEEE 1516.1-2025", "unknown") == "IEEE 1516.1-2025 unknown"


def test_service_conformance_matrix_section_refs_follow_row_document_labels() -> None:
    matrix = build_service_conformance_matrix()
    row = next(item for item in matrix.rows if item.interface == "RTIambassador" and item.section)
    assert row.section_ref == f"{row.document} §{row.section}"


def test_edition_qualified_requirement_document_title_adds_explicit_suffix() -> None:
    assert edition_qualified_requirement_document_title("IEEE 1516.1-2010", 2010) == (
        "IEEE 1516.1-2010 (2010 edition)"
    )


def test_validate_requirement_document_registry_rejects_ambiguous_document_titles() -> None:
    source = _sample_source()
    specs = source["requirement_id_registry"]["specs"]
    assert isinstance(specs, list)
    specs[0]["document_title"] = "IEEE 1516-2010"
    errors = validate_requirement_document_registry(source)
    assert any("IEEE 1516-2010 (2010 edition)" in error for error in errors)
