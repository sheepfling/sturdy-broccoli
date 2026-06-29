"""Source-derived HLA API metadata helpers.

This module exposes the generated Java/C++ method metadata without pulling in
the legacy ``raw_api`` abstract ambassador scaffolding.
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


def load_api_metadata() -> dict[str, dict[str, list[dict[str, Any]]]]:
    metadata = resources.files("hla.rti1516e").joinpath("api_metadata.json").read_text(encoding="utf-8")
    payload = json.loads(metadata)
    payload.setdefault("RTIambassador", {}).setdefault("getRegionHandleFactory", [])
    payload.setdefault("RTIambassador", {}).setdefault("getMessageRetractionHandleFactory", [])
    return payload


API_METADATA = load_api_metadata()


__all__ = ["API_METADATA", "load_api_metadata"]
