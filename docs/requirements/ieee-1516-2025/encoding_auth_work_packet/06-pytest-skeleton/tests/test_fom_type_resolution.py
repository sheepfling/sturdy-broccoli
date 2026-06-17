from __future__ import annotations

from pathlib import Path

from hla_x.runtime import HlaRuntimeFactory


def test_fom_type_repository_resolves_all_smoke_types(
    fake_runtime_config: dict[str, object],
    smoke_fom_path: Path,
) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    encoding = factory.create_encoding_context(fom_modules=[smoke_fom_path])
    repository = encoding.type_repository

    for type_name in [
        'TrackId',
        'Latitude',
        'SensorKind',
        'TrackHistory',
        'FixedFourTrackIds',
        'Position',
        'TrackState',
        'SensorContact',
    ]:
        assert repository.resolve(type_name).name == type_name
    ####
####


def test_fixed_record_field_order_is_preserved(
    fake_runtime_config: dict[str, object],
    smoke_fom_path: Path,
) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    repository = factory.create_encoding_context(fom_modules=[smoke_fom_path]).type_repository

    position = repository.resolve('Position')

    assert [field.name for field in position.fields] == ['Latitude', 'Longitude', 'Altitude']
####


def test_variant_record_uses_discriminant(
    fake_runtime_config: dict[str, object],
    smoke_fom_path: Path,
) -> None:
    factory = HlaRuntimeFactory.select(**fake_runtime_config)
    repository = factory.create_encoding_context(fom_modules=[smoke_fom_path]).type_repository

    contact = repository.resolve('SensorContact')

    assert contact.discriminant == 'Kind'
    assert contact.discriminant_type.name == 'SensorKind'
    assert 'Radar' in contact.alternatives
    assert 'HLAother' in contact.alternatives
####
