from __future__ import annotations

"""Backend compliance discovery tests for the IEEE/HLA 2010 editorial-edition corpus."""

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

from hla2010_repo_internal.verification.backend_compliance_discovery import (
    build_backend_compliance_catalog,
    build_discovery_payload,
    build_vendor_discovery_backlog,
    render_backend_compliance_catalog_text,
    write_vendor_discovery_backlog_artifacts,
)
from tests.pitch_clause4_policy_helpers import (
    PITCH_CLAUSE4_ALLOWED_EVIDENCE_PREFIXES,
    PITCH_CLAUSE4_BLOCKED_FAMILY_REFS,
    PITCH_CLAUSE4_BLOCKED_JPYPE_REFS,
    PITCH_CLAUSE4_BLOCKED_NOTES_FRAGMENTS,
    PITCH_CLAUSE4_BLOCKED_PY4J_REFS,
    PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS,
    PITCH_CLAUSE4_RESIDUAL_FRONTIER,
)
from tests.conftest import REPO_ROOT, load_compliance_json, load_compliance_text, load_json_fixture
from .evidence_bundles import bundle


ALLOWED_DISPOSITIONS = {
    "verified",
    "blocked",
    "vendor-divergent",
    "not-applicable",
    "classification-required",
    "not-yet-tested",
}
ROOT = REPO_ROOT
FEDERATE_INTERFACE_2010_DOCUMENT = "IEEE 1516.1-2010 (2010 edition)"
OMT_2010_DOCUMENT = "IEEE 1516.2-2010 (2010 edition)"
DISCOVERY_POLICY = load_json_fixture("backend_compliance_discovery_policy.json")


def _source_checkout_env(project_root: Path) -> dict[str, str]:
    data = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    roots = data["tool"]["pytest"]["ini_options"]["pythonpath"]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(project_root / root) for root in roots)
    return env


def _requirement_disposition_artifact_paths(project_root: Path) -> list[Path]:
    return sorted((project_root / "analysis" / "compliance").glob("*_requirement_disposition.json"))


def _catalog_summary_key_for_artifact(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_summary"


def _catalog_row_count_key_for_artifact(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_row_count"


def _row_disposition_keys(payload: dict[str, object]) -> set[str]:
    rows = payload["rows"]  # type: ignore[index]
    return {
        key
        for row in rows  # type: ignore[assignment]
        for key in row
        if key == "runtime_disposition" or key.endswith("_disposition")
    }


def _compliance_payload(name: str, project_root: Path = ROOT) -> dict[str, object]:
    if project_root == ROOT:
        return load_compliance_json(name)
    compliance_dir = project_root / Path("analysis/compliance")
    return json.loads((compliance_dir / name).read_text(encoding="utf-8"))


def _rows_by_requirement(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(row["requirement_id"] or row["matrix_id"]): row
        for row in payload["rows"]  # type: ignore[index]
    }


def _document_matches(row_document: str | None, document: str) -> bool:
    if row_document is None:
        return False
    if document.endswith(" (2010 edition)"):
        return row_document in {document, document.removesuffix(" (2010 edition)")}
    return row_document == document


def _assert_refs_exclude_backend_and_pitch_noise(refs: list[str], notes: str) -> None:
    assert not any(ref.startswith("tests/backends/") for ref in refs)
    assert not any("pitch" in ref.lower() for ref in refs)
    assert "pitch" not in notes.lower()


def _assert_family_projection(
    family_payload: dict[str, object],
    profile_payloads: dict[str, dict[str, object]],
    requirement_id: str,
) -> None:
    family_rows = _rows_by_requirement(family_payload)
    for backend, payload in profile_payloads.items():
        rows = _rows_by_requirement(payload)
        assert rows[requirement_id]["runtime_disposition"] == family_rows[requirement_id]["runtime_disposition"], backend


def _assert_row_disposition_and_refs(
    rows: dict[str, dict[str, object]],
    requirement_id: str,
    disposition_key: str,
    expected_disposition: str,
    expected_refs: tuple[str, ...],
) -> None:
    row = rows[requirement_id]
    assert row[disposition_key] == expected_disposition
    for ref in expected_refs:
        assert ref in row["evidence_refs"]


def _assert_rows_share_disposition_and_refs(
    rows: dict[str, dict[str, object]],
    requirement_ids: set[str],
    disposition_key: str,
    expected_disposition: str,
    expected_refs: tuple[str, ...],
) -> None:
    for requirement_id in requirement_ids:
        _assert_row_disposition_and_refs(
            rows,
            requirement_id,
            disposition_key,
            expected_disposition,
            expected_refs,
        )


def _assert_rows_have_clean_refs(
    rows: dict[str, dict[str, object]],
    requirement_ids: set[str],
) -> None:
    for requirement_id in requirement_ids:
        _assert_refs_exclude_backend_and_pitch_noise(rows[requirement_id]["evidence_refs"], rows[requirement_id]["notes"])


def _verified_ids_for_clause(
    payload: dict[str, object],
    *,
    clause_root: str,
    document: str = FEDERATE_INTERFACE_2010_DOCUMENT,
) -> set[str]:
    return {
        row["requirement_id"] or row["matrix_id"]
        for row in payload["rows"]
        if _document_matches(row.get("document"), document)
        and row.get("clause_root") == clause_root
        and row.get("runtime_disposition") == "verified"
    }


def _rows_for_clause_with_dispositions(
    payload: dict[str, object],
    *,
    clause_root: str,
    disposition_key: str,
    dispositions: set[str],
    document: str = FEDERATE_INTERFACE_2010_DOCUMENT,
) -> list[dict[str, object]]:
    return [
        row
        for row in payload["rows"]
        if _document_matches(row.get("document"), document)
        and row.get("clause_root") == clause_root
        and row.get(disposition_key) in dispositions
    ]


def _assert_refs_use_allowed_prefixes(
    rows: list[dict[str, object]],
    *,
    allowed_prefixes: tuple[str, ...],
    verified_only: bool = False,
) -> None:
    for row in rows:
        refs = row["evidence_refs"]
        assert refs, row["requirement_id"]
        if (
            "pitch_disposition" in row
            and "pitch_jpype_disposition" in row
            and "pitch_py4j_disposition" in row
            and (verified_only or row["pitch_disposition"] == "verified")
        ):
            assert row["pitch_jpype_disposition"] == "verified", row["requirement_id"]
            assert row["pitch_py4j_disposition"] == "verified", row["requirement_id"]
        assert any(ref.startswith(allowed_prefixes) for ref in refs), (row["requirement_id"], refs)


def _assert_clause_rows_use_allowed_prefixes(
    payload: dict[str, object],
    *,
    clause_root: str,
    disposition_key: str,
    dispositions: set[str],
    allowed_prefixes: tuple[str, ...],
    verified_only: bool = False,
) -> None:
    rows = _rows_for_clause_with_dispositions(
        payload,
        clause_root=clause_root,
        disposition_key=disposition_key,
        dispositions=dispositions,
    )
    assert rows
    _assert_refs_use_allowed_prefixes(rows, allowed_prefixes=allowed_prefixes, verified_only=verified_only)


def _assert_ref_fields_use_allowed_prefixes(
    rows: list[dict[str, object]],
    *,
    fields: tuple[str, ...],
    allowed_prefixes: tuple[str, ...],
) -> None:
    for row in rows:
        for field in fields:
            refs = row[field]
            if not refs:
                continue
            assert any(ref.startswith(allowed_prefixes) for ref in refs), (
                row.get("requirement_id") or row["matrix_id"],
                field,
                refs,
            )


def _assert_forbidden_refs_absent(
    rows: dict[str, dict[str, object]],
    requirement_ids: set[str],
    forbidden_refs: tuple[str, ...],
) -> None:
    for requirement_id in requirement_ids:
        for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
            refs = rows[requirement_id][field]
            if refs:
                assert any(ref not in forbidden_refs for ref in refs)


def _assert_clause_rows_have_evidence_shape(
    rows: list[dict[str, object]],
    *,
    harness_fragment: str,
    test_prefix_groups: tuple[tuple[str, ...], ...],
) -> None:
    for row in rows:
        refs = row["evidence_refs"]
        assert any(harness_fragment in ref for ref in refs), row["requirement_id"] or row["matrix_id"]
        for test_prefixes in test_prefix_groups:
            assert any(any(ref.startswith(test_prefix) for ref in refs) for test_prefix in test_prefixes), (
                row["requirement_id"] or row["matrix_id"]
            )


def _assert_clause_mapped_rows_prefer_shared_harness_evidence_only(
    payload: dict[str, object],
    *,
    clause_root: str,
    strict_prefixes: tuple[str, ...],
    allowed_verified: tuple[str, ...] | None = None,
    forbidden_cases: tuple[tuple[set[str], tuple[str, ...]], ...] = (),
) -> None:
    rows = {
        row["requirement_id"]: row
        for row in _rows_for_clause_with_dispositions(
            payload,
            clause_root=clause_root,
            disposition_key="pitch_disposition",
            dispositions=ALLOWED_DISPOSITIONS,
        )
        if row.get("requirement_id")
    }
    _assert_clause_rows_use_allowed_prefixes(
        payload,
        clause_root=clause_root,
        disposition_key="pitch_disposition",
        dispositions={"verified"},
        allowed_prefixes=allowed_verified or strict_prefixes,
        verified_only=True,
    )
    if clause_root != "9":
        _assert_clause_rows_use_allowed_prefixes(
            payload,
            clause_root=clause_root,
            disposition_key="pitch_disposition",
            dispositions={"vendor-divergent"},
            allowed_prefixes=strict_prefixes,
        )
    for requirement_ids, forbidden_refs in forbidden_cases:
        _assert_forbidden_refs_absent(rows, requirement_ids, forbidden_refs)


def _assert_pitch_blocked_rows(
    rows: dict[str, dict[str, object]],
    requirement_ids: set[str],
    *,
    notes_fragments: tuple[str, ...],
    operator_refs: set[str],
    jpype_refs: set[str],
    py4j_refs: set[str],
) -> None:
    for requirement_id in requirement_ids:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "blocked"
        assert row["pitch_jpype_disposition"] == "blocked"
        assert row["pitch_py4j_disposition"] == "blocked"
        for fragment in notes_fragments:
            assert fragment in row["notes"]
        for expected_ref in operator_refs:
            assert expected_ref in row["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in row["evidence_refs"])
        assert not any(ref.startswith("tests/verification/") for ref in row["evidence_refs"])
        assert jpype_refs.issubset(set(row["pitch_jpype_evidence_refs"]))
        for expected_ref in py4j_refs:
            assert expected_ref in row["pitch_py4j_evidence_refs"]


def _assert_clause_disposition_partition(
    raw_rows: list[dict[str, object]],
    *,
    total: int,
    blocked_ids: set[str],
    vendor_divergent_ids: set[str],
    not_applicable_ids: set[str] | None = None,
    verified_count: int | None = None,
    verified_ids: set[str] | None = None,
) -> None:
    assert len(raw_rows) == total
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"} == blocked_ids
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"} == vendor_divergent_ids
    if not_applicable_ids is not None:
        assert {row["requirement_id"] or row["matrix_id"] for row in raw_rows if row["pitch_disposition"] == "not-applicable"} == not_applicable_ids
    if verified_count is not None:
        assert len([row for row in raw_rows if row["pitch_disposition"] == "verified"]) == verified_count
    if verified_ids is not None:
        assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "verified"} == verified_ids


def _assert_rows_have_disposition_and_ref(
    rows: dict[str, dict[str, object]],
    requirement_ids: set[str],
    *,
    disposition_key: str,
    expected_disposition: str,
    expected_ref: str,
) -> None:
    for requirement_id in requirement_ids:
        row = rows[requirement_id]
        assert row[disposition_key] == expected_disposition
        assert expected_ref in row["evidence_refs"]


def _assert_row_includes_refs(
    rows: dict[str, dict[str, object]],
    requirement_id: str,
    *expected_refs: str,
) -> None:
    for ref in expected_refs:
        assert ref in rows[requirement_id]["evidence_refs"]


def _assert_rows_have_empty_refs(
    rows: dict[str, dict[str, object]],
    requirement_ids: set[str],
) -> None:
    for requirement_id in requirement_ids:
        assert rows[requirement_id]["evidence_refs"] == []


def _clause_rows(
    payload: dict[str, object],
    *,
    clause_root: str,
    document: str = FEDERATE_INTERFACE_2010_DOCUMENT,
) -> list[dict[str, object]]:
    return [
        row
        for row in payload["rows"]
        if _document_matches(row.get("document"), document) and row.get("clause_root") == clause_root
    ]


def _clause_rows_by_requirement(
    payload: dict[str, object],
    *,
    clause_root: str,
    document: str = FEDERATE_INTERFACE_2010_DOCUMENT,
) -> dict[str, dict[str, object]]:
    return _rows_by_requirement({"rows": _clause_rows(payload, clause_root=clause_root, document=document)})


def _requirement_ids_with_disposition(
    rows: list[dict[str, object]],
    *,
    disposition_key: str,
    disposition: str,
) -> set[str]:
    return {
        row["requirement_id"] or row["matrix_id"]
        for row in rows
        if row[disposition_key] == disposition
    }


def _assert_clause_disposition_counts(
    rows: list[dict[str, object]],
    *,
    disposition_key: str,
    expected_counts: dict[str, int],
) -> None:
    counts = {
        disposition: len(_requirement_ids_with_disposition(rows, disposition_key=disposition_key, disposition=disposition))
        for disposition in ("blocked", "classification-required", "not-yet-tested", "not-applicable", "vendor-divergent", "verified")
    }
    assert counts == expected_counts


def _clause_summary_counts(
    payload: dict[str, object],
    *,
    clause_root: str,
    disposition_key: str,
    document: str = FEDERATE_INTERFACE_2010_DOCUMENT,
) -> dict[str, int]:
    rows = _clause_rows(payload, clause_root=clause_root, document=document)
    counts: dict[str, int] = {"total": len(rows)}
    for row in rows:
        disposition = row[disposition_key]
        counts[disposition] = counts.get(disposition, 0) + 1
    return counts


def _assert_clause_residual_frontier(
    payload: dict[str, object],
    *,
    clause_root: str,
    disposition_key: str,
    expected: dict[str, str],
    document: str = FEDERATE_INTERFACE_2010_DOCUMENT,
) -> None:
    residual_rows = {
        row["requirement_id"] or row["matrix_id"]: row[disposition_key]
        for row in payload["rows"]
        if _document_matches(row.get("document"), document)
        and row["clause_root"] == clause_root
        and row[disposition_key] != "verified"
    }
    assert residual_rows == expected


def _assert_no_classification_required_outside_document(
    rows: dict[str, dict[str, object]],
    *,
    clause_root: str,
    disposition_key: str,
    excluded_document: str,
) -> None:
    assert {
        requirement_id
        for requirement_id, row in rows.items()
        if row["clause_root"] == clause_root
        and row[disposition_key] == "classification-required"
        and not _document_matches(row["document"], excluded_document)
    } == set()


def _assert_omt_clause_is_unverified_staging_surface(
    payload: dict[str, object],
    *,
    clause_root: str,
    total: int,
    classification_required: int,
) -> None:
    rows = _clause_rows(
        payload,
        clause_root=clause_root,
        document="IEEE 1516.2-2010 (2010 edition)",
    )
    assert len(rows) == total
    _assert_clause_disposition_counts(
        rows,
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": classification_required,
            "not-yet-tested": 0,
            "not-applicable": 0,
            "vendor-divergent": 0,
            "verified": 0,
        },
    )
    assert {row["pitch_disposition"] for row in rows} == {"classification-required"}
    _assert_rows_have_empty_refs(
        _rows_by_requirement({"rows": rows}),
        {row["requirement_id"] or row["matrix_id"] for row in rows},
    )


def _assert_contains_all(actual: set[str] | list[str], expected: set[str]) -> None:
    assert expected <= set(actual)


def _assert_render_contains_once(text: str, tokens: set[str]) -> None:
    for token in tokens:
        assert text.count(token) == 1


def _assert_min_counts(actual: dict[str, int], minimums: dict[str, int]) -> None:
    for key, minimum in minimums.items():
        assert actual.get(key, 0) >= minimum


def test_backend_compliance_payload_uses_edition_qualified_2010_documents() -> None:
    payload_names = (
        "core_backend_matrix.json",
        "python_requirement_disposition.json",
        "certi_requirement_disposition.json",
        "pitch_requirement_disposition.json",
    )

    for payload_name in payload_names:
        payload = _compliance_payload(payload_name)
        for row in payload["rows"]:
            requirement_id = row.get("requirement_id") or row.get("matrix_id") or ""
            document = row.get("document") or ""
            if str(requirement_id).startswith("HLA1516.1-"):
                assert _document_matches(document, FEDERATE_INTERFACE_2010_DOCUMENT), (
                    payload_name,
                    requirement_id,
                )
            if str(requirement_id).startswith("HLA1516.2-"):
                assert _document_matches(document, OMT_2010_DOCUMENT), (payload_name, requirement_id)


def _assert_backend_disposition_counts_match_family(
    family_counts: dict[str, int],
    *payloads: dict[str, object],
) -> None:
    for payload in payloads:
        assert payload["summary"]["disposition_counts"] == family_counts


def test_backend_compliance_catalog_exposes_primary_backend_views():
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)
    expected_source_artifacts = {
        "analysis/compliance/core_backend_matrix.json",
        "analysis/compliance/python_requirement_disposition.json",
        "analysis/compliance/certi_requirement_disposition.json",
        "analysis/compliance/certi-native_requirement_disposition.json",
        "analysis/compliance/certi-jpype_requirement_disposition.json",
        "analysis/compliance/certi-py4j_requirement_disposition.json",
        "analysis/compliance/portico_requirement_disposition.json",
        "analysis/compliance/portico-jpype_requirement_disposition.json",
        "analysis/compliance/portico-py4j_requirement_disposition.json",
        "analysis/compliance/pitch_requirement_disposition.json",
        "analysis/compliance/pitch-jpype_requirement_disposition.json",
        "analysis/compliance/pitch-py4j_requirement_disposition.json",
        "analysis/compliance/vendor_discovery_backlog.json",
    }

    assert catalog["summary"]["backend_count"] >= 6
    _assert_contains_all(catalog["source_artifacts"], expected_source_artifacts)
    assert catalog["operator_entrypoints"]["discover_command"] == "./tools/compliance discover"

    backends = {row["backend_id"]: row for row in catalog["backends"]}
    assert "python-inmemory" in backends
    assert "certi-native" in backends
    assert "pitch-jpype" in backends

    assert "core" in backends["python-inmemory"]["matrices_present"]
    assert "section8" in backends["python-inmemory"]["matrices_present"]
    assert backends["certi-native"]["status_counts"].get("vendor-divergent", 0) >= 1
    assert any("queryGALT" in " ".join(row["section_refs"]) or row["slice_id"] == "negotiated-ownership" for row in backends["certi-native"]["notable_rows"])

    vendor_summary = catalog["requirements_vendor_summary"]
    _assert_min_counts(vendor_summary["python_runtime_disposition_counts"], {"verified": 1})
    _assert_min_counts(vendor_summary["certi_runtime_disposition_counts"], {"verified": 1})

    equal_profile_dispositions = (
        (
            catalog["certi_native_requirement_disposition_summary"]["disposition_counts"],
            catalog["certi_requirement_disposition_summary"]["disposition_counts"],
        ),
        (
            catalog["certi_jpype_requirement_disposition_summary"]["disposition_counts"],
            catalog["certi_requirement_disposition_summary"]["disposition_counts"],
        ),
        (
            catalog["certi_py4j_requirement_disposition_summary"]["disposition_counts"],
            catalog["certi_requirement_disposition_summary"]["disposition_counts"],
        ),
        (
            catalog["portico_jpype_requirement_disposition_summary"]["disposition_counts"],
            catalog["portico_requirement_disposition_summary"]["disposition_counts"],
        ),
        (
            catalog["portico_py4j_requirement_disposition_summary"]["disposition_counts"],
            catalog["portico_requirement_disposition_summary"]["disposition_counts"],
        ),
    )
    for actual, expected in equal_profile_dispositions:
        assert actual == expected

    python_disposition = catalog["python_requirement_disposition_summary"]["disposition_counts"]
    _assert_min_counts(python_disposition, {"verified": 1})
    certi_disposition = catalog["certi_requirement_disposition_summary"]["disposition_counts"]
    _assert_min_counts(certi_disposition, {"verified": 1, "classification-required": 1})
    portico_disposition = catalog["portico_requirement_disposition_summary"]["disposition_counts"]
    _assert_min_counts(portico_disposition, {"classification-required": 1})
    _assert_min_counts(vendor_summary["pitch_runtime_disposition_counts"], {"verified": 1, "vendor-divergent": 1})
    _assert_min_counts(vendor_summary["pitch_jpype_runtime_disposition_counts"], {"verified": 1, "vendor-divergent": 1})
    _assert_min_counts(vendor_summary["pitch_py4j_runtime_disposition_counts"], {"verified": 1, "vendor-divergent": 1})
    pitch_disposition = catalog["pitch_requirement_disposition_summary"]["disposition_counts"]
    _assert_min_counts(
        pitch_disposition,
        {"verified": 1, "blocked": 1, "not-applicable": 1, "classification-required": 1},
    )
    pitch_jpype_disposition = catalog["pitch_jpype_requirement_disposition_summary"]["disposition_counts"]
    _assert_min_counts(pitch_jpype_disposition, {"verified": 1, "blocked": 2})
    pitch_py4j_disposition = catalog["pitch_py4j_requirement_disposition_summary"]["disposition_counts"]
    _assert_min_counts(pitch_py4j_disposition, {"verified": 1})
    profile_disposition = catalog["pitch_requirement_disposition_summary"]["profile_disposition_counts"]
    _assert_min_counts(profile_disposition["pitch-jpype"], {"blocked": 2})
    _assert_min_counts(profile_disposition["pitch-py4j"], {"verified": 1})
    clause_summary = catalog["pitch_requirement_disposition_summary"]["clause_summary"]
    assert clause_summary["IEEE 1516.1-2010 (2010 edition) §4"].get("not-yet-tested", 0) == 0
    assert clause_summary["IEEE 1516.1-2010 (2010 edition) §6"].get("not-yet-tested", 0) == 0
    assert clause_summary["IEEE 1516.1-2010 (2010 edition) §8"]["vendor-divergent"] > 0
    profile_clause_summary = catalog["pitch_requirement_disposition_summary"]["profile_clause_summary"]
    _assert_min_counts(profile_clause_summary["pitch-jpype"]["IEEE 1516.1-2010 (2010 edition) §4"], {"blocked": 2})
    _assert_min_counts(profile_clause_summary["pitch-py4j"]["IEEE 1516.1-2010 (2010 edition) §4"], {"verified": 2})


