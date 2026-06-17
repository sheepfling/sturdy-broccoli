"""Shared vendor-runtime process helper package."""
from __future__ import annotations

from .intake import INTAKE_STATUS_LADDER, IntakeArtifact, IntakeCheck, intake_status_from_checks
from .plugin_api import (
    BACKEND_ENTRY_POINT_GROUP,
    SPEC_ENTRY_POINT_GROUP,
    TRANSPORT_ENTRY_POINT_GROUP,
    BackendRequest,
    FactoryComposition,
    HLASpec,
    RTIBackendDiscovery,
    RTIBackendPlugin,
    RTIBackendSpec,
    RTITransportSpec,
    SpecPlugin,
    TransportRequest,
)
from .real_rti_process import RuntimeProcess, reserve_tcp_port, wait_for_process_boot, wait_for_tcp_listener
from .standard_shims import (
    STANDARD_SHIM_ARTIFACTS,
    StandardShimArtifact,
    StandardShimRoute,
    iter_standard_shim_artifacts,
    iter_standard_shim_routes,
    official_api_bundle_paths,
    standard_shim_route_names,
)

_FACTORY_EXPORTS = {
    "AuthenticationContext",
    "available_spec_plugins",
    "available_backend_plugins",
    "create_backend",
    "CredentialProvider",
    "EncodingContext",
    "HlaFactoryRegistry",
    "HlaRuntimeContext",
    "create_hla_factory",
    "create_rti_ambassador",
    "discover_specs",
    "discover_rti_backends",
    "iter_hla_spec_plugins",
    "iter_rti_backend_plugins",
    "register_backend_factory",
    "register_backend_plugin",
    "register_spec_plugin",
    "register_transport_factory",
    "resolve_spec",
}


def __getattr__(name: str):
    if name in _FACTORY_EXPORTS:
        from . import factory

        value = getattr(factory, name)
        globals()[name] = value
        return value
    raise AttributeError(name)


__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "BackendRequest",
    "FactoryComposition",
    "HlaFactoryRegistry",
    "HLASpec",
    "INTAKE_STATUS_LADDER",
    "IntakeArtifact",
    "IntakeCheck",
    "RTIBackendDiscovery",
    "RTIBackendPlugin",
    "RTIBackendSpec",
    "RTITransportSpec",
    "RuntimeProcess",
    "SPEC_ENTRY_POINT_GROUP",
    "STANDARD_SHIM_ARTIFACTS",
    "SpecPlugin",
    "StandardShimArtifact",
    "StandardShimRoute",
    "TRANSPORT_ENTRY_POINT_GROUP",
    "TransportRequest",
    *_FACTORY_EXPORTS,
    "iter_standard_shim_artifacts",
    "iter_standard_shim_routes",
    "intake_status_from_checks",
    "official_api_bundle_paths",
    "reserve_tcp_port",
    "standard_shim_route_names",
    "wait_for_process_boot",
    "wait_for_tcp_listener",
]
