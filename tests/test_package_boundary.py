from __future__ import annotations

from setuptools import find_packages


def test_installable_package_excludes_repo_internal_testing_helpers():
    packages = set(
        find_packages(
            where="src",
            include=["hla2010*"],
            exclude=["hla2010.testing*"],
        )
    )
    assert "hla2010" in packages
    assert "hla2010.backends" in packages
    assert "hla2010.testing" not in packages


def test_transitional_mega_package_includes_split_python_rti_package():
    python_packages = set(find_packages(where="packages/hla2010-rti-python/src", include=["hla2010_rti_python*"]))
    certi_packages = set(find_packages(where="packages/hla2010-rti-certi/src", include=["hla2010_rti_certi*"]))
    backend_common_packages = set(find_packages(where="packages/hla2010-rti-backend-common/src", include=["hla2010_rti_backend_common*"]))
    java_common_packages = set(find_packages(where="packages/hla2010-rti-java-common/src", include=["hla2010_rti_java_common*"]))
    runtime_common_packages = set(find_packages(where="packages/hla2010-rti-runtime-common/src", include=["hla2010_rti_runtime_common*"]))
    java_jpype_packages = set(find_packages(where="packages/hla2010-rti-java-jpype/src", include=["hla2010_rti_java_jpype*"]))
    java_py4j_packages = set(find_packages(where="packages/hla2010-rti-java-py4j/src", include=["hla2010_rti_java_py4j*"]))
    pitch_common_packages = set(find_packages(where="packages/hla2010-rti-pitch-common/src", include=["hla2010_rti_pitch_common*"]))
    pitch_jpype_packages = set(find_packages(where="packages/hla2010-rti-pitch-jpype/src", include=["hla2010_rti_pitch_jpype*"]))
    pitch_py4j_packages = set(find_packages(where="packages/hla2010-rti-pitch-py4j/src", include=["hla2010_rti_pitch_py4j*"]))
    portico_packages = set(find_packages(where="packages/hla2010-rti-portico/src", include=["hla2010_rti_portico*"]))
    target_radar_packages = set(find_packages(where="packages/hla2010-fom-target-radar/src", include=["hla2010_fom_target_radar*"]))
    verification_harness_packages = set(find_packages(where="packages/hla2010-verification-harness/src", include=["hla2010_verification_harness*"]))

    assert "hla2010_rti_python" in python_packages
    assert "hla2010_rti_certi" in certi_packages
    assert "hla2010_rti_certi.certi" in certi_packages
    assert "hla2010_rti_certi.certi_java" in certi_packages
    assert "hla2010_rti_backend_common" in backend_common_packages
    assert "hla2010_rti_java_common" in java_common_packages
    assert "hla2010_rti_runtime_common" in runtime_common_packages
    assert "hla2010_rti_java_jpype" in java_jpype_packages
    assert "hla2010_rti_java_py4j" in java_py4j_packages
    assert "hla2010_rti_pitch_common" in pitch_common_packages
    assert "hla2010_rti_pitch_jpype" in pitch_jpype_packages
    assert "hla2010_rti_pitch_py4j" in pitch_py4j_packages
    assert "hla2010_rti_portico" in portico_packages
    assert "hla2010_fom_target_radar" in target_radar_packages
    assert "hla2010_fom_target_radar.scenarios" in target_radar_packages
    assert "hla2010_fom_target_radar.testing" in target_radar_packages
    assert "hla2010_verification_harness" in verification_harness_packages
