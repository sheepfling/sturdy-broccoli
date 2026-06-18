from __future__ import annotations

from hla.foms.proto2025_space_lite._internal import run_space_lite_showcase


def test_proto2025_space_lite_showcase_helpers_stay_internal_to_the_package() -> None:
    assert run_space_lite_showcase.__module__.startswith("hla.foms.proto2025_space_lite._internal")


def test_proto2025_space_lite_showcase_runs_to_completion() -> None:
    summary = run_space_lite_showcase()

    assert summary["scenario"] == "space-lite"
    assert summary["status"] == "lifecycle-green"
    assert summary["execution_complete"] is True
    assert summary["fom_modules"] == ["Proto2025_Base.xml", "Proto2025_SpaceLite.xml"]
