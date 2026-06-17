from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def work_packet_root() -> Path:
    return Path(__file__).resolve().parents[2]
####


@pytest.fixture
def smoke_fom_path(work_packet_root: Path) -> Path:
    return work_packet_root / '05-example-foms' / 'EncodingSmokeTest-2025.xml'
####


@pytest.fixture
def primitive_vectors_path(work_packet_root: Path) -> Path:
    return work_packet_root / '04-test-data' / 'primitive_vectors.yaml'
####


@pytest.fixture
def auth_vectors_path(work_packet_root: Path) -> Path:
    return work_packet_root / '04-test-data' / 'auth_vectors.yaml'
####


@pytest.fixture
def fake_runtime_config() -> dict[str, Any]:
    return {
        'edition': '1516-2025',
        'provider': 'fake',
        'transport': 'inproc',
    }
####
