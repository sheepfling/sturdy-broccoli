from __future__ import annotations

import importlib.util
from pathlib import Path

_HELPER_PATH = Path(__file__).with_name("evidence_bundles.py")
_HELPER_SPEC = importlib.util.spec_from_file_location("verification_evidence_bundles", _HELPER_PATH)
assert _HELPER_SPEC is not None
assert _HELPER_SPEC.loader is not None
_HELPER = importlib.util.module_from_spec(_HELPER_SPEC)
_HELPER_SPEC.loader.exec_module(_HELPER)

PITCH_BUNDLES = _HELPER.PITCH_BUNDLES
ROOT = _HELPER.ROOT


def _anchor_exists(ref: str) -> bool:
    file_ref, _, anchor = ref.partition("::")
    path = ROOT / file_ref
    if not path.exists():
        return False
    if not anchor:
        return True
    text = path.read_text(encoding="utf-8")
    normalized_anchor = anchor.split("[", 1)[0]
    return f"def {normalized_anchor}(" in text or normalized_anchor in text


def test_pitch_evidence_bundles_resolve_to_real_paths_and_anchors() -> None:
    assert PITCH_BUNDLES
    for bundle_name, refs in PITCH_BUNDLES.items():
        assert refs, bundle_name
        for ref in refs:
            assert _anchor_exists(ref), f"{bundle_name}: {ref}"
