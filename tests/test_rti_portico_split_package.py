from __future__ import annotations

from hla.backends.common import RTIBackendPlugin


def test_split_portico_package_exports_runtime_helpers():
    from hla.vendors.portico import (
        PorticoRuntime,
        discover_portico_runtime,
        discover_portico_two_federate_profile,
    )
    from hla.vendors.portico.real_rti_portico import (
        PorticoRuntime as RuntimeFromModule,
    )
    from hla.vendors.portico.real_rti_portico import (
        discover_portico_runtime as discover_from_module,
    )
    from hla.vendors.portico.testing_policy import (
        discover_portico_two_federate_profile as discover_profile_from_module,
    )

    assert RuntimeFromModule is PorticoRuntime
    assert discover_from_module is discover_portico_runtime
    assert discover_profile_from_module is discover_portico_two_federate_profile


def test_split_portico_plugin_descriptors_are_registered():
    from hla.vendors.portico.plugin import portico_jpype_plugin, portico_py4j_plugin

    jpype_descriptor = portico_jpype_plugin()
    py4j_descriptor = portico_py4j_plugin()

    assert isinstance(jpype_descriptor, RTIBackendPlugin)
    assert isinstance(py4j_descriptor, RTIBackendPlugin)
    assert jpype_descriptor.name == "portico-jpype"
    assert py4j_descriptor.name == "portico-py4j"
    assert jpype_descriptor.family == "portico/java"
    assert py4j_descriptor.family == "portico/java"
