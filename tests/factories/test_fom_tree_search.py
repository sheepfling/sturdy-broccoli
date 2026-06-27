from __future__ import annotations

from hla.verification.repo_internal.fom_tree_search import (
    build_fom_search_rows,
    build_fom_tree_nodes,
    describe_loaded_fom_modules,
)


class _FakeSpec:
    def __init__(
        self,
        full_name: str,
        parent_name: str | None,
        *,
        declared_attributes: tuple[str, ...] = (),
        attributes: tuple[str, ...] = (),
        attribute_datatypes: dict[str, str] | None = None,
        declared_parameters: tuple[str, ...] = (),
        parameters: tuple[str, ...] = (),
        parameter_datatypes: dict[str, str] | None = None,
    ) -> None:
        self.full_name = full_name
        self.parent_name = parent_name
        self.declared_attributes = declared_attributes
        self.attributes = attributes
        self.attribute_datatypes = attribute_datatypes or {}
        self.declared_parameters = declared_parameters
        self.parameters = parameters
        self.parameter_datatypes = parameter_datatypes or {}


def test_build_fom_tree_nodes_and_search_rows_shape_hierarchy() -> None:
    object_nodes = build_fom_tree_nodes(
        (
            _FakeSpec("HLAobjectRoot.BaseEntity", "HLAobjectRoot", declared_attributes=("Callsign",), attributes=("Callsign",), attribute_datatypes={"Callsign": "HLAunicodeString"}),
            _FakeSpec("HLAobjectRoot.BaseEntity.Platform", "HLAobjectRoot.BaseEntity", declared_attributes=("Speed",), attributes=("Callsign", "Speed"), attribute_datatypes={"Speed": "HLAfloat32BE"}),
        ),
        kind="object",
    )
    interaction_nodes = build_fom_tree_nodes(
        (
            _FakeSpec("HLAinteractionRoot.Fire", "HLAinteractionRoot", declared_parameters=("Munition",), parameters=("Munition",), parameter_datatypes={"Munition": "HLAunicodeString"}),
        ),
        kind="interaction",
    )
    search_rows = build_fom_search_rows(
        source_name="demo",
        source_kind="family",
        object_nodes=object_nodes,
        interaction_nodes=interaction_nodes,
        datatype_names=("HLAunicodeString",),
        edition_classes=("2010",),
        edition_scope="2010 only",
        baseline_kinds=("repo-owned",),
        load_mode="standalone",
    )

    assert object_nodes[0].kind == "object"
    assert object_nodes[1].lineage == ("HLAobjectRoot.BaseEntity", "HLAobjectRoot.BaseEntity.Platform")
    assert interaction_nodes[0].datatype_hints == ("HLAunicodeString",)
    assert any(row.kind == "object" and row.name == "HLAobjectRoot.BaseEntity.Platform" for row in search_rows)
    assert any(row.kind == "interaction" and row.name == "HLAinteractionRoot.Fire" for row in search_rows)
    assert any(row.kind == "datatype" and row.name == "HLAunicodeString" for row in search_rows)


def test_describe_loaded_fom_modules_maps_inventory_and_workbench_targets() -> None:
    descriptor = describe_loaded_fom_modules(["DemoFOMmodule.xml"], year=2010)

    assert descriptor is not None
    assert descriptor["scenario_families"] == ["demo"]
    assert descriptor["edition_scope"] == "2010 only"
    assert descriptor["record_ids"] == ["repo-2010-demo"]
    assert descriptor["workbench_targets"][0]["fragment"] == "#family=demo"
