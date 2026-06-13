# Generated from specs/hla2010_api.json.
# Do not edit by hand. Run ./tools/spec-api generate.
"""Source-derived metadata surface for HLA IEEE 1516.1-2010.

This module intentionally exposes only the generated overload/source metadata.
Contributor-facing interface reading should start with ``hla2010.spec`` and
``hla2010.runtime_api`` instead of this compatibility metadata module.

"""

from __future__ import annotations

import json
from importlib import resources


def _load_api_metadata() -> dict[str, dict[str, list[dict[str, object]]]]:
    text = resources.files("hla2010").joinpath("resources/api_metadata.json").read_text(encoding="utf-8")
    payload = json.loads(text)
    return payload


API_METADATA = _load_api_metadata()

__all__ = ["API_METADATA"]
