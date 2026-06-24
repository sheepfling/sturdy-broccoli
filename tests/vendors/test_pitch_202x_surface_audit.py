from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.pitch_202x_surface_audit import build_pitch_202x_surface_audit


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_pitch_202x_surface_audit_confirms_close_method_surface_but_bridge_blockers() -> None:
    report = build_pitch_202x_surface_audit(REPO_ROOT)

    assert report.vendor_bundle_version == "Pitch pRTI Free v 5.5.10"
    assert report.vendor_api_version == "202X-240403"
    assert report.adapter_readiness == "surface-close-bridge-blocked"

    assert report.rti_ambassador.vendor_only_method_names == ()
    assert report.rti_ambassador.repo_only_method_names == (
        "decodeAttributeHandle",
        "decodeDimensionHandle",
        "decodeFederateHandle",
        "decodeInteractionClassHandle",
        "decodeMessageRetractionHandle",
        "decodeObjectClassHandle",
        "decodeObjectInstanceHandle",
        "decodeParameterHandle",
        "decodeRegionHandle",
        "getTimeFactory",
    )
    assert report.rti_ambassador.overload_count_mismatches == ()
    assert report.federate_ambassador.vendor_only_method_names == ()
    assert report.federate_ambassador.repo_only_method_names == ()
    assert report.federate_ambassador.overload_count_mismatches == ()

    blocker_paths = {finding.path for finding in report.blocker_findings}
    assert "packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py" in blocker_paths
    assert "packages/hla-bridge-java-common/src/hla/bridges/java/common/java_factory_selection.py" in blocker_paths