def test_discovery_script_uses_explicit_project_root_from_outside_repo(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(project_root / "scripts" / "discover_backend_compliance.py"),
            "--project-root",
            str(project_root),
            "--backend",
            "certi-native",
            "--show-backlog",
            "--priority",
            "P1",
        ],
        cwd=tmp_path,
        env=_source_checkout_env(project_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Backend Compliance Discovery" in result.stdout
    assert "P1 certi-native" in result.stdout


def test_backend_compliance_catalog_text_render_supports_filtering():
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)
    required_render_tokens = {
        "python_requirement_dispositions:",
        "certi_requirement_dispositions:",
        "certi-native_requirement_dispositions:",
        "certi-jpype_requirement_dispositions:",
        "certi-py4j_requirement_dispositions:",
        "portico-jpype_requirement_dispositions:",
        "portico-py4j_requirement_dispositions:",
        "pitch_requirement_dispositions:",
        "pitch-jpype_requirement_dispositions:",
        "pitch-py4j_requirement_dispositions:",
    }

    rendered = render_backend_compliance_catalog_text(catalog, backend_filter="certi-native")
    assert "Backend Compliance Discovery" in rendered
    assert "certi-native" in rendered
    assert "python-inmemory" not in rendered
    _assert_render_contains_once(rendered, required_render_tokens)
    assert "Requirement vendor status counts:" in rendered
    assert "Refresh: ./tools/compliance generate" in rendered


def test_pitch_requirement_disposition_markdown_surfaces_profile_split_rows():
    rendered = load_compliance_text("pitch_requirement_disposition.md")
    required_markdown_tokens = {
        "## Profile Summary",
        "Vendor divergent",
        "## Profile Clause Summary",
        "### pitch-jpype",
        "## Backend-Split Rows",
        "| pitch-jpype |",
        "| pitch-py4j |",
    }

    for token in required_markdown_tokens:
        assert token in rendered
    assert "HLA1516.1-FM-4.1.5-001" not in rendered
    assert "| blocked | blocked | blocked |" not in rendered


def test_generated_requirement_disposition_artifacts_use_only_allowed_statuses() -> None:
    project_root = Path(__file__).resolve().parents[2]

    for path in _requirement_disposition_artifact_paths(project_root):
        payload = _compliance_payload(path.name, project_root)
        disposition_keys = _row_disposition_keys(payload)
        assert disposition_keys, path.name

        for row in payload["rows"]:
            for key in disposition_keys:
                value = row.get(key)
                assert value in ALLOWED_DISPOSITIONS, (path.name, row.get("requirement_id") or row.get("matrix_id"), key, value)

        summary = payload["summary"]
        assert set(summary["disposition_counts"]).issubset(ALLOWED_DISPOSITIONS), path.name
        assert sum(summary["disposition_counts"].values()) == summary["row_count"], path.name

        profile_counts = summary.get("profile_disposition_counts")
        if profile_counts is not None:
            for profile, counts in profile_counts.items():
                assert set(counts).issubset(ALLOWED_DISPOSITIONS), (path.name, profile)
                assert sum(counts.values()) == summary["row_count"], (path.name, profile)


def test_generated_requirement_disposition_summaries_match_row_level_counts() -> None:
    project_root = Path(__file__).resolve().parents[2]

    for path in _requirement_disposition_artifact_paths(project_root):
        payload = _compliance_payload(path.name, project_root)
        disposition_keys = _row_disposition_keys(payload)
        summary = payload["summary"]

        if disposition_keys == {"runtime_disposition"}:
            observed: dict[str, int] = {}
            for row in payload["rows"]:
                value = row["runtime_disposition"]
                observed[value] = observed.get(value, 0) + 1
            assert observed == summary["disposition_counts"], path.name
            continue

        assert path.name == "pitch_requirement_disposition.json", path.name
        observed_family: dict[str, int] = {}
        observed_profiles: dict[str, dict[str, int]] = {
            "pitch-jpype": {},
            "pitch-py4j": {},
        }
        profile_key_map = {
            "pitch-jpype": "pitch_jpype_disposition",
            "pitch-py4j": "pitch_py4j_disposition",
        }
        for row in payload["rows"]:
            family_value = row["pitch_disposition"]
            observed_family[family_value] = observed_family.get(family_value, 0) + 1
            for profile, key in profile_key_map.items():
                value = row[key]
                observed_profiles[profile][value] = observed_profiles[profile].get(value, 0) + 1

        assert observed_family == summary["disposition_counts"]
        assert observed_profiles == summary["profile_disposition_counts"]


def test_backend_compliance_catalog_mirrors_generated_requirement_disposition_packet_summaries() -> None:
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)

    for path in _requirement_disposition_artifact_paths(project_root):
        payload = _compliance_payload(path.name, project_root)
        source_artifact = f"analysis/compliance/{path.name}"
        summary_key = _catalog_summary_key_for_artifact(path)
        row_count_key = _catalog_row_count_key_for_artifact(path)

        assert source_artifact in catalog["source_artifacts"], path.name
        assert source_artifact in catalog["operator_entrypoints"]["primary_artifacts"], path.name
        assert catalog[summary_key] == payload["summary"], path.name
        assert catalog["summary"][row_count_key] == payload["summary"]["row_count"], path.name


def test_pitch_profile_requirement_disposition_artifacts_surface_profile_specific_rows():
    jpype = _compliance_payload("pitch-jpype_requirement_disposition.json")
    py4j = _compliance_payload("pitch-py4j_requirement_disposition.json")

    assert jpype["summary"]["backend"] == "pitch-jpype"
    assert py4j["summary"]["backend"] == "pitch-py4j"
    _assert_min_counts(jpype["summary"]["disposition_counts"], {"blocked": 2})
    _assert_min_counts(py4j["summary"]["disposition_counts"], {"verified": 1})

    jpype_rows = _rows_by_requirement(jpype)
    py4j_rows = _rows_by_requirement(py4j)

    assert jpype_rows["HLA1516.1-FM-4.1.5-001"]["runtime_disposition"] == "blocked"
    assert py4j_rows["HLA1516.1-FM-4.1.5-001"]["runtime_disposition"] == "blocked"
    assert (
        "packages/hla2010-rti-pitch-common/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md"
        in jpype_rows["HLA1516.1-FM-4.1.5-001"]["evidence_refs"]
    )
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_lost_federate.py::run_lost_federate_mom_scenario"
        in py4j_rows["HLA1516.1-FM-4.1.5-001"]["evidence_refs"]
    )
    for payload in (jpype_rows["HLA1516.1-FM-4.1.5-001"], py4j_rows["HLA1516.1-FM-4.1.5-001"]):
        assert "analysis/preflight_artifacts/pitch-preflight.json" in payload["evidence_refs"]
        assert (
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json"
            in payload["evidence_refs"]
        )
        assert (
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md"
            in payload["evidence_refs"]
        )


def test_pitch_clause4_profile_residual_frontier_is_exact():
    expected_residuals = {
        "HLA1516.1-FM-001": "not-applicable",
        "HLA1516.1-FM-4.1.5-001": "blocked",
        "HLA1516.1-FM-4.1.5-002": "blocked",
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM": "vendor-divergent",
        "HLA1516.1-FM-4.5-EXC-001": "vendor-divergent",
        "HLA1516.1-FM-4.9-EXC-001": "vendor-divergent",
    }

    for backend in ("pitch-jpype", "pitch-py4j"):
        payload = _compliance_payload(f"{backend}_requirement_disposition.json")
        residuals = {
            row["requirement_id"]: row["runtime_disposition"]
            for row in payload["rows"]
            if _document_matches(row.get("document"), "IEEE 1516.1-2010 (2010 edition)")
            and row.get("clause_root") == "4"
            and row.get("requirement_id")
            and row["runtime_disposition"] != "verified"
        }
        assert residuals == expected_residuals, backend


def test_pitch_clause4_lost_federate_rows_pin_current_blocked_operator_evidence() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}

    for requirement_id, verification_method in (
        ("HLA1516.1-FM-4.1.5-001", "verification_method=observer verification slice"),
        ("HLA1516.1-FM-4.1.5-002", "verification_method=integration test"),
    ):
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "blocked"
        assert row["pitch_jpype_disposition"] == "blocked"
        assert row["pitch_py4j_disposition"] == "blocked"
        assert "The canonical `./tools/pitch lost-federate-probe` lane currently stops at preflight on this surface" in row["notes"]
        assert "Docker is unreachable and the required CRC/FedPro loopback ports are blocked" in row["notes"]
        assert "the JPype path auto-resumed its dropped session and the Py4J path did not surface the report" in row["notes"]
        assert verification_method in row["notes"]
        assert "analysis/preflight_artifacts/pitch-preflight.json" in row["evidence_refs"]
        assert (
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json"
            in row["evidence_refs"]
        )
        assert (
            "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md"
            in row["evidence_refs"]
        )


