from __future__ import annotations

import pytest
from hla.backends.certi.certi.runtime import coerce_time_scalar
from hla.rti1516e.exceptions import RTIinternalError


class _CustomTime:
    value = 1


def test_certi_rejects_non_builtin_logical_time_scalar() -> None:
    with pytest.raises(RTIinternalError, match="only supports HLAinteger64Time and HLAfloat64Time"):
        coerce_time_scalar(_CustomTime())
