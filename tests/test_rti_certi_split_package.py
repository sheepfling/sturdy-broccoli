from __future__ import annotations

from hla2010_rti_backend_common import RTIBackendPlugin


class _TransportStub:
    def start(self):
        return self

    def request(self, request):
        raise AssertionError("not used")


def test_split_certi_package_exports_backend_surface():
    from hla2010_rti_certi import (
        CERTIBackend,
        CERTIConfig,
        CERTITransport,
        prepare_certi_two_federate_profile,
    )
    from hla2010_rti_certi.certi import CERTIBackend as PackageBackend
    from hla2010_rti_certi.certi.transport import CERTITransport as PackageTransport
    from hla2010_rti_certi.testing_policy import (
        prepare_certi_two_federate_profile as prepare_profile_from_module,
    )

    assert CERTIBackend is PackageBackend
    assert CERTITransport is PackageTransport
    assert prepare_certi_two_federate_profile is prepare_profile_from_module
    assert CERTIBackend(CERTIConfig()).info.name == "CERTI"


def test_legacy_certi_modules_are_compatibility_facades():
    from hla2010_rti_certi import CERTIBackend, CERTITransport
    from hla2010_rti_certi.certi.service_adapter import CERTIBackend as ServiceBackend
    from hla2010_rti_certi.certi.transport import CERTITransport as PackageTransport

    assert ServiceBackend is CERTIBackend
    assert PackageTransport is CERTITransport


def test_split_certi_plugin_descriptors_create_transport_backends():
    from hla2010_rti_certi.certi.plugin import (
        backend_plugins,
        certi_jpype_plugin,
        certi_py4j_plugin,
        plugin,
    )

    descriptor = plugin()
    assert isinstance(descriptor, RTIBackendPlugin)
    assert descriptor.name == "certi"
    assert "certi-native" in descriptor.aliases
    assert descriptor.create_backend({"transport": _TransportStub()}).info.name == "CERTI"

    assert certi_jpype_plugin().name == "certi-jpype"
    assert certi_py4j_plugin().name == "certi-py4j"

    names = {item.name for item in backend_plugins()}
    assert names == {"certi", "certi-jpype", "certi-py4j"}
