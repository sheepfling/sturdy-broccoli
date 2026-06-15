from __future__ import annotations

from hla2010_repo_internal.requirements_source import (
    edition_qualified_requirement_document_title,
    format_requirement_clause_key,
    format_requirement_section_ref,
    match_requirement_spec_prefix,
    normalize_requirement_section_ref,
    requirement_active_binding_editions,
    requirement_active_bindings,
    requirement_document_matches_alias,
    requirement_document_matches_binding,
    requirement_document_title_for_alias,
    requirement_document_title_for_binding,
    requirement_selected_editions,
    validate_requirement_document_registry,
)
from hla2010_repo_internal.conformance import build_service_conformance_matrix
from tests.typed_json_models import RequirementRegistry, RequirementSourceOfTruth, RequirementSpec

FUTURE_FEDERATE_INTERFACE_TITLE = edition_qualified_requirement_document_title("IEEE 1516.1-2025", 2025)


def _sample_source() -> RequirementSourceOfTruth:
    return RequirementSourceOfTruth(
        registry=RequirementRegistry(
            active_bindings={
                "framework_rules": "HLA1516-2010",
                "federate_interface": "HLA1516.1-2010",
                "omt": "HLA1516.2-2010",
            },
            specs=(
                RequirementSpec(
                    spec_id="HLA1516-2010",
                    legacy_requirement_prefix="HLA1516",
                    document_title="IEEE 1516-2010 (2010 edition)",
                    edition_year=2010,
                ),
                RequirementSpec(
                    spec_id="HLA1516.1-2010",
                    legacy_requirement_prefix="HLA1516.1",
                    document_title="IEEE 1516.1-2010 (2010 edition)",
                    edition_year=2010,
                ),
                RequirementSpec(
                    spec_id="HLA1516.1-2025",
                    legacy_requirement_prefix="HLA1516.1",
                    document_title=FUTURE_FEDERATE_INTERFACE_TITLE,
                    edition_year=2025,
                ),
                RequirementSpec(
                    spec_id="HLA1516.2-2010",
                    legacy_requirement_prefix="HLA1516.2",
                    document_title="IEEE 1516.2-2010 (2010 edition)",
                    edition_year=2010,
                ),
            ),
        )
    )


def test_match_requirement_spec_prefix_supports_current_legacy_ids() -> None:
    assert match_requirement_spec_prefix("HLA1516.1-TM-8.8-001") == ("HLA1516.1", "TM")


def test_match_requirement_spec_prefix_supports_edition_aware_ids_from_source_data() -> None:
    source = _sample_source()
    assert match_requirement_spec_prefix("HLA1516.1-2025-TM-8.8-001", source.to_mapping()) == (
        "HLA1516.1-2025",
        "TM",
    )


def test_match_requirement_spec_prefix_prefers_longer_edition_prefixes_over_legacy_aliases() -> None:
    source = _sample_source()
    assert match_requirement_spec_prefix("HLA1516.1-2025-FM-4.2-001", source.to_mapping()) == (
        "HLA1516.1-2025",
        "FM",
    )


def test_requirement_active_bindings_expose_current_repo_selected_2010_editions() -> None:
    source = _sample_source()
    bindings = requirement_active_bindings(source.to_mapping())
    assert bindings["federate_interface"] == "HLA1516.1-2010"
    assert bindings["framework_rules"] == "HLA1516-2010"
    assert requirement_active_binding_editions(source.to_mapping()) == {
        "framework_rules": 2010,
        "federate_interface": 2010,
        "omt": 2010,
    }
    assert requirement_selected_editions(source.to_mapping()) == ("2010",)


def test_requirement_document_title_lookups_resolve_spec_aliases_and_bindings() -> None:
    source = _sample_source()
    assert requirement_document_title_for_alias("HLA1516.1-2010", source.to_mapping()) == "IEEE 1516.1-2010 (2010 edition)"
    assert requirement_document_title_for_alias("HLA1516.1-2025", source.to_mapping()) == FUTURE_FEDERATE_INTERFACE_TITLE
    assert requirement_document_title_for_alias("HLA1516.2", source.to_mapping()) == "IEEE 1516.2-2010 (2010 edition)"
    assert requirement_document_title_for_binding("federate_interface", source.to_mapping()) == "IEEE 1516.1-2010 (2010 edition)"


def test_format_requirement_section_ref_preserves_explicit_edition_qualified_document_titles() -> None:
    assert format_requirement_section_ref(FUTURE_FEDERATE_INTERFACE_TITLE, "8.8") == (
        f"{FUTURE_FEDERATE_INTERFACE_TITLE} §8.8"
    )
    assert format_requirement_section_ref(FUTURE_FEDERATE_INTERFACE_TITLE, "") == "unmapped"


def test_normalize_requirement_section_ref_accepts_shorthand_and_edition_qualified_forms() -> None:
    source = _sample_source()
    assert normalize_requirement_section_ref("1516.1-2010 §8.8", source=source.to_mapping()) == (
        "IEEE 1516.1-2010 (2010 edition) §8.8"
    )
    assert normalize_requirement_section_ref("IEEE 1516-2010 §12.2", source=source.to_mapping()) == (
        "IEEE 1516-2010 (2010 edition) §12.2"
    )
    assert normalize_requirement_section_ref("§8.8", default_document=FUTURE_FEDERATE_INTERFACE_TITLE) == (
        f"{FUTURE_FEDERATE_INTERFACE_TITLE} §8.8"
    )


def test_requirement_document_match_helpers_follow_aliases_and_active_bindings() -> None:
    source = _sample_source()
    assert requirement_document_matches_alias("IEEE 1516.2-2010 (2010 edition)", "HLA1516.2", source.to_mapping())
    assert requirement_document_matches_binding("IEEE 1516.1-2010 (2010 edition)", "federate_interface", source.to_mapping())
    assert not requirement_document_matches_binding(
        "IEEE 1516.2-2010 (2010 edition)",
        "federate_interface",
        source.to_mapping(),
    )


def test_format_requirement_clause_key_uses_standard_section_or_unknown_suffix() -> None:
    assert format_requirement_clause_key(FUTURE_FEDERATE_INTERFACE_TITLE, "8") == (
        f"{FUTURE_FEDERATE_INTERFACE_TITLE} §8"
    )
    assert format_requirement_clause_key(FUTURE_FEDERATE_INTERFACE_TITLE, "unknown") == (
        f"{FUTURE_FEDERATE_INTERFACE_TITLE} unknown"
    )


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
    source_mapping = source.to_mapping()
    registry_payload = source_mapping["requirement_id_registry"]
    assert isinstance(registry_payload, dict)
    specs = registry_payload["specs"]
    assert isinstance(specs, list)
    specs[0]["document_title"] = "IEEE 1516-2010"
    errors = validate_requirement_document_registry(source_mapping)
    assert any("IEEE 1516-2010 (2010 edition)" in error for error in errors)
