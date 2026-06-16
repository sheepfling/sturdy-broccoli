"""Readable source references for the HLA 1516.1-2010 Python work.

This module keeps the Java and C++ source locations in ordinary Python strings
so the clean spec layer can surface them directly in docstrings.
"""
from __future__ import annotations

from functools import lru_cache

from .raw_api import API_METADATA

_LANGUAGE_LABELS = {
    "cpp": "C++",
    "java": "Java",
}


@lru_cache(maxsize=None)
def method_source_summary(method_name: str) -> str | None:
    """Return a human-readable summary of Java and C++ source locations."""

    entries: list[str] = []
    seen: set[str] = set()
    for class_name in ("RTIambassador", "FederateAmbassador"):
        for item in API_METADATA[class_name].get(method_name, ()):
            language = _LANGUAGE_LABELS.get(item.get("language", ""), item.get("language", "source"))
            source_file = item.get("source_file")
            source_line = item.get("source_line")
            if not source_file or source_line is None:
                continue
            label = f"{language}: {source_file}:{source_line}"
            if label not in seen:
                seen.add(label)
                entries.append(label)
    return "; ".join(entries) if entries else None
