from __future__ import annotations

from typing import Any, Iterable, Mapping

from ._fom_errors import FOMMergeError
from ._fom_models import (
    ArrayDatatypeSpec,
    BasicDatatypeSpec,
    EnumeratedDatatypeSpec,
    FOMCatalog,
    FOMModule,
    FixedRecordDatatypeSpec,
    InteractionClassSpec,
    ObjectClassSpec,
    SimpleDatatypeSpec,
    VariantRecordDatatypeSpec,
)


def _stable_union(*groups: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value and value not in seen:
                result.append(value)
                seen.add(value)
    return tuple(result)


def _stable_mapping_union(*groups: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for group in groups:
        for key, value in dict(group).items():
            if key and value and key not in result:
                result[key] = value
    return result


def _stable_spec_union(existing: Mapping[str, Any], incoming: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    result = dict(existing)
    for name, spec in dict(incoming).items():
        if name in result and result[name] != spec:
            raise FOMMergeError(f"Conflicting {kind} definition {name!r} across FOM modules")
        result.setdefault(name, spec)
    return result


def merge_fom_modules(modules: Iterable[FOMModule], *, mim_module: FOMModule | None = None) -> FOMCatalog:
    """Merge a MIM and FOM modules into a name catalog."""

    ordered_modules = tuple(module for module in modules if module is not None)
    all_modules = tuple([mim_module] if mim_module is not None else ()) + ordered_modules

    objects: dict[str, ObjectClassSpec] = {}
    interactions: dict[str, InteractionClassSpec] = {}
    dimensions: set[str] = set()
    datatype_names: set[str] = set()
    basic_datatypes: dict[str, BasicDatatypeSpec] = {}
    simple_datatypes: dict[str, SimpleDatatypeSpec] = {}
    enumerated_datatypes: dict[str, EnumeratedDatatypeSpec] = {}
    array_datatypes: dict[str, ArrayDatatypeSpec] = {}
    fixed_record_datatypes: dict[str, FixedRecordDatatypeSpec] = {}
    variant_record_datatypes: dict[str, VariantRecordDatatypeSpec] = {}
    tag_representations: dict[str, dict[str, str]] = {}
    transportation_names: set[str] = set()
    update_rates: dict[str, str] = {}
    synchronization_points: dict[str, dict[str, str]] = {}
    switch_settings: dict[str, str] = {}
    notes: list[str] = []
    time_impls: list[str] = []

    for module in all_modules:
        if module.inferred_time_implementation:
            time_impls.append(module.inferred_time_implementation)
        dimensions.update(module.dimensions)
        datatype_names.update(module.datatype_names)
        basic_datatypes = _stable_spec_union(basic_datatypes, module.basic_datatypes, kind="basic datatype")
        simple_datatypes = _stable_spec_union(simple_datatypes, module.simple_datatypes, kind="simple datatype")
        enumerated_datatypes = _stable_spec_union(enumerated_datatypes, module.enumerated_datatypes, kind="enumerated datatype")
        array_datatypes = _stable_spec_union(array_datatypes, module.array_datatypes, kind="array datatype")
        fixed_record_datatypes = _stable_spec_union(fixed_record_datatypes, module.fixed_record_datatypes, kind="fixed record datatype")
        variant_record_datatypes = _stable_spec_union(variant_record_datatypes, module.variant_record_datatypes, kind="variant record datatype")
        for category, metadata in dict(module.tag_representations).items():
            tag_representations.setdefault(category, dict(metadata))
        transportation_names.update(module.transportation_names)
        for name, value in dict(module.update_rates).items():
            update_rates.setdefault(name, value)
        for label, metadata in dict(module.synchronization_points).items():
            synchronization_points.setdefault(label, dict(metadata))
        for name, value in dict(module.switch_settings).items():
            switch_settings.setdefault(name, value)
        for note in module.notes:
            if note and note not in notes:
                notes.append(note)

        for spec in module.object_classes:
            existing = objects.get(spec.full_name)
            if existing is None:
                objects[spec.full_name] = spec
            else:
                if existing.parent_name and spec.parent_name and existing.parent_name != spec.parent_name:
                    raise FOMMergeError(
                        f"Object class {spec.full_name!r} has conflicting superclasses: {existing.parent_name!r} vs {spec.parent_name!r}"
                    )
                objects[spec.full_name] = ObjectClassSpec(
                    spec.full_name,
                    _stable_union(existing.attributes, spec.attributes),
                    existing.parent_name or spec.parent_name,
                    _stable_union(existing.declared_attributes, spec.declared_attributes),
                    _stable_mapping_union(existing.attribute_datatypes, spec.attribute_datatypes),
                    _stable_mapping_union(existing.attribute_transportations, spec.attribute_transportations),
                    _stable_mapping_union(existing.attribute_update_rates, spec.attribute_update_rates),
                )

        for spec in module.interaction_classes:
            existing = interactions.get(spec.full_name)
            if existing is None:
                interactions[spec.full_name] = spec
            else:
                if existing.parent_name and spec.parent_name and existing.parent_name != spec.parent_name:
                    raise FOMMergeError(
                        f"Interaction class {spec.full_name!r} has conflicting superclasses: {existing.parent_name!r} vs {spec.parent_name!r}"
                    )
                interactions[spec.full_name] = InteractionClassSpec(
                    spec.full_name,
                    _stable_union(existing.parameters, spec.parameters),
                    existing.parent_name or spec.parent_name,
                    _stable_union(existing.declared_parameters, spec.declared_parameters),
                    _stable_mapping_union(existing.parameter_datatypes, spec.parameter_datatypes),
                    existing.transportation or spec.transportation,
                )

    unique_time_impls = {name for name in time_impls if name}
    if len(unique_time_impls) > 1:
        raise FOMMergeError(f"Conflicting logical time implementations in FOM modules: {sorted(unique_time_impls)}")

    return FOMCatalog(
        modules=ordered_modules,
        mim_module=mim_module,
        object_classes=dict(sorted(objects.items())),
        interaction_classes=dict(sorted(interactions.items())),
        dimensions=frozenset(dimensions),
        datatype_names=frozenset(datatype_names),
        basic_datatypes=dict(sorted(basic_datatypes.items())),
        simple_datatypes=dict(sorted(simple_datatypes.items())),
        enumerated_datatypes=dict(sorted(enumerated_datatypes.items())),
        array_datatypes=dict(sorted(array_datatypes.items())),
        fixed_record_datatypes=dict(sorted(fixed_record_datatypes.items())),
        variant_record_datatypes=dict(sorted(variant_record_datatypes.items())),
        tag_representations={key: dict(sorted(value.items())) for key, value in sorted(tag_representations.items())},
        transportation_names=frozenset(transportation_names),
        update_rates=dict(sorted(update_rates.items())),
        synchronization_points={key: dict(sorted(value.items())) for key, value in sorted(synchronization_points.items())},
        switch_settings=dict(sorted(switch_settings.items())),
        notes=tuple(notes),
        logical_time_implementation=next(iter(unique_time_impls), None),
    )
