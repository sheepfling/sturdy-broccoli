from __future__ import annotations

import ast
from pathlib import Path

from hla.foms.target_radar._internal.target_radar_2025_adapter import TargetRadar2025RTIAdapter
from hla.foms.target_radar._internal.target_radar_factory import make_target_radar_factory
from hla.foms.target_radar._internal import run_target_radar_scenario as internal_run_target_radar_scenario
from hla.foms.target_radar._internal import target_radar_fom_path as internal_target_radar_fom_path
from hla.transports.grpc.python_server_2025 import start_2025_grpc_server
from hla.verification.repo_internal.verification.target_radar_backend_matrix import run_target_radar_backend_matrix
from hla.verification.repo_internal.verification.target_radar_proof import run_target_radar_proof


def test_target_radar_scenario_helpers_stay_internal_to_the_package() -> None:
    assert internal_run_target_radar_scenario.__module__.startswith("hla.foms.target_radar._internal")
    assert TargetRadar2025RTIAdapter.__module__.startswith("hla.foms.target_radar._internal")


def test_target_radar_fom_helper_points_to_package_owned_resource() -> None:
    split_path = Path(internal_target_radar_fom_path()).resolve()
    assert split_path.name == "TargetRadarFOMmodule.xml"
    assert "packages/hla-fom-target-radar/src/hla/foms/target_radar/resources/foms" in str(split_path)


def test_target_radar_verification_helpers_are_repo_internal() -> None:
    matrix_summary = run_target_radar_backend_matrix(["python1516e"], target_radar_steps=2)
    proof_summary = run_target_radar_proof(["python1516e"], target_radar_steps=2)

    assert matrix_summary["suite_name"] == "target-radar-backend-matrix"
    assert proof_summary["suite_name"] == "target-radar-proof"
    assert proof_summary["proof"]["track_reports"]


def test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter() -> None:
    runtime_factory = make_target_radar_factory("python1516_2025")
    runtime_rti = runtime_factory("target")

    assert isinstance(runtime_rti, TargetRadar2025RTIAdapter)
    assert runtime_rti.__class__.__module__.startswith("hla.foms.target_radar._internal")
    assert runtime_rti.backend_info.kind == "python/2025"
    assert runtime_rti.backend_info.details["implementation_lane"] == "hla-backend-python2025"
    assert runtime_rti.backend_info.details["counts_as_python_2025_rti"] is True


def test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface() -> None:
    scenario_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "hla-fom-target-radar"
        / "src"
        / "hla"
        / "foms"
        / "target_radar"
        / "_internal"
        / "target_radar.py"
    )
    module = ast.parse(scenario_path.read_text(encoding="utf-8"))
    required_methods: set[str] = set()

    class _Visitor(ast.NodeVisitor):
        def visit_Attribute(self, node: ast.Attribute) -> None:
            base = node.value
            if isinstance(base, ast.Name) and (base.id.endswith("_rti") or base.id == "rti"):
                required_methods.add(node.attr)
            elif (
                isinstance(base, ast.Attribute)
                and base.attr == "rti"
                and isinstance(base.value, ast.Name)
                and base.value.id == "self"
            ):
                required_methods.add(node.attr)
            self.generic_visit(node)

    _Visitor().visit(module)
    adapter_methods = {
        name
        for name, value in TargetRadar2025RTIAdapter.__dict__.items()
        if callable(value) and not name.startswith("_")
    }

    assert required_methods <= adapter_methods


def test_target_radar_factory_supports_hosted_python1516_2025_route_with_package_owned_adapter() -> None:
    server = start_2025_grpc_server()
    try:
        result = internal_run_target_radar_scenario(
            make_target_radar_factory(
                "python1516_2025",
                backend_options={"transport": {"kind": "grpc", "target": server.target}},
            ),
            federation_name="target-radar-python1516_2025-hosted",
            steps=2,
            fom_modules=["TargetRadarFOMmodule.xml"],
        )
    finally:
        server.close()

    assert result.backend_kinds == ("python/2025", "python/2025")
    assert len(result.track_reports) == 2
