import math
import pytest

from hla2010.backends.python_rti import InMemoryRTIEngine
from hla2010.rti import create_rti_ambassador
from hla2010.scenarios.target_radar import run_target_radar_scenario
from hla2010.testing.java_shim import SharedJavaShimKernel


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


@pytest.mark.parametrize("kind,profile", [("java-shim-jpype", "jpype"), ("java-shim-py4j", "py4j")])
def test_target_radar_same_code_runs_on_shared_java_shim(kind, profile):
    kernel = SharedJavaShimKernel()

    def factory(role):
        return create_rti_ambassador(kind, kernel=kernel, shared=True)

    result = run_target_radar_scenario(factory, federation_name=f"target-radar-{profile}", steps=2)
    assert result.backend_kinds == (f"java/{profile}/shared-shim", f"java/{profile}/shared-shim")
    assert len(result.track_reports) == 2
    assert [report.track_id for report in result.track_reports] == ["TRK-001", "TRK-002"]
    assert result.track_reports[-1].range_m > result.track_reports[0].range_m
