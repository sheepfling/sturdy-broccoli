import math
import importlib.util
from pathlib import Path

import pytest

from hla.backends.common import make_rti_ambassador
from hla.foms.target_radar._internal import run_target_radar_scenario
from hla.backends.inmemory import InMemoryRTIEngine
from hla.rti1516e.factory import create_rti_ambassador
from hla.bridges.java.common.java_shim_factory import create_shared_java_shim_backend
from hla.bridges.java.common.java_shim_kernel import SharedJavaShimKernel

ROOT = Path(__file__).resolve().parents[2]


def _load_target_radar_example_module():
    module_path = ROOT / "examples" / "target_radar_simulation.py"
    spec = importlib.util.spec_from_file_location("target_radar_simulation_example", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_target_radar_runs_on_python_rti():
    engine = InMemoryRTIEngine()

    def factory(role):
        return create_rti_ambassador("python", engine=engine)

    result = run_target_radar_scenario(factory, federation_name="target-radar-python", steps=3)
    assert result.backend_kinds == ("python/in-memory", "python/in-memory")
    assert len(result.track_reports) == 3
    assert any(name == "provide_attribute_value_update" for name, _ in result.target_events)
    assert [name for name, _ in result.radar_events].count("track") == 3
    first = result.track_reports[0]
    assert first.target_name == "Target-1"
    assert math.isclose(first.range_m, math.sqrt(10_250.0**2 + 1_030.0**2 + 2_000.0**2))
    assert first.rcs_square_meters == 12.5
    assert result.track_reports[-1].range_m > result.track_reports[0].range_m


def test_target_radar_example_keeps_python2025_as_primary_2025_lane_and_shim_as_wrapper_alias() -> None:
    module = _load_target_radar_example_module()

    assert module.__doc__ is not None
    normalized_doc = " ".join(module.__doc__.split()).lower()
    assert "treat ``python2025`` as the main full python rti implementation lane" in normalized_doc
    assert "``shim`` spellings remain available only as compatibility-wrapper aliases" in normalized_doc
    assert module._BACKEND_HELP == (
        "Backend/provider name. Use 'python2025' for the primary IEEE 1516.1-2025 Python RTI. "
        "The 'shim' names are compatibility-wrapper aliases over that same runtime."
    )


@pytest.mark.parametrize(
    ("backend_name", "expected_backend_kind"),
    [("python2025", "python/2025"), ("shim", "shim/2025")],
)
def test_target_radar_example_supports_2025_backends(backend_name: str, expected_backend_kind: str, capsys) -> None:
    module = _load_target_radar_example_module()

    exit_code = module.main(["--backend", backend_name, "--steps", "2"])

    assert exit_code == 0
    stdout = capsys.readouterr().out
    assert f"backend={expected_backend_kind},{expected_backend_kind}" in stdout
    assert "federation=TargetRadarFederation" in stdout
    assert "tracks=2" in stdout


@pytest.mark.parametrize("kind,profile", [("java-shim-jpype", "jpype"), ("java-shim-py4j", "py4j")])
def test_target_radar_same_code_runs_on_shared_java_shim(kind, profile):
    kernel = SharedJavaShimKernel()

    def factory(role):
        return make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))

    result = run_target_radar_scenario(factory, federation_name=f"target-radar-{profile}", steps=2)
    assert result.backend_kinds == (f"java/{profile}/shared-shim", f"java/{profile}/shared-shim")
    assert len(result.track_reports) == 2
    assert [report.track_id for report in result.track_reports] == ["TRK-001", "TRK-002"]
    assert result.track_reports[-1].range_m > result.track_reports[0].range_m
