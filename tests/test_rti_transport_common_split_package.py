from __future__ import annotations


def test_split_transport_common_package_exports_shared_transport_surface():
    import hla.transports.common
    from hla.transports.common.transport import (
        RTITransport as PackageTransport,
        SubprocessLineTransport as PackageSubprocessLineTransport,
        TransportError as PackageTransportError,
        TransportRequest as PackageTransportRequest,
        TransportResponse as PackageTransportResponse,
    )
    from hla.transports.common.transport_registry import (
        RTITransportSpec as PackageTransportSpec,
        coerce_transport_spec as package_coerce_transport_spec,
        register_transport_factory as package_register_transport_factory,
    )

    assert hla.transports.common.RTITransport is PackageTransport
    assert hla.transports.common.SubprocessLineTransport is PackageSubprocessLineTransport
    assert hla.transports.common.TransportError is PackageTransportError
    assert hla.transports.common.TransportRequest is PackageTransportRequest
    assert hla.transports.common.TransportResponse is PackageTransportResponse
    assert hla.transports.common.RTITransportSpec is PackageTransportSpec
    assert hla.transports.common.coerce_transport_spec is package_coerce_transport_spec
    assert hla.transports.common.register_transport_factory is package_register_transport_factory


def test_split_transport_common_package_exports_shared_codec_surface():
    import hla.transports.common
    from hla.transports.common.transport_codecs import (
        decode_bytes as package_decode_bytes,
        decode_handle_set as package_decode_handle_set,
        decode_handle_value_map as package_decode_handle_value_map,
        decode_order as package_decode_order,
        encode_bytes as package_encode_bytes,
        federate_handle_set_spec as package_federate_handle_set_spec,
        handle_set_spec as package_handle_set_spec,
        handle_value_map_spec as package_handle_value_map_spec,
    )

    assert hla.transports.common.decode_bytes is package_decode_bytes
    assert hla.transports.common.decode_handle_set is package_decode_handle_set
    assert hla.transports.common.decode_handle_value_map is package_decode_handle_value_map
    assert hla.transports.common.decode_order is package_decode_order
    assert hla.transports.common.encode_bytes is package_encode_bytes
    assert hla.transports.common.federate_handle_set_spec is package_federate_handle_set_spec
    assert hla.transports.common.handle_set_spec is package_handle_set_spec
    assert hla.transports.common.handle_value_map_spec is package_handle_value_map_spec
