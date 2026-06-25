from __future__ import annotations

from hla.backends.common import RecordingFederateAmbassador, make_rti_ambassador
from hla.rti import create_backend
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel
from hla.verification.startup import FederationStartupConfig, connect_create_join, synchronize_ready_to_run
from hla.transports.common import coerce_transport_spec
from hla.transports.common.transport import TransportRequest, TransportResponse
from hla.transports.grpc import (
    QuirkyVendorGrpcWireAdapter,
    VendorGrpcTransport,
    VendorGrpcTransportConfig,
    VendorGrpcWireAdapter,
)


class _SharedVendorRouteController:
    def __init__(self) -> None:
        self.next_handle = 1
        self.federation_created = False
        self.member_handles: dict[str, int] = {}
        self.achieved_members: set[str] = set()
        self.pending_callbacks: dict[str, list[tuple[str, list[str]]]] = {"left": [], "right": []}

    def invoke(self, rpc_name: str, payload: object) -> object:
        payload_dict = payload if isinstance(payload, dict) else {}
        metadata = payload_dict.get("metadata", {}) if isinstance(payload_dict, dict) else {}
        member = metadata.get("member", "")
        request_payload = payload_dict.get("payload", {}) if isinstance(payload_dict, dict) else {}
        fields = list(request_payload.get("fields", [])) if isinstance(request_payload, dict) else []

        if rpc_name == "GetHlaVersion":
            return {"fields": ["HLA 1516.1-2010"]}
        if rpc_name == "Connect":
            return {"fields": []}
        if rpc_name == "Create":
            self.federation_created = True
            return {"fields": []}
        if rpc_name == "Join":
            if member not in self.member_handles:
                self.member_handles[member] = self.next_handle
                self.next_handle += 1
            return {"fields": [str(self.member_handles[member])]}
        if rpc_name == "RegisterSyncPoint":
            label = str(fields[0])
            tag_hex = str(fields[1])
            for target in self.pending_callbacks:
                self.pending_callbacks[target].append(("ANNOUNCE_SYNC_POINT", [label, tag_hex]))
            return {"fields": []}
        if rpc_name == "AchieveSyncPoint":
            self.achieved_members.add(str(member))
            if len(self.achieved_members) == len(self.pending_callbacks):
                handle_set = ",".join(str(self.member_handles[key]) for key in sorted(self.member_handles))
                for target in self.pending_callbacks:
                    self.pending_callbacks[target].append(("FEDERATION_SYNCHRONIZED", [str(fields[0]), handle_set]))
            return {"fields": []}
        if rpc_name == "VendorPoll":
            queue = self.pending_callbacks[str(member)]
            if not queue:
                return {"delivered": False}
            callback_name, callback_fields = queue.pop(0)
            return {
                "delivered": True,
                "callback_name": callback_name,
                "fields": callback_fields,
            }
        if rpc_name in {"Resign", "Destroy", "Disconnect", "CLOSE"}:
            return {"fields": []}
        raise AssertionError(f"Unexpected vendor route RPC {rpc_name!r} for member {member!r}")


def test_vendor_grpc_wire_adapter_maps_requests_without_changing_transport_contract():
    config = VendorGrpcTransportConfig(
        target="vendor.test:50051",
        metadata={"x-route": "vendor"},
        command_rpc_names={"GET_FEDERATE_HANDLE": "LookupFederateHandle"},
    )
    adapter = VendorGrpcWireAdapter(config)

    encoded = adapter.encode_request(
        TransportRequest(
            command="GET_FEDERATE_HANDLE",
            fields=("alpha",),
            metadata={"x-request-id": "req-1"},
        )
    )

    assert encoded["rpc"] == "LookupFederateHandle"
    assert encoded["payload"] == {"command": "GET_FEDERATE_HANDLE", "fields": ["alpha"]}
    assert encoded["metadata"] == {
        "x-route": "vendor",
        "x-request-id": "req-1",
    }


