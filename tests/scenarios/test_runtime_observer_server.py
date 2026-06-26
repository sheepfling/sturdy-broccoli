from __future__ import annotations

import json
from pathlib import Path
from threading import Thread
import time
from urllib.request import urlopen

from hla.verification.repo_internal.verification import runtime_observer_server as observer_module
from hla.verification.repo_internal.verification.runtime_observer_server import (
    RuntimeObserverControl,
    RuntimeObserverSession,
    build_runtime_observer_event_schema,
    build_runtime_observer_catalog,
    _derive_generic_inspectors,
    _derive_link16_plugin,
    _derive_rpr_plugin,
    _derive_target_radar_plugin,
    _normalize_event,
    render_runtime_observer_html,
)


def test_runtime_observer_session_reports_live_state_from_listener_artifacts(tmp_path: Path, monkeypatch) -> None:
    scenario = "link16-rpr2-integrated-2010-micro-2"

    class _FakeProcess:
        def __init__(self, target, args, daemon):
            self._target = target
            self._args = args
            self.daemon = daemon
            self.exitcode = None
            self._alive = False

        def start(self):
            self._alive = True
            try:
                self._target(*self._args)
            except Exception:
                self.exitcode = 1
                raise
            else:
                self.exitcode = 0
            finally:
                self._alive = False

        def is_alive(self):
            return self._alive

        def terminate(self):
            self._alive = False
            self.exitcode = -15

        def join(self, timeout=None):
            return None

    class _FakeContext:
        @staticmethod
        def Process(target, args, daemon):
            return _FakeProcess(target, args, daemon)

    def fake_run(selected_scenario: str, *, backend: str | None = None, listener_output_dir: str | Path | None = None):
        assert selected_scenario == scenario
        assert listener_output_dir is not None
        scenario_dir = Path(listener_output_dir) / scenario
        scenario_dir.mkdir(parents=True, exist_ok=True)
        trace = scenario_dir / "listener_trace.ndjson"
        trace.write_text(
            "\n".join(
                [
                    json.dumps({"sequence": 1, "kind": "phase", "phase": "ready-to-run-synchronized"}),
                    json.dumps({"sequence": 2, "kind": "operation", "operation": "send-interaction", "actor": "Link16Federate1"}),
                    json.dumps({"sequence": 3, "kind": "callback", "callback": "receiveInteraction", "listener_name": "Link16Federate2"}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        summary = scenario_dir / "listener_summary.json"
        summary.write_text(
            json.dumps(
                {
                    "scenario": scenario,
                    "statistics": {
                        "phases": 1,
                        "operations": 1,
                        "callbacks": {
                            "discoverObjectInstance": 0,
                            "reflectAttributeValues": 0,
                            "receiveInteraction": 1,
                        },
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report = scenario_dir / "listener_report.html"
        report.write_text("<html>listener report</html>\n", encoding="utf-8")
        return {"scenario": scenario, "execution_complete": True}

    monkeypatch.setattr(observer_module, "run_siso_runtime_showcase_scenario", fake_run)
    monkeypatch.setattr(observer_module.multiprocessing, "get_context", lambda name: _FakeContext())
    session = RuntimeObserverSession(provider="siso-runtime", scenario=scenario, output_dir=tmp_path, backend="python1516e")
    session.start()

    state = session.live_state()
    assert state["status"] == "complete"
    assert state["summary_ready"] is True
    assert state["listener_report_ready"] is True
    assert state["live_metrics"]["event_count"] == 3
    assert state["live_metrics"]["last_phase"] == "ready-to-run-synchronized"
    assert state["live_metrics"]["callbacks"]["receiveInteraction"] == 1
    assert state["participant_profiles"][0]["federate"] == "Link16Federate1"


def test_runtime_observer_http_schema_and_state_support_non_ui_subscriber(tmp_path: Path, monkeypatch) -> None:
    scenario = "link16-rpr2-integrated-2010-micro-2"
    captured: dict[str, object] = {}

    class _FakeProcess:
        def __init__(self, target, args, daemon):
            self._target = target
            self._args = args
            self.daemon = daemon
            self.exitcode = None
            self._alive = False

        def start(self):
            self._alive = True
            try:
                self._target(*self._args)
            except Exception:
                self.exitcode = 1
                raise
            else:
                self.exitcode = 0
            finally:
                self._alive = False

        def is_alive(self):
            return self._alive

        def terminate(self):
            self._alive = False
            self.exitcode = -15

        def join(self, timeout=None):
            return None

    class _FakeContext:
        @staticmethod
        def Process(target, args, daemon):
            return _FakeProcess(target, args, daemon)

    class _CapturingServer(observer_module.ThreadingHTTPServer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            captured["server"] = self

    def fake_run(selected_scenario: str, *, backend: str | None = None, listener_output_dir: str | Path | None = None):
        assert selected_scenario == scenario
        assert listener_output_dir is not None
        scenario_dir = Path(listener_output_dir) / scenario
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "listener_trace.ndjson").write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "sequence": 1,
                            "kind": "callback",
                            "provider": "siso-runtime",
                            "scenario": scenario,
                            "callback": "discoverObjectInstance",
                            "entity_name": "Link16Radio-1",
                            "entity_handle_text": "ObjectInstanceHandle(101)",
                            "class_name": "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
                            "class_handle_text": "ObjectClassHandle(33)",
                            "listener_name": "Link16Federate2",
                            "listener_role": "observer",
                        }
                    ),
                    json.dumps(
                        {
                            "sequence": 2,
                            "kind": "callback",
                            "provider": "siso-runtime",
                            "scenario": scenario,
                            "callback": "reflectAttributeValues",
                            "entity_handle_text": "ObjectInstanceHandle(101)",
                            "class_handle_text": "ObjectClassHandle(33)",
                            "values": {"Frequency": "969001000"},
                            "listener_name": "Link16Federate2",
                            "listener_role": "observer",
                        }
                    ),
                    json.dumps(
                        {
                            "sequence": 3,
                            "kind": "callback",
                            "provider": "siso-runtime",
                            "scenario": scenario,
                            "callback": "receiveInteraction",
                            "class_name": "JTIDSMessageRadioSignal",
                            "class_handle_text": "InteractionClassHandle(9)",
                            "values": {"NetNumber": "12"},
                            "listener_name": "Link16Federate2",
                            "listener_role": "observer",
                        }
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (scenario_dir / "listener_summary.json").write_text(
            json.dumps(
                {
                    "scenario": scenario,
                    "statistics": {
                        "phases": 0,
                        "operations": 0,
                        "callbacks": {
                            "discoverObjectInstance": 1,
                            "reflectAttributeValues": 1,
                            "receiveInteraction": 1,
                        },
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (scenario_dir / "listener_report.html").write_text("<html>listener report</html>\n", encoding="utf-8")
        return {"scenario": scenario, "execution_complete": True}

    monkeypatch.setattr(observer_module, "run_siso_runtime_showcase_scenario", fake_run)
    monkeypatch.setattr(observer_module.multiprocessing, "get_context", lambda name: _FakeContext())
    monkeypatch.setattr(observer_module, "ThreadingHTTPServer", _CapturingServer)

    thread = Thread(
        target=observer_module.serve_runtime_observer,
        kwargs={
            "provider": "siso-runtime",
            "scenario": scenario,
            "output_dir": tmp_path,
            "host": "127.0.0.1",
            "port": 0,
            "backend": "python1516e",
        },
        daemon=True,
    )
    thread.start()
    try:
        deadline = time.time() + 5.0
        while "server" not in captured and time.time() < deadline:
            time.sleep(0.05)
        server = captured["server"]
        base_url = f"http://127.0.0.1:{server.server_port}"
        with urlopen(f"{base_url}/api/schema", timeout=5) as response:
            schema = json.loads(response.read().decode("utf-8"))
        with urlopen(f"{base_url}/api/state", timeout=5) as response:
            state = json.loads(response.read().decode("utf-8"))

        assert schema["schema_version"] == state["schema_version"]
        assert "object_key" in schema["normalized_event_properties"]
        assert state["inspectors"]["objects"][0]["object_key"] == "ObjectInstanceHandle(101)"
        assert state["inspectors"]["objects"][0]["class_handle_text"] == "ObjectClassHandle(33)"
        assert state["inspectors"]["interactions"][0]["interaction_class"] == "JTIDSMessageRadioSignal"
        assert state["normalized_events"][0]["event_type"] == "object.discovered"
        assert state["normalized_events"][1]["event_type"] == "object.updated"
    finally:
        server = captured.get("server")
        if server is not None:
            server.shutdown()
            server.server_close()
        thread.join(timeout=5)


def test_runtime_observer_catalog_and_control_support_multiple_providers(tmp_path: Path) -> None:
    catalog = build_runtime_observer_catalog()

    providers = {row["provider"] for row in catalog["providers"]}
    assert {"siso-runtime", "two-federate", "target-radar"} <= providers
    by_provider = {row["provider"]: row for row in catalog["providers"]}
    assert by_provider["two-federate"]["scenarios"][0]["default_options"]["target_radar_steps"] == 4

    control = RuntimeObserverControl(output_dir=tmp_path)
    state = control.state()
    assert state["status"] == "idle"
    assert "catalog" in state


def test_runtime_observer_normalizes_generic_event_types_and_plugins() -> None:
    raw_events = [
        {
            "sequence": 1,
            "kind": "callback",
            "provider": "siso-runtime",
            "scenario": "link16-rpr2-integrated-2010-micro-2",
            "callback": "discoverObjectInstance",
            "entity_name": "Link16Radio-1",
            "entity_handle_text": "ObjectInstanceHandle(101)",
            "class_name": "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
            "class_handle_text": "ObjectClassHandle(33)",
            "listener_name": "Link16Federate2",
        },
        {
            "sequence": 2,
            "kind": "callback",
            "provider": "siso-runtime",
            "scenario": "link16-rpr2-integrated-2010-micro-2",
            "callback": "reflectAttributeValues",
            "entity_handle_text": "ObjectInstanceHandle(101)",
            "values": {"Frequency": "969001000"},
            "tag": "tag-1",
            "listener_name": "Link16Federate2",
        },
        {
            "sequence": 3,
            "kind": "callback",
            "provider": "siso-runtime",
            "scenario": "link16-rpr2-integrated-2010-micro-2",
            "callback": "receiveInteraction",
            "class_name": "JTIDSMessageRadioSignal",
            "class_handle_text": "InteractionClassHandle(9)",
            "values": {"NetNumber": "12"},
            "listener_name": "Link16Federate2",
        },
    ]
    normalized = [_normalize_event(event) for event in raw_events]

    assert normalized[0]["event_type"] == "object.discovered"
    assert normalized[0]["object_key"] == "ObjectInstanceHandle(101)"
    assert normalized[1]["event_type"] == "object.updated"
    assert normalized[1]["object_key"] == "ObjectInstanceHandle(101)"
    assert normalized[2]["event_type"] == "interaction.received"
    assert normalized[2]["family"] == "link16"

    inspectors = _derive_generic_inspectors({}, normalized)
    assert inspectors["objects"][0]["object_name"] == "Link16Radio-1"
    assert inspectors["objects"][0]["object_handle_text"] == "ObjectInstanceHandle(101)"
    assert inspectors["objects"][0]["class_handle_text"] == "ObjectClassHandle(33)"
    assert inspectors["objects"][0]["aliases"] == ["Link16Radio-1"]
    assert inspectors["interactions"][0]["interaction_class"] == "JTIDSMessageRadioSignal"
    assert inspectors["interactions"][0]["class_handle_text"] == "InteractionClassHandle(9)"

    link16_plugin = _derive_link16_plugin({"family": "link16"}, inspectors)
    assert link16_plugin is not None
    assert link16_plugin["jtids_count"] == 1

    rpr_plugin = _derive_rpr_plugin(
        {"family": "rpr"},
        {
            "objects": [{"object_name": "Bridge-Alpha", "class_name": "BridgeObject"}],
            "interactions": [
                {"interaction_class": "WeaponFire", "source": "RprFederate1", "parameters": {"TargetObjectIdentifier": "bridge-alpha"}},
                {"interaction_class": "MunitionDetonation", "source": "RprFederate1", "parameters": {"TargetObjectIdentifier": "bridge-alpha"}},
            ],
        },
    )
    assert rpr_plugin is not None
    assert rpr_plugin["weapon_fire_count"] == 1
    assert rpr_plugin["detonation_count"] == 1

    target_radar_plugin = _derive_target_radar_plugin(
        {"provider": "target-radar", "scenario": "target-radar-proof", "final_summary": None},
        [{"interaction_class": "track", "parameters": {"track_id": "TRK-001", "target_name": "Target-1"}}],
    )
    assert target_radar_plugin is not None
    assert target_radar_plugin["track_report_count"] == 1


def test_runtime_observer_schema_matches_checked_in_reference() -> None:
    schema = build_runtime_observer_event_schema()
    schema_path = Path("docs/reference/runtime_observer_event_schema.json")
    checked_in = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema == checked_in
    assert schema["schema_version"] == "runtime-observer-event-schema-v1"
    assert "object.updated" in schema["event_types"]


def test_runtime_observer_html_includes_live_endpoints() -> None:
    control = RuntimeObserverControl(output_dir=Path("runtime-observer-test"))
    html = render_runtime_observer_html(
        control,
        {
            "provider": "siso-runtime",
            "scenario": "rpr-runtime-2025-micro-2",
            "story": "Bridge owner and observer.",
            "runtime_edition": "2025",
            "family": "rpr",
            "topology": "micro-2",
            "backend": "python1516_2025",
            "fom_modules": ["RPR.xml"],
            "status": "running",
            "participant_profiles": [
                {
                    "federate": "RprFederate1",
                    "role": "bridge-owner-shooter",
                    "posture": "bridge-owner + shooter",
                    "publishes": ["BridgeObject", "WeaponFire"],
                    "subscribes": [],
                }
            ],
            "inspectors": {
                "objects": [{"object_name": "Bridge-Alpha", "class_name": "BridgeObject"}],
                "interactions": [{"interaction_class": "WeaponFire", "parameters": {"TargetObjectIdentifier": "bridge-alpha"}}],
            },
            "plugin_panels": [{"title": "Target/Radar Panel", "track_report_count": 1}],
            "normalized_events": [
                {"sequence": 1, "event_type": "object.discovered", "family": "rpr", "class_name": "BridgeObject"},
                {"sequence": 2, "event_type": "interaction.received", "family": "rpr", "interaction_class": "WeaponFire"},
            ],
            "schema_version": "runtime-observer-event-schema-v1",
        }
    )

    assert "/api/state" in html
    assert "/api/schema" in html
    assert "/api/control/start" in html
    assert "/api/control/stop" in html
    assert "/events" in html
    assert "target_radar_steps" in html
    assert "Federation Subscriber" in html
    assert "family-filter" in html
    assert "class-filter" in html
    assert "event-type-filter" in html
    assert "Object Inspector" in html
    assert "Interaction Inspector" in html
    assert "Scenario Plugin" in html
    assert "renderPluginPanel" in html
    assert "Schema:" in html
    assert "RprFederate1" in html
    assert "BridgeObject" in html