def test_portico_requirement_disposition_artifact_is_explicitly_generated():
    payload = _compliance_payload("portico_requirement_disposition.json")

    assert payload["summary"]["backend"] == "portico"
    _assert_min_counts(payload["summary"]["disposition_counts"], {"classification-required": 1})

    rows = _rows_by_requirement(payload)
    assert rows["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]["runtime_disposition"] == "classification-required"
    assert rows["REQ-RTI-OM-6_10-updateAttributeValues"]["runtime_disposition"] == "classification-required"
    assert rows["HLA1516.1-FM-4.5-EXC-001"]["runtime_disposition"] == "classification-required"


def test_certi_profile_requirement_disposition_artifacts_are_generated_from_family_projection():
    family = _compliance_payload("certi_requirement_disposition.json")
    native = _compliance_payload("certi-native_requirement_disposition.json")
    jpype = _compliance_payload("certi-jpype_requirement_disposition.json")
    py4j = _compliance_payload("certi-py4j_requirement_disposition.json")

    assert native["summary"]["backend"] == "certi-native"
    assert jpype["summary"]["backend"] == "certi-jpype"
    assert py4j["summary"]["backend"] == "certi-py4j"

    family_counts = family["summary"]["disposition_counts"]
    _assert_backend_disposition_counts_match_family(family_counts, native, jpype, py4j)

    _assert_family_projection(
        family,
        {
            "certi-native": native,
            "certi-jpype": jpype,
            "certi-py4j": py4j,
        },
        "REQ-RTI-FM-4_16-requestFederationSave",
    )


def test_portico_profile_requirement_disposition_artifacts_are_generated_from_family_projection():
    family = _compliance_payload("portico_requirement_disposition.json")
    jpype = _compliance_payload("portico-jpype_requirement_disposition.json")
    py4j = _compliance_payload("portico-py4j_requirement_disposition.json")

    assert jpype["summary"]["backend"] == "portico-jpype"
    assert py4j["summary"]["backend"] == "portico-py4j"
    family_counts = family["summary"]["disposition_counts"]
    _assert_backend_disposition_counts_match_family(family_counts, jpype, py4j)

    _assert_family_projection(
        family,
        {
            "portico-jpype": jpype,
            "portico-py4j": py4j,
        },
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
    )


def test_certi_requirement_disposition_tracks_shared_save_restore_evidence():
    payload = _compliance_payload("certi_requirement_disposition.json")
    rows = _rows_by_requirement(payload)
    requirement_ids = {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "HLA1516.1-FM-4.16-001",
        "HLA1516.1-FM-4.17-001",
        "HLA1516.1-FM-4.22-001",
        "HLA1516.1-FM-4.24-001",
        "HLA1516.1-FM-4.27-001",
        "HLA1516.1-FM-4.31-001",
    }
    shared_harness_rows = {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
    }

    _assert_rows_share_disposition_and_refs(
        rows,
        requirement_ids,
        "runtime_disposition",
        "verified",
        (),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        shared_harness_rows,
        "runtime_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_scenario",
            "tests/vendors/test_real_vendor_runtime_smoke.py::test_certi_real_save_restore_smoke",
        ),
    )
    _assert_rows_have_clean_refs(rows, shared_harness_rows)


def test_certi_requirement_disposition_tracks_shared_synchronization_evidence():
    payload = _compliance_payload("certi_requirement_disposition.json")
    rows = _rows_by_requirement(payload)
    requirement_ids = {
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded",
        "REQ-FED-FM-4_13-announceSynchronizationPoint",
        "REQ-RTI-FM-4_14-synchronizationPointAchieved",
        "REQ-FED-FM-4_15-federationSynchronized",
    }

    _assert_rows_share_disposition_and_refs(
        rows,
        requirement_ids,
        "runtime_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_synchronization_matrix",
        ),
    )
    _assert_rows_have_clean_refs(rows, requirement_ids)


def test_certi_requirement_disposition_tracks_clause6_exchange_evidence():
    payload = _compliance_payload("certi_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    expected_ids = {
        "REQ-RTI-OM-6_10-updateAttributeValues",
        "REQ-RTI-OM-6_12-sendInteraction",
        "HLA1516.1-OM-6.10-001",
        "HLA1516.1-OM-6.10-002",
        "HLA1516.1-OM-6.10-003",
        "HLA1516.1-OM-6.10-004",
        "HLA1516.1-OM-6.10-005",
        "HLA1516.1-OM-6.12-001",
        "HLA1516.1-OM-6.12-002",
        "HLA1516.1-OM-6.12-003",
        "HLA1516.1-OM-6.12-004",
        "HLA1516.1-OM-6.12-005",
    }

    assert _verified_ids_for_clause(payload, clause_root="6") == expected_ids

    _assert_rows_share_disposition_and_refs(
        rows,
        expected_ids,
        "runtime_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_exchange.py::run_two_federate_exchange_scenario",
            "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_exchange_matrix",
        ),
    )
    _assert_rows_have_clean_refs(rows, expected_ids)


def test_certi_requirement_disposition_tracks_clause7_ownership_evidence():
    payload = _compliance_payload("certi_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    expected_ids = {
        "REQ-FED-OWN-7_11-requestAttributeOwnershipRelease",
        "REQ-RTI-OWN-7_17-queryAttributeOwnership",
        "REQ-FED-OWN-7_18-attributeIsNotOwned",
        "REQ-FED-OWN-7_18-attributeIsOwnedByRTI",
        "REQ-FED-OWN-7_18-informAttributeOwnership",
        "REQ-RTI-OWN-7_19-isAttributeOwnedByFederate",
        "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable",
        "HLA1516.1-OWN-7.11-001",
        "HLA1516.1-OWN-7.2-001",
        "HLA1516.1-OWN-7.9-001",
        "HLA1516.1-OWN-7.9-002",
    }

    assert _verified_ids_for_clause(payload, clause_root="7") == expected_ids
    _assert_rows_share_disposition_and_refs(
        rows,
        expected_ids,
        "runtime_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_scenario",
            "tests/vendors/test_certi_real_backend_ownership_matrix.py::test_certi_backend_ownership_matrix",
        ),
    )
    _assert_rows_have_clean_refs(rows, expected_ids)


def test_certi_requirement_disposition_tracks_clause8_shared_harness_subset():
    payload = _compliance_payload("certi_requirement_disposition.json")
    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    _assert_min_counts(
        _clause_summary_counts(payload, clause_root="8", disposition_key="runtime_disposition"),
        {"classification-required": 1, "not-applicable": 1, "verified": 1},
    )

    state_service_ids = {
        "REQ-RTI-TM-8_2-enableTimeRegulation",
        "REQ-FED-TM-8_3-timeRegulationEnabled",
        "REQ-RTI-TM-8_5-enableTimeConstrained",
        "REQ-FED-TM-8_6-timeConstrainedEnabled",
        "HLA1516.1-TM-8.2-001",
        "HLA1516.1-TM-8.2-002",
        "HLA1516.1-TM-8.5-001",
        "HLA1516.1-TM-8.5-002",
    }
    ordering_ids = {
        "REQ-RTI-TM-8_8-timeAdvanceRequest",
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "HLA1516.1-TM-8.8-001",
        "HLA1516.1-TM-8.8-002",
        "HLA1516.1-TM-8.10-001",
    }
    available_flush_ids = {
        "REQ-RTI-TM-8_9-timeAdvanceRequestAvailable",
        "REQ-RTI-TM-8_12-flushQueueRequest",
        "REQ-FED-TM-8_13-timeAdvanceGrant",
        "HLA1516.1-TM-8.12-001",
    }
    available_retraction_ids = {
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
    }
    logical_time_ids = {
        "REQ-RTI-TM-8_17-queryLogicalTime",
        "HLA1516.1-TM-8.17-001",
    }
    state_toggle_ids = {
        "REQ-RTI-TM-8_14-enableAsynchronousDelivery",
        "REQ-RTI-TM-8_15-disableAsynchronousDelivery",
        "REQ-RTI-TM-8_19-modifyLookahead",
        "REQ-RTI-TM-8_20-queryLookahead",
        "REQ-RTI-TM-8_4-disableTimeRegulation",
        "REQ-RTI-TM-8_7-disableTimeConstrained",
        "HLA1516.1-TM-8.19-001",
        "HLA1516.1-TM-8.4-001",
        "HLA1516.1-TM-8.7-001",
    }
    request_retraction_ids = {
        "REQ-RTI-TM-8_21-retract",
        "REQ-FED-TM-8_22-requestRetraction",
        "HLA1516.1-TM-8.21-001",
    }
    order_override_ids = {
        "REQ-RTI-TM-8_24-changeInteractionOrderType",
        "HLA1516.1-TM-8.1.2-003",
    }
    time_bound_vendor_divergent_ids = {
        "REQ-RTI-TM-8_16-queryGALT",
        "REQ-RTI-TM-8_18-queryLITS",
        "HLA1516.1-TM-8.16-001",
        "HLA1516.1-TM-8.18-001",
    }
    order_override_vendor_divergent_ids = {
        "REQ-RTI-TM-8_23-changeAttributeOrderType",
    }
    duplicate_enable_rejection_ids = {
        "HLA1516.1-TM-8.2-003",
        "HLA1516.1-TM-8.5-003",
    }
    tar_boundary_ids = {
        "HLA1516.1-TM-8.8-003",
    }

    section8_cases = (
        (
            state_service_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_state_services_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_state_services_matrix",
            ),
        ),
        (
            ordering_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_ordering_and_query_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_ordering_and_query_matrix",
            ),
        ),
        (
            available_flush_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_available_and_flush_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_available_and_flush_matrix",
            ),
        ),
        (
            available_retraction_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_available_and_retraction_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_available_and_retraction_matrix",
            ),
        ),
        (
            logical_time_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_state_services_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_logical_time_query_matrix",
            ),
        ),
        (
            state_toggle_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_state_services_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_state_toggle_services_matrix",
            ),
        ),
        (
            request_retraction_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_request_retraction_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_request_retraction_matrix",
            ),
        ),
        (
            order_override_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_order_override_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_order_override_matrix",
            ),
        ),
        (
            time_bound_vendor_divergent_ids,
            "runtime_disposition",
            "vendor-divergent",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_time_bound_query_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_time_bound_query_matrix",
            ),
        ),
        (
            order_override_vendor_divergent_ids,
            "runtime_disposition",
            "vendor-divergent",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_order_override_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_order_override_matrix",
            ),
        ),
        (
            duplicate_enable_rejection_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_duplicate_enable_rejection_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_duplicate_enable_rejection_matrix",
            ),
        ),
        (
            tar_boundary_ids,
            "runtime_disposition",
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_tar_galt_boundary_case",
                "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_tar_galt_boundary_matrix",
            ),
        ),
    )
    section8_cases = tuple(
        (
            {requirement_id for requirement_id in requirement_ids if not requirement_id.startswith("HLA1516.1-")},
            disposition_key,
            disposition,
            expected_refs,
        )
        for requirement_ids, disposition_key, disposition, expected_refs in section8_cases
    )
    for requirement_ids, disposition_key, disposition, expected_refs in section8_cases:
        _assert_rows_share_disposition_and_refs(
            rows,
            requirement_ids,
            disposition_key,
            disposition,
            expected_refs,
        )

    for requirement_id in (
        state_service_ids
        | ordering_ids
        | available_flush_ids
        | available_retraction_ids
        | logical_time_ids
        | state_toggle_ids
        | request_retraction_ids
        | order_override_ids
        | time_bound_vendor_divergent_ids
        | order_override_vendor_divergent_ids
        | duplicate_enable_rejection_ids
        | tar_boundary_ids
    ):
        refs = rows[requirement_id]["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in rows[requirement_id]["notes"].lower()


def test_requirements_matrix_projects_certi_shared_save_restore_rows_as_verified():
    payload = _compliance_payload("requirements_matrix_2010.json")
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}

    for requirement_id in DISCOVERY_POLICY["certi_verified_requirement_ids"]:
        assert rows[requirement_id]["certi_runtime_disposition"] == "verified"


def test_vendor_discovery_backlog_covers_divergent_gated_matrixed_and_defended_rows():
    project_root = Path(__file__).resolve().parents[2]
    backlog = build_vendor_discovery_backlog(project_root)

    assert backlog["summary"]["row_count"] > 0
    _assert_min_counts(backlog["summary"]["status_counts"], DISCOVERY_POLICY["required_backlog_status_counts"])

    by_backend_and_target = {
        (row["backend_id"], row["requirement_id"] or row["section_ref"], row["current_status"]): row
        for row in backlog["rows"]
    }
    for example in DISCOVERY_POLICY["expected_backlog_examples"]:
        assert (
            example["backend_id"],
            example["target"],
            example["current_status"],
        ) in by_backend_and_target
    for example in DISCOVERY_POLICY["forbidden_backlog_examples"]:
        assert (
            example["backend_id"],
            example["target"],
            example["current_status"],
        ) not in by_backend_and_target

    hosted_positive = [
        row
        for row in backlog["rows"]
        if row["backend_id"] == DISCOVERY_POLICY["hosted_positive_backend_id"]
        and row["current_status"] == DISCOVERY_POLICY["hosted_positive_status"]
    ]
    assert hosted_positive
    assert hosted_positive[0]["recommended_next_action"] == DISCOVERY_POLICY["hosted_positive_action"]

    defended = [row for row in backlog["rows"] if row["current_status"] == "defended-partial"]
    defended_ids = {row["requirement_id"] for row in defended}
    assert set(DISCOVERY_POLICY["defended_requirement_ids"]) <= defended_ids
    assert backlog["rows"][0]["priority"] == "P1"


def test_pitch_requirement_disposition_tracks_lifecycle_probe_evidence():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    clause4_summary = _clause_summary_counts(
        payload,
        clause_root="4",
        disposition_key="pitch_disposition",
    )
    assert clause4_summary == {
        "blocked": 2,
        "not-applicable": 2,
        "total": 281,
        "vendor-divergent": 3,
        "verified": 274,
    }
    profile_summary = payload["summary"]["profile_disposition_counts"]
    _assert_min_counts(profile_summary["pitch-jpype"], {"blocked": 2})
    _assert_min_counts(profile_summary["pitch-py4j"], {"verified": 1})
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}
    clause4_cases = (
        (
            {
                "REQ-RTI-FM-4_2-connect",
                "REQ-RTI-FM-4_3-disconnect",
                "REQ-RTI-FM-4_5-createFederationExecution",
                "REQ-RTI-FM-4_6-destroyFederationExecution",
                "REQ-RTI-FM-4_9-joinFederationExecution",
                "REQ-RTI-FM-4_10-resignFederationExecution",
            },
            "verified",
            bundle("federation_lifecycle"),
        ),
        (
            {"REQ-RTI-FM-4_7-listFederationExecutions", "REQ-FED-FM-4_8-reportFederationExecutions"},
            "verified",
            bundle("federation_listing"),
        ),
        (
            {"HLA1516.1-FM-4.1.4.2-001", "HLA1516.1-FM-4.5-MOM-001"},
            "verified",
            bundle("fom_module_visibility"),
        ),
        (
            {
                "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
                "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded",
                "REQ-FED-FM-4_13-announceSynchronizationPoint",
                "REQ-RTI-FM-4_14-synchronizationPointAchieved",
                "REQ-FED-FM-4_15-federationSynchronized",
            },
            "verified",
            bundle("synchronization"),
        ),
        (
            {
                "HLA1516.1-FM-4.15-001",
                "HLA1516.1-FM-4.15-002",
                "HLA1516.1-FM-4.15-CB-001",
                "HLA1516.1-FM-4.15-EFF-001",
                "HLA1516.1-FM-4.15-EXC-001",
                "HLA1516.1-FM-4.15-MOM-001",
                "HLA1516.1-FM-4.15-PRE-001",
                "HLA1516.1-FM-4.15-SIG-001",
                "HLA1516.1-FM-4.15-TEST-001",
            },
            "verified",
            bundle("failed_federate_synchronization"),
        ),
        (
            {
                "HLA1516.1-FM-4.2-EXC-001",
                "HLA1516.1-FM-4.2-PRE-001",
                "HLA1516.1-FM-4.3-EXC-001",
                "HLA1516.1-FM-4.6-EXC-001",
            },
            "verified",
            bundle("federation_lifecycle_negative"),
        ),
    )
    for requirement_ids, expected_disposition, expected_refs in clause4_cases:
        _assert_rows_share_disposition_and_refs(
            rows,
            requirement_ids,
            "pitch_disposition",
            expected_disposition,
            expected_refs,
        )

    _assert_row_disposition_and_refs(
        rows,
        "REQ-SAVE-RESTORE-001",
        "pitch_disposition",
        "verified",
        bundle("scheduled_save_restore_time_state"),
    )

    _assert_row_disposition_and_refs(
        rows,
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM",
        "pitch_disposition",
        "vendor-divergent",
        bundle("federation_lifecycle_with_mim"),
    )

    _assert_row_disposition_and_refs(
        rows,
        "REQ-FED-FM-4_4-connectionLost",
        "pitch_disposition",
        "verified",
        bundle("connection_lost"),
    )

    for requirement_id in {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "blocked"
        assert row["pitch_jpype_disposition"] == "blocked"
        assert row["pitch_py4j_disposition"] == "blocked"
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_lost_federate.py::run_external_lost_federate_observer_scenario"
            in row["pitch_jpype_evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix" in row["pitch_jpype_evidence_refs"]
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_lost_federate.py::run_lost_federate_mom_scenario"
            in row["pitch_py4j_evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix" in row["pitch_py4j_evidence_refs"]

    sync_clause4_pairs = {
        "HLA1516.1-FM-4.11-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.11-CB-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_registration_failure_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix",
        ),
        "HLA1516.1-FM-4.11-EXC-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_registration_failure_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix",
        ),
        "HLA1516.1-FM-4.13-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.14-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.14-EXC-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_multiple_synchronization_points_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_multiple_synchronization_points_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multiple_synchronization_points_matrix",
        ),
        "HLA1516.1-FM-4.15-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.15-002": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
    }
    for requirement_id, refs in sync_clause4_pairs.items():
        _assert_row_disposition_and_refs(
            rows,
            requirement_id,
            "pitch_disposition",
            "verified",
            refs,
        )

    _assert_row_disposition_and_refs(
        rows,
        "REQ-FED-FM-4_12-synchronizationPointRegistrationFailed",
        "pitch_disposition",
        "verified",
        bundle("synchronization_registration_failure"),
    )

    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.1-FM-4.9-CB-001",
        "pitch_disposition",
        "verified",
        bundle("late_join_synchronization"),
    )

    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.1-FM-4.1.3-001",
        "pitch_disposition",
        "verified",
        bundle("multiple_synchronization_points"),
    )

    save_restore_pairs = {
        "REQ-RTI-FM-4_16-requestFederationSave": bundle("save_restore"),
        "REQ-FED-FM-4_17-initiateFederateSave": bundle("save_restore"),
        "REQ-RTI-FM-4_18-federateSaveBegun": bundle("save_restore"),
        "REQ-RTI-FM-4_19-federateSaveComplete": bundle("save_restore"),
        "REQ-FED-FM-4_20-federationSaved": bundle("save_restore"),
        "REQ-RTI-FM-4_22-queryFederationSaveStatus": bundle("save_restore"),
        "REQ-FED-FM-4_23-federationSaveStatusResponse": bundle("save_restore"),
        "REQ-RTI-FM-4_24-requestFederationRestore": bundle("save_restore"),
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded": bundle("save_restore"),
        "REQ-FED-FM-4_26-federationRestoreBegun": bundle("save_restore"),
        "REQ-FED-FM-4_27-initiateFederateRestore": bundle("save_restore"),
        "REQ-RTI-FM-4_28-federateRestoreComplete": bundle("save_restore"),
        "REQ-FED-FM-4_29-federationRestored": bundle("save_restore"),
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus": bundle("save_restore"),
        "REQ-FED-FM-4_32-federationRestoreStatusResponse": bundle("save_restore"),
    }
    for requirement_id, refs in save_restore_pairs.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for ref in refs:
            assert ref in row["evidence_refs"]


