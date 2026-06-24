from hla.rti1516e.raw_api import API_METADATA
from hla.spec.refs import FOM_REFERENCES, method_reference
from hla.backends.common import DelegatingRTIAmbassador
from hla.backends.inmemory import PythonRTIBackend


def test_all_generated_ambassador_methods_are_section_mapped():
    for ambassador_name, methods in API_METADATA.items():
        missing = [method for method in methods if method_reference(method) is None]
        assert missing == [], f"{ambassador_name} missing spec refs: {missing}"


def test_python_rti_has_entry_points_for_all_generated_rti_services():
    missing = [
        method for method in API_METADATA["RTIambassador"]
        if not hasattr(PythonRTIBackend, f"_svc_{method}")
    ]
    assert missing == []


def test_delegating_ambassador_docstrings_include_clause_numbers():
    assert "§4.2" in (DelegatingRTIAmbassador.connect.__doc__ or "")
    assert "§4.9" in (DelegatingRTIAmbassador.joinFederationExecution.__doc__ or "")
    assert method_reference("timeAdvanceGrant").section == "8.13"
    assert FOM_REFERENCES["object_class_structure"].section == "4.2"
    assert FOM_REFERENCES["time_representation_table"].section == "4.7"
