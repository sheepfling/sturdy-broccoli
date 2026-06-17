from __future__ import annotations

import pytest
from hla.rti1516_2025.foms import HLAX_V0_1_MODULES, fom_path, fom_paths, scenario_fom_paths
from hla.rti1516e.fom import FOMResolutionError, FOMResolver, merge_fom_modules, parse_fom_xml, standard_mim_module


@pytest.mark.requirements("HLA-X-2025-FR-001", "HLA-X-2025-OMT-002", "HLA-X-2025-OMT-007")
def test_hlax_2025_fom_resources_are_packaged_and_dependency_aware() -> None:
    paths = fom_paths()

    assert tuple(path.name for path in paths) == HLAX_V0_1_MODULES
    assert all(path.exists() for path in paths)
    assert all("IEEE1516-2025" in path.read_text(encoding="utf-8") for path in paths)

    modules = FOMResolver().resolve_many(paths)
    catalog = merge_fom_modules(modules, mim_module=standard_mim_module())

    assert "HLAobjectRoot.HLAx.FederateHealth" in catalog.object_classes
    assert "HLAobjectRoot.HLAx.MessageTest.TestSuite" in catalog.object_classes
    assert "HLAobjectRoot.HLAx.SpaceLite.PhysicalEntity.DynamicalEntity" in catalog.object_classes
    assert "HLAobjectRoot.HLAx.TimeMgmtTest.TimeParticipant" in catalog.object_classes
    assert "HLAinteractionRoot.HLAx.MessageTest.SendStimulus" in catalog.interaction_classes
    assert "HLAinteractionRoot.HLAx.SpaceLite.ReferenceFrameAnnouncement" in catalog.interaction_classes
    assert "HLAinteractionRoot.HLAx.TimeMgmtTest.EmitReceiveOrderEvent" in catalog.interaction_classes


@pytest.mark.requirements("HLA-X-2025-FI-008", "HLA-X-2025-OMT-007")
def test_hlax_2025_extension_modules_require_base_module_datatypes() -> None:
    message_extension = fom_path("HLAx_MessageTest.xml")

    with pytest.raises(FOMResolutionError, match="undefined datatype 'HLAxVerdict'"):
        parse_fom_xml(message_extension)

    resolved = FOMResolver().resolve_many(scenario_fom_paths("message-test"))
    assert [module.name for module in resolved] == [
        "HLA-X Base FOM Module",
        "HLA-X Message Test FOM Module",
    ]


@pytest.mark.requirements("HLA-X-2025-FR-001", "HLA-X-2025-FI-007")
@pytest.mark.parametrize(
    ("scenario", "expected_object", "expected_interaction"),
    [
        ("message-test", "HLAobjectRoot.HLAx.MessageTest.TestSuite", "HLAinteractionRoot.HLAx.MessageTest.SendStimulus"),
        ("space-lite", "HLAobjectRoot.HLAx.SpaceLite.ReferenceFrame", "HLAinteractionRoot.HLAx.SpaceLite.ReferenceFrameAnnouncement"),
        ("time-mgmt-test", "HLAobjectRoot.HLAx.TimeMgmtTest.TimeParticipant", "HLAinteractionRoot.HLAx.TimeMgmtTest.EmitReceiveOrderEvent"),
    ],
)
def test_each_hlax_2025_scenario_fom_set_merges_with_standard_mim(
    scenario: str,
    expected_object: str,
    expected_interaction: str,
) -> None:
    catalog = merge_fom_modules(FOMResolver().resolve_many(scenario_fom_paths(scenario)), mim_module=standard_mim_module())

    assert expected_object in catalog.object_classes
    assert expected_interaction in catalog.interaction_classes
    assert "HLAunicodeString" in catalog.datatype_names
