"""Compatibility facade for backend-neutral transport codecs."""
from __future__ import annotations

from hla.transports.common.transport_codecs import (
    decode_bytes,
    decode_handle_set,
    decode_handle_value_map,
    decode_order,
    encode_bytes,
    federate_handle_set_spec,
    handle_set_spec,
    handle_value_map_spec,
)

__all__ = [
    "decode_bytes",
    "decode_handle_set",
    "decode_handle_value_map",
    "decode_order",
    "encode_bytes",
    "federate_handle_set_spec",
    "handle_set_spec",
    "handle_value_map_spec",
]
