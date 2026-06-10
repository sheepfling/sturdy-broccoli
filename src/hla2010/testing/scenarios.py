"""Compatibility scenario aggregator for repo-internal tests and scripts."""

from __future__ import annotations

from hla2010_verification_harness.two_federate_suite_scenarios import (
    run_suite_ddm_scenario,
    run_suite_save_restore_scenario,
)

from hla2010_verification_harness.scenario_basic import run_basic_federate_scenario
from hla2010_verification_harness.scenario_exchange import (
    ExchangeRoundConfig,
    TwoFederateExchangeConfig,
    run_two_federate_exchange_scenario,
)
from hla2010_verification_harness.scenario_ownership import (
    NegotiatedOwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    run_attribute_ownership_scenario,
    run_negotiated_attribute_ownership_scenario,
    run_release_request_ownership_scenario,
)
from hla2010_verification_harness.scenario_sync import SynchronizationScenarioConfig, run_synchronization_scenario

__all__ = [
    "ExchangeRoundConfig",
    "NegotiatedOwnershipScenarioConfig",
    "ReleaseRequestOwnershipScenarioConfig",
    "SynchronizationScenarioConfig",
    "TwoFederateExchangeConfig",
    "run_attribute_ownership_scenario",
    "run_basic_federate_scenario",
    "run_negotiated_attribute_ownership_scenario",
    "run_release_request_ownership_scenario",
    "run_suite_ddm_scenario",
    "run_suite_save_restore_scenario",
    "run_synchronization_scenario",
    "run_two_federate_exchange_scenario",
]
