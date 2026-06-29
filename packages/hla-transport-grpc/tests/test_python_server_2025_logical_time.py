from __future__ import annotations

import pytest
from hla.transports.grpc.fedpro2025 import datatypes_2025_pb2
from hla.transports.grpc.python_server_2025 import _logical_time_value


def test_python_server_2025_rejects_unsupported_logical_time_type() -> None:
    value = datatypes_2025_pb2.LogicalTime(data=b"CustomTime:123")

    with pytest.raises(ValueError, match="Unsupported logical time type"):
        _logical_time_value(value)