def test_vendor_grpc_wire_adapter_maps_callback_polling_to_transport_response_shape():
    adapter = VendorGrpcWireAdapter(VendorGrpcTransportConfig(target="vendor.test:50051"))

    response = adapter.decode_callback_request(
        {
            "delivered": True,
            "callback_name": "TIME_ADVANCE_GRANT",
            "fields": ["7.0"],
        }
    )

    assert response == TransportResponse(fields=("1", "TIME_ADVANCE_GRANT", "7.0"))
    assert adapter.decode_callback_request({"delivered": False}) == TransportResponse(fields=("0",))


def test_quirky_vendor_grpc_wire_adapter_maps_odd_envelope_shape_back_to_transport_contract():
    config = VendorGrpcTransportConfig(
        target="quirky.vendor.test:50051",
        metadata={"x-route": "quirky"},
        command_rpc_names={"GET_FEDERATE_HANDLE": "QuirkyLookup"},
        callback_poll_rpc_name="QuirkyTick",
    )
    adapter = QuirkyVendorGrpcWireAdapter(config)

    encoded = adapter.encode_request(
        TransportRequest(
            command="GET_FEDERATE_HANDLE",
            fields=("alpha",),
            metadata={"x-request-id": "quirky-1"},
        )
    )
    decoded = adapter.decode_response(
        TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)),
        {"result": {"values": ["42"], "meta": {"route": "quirky"}}},
    )
    callback = adapter.decode_callback_request(
        {
            "callbackEnvelope": {
                "present": True,
                "name": "TIME_ADVANCE_GRANT",
                "arguments": ["HLAfloat64Time", "13.0"],
            }
        }
    )

    assert encoded["rpc"] == "QuirkyLookup"
    assert encoded["quirks"] == {"style": "capsule-v1", "field_count": 1}
    assert encoded["capsule"] == {
        "verb": "get_federate_handle",
        "items": [{"slot": 0, "text": "alpha"}],
    }
    assert encoded["metadata"] == {
        "x-route": "quirky",
        "x-request-id": "quirky-1",
        "x-quirky-wire": "enabled",
    }
    assert decoded == TransportResponse(fields=("42",), metadata={"route": "quirky"})
    assert callback == TransportResponse(fields=("1", "TIME_ADVANCE_GRANT", "HLAfloat64Time", "13.0"))


def test_vendor_grpc_transport_uses_injected_route_invoke_for_calls_and_callback_polling():
    calls: list[tuple[str, object]] = []

    def _invoke(rpc_name: str, payload: object) -> object:
        calls.append((rpc_name, payload))
        if rpc_name == "LookupFederateHandle":
            return {"fields": ["42"], "metadata": {"route": "vendor"}}
        if rpc_name == "VendorPoll":
            return {
                "delivered": True,
                "callback_name": "TIME_ADVANCE_GRANT",
                "fields": ["9.0"],
            }
        raise AssertionError(f"Unexpected RPC name: {rpc_name}")

    transport = VendorGrpcTransport(
        VendorGrpcTransportConfig(
            target="vendor.test:50051",
            command_rpc_names={"GET_FEDERATE_HANDLE": "LookupFederateHandle"},
            callback_poll_rpc_name="VendorPoll",
        ),
        invoke=_invoke,
    ).start()
    try:
        handle_response = transport.request(TransportRequest(command="GET_FEDERATE_HANDLE", fields=("alpha",)))
        callback_response = transport.request(TransportRequest(command="EVOKE"))
    finally:
        transport.close()

    assert handle_response == TransportResponse(fields=("42",), metadata={"route": "vendor"})
    assert callback_response == TransportResponse(fields=("1", "TIME_ADVANCE_GRANT", "9.0"))
    assert calls[0][0] == "LookupFederateHandle"
    assert calls[1][0] == "VendorPoll"


def test_vendor_grpc_transport_registers_through_shared_transport_registry():
    transport = coerce_transport_spec(
        {
            "kind": "vendor-grpc",
            "target": "vendor.test:50051",
            "callback_poll_rpc_name": "VendorPoll",
        }
    )

    assert isinstance(transport, VendorGrpcTransport)
    assert transport.config.target == "vendor.test:50051"
    assert transport.config.callback_poll_rpc_name == "VendorPoll"


