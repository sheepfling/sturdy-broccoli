from __future__ import annotations


def test_split_transport_common_package_exports_shared_transport_surface():
    import hla2010_rti_transport_common
    from hla2010_rti_transport_common.transport import (
        RTITransport as PackageTransport,
        SubprocessLineTransport as PackageSubprocessLineTransport,
        TransportError as PackageTransportError,
        TransportRequest as PackageTransportRequest,
        TransportResponse as PackageTransportResponse,
    )
    from hla2010_rti_transport_common.transport_registry import (
        RTITransportSpec as PackageTransportSpec,
        coerce_transport_spec as package_coerce_transport_spec,
        register_transport_factory as package_register_transport_factory,
    )

    assert hla2010_rti_transport_common.RTITransport is PackageTransport
    assert hla2010_rti_transport_common.SubprocessLineTransport is PackageSubprocessLineTransport
    assert hla2010_rti_transport_common.TransportError is PackageTransportError
    assert hla2010_rti_transport_common.TransportRequest is PackageTransportRequest
    assert hla2010_rti_transport_common.TransportResponse is PackageTransportResponse
    assert hla2010_rti_transport_common.RTITransportSpec is PackageTransportSpec
    assert hla2010_rti_transport_common.coerce_transport_spec is package_coerce_transport_spec
    assert hla2010_rti_transport_common.register_transport_factory is package_register_transport_factory


def test_split_transport_common_package_exports_shared_codec_surface():
    import hla2010_rti_transport_common
    from hla2010_rti_transport_common.transport_codecs import (
        decode_bytes as package_decode_bytes,
        decode_handle_set as package_decode_handle_set,
        decode_handle_value_map as package_decode_handle_value_map,
        decode_order as package_decode_order,
        encode_bytes as package_encode_bytes,
        federate_handle_set_spec as package_federate_handle_set_spec,
        handle_set_spec as package_handle_set_spec,
        handle_value_map_spec as package_handle_value_map_spec,
    )

    assert hla2010_rti_transport_common.decode_bytes is package_decode_bytes
    assert hla2010_rti_transport_common.decode_handle_set is package_decode_handle_set
    assert hla2010_rti_transport_common.decode_handle_value_map is package_decode_handle_value_map
    assert hla2010_rti_transport_common.decode_order is package_decode_order
    assert hla2010_rti_transport_common.encode_bytes is package_encode_bytes
    assert hla2010_rti_transport_common.federate_handle_set_spec is package_federate_handle_set_spec
    assert hla2010_rti_transport_common.handle_set_spec is package_handle_set_spec
    assert hla2010_rti_transport_common.handle_value_map_spec is package_handle_value_map_spec