def test_pitch_clause4_1516_1_dispositions_are_fully_classified_and_harness_backed():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="4")
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}
    by_requirement_id = rows

    assert len(raw_rows) == 281

    blocked_ids = {
        "HLA1516.1-FM-4.1.5-001",
        "HLA1516.1-FM-4.1.5-002",
    }
    vendor_divergent_ids = {
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM",
        "HLA1516.1-FM-4.5-EXC-001",
        "HLA1516.1-FM-4.9-EXC-001",
    }

    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"} == blocked_ids
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"} == vendor_divergent_ids

    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    assert len(verified_rows) == 274

    for row in verified_rows:
        refs = row["evidence_refs"]
        assert any(
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/" in ref
            for ref in refs
        ), row["requirement_id"]
        assert any(
            ref.startswith("tests/scenarios/test_federation_") or ref.startswith("tests/scenarios/test_object_management_")
            for ref in refs
        ), row["requirement_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"]

    for requirement_id in blocked_ids | vendor_divergent_ids:
        refs = by_requirement_id[requirement_id]["evidence_refs"]
        assert any(
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/" in ref
            for ref in refs
        ), requirement_id
        assert any(
            ref.startswith("tests/scenarios/test_federation_") or ref.startswith("tests/scenarios/test_object_management_")
            for ref in refs
        ), requirement_id
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), requirement_id

    save_abort_row = by_requirement_id["REQ-RTI-FM-4_21-abortFederationSave"]
    _assert_row_disposition_and_refs(
        by_requirement_id,
        "REQ-RTI-FM-4_21-abortFederationSave",
        "pitch_disposition",
        "verified",
        bundle("save_abort"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "REQ-FED-FM-4_25-requestFederationRestoreFailed",
        "pitch_disposition",
        "verified",
        bundle("restore_request_failure")[:2],
    )

    restore_failure_pairs = {
        "REQ-FED-FM-4_29-federationNotRestored": bundle("restore_failure"),
        "REQ-RTI-FM-4_30-abortFederationRestore": bundle("restore_abort"),
    }
    for requirement_id, refs in restore_failure_pairs.items():
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for ref in refs:
            assert ref in row["evidence_refs"]

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.30-EXC-001",
        "pitch_disposition",
        "verified",
        bundle("restore_abort_exception"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.10-CB-001",
        "pitch_disposition",
        "verified",
        bundle("resigned_federate_callback_silence"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.10-PRE-001",
        "pitch_disposition",
        "verified",
        bundle("resign_precondition"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.10-EXC-001",
        "pitch_disposition",
        "verified",
        bundle("resign_precondition"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.10-MOM-001",
        "pitch_disposition",
        "verified",
        bundle("resign_mom_cleanup"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.3-MOM-001",
        "pitch_disposition",
        "verified",
        bundle("disconnect_mom_cleanup"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.9-PRE-001",
        "pitch_disposition",
        "verified",
        bundle("join_precondition"),
    )

    _assert_rows_share_disposition_and_refs(
        by_requirement_id,
        {"HLA1516.1-FM-4.1-005", "HLA1516.1-FM-4.1-006"},
        "pitch_disposition",
        "verified",
        bundle("multi_participation"),
    )

    _assert_rows_share_disposition_and_refs(
        by_requirement_id,
        {"HLA1516.1-FM-4.1.4.1-001", "HLA1516.1-FM-4.1.4.1-002"},
        "pitch_disposition",
        "verified",
        bundle("fom_integrity_negative"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.1.4-001",
        "pitch_disposition",
        "verified",
        bundle("multi_module_fom_visibility"),
    )

    _assert_row_disposition_and_refs(
        by_requirement_id,
        "HLA1516.1-FM-4.1.4-002",
        "pitch_disposition",
        "verified",
        bundle("fom_module_visibility"),
    )


def test_pitch_clause4_mapped_rows_prefer_shared_harness_evidence_only():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _rows_for_clause_with_dispositions(
        payload,
        clause_root="4",
        disposition_key="pitch_disposition",
        dispositions=ALLOWED_DISPOSITIONS,
    )
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}
    by_requirement_id = rows
    clause4_listing_rows = {
        "REQ-RTI-FM-4_7-listFederationExecutions",
        "REQ-FED-FM-4_8-reportFederationExecutions",
    }
    clause4_sync_rows = {
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationFailed",
        "REQ-FED-FM-4_13-announceSynchronizationPoint",
        "REQ-RTI-FM-4_14-synchronizationPointAchieved",
        "REQ-FED-FM-4_15-federationSynchronized",
    }
    clause4_save_restore_service_rows = {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_18-federateSaveBegun",
        "REQ-RTI-FM-4_19-federateSaveComplete",
        "REQ-FED-FM-4_20-federationSaved",
        "REQ-RTI-FM-4_21-abortFederationSave",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-FED-FM-4_23-federationSaveStatusResponse",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded",
        "REQ-FED-FM-4_25-requestFederationRestoreFailed",
        "REQ-FED-FM-4_26-federationRestoreBegun",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_28-federateRestoreComplete",
        "REQ-FED-FM-4_29-federationRestored",
        "REQ-FED-FM-4_29-federationNotRestored",
        "REQ-RTI-FM-4_30-abortFederationRestore",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
    }
    clause4_save_restore_verified_rows = {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_18-federateSaveBegun",
        "REQ-RTI-FM-4_19-federateSaveComplete",
        "REQ-FED-FM-4_20-federationSaved",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-FED-FM-4_23-federationSaveStatusResponse",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded",
        "REQ-FED-FM-4_26-federationRestoreBegun",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_28-federateRestoreComplete",
        "REQ-FED-FM-4_29-federationRestored",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
    }
    clause4_restore_status_rows = {
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded",
        "REQ-FED-FM-4_25-requestFederationRestoreFailed",
        "REQ-FED-FM-4_26-federationRestoreBegun",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-FED-FM-4_29-federationRestored",
        "REQ-FED-FM-4_29-federationNotRestored",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
    }
    clause4_save_restore_extracted_rows = {
        "HLA1516.1-FM-4.16-001",
        "HLA1516.1-FM-4.21-001",
        "HLA1516.1-FM-4.23-001",
        "HLA1516.1-FM-4.24-001",
        "HLA1516.1-FM-4.26-001",
        "HLA1516.1-FM-4.31-001",
        "HLA1516.1-FM-4.32-001",
    }
    clause4_milestone_callback_rows = {
        "HLA1516.1-FM-4.1.2-001",
        "HLA1516.1-FM-4.1.2-002",
        "HLA1516.1-FM-4.1.3-001",
        "HLA1516.1-FM-4.9-CB-001",
    }
    clause4_residual_verified_rows = {
        "HLA1516.1-FM-4.16-MOM-001",
        "HLA1516.1-FM-4.18-EXC-001",
        "HLA1516.1-FM-4.18-MOM-001",
        "HLA1516.1-FM-4.23-EXC-001",
        "HLA1516.1-FM-4.23-MOM-001",
        "HLA1516.1-FM-4.24-MOM-001",
        "HLA1516.1-FM-4.19-EXC-001",
        "HLA1516.1-FM-4.19-MOM-001",
        "HLA1516.1-FM-4.20-EXC-001",
        "HLA1516.1-FM-4.20-MOM-001",
        "HLA1516.1-FM-4.21-EXC-001",
        "HLA1516.1-FM-4.21-MOM-001",
        "HLA1516.1-FM-4.25-EXC-001",
        "HLA1516.1-FM-4.25-MOM-001",
        "HLA1516.1-FM-4.26-EXC-001",
        "HLA1516.1-FM-4.26-MOM-001",
        "HLA1516.1-FM-4.29-EXC-001",
        "HLA1516.1-FM-4.29-MOM-001",
        "HLA1516.1-FM-4.28-EXC-001",
        "HLA1516.1-FM-4.28-MOM-001",
        "HLA1516.1-FM-4.31-MOM-001",
        "HLA1516.1-FM-4.32-EXC-001",
        "HLA1516.1-FM-4.32-MOM-001",
    }
    _assert_ref_fields_use_allowed_prefixes(
        raw_rows,
        fields=("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"),
        allowed_prefixes=PITCH_CLAUSE4_ALLOWED_EVIDENCE_PREFIXES,
    )

    milestone_rows = clause4_listing_rows | clause4_sync_rows | clause4_save_restore_service_rows | clause4_milestone_callback_rows
    strict_milestone_evidence_prefixes = (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
        "tests/scenarios/test_federation_management_backend_matrix.py::",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        milestone_rows,
        "pitch_disposition",
        "verified",
        (),
    )
    _assert_ref_fields_use_allowed_prefixes(
        [rows[requirement_id] for requirement_id in milestone_rows],
        fields=("evidence_refs",),
        allowed_prefixes=strict_milestone_evidence_prefixes,
    )
    for requirement_id in milestone_rows:
        assert rows[requirement_id]["pitch_jpype_disposition"] == "verified", requirement_id
        assert rows[requirement_id]["pitch_py4j_disposition"] == "verified", requirement_id

    _assert_forbidden_refs_absent(
        rows,
        clause4_listing_rows | clause4_restore_status_rows,
        (
            "tests/verification/test_spec_traceability_and_extended_python_rti.py",
            "tests/verification/test_compliance_slice_v011.py",
        ),
    )

    for requirement_ids, expected_refs in (
        (
            {"HLA1516.1-FM-4.17-MOM-001", "HLA1516.1-FM-4.27-MOM-001"},
            bundle("save_restore"),
        ),
        (
            clause4_save_restore_verified_rows | (clause4_save_restore_extracted_rows - {"HLA1516.1-FM-4.21-001"}),
            bundle("save_restore"),
        ),
        (
            {"REQ-RTI-FM-4_19-federateSaveNotComplete", "REQ-FED-FM-4_20-federationNotSaved"},
            bundle("save_failure"),
        ),
    ):
        _assert_rows_share_disposition_and_refs(
            by_requirement_id,
            requirement_ids,
            "pitch_disposition",
            "verified",
            expected_refs,
        )

    _assert_rows_share_disposition_and_refs(
        by_requirement_id,
        {"REQ-RTI-FM-4_21-abortFederationSave", "HLA1516.1-FM-4.21-001"},
        "pitch_disposition",
        "verified",
        bundle("save_abort"),
    )
    _assert_rows_share_disposition_and_refs(
        by_requirement_id,
        {"REQ-FED-FM-4_25-requestFederationRestoreFailed"},
        "pitch_disposition",
        "verified",
        bundle("restore_request_failure"),
    )
    _assert_rows_share_disposition_and_refs(
        by_requirement_id,
        {"REQ-RTI-FM-4_30-abortFederationRestore", "HLA1516.1-FM-4.30-MOM-001", "HLA1516.1-FM-4.30-CB-001"},
        "pitch_disposition",
        "verified",
        bundle("restore_abort"),
    )
    _assert_rows_share_disposition_and_refs(
        by_requirement_id,
        {"REQ-RTI-FM-4_28-federateRestoreNotComplete", "REQ-FED-FM-4_29-federationNotRestored"},
        "pitch_disposition",
        "verified",
        bundle("restore_failure"),
    )

    verified_clause4_special_rows = {
        "HLA1516.1-FM-4.1.2-002": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_queued_callback_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_queued_callback_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_queued_callback_matrix",
        ),
        "HLA1516.1-FM-4.17-EXC-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_scenario",
            *bundle("save_failure")[:1],
            *bundle("save_abort")[:1],
        ),
        "HLA1516.1-FM-4.27-EXC-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_scenario",
            *bundle("restore_failure")[:1],
            *bundle("restore_abort")[:1],
        ),
        "HLA1516.1-FM-4.22-EXC-001": bundle("save_status_exception"),
        "HLA1516.1-FM-4.22-MOM-001": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_scenario",
            *bundle("save_failure")[:1],
            *bundle("save_abort")[:1],
        ),
        "HLA1516.1-FM-4.6-MOM-001": bundle("federation_listing"),
        "HLA1516.1-FM-4.12-MOM-001": bundle("synchronization"),
    }
    vendor_divergent_clause4_special_rows = {
        "HLA1516.1-FM-4.5-EXC-001": (
            *bundle("federation_lifecycle_negative")[:1],
            *bundle("fom_integrity_negative")[:1],
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_with_mim_matrix",
        ),
        "HLA1516.1-FM-4.9-EXC-001": (
            *bundle("join_precondition")[:1],
            *bundle("fom_integrity_negative")[:1],
        ),
    }
    for expected_disposition, special_rows in (
        ("verified", verified_clause4_special_rows),
        ("vendor-divergent", vendor_divergent_clause4_special_rows),
    ):
        for requirement_id, expected_refs in special_rows.items():
            _assert_row_disposition_and_refs(
                by_requirement_id,
                requirement_id,
                "pitch_disposition",
                expected_disposition,
                expected_refs,
            )

    blocked_clause4_rows = {
        row["requirement_id"]
        for row in rows.values()
        if _document_matches(row.get("document"), "IEEE 1516.1-2010 (2010 edition)")
        and row["clause_root"] == "4"
        and row["pitch_disposition"] == "blocked"
    }
    assert blocked_clause4_rows == PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS

    residual_clause4_rows = {
        row["requirement_id"] or row["matrix_id"]: row["pitch_disposition"]
        for row in payload["rows"]
        if _document_matches(row.get("document"), "IEEE 1516.1-2010 (2010 edition)")
        and row["clause_root"] == "4"
        and row["pitch_disposition"] != "verified"
    }
    assert residual_clause4_rows == PITCH_CLAUSE4_RESIDUAL_FRONTIER

    _assert_pitch_blocked_rows(
        by_requirement_id,
        PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS,
        notes_fragments=PITCH_CLAUSE4_BLOCKED_NOTES_FRAGMENTS,
        operator_refs=PITCH_CLAUSE4_BLOCKED_FAMILY_REFS,
        jpype_refs=PITCH_CLAUSE4_BLOCKED_JPYPE_REFS,
        py4j_refs=PITCH_CLAUSE4_BLOCKED_PY4J_REFS,
    )

    clause4_seed_row = next(
        row
        for row in raw_rows
        if _document_matches(row.get("document"), "IEEE 1516.1-2010 (2010 edition)")
        and row["clause_root"] == "4"
        and not row["requirement_id"]
        and row["section_ref"].endswith("§4")
    )
    assert clause4_seed_row["pitch_disposition"] == "not-applicable"

    for requirement_id in clause4_residual_verified_rows:
        assert rows[requirement_id]["pitch_disposition"] == "verified"

    assert not {
        row["requirement_id"]
        for row in rows.values()
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)" and row["clause_root"] == "4" and row["pitch_disposition"] == "not-yet-tested"
    }


def test_pitch_clause6_mapped_rows_prefer_shared_harness_evidence_only():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    _assert_clause_mapped_rows_prefer_shared_harness_evidence_only(
        payload,
        clause_root="6",
        strict_prefixes=(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
        "tests/scenarios/test_object_management_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
        "packages/hla2010-rti-pitch-common/docs/evidence/",
        ),
        forbidden_cases=((
            {"REQ-RTI-OM-6_10-updateAttributeValues", "REQ-RTI-OM-6_12-sendInteraction"},
            (
                "tests/backends/test_python_backend_support_services.py",
                "tests/backends/test_python_backend_federation_extended.py",
                "tests/backends/test_python_backend_object_ownership_extended.py",
                "tests/backends/test_python_backend_time_ddm_extended.py",
            ),
        ),),
    )


def test_pitch_clause7_mapped_rows_prefer_shared_harness_evidence_only():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    _assert_clause_mapped_rows_prefer_shared_harness_evidence_only(
        payload,
        clause_root="7",
        strict_prefixes=(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
        "tests/scenarios/test_ownership_management_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
        "packages/hla2010-rti-pitch-common/docs/evidence/",
        ),
        forbidden_cases=(
            (
                {"REQ-FED-OWN-7_10-attributeOwnershipUnavailable"},
                (
                    "tests/backends/test_python_backend_object_ownership_extended.py",
                    "tests/backends/test_certi_backend_callbacks.py",
                    "tests/backends/test_certi_java_profile_callbacks.py",
                ),
            ),
            (
                {"REQ-FED-OWN-7_11-requestAttributeOwnershipRelease"},
                (
                    "tests/backends/test_python_backend_support_services.py",
                    "tests/backends/test_python_backend_federation_extended.py",
                    "tests/backends/test_python_backend_object_ownership_extended.py",
                    "tests/backends/test_python_backend_time_ddm_extended.py",
                    "tests/backends/test_certi_backend_callbacks.py",
                    "tests/backends/test_certi_java_profile_callbacks.py",
                ),
            ),
        ),
    )


def test_pitch_clause8_mapped_rows_prefer_shared_harness_evidence_only():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    _assert_clause_mapped_rows_prefer_shared_harness_evidence_only(
        payload,
        clause_root="8",
        strict_prefixes=(
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::",
        "tests/time/test_section8_backend_matrix.py::",
        "tests/time/test_lookahead_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
        "packages/hla2010-rti-pitch-common/docs/evidence/",
        ),
        forbidden_cases=(
            (
                {"REQ-RTI-TM-8_12-flushQueueRequest"},
                (
                    "tests/backends/test_python_backend_support_services.py",
                    "tests/backends/test_python_backend_federation_extended.py",
                    "tests/backends/test_python_backend_object_ownership_extended.py",
                    "tests/backends/test_python_backend_time_ddm_extended.py",
                ),
            ),
            (
                {"REQ-RTI-TM-8_16-queryGALT"},
                (
                    "tests/verification/test_compliance_slice_v011.py",
                    "tests/backends/test_python_backend_support_services.py",
                    "tests/backends/test_python_backend_federation_extended.py",
                    "tests/backends/test_python_backend_object_ownership_extended.py",
                    "tests/backends/test_python_backend_time_ddm_extended.py",
                ),
            ),
        ),
    )


def test_pitch_clause9_mapped_rows_prefer_shared_harness_evidence_only():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    _assert_clause_mapped_rows_prefer_shared_harness_evidence_only(
        payload,
        clause_root="9",
        strict_prefixes=(
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_ddm_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
        ),
        forbidden_cases=(
            (
                {"REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions"},
                (
                    "tests/backends/test_python_backend_support_services.py",
                    "tests/backends/test_python_backend_federation_extended.py",
                    "tests/backends/test_python_backend_object_ownership_extended.py",
                    "tests/backends/test_python_backend_time_ddm_extended.py",
                    "tests/verification/test_compliance_slice_v011.py",
                ),
            ),
            (
                {"REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions"},
                (
                    "tests/backends/test_python_backend_support_services.py",
                    "tests/backends/test_python_backend_federation_extended.py",
                    "tests/backends/test_python_backend_object_ownership_extended.py",
                    "tests/backends/test_python_backend_time_ddm_extended.py",
                    "tests/verification/test_spec_traceability_and_extended_python_rti.py",
                ),
            ),
        ),
    )


def test_pitch_clause6_1516_1_dispositions_are_fully_classified_and_harness_backed():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="6")
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    vendor_divergent_ids = {
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.24-001",
        "HLA1516.1-OM-6.25-001",
        "HLA1516.1-OM-6.26-001",
        "HLA1516.1-OM-6.27-001",
        "HLA1516.1-OM-6.28-001",
        "HLA1516.1-OM-6.29-001",
        "HLA1516.1-OM-6.30-001",
    }

    _assert_clause_disposition_partition(
        raw_rows,
        total=110,
        blocked_ids=set(),
        vendor_divergent_ids=vendor_divergent_ids,
        verified_count=99,
    )
    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    _assert_clause_rows_have_evidence_shape(
        verified_rows + [rows[requirement_id] for requirement_id in vendor_divergent_ids],
        harness_fragment="packages/hla2010-verification-harness/src/hla2010_verification_harness/",
        test_prefix_groups=(
            ("tests/scenarios/test_object_management_backend_matrix.py::",),
            ("tests/vendors/test_pitch_real_backend_matrix.py::",),
        ),
    )


