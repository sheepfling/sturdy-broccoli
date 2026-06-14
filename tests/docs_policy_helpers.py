from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from conftest import load_json_fixture
from tests.doc_test_helpers import ROOT, doc_relative_reference


@dataclass(frozen=True)
class DocsPolicyManifest:
    key_public_docs: tuple[str, ...]
    banned_primary_refs: tuple[str, ...]
    expected_headings: dict[str, tuple[str, ...]]
    expected_paths: dict[str, tuple[str, ...]]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> DocsPolicyManifest:
        return cls(
            key_public_docs=tuple(str(path) for path in payload["key_public_docs"]),
            banned_primary_refs=tuple(str(item) for item in payload["banned_primary_refs"]),
            expected_headings={
                str(path): tuple(str(heading) for heading in headings)
                for path, headings in payload["expected_headings"].items()
            },
            expected_paths={
                str(path): tuple(str(ref) for ref in refs)
                for path, refs in payload["expected_paths"].items()
            },
        )


_MANIFEST = DocsPolicyManifest.from_mapping(load_json_fixture("docs_policy_manifest.json"))

KEY_PUBLIC_DOCS = tuple(ROOT / path for path in _MANIFEST.key_public_docs)

BANNED_PRIMARY_REFS = _MANIFEST.banned_primary_refs

EXPECTED_HEADINGS = {
    ROOT / path: headings
    for path, headings in _MANIFEST.expected_headings.items()
}

EXPECTED_PATHS = {
    ROOT / path: tuple(ROOT / ref for ref in refs)
    for path, refs in _MANIFEST.expected_paths.items()
}


__all__ = (
    "BANNED_PRIMARY_REFS",
    "EXPECTED_HEADINGS",
    "EXPECTED_PATHS",
    "KEY_PUBLIC_DOCS",
    "ROOT",
    "doc_relative_reference",
)
