"""Backend plugin bridge for generic C++ SDK intake routes."""
from __future__ import annotations

from hla.backends.common import BackendInfo
from hla.rti.plugin_api import BackendRequest

from .cpp_intake import CppSdkIntakeRequest, cpp_api_profile, discover_cpp_sdk


def discover_cpp_sdk_backend(edition: str, transport: str) -> BackendInfo:
    profile = cpp_api_profile(edition)
    return BackendInfo(
        name=f"cpp-{profile.edition}-sdk-{transport}",
        kind=f"cpp/{transport}/sdk-intake-{profile.edition}",
        details={
            "edition": profile.edition,
            "spec": profile.spec_name,
            "transport": transport,
            "generic_intake": True,
            "default_external_transport": "grpc",
            "status_ladder": (
                "profile-valid",
                "header-green",
                "compile-green",
                "link-green",
                "factory-green",
                "ambassador-green",
                "connect-green",
                "callback-green",
                "core-green",
                "trace-green",
            ),
        },
    )


def create_cpp_sdk_intake_backend(edition: str, transport: str, request: BackendRequest):
    profile = cpp_api_profile(edition)
    if request.spec.name != profile.spec_name:
        raise ValueError(f"C++ {profile.edition} SDK intake route does not support HLA spec {request.spec.name!r}")
    profile_path = request.options.get("profile") or request.options.get("profile_path")
    if not profile_path:
        raise ValueError("Generic C++ SDK intake routes require profile=... or profile_path=...")
    report = discover_cpp_sdk(CppSdkIntakeRequest(profile_path=str(profile_path), transport=transport))
    if report.errors:
        raise RuntimeError("; ".join(report.errors))
    raise RuntimeError(
        f"C++ {profile.edition} SDK capsule invocation is not implemented yet. "
        f"Discovery reached {report.status}; next step is generated {transport} capsule build."
    )


__all__ = ["create_cpp_sdk_intake_backend", "discover_cpp_sdk_backend"]
