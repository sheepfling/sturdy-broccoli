from __future__ import annotations

from hla.backends.common import RTIBackendPlugin


class _TransportStub:
    def start(self):
        return self

    def request(self, request):
        raise AssertionError("not used")


def test_split_certi_package_exports_backend_surface():
    from hla.backends.certi import (
        CERTIBackend,
        CERTIConfig,
        CERTITransport,
        prepare_certi_two_federate_profile,
    )
    from hla.backends.certi.certi import CERTIBackend as PackageBackend
    from hla.backends.certi.certi.transport import CERTITransport as PackageTransport
    from hla.backends.certi.testing_policy import (
        prepare_certi_two_federate_profile as prepare_profile_from_module,
    )

    assert CERTIBackend is PackageBackend
    assert CERTITransport is PackageTransport
    assert prepare_certi_two_federate_profile is prepare_profile_from_module
    assert CERTIBackend(CERTIConfig()).info.name == "CERTI"


def test_split_certi_plugin_descriptors_create_transport_backends():
    from hla.backends.certi.certi.plugin import backend_plugins, plugin

    descriptor = plugin()
    assert isinstance(descriptor, RTIBackendPlugin)
    assert descriptor.name == "certi"
    assert "certi-native" in descriptor.aliases
    assert descriptor.create_backend({"transport": _TransportStub()}).info.name == "CERTI"

    names = {item.name for item in backend_plugins()}
    assert names == {"certi"}
