from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from hla.verification.repo_internal.verification import runtime_observer_server as observer_module
from hla.verification.repo_internal.verification.runtime_observer_fastapi import create_runtime_observer_fastapi_app
from hla.verification.repo_internal.verification.runtime_observer_server import RuntimeObserverControl


def test_runtime_observer_fastapi_exposes_health_schema_and_bounded_control(tmp_path: Path, monkeypatch) -> None:
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
        (scenario_dir / "listener_trace.ndjson").write_text(
            "\n".join(
                [
                    '{"sequence": 1, "kind": "callback", "provider": "siso-runtime", "scenario": "link16-rpr2-integrated-2010-micro-2", "callback": "discoverObjectInstance", "entity_name": "Link16Radio-1", "entity_handle_text": "ObjectInstanceHandle(101)", "class_name": "HLAobjectRoot.EmbeddedSystem.RadioTransmitter", "class_handle_text": "ObjectClassHandle(33)", "listener_name": "Link16Federate2", "listener_role": "observer"}',
                    '{"sequence": 2, "kind": "callback", "provider": "siso-runtime", "scenario": "link16-rpr2-integrated-2010-micro-2", "callback": "receiveInteraction", "class_name": "JTIDSMessageRadioSignal", "class_handle_text": "InteractionClassHandle(9)", "values": {"NetNumber": "12"}, "listener_name": "Link16Federate2", "listener_role": "observer"}',
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (scenario_dir / "listener_summary.json").write_text(
            '{"scenario": "link16-rpr2-integrated-2010-micro-2", "statistics": {"phases": 0, "operations": 0, "callbacks": {"discoverObjectInstance": 1, "reflectAttributeValues": 0, "receiveInteraction": 1}}}\n',
            encoding="utf-8",
        )
        (scenario_dir / "listener_report.html").write_text("<html>listener report</html>\n", encoding="utf-8")
        return {"scenario": scenario, "execution_complete": True}

    monkeypatch.setattr(observer_module, "run_siso_runtime_showcase_scenario", fake_run)
    monkeypatch.setattr(observer_module.multiprocessing, "get_context", lambda name: _FakeContext())
    control = RuntimeObserverControl(output_dir=tmp_path, default_backend="python1516e")
    app = create_runtime_observer_fastapi_app(control)
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["service"] == "federation-studio"

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    schemas = openapi.json()["components"]["schemas"]
    assert "NormalizedEventRecord" in schemas
    assert "ObjectInspectorRow" in schemas
    assert "InteractionInspectorRow" in schemas

    schema = client.get("/api/schema")
    assert schema.status_code == 200
    assert "interaction_inspector_fields" in schema.json()

    start = client.post(
        "/api/control/start",
        json={
            "provider": "siso-runtime",
            "scenario": scenario,
            "backend": "python1516e",
            "options": {},
        },
    )
    assert start.status_code == 200
    state = start.json()
    assert state["status"] == "complete"
    assert state["normalized_events"][0]["event_type"] == "object.discovered"
    assert state["inspectors"]["objects"][0]["object_handle_text"] == "ObjectInstanceHandle(101)"

    objects = client.get("/api/inspectors/objects")
    assert objects.status_code == 200
    assert objects.json()["objects"][0]["object_key"] == "ObjectInstanceHandle(101)"

    interactions = client.get("/api/inspectors/interactions")
    assert interactions.status_code == 200
    assert interactions.json()["interactions"][0]["interaction_class"] == "JTIDSMessageRadioSignal"

    events = client.get("/api/events")
    assert events.status_code == 200
    assert events.json()["events"][0]["callback"] == "discoverObjectInstance"

    stop = client.post("/api/control/stop")
    assert stop.status_code == 200
    assert stop.json()["status"] in {"stopped", "complete"}


def test_runtime_observer_fastapi_frontend_and_websocket_surface(tmp_path: Path, monkeypatch) -> None:
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

    def fake_worker(provider: str, scenario: str, output_dir: str, backend: str | None, options: dict[str, object]) -> None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "runtime_observer_trace.ndjson").write_text(
            '{"sequence": 1, "kind": "phase", "provider": "two-federate", "scenario": "workspace-two-federate", "phase": "suite-start"}\n',
            encoding="utf-8",
        )
        (out / "two_federate_suite_summary.json").write_text('{"status": "complete"}\n', encoding="utf-8")

    monkeypatch.setattr(observer_module.multiprocessing, "get_context", lambda name: _FakeContext())
    monkeypatch.setattr(observer_module, "_worker_main", fake_worker)
    control = RuntimeObserverControl(output_dir=tmp_path)
    app = create_runtime_observer_fastapi_app(control)
    client = TestClient(app)

    html = client.get("/")
    assert html.status_code == 200
    assert "Federation Studio" in html.text
    assert "/api/schema" in html.text
    assert "/ws/events" in html.text
    assert "Object Instances" in html.text

    with client.websocket_connect("/ws/events") as websocket:
        control.start(provider="two-federate", scenario="workspace-two-federate", options={"target_radar_steps": 1})
        message = websocket.receive_json()
        assert message["kind"] == "phase"
