from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from fastapi.testclient import TestClient

from hla.verification.repo_internal.verification import federate_service_fastapi as service_module
from hla.verification.repo_internal.verification.federate_service_fastapi import (
    FederateServiceControl,
    create_federate_service_fastapi_app,
)


def test_federate_service_contract_exposes_canonical_interfaces_and_support() -> None:
    app = create_federate_service_fastapi_app(FederateServiceControl())
    client = TestClient(app)

    landing = client.get("/")
    assert landing.status_code == 200
    assert "RTI Bridge API" in landing.text
    assert "federate-service" in landing.text
    assert "/api/contract" in landing.text
    assert "/api/sessions" in landing.text
    assert "/docs" in landing.text

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["service"] == "federate-service"

    contract = client.get("/api/contract")
    assert contract.status_code == 200
    payload = contract.json()
    assert "RTIambassador" in payload["interfaces"]
    assert "FederateAmbassador" in payload["interfaces"]

    rti = client.get("/api/contract/RTIambassador")
    assert rti.status_code == 200
    assert "connect" in rti.json()["methods"]
    assert "createFederationExecution" in rti.json()["methods"]

    method = client.get("/api/contract/RTIambassador/joinFederationExecution")
    assert method.status_code == 200
    row = method.json()
    assert row["method_name"] == "joinFederationExecution"
    assert row["python_alias"] == "join_federation_execution"
    assert row["support"]["execution_status"] == "supported"
    assert "federateName" in row["support"]["http_argument_names"]

    metadata_only = client.get("/api/contract/RTIambassador/queryGALT")
    assert metadata_only.status_code == 200
    assert metadata_only.json()["support"]["execution_status"] == "metadata-only"


