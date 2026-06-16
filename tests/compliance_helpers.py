from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

IEEE_1516_1_2010 = "IEEE 1516.1-2010"
IEEE_1516_2_2010 = "IEEE 1516.2-2010"


def compliance_document_key(value: object) -> str:
    text = str(value or "").strip()
    if text in {IEEE_1516_1_2010, f"{IEEE_1516_1_2010} (2010 edition)"}:
        return IEEE_1516_1_2010
    if text in {IEEE_1516_2_2010, f"{IEEE_1516_2_2010} (2010 edition)"}:
        return IEEE_1516_2_2010
    return text


def compliance_section_key(value: object) -> str:
    text = str(value or "").strip()
    text = text.replace(f"{IEEE_1516_1_2010} (2010 edition) §", f"{IEEE_1516_1_2010} §")
    text = text.replace(f"{IEEE_1516_2_2010} (2010 edition) §", f"{IEEE_1516_2_2010} §")
    text = text.replace(f"{IEEE_1516_1_2010} (2010 edition) unknown", f"{IEEE_1516_1_2010} unknown")
    text = text.replace(f"{IEEE_1516_2_2010} (2010 edition) unknown", f"{IEEE_1516_2_2010} unknown")
    return text


def is_1516_1_2010_row(row: Mapping[str, Any]) -> bool:
    return compliance_document_key(row.get("document")) == IEEE_1516_1_2010


def is_1516_2_2010_row(row: Mapping[str, Any]) -> bool:
    return compliance_document_key(row.get("document")) == IEEE_1516_2_2010


def is_1516_1_2010_clause(row: Mapping[str, Any], clause_root: str) -> bool:
    return is_1516_1_2010_row(row) and str(row.get("clause_root")) == clause_root


def is_1516_2_2010_clause(row: Mapping[str, Any], clause_root: str) -> bool:
    return is_1516_2_2010_row(row) and str(row.get("clause_root")) == clause_root


def clause_summary_counts(summary: Mapping[str, Any], document: str, clause_root: str) -> Mapping[str, int]:
    target = compliance_section_key(f"{document} §{clause_root}")
    for section_ref, counts in summary.items():
        if compliance_section_key(section_ref) == target:
            return counts
    raise KeyError(target)


def has_section_ref(section_refs: Iterable[object], document: str, clause_ref: str) -> bool:
    target = compliance_section_key(f"{document} §{clause_ref}")
    return any(compliance_section_key(ref) == target for ref in section_refs)
