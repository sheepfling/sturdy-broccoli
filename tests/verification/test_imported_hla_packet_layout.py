from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_ROOT = REPO_ROOT / "requirements"
IMPORT_ROOT = REQUIREMENTS_ROOT / "imports" / "hla_1516_requirements_codebase_packet_v1_0"


def test_requirements_directory_exposes_canonical_packet_facing_layout():
    latest = REQUIREMENTS_ROOT / "latest"
    catalogs = REQUIREMENTS_ROOT / "catalogs"
    history = REQUIREMENTS_ROOT / "history"
    dashboards = REQUIREMENTS_ROOT / "dashboards"
    manifests = REQUIREMENTS_ROOT / "manifests"

    assert latest.is_symlink()
    assert catalogs.is_symlink()
    assert history.is_symlink()
    assert dashboards.is_dir()
    assert manifests.is_dir()

    assert latest.resolve() == (IMPORT_ROOT / "latest").resolve()
    assert catalogs.resolve() == (IMPORT_ROOT / "catalogs").resolve()
    assert history.resolve() == (IMPORT_ROOT / "history").resolve()


def test_requirements_canonical_packet_views_point_at_expected_assets():
    assert (REQUIREMENTS_ROOT / "latest" / "hla_1516_requirements_master_v1_0.csv").exists()
    assert (REQUIREMENTS_ROOT / "latest" / "hla_1516_verification_matrix_v1_0.csv").exists()
    assert (REQUIREMENTS_ROOT / "latest" / "hla_1516_clause_tracker_v1_0.csv").exists()
    assert (REQUIREMENTS_ROOT / "latest" / "hla_1516_requirements_summary_v1_0.csv").exists()
    assert (REQUIREMENTS_ROOT / "catalogs" / "hla_1516_api_service_catalog_v0_3.csv").exists()
    assert (REQUIREMENTS_ROOT / "catalogs" / "hla_1516_mim_catalog_v0_3.csv").exists()
    assert (REQUIREMENTS_ROOT / "catalogs" / "hla_1516_xsd_catalog_v0_3.csv").exists()
    assert (REQUIREMENTS_ROOT / "catalogs" / "hla_1516_wsdl_catalog_v0_3.csv").exists()
    assert (REQUIREMENTS_ROOT / "history" / "hla_1516_requirements_master_v0_1.csv").exists()

    manifest_link = REQUIREMENTS_ROOT / "manifests" / "hla_1516_requirements_codebase_packet_v1_0_MANIFEST.json"
    dashboard_link = REQUIREMENTS_ROOT / "dashboards" / "hla_1516_requirements_dashboard_v1_0_preview.png"

    assert manifest_link.is_symlink()
    assert dashboard_link.is_symlink()
    assert manifest_link.resolve() == (IMPORT_ROOT / "MANIFEST.json").resolve()
    assert dashboard_link.resolve() == (
        IMPORT_ROOT / "latest" / "hla_1516_requirements_dashboard_v1_0_preview.png"
    ).resolve()