def test_pitch_clause7_1516_1_dispositions_are_fully_classified_and_harness_backed():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="7")
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    vendor_divergent_ids = {
        "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
    }

    _assert_clause_disposition_partition(
        raw_rows,
        total=39,
        blocked_ids=set(),
        vendor_divergent_ids=vendor_divergent_ids,
        not_applicable_ids={"AREA-1516.1-7", "HLA1516.1-OWN-001"},
        verified_count=27,
    )
    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    _assert_clause_rows_have_evidence_shape(
        verified_rows + [rows[requirement_id] for requirement_id in vendor_divergent_ids],
        harness_fragment="packages/hla2010-verification-harness/src/hla2010_verification_harness/",
        test_prefix_groups=(
            ("tests/scenarios/test_ownership_management_backend_matrix.py::",),
            ("tests/vendors/test_pitch_real_backend_matrix.py::",),
        ),
    )

    probe_rows = {
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
    }
    for requirement_id in probe_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::probe_negotiated_attribute_ownership_offer"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_negotiated_divesting_offer_probe_matrix"
            in row["evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_negotiated_divesting_offer_probe" in row["evidence_refs"]

    negotiated_rows = {
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
    }
    for requirement_id in negotiated_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_negotiated_attribute_ownership_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_negotiated_ownership_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_negotiated_ownership_matrix" in row["evidence_refs"]

    ownership_unavailable_row = rows["REQ-FED-OWN-7_10-attributeOwnershipUnavailable"]
    assert ownership_unavailable_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_unavailable_scenario"
        in ownership_unavailable_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix"
        in ownership_unavailable_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix" in ownership_unavailable_row["evidence_refs"]


def test_pitch_clause8_1516_1_dispositions_are_fully_classified_and_harness_backed():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="8")
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    blocked_ids = set()
    vendor_divergent_ids = {
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
        "REQ-RTI-TM-8_21-retract",
        "REQ-FED-TM-8_22-requestRetraction",
        "HLA1516.1-TM-8.1-001",
        "HLA1516.1-TM-8.1-002",
        "HLA1516.1-TM-8.1.1-001",
        "HLA1516.1-TM-8.1.2-001",
        "HLA1516.1-TM-8.1.2-002",
        "HLA1516.1-TM-8.1.2-003",
        "HLA1516.1-TM-8.1.2-004",
        "HLA1516.1-TM-8.1.3-002",
        "HLA1516.1-TM-8.1.3-003",
        "HLA1516.1-TM-8.1.5-001",
        "HLA1516.1-TM-8.1.6-001",
        "HLA1516.1-TM-8.1.7-001",
        "HLA1516.1-TM-8.10-001",
        "HLA1516.1-TM-8.21-001",
    }

    _assert_clause_disposition_partition(
        raw_rows,
        total=61,
        blocked_ids=blocked_ids,
        vendor_divergent_ids=vendor_divergent_ids,
        not_applicable_ids={"AREA-1516.1-8", "HLA1516.1-TM-001"},
        verified_count=41,
    )
    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    _assert_clause_rows_have_evidence_shape(
        verified_rows + [rows[requirement_id] for requirement_id in vendor_divergent_ids | blocked_ids],
        harness_fragment="packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::",
        test_prefix_groups=(
            (
                "tests/time/test_section8_backend_matrix.py::",
                "tests/time/test_lookahead_backend_matrix.py::",
            ),
            ("tests/vendors/test_pitch_real_backend_matrix.py::",),
        ),
    )

    next_message_request_row = rows["REQ-RTI-TM-8_10-nextMessageRequest"]
    assert next_message_request_row["pitch_disposition"] == "vendor-divergent"
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_ordering_and_query_case"
        in next_message_request_row["evidence_refs"]
    )
    assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries" in next_message_request_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix" in next_message_request_row["evidence_refs"]

    query_galt_row = rows["REQ-RTI-TM-8_16-queryGALT"]
    assert query_galt_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_time_bound_query_case"
        in query_galt_row["evidence_refs"]
    )
    assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_time_bound_queries" in query_galt_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_time_bound_query_matrix" in query_galt_row["evidence_refs"]


def test_pitch_clause9_1516_1_dispositions_are_fully_classified_and_harness_backed():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="9")
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    blocked_ids = set()
    verified_ids = {
        "HLA1516.1-DDM-9.1-001",
        "HLA1516.1-DDM-9.1-002",
        "HLA1516.1-DDM-9.1-003",
        "REQ-RTI-DDM-9_2-createRegion",
        "REQ-RTI-DDM-9_3-commitRegionModifications",
        "REQ-RTI-DDM-9_4-deleteRegion",
        "REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions",
        "REQ-RTI-DDM-9_6-associateRegionsForUpdates",
        "REQ-RTI-DDM-9_7-unassociateRegionsForUpdates",
        "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions",
        "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions",
        "REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions",
        "REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions",
        "REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions",
        "REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions",
        "REQ-RTI-DDM-9_12-sendInteractionWithRegions",
        "REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions",
        "HLA1516.1-DDM-9.2-001",
        "HLA1516.1-DDM-9.3-001",
        "HLA1516.1-DDM-9.4-001",
        "HLA1516.1-DDM-9.5-001",
        "HLA1516.1-DDM-9.6-001",
        "HLA1516.1-DDM-9.7-001",
        "HLA1516.1-DDM-9.8-001",
        "HLA1516.1-DDM-9.9-001",
        "HLA1516.1-DDM-9.10-001",
        "HLA1516.1-DDM-9.11-001",
        "HLA1516.1-DDM-9.12-001",
        "HLA1516.1-DDM-9.13-001",
    }

    _assert_clause_disposition_partition(
        raw_rows,
        total=31,
        blocked_ids=blocked_ids,
        vendor_divergent_ids=set(),
        not_applicable_ids={"AREA-1516.1-9", "HLA1516.1-DDM-001"},
        verified_ids=verified_ids,
    )

    _assert_clause_rows_have_evidence_shape(
        [rows[requirement_id] for requirement_id in verified_ids | blocked_ids],
        harness_fragment="packages/hla2010-verification-harness/src/hla2010_verification_harness/",
        test_prefix_groups=(
            ("tests/scenarios/test_ddm_backend_matrix.py::",),
            ("tests/vendors/test_pitch_real_backend_matrix.py::",),
        ),
    )

    suite_ddm_row = rows["HLA1516.1-DDM-9.1-001"]
    assert suite_ddm_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/two_federate_suite_scenarios.py::run_suite_ddm_scenario"
        in suite_ddm_row["evidence_refs"]
    )
    assert "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix" in suite_ddm_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_matrix" in suite_ddm_row["evidence_refs"]

    passive_region_row = rows["REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions"]
    assert passive_region_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario"
        in passive_region_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_passive_region_subscription_matrix"
        in passive_region_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_passive_region_subscription_matrix" in passive_region_row["evidence_refs"]

    region_lifecycle_row = rows["REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions"]
    assert region_lifecycle_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario"
        in region_lifecycle_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix"
        in region_lifecycle_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_object_region_lifecycle_matrix" in region_lifecycle_row["evidence_refs"]


def test_pitch_clause10_1516_1_dispositions_are_explicitly_staged():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="10")
    rows = _clause_rows_by_requirement(payload, clause_root="10")

    assert len(raw_rows) == 84
    clause10_counts = _clause_summary_counts(payload, clause_root="10", disposition_key="pitch_disposition")
    assert clause10_counts["total"] == 84
    assert clause10_counts["not-applicable"] == 2
    assert clause10_counts.get("blocked", 0) == 0
    assert clause10_counts.get("vendor-divergent", 0) == 0
    assert clause10_counts.get("verified", 0) == 0
    assert clause10_counts.get("classification-required", 0) + clause10_counts["not-yet-tested"] == 82
    assert _requirement_ids_with_disposition(
        raw_rows,
        disposition_key="pitch_disposition",
        disposition="not-applicable",
    ) == {"AREA-1516.1-10", "HLA1516.1-SUP-001"}

    not_yet_tested_ids = _requirement_ids_with_disposition(
        raw_rows,
        disposition_key="pitch_disposition",
        disposition="not-yet-tested",
    )
    assert len(not_yet_tested_ids) == 82
    assert {"REQ-RTI-SS-10_4-getFederateHandle", "REQ-RTI-SS-10_41-evokeCallback", "HLA1516.1-SUP-10.17-001"} <= not_yet_tested_ids
    _assert_rows_have_disposition_and_ref(
        rows,
        {"REQ-RTI-SS-10_4-getFederateHandle", "REQ-RTI-SS-10_41-evokeCallback", "HLA1516.1-SUP-10.17-001"},
        disposition_key="pitch_disposition",
        expected_disposition="not-yet-tested",
        expected_ref="analysis/compliance/section10_backend_matrix.json",
    )


def test_pitch_clause11_mom_rows_are_explicitly_staged() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="11")
    rows = _clause_rows_by_requirement(payload, clause_root="11")

    assert _clause_summary_counts(
        payload,
        clause_root="11",
        disposition_key="pitch_disposition",
    ) == {
        "classification-required": 35,
        "not-applicable": 2,
        "total": 37,
    }
    assert len(raw_rows) == 37
    _assert_clause_disposition_counts(
        raw_rows,
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": 35,
            "not-yet-tested": 0,
            "not-applicable": 2,
            "vendor-divergent": 0,
            "verified": 0,
        },
    )
    assert _requirement_ids_with_disposition(
        raw_rows,
        disposition_key="pitch_disposition",
        disposition="not-applicable",
    ) == {"AREA-1516.1-11", "HLA1516.1-MOM-001"}

    classification_required_ids = _requirement_ids_with_disposition(
        raw_rows,
        disposition_key="pitch_disposition",
        disposition="classification-required",
    )
    assert len(classification_required_ids) == 35
    assert {
        "HLA1516.1-MOM-11.1-001",
        "HLA1516.1-MOM-11.2.1-003",
        "HLA1516.1-MOM-11.6-001",
    } <= classification_required_ids
    for requirement_id in classification_required_ids:
        assert rows[requirement_id]["evidence_refs"] == []


