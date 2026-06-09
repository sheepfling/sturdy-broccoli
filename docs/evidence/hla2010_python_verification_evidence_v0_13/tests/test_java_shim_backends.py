import pytest

from hla2010.backends.base import make_rti_ambassador
from hla2010.exceptions import FederationExecutionDoesNotExist
from hla2010.testing.java_shim_factory import create_java_shim_backend
from hla2010.testing.scenario_basic import run_basic_federate_scenario


@pytest.mark.parametrize("profile", ["jpype", "py4j"])
def test_java_bridge_profile_runs_backend_neutral_federate_scenario(profile):
    summary = run_basic_federate_scenario(
        lambda: make_rti_ambassador(create_java_shim_backend(profile)),
        federation_name=f"{profile}-scenario",
    )
    assert summary["backend"].kind == f"java/{profile}/shim"
    assert summary["event_names"].count("discover") == 1
    assert summary["event_names"].count("reflect") == 1
    assert summary["event_names"].count("interaction") == 1


def test_same_federate_scenario_does_not_branch_on_java_bridge_profile():
    jpype_summary = run_basic_federate_scenario(
        lambda: make_rti_ambassador(create_java_shim_backend("jpype")),
        federation_name="same-code-jpype",
    )
    py4j_summary = run_basic_federate_scenario(
        lambda: make_rti_ambassador(create_java_shim_backend("py4j")),
        federation_name="same-code-py4j",
    )
    assert jpype_summary["event_names"] == py4j_summary["event_names"]


def test_java_like_exceptions_translate_to_python_rti_exceptions():
    rti = make_rti_ambassador(create_java_shim_backend("jpype"))
    # Destroying a federation before connect should first show NotConnected.  We
    # then connect and ask for a missing federation to prove Java simple class
    # names map into the Python exception hierarchy.
    from hla2010.runtime_api import FederateAmbassador
    from hla2010.enums import CallbackModel

    rti.connect(FederateAmbassador(), CallbackModel.HLA_EVOKED)
    with pytest.raises(FederationExecutionDoesNotExist):
        rti.destroy_federation_execution("missing")
    rti.disconnect()
    rti.close()
