from __future__ import annotations

from hla.foms.proto2025_message_test._internal import run_message_test_showcase


def test_proto2025_message_test_showcase_helpers_stay_internal_to_the_package() -> None:
    assert run_message_test_showcase.__module__.startswith("hla.foms.proto2025_message_test._internal")


def test_proto2025_message_test_showcase_runs_to_completion() -> None:
    summary = run_message_test_showcase()

    assert summary["scenario"] == "message-test"
    assert summary["status"] == "lifecycle-green"
    assert summary["execution_complete"] is True
    assert summary["fom_modules"] == ["Proto2025_Base.xml", "Proto2025_MessageTest.xml"]