def test_pitch_clause12_designator_rows_are_explicitly_not_yet_tested():
    payload = _compliance_payload("pitch_requirement_disposition.json")
    raw_rows = _clause_rows(payload, clause_root="12")
    rows = _clause_rows_by_requirement(payload, clause_root="12")

    clause12_summary = _clause_summary_counts(
        payload,
        clause_root="12",
        disposition_key="pitch_disposition",
    )
    assert clause12_summary == {
        "not-applicable": 1,
        "not-yet-tested": 9,
        "total": 10,
    }
    assert len(raw_rows) == 10
    _assert_clause_disposition_counts(
        raw_rows,
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": 0,
            "not-yet-tested": 9,
            "not-applicable": 1,
            "vendor-divergent": 0,
            "verified": 0,
        },
    )
    assert _requirement_ids_with_disposition(
        raw_rows,
        disposition_key="pitch_disposition",
        disposition="not-applicable",
    ) == {"AREA-1516.1-12"}

    clause12_decode_rows = {
        "REQ-RTI-PLM-12_2-decodeAttributeHandle",
        "REQ-RTI-PLM-12_2-decodeDimensionHandle",
        "REQ-RTI-PLM-12_2-decodeFederateHandle",
        "REQ-RTI-PLM-12_2-decodeInteractionClassHandle",
        "REQ-RTI-PLM-12_2-decodeMessageRetractionHandle",
        "REQ-RTI-PLM-12_2-decodeObjectClassHandle",
        "REQ-RTI-PLM-12_2-decodeObjectInstanceHandle",
        "REQ-RTI-PLM-12_2-decodeParameterHandle",
        "REQ-RTI-PLM-12_2-decodeRegionHandle",
    }
    _assert_rows_have_disposition_and_ref(
        rows,
        clause12_decode_rows,
        disposition_key="pitch_disposition",
        expected_disposition="not-yet-tested",
        expected_ref="packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_support_services.py::run_support_factory_and_decode_scenario",
    )
    for requirement_id in clause12_decode_rows:
        assert "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix" in rows[requirement_id]["evidence_refs"]


def test_pitch_supporting_slices_and_non_omt_clause4_staging() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    _assert_row_disposition_and_refs(
        rows,
        "REQ-SAVE-RESTORE-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
    )

    supporting_restore_slices = {
        "REQ-SAVE-RESTORE-OBJECT-STATE-001": (
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_object_state_scenario",
                "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_object_state_matrix",
                "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_object_state_matrix",
            ),
        ),
        "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001": (
            "verified",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_federate_local_state_scenario",
                "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_federate_local_state_matrix",
                "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_federate_local_state_matrix",
            ),
        ),
        "REQ-SAVE-RESTORE-CALLBACK-POLICY-001": (
            "not-applicable",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_callback_policy_scenario",
                "tests/verification/test_compliance_slice_v011.py::test_restore_treats_callback_enablement_as_runtime_policy_not_saved_state",
            ),
        ),
        "REQ-SAVE-RESTORE-TRANSIENT-STATE-001": (
            "not-applicable",
            (
                "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_save_restore.py::run_restore_transient_state_scenario",
                "tests/verification/test_compliance_slice_v011.py::test_restore_discards_pre_restore_callback_queue_and_retraction_bookkeeping",
            ),
        ),
    }
    for requirement_id, (expected_disposition, expected_refs) in supporting_restore_slices.items():
        _assert_row_disposition_and_refs(
            rows,
            requirement_id,
            "pitch_disposition",
            expected_disposition,
            expected_refs,
        )

    assert rows["REQ-OMT-PARSE-001"]["pitch_disposition"] == "not-applicable"
    assert any(ref.endswith("src/hla2010/fom.py::parse_fom_xml") for ref in rows["REQ-OMT-PARSE-001"]["evidence_refs"])
    _assert_row_includes_refs(
        rows,
        "REQ-OMT-PARSE-001",
        "tests/factories/test_fom_omt_parsing.py",
        "analysis/compliance/verification_assets.json",
    )
    _assert_row_disposition_and_refs(
        rows,
        "SCENARIO-TARGET-RADAR-001",
        "pitch_disposition",
        "not-applicable",
        (
            "tests/scenarios/test_target_radar_scenario.py",
            "analysis/compliance/verification_assets.json",
            "docs/evidence/hla2010_python_verification_evidence_v0_13/docs/mom_table_verification_v0_12.md",
        ),
    )
    _assert_no_classification_required_outside_document(
        rows,
        clause_root="4",
        disposition_key="pitch_disposition",
        excluded_document="IEEE 1516.2-2010 (2010 edition)",
    )


def test_pitch_clause5_declaration_surface_is_compact_and_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    assert _clause_summary_counts(
        payload,
        clause_root="5",
        disposition_key="pitch_disposition",
    ) == {
        "blocked": 2,
        "not-applicable": 5,
        "total": 52,
        "verified": 45,
    }

    declaration_rows = {
        "REQ-RTI-DM-5_2-publishObjectClassAttributes",
        "REQ-RTI-DM-5_3-unpublishObjectClassAttributes",
        "REQ-RTI-DM-5_4-publishInteractionClass",
        "REQ-RTI-DM-5_5-unpublishInteractionClass",
        "REQ-RTI-DM-5_6-subscribeObjectClassAttributes",
        "REQ-RTI-DM-5_7-unsubscribeObjectClassAttributes",
        "REQ-RTI-DM-5_8-subscribeInteractionClass",
        "REQ-RTI-DM-5_9-unsubscribeInteractionClass",
        "REQ-FED-DM-5_10-startRegistrationForObjectClass",
        "REQ-FED-DM-5_11-stopRegistrationForObjectClass",
        "REQ-FED-DM-5_12-turnInteractionsOn",
        "REQ-FED-DM-5_13-turnInteractionsOff",
        "HLA1516.1-DM-5.1-001",
        "HLA1516.1-DM-5.1-002",
        "HLA1516.1-DM-5.1-003",
        "HLA1516.1-DM-5.1.2-001",
        "HLA1516.1-DM-5.1.2-002",
        "HLA1516.1-DM-5.1.3-001",
        "HLA1516.1-DM-5.1.3-002",
        "HLA1516.1-DM-5.10-001",
        "HLA1516.1-DM-5.11-001",
        "HLA1516.1-DM-5.12-001",
        "HLA1516.1-DM-5.13-001",
        "HLA1516.1-DM-5.2-001",
        "HLA1516.1-DM-5.2-002",
        "HLA1516.1-DM-5.3-001",
        "HLA1516.1-DM-5.4-001",
        "HLA1516.1-DM-5.4-002",
        "HLA1516.1-DM-5.5-001",
        "HLA1516.1-DM-5.6-001",
        "HLA1516.1-DM-5.6-002",
        "HLA1516.1-DM-5.6-003",
        "HLA1516.1-DM-5.7-001",
        "HLA1516.1-DM-5.7-002",
        "HLA1516.1-DM-5.8-001",
        "HLA1516.1-DM-5.8-002",
        "HLA1516.1-DM-5.9-001",
    }
    _assert_rows_share_disposition_and_refs(
        rows,
        declaration_rows,
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_declaration.py::run_declaration_management_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_management_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.1-DM-5.1.6-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_update_rate.py::run_update_rate_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_update_rate_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_update_rate_matrix",
        ),
    )

    declaration_overload_rows = {
        "REQ-RTI-DM-5_3-unpublishObjectClass",
        "REQ-RTI-DM-5_6-subscribeObjectClassAttributesPassively",
        "REQ-RTI-DM-5_7-unsubscribeObjectClass",
        "REQ-RTI-DM-5_8-subscribeInteractionClassPassively",
    }
    _assert_rows_share_disposition_and_refs(
        rows,
        declaration_overload_rows,
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_declaration.py::run_declaration_management_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_overload_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_management_overload_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.1-DM-5.2-003",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_declaration.py::run_declaration_invalid_attribute_publication_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_invalid_attribute_publication_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_invalid_attribute_publication_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.1-DM-5.1-004",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_declaration.py::run_time_managed_declaration_independence_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_time_managed_declaration_independence_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_time_managed_declaration_independence_matrix",
        ),
    )

    assert rows["HLA1516.1-DM-5.1.1-001"]["pitch_disposition"] == "not-applicable"
    assert any(ref.endswith("src/hla2010/fom.py::parse_fom_xml") for ref in rows["HLA1516.1-DM-5.1.1-001"]["evidence_refs"])
    assert any(ref.endswith("src/hla2010/fom.py::merge_fom_modules") for ref in rows["HLA1516.1-DM-5.1.1-001"]["evidence_refs"])
    _assert_row_includes_refs(
        rows,
        "HLA1516.1-DM-5.1.1-001",
        "tests/factories/test_fom_omt_parsing.py",
        "analysis/compliance/verification_assets.json",
    )
    for requirement_id in {"HLA1516.1-DM-5.1.1-002", "HLA1516.1-DM-5.1.1-003"}:
        assert rows[requirement_id]["pitch_disposition"] == "not-applicable"
        assert any(ref.endswith("src/hla2010/fom.py::parse_fom_xml") for ref in rows[requirement_id]["evidence_refs"])
        _assert_row_includes_refs(
            rows,
            requirement_id,
            "tests/factories/test_fom_omt_parsing.py",
            "analysis/compliance/verification_assets.json",
        )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"HLA1516.1-DM-5.3-002", "HLA1516.1-DM-5.5-002"},
        "pitch_disposition",
        "blocked",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_declaration.py::run_declaration_unpublish_rejection_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_unpublish_rejection_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_unpublish_rejection_matrix",
        ),
    )
    assert {
        requirement_id
        for requirement_id, row in rows.items()
        if row["clause_root"] == "5"
        and row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["pitch_disposition"] == "classification-required"
    } == set()


def test_pitch_clause6_object_management_surface_is_compact_and_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    assert _clause_summary_counts(
        payload,
        clause_root="6",
        disposition_key="pitch_disposition",
    ) == {
        "not-applicable": 2,
        "total": 110,
        "vendor-divergent": 9,
        "verified": 99,
    }

    clause6_cases = (
        (
            {
                "REQ-RTI-OM-6_2-reserveObjectInstanceName",
                "REQ-FED-OM-6_3-objectInstanceNameReservationSucceeded",
                "REQ-FED-OM-6_3-objectInstanceNameReservationFailed",
                "REQ-RTI-OM-6_4-releaseObjectInstanceName",
                "REQ-RTI-OM-6_5-reserveMultipleObjectInstanceName",
                "REQ-FED-OM-6_6-multipleObjectInstanceNameReservationSucceeded",
                "REQ-FED-OM-6_6-multipleObjectInstanceNameReservationFailed",
                "REQ-RTI-OM-6_7-releaseMultipleObjectInstanceName",
            },
            bundle("name_reservation"),
        ),
        (
            {
                "REQ-RTI-OM-6_8-registerObjectInstance",
                "REQ-FED-OM-6_9-discoverObjectInstance",
                "REQ-FED-OM-6_11-reflectAttributeValues",
                "REQ-FED-OM-6_13-receiveInteraction",
                "REQ-RTI-OM-6_14-deleteObjectInstance",
                "REQ-FED-OM-6_15-removeObjectInstance",
            },
            bundle("exchange"),
        ),
        (
            {
                "REQ-FED-OM-6_9-hasProducingFederate",
                "REQ-FED-OM-6_9-getProducingFederate",
                "REQ-FED-OM-6_9-hasSentRegions",
                "REQ-FED-OM-6_9-getSentRegions",
            },
            bundle("discovery_metadata"),
        ),
        (
            {
                "REQ-FED-OM-6_17-attributesInScope",
                "REQ-FED-OM-6_18-attributesOutOfScope",
                "REQ-FED-OM-6_20-provideAttributeValueUpdate",
                "REQ-FED-OM-6_21-turnUpdatesOnForObjectInstance",
                "REQ-FED-OM-6_22-turnUpdatesOffForObjectInstance",
            },
            bundle("update_advisory"),
        ),
        (
            {
                "REQ-FED-OM-6_24-confirmAttributeTransportationTypeChange",
                "REQ-RTI-OM-6_25-queryAttributeTransportationType",
                "REQ-FED-OM-6_26-reportAttributeTransportationType",
                "REQ-FED-OM-6_28-confirmInteractionTransportationTypeChange",
                "REQ-RTI-OM-6_29-queryInteractionTransportationType",
                "REQ-FED-OM-6_30-reportInteractionTransportationType",
            },
            bundle("transportation_type"),
        ),
    )
    for requirement_ids, expected_refs in clause6_cases:
        _assert_rows_share_disposition_and_refs(
            rows,
            requirement_ids,
            "pitch_disposition",
            "verified",
            expected_refs,
        )

    _assert_row_disposition_and_refs(rows, "REQ-RTI-OM-6_16-localDeleteObjectInstance", "pitch_disposition", "verified", bundle("local_delete"))
    _assert_row_disposition_and_refs(rows, "REQ-RTI-OM-6_19-requestAttributeValueUpdate", "pitch_disposition", "verified", bundle("request_attribute_value_update"))
    for requirement_id in {
        "REQ-RTI-OM-6_23-requestAttributeTransportationTypeChange",
        "REQ-RTI-OM-6_27-requestInteractionTransportationTypeChange",
    }:
        _assert_row_disposition_and_refs(
            rows,
            requirement_id,
            "pitch_disposition",
            "verified",
            bundle("transportation_type") + bundle("transportation_type_restore_persistence"),
        )

    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture",
            "REQ-FED-OWN-7_7-attributeOwnershipAcquisitionNotification",
            "REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable",
            "REQ-RTI-OWN-7_17-queryAttributeOwnership",
            "REQ-FED-OWN-7_18-attributeIsNotOwned",
            "REQ-FED-OWN-7_18-informAttributeOwnership",
            "REQ-RTI-OWN-7_19-isAttributeOwnedByFederate",
        },
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-FED-OWN-7_10-attributeOwnershipUnavailable",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_unavailable_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix",
        ),
    )

    extracted_clause6_rows = {
        "HLA1516.1-OM-6.2-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.3-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.4-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.5-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.6-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.7-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.1-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.1-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-003": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-005": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.1-002": "scenario_discovery_class.py::run_discovery_class_scenario",
        "HLA1516.1-OM-6.1.1-003": "scenario_discovery_class.py::run_discovery_class_scenario",
        "HLA1516.1-OM-6.1.1-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.2-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.3-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.4-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.5-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.7-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.11-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.12-001": "scenario_update_rate.py::run_update_rate_scenario",
        "HLA1516.1-OM-6.12-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-003": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-005": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-003": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.9-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.11-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.11-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.13-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.14-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.14-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.15-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.6-001": "scenario_local_delete.py::run_local_delete_scenario",
        "HLA1516.1-OM-6.16-001": "scenario_local_delete.py::run_local_delete_scenario",
        "HLA1516.1-OM-6.16-002": "scenario_local_delete.py::run_local_delete_scenario",
        "HLA1516.1-OM-6.17-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.18-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.19-001": "scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
        "HLA1516.1-OM-6.19-002": "scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
        "HLA1516.1-OM-6.21-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.21-002": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.22-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.1.10-002": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.1.10-003": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.23-002": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.24-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.24-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "HLA1516.1-OM-6.25-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.26-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.26-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "HLA1516.1-OM-6.27-002": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.28-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.28-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "HLA1516.1-OM-6.29-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.30-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.30-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
    }
    for requirement_id, harness_ref in extracted_clause6_rows.items():
        assert rows[requirement_id]["pitch_disposition"] == "verified"
        assert any(harness_ref in ref for ref in rows[requirement_id]["evidence_refs"])

    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-RTI-OM-6_10-updateAttributeValues", "REQ-RTI-OM-6_12-sendInteraction"},
        "pitch_disposition",
        "verified",
        bundle("exchange"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"HLA1516.1-OM-6.10-005", "HLA1516.1-OM-6.12-005"},
        "pitch_disposition",
        "verified",
        bundle("exchange") + bundle("transportation_type"),
    )

    vendor_divergent_clause6_rows = {
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.24-001",
        "HLA1516.1-OM-6.25-001",
        "HLA1516.1-OM-6.26-001",
        "HLA1516.1-OM-6.27-001",
        "HLA1516.1-OM-6.28-001",
        "HLA1516.1-OM-6.29-001",
        "HLA1516.1-OM-6.30-001",
    }
    _assert_rows_share_disposition_and_refs(
        rows,
        vendor_divergent_clause6_rows,
        "pitch_disposition",
        "vendor-divergent",
        ("packages/hla2010-rti-pitch-common/docs/evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md",)
        + bundle("transportation_type")[:1],
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"HLA1516.1-OM-6.1.10-001", "HLA1516.1-OM-6.23-001", "HLA1516.1-OM-6.27-001"},
        "pitch_disposition",
        "vendor-divergent",
        ("packages/hla2010-rti-pitch-common/docs/evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md",)
        + bundle("transportation_type")[:1]
        + bundle("transportation_type_restore_persistence"),
    )

    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-OM-DISCOVERY-CLASS-001", "REQ-OM-REFLECT-KNOWN-CLASS-001"},
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_discovery_class.py::run_discovery_class_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_class_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_class_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-OM-LOCAL-KNOWLEDGE-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_local_delete.py::run_local_delete_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_local_delete_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_local_delete_matrix",
        ),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-OM-ORPHAN-KNOWLEDGE-001", "REQ-OM-ORPHAN-LIFECYCLE-001"},
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_orphan_object.py::run_orphan_object_lifecycle_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_orphan_object_lifecycle_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_orphan_object_lifecycle_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-OM-TIMED-DELETE-REMOVE-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_timed_delete.py::run_timed_delete_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_timed_delete_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_timed_delete_matrix",
        ),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-OM-ATTRIBUTE-RELEVANCE-001", "REQ-OM-SCOPE-CALLBACKS-001"},
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_object_scope.py::run_object_scope_relevance_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_object_scope_relevance_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_object_scope_relevance_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-OM-REQUEST-VALUE-UPDATE-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-OM-REQUEST-VALUE-UPDATE-ROUTING-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_request_attribute_value_update.py::run_request_attribute_value_update_routing_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_routing_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_routing_matrix",
        ),
    )

    assert rows["REQ-OM-TRANSPORT-REPORT-001"]["pitch_disposition"] == "verified"
    _assert_row_includes_refs(
        rows,
        "REQ-OM-TRANSPORT-REPORT-001",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix",
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_rejection_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_rejection_matrix",
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-OM-TRANSPORT-BEST-EFFORT-001",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix",
        ),
    )
    assert rows["REQ-OM-DISCOVERY-LIFECYCLE-001"]["pitch_disposition"] == "verified"
    for harness_ref in (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_exchange.py::run_two_federate_exchange_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_discovery_class.py::run_discovery_class_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_timed_delete.py::run_timed_delete_scenario",
    ):
        assert harness_ref in rows["REQ-OM-DISCOVERY-LIFECYCLE-001"]["evidence_refs"]
    assert rows["REQ-OM-TRANSPORT-SCOPE-001"]["pitch_disposition"] == "vendor-divergent"
    for harness_ref in (
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_object_scope.py::run_object_scope_relevance_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_local_delete.py::run_local_delete_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
    ):
        assert harness_ref in rows["REQ-OM-TRANSPORT-SCOPE-001"]["evidence_refs"]

    clause6_rows = {
        requirement_id: row
        for requirement_id, row in rows.items()
        if requirement_id.startswith("HLA1516.1-OM-6.")
    }
    clause6_disposition_counts: dict[str, int] = {}
    for row in clause6_rows.values():
        clause6_disposition_counts[row["pitch_disposition"]] = clause6_disposition_counts.get(row["pitch_disposition"], 0) + 1
    assert clause6_disposition_counts == {"verified": 64, "vendor-divergent": 9}
    assert {
        requirement_id
        for requirement_id, row in clause6_rows.items()
        if row["pitch_disposition"] != "verified"
    } == vendor_divergent_clause6_rows
    _assert_clause_residual_frontier(
        payload,
        clause_root="6",
        disposition_key="pitch_disposition",
        expected={
            "AREA-1516.1-6": "not-applicable",
            "HLA1516.1-OM-001": "not-applicable",
            "HLA1516.1-OM-6.1.10-001": "vendor-divergent",
            "HLA1516.1-OM-6.23-001": "vendor-divergent",
            "HLA1516.1-OM-6.24-001": "vendor-divergent",
            "HLA1516.1-OM-6.25-001": "vendor-divergent",
            "HLA1516.1-OM-6.26-001": "vendor-divergent",
            "HLA1516.1-OM-6.27-001": "vendor-divergent",
            "HLA1516.1-OM-6.28-001": "vendor-divergent",
            "HLA1516.1-OM-6.29-001": "vendor-divergent",
            "HLA1516.1-OM-6.30-001": "vendor-divergent",
        },
    )
    assert {
        requirement_id
        for requirement_id, row in rows.items()
        if row["clause_root"] == "6" and row["pitch_disposition"] == "classification-required"
    } == set()
    _assert_clause_disposition_counts(
        _clause_rows(payload, clause_root="6"),
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": 0,
            "not-yet-tested": 0,
            "not-applicable": 2,
            "vendor-divergent": 9,
            "verified": 99,
        },
    )


