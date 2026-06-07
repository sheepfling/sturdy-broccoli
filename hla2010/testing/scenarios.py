"""Reusable backend-neutral smoke scenarios for HLA RTI adapters."""
from __future__ import annotations

from .scenario_basic import run_basic_federate_scenario
from .scenario_exchange import (
    ExchangeRoundConfig,
    TwoFederateExchangeConfig,
    assert_two_federate_exchange_callback_history,
    run_exchange_round,
    run_two_federate_exchange_scenario,
)
from .scenario_ownership import (
    NegotiatedOwnershipScenarioConfig,
    OwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    probe_negotiated_attribute_ownership_offer,
    run_attribute_ownership_scenario,
    run_confirm_divestiture_negotiated_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_release_request_ownership_scenario,
)
from .scenario_support import (
    DemoFederate,
    drain_callbacks,
    drain_callbacks_pair,
    wait_for_callback,
    wait_for_callback_count,
    wait_for_callback_count_pair,
)
from .scenario_sync import SynchronizationScenarioConfig, run_synchronization_scenario

__all__ = [
    "DemoFederate",
    "ExchangeRoundConfig",
    "NegotiatedOwnershipScenarioConfig",
    "OwnershipScenarioConfig",
    "ReleaseRequestOwnershipScenarioConfig",
    "SynchronizationScenarioConfig",
    "TwoFederateExchangeConfig",
    "assert_two_federate_exchange_callback_history",
    "drain_callbacks",
    "drain_callbacks_pair",
    "probe_negotiated_attribute_ownership_offer",
    "run_attribute_ownership_scenario",
    "run_basic_federate_scenario",
    "run_confirm_divestiture_negotiated_scenario",
    "run_exchange_round",
    "run_negotiated_attribute_ownership_scenario",
    "run_release_request_ownership_scenario",
    "run_synchronization_scenario",
    "run_two_federate_exchange_scenario",
    "wait_for_callback",
    "wait_for_callback_count",
    "wait_for_callback_count_pair",
]
