from __future__ import annotations

import pytest

from hla2010.time import HLAinteger64Time
from hla2010_rti_backend_common.time_management import TAR, TimeAdvanceRequestState, compute_galt, valid_tso_lower_bound

from tests.requirement_marker_groups import (
    TM_QUERY_GALT_REQUIREMENTS,
    TM_VALID_TSO_LOWER_BOUND_REQUIREMENTS,
)
from tests.time._time_algorithm_support import DummyFederate, federation, regulating_federate, target_federate


@pytest.mark.requirements(*TM_VALID_TSO_LOWER_BOUND_REQUIREMENTS)
def test_valid_tso_lower_bound_requires_time_regulation_and_uses_pending_minimum_base():
    disabled = regulating_federate(current_time=4, lookahead=2)
    disabled.time_regulation_enabled = False
    assert valid_tso_lower_bound(disabled) is None

    active = regulating_federate(current_time=4, lookahead=2, pending=10)
    assert valid_tso_lower_bound(active) == HLAinteger64Time(6)

    active.pending_time_advance = TimeAdvanceRequestState(TAR, HLAinteger64Time(2))
    assert valid_tso_lower_bound(active) == HLAinteger64Time(4)


@pytest.mark.requirements(*TM_QUERY_GALT_REQUIREMENTS)
def test_compute_galt_uses_other_active_regulators_only_and_returns_invalid_when_none_contribute():
    target = target_federate()
    assert compute_galt(federation(("target", target)), target).time_is_valid is False

    self_regulating = regulating_federate(current_time=1, lookahead=1)
    active = regulating_federate(current_time=8, lookahead=2)
    resigned = regulating_federate(current_time=0, lookahead=1)
    resigned.resigned = True
    deleted = regulating_federate(current_time=0, lookahead=1)
    deleted.deleted = True

    result = compute_galt(
        federation(
            ("target", self_regulating),
            ("active", active),
            ("resigned", resigned),
            ("deleted", deleted),
        ),
        self_regulating,
    )

    assert result.time_is_valid is True
    assert result.time == HLAinteger64Time(10)


@pytest.mark.requirements(*TM_QUERY_GALT_REQUIREMENTS)
def test_compute_galt_rejects_negative_lookahead_contribution():
    target = target_federate()
    bad = regulating_federate(current_time=4, lookahead=-1)

    with pytest.raises(ValueError, match="lookahead must be non-negative"):
        compute_galt(federation(("bad", bad), ("target", target)), target)