def test_federate_service_session_and_bounded_invoke_flow(monkeypatch) -> None:
    @dataclass(slots=True)
    class _FakeSessionConfig:
        edition: str
        backend: str
        federation_name: str
        federate_name: str
        federate_type: str
        fom_modules: tuple[str, ...]
        logical_time_implementation: str
        transport_kind: str | None = None
        transport_target: str | None = None
        json_output: bool = False

    class _FakeInteractiveFederateSession:
        def __init__(self, config: _FakeSessionConfig):
            self.config = config
            self.connected = False
            self.created = False
            self.joined = False
            self.history: list[tuple[str, object]] = []

        def connect(self) -> dict[str, object]:
            self.connected = True
            self.history.append(("connect", None))
            return {"status": "ok", "message": "connected"}

        def create(self, federation_name=None, *, fom_modules=(), logical_time_implementation=None):
            self.created = True
            self.history.append(
                (
                    "create",
                    {
                        "federation_name": federation_name,
                        "fom_modules": tuple(fom_modules),
                        "logical_time_implementation": logical_time_implementation,
                    },
                )
            )
            return {"status": "ok", "message": "created", "federation_name": federation_name}

        def join(self, federate_name=None, federate_type=None, federation_name=None, *, create_if_missing=True):
            self.joined = True
            self.history.append(
                (
                    "join",
                    {
                        "federate_name": federate_name,
                        "federate_type": federate_type,
                        "federation_name": federation_name,
                        "create_if_missing": create_if_missing,
                    },
                )
            )
            return {"status": "ok", "message": "joined", "federate_name": federate_name}

        def publish_object(self, class_name, attribute_names):
            self.history.append(("publish_object", {"class_name": class_name, "attribute_names": tuple(attribute_names)}))
            return {"status": "ok", "message": "published object"}

        def subscribe_object(self, class_name, attribute_names):
            self.history.append(("subscribe_object", {"class_name": class_name, "attribute_names": tuple(attribute_names)}))
            return {"status": "ok", "message": "subscribed object"}

        def publish_interaction(self, class_name):
            self.history.append(("publish_interaction", class_name))
            return {"status": "ok", "message": "published interaction"}

        def subscribe_interaction(self, class_name):
            self.history.append(("subscribe_interaction", class_name))
            return {"status": "ok", "message": "subscribed interaction"}

        def register_object(self, class_name, instance_name):
            self.history.append(("register_object", {"class_name": class_name, "instance_name": instance_name}))
            return {"status": "ok", "message": "registered object"}

        def update_object(self, instance_name, updates):
            self.history.append(("update_object", {"instance_name": instance_name, "updates": dict(updates)}))
            return {"status": "ok", "message": "updated object"}

        def send_interaction(self, class_name, parameters):
            self.history.append(("send_interaction", {"class_name": class_name, "parameters": dict(parameters)}))
            return {"status": "ok", "message": "sent interaction"}

        def evoke(self, minimum_seconds=0.0, maximum_seconds=0.0):
            self.history.append(("evoke", {"minimum_seconds": minimum_seconds, "maximum_seconds": maximum_seconds}))
            return {"status": "ok", "message": "evoked"}

        def resign(self, action_name="NO_ACTION"):
            self.joined = False
            self.history.append(("resign", action_name))
            return {"status": "ok", "message": "resigned"}

        def destroy(self, federation_name=None):
            self.created = False
            self.history.append(("destroy", federation_name))
            return {"status": "ok", "message": "destroyed"}

        def disconnect(self):
            self.connected = False
            self.history.append(("disconnect", None))
            return {"status": "ok", "message": "disconnected"}

        def status(self):
            return {
                "status": "ok",
                "message": "session status",
                "session": {
                    "edition": self.config.edition,
                    "backend": self.config.backend,
                    "connected": self.connected,
                    "federation_created": self.created,
                    "joined": self.joined,
                    "active_federation_name": self.config.federation_name,
                    "joined_federate_name": self.config.federate_name if self.joined else None,
                    "joined_federate_type": self.config.federate_type if self.joined else None,
                    "history": list(self.history),
                },
            }

        def close(self):
            self.history.append(("close", None))

    fake_module = SimpleNamespace(
        SessionConfig=_FakeSessionConfig,
        InteractiveFederateSession=_FakeInteractiveFederateSession,
    )
    monkeypatch.setattr(service_module, "_load_federate_cli_module", lambda: fake_module)

    app = create_federate_service_fastapi_app(FederateServiceControl())
    client = TestClient(app)

    created = client.post(
        "/api/sessions",
        json={
            "edition": "2025",
            "backend": "python1516_2025",
            "federation_name": "svc-fed",
            "federate_name": "svc-federate",
            "federate_type": "analysis",
        },
    )
    assert created.status_code == 200
    session_id = created.json()["session_id"]
    assert created.json()["session"]["backend"] == "python1516_2025"

    connect = client.post(f"/api/sessions/{session_id}/invoke/connect", json={})
    assert connect.status_code == 200
    assert connect.json()["result"]["message"] == "connected"

    create = client.post(
        f"/api/sessions/{session_id}/invoke/createFederationExecution",
        json={
            "kwargs": {
                "federationExecutionName": "svc-fed",
                "fomModules": ["A.xml", "B.xml"],
                "logicalTimeImplementationName": "HLAinteger64Time",
            }
        },
    )
    assert create.status_code == 200
    assert create.json()["result"]["message"] == "created"

    join = client.post(
        f"/api/sessions/{session_id}/invoke/joinFederationExecution",
        json={
            "kwargs": {
                "federateName": "svc-federate",
                "federateType": "analysis",
                "federationExecutionName": "svc-fed",
            }
        },
    )
    assert join.status_code == 200
    assert join.json()["session"]["joined"] is True

    publish = client.post(
        f"/api/sessions/{session_id}/invoke/publishObjectClassAttributes",
        json={
            "kwargs": {
                "className": "HLAobjectRoot.BaseEntity.PhysicalEntity",
                "attributeNames": ["EntityIdentifier", "WorldLocation"],
            }
        },
    )
    assert publish.status_code == 200
    assert publish.json()["execution_status"] == "supported"

    unsupported = client.post(f"/api/sessions/{session_id}/invoke/queryGALT", json={})
    assert unsupported.status_code == 400
    assert "metadata-only" in unsupported.json()["detail"]

    removed = client.delete(f"/api/sessions/{session_id}")
    assert removed.status_code == 200
    assert removed.json()["session_id"] == session_id