def test_quirky_vendor_grpc_transport_registers_through_shared_transport_registry():
    transport = coerce_transport_spec(
        {
            "kind": "quirky-vendor-grpc",
            "target": "quirky.vendor.test:50051",
            "callback_poll_rpc_name": "QuirkyTick",
        }
    )

    assert isinstance(transport, VendorGrpcTransport)
    assert isinstance(transport.adapter, QuirkyVendorGrpcWireAdapter)
    assert transport.config.target == "quirky.vendor.test:50051"
    assert transport.config.callback_poll_rpc_name == "QuirkyTick"


def test_vendor_grpc_transport_can_drive_backend_and_ambassador_end_to_end():
    calls: list[tuple[str, object]] = []

    def _invoke(rpc_name: str, payload: object) -> object:
        calls.append((rpc_name, payload))
        payload_dict = payload if isinstance(payload, dict) else {}
        request_payload = payload_dict.get("payload", {}) if isinstance(payload_dict, dict) else {}
        command = request_payload.get("command")
        if rpc_name == "GetHlaVersion":
            return {"fields": ["HLA 1516.1-2010"]}
        if rpc_name == "Connect":
            return {"fields": []}
        if rpc_name == "LookupFederateHandle":
            return {"fields": ["42"]}
        if rpc_name == "VendorPoll":
            return {
                "delivered": True,
                "callback_name": "TIME_ADVANCE_GRANT",
                "fields": ["HLAfloat64Time", "11.0"],
            }
        raise AssertionError(f"Unexpected RPC name: {rpc_name} for command {command!r}")

    backend = create_backend(
        "certi",
        spec="rti1516e",
        transport={
            "kind": "vendor-grpc",
            "target": "vendor.test:50051",
            "command_rpc_names": {
                "GET_HLA_VERSION": "GetHlaVersion",
                "GET_FEDERATE_HANDLE": "LookupFederateHandle",
                "CONNECT": "Connect",
            },
            "callback_poll_rpc_name": "VendorPoll",
            "invoke": _invoke,
        },
    )
    rti = make_rti_ambassador(backend)
    try:
        assert backend.start() is backend
        assert rti.getHLAversion() == "HLA 1516.1-2010"

        rti.connect(NullFederateAmbassador(), CallbackModel.HLA_EVOKED)
        handle = rti.getFederateHandle("alpha")
        callback = rti.evokeCallback(0.0)
    finally:
        backend.close()

    assert int(handle.value) == 42
    assert callback is True
    assert [rpc_name for rpc_name, _payload in calls] == [
        "GetHlaVersion",
        "Connect",
        "LookupFederateHandle",
        "VendorPoll",
        "CLOSE",
    ]


