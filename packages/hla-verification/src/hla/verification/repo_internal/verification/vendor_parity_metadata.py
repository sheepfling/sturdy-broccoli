"""Repo-internal vendor parity metadata loaders and row augmentation."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def load_backend_conformance_vendor_rows(project_root: str | Path) -> dict[str, list[dict[str, Any]]]:
    matrix_path = Path(project_root).resolve() / "docs" / "backend_conformance_matrix.md"
    if not matrix_path.exists():
        return {}

    rows_by_clause: dict[str, list[dict[str, Any]]] = {}
    for raw_line in matrix_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 7:
            continue
        if parts[0] in {"Clause", "---"}:
            continue
        clause = parts[0]
        if not re.fullmatch(r"\d+(?:\.\d+)*", clause):
            continue
        rows_by_clause.setdefault(clause, []).append(
            {
                "vendor_row_title": parts[1],
                "python_runtime_status": parts[2],
                "certi_runtime_status": parts[3],
                "pitch_runtime_status": parts[4],
                "vendor_evidence_refs": _extract_markdown_link_targets(parts[5]),
                "vendor_notes": "|".join(parts[6:]).strip(),
                "vendor_source": "docs/backend_conformance_matrix.md",
            }
        )
    return rows_by_clause


def load_operational_vendor_profiles(project_root: str | Path) -> dict[str, list[dict[str, Any]]]:
    matrix_path = Path(project_root).resolve() / "docs" / "rti_options_and_test_matrix.md"
    if not matrix_path.exists():
        return {}

    rows: list[dict[str, Any]] = []
    in_table = False
    for raw_line in matrix_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Backend family | Bridge model | Transport | Exchange | Timed | Sync | Ownership | Negotiated Ownership | Real runtime |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) != 9:
            continue
        if parts[0] == "---":
            continue
        rows.append(
            {
                "backend_family": parts[0],
                "bridge_model": parts[1],
                "transport": parts[2],
                "exchange": parts[3],
                "timed": parts[4],
                "sync": parts[5],
                "ownership": parts[6],
                "negotiated ownership": parts[7],
                "real runtime": parts[8],
            }
        )
    return {"rows": rows, "source": "docs/rti_options_and_test_matrix.md"}


def with_vendor_parity(
    row: dict[str, Any],
    *,
    vendor_rows_by_clause: dict[str, list[dict[str, Any]]],
    operational_vendor_profiles: dict[str, Any] | None = None,
) -> dict[str, Any]:
    augmented = dict(row)
    clause = _extract_numeric_clause(augmented.get("section_ref"))
    vendor = _select_vendor_row(augmented, vendor_rows_by_clause) if _is_1516_1_2010_document(augmented.get("document")) else {}
    augmented.setdefault("python_runtime_status", vendor.get("python_runtime_status", ""))
    augmented.setdefault("certi_runtime_status", vendor.get("certi_runtime_status", ""))
    augmented.setdefault("pitch_runtime_status", vendor.get("pitch_runtime_status", ""))
    augmented.setdefault("vendor_evidence_refs", list(vendor.get("vendor_evidence_refs", ())))
    augmented.setdefault("vendor_notes", vendor.get("vendor_notes", ""))
    augmented.setdefault("vendor_source", vendor.get("vendor_source", ""))
    return _operational_vendor_note(
        augmented,
        profile_rows=operational_vendor_profiles or {},
    )


def _extract_markdown_link_targets(value: Any) -> list[str]:
    text = str(value or "")
    return [match.strip() for match in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text) if match.strip()]


def _is_1516_1_2010_document(value: Any) -> bool:
    return str(value) in {"IEEE 1516.1-2010", "IEEE 1516.1-2010 (2010 edition)"}


def _extract_numeric_clause(section_ref: Any) -> str:
    match = re.search(r"§\s*(\d+(?:\.\d+)*)", str(section_ref or ""))
    return match.group(1) if match else ""


def _normalize_title_tokens(value: Any) -> set[str]:
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower())
    return {token for token in text.split() if token}


def _select_vendor_row(
    row: dict[str, Any],
    vendor_rows_by_clause: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    clause = _extract_numeric_clause(row.get("section_ref"))
    candidates = vendor_rows_by_clause.get(clause, [])
    if not candidates:
        return {}
    if len(candidates) == 1:
        return dict(candidates[0])

    target_title = str(row.get("title", ""))
    target_tokens = _normalize_title_tokens(target_title)

    def _score(candidate: dict[str, Any]) -> tuple[int, int, int]:
        candidate_title = str(candidate.get("vendor_row_title", ""))
        candidate_tokens = _normalize_title_tokens(candidate_title)
        overlap = len(target_tokens & candidate_tokens)
        substring_bonus = int(candidate_title.lower() in target_title.lower() or target_title.lower() in candidate_title.lower())
        return (overlap, substring_bonus, len(candidate_tokens))

    return dict(max(candidates, key=_score))


def _operational_capability_bucket(row: dict[str, Any]) -> str:
    if not _is_1516_1_2010_document(row.get("document")):
        return ""
    clause = _extract_numeric_clause(row.get("section_ref"))
    root = clause.split(".", 1)[0] if clause else ""
    title = str(row.get("title", "")).lower()
    if root == "8":
        return "Timed"
    if root == "6":
        return "Exchange"
    if root == "7":
        negotiated_tokens = ("negotiated", "acquisition", "divestiture", "release", "cancel", "assumption")
        if any(token in title for token in negotiated_tokens):
            return "Negotiated Ownership"
        return "Ownership"
    if root == "4" and clause in {"4.11", "4.12", "4.13", "4.14", "4.15"}:
        return "Sync"
    return ""


def _operational_vendor_note(
    row: dict[str, Any],
    *,
    profile_rows: dict[str, Any],
) -> dict[str, Any]:
    augmented = dict(row)
    bucket = _operational_capability_bucket(augmented)
    augmented.setdefault("vendor_profile_bucket", bucket)
    if not bucket or not profile_rows:
        augmented.setdefault("vendor_profile_refs", [])
        augmented.setdefault("vendor_profile_notes", "")
        augmented.setdefault("vendor_profile_source", "")
        return augmented

    matching: list[str] = []
    for profile in profile_rows.get("rows", []):
        value = profile.get(bucket.lower(), "")
        matching.append(
            f"{profile['backend_family']} ({profile['bridge_model']}, {profile['transport']}): {value}"
        )
    augmented.setdefault("vendor_profile_refs", [profile_rows.get("source", "")] if profile_rows.get("source") else [])
    augmented.setdefault("vendor_profile_notes", "; ".join(matching))
    augmented.setdefault("vendor_profile_source", profile_rows.get("source", ""))
    return augmented


__all__ = [
    "load_backend_conformance_vendor_rows",
    "load_operational_vendor_profiles",
    "with_vendor_parity",
]
