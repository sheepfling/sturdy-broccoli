from __future__ import annotations

from hla.rti import create_rti_ambassador
from hla.bridges.java.common import create_java_backend
from hla.bridges.java.common.java_shim_kernel import SharedJavaShimKernel
from hla.rti import available_backend_plugins
import pytest


def test_java_shim_route_aliases_are_first_class_test_shim_plugins() -> None:
    plugins = available_backend_plugins()

    assert "java-standard-shim-jpype" not in plugins
    assert "java-standard-shim-py4j" not in plugins
    assert plugins["jpype"].name == "jpype"
    assert plugins["py4j"].name == "py4j"
    assert plugins["java-shim-jpype"].name == "java-shim-jpype"
    assert plugins["java-shim-py4j"].name == "java-shim-py4j"
    assert plugins["java-standard-2010-jpype"].family == "standard/java"
    assert plugins["java-standard-2010-py4j"].family == "standard/java"


def test_java_shim_route_aliases_create_java_shim_backends() -> None:
    jpype_backend = create_java_backend(bridge="java-shim-jpype", shared=True, kernel=SharedJavaShimKernel())
    py4j_backend = create_java_backend(bridge="java-shim-py4j", shared=True, kernel=SharedJavaShimKernel())

    assert jpype_backend.info.kind == "java/jpype/shared-shim"
    assert py4j_backend.info.kind == "java/py4j/shared-shim"


def test_java_shim_routes_create_2025_native_ambassadors() -> None:
    for backend_name, expected_kind in (
        ("java-shim-jpype", "java/jpype/shim"),
        ("java-shim-py4j", "java/py4j/shim"),
    ):
        rti = create_rti_ambassador(spec="2025", backend=backend_name)
        assert rti.__class__.__name__ == "Python2025RTIAmbassador"
        assert rti.backend_info.kind == expected_kind
        assert rti.backend_info.details["spec"] == "rti1516_2025"
        assert rti.backend_info.details["runtime_provider"] == "python1516_2025"
        assert rti.backend_info.details["implementation_lane"] == "hla-backend-python2025"
        assert rti.backend_info.details["counts_as_python_2025_rti"] is False
        assert rti.backend_info.details["wrapper_only"] is False
        assert rti.getHLAversion() == "IEEE 1516.1-2025"


@pytest.mark.parametrize("backend_name", ["java-standard-2010-jpype", "java-standard-2010-py4j"])
def test_java_standard_2010_routes_do_not_fall_back_to_test_shim(backend_name: str) -> None:
    with pytest.raises(RuntimeError, match="Java 2010 standard shim jar is missing"):
        create_rti_ambassador(spec="rti1516e", backend=backend_name, jar_path="missing-standard-shim.jar")
