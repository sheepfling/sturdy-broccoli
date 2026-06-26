from __future__ import annotations

from dataclasses import dataclass

from hla.foms.target_radar._internal import run_target_radar_scenario
from hla.verification.two_federate_suite_pairs import SuiteRecordingFederateAmbassador
from hla.verification.two_federate_suite_runner import TwoFederateSuiteHooks, run_two_federate_suite_for_pair_factory


def test_target_radar_scenario_emits_live_events() -> None:
    seen: list[dict[str, object]] = []

    result = run_target_radar_scenario(steps=1, event_sink=seen.append)

    assert result.track_reports
    assert any(event.get("kind") == "phase" and event.get("phase") == "step-start" for event in seen)
    assert any(event.get("actor") == "target" and event.get("event") == "step" for event in seen)
    assert any(event.get("actor") == "radar" and event.get("event") == "query_rcs" for event in seen)
    assert any(event.get("actor") == "radar" and event.get("event") == "track" for event in seen)


def test_two_federate_suite_runner_emits_live_callback_and_phase_events() -> None:
    seen: list[dict[str, object]] = []

    @dataclass
    class _Config:
        federation_name: str
        fom_modules: tuple[str, ...] = ("TargetRadarFOMmodule.xml",)

    class _DummyRTI:
        def resign_federation_execution(self, action):
            return None

        def destroy_federation_execution(self, federation_name):
            return None

        def disconnect(self):
            return None

    def pair_factory(scenario, timeline):
        return (
            _DummyRTI(),
            _DummyRTI(),
            SuiteRecordingFederateAmbassador(profile="python", scenario=scenario, role="left", timeline=timeline),
            SuiteRecordingFederateAmbassador(profile="python", scenario=scenario, role="right", timeline=timeline),
        )

    def _record(left_federate, right_federate, callback_name: str):
        left_federate.record_callback(callback_name, "left")
        right_federate.record_callback(callback_name, "right")
        return {"status": "ok"}

    hooks = TwoFederateSuiteHooks(
        exchange_config_factory=lambda: _Config("exchange"),
        sync_config_factory=lambda: _Config("sync"),
        ownership_config_factory=lambda: _Config("ownership"),
        negotiated_config_factory=lambda: _Config("negotiated"),
        save_restore_config_factory=lambda: {"federation_name": "save-restore"},
        ddm_config_factory=lambda: {"federation_name": "ddm"},
        future_exclusion_config_factory=lambda: _Config("future"),
        restore_state_config_factory=lambda: _Config("restore"),
        run_exchange_scenario=lambda pub, sub, config, publisher_federate, subscriber_federate: _record(
            publisher_federate, subscriber_federate, "receiveInteraction"
        ),
        assert_exchange_history=lambda *args, **kwargs: {"history": "ok"},
        run_sync_scenario=lambda leader, wing, config, leader_federate, wing_federate: _record(
            leader_federate, wing_federate, "federationSynchronized"
        ),
        run_ownership_scenario=lambda owner, acquirer, config, owner_federate, acquirer_federate: _record(
            owner_federate, acquirer_federate, "attributeOwnershipAcquisitionNotification"
        ),
        run_negotiated_scenario=lambda owner, acquirer, config, owner_federate, acquirer_federate: _record(
            owner_federate, acquirer_federate, "requestAttributeOwnershipRelease"
        ),
        run_save_restore_scenario=lambda left, right, config, left_federate, right_federate: _record(
            left_federate, right_federate, "federationSaved"
        ),
        run_ddm_scenario=lambda sender, receiver, config, sender_federate, receiver_federate: _record(
            sender_federate, receiver_federate, "receiveInteraction"
        ),
        run_future_exclusion_scenario=lambda slow, radar, config, slow_federate, radar_federate: _record(
            slow_federate, radar_federate, "timeAdvanceGrant"
        ),
        run_restore_state_scenario=lambda truth, radar, config, truth_federate, radar_federate: _record(
            truth_federate, radar_federate, "federationRestored"
        ),
        extension_name="target_radar",
        extension_summary_factory=lambda target_radar_steps, event_sink=None: {
            "scenario_row": {
                "scenario": "target_radar",
                "backend": "python/1516e",
                "callbacks": 1,
                "artifacts": ["event log"],
                "key_outcome": "1 track report",
            },
            "result": {"track_reports": 1},
            "fom_path": "TargetRadarFOMmodule.xml",
        },
    )

    summary = run_two_federate_suite_for_pair_factory(pair_factory, hooks=hooks, extension_steps=2, event_sink=seen.append)

    assert summary["scenario_rows"]
    assert any(event["kind"] == "phase" and event["scenario"] == "exchange_time" and event["phase"] == "scenario-start" for event in seen)
    assert any(event["kind"] == "callback" and event["provider"] == "two-federate" and event["callback"] == "receiveInteraction" for event in seen)
    assert any(event["kind"] == "phase" and event["scenario"] == "target_radar" and event["phase"] == "scenario-complete" for event in seen)