def test_pitch_clause7_merge_and_omt_conformance_surfaces_are_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.2-OMT-6-001",
        "pitch_disposition",
        "verified",
        (
            "docs/verification/requirements_hierarchy.md",
            "requirements/reference/hla1516_2_priority_omt.csv",
            "tests/verification/test_requirement_traceability_1516_2_v013.py",
        ),
    )
    assert rows["REQ-OMT-6-conformance"]["pitch_disposition"] == "not-applicable"
    assert "HLA1516.2-OMT-6-001" not in rows["REQ-OMT-6-conformance"]["evidence_refs"]
    assert _clause_summary_counts(
        payload,
        clause_root="7",
        disposition_key="pitch_disposition",
    ) == {
        "not-applicable": 2,
        "total": 39,
        "vendor-divergent": 10,
        "verified": 27,
    }

    clause7_merge_cases = (
        (
            {"HLA1516.2-MERGE-7-001", "HLA1516.2-OMT-7-001", "HLA1516.2-MERGE-7.0-005", "HLA1516.2-MERGE-7.0-006"},
            "verified",
            bundle("fom_integrity_negative"),
        ),
        (
            {
                "HLA1516.2-OMT-7-002",
                "REQ-OMT-7-merging_rules",
                "HLA1516.2-MERGE-7.0-001",
                "HLA1516.2-MERGE-7.0-002",
                "HLA1516.2-MERGE-7.0-003",
                "HLA1516.2-MERGE-7.0-004",
                "HLA1516.2-MERGE-7.0-007",
                "REQ-OMT-MERGE-001",
            },
            "verified",
            bundle("multi_module_fom_visibility"),
        ),
        (
            {"HLA1516.2-MERGE-7.0-008"},
            "verified",
            bundle("fom_module_visibility"),
        ),
        (
            {"HLA1516.2-MERGE-7-002"},
            "vendor-divergent",
            bundle("federation_lifecycle_with_mim"),
        ),
    )
    for requirement_ids, expected_disposition, expected_refs in clause7_merge_cases:
        _assert_rows_share_disposition_and_refs(
            rows,
            requirement_ids,
            "pitch_disposition",
            expected_disposition,
            expected_refs,
        )

    clause7_merge_requirement_ids = {
        "HLA1516.2-MERGE-7-001",
        "HLA1516.2-MERGE-7-002",
        "HLA1516.2-OMT-7-001",
        "HLA1516.2-OMT-7-002",
        "REQ-OMT-7-merging_rules",
        "HLA1516.2-MERGE-7.0-001",
        "HLA1516.2-MERGE-7.0-002",
        "HLA1516.2-MERGE-7.0-003",
        "HLA1516.2-MERGE-7.0-004",
        "HLA1516.2-MERGE-7.0-005",
        "HLA1516.2-MERGE-7.0-006",
        "HLA1516.2-MERGE-7.0-007",
        "HLA1516.2-MERGE-7.0-008",
        "REQ-OMT-MERGE-001",
    }
    assert {
        requirement_id
        for requirement_id in clause7_merge_requirement_ids
        if rows[requirement_id]["pitch_disposition"] == "classification-required"
    } == set()


def test_pitch_omt_clause_staging_surfaces_are_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    assert _clause_summary_counts(
        payload,
        clause_root="4",
        disposition_key="pitch_disposition",
        document="IEEE 1516.2-2010 (2010 edition)",
    ) == {
        "classification-required": 99,
        "total": 99,
    }
    assert _clause_summary_counts(
        payload,
        clause_root="5",
        disposition_key="pitch_disposition",
        document="IEEE 1516.2-2010 (2010 edition)",
    ) == {
        "classification-required": 2,
        "total": 2,
    }
    assert _clause_summary_counts(
        payload,
        clause_root="6",
        disposition_key="pitch_disposition",
        document="IEEE 1516.2-2010 (2010 edition)",
    ) == {
        "not-applicable": 1,
        "total": 2,
        "verified": 1,
    }
    assert _clause_summary_counts(
        payload,
        clause_root="7",
        disposition_key="pitch_disposition",
        document="IEEE 1516.2-2010 (2010 edition)",
    ) == {
        "total": 13,
        "vendor-divergent": 1,
        "verified": 12,
    }
    _assert_omt_clause_is_unverified_staging_surface(payload, clause_root="4", total=99, classification_required=99)
    _assert_omt_clause_is_unverified_staging_surface(payload, clause_root="5", total=2, classification_required=2)
    _assert_row_disposition_and_refs(
        rows,
        "HLA1516.2-OMT-6-001",
        "pitch_disposition",
        "verified",
        (
            "docs/verification/requirements_hierarchy.md",
            "requirements/reference/hla1516_2_priority_omt.csv",
            "tests/verification/test_requirement_traceability_1516_2_v013.py",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-OMT-6-conformance",
        "pitch_disposition",
        "not-applicable",
        (
            "docs/verification/requirements_hierarchy.md",
            "requirements/reference/hla1516_2_priority_omt.csv",
            "tests/verification/test_requirement_traceability_1516_2_v013.py",
        ),
    )


def test_pitch_clause7_ownership_surface_is_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    _assert_row_disposition_and_refs(
        rows,
        "REQ-FED-OWN-7_18-attributeIsOwnedByRTI",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_attribute_ownership_query_callback_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_attribute_ownership_query_callback_matrix",
        ),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-OWN-7_8-attributeOwnershipAcquisition",
            "REQ-FED-OWN-7_11-requestAttributeOwnershipRelease",
            "REQ-RTI-OWN-7_13-attributeOwnershipDivestitureIfWanted",
        },
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_release_request_ownership_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_request_ownership_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_release_request_owned_attribute_probe",
        ),
    )
    _assert_row_disposition_and_refs(
        rows,
        "REQ-RTI-OWN-7_12-attributeOwnershipReleaseDenied",
        "pitch_disposition",
        "verified",
        (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py::run_release_request_ownership_scenario",
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_denied_ownership_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_release_denied_ownership_matrix",
        ),
    )
    _assert_row_disposition_and_refs(rows, "HLA1516.1-OWN-7.1-003", "pitch_disposition", "verified", bundle("non_owner_update_rejection"))
    _assert_row_disposition_and_refs(rows, "REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption", "pitch_disposition", "verified", bundle("negotiated_divesting_offer_probe"))

    negotiated_ownership_rows = {
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
    }
    _assert_rows_share_disposition_and_refs(
        rows,
        negotiated_ownership_rows,
        "pitch_disposition",
        "vendor-divergent",
        bundle("negotiated_ownership"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
            "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
            "REQ-RTI-OWN-7_6-confirmDivestiture",
            "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture",
            "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
            "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
            "HLA1516.1-OWN-7.3-001",
            "HLA1516.1-OWN-7.4-001",
        },
        "pitch_disposition",
        "vendor-divergent",
        ("packages/hla2010-rti-pitch-common/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md",),
    )
    _assert_clause_residual_frontier(
        payload,
        clause_root="7",
        disposition_key="pitch_disposition",
        expected={
            "AREA-1516.1-7": "not-applicable",
            "HLA1516.1-OWN-001": "not-applicable",
            "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture": "vendor-divergent",
            "REQ-FED-OWN-7_5-requestDivestitureConfirmation": "vendor-divergent",
            "REQ-RTI-OWN-7_6-confirmDivestiture": "vendor-divergent",
            "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture": "vendor-divergent",
            "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition": "vendor-divergent",
            "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation": "vendor-divergent",
            "HLA1516.1-OWN-7.3-001": "vendor-divergent",
            "HLA1516.1-OWN-7.4-001": "vendor-divergent",
            "HLA1516.1-OWN-7.10-001": "vendor-divergent",
            "HLA1516.1-OWN-7.11-001": "vendor-divergent",
        },
    )
    _assert_clause_disposition_counts(
        _clause_rows(payload, clause_root="7"),
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": 0,
            "not-yet-tested": 0,
            "not-applicable": 2,
            "vendor-divergent": 10,
            "verified": 27,
        },
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "HLA1516.1-OWN-7.1-001",
            "HLA1516.1-OWN-7.1-002",
            "HLA1516.1-OWN-7.2-001",
            "HLA1516.1-OWN-7.6-001",
            "HLA1516.1-OWN-7.9-001",
            "HLA1516.1-OWN-7.7-001",
            "HLA1516.1-OWN-7.12-001",
        },
        "pitch_disposition",
        "verified",
        bundle("ownership")[:1],
    )
    _assert_row_disposition_and_refs(rows, "HLA1516.1-OWN-7.5-001", "pitch_disposition", "verified", bundle("release_request_ownership")[:1])
    assert rows["HLA1516.1-OWN-7.7-002"]["pitch_disposition"] == "verified"
    for ref in bundle("release_denied_ownership")[1:]:
        assert ref in rows["HLA1516.1-OWN-7.7-002"]["evidence_refs"]
    _assert_row_disposition_and_refs(rows, "HLA1516.1-OWN-7.8-001", "pitch_disposition", "verified", bundle("ownership_unavailable")[:1])
    _assert_row_disposition_and_refs(rows, "HLA1516.1-OWN-7.9-002", "pitch_disposition", "verified", bundle("ownership_unavailable"))
    _assert_row_disposition_and_refs(rows, "HLA1516.1-OWN-7.13-001", "pitch_disposition", "verified", bundle("ownership_query_callback"))