def test_vendor_grpc_transport_can_run_two_federate_startup_sync_smoke():
    controller = _SharedVendorRouteController()
    left_backend = create_backend(
        "certi",
        spec="rti1516e",
        transport={
            "kind": "vendor-grpc",
            "target": "vendor.test:50051",
            "metadata": {"member": "left"},
            "command_rpc_names": {
                "GET_HLA_VERSION": "GetHlaVersion",
                "CONNECT": "Connect",
                "CREATE": "Create",
                "JOIN": "Join",
                "REGISTER_FEDERATION_SYNCHRONIZATION_POINT": "RegisterSyncPoint",
                "SYNCHRONIZATION_POINT_ACHIEVED": "AchieveSyncPoint",
                "RESIGN": "Resign",
                "DESTROY": "Destroy",
                "DISCONNECT": "Disconnect",
            },
            "callback_poll_rpc_name": "VendorPoll",
            "invoke": controller.invoke,
        },
    )
    right_backend = create_backend(
        "certi",
        spec="rti1516e",
        transport={
            "kind": "vendor-grpc",
            "target": "vendor.test:50051",
            "metadata": {"member": "right"},
            "command_rpc_names": {
                "GET_HLA_VERSION": "GetHlaVersion",
                "CONNECT": "Connect",
                "CREATE": "Create",
                "JOIN": "Join",
                "REGISTER_FEDERATION_SYNCHRONIZATION_POINT": "RegisterSyncPoint",
                "SYNCHRONIZATION_POINT_ACHIEVED": "AchieveSyncPoint",
                "RESIGN": "Resign",
                "DESTROY": "Destroy",
                "DISCONNECT": "Disconnect",
            },
            "callback_poll_rpc_name": "VendorPoll",
            "invoke": controller.invoke,
        },
    )
    left = make_rti_ambassador(left_backend)
    right = make_rti_ambassador(right_backend)
    left_fed = RecordingFederateAmbassador()
    right_fed = RecordingFederateAmbassador()
    config = FederationStartupConfig(
        federation_name="VendorGrpcStartupFederation",
        federate_type="VendorRouteFederate",
        logical_time_implementation_name="HLAfloat64Time",
        callback_model=CallbackModel.HLA_EVOKED,
    )
    try:
        connect_create_join(left, left_fed, config)
        connect_create_join(right, right_fed, config)
        synchronize_ready_to_run((left, right), label="ReadyToRun", tag=b"startup", max_passes=8)

        assert left_fed.last_callback("announceSynchronizationPoint") is not None
        assert right_fed.last_callback("announceSynchronizationPoint") is not None
        assert left_fed.last_callback("federationSynchronized") is not None
        assert right_fed.last_callback("federationSynchronized") is not None

        right.resign_federation_execution("NO_ACTION")
        left.resign_federation_execution("NO_ACTION")
        left.destroy_federation_execution(config.federation_name)
        right.disconnect()
        left.disconnect()
    finally:
        right.close()
        left.close()


def test_quirky_vendor_grpc_transport_can_drive_backend_and_ambassador_end_to_end():
    calls: list[tuple[str, object]] = []

    def _invoke(rpc_name: str, payload: object) -> object:
        calls.append((rpc_name, payload))
        payload_dict = payload if isinstance(payload, dict) else {}
        capsule = payload_dict.get("capsule", {}) if isinstance(payload_dict, dict) else {}
        if rpc_name == "QuirkyVersion":
            return {"result": {"values": ["HLA 1516.1-2010"], "meta": {"route": "quirky"}}}
        if rpc_name == "QuirkyConnect":
            return {"result": {"values": []}}
        if rpc_name == "QuirkyLookup":
            assert capsule == {
                "verb": "get_federate_handle",
                "items": [{"slot": 0, "text": "alpha"}],
            }
            return {"result": {"values": ["42"]}}
        if rpc_name == "QuirkyTick":
            return {
                "callbackEnvelope": {
                    "present": True,
                    "name": "TIME_ADVANCE_GRANT",
                    "arguments": ["HLAfloat64Time", "15.0"],
                }
            }
        if rpc_name == "CLOSE":
            return {"result": {"values": []}}
        raise AssertionError(f"Unexpected quirky vendor RPC {rpc_name!r}")

    backend = create_backend(
        "certi",
        spec="rti1516e",
        transport={
            "kind": "quirky-vendor-grpc",
            "target": "quirky.vendor.test:50051",
            "command_rpc_names": {
                "GET_HLA_VERSION": "QuirkyVersion",
                "GET_FEDERATE_HANDLE": "QuirkyLookup",
                "CONNECT": "QuirkyConnect",
            },
            "callback_poll_rpc_name": "QuirkyTick",
            "invoke": _invoke,
        },
    )
    rti = make_rti_ambassador(backend)
    try:
        assert backend.start() is backend
        assert rti.getHLAversion() == "HLA 1516.1-2010"

        rti.connect(NullFederateAmbassador(), CallbackModel.HLA_EVOKED)
        handle = rti.getFederateHandle("alpha")
        callback = rti.evokeCallback(0.0)
    finally:
        backend.close()

    assert int(handle.value) == 42
    assert callback is True
    assert [rpc_name for rpc_name, _payload in calls] == [
        "QuirkyVersion",
        "QuirkyConnect",
        "QuirkyLookup",
        "QuirkyTick",
        "CLOSE",
    ]
