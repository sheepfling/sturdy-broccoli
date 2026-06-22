from __future__ import annotations

from hla.backends.python2025.ownership_runtime import (
    attribute_ownership_acquisition,
    attribute_ownership_acquisition_if_available,
    attribute_ownership_divestiture_if_wanted,
    attribute_ownership_release_denied,
    cancel_attribute_ownership_acquisition,
    cancel_negotiated_attribute_ownership_divestiture,
    confirm_divestiture,
    is_attribute_owned_by_federate,
    negotiated_attribute_ownership_divestiture,
    query_attribute_ownership,
    unconditional_attribute_ownership_divestiture,
)

__all__ = [
    "attribute_ownership_acquisition",
    "attribute_ownership_acquisition_if_available",
    "attribute_ownership_divestiture_if_wanted",
    "attribute_ownership_release_denied",
    "cancel_attribute_ownership_acquisition",
    "cancel_negotiated_attribute_ownership_divestiture",
    "confirm_divestiture",
    "is_attribute_owned_by_federate",
    "negotiated_attribute_ownership_divestiture",
    "query_attribute_ownership",
    "unconditional_attribute_ownership_divestiture",
]
