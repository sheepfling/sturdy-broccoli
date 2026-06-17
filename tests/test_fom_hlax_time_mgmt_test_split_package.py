from __future__ import annotations

from hla.foms.hlax_time_mgmt_test._internal import run_time_mgmt_test_showcase


def test_hlax_time_mgmt_test_showcase_helpers_stay_internal_to_the_package() -> None:
    assert run_time_mgmt_test_showcase.__module__.startswith("hla.foms.hlax_time_mgmt_test._internal")


def test_hlax_time_mgmt_test_showcase_runs_to_completion() -> None:
    summary = run_time_mgmt_test_showcase()

    assert summary["scenario"] == "time-mgmt-test"
    assert summary["status"] == "lifecycle-green"
    assert summary["execution_complete"] is True
    assert summary["fom_modules"] == ["HLAx_Base.xml", "HLAx_TimeMgmtTest.xml"]
    assert summary["delivered_tags"][-2:] == ["event-1", "event-2"]