def test_pitch_clause9_ddm_surface_is_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    _assert_rows_share_disposition_and_refs(
        rows,
        {"HLA1516.1-DDM-9.1-001", "HLA1516.1-DDM-9.1-002", "HLA1516.1-DDM-9.1-003"},
        "pitch_disposition",
        "verified",
        bundle("ddm_suite"),
    )
    assert _clause_summary_counts(
        payload,
        clause_root="9",
        disposition_key="pitch_disposition",
    ) == {
        "not-applicable": 2,
        "total": 31,
        "verified": 29,
    }
    for row in _clause_rows(payload, clause_root="9"):
        if row["pitch_disposition"] == "not-applicable":
            continue
        refs = row["evidence_refs"]
        assert any("packages/hla2010-verification-harness/src/hla2010_verification_harness/" in ref for ref in refs), row["requirement_id"] or row["matrix_id"]
        assert any(ref.startswith("tests/scenarios/test_ddm_backend_matrix.py::") for ref in refs), row["requirement_id"] or row["matrix_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"] or row["matrix_id"]
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-DDM-9_2-createRegion",
            "REQ-RTI-DDM-9_3-commitRegionModifications",
            "REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions",
            "REQ-RTI-DDM-9_12-sendInteractionWithRegions",
            "HLA1516.1-DDM-9.2-001",
            "HLA1516.1-DDM-9.3-001",
            "HLA1516.1-DDM-9.10-001",
            "HLA1516.1-DDM-9.12-001",
        },
        "pitch_disposition",
        "verified",
        bundle("ddm_suite"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-DDM-9_4-deleteRegion",
            "REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions",
            "REQ-RTI-DDM-9_6-associateRegionsForUpdates",
            "REQ-RTI-DDM-9_7-unassociateRegionsForUpdates",
            "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions",
            "REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions",
            "REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions",
            "REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions",
            "HLA1516.1-DDM-9.4-001",
            "HLA1516.1-DDM-9.5-001",
            "HLA1516.1-DDM-9.6-001",
            "HLA1516.1-DDM-9.7-001",
            "HLA1516.1-DDM-9.8-001",
            "HLA1516.1-DDM-9.9-001",
            "HLA1516.1-DDM-9.11-001",
            "HLA1516.1-DDM-9.13-001",
        },
        "pitch_disposition",
        "verified",
        bundle("ddm_object_region_lifecycle"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions",
            "REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions",
        },
        "pitch_disposition",
        "verified",
        bundle("ddm_passive_region_subscription"),
    )
    _assert_row_disposition_and_refs(rows, "HLA1516.1-DM-5.1.5-001", "pitch_disposition", "verified", bundle("ddm_declaration_gating"))
    _assert_clause_residual_frontier(
        payload,
        clause_root="9",
        disposition_key="pitch_disposition",
        expected={"AREA-1516.1-9": "not-applicable", "HLA1516.1-DDM-001": "not-applicable"},
    )
    _assert_clause_disposition_counts(
        _clause_rows(payload, clause_root="9"),
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": 0,
            "not-yet-tested": 0,
            "not-applicable": 2,
            "vendor-divergent": 0,
            "verified": 29,
        },
    )


def test_pitch_clause8_time_management_surface_is_explicit() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")
    rows = _rows_by_requirement(payload)

    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-TM-8_2-enableTimeRegulation",
            "REQ-FED-TM-8_3-timeRegulationEnabled",
            "REQ-RTI-TM-8_5-enableTimeConstrained",
            "REQ-FED-TM-8_6-timeConstrainedEnabled",
            "HLA1516.1-TM-8.2-001",
            "HLA1516.1-TM-8.2-002",
            "HLA1516.1-TM-8.2-003",
            "HLA1516.1-TM-8.5-001",
            "HLA1516.1-TM-8.5-002",
            "HLA1516.1-TM-8.5-003",
        },
        "pitch_disposition",
        "verified",
        bundle("section8_state_services"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-RTI-TM-8_17-queryLogicalTime", "HLA1516.1-TM-8.17-001", "HLA1516.1-TM-8.1.3-001"},
        "pitch_disposition",
        "verified",
        bundle("section8_logical_time_query"),
    )
    assert _clause_summary_counts(
        payload,
        clause_root="8",
        disposition_key="pitch_disposition",
    ) == {
        "not-applicable": 2,
        "total": 61,
        "verified": 41,
        "vendor-divergent": 18,
    }
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-TM-8_4-disableTimeRegulation",
            "REQ-RTI-TM-8_7-disableTimeConstrained",
            "REQ-RTI-TM-8_14-enableAsynchronousDelivery",
            "REQ-RTI-TM-8_15-disableAsynchronousDelivery",
            "HLA1516.1-TM-8.4-001",
            "HLA1516.1-TM-8.7-001",
        },
        "pitch_disposition",
        "verified",
        bundle("section8_state_toggle_services"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-TM-8_8-timeAdvanceRequest",
            "REQ-FED-TM-8_13-timeAdvanceGrant",
            "HLA1516.1-TM-8.8-001",
            "HLA1516.1-TM-8.8-002",
            "HLA1516.1-TM-8.8-003",
        },
        "pitch_disposition",
        "verified",
        bundle("section8_ordering_and_queries"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-TM-8_16-queryGALT",
            "REQ-RTI-TM-8_18-queryLITS",
            "HLA1516.1-TM-8.16-001",
            "HLA1516.1-TM-8.18-001",
            "HLA1516.1-TM-8.1.5-002",
            "HLA1516.1-TM-8.1.5-003",
        },
        "pitch_disposition",
        "verified",
        bundle("section8_time_bound_queries"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-RTI-TM-8_9-timeAdvanceRequestAvailable", "REQ-RTI-TM-8_12-flushQueueRequest", "HLA1516.1-TM-8.12-001"},
        "pitch_disposition",
        "verified",
        bundle("section8_available_and_flush"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-RTI-TM-8_23-changeAttributeOrderType", "REQ-RTI-TM-8_24-changeInteractionOrderType"},
        "pitch_disposition",
        "verified",
        bundle("section8_order_override"),
    )
    _assert_row_disposition_and_refs(rows, "HLA1516.1-TM-8.1.4-001", "pitch_disposition", "verified", bundle("section8_early_timestamp_send"))
    _assert_row_disposition_and_refs(rows, "HLA1516.1-TM-8.1-001", "pitch_disposition", "vendor-divergent", bundle("section8_state_services"))
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "HLA1516.1-TM-8.1-002",
            "HLA1516.1-TM-8.1.1-001",
            "HLA1516.1-TM-8.1.2-004",
            "HLA1516.1-TM-8.1.3-002",
            "HLA1516.1-TM-8.1.3-003",
            "HLA1516.1-TM-8.1.5-001",
            "HLA1516.1-TM-8.1.6-001",
            "HLA1516.1-TM-8.1.7-001",
            "REQ-TIME-ORDER-001",
            "REQ-RTI-TM-8_10-nextMessageRequest",
            "HLA1516.1-TM-8.10-001",
        },
        "pitch_disposition",
        "vendor-divergent",
        bundle("section8_ordering_and_queries"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {"REQ-RTI-TM-8_11-nextMessageRequestAvailable", "REQ-RTI-TM-8_21-retract", "HLA1516.1-TM-8.21-001"},
        "pitch_disposition",
        "vendor-divergent",
        bundle("section8_available_and_retraction"),
    )
    _assert_row_disposition_and_refs(rows, "REQ-FED-TM-8_22-requestRetraction", "pitch_disposition", "vendor-divergent", bundle("section8_request_retraction"))
    _assert_rows_share_disposition_and_refs(
        rows,
        {"HLA1516.1-TM-8.1.2-001", "HLA1516.1-TM-8.1.2-002", "HLA1516.1-TM-8.1.2-003"},
        "pitch_disposition",
        "vendor-divergent",
        bundle("section8_order_override"),
    )
    _assert_rows_share_disposition_and_refs(
        rows,
        {
            "REQ-RTI-TM-8_19-modifyLookahead",
            "REQ-RTI-TM-8_20-queryLookahead",
            "HLA1516.1-TM-8.19-001",
            "HLA1516.1-TM-8.1.4-002",
            "HLA1516.1-TM-8.1.4-003",
        },
        "pitch_disposition",
        "verified",
        bundle("lookahead"),
    )
    _assert_clause_residual_frontier(
        payload,
        clause_root="8",
        disposition_key="pitch_disposition",
        expected={
            "REQ-RTI-TM-8_10-nextMessageRequest": "vendor-divergent",
            "REQ-RTI-TM-8_11-nextMessageRequestAvailable": "vendor-divergent",
            "REQ-RTI-TM-8_21-retract": "vendor-divergent",
            "REQ-FED-TM-8_22-requestRetraction": "vendor-divergent",
            "AREA-1516.1-8": "not-applicable",
            "HLA1516.1-TM-001": "not-applicable",
            "HLA1516.1-TM-8.1-001": "vendor-divergent",
            "HLA1516.1-TM-8.1-002": "vendor-divergent",
            "HLA1516.1-TM-8.1.1-001": "vendor-divergent",
            "HLA1516.1-TM-8.1.2-001": "vendor-divergent",
            "HLA1516.1-TM-8.1.2-002": "vendor-divergent",
            "HLA1516.1-TM-8.1.2-003": "vendor-divergent",
            "HLA1516.1-TM-8.1.2-004": "vendor-divergent",
            "HLA1516.1-TM-8.1.3-002": "vendor-divergent",
            "HLA1516.1-TM-8.1.3-003": "vendor-divergent",
            "HLA1516.1-TM-8.1.5-001": "vendor-divergent",
            "HLA1516.1-TM-8.1.6-001": "vendor-divergent",
            "HLA1516.1-TM-8.1.7-001": "vendor-divergent",
            "HLA1516.1-TM-8.10-001": "vendor-divergent",
            "HLA1516.1-TM-8.21-001": "vendor-divergent",
        },
    )
    _assert_clause_disposition_counts(
        _clause_rows(payload, clause_root="8"),
        disposition_key="pitch_disposition",
        expected_counts={
            "blocked": 0,
            "classification-required": 0,
            "not-yet-tested": 0,
            "not-applicable": 2,
            "vendor-divergent": 18,
            "verified": 41,
        },
    )


def test_discovery_payload_and_text_support_backlog_filters():
    project_root = Path(__file__).resolve().parents[2]
    payload = build_discovery_payload(project_root, backend_filter="certi-native", priority_filter="P1")

    assert payload["catalog"]["summary"]["backend_count"] == 1
    assert all(row["backend_id"] == "certi-native" for row in payload["backlog"]["rows"])
    assert all(row["priority"] == "P1" for row in payload["backlog"]["rows"])

    rendered = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter="certi-native",
        backlog=payload["backlog"],
        priority_filter="P1",
    )
    assert "Vendor discovery backlog:" in rendered
    assert "P1 certi-native" in rendered
    assert "priority=P1" in rendered


def test_vendor_discovery_backlog_writers_emit_generated_artifacts(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    json_path, md_path = write_vendor_discovery_backlog_artifacts(
        project_root,
        json_path=tmp_path / "vendor_discovery_backlog.json",
        markdown_path=tmp_path / "vendor_discovery_backlog.md",
    )

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    md_text = md_path.read_text(encoding="utf-8")
    assert "Vendor Discovery Backlog" in md_text
    assert "certi-native" in md_text
    assert "pitch-jpype" in md_text


def test_requirements_matrix_projects_pitch_dispositions_into_canonical_artifact() -> None:
    payload = _compliance_payload("requirements_matrix_2010.json")

    summary = payload["summary"]
    _assert_min_counts(summary["pitch_runtime_disposition_counts"], {"verified": 1, "blocked": 2})
    _assert_min_counts(summary["pitch_jpype_runtime_disposition_counts"], {"blocked": 2})
    _assert_min_counts(summary["pitch_py4j_runtime_disposition_counts"], {"verified": 1})

    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    blocked_row = rows["HLA1516.1-FM-4.1.5-001"]
    assert blocked_row["pitch_runtime_disposition"] == "blocked"
    assert blocked_row["pitch_jpype_runtime_disposition"] == "blocked"
    assert blocked_row["pitch_py4j_runtime_disposition"] == "blocked"

    verified_row = rows["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]
    assert verified_row["pitch_runtime_disposition"] == "verified"
    assert verified_row["pitch_jpype_runtime_disposition"] == "verified"
    assert verified_row["pitch_py4j_runtime_disposition"] == "verified"
    assert verified_row["python_runtime_disposition"] == "verified"
    assert verified_row["certi_runtime_disposition"] == "verified"

    certi_gap_row = rows["REQ-RTI-FM-4_16-requestFederationSave"]
    assert certi_gap_row["certi_runtime_disposition"] == "verified"

    planning_row = rows["AREA-1516.1-4"]
    assert planning_row["python_runtime_disposition"] == "not-applicable"
    assert planning_row["certi_runtime_disposition"] == "not-applicable"
    assert planning_row["pitch_runtime_disposition"] == "not-applicable"

    assert rows["HLA1516.1-FM-4.3-MOM-001"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.5-001"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.5-002"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.2-002"]["python_runtime_disposition"] == "verified"


def test_python_and_certi_requirement_disposition_artifacts_are_generated() -> None:
    python_payload = _compliance_payload("python_requirement_disposition.json")
    certi_payload = _compliance_payload("certi_requirement_disposition.json")

    assert python_payload["summary"]["backend"] == "python"
    _assert_min_counts(python_payload["summary"]["disposition_counts"], {"verified": 1})
    assert certi_payload["summary"]["backend"] == "certi"
    _assert_min_counts(certi_payload["summary"]["disposition_counts"], {"verified": 1, "classification-required": 1})

    python_rows = {row["requirement_id"] or row["matrix_id"]: row for row in python_payload["rows"]}
    certi_rows = {row["requirement_id"] or row["matrix_id"]: row for row in certi_payload["rows"]}
    assert python_rows["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]["runtime_disposition"] == "verified"
    assert python_rows["HLA1516.1-FM-4.3-MOM-001"]["runtime_disposition"] == "verified"
    assert python_rows["HLA1516.1-FM-4.1.5-001"]["runtime_disposition"] == "verified"
    assert certi_rows["REQ-RTI-FM-4_16-requestFederationSave"]["runtime_disposition"] == "verified"


def test_python_tranche_clauses_4_6_7_8_9_use_shared_harness_evidence_only() -> None:
    payload = _compliance_payload("python_requirement_disposition.json")

    allowed_prefixes_by_clause = {
        "4": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
            "tests/scenarios/test_federation_management_backend_matrix.py::",
        ),
        "6": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_object_management_backend_matrix.py::",
        ),
        "7": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_ownership_management_backend_matrix.py::",
        ),
        "8": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::",
            "tests/time/test_section8_backend_matrix.py::",
            "tests/time/test_lookahead_backend_matrix.py::",
        ),
        "9": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_ddm_backend_matrix.py::",
        ),
    }

    for clause_root, allowed_prefixes in allowed_prefixes_by_clause.items():
        _assert_clause_rows_use_allowed_prefixes(
            payload,
            clause_root=clause_root,
            disposition_key="runtime_disposition",
            dispositions={"verified", "vendor-divergent"},
            allowed_prefixes=allowed_prefixes,
        )


def test_pitch_tranche_clauses_4_6_7_8_9_use_shared_harness_evidence_only() -> None:
    payload = _compliance_payload("pitch_requirement_disposition.json")

    allowed_prefixes_by_clause = {
        "4": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
            "tests/scenarios/test_federation_management_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
        ),
        "6": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_object_management_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
            "packages/hla2010-rti-pitch-common/docs/evidence/",
        ),
        "7": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_ownership_management_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
            "packages/hla2010-rti-pitch-common/docs/evidence/",
        ),
        "8": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::",
            "tests/time/test_section8_backend_matrix.py::",
            "tests/time/test_lookahead_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
            "packages/hla2010-rti-pitch-common/docs/evidence/",
        ),
        "9": (
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/",
            "tests/scenarios/test_ddm_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
        ),
    }

    for clause_root, allowed_prefixes in allowed_prefixes_by_clause.items():
        _assert_clause_rows_use_allowed_prefixes(
            payload,
            clause_root=clause_root,
            disposition_key="pitch_disposition",
            dispositions={"verified", "vendor-divergent"},
            allowed_prefixes=allowed_prefixes,
        )


def test_python_tranche_clause_summaries_and_reclassified_rows_are_generated() -> None:
    payload = _compliance_payload("python_requirement_disposition.json")

    assert _clause_summary_counts(payload, clause_root="4", disposition_key="runtime_disposition")["total"] == 281
    assert _clause_summary_counts(payload, clause_root="6", disposition_key="runtime_disposition")["total"] == 110
    assert _clause_summary_counts(payload, clause_root="7", disposition_key="runtime_disposition")["total"] == 39
    assert _clause_summary_counts(payload, clause_root="8", disposition_key="runtime_disposition")["total"] == 61
    assert _clause_summary_counts(payload, clause_root="9", disposition_key="runtime_disposition")["total"] == 31

    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    for requirement_id, harness_ref, backend_ref in (
        (
            "HLA1516.1-FM-4.1-005",
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_multi_participation_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix",
        ),
        (
            "HLA1516.1-FM-4.1-006",
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_multi_participation_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix",
        ),
        (
            "HLA1516.1-FM-4.1.4.1-002",
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_integrity_negative_matrix",
        ),
        (
            "HLA1516.1-TM-8.1.2-003",
            "packages/hla2010-verification-harness/src/hla2010_verification_harness/section8_matrix.py::run_section8_order_override_case",
            "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services",
        ),
    ):
        row = rows[requirement_id]
        assert row["runtime_disposition"] == "verified"
        assert harness_ref in row["evidence_refs"]
        assert backend_ref in row["evidence_refs"]
