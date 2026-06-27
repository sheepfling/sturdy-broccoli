from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import tomllib
from compliance_helpers import (
    IEEE_1516_1_2010,
    clause_summary_counts,
    compliance_section_key,
)
from hla.verification.repo_internal.verification.backend_compliance_discovery import (
    build_backend_compliance_catalog,
    build_discovery_payload,
    build_vendor_discovery_backlog,
    render_backend_compliance_catalog_text,
    write_vendor_discovery_backlog_artifacts,
)

ALLOWED_DISPOSITIONS = {
    "verified",
    "blocked",
    "vendor-divergent",
    "not-applicable",
    "classification-required",
    "not-yet-tested",
}


def _source_checkout_env(project_root: Path) -> dict[str, str]:
    data = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    roots = data["tool"]["pytest"]["ini_options"]["pythonpath"]
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(project_root / root) for root in roots)
    return env


def _requirement_disposition_artifact_paths(project_root: Path) -> list[Path]:
    return sorted((project_root / "analysis" / "compliance").glob("*_requirement_disposition.json"))


def _catalog_summary_key_for_artifact(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_summary"


def _catalog_row_count_key_for_artifact(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_row_count"


def _row_disposition_keys(payload: dict[str, object]) -> set[str]:
    rows = payload["rows"]  # type: ignore[index]
    return {
        key
        for row in rows  # type: ignore[assignment]
        for key in row
        if key == "runtime_disposition" or key.endswith("_disposition")
    }


def test_backend_compliance_catalog_exposes_primary_backend_views():
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)

    assert catalog["summary"]["backend_count"] >= 6
    assert "analysis/compliance/core_backend_matrix.json" in catalog["source_artifacts"]
    assert "analysis/compliance/python_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/certi_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/certi-native_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/certi-jpype_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/certi-py4j_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/portico_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/portico-jpype_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/portico-py4j_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/pitch_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/pitch-jpype_requirement_disposition.json" in catalog["source_artifacts"]
    assert "analysis/compliance/pitch-py4j_requirement_disposition.json" in catalog["source_artifacts"]
    assert catalog["operator_entrypoints"]["discover_command"] == "./tools/compliance discover"

    backends = {row["backend_id"]: row for row in catalog["backends"]}
    assert "python-inmemory" in backends
    assert "certi-native" in backends
    assert "pitch-jpype" in backends

    assert "core" in backends["python-inmemory"]["matrices_present"]
    assert "section8" in backends["python-inmemory"]["matrices_present"]
    assert backends["certi-native"]["status_counts"].get("vendor-divergent", 0) >= 1
    assert any("queryGALT" in " ".join(row["section_refs"]) or row["slice_id"] == "negotiated-ownership" for row in backends["certi-native"]["notable_rows"])

    vendor_summary = catalog["requirements_vendor_summary"]
    assert vendor_summary["python_runtime_status_counts"].get("yes", 0) > 0
    assert vendor_summary["certi_runtime_status_counts"].get("partial", 0) > 0
    assert vendor_summary["python_runtime_disposition_counts"].get("verified", 0) > 0
    assert vendor_summary["certi_runtime_disposition_counts"].get("vendor-divergent", 0) > 0
    assert vendor_summary["certi_runtime_disposition_counts"].get("not-yet-tested", 0) > 0
    python_disposition = catalog["python_requirement_disposition_summary"]["disposition_counts"]
    assert python_disposition.get("verified", 0) > 0
    certi_disposition = catalog["certi_requirement_disposition_summary"]["disposition_counts"]
    assert certi_disposition.get("verified", 0) > 0
    assert certi_disposition.get("classification-required", 0) > 0
    certi_native_disposition = catalog["certi_native_requirement_disposition_summary"]["disposition_counts"]
    certi_jpype_disposition = catalog["certi_jpype_requirement_disposition_summary"]["disposition_counts"]
    certi_py4j_disposition = catalog["certi_py4j_requirement_disposition_summary"]["disposition_counts"]
    assert certi_native_disposition == certi_disposition
    assert certi_jpype_disposition == certi_disposition
    assert certi_py4j_disposition == certi_disposition
    portico_disposition = catalog["portico_requirement_disposition_summary"]["disposition_counts"]
    assert portico_disposition.get("classification-required", 0) > 0
    portico_jpype_disposition = catalog["portico_jpype_requirement_disposition_summary"]["disposition_counts"]
    portico_py4j_disposition = catalog["portico_py4j_requirement_disposition_summary"]["disposition_counts"]
    assert portico_jpype_disposition == portico_disposition
    assert portico_py4j_disposition == portico_disposition
    assert vendor_summary["pitch_runtime_disposition_counts"].get("verified", 0) > 0
    assert vendor_summary["pitch_runtime_disposition_counts"].get("blocked", 0) > 0
    assert vendor_summary["pitch_jpype_runtime_disposition_counts"].get("blocked", 0) >= 2
    assert vendor_summary["pitch_py4j_runtime_disposition_counts"].get("verified", 0) > 0
    pitch_disposition = catalog["pitch_requirement_disposition_summary"]["disposition_counts"]
    assert pitch_disposition.get("verified", 0) > 0
    assert pitch_disposition.get("blocked", 0) > 0
    assert pitch_disposition.get("not-applicable", 0) > 0
    assert pitch_disposition.get("classification-required", 0) > 0
    pitch_jpype_disposition = catalog["pitch_jpype_requirement_disposition_summary"]["disposition_counts"]
    assert pitch_jpype_disposition.get("verified", 0) > 0
    assert pitch_jpype_disposition.get("blocked", 0) >= 2
    pitch_py4j_disposition = catalog["pitch_py4j_requirement_disposition_summary"]["disposition_counts"]
    assert pitch_py4j_disposition.get("verified", 0) > 0
    profile_disposition = catalog["pitch_requirement_disposition_summary"]["profile_disposition_counts"]
    assert profile_disposition["pitch-jpype"].get("blocked", 0) >= 2
    assert profile_disposition["pitch-py4j"].get("verified", 0) > 0
    clause_summary = catalog["pitch_requirement_disposition_summary"]["clause_summary"]
    assert clause_summary_counts(clause_summary, IEEE_1516_1_2010, "4").get("not-yet-tested", 0) == 0
    assert clause_summary_counts(clause_summary, IEEE_1516_1_2010, "6").get("not-yet-tested", 0) == 3
    assert clause_summary_counts(clause_summary, IEEE_1516_1_2010, "8")["vendor-divergent"] > 0
    profile_clause_summary = catalog["pitch_requirement_disposition_summary"]["profile_clause_summary"]
    assert clause_summary_counts(profile_clause_summary["pitch-jpype"], IEEE_1516_1_2010, "4")["blocked"] >= 2
    assert clause_summary_counts(profile_clause_summary["pitch-py4j"], IEEE_1516_1_2010, "4")["verified"] >= 2
    assert "analysis/compliance/vendor_discovery_backlog.json" in catalog["source_artifacts"]


def test_discovery_script_uses_explicit_project_root_from_outside_repo(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(project_root / "scripts" / "discover_backend_compliance.py"),
            "--project-root",
            str(project_root),
            "--backend",
            "certi-native",
            "--show-backlog",
            "--priority",
            "P1",
        ],
        cwd=tmp_path,
        env=_source_checkout_env(project_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Backend Compliance Discovery" in result.stdout
    assert "P1 certi-native" in result.stdout


def test_backend_compliance_catalog_text_render_supports_filtering():
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)

    rendered = render_backend_compliance_catalog_text(catalog, backend_filter="certi-native")
    assert "Backend Compliance Discovery" in rendered
    assert "certi-native" in rendered
    assert "python-inmemory" not in rendered
    assert "python_requirement_dispositions:" in rendered
    assert "certi_requirement_dispositions:" in rendered
    assert "certi-native_requirement_dispositions:" in rendered
    assert "certi-jpype_requirement_dispositions:" in rendered
    assert "certi-py4j_requirement_dispositions:" in rendered
    assert "portico-jpype_requirement_dispositions:" in rendered
    assert "portico-py4j_requirement_dispositions:" in rendered
    assert "pitch_requirement_dispositions:" in rendered
    assert rendered.count("pitch-jpype_requirement_dispositions:") == 1
    assert "pitch-py4j_clause4_requirement_dispositions:" in rendered
    assert rendered.count("pitch-py4j_requirement_dispositions:") == 1
    assert "Refresh: ./tools/compliance generate" in rendered


def test_pitch_requirement_disposition_markdown_surfaces_profile_split_rows():
    project_root = Path(__file__).resolve().parents[2]
    rendered = (project_root / "analysis" / "compliance" / "pitch_requirement_disposition.md").read_text(encoding="utf-8")

    assert "## Profile Summary" in rendered
    assert "Vendor divergent" in rendered
    assert "## Profile Clause Summary" in rendered
    assert "### pitch-jpype" in rendered
    assert "## Backend-Split Rows" in rendered
    assert "| pitch-jpype |" in rendered
    assert "| pitch-py4j |" in rendered
    assert "HLA1516.1-FM-4.1.5-001" not in rendered
    assert "| blocked | blocked | blocked |" not in rendered


def test_generated_requirement_disposition_artifacts_use_only_allowed_statuses() -> None:
    project_root = Path(__file__).resolve().parents[2]

    for path in _requirement_disposition_artifact_paths(project_root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        disposition_keys = _row_disposition_keys(payload)
        assert disposition_keys, path.name

        for row in payload["rows"]:
            for key in disposition_keys:
                value = row.get(key)
                assert value in ALLOWED_DISPOSITIONS, (path.name, row.get("requirement_id") or row.get("matrix_id"), key, value)

        summary = payload["summary"]
        assert set(summary["disposition_counts"]).issubset(ALLOWED_DISPOSITIONS), path.name
        assert sum(summary["disposition_counts"].values()) == summary["row_count"], path.name

        profile_counts = summary.get("profile_disposition_counts")
        if profile_counts is not None:
            for profile, counts in profile_counts.items():
                assert set(counts).issubset(ALLOWED_DISPOSITIONS), (path.name, profile)
                assert sum(counts.values()) == summary["row_count"], (path.name, profile)


def test_generated_requirement_disposition_summaries_match_row_level_counts() -> None:
    project_root = Path(__file__).resolve().parents[2]

    for path in _requirement_disposition_artifact_paths(project_root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        disposition_keys = _row_disposition_keys(payload)
        summary = payload["summary"]

        if disposition_keys == {"runtime_disposition"}:
            observed: dict[str, int] = {}
            for row in payload["rows"]:
                value = row["runtime_disposition"]
                observed[value] = observed.get(value, 0) + 1
            assert observed == summary["disposition_counts"], path.name
            continue

        assert path.name == "pitch_requirement_disposition.json", path.name
        observed_family: dict[str, int] = {}
        observed_profiles: dict[str, dict[str, int]] = {
            "pitch-jpype": {},
            "pitch-py4j": {},
        }
        profile_key_map = {
            "pitch-jpype": "pitch_jpype_disposition",
            "pitch-py4j": "pitch_py4j_disposition",
        }
        for row in payload["rows"]:
            family_value = row["pitch_disposition"]
            observed_family[family_value] = observed_family.get(family_value, 0) + 1
            for profile, key in profile_key_map.items():
                value = row[key]
                observed_profiles[profile][value] = observed_profiles[profile].get(value, 0) + 1

        assert observed_family == summary["disposition_counts"]
        assert observed_profiles == summary["profile_disposition_counts"]


def test_backend_compliance_catalog_mirrors_generated_requirement_disposition_packet_summaries() -> None:
    project_root = Path(__file__).resolve().parents[2]
    catalog = build_backend_compliance_catalog(project_root)

    for path in _requirement_disposition_artifact_paths(project_root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        source_artifact = f"analysis/compliance/{path.name}"
        summary_key = _catalog_summary_key_for_artifact(path)
        row_count_key = _catalog_row_count_key_for_artifact(path)

        assert source_artifact in catalog["source_artifacts"], path.name
        assert source_artifact in catalog["operator_entrypoints"]["primary_artifacts"], path.name
        assert catalog[summary_key] == payload["summary"], path.name
        assert catalog["summary"][row_count_key] == payload["summary"]["row_count"], path.name


def test_pitch_profile_requirement_disposition_artifacts_surface_profile_specific_rows():
    project_root = Path(__file__).resolve().parents[2]
    jpype = json.loads((project_root / "analysis" / "compliance" / "pitch-jpype_requirement_disposition.json").read_text(encoding="utf-8"))
    py4j = json.loads((project_root / "analysis" / "compliance" / "pitch-py4j_requirement_disposition.json").read_text(encoding="utf-8"))

    assert jpype["summary"]["backend"] == "pitch-jpype"
    assert py4j["summary"]["backend"] == "pitch-py4j"
    assert jpype["summary"]["disposition_counts"].get("blocked", 0) >= 2
    assert py4j["summary"]["disposition_counts"].get("verified", 0) > 0

    jpype_rows = {row["requirement_id"] or row["matrix_id"]: row for row in jpype["rows"]}
    py4j_rows = {row["requirement_id"] or row["matrix_id"]: row for row in py4j["rows"]}

    assert jpype_rows["HLA1516.1-FM-4.1.5-001"]["runtime_disposition"] == "blocked"
    assert py4j_rows["HLA1516.1-FM-4.1.5-001"]["runtime_disposition"] == "blocked"
    assert (
        "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md"
        in jpype_rows["HLA1516.1-FM-4.1.5-001"]["evidence_refs"]
    )
    assert (
        "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_lost_federate_mom_scenario"
        in py4j_rows["HLA1516.1-FM-4.1.5-001"]["evidence_refs"]
    )
    for payload in (jpype_rows["HLA1516.1-FM-4.1.5-001"], py4j_rows["HLA1516.1-FM-4.1.5-001"]):
        assert "artifacts/preflight_artifacts/pitch-preflight.json" in payload["evidence_refs"]
        assert (
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json"
            in payload["evidence_refs"]
        )
        assert (
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md"
            in payload["evidence_refs"]
        )


def test_pitch_clause4_profile_residual_frontier_is_exact():
    project_root = Path(__file__).resolve().parents[2]
    expected_residuals = {
        "HLA1516.1-FM-001": "not-applicable",
        "HLA1516.1-FM-4.1.5-001": "blocked",
        "HLA1516.1-FM-4.1.5-002": "blocked",
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM": "vendor-divergent",
        "HLA1516.1-FM-4.5-EXC-001": "vendor-divergent",
        "HLA1516.1-FM-4.9-EXC-001": "vendor-divergent",
    }

    for backend in ("pitch-jpype", "pitch-py4j"):
        payload = json.loads(
            (project_root / "analysis" / "compliance" / f"{backend}_requirement_disposition.json").read_text(encoding="utf-8")
        )
        residuals = {
            row["requirement_id"]: row["runtime_disposition"]
            for row in payload["rows"]
            if row.get("document") == "IEEE 1516.1-2010 (2010 edition)"
            and row.get("clause_root") == "4"
            and row.get("requirement_id")
            and row["runtime_disposition"] != "verified"
        }
        assert residuals == expected_residuals, backend


def test_pitch_clause4_lost_federate_rows_pin_current_blocked_operator_evidence() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}

    for requirement_id in (
        "HLA1516.1-FM-4.1.5-001",
        "HLA1516.1-FM-4.1.5-002",
    ):
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "blocked"
        assert row["pitch_jpype_disposition"] == "blocked"
        assert row["pitch_py4j_disposition"] == "blocked"
        assert "A shared lost-federate MOM scenario now exists" in row["notes"]
        assert "The canonical `./tools/pitch lost-federate-probe` lane currently stops at preflight on this surface" in row["notes"]
        assert "Docker is unreachable and the required CRC/FedPro loopback ports are blocked" in row["notes"]
        assert "the JPype path auto-resumed its dropped session and the Py4J path did not surface the report" in row["notes"]
        assert "Canonical status stays partial because the runtime split is mixed" in row["notes"]
        assert "hla1516_1_priority_backend_resolution.csv" in row["notes"]
        assert "artifacts/preflight_artifacts/pitch-preflight.json" in row["evidence_refs"]
        assert (
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json"
            in row["evidence_refs"]
        )
        assert (
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md"
            in row["evidence_refs"]
        )


def test_portico_requirement_disposition_artifact_is_explicitly_generated():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "portico_requirement_disposition.json").read_text(encoding="utf-8"))

    assert payload["summary"]["backend"] == "portico"
    assert payload["summary"]["disposition_counts"].get("classification-required", 0) > 0

    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    assert rows["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]["runtime_disposition"] == "classification-required"
    assert rows["REQ-RTI-OM-6_10-updateAttributeValues"]["runtime_disposition"] == "classification-required"


def test_certi_profile_requirement_disposition_artifacts_are_generated_from_family_projection():
    project_root = Path(__file__).resolve().parents[2]
    family = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    native = json.loads((project_root / "analysis" / "compliance" / "certi-native_requirement_disposition.json").read_text(encoding="utf-8"))
    jpype = json.loads((project_root / "analysis" / "compliance" / "certi-jpype_requirement_disposition.json").read_text(encoding="utf-8"))
    py4j = json.loads((project_root / "analysis" / "compliance" / "certi-py4j_requirement_disposition.json").read_text(encoding="utf-8"))

    assert native["summary"]["backend"] == "certi-native"
    assert jpype["summary"]["backend"] == "certi-jpype"
    assert py4j["summary"]["backend"] == "certi-py4j"

    family_counts = family["summary"]["disposition_counts"]
    assert native["summary"]["disposition_counts"] == family_counts
    assert jpype["summary"]["disposition_counts"] == family_counts
    assert py4j["summary"]["disposition_counts"] == family_counts

    family_rows = {row["requirement_id"] or row["matrix_id"]: row for row in family["rows"]}
    native_rows = {row["requirement_id"] or row["matrix_id"]: row for row in native["rows"]}
    jpype_rows = {row["requirement_id"] or row["matrix_id"]: row for row in jpype["rows"]}
    py4j_rows = {row["requirement_id"] or row["matrix_id"]: row for row in py4j["rows"]}

    requirement_id = "REQ-RTI-FM-4_16-requestFederationSave"
    assert native_rows[requirement_id]["runtime_disposition"] == family_rows[requirement_id]["runtime_disposition"]
    assert jpype_rows[requirement_id]["runtime_disposition"] == family_rows[requirement_id]["runtime_disposition"]
    assert py4j_rows[requirement_id]["runtime_disposition"] == family_rows[requirement_id]["runtime_disposition"]


def test_portico_profile_requirement_disposition_artifacts_are_generated_from_family_projection():
    project_root = Path(__file__).resolve().parents[2]
    family = json.loads((project_root / "analysis" / "compliance" / "portico_requirement_disposition.json").read_text(encoding="utf-8"))
    jpype = json.loads((project_root / "analysis" / "compliance" / "portico-jpype_requirement_disposition.json").read_text(encoding="utf-8"))
    py4j = json.loads((project_root / "analysis" / "compliance" / "portico-py4j_requirement_disposition.json").read_text(encoding="utf-8"))

    assert jpype["summary"]["backend"] == "portico-jpype"
    assert py4j["summary"]["backend"] == "portico-py4j"
    family_counts = family["summary"]["disposition_counts"]
    assert jpype["summary"]["disposition_counts"] == family_counts
    assert py4j["summary"]["disposition_counts"] == family_counts

    family_rows = {row["requirement_id"] or row["matrix_id"]: row for row in family["rows"]}
    jpype_rows = {row["requirement_id"] or row["matrix_id"]: row for row in jpype["rows"]}
    py4j_rows = {row["requirement_id"] or row["matrix_id"]: row for row in py4j["rows"]}

    requirement_id = "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"
    assert jpype_rows[requirement_id]["runtime_disposition"] == family_rows[requirement_id]["runtime_disposition"]
    assert py4j_rows[requirement_id]["runtime_disposition"] == family_rows[requirement_id]["runtime_disposition"]


def test_certi_requirement_disposition_tracks_shared_save_restore_evidence():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}

    for requirement_id in {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "HLA1516.1-FM-4.16-001",
        "HLA1516.1-FM-4.17-001",
        "HLA1516.1-FM-4.22-001",
        "HLA1516.1-FM-4.24-001",
        "HLA1516.1-FM-4.27-001",
        "HLA1516.1-FM-4.31-001",
    }:
        assert rows[requirement_id]["runtime_disposition"] == "verified"

    for requirement_id in {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
    }:
        refs = rows[requirement_id]["evidence_refs"]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario"
            in refs
        )
        assert "tests/vendors/test_real_vendor_runtime_smoke.py::test_certi_real_save_restore_smoke" in refs
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in rows[requirement_id]["notes"].lower()


def test_certi_requirement_disposition_tracks_shared_synchronization_evidence():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}

    for requirement_id in {
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded",
        "REQ-FED-FM-4_13-announceSynchronizationPoint",
        "REQ-RTI-FM-4_14-synchronizationPointAchieved",
        "REQ-FED-FM-4_15-federationSynchronized",
    }:
        refs = rows[requirement_id]["evidence_refs"]
        assert rows[requirement_id]["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_synchronization_matrix" in refs
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in rows[requirement_id]["notes"].lower()


def test_certi_requirement_disposition_tracks_clause6_exchange_evidence():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}

    expected_ids = {
        "REQ-RTI-OM-6_10-updateAttributeValues",
        "REQ-RTI-OM-6_12-sendInteraction",
        "HLA1516.1-OM-6.10-001",
        "HLA1516.1-OM-6.10-002",
        "HLA1516.1-OM-6.10-003",
        "HLA1516.1-OM-6.10-004",
        "HLA1516.1-OM-6.10-005",
        "HLA1516.1-OM-6.12-001",
        "HLA1516.1-OM-6.12-002",
        "HLA1516.1-OM-6.12-003",
        "HLA1516.1-OM-6.12-004",
        "HLA1516.1-OM-6.12-005",
    }

    verified_clause6_ids = {
        row["requirement_id"] or row["matrix_id"]
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)"
        and row.get("clause_root") == "6"
        and row.get("runtime_disposition") == "verified"
    }
    assert verified_clause6_ids == expected_ids

    for requirement_id in expected_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_exchange_matrix.py::test_certi_backend_exchange_matrix" in refs
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in row["notes"].lower()


def test_certi_requirement_disposition_tracks_clause7_ownership_evidence():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}

    expected_ids = {
        "REQ-FED-OWN-7_11-requestAttributeOwnershipRelease",
        "REQ-RTI-OWN-7_17-queryAttributeOwnership",
        "REQ-FED-OWN-7_18-attributeIsNotOwned",
        "REQ-FED-OWN-7_18-attributeIsOwnedByRTI",
        "REQ-FED-OWN-7_18-informAttributeOwnership",
        "REQ-RTI-OWN-7_19-isAttributeOwnedByFederate",
        "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable",
        "HLA1516.1-OWN-7.11-001",
        "HLA1516.1-OWN-7.2-001",
        "HLA1516.1-OWN-7.9-001",
        "HLA1516.1-OWN-7.9-002",
    }

    verified_clause7_ids = {
        row["requirement_id"] or row["matrix_id"]
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)"
        and row.get("clause_root") == "7"
        and row.get("runtime_disposition") == "verified"
    }
    assert verified_clause7_ids == expected_ids

    for requirement_id in expected_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_ownership_matrix.py::test_certi_backend_ownership_matrix" in refs
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in row["notes"].lower()


def test_certi_requirement_disposition_tracks_clause8_shared_harness_subset():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "8") == {
        "classification-required": 17,
        "not-applicable": 2,
        "total": 61,
        "vendor-divergent": 5,
        "verified": 37,
    }

    state_service_ids = {
        "REQ-RTI-TM-8_2-enableTimeRegulation",
        "REQ-FED-TM-8_3-timeRegulationEnabled",
        "REQ-RTI-TM-8_5-enableTimeConstrained",
        "REQ-FED-TM-8_6-timeConstrainedEnabled",
        "HLA1516.1-TM-8.2-001",
        "HLA1516.1-TM-8.2-002",
        "HLA1516.1-TM-8.5-001",
        "HLA1516.1-TM-8.5-002",
    }
    ordering_ids = {
        "REQ-RTI-TM-8_8-timeAdvanceRequest",
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "HLA1516.1-TM-8.8-001",
        "HLA1516.1-TM-8.8-002",
        "HLA1516.1-TM-8.10-001",
    }
    available_flush_ids = {
        "REQ-RTI-TM-8_9-timeAdvanceRequestAvailable",
        "REQ-RTI-TM-8_12-flushQueueRequest",
        "REQ-FED-TM-8_13-timeAdvanceGrant",
        "HLA1516.1-TM-8.12-001",
    }
    available_retraction_ids = {
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
    }
    logical_time_ids = {
        "REQ-RTI-TM-8_17-queryLogicalTime",
        "HLA1516.1-TM-8.17-001",
    }
    state_toggle_ids = {
        "REQ-RTI-TM-8_14-enableAsynchronousDelivery",
        "REQ-RTI-TM-8_15-disableAsynchronousDelivery",
        "REQ-RTI-TM-8_19-modifyLookahead",
        "REQ-RTI-TM-8_20-queryLookahead",
        "REQ-RTI-TM-8_4-disableTimeRegulation",
        "REQ-RTI-TM-8_7-disableTimeConstrained",
        "HLA1516.1-TM-8.19-001",
        "HLA1516.1-TM-8.4-001",
        "HLA1516.1-TM-8.7-001",
    }
    request_retraction_ids = {
        "REQ-RTI-TM-8_21-retract",
        "REQ-FED-TM-8_22-requestRetraction",
        "HLA1516.1-TM-8.21-001",
    }
    order_override_ids = {
        "REQ-RTI-TM-8_24-changeInteractionOrderType",
        "HLA1516.1-TM-8.1.2-003",
    }
    time_bound_vendor_divergent_ids = {
        "REQ-RTI-TM-8_16-queryGALT",
        "REQ-RTI-TM-8_18-queryLITS",
        "HLA1516.1-TM-8.16-001",
        "HLA1516.1-TM-8.18-001",
    }
    order_override_vendor_divergent_ids = {
        "REQ-RTI-TM-8_23-changeAttributeOrderType",
    }
    duplicate_enable_rejection_ids = {
        "HLA1516.1-TM-8.2-003",
        "HLA1516.1-TM-8.5-003",
    }
    tar_boundary_ids = {
        "HLA1516.1-TM-8.8-003",
    }

    for requirement_id in state_service_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_state_services_matrix" in refs

    for requirement_id in ordering_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_ordering_and_query_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_ordering_and_query_matrix" in refs

    for requirement_id in available_flush_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_flush_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_available_and_flush_matrix" in refs

    for requirement_id in available_retraction_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_retraction_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_available_and_retraction_matrix" in refs

    for requirement_id in logical_time_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_logical_time_query_matrix" in refs

    for requirement_id in state_toggle_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_state_toggle_services_matrix" in refs

    for requirement_id in request_retraction_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_request_retraction_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_request_retraction_matrix" in refs

    for requirement_id in order_override_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_order_override_matrix" in refs

    for requirement_id in time_bound_vendor_divergent_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_time_bound_query_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_time_bound_query_matrix" in refs

    for requirement_id in order_override_vendor_divergent_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case"
            in refs
        )
        assert "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_order_override_matrix" in refs

    for requirement_id in duplicate_enable_rejection_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_duplicate_enable_rejection_case"
            in refs
        )
        assert (
            "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_duplicate_enable_rejection_matrix"
            in refs
        )

    for requirement_id in tar_boundary_ids:
        row = rows[requirement_id]
        refs = row["evidence_refs"]
        assert row["runtime_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_tar_galt_boundary_case"
            in refs
        )
        assert (
            "tests/vendors/test_certi_real_backend_time_matrix.py::test_certi_backend_section8_tar_galt_boundary_matrix"
            in refs
        )

    for requirement_id in state_service_ids | ordering_ids | available_flush_ids:
        refs = rows[requirement_id]["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in rows[requirement_id]["notes"].lower()

    for requirement_id in (
        state_service_ids
        | ordering_ids
        | available_flush_ids
        | available_retraction_ids
        | logical_time_ids
        | state_toggle_ids
        | request_retraction_ids
        | order_override_ids
        | time_bound_vendor_divergent_ids
        | order_override_vendor_divergent_ids
        | duplicate_enable_rejection_ids
        | tar_boundary_ids
    ):
        refs = rows[requirement_id]["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs)
        assert not any("pitch" in ref.lower() for ref in refs)
        assert "pitch" not in rows[requirement_id]["notes"].lower()


def test_requirements_matrix_projects_certi_shared_save_restore_rows_as_verified():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "requirements_matrix_2010.json").read_text(encoding="utf-8"))
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}

    assert rows["REQ-RTI-FM-4_16-requestFederationSave"]["certi_runtime_disposition"] == "verified"
    assert rows["REQ-FED-FM-4_17-initiateFederateSave"]["certi_runtime_disposition"] == "verified"
    assert rows["REQ-RTI-FM-4_24-requestFederationRestore"]["certi_runtime_disposition"] == "verified"
    assert rows["REQ-FED-FM-4_27-initiateFederateRestore"]["certi_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.16-001"]["certi_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.24-001"]["certi_runtime_disposition"] == "verified"


def test_vendor_discovery_backlog_covers_divergent_gated_matrixed_and_defended_rows():
    project_root = Path(__file__).resolve().parents[2]
    backlog = build_vendor_discovery_backlog(project_root)

    assert backlog["summary"]["row_count"] > 0
    assert backlog["summary"]["status_counts"].get("vendor-divergent", 0) > 0
    assert backlog["summary"]["status_counts"].get("blocked", 0) > 0
    assert backlog["summary"]["status_counts"].get("env-gated-positive", 0) > 0
    assert backlog["summary"]["status_counts"].get("not-yet-matrixed", 0) > 0
    assert backlog["summary"]["status_counts"].get("classification-required", 0) > 0
    assert backlog["summary"]["status_counts"].get("defended-partial", 0) > 0

    by_backend_and_target = {
        (row["backend_id"], row["requirement_id"] or compliance_section_key(row["section_ref"]), row["current_status"]): row
        for row in backlog["rows"]
    }
    assert ("certi-native", "IEEE 1516.1-2010 §7.3, IEEE 1516.1-2010 §7.15", "vendor-divergent") in by_backend_and_target
    assert ("certi-native", "IEEE 1516.1-2010 §4.25, IEEE 1516.1-2010 §4.26", "env-gated-positive") in by_backend_and_target
    assert ("pitch-jpype", "IEEE 1516.1-2010 §8.16", "not-yet-matrixed") in by_backend_and_target
    assert ("pitch-jpype", "IEEE 1516.1-2010 §4.1.5", "not-yet-matrixed") not in by_backend_and_target
    assert ("pitch-py4j", "IEEE 1516.1-2010 §4.1.5", "not-yet-matrixed") not in by_backend_and_target
    assert ("pitch-py4j", "IEEE 1516.1-2010 §4.1.5", "blocked") not in by_backend_and_target
    assert ("pitch-jpype", "HLA1516.1-FM-4.1.5-001", "blocked") in by_backend_and_target
    assert ("pitch-py4j", "HLA1516.1-FM-4.1.5-001", "blocked") in by_backend_and_target
    assert ("pitch-py4j", "HLA1516.1-FM-4.1.5-001", "verified") not in by_backend_and_target
    assert ("pitch-requirements", "REQ-RTI-FM-4_5-createFederationExecutionWithMIM", "vendor-divergent") in by_backend_and_target

    hosted_positive = [
        row for row in backlog["rows"] if row["backend_id"] == "rest-hosted-python" and row["current_status"] == "positive-path-passing"
    ]
    assert hosted_positive
    assert hosted_positive[0]["recommended_next_action"] == "widen from positive-path slice into deeper vendor matrix coverage"

    defended = [row for row in backlog["rows"] if row["current_status"] == "defended-partial"]
    assert any(row["requirement_id"] == "HLA1516.1-OM-6.1.10-001" for row in defended)
    assert backlog["rows"][0]["priority"] == "P1"


def test_pitch_requirement_disposition_tracks_lifecycle_probe_evidence():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    clause4_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "4")
    assert clause4_summary == {
        "blocked": 2,
        "not-applicable": 2,
        "total": 281,
        "vendor-divergent": 3,
        "verified": 274,
    }
    profile_summary = payload["summary"]["profile_disposition_counts"]
    assert profile_summary["pitch-jpype"].get("blocked", 0) >= 2
    assert profile_summary["pitch-py4j"].get("verified", 0) > 0
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}
    lifecycle_ids = {
        "REQ-RTI-FM-4_2-connect",
        "REQ-RTI-FM-4_3-disconnect",
        "REQ-RTI-FM-4_5-createFederationExecution",
        "REQ-RTI-FM-4_6-destroyFederationExecution",
        "REQ-RTI-FM-4_9-joinFederationExecution",
        "REQ-RTI-FM-4_10-resignFederationExecution",
    }

    for requirement_id in lifecycle_ids:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_matrix" in row["evidence_refs"]

    for requirement_id in {"REQ-RTI-FM-4_7-listFederationExecutions", "REQ-FED-FM-4_8-reportFederationExecutions"}:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_listing_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_listing_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_listing_matrix" in row["evidence_refs"]

    save_restore_time_state_row = rows["REQ-SAVE-RESTORE-001"]
    assert save_restore_time_state_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_scheduled_save_restore_time_state_scenario"
        in save_restore_time_state_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_scheduled_save_restore_time_state_matrix"
        in save_restore_time_state_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_scheduled_save_restore_time_state_matrix" in save_restore_time_state_row["evidence_refs"]

    for requirement_id in {"HLA1516.1-FM-4.1.4.2-001", "HLA1516.1-FM-4.5-MOM-001"}:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_module_visibility_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_module_visibility_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_module_visibility_matrix" in row["evidence_refs"]

    mim_row = rows["REQ-RTI-FM-4_5-createFederationExecutionWithMIM"]
    assert mim_row["pitch_disposition"] == "vendor-divergent"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario"
        in mim_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_with_mim_matrix" in mim_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_with_mim_matrix" in mim_row["evidence_refs"]

    connection_lost = rows["REQ-FED-FM-4_4-connectionLost"]
    assert connection_lost["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_connection_lost.py::run_connection_lost_callback_scenario"
        in connection_lost["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_connection_lost_callback_matrix" in connection_lost["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_connection_lost_callback_matrix" in connection_lost["evidence_refs"]

    for requirement_id in {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "blocked"
        assert row["pitch_jpype_disposition"] == "blocked"
        assert row["pitch_py4j_disposition"] == "blocked"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_external_lost_federate_observer_scenario"
            in row["pitch_jpype_evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix" in row["pitch_jpype_evidence_refs"]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_lost_federate_mom_scenario"
            in row["pitch_py4j_evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix" in row["pitch_py4j_evidence_refs"]

    for requirement_id in {
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded",
        "REQ-FED-FM-4_13-announceSynchronizationPoint",
        "REQ-RTI-FM-4_14-synchronizationPointAchieved",
        "REQ-FED-FM-4_15-federationSynchronized",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix" in row["evidence_refs"]

    failure_row = rows["REQ-FED-FM-4_12-synchronizationPointRegistrationFailed"]
    assert failure_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_registration_failure_scenario"
        in failure_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix"
        in failure_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix" in failure_row["evidence_refs"]

    sync_clause4_pairs = {
        "HLA1516.1-FM-4.11-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.11-CB-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_registration_failure_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix",
        ),
        "HLA1516.1-FM-4.11-EXC-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_registration_failure_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_registration_failure_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_registration_failure_matrix",
        ),
        "HLA1516.1-FM-4.13-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.14-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.14-EXC-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_multiple_synchronization_points_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_multiple_synchronization_points_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multiple_synchronization_points_matrix",
        ),
        "HLA1516.1-FM-4.15-001": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
        "HLA1516.1-FM-4.15-002": (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix",
        ),
    }

    for requirement_id, refs in sync_clause4_pairs.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for ref in refs:
            assert ref in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-FM-4.15-001",
        "HLA1516.1-FM-4.15-002",
        "HLA1516.1-FM-4.15-CB-001",
        "HLA1516.1-FM-4.15-EFF-001",
        "HLA1516.1-FM-4.15-EXC-001",
        "HLA1516.1-FM-4.15-MOM-001",
        "HLA1516.1-FM-4.15-PRE-001",
        "HLA1516.1-FM-4.15-SIG-001",
        "HLA1516.1-FM-4.15-TEST-001",
    }:
        row = rows[requirement_id]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_sync.py::run_failed_federate_synchronization_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_failed_federate_synchronization_matrix"
            in row["evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_failed_federate_synchronization_matrix" in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-FM-4.2-EXC-001",
        "HLA1516.1-FM-4.2-PRE-001",
        "HLA1516.1-FM-4.3-EXC-001",
        "HLA1516.1-FM-4.6-EXC-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_negative_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_negative_matrix"
            in row["evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_negative_matrix" in row["evidence_refs"]

    late_join_row = rows["HLA1516.1-FM-4.9-CB-001"]
    assert late_join_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_late_join_synchronization_scenario"
        in late_join_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_late_join_synchronization_matrix"
        in late_join_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_late_join_synchronization_matrix" in late_join_row["evidence_refs"]

    multi_sync_row = rows["HLA1516.1-FM-4.1.3-001"]
    assert multi_sync_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_multiple_synchronization_points_scenario"
        in multi_sync_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_multiple_synchronization_points_matrix"
        in multi_sync_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multiple_synchronization_points_matrix" in multi_sync_row["evidence_refs"]

    save_restore_pairs = {
        "REQ-RTI-FM-4_16-requestFederationSave": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_17-initiateFederateSave": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-RTI-FM-4_18-federateSaveBegun": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-RTI-FM-4_19-federateSaveComplete": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_20-federationSaved": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-RTI-FM-4_22-queryFederationSaveStatus": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_23-federationSaveStatusResponse": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-RTI-FM-4_24-requestFederationRestore": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_26-federationRestoreBegun": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_27-initiateFederateRestore": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-RTI-FM-4_28-federateRestoreComplete": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_29-federationRestored": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "REQ-FED-FM-4_32-federationRestoreStatusResponse": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
    }
    for requirement_id, refs in save_restore_pairs.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for ref in refs:
            assert ref in row["evidence_refs"]


def test_pitch_clause4_1516_1_dispositions_are_fully_classified_and_harness_backed():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "4"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}
    by_requirement_id = rows

    assert len(raw_rows) == 281

    blocked_ids = {
        "HLA1516.1-FM-4.1.5-001",
        "HLA1516.1-FM-4.1.5-002",
    }
    vendor_divergent_ids = {
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM",
        "HLA1516.1-FM-4.5-EXC-001",
        "HLA1516.1-FM-4.9-EXC-001",
    }

    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"} == blocked_ids
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"} == vendor_divergent_ids

    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    assert len(verified_rows) == 274

    for row in verified_rows:
        refs = row["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), row["requirement_id"]
        assert any(
            ref.startswith("tests/scenarios/test_federation_") or ref.startswith("tests/scenarios/test_object_management_")
            for ref in refs
        ), row["requirement_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"]

    for requirement_id in blocked_ids | vendor_divergent_ids:
        refs = by_requirement_id[requirement_id]["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), requirement_id
        assert any(
            ref.startswith("tests/scenarios/test_federation_") or ref.startswith("tests/scenarios/test_object_management_")
            for ref in refs
        ), requirement_id
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), requirement_id

    save_abort_row = by_requirement_id["REQ-RTI-FM-4_21-abortFederationSave"]
    assert save_abort_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario"
        in save_abort_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_abort_matrix" in save_abort_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_abort_matrix" in save_abort_row["evidence_refs"]

    restore_request_failure_row = by_requirement_id["REQ-FED-FM-4_25-requestFederationRestoreFailed"]
    assert restore_request_failure_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_request_failure_scenario"
        in restore_request_failure_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_failure_matrix"
        in restore_request_failure_row["evidence_refs"]
    )

    restore_failure_pairs = {
        "REQ-FED-FM-4_29-federationNotRestored": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_failure_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_failure_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_failure_matrix",
        ),
        "REQ-RTI-FM-4_30-abortFederationRestore": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_matrix",
        ),
    }
    for requirement_id, refs in restore_failure_pairs.items():
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for ref in refs:
            assert ref in row["evidence_refs"]

    restore_abort_exc_row = by_requirement_id["HLA1516.1-FM-4.30-EXC-001"]
    assert restore_abort_exc_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_exception_scenario"
        in restore_abort_exc_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_exception_matrix"
        in restore_abort_exc_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_exception_matrix" in restore_abort_exc_row["evidence_refs"]

    resign_callback_row = by_requirement_id["HLA1516.1-FM-4.10-CB-001"]
    assert resign_callback_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_resigned_federate_callback_silence_scenario"
        in resign_callback_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resigned_federate_callback_silence_matrix"
        in resign_callback_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resigned_federate_callback_silence_matrix" in resign_callback_row["evidence_refs"]

    resign_precondition_row = by_requirement_id["HLA1516.1-FM-4.10-PRE-001"]
    assert resign_precondition_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_precondition_scenario"
        in resign_precondition_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix"
        in resign_precondition_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_precondition_matrix" in resign_precondition_row["evidence_refs"]

    resign_exception_row = by_requirement_id["HLA1516.1-FM-4.10-EXC-001"]
    assert resign_exception_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_precondition_scenario"
        in resign_exception_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix"
        in resign_exception_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_precondition_matrix" in resign_exception_row["evidence_refs"]

    resign_mom_row = by_requirement_id["HLA1516.1-FM-4.10-MOM-001"]
    assert resign_mom_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_mom_cleanup_scenario"
        in resign_mom_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_mom_cleanup_matrix"
        in resign_mom_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_resign_mom_cleanup_matrix" in resign_mom_row["evidence_refs"]

    disconnect_mom_row = by_requirement_id["HLA1516.1-FM-4.3-MOM-001"]
    assert disconnect_mom_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_resign.py::run_disconnect_mom_cleanup_scenario"
        in disconnect_mom_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_disconnect_mom_cleanup_matrix"
        in disconnect_mom_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_disconnect_mom_cleanup_matrix" in disconnect_mom_row["evidence_refs"]

    join_precondition_row = by_requirement_id["HLA1516.1-FM-4.9-PRE-001"]
    assert join_precondition_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_join.py::run_join_precondition_scenario"
        in join_precondition_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix"
        in join_precondition_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_join_precondition_matrix" in join_precondition_row["evidence_refs"]

    for requirement_id in {"HLA1516.1-FM-4.1-005", "HLA1516.1-FM-4.1-006"}:
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_multi_participation_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multi_participation_matrix" in row["evidence_refs"]

    for requirement_id in {"HLA1516.1-FM-4.1.4.1-001", "HLA1516.1-FM-4.1.4.1-002"}:
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_integrity_negative_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_integrity_negative_matrix" in row["evidence_refs"]

    combined_fom_row = by_requirement_id["HLA1516.1-FM-4.1.4-001"]
    assert combined_fom_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario"
        in combined_fom_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_module_fom_visibility_matrix" in combined_fom_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_multi_module_fom_visibility_matrix" in combined_fom_row["evidence_refs"]

    auto_mim_row = by_requirement_id["HLA1516.1-FM-4.1.4-002"]
    assert auto_mim_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_module_visibility_scenario"
        in auto_mim_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_module_visibility_matrix" in auto_mim_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_fom_module_visibility_matrix" in auto_mim_row["evidence_refs"]


def test_pitch_clause4_mapped_rows_prefer_shared_harness_evidence_only():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "4"
    ]
    rows = {row["requirement_id"]: row for row in payload["rows"] if row.get("requirement_id")}
    by_requirement_id = rows
    allowed_clause4_evidence_prefixes = (
        "packages/hla-verification/",
        "tests/scenarios/",
        "tests/vendors/",
        "packages/hla-vendor-pitch/docs/evidence/",
        "artifacts/preflight_artifacts/",
        "artifacts/vendor_runtime_status/",
        "tests/test_rti_pitch_split_packages.py::",
    )

    for row in raw_rows:
        for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
            refs = row[field]
            assert all(ref.startswith(allowed_clause4_evidence_prefixes) for ref in refs), (
                row.get("requirement_id") or row["matrix_id"],
                field,
                refs,
            )

    milestone_rows = {
        "REQ-RTI-FM-4_7-listFederationExecutions",
        "REQ-FED-FM-4_8-reportFederationExecutions",
        "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded",
        "REQ-FED-FM-4_12-synchronizationPointRegistrationFailed",
        "REQ-FED-FM-4_13-announceSynchronizationPoint",
        "REQ-RTI-FM-4_14-synchronizationPointAchieved",
        "REQ-FED-FM-4_15-federationSynchronized",
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_18-federateSaveBegun",
        "REQ-RTI-FM-4_19-federateSaveComplete",
        "REQ-FED-FM-4_20-federationSaved",
        "REQ-RTI-FM-4_21-abortFederationSave",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-FED-FM-4_23-federationSaveStatusResponse",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded",
        "REQ-FED-FM-4_25-requestFederationRestoreFailed",
        "REQ-FED-FM-4_26-federationRestoreBegun",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_28-federateRestoreComplete",
        "REQ-FED-FM-4_29-federationRestored",
        "REQ-FED-FM-4_29-federationNotRestored",
        "REQ-RTI-FM-4_30-abortFederationRestore",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
        "HLA1516.1-FM-4.1.2-001",
        "HLA1516.1-FM-4.1.2-002",
        "HLA1516.1-FM-4.1.3-001",
        "HLA1516.1-FM-4.9-CB-001",
    }
    strict_milestone_evidence_prefixes = (
        "packages/hla-verification/src/hla.verification/",
        "tests/scenarios/test_federation_management_backend_matrix.py::",
        "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )
    for requirement_id in milestone_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified", requirement_id
        assert row["pitch_jpype_disposition"] == "verified", requirement_id
        assert row["pitch_py4j_disposition"] == "verified", requirement_id
        assert all(ref.startswith(strict_milestone_evidence_prefixes) for ref in row["evidence_refs"]), (
            requirement_id,
            row["evidence_refs"],
        )

    for requirement_id in {
        "REQ-RTI-FM-4_7-listFederationExecutions",
        "REQ-FED-FM-4_8-reportFederationExecutions",
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded",
        "REQ-FED-FM-4_25-requestFederationRestoreFailed",
        "REQ-FED-FM-4_26-federationRestoreBegun",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-FED-FM-4_29-federationRestored",
        "REQ-FED-FM-4_29-federationNotRestored",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
    }:
        refs = rows[requirement_id]["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs), requirement_id
        assert "tests/verification/test_spec_traceability_and_extended_python_rti.py" not in refs, requirement_id
        assert "tests/verification/test_compliance_slice_v011.py" not in refs, requirement_id

    for requirement_id in {"HLA1516.1-FM-4.17-MOM-001", "HLA1516.1-FM-4.27-MOM-001"}:
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix" in row["evidence_refs"]

    queued_save_restore_row = by_requirement_id["HLA1516.1-FM-4.1.2-002"]
    assert queued_save_restore_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_queued_callback_scenario"
        in queued_save_restore_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_queued_callback_matrix"
        in queued_save_restore_row["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_queued_callback_matrix"
        in queued_save_restore_row["evidence_refs"]
    )

    for requirement_id, expected_refs in {
        "HLA1516.1-FM-4.17-EXC-001": {
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_failure_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario",
        },
        "HLA1516.1-FM-4.27-EXC-001": {
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_failure_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_scenario",
        },
    }.items():
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for expected_ref in expected_refs:
            assert expected_ref in row["evidence_refs"]

    save_status_exc_row = by_requirement_id["HLA1516.1-FM-4.22-EXC-001"]
    assert save_status_exc_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_status_exception_scenario"
        in save_status_exc_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_status_exception_matrix"
        in save_status_exc_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_status_exception_matrix" in save_status_exc_row["evidence_refs"]

    create_exception_row = by_requirement_id["HLA1516.1-FM-4.5-EXC-001"]
    assert create_exception_row["pitch_disposition"] == "vendor-divergent"
    for expected_ref in {
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_negative_scenario",
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_with_mim_matrix",
    }:
        assert expected_ref in create_exception_row["evidence_refs"]

    join_exception_row = by_requirement_id["HLA1516.1-FM-4.9-EXC-001"]
    assert join_exception_row["pitch_disposition"] == "vendor-divergent"
    for expected_ref in {
        "packages/hla-verification/src/hla.verification/scenario_join.py::run_join_precondition_scenario",
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
    }:
        assert expected_ref in join_exception_row["evidence_refs"]

    blocked_clause4_rows = {
        row["requirement_id"]
        for row in rows.values()
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)" and row["clause_root"] == "4" and row["pitch_disposition"] == "blocked"
    }
    assert blocked_clause4_rows == {"HLA1516.1-FM-4.1.5-001", "HLA1516.1-FM-4.1.5-002"}

    residual_clause4_rows = {
        row["requirement_id"] or row["matrix_id"]: row["pitch_disposition"]
        for row in payload["rows"]
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["clause_root"] == "4"
        and row["pitch_disposition"] != "verified"
    }
    assert residual_clause4_rows == {
        "REQ-RTI-FM-4_5-createFederationExecutionWithMIM": "vendor-divergent",
        "AREA-1516.1-4": "not-applicable",
        "HLA1516.1-FM-001": "not-applicable",
        "HLA1516.1-FM-4.1.5-001": "blocked",
        "HLA1516.1-FM-4.1.5-002": "blocked",
        "HLA1516.1-FM-4.5-EXC-001": "vendor-divergent",
        "HLA1516.1-FM-4.9-EXC-001": "vendor-divergent",
    }

    for requirement_id in blocked_clause4_rows:
        row = by_requirement_id[requirement_id]
        assert row["pitch_disposition"] == "blocked"
        assert row["pitch_jpype_disposition"] == "blocked"
        assert row["pitch_py4j_disposition"] == "blocked"
        assert "./tools/pitch lost-federate-probe" in row["notes"]
        assert "Docker is unreachable" in row["notes"]
        assert "loopback ports are blocked" in row["notes"]
        for expected_ref in {
            "packages/hla-verification/src/hla.verification/scenario_connection_lost.py::run_connection_lost_callback_scenario",
            "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_lost_federate_mom_scenario",
            "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
            "artifacts/preflight_artifacts/pitch-preflight.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
            "packages/hla-verification/src/hla.verification/scenario_resign.py::run_disconnect_mom_cleanup_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_lost_federate_mom_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
        }:
            assert expected_ref in row["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in row["evidence_refs"])
        assert not any(ref.startswith("tests/verification/") for ref in row["evidence_refs"])
        assert {
            "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
            "artifacts/preflight_artifacts/pitch-preflight.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
            "tests/test_rti_pitch_split_packages.py::test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process",
        }.issubset(set(row["pitch_jpype_evidence_refs"]))
        for expected_ref in {
            "artifacts/preflight_artifacts/pitch-preflight.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
            "artifacts/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
            "packages/hla-verification/src/hla.verification/scenario_lost_federate.py::run_lost_federate_mom_scenario",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
            "tests/test_rti_pitch_split_packages.py::test_pitch_py4j_factory_attaches_gateway_process",
            "packages/hla-vendor-pitch/docs/evidence/pitch_clause4_lost_federate_gap_2026-06-11.md",
        }:
            assert expected_ref in row["pitch_py4j_evidence_refs"]

    clause4_seed_row = next(
        row
        for row in raw_rows
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["clause_root"] == "4"
        and not row["requirement_id"]
        and compliance_section_key(row["section_ref"]) == "IEEE 1516.1-2010 §4"
    )
    assert clause4_seed_row["pitch_disposition"] == "not-applicable"

    save_status_mom_row = by_requirement_id["HLA1516.1-FM-4.22-MOM-001"]
    assert save_status_mom_row["pitch_disposition"] == "verified"
    for expected_ref in {
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_failure_scenario",
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario",
    }:
        assert expected_ref in save_status_mom_row["evidence_refs"]

    restore_abort_mom_row = by_requirement_id["HLA1516.1-FM-4.30-MOM-001"]
    assert restore_abort_mom_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_scenario"
        in restore_abort_mom_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_matrix" in restore_abort_mom_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_matrix" in restore_abort_mom_row["evidence_refs"]

    sync_mom_row = by_requirement_id["HLA1516.1-FM-4.12-MOM-001"]
    assert sync_mom_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_sync.py::run_synchronization_scenario"
        in sync_mom_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_synchronization_matrix" in sync_mom_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_synchronization_matrix" in sync_mom_row["evidence_refs"]

    for requirement_id in {"HLA1516.1-FM-4.2-MOM-001", "HLA1516.1-FM-4.9-MOM-001"}:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_resign.py::run_resign_mom_cleanup_scenario"
            in row["evidence_refs"]
        )

    destroy_mom_row = by_requirement_id["HLA1516.1-FM-4.6-MOM-001"]
    assert destroy_mom_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_listing_scenario"
        in destroy_mom_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_listing_matrix" in destroy_mom_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_listing_matrix" in destroy_mom_row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-FM-4_16-requestFederationSave",
        "REQ-FED-FM-4_17-initiateFederateSave",
        "REQ-RTI-FM-4_18-federateSaveBegun",
        "REQ-RTI-FM-4_19-federateSaveComplete",
        "REQ-FED-FM-4_20-federationSaved",
        "REQ-RTI-FM-4_22-queryFederationSaveStatus",
        "REQ-FED-FM-4_23-federationSaveStatusResponse",
        "REQ-RTI-FM-4_24-requestFederationRestore",
        "REQ-FED-FM-4_25-requestFederationRestoreSucceeded",
        "REQ-FED-FM-4_26-federationRestoreBegun",
        "REQ-FED-FM-4_27-initiateFederateRestore",
        "REQ-RTI-FM-4_28-federateRestoreComplete",
        "REQ-FED-FM-4_29-federationRestored",
        "REQ-RTI-FM-4_31-queryFederationRestoreStatus",
        "REQ-FED-FM-4_32-federationRestoreStatusResponse",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-FM-4_19-federateSaveNotComplete",
        "REQ-FED-FM-4_20-federationNotSaved",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_failure_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_failure_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_failure_matrix" in row["evidence_refs"]

    save_abort = by_requirement_id["REQ-RTI-FM-4_21-abortFederationSave"]
    assert save_abort["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario"
        in save_abort["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_abort_matrix" in save_abort["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_abort_matrix" in save_abort["evidence_refs"]

    failed_restore_request = by_requirement_id["REQ-FED-FM-4_25-requestFederationRestoreFailed"]
    assert failed_restore_request["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_request_failure_scenario"
        in failed_restore_request["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_failure_matrix"
        in failed_restore_request["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_request_failure_matrix"
        in failed_restore_request["evidence_refs"]
    )

    for requirement_id in {
        "REQ-RTI-FM-4_28-federateRestoreNotComplete",
        "REQ-FED-FM-4_29-federationNotRestored",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_failure_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_failure_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_failure_matrix" in row["evidence_refs"]

    restore_abort = by_requirement_id["REQ-RTI-FM-4_30-abortFederationRestore"]
    assert restore_abort["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_abort_scenario"
        in restore_abort["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_abort_matrix" in restore_abort["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_abort_matrix" in restore_abort["evidence_refs"]

    broad_positive_rows = {
        "HLA1516.1-FM-4.16-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "HLA1516.1-FM-4.21-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_abort_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_abort_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_abort_matrix",
        ),
        "HLA1516.1-FM-4.23-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "HLA1516.1-FM-4.24-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "HLA1516.1-FM-4.26-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "HLA1516.1-FM-4.31-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
        "HLA1516.1-FM-4.32-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix",
        ),
    }
    for requirement_id, expected_refs in broad_positive_rows.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for expected_ref in expected_refs:
            assert expected_ref in row["evidence_refs"]

    broad_mixed_rows = {
        "HLA1516.1-FM-4.19-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_failure_scenario",
        ),
        "HLA1516.1-FM-4.20-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_failure_scenario",
        ),
        "HLA1516.1-FM-4.25-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_request_failure_scenario",
        ),
        "HLA1516.1-FM-4.28-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_failure_scenario",
        ),
        "HLA1516.1-FM-4.29-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario",
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_failure_scenario",
        ),
    }
    for requirement_id, expected_refs in broad_mixed_rows.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        for expected_ref in expected_refs:
            assert expected_ref in row["evidence_refs"]

    extracted_clause_rows = {
        "HLA1516.1-FM-4.1-005": "scenario_federation_lifecycle.py::run_multi_participation_scenario",
        "HLA1516.1-FM-4.1-006": "scenario_federation_lifecycle.py::run_multi_participation_scenario",
        "HLA1516.1-FM-4.1.2-002": "scenario_save_restore.py::run_save_restore_queued_callback_scenario",
        "HLA1516.1-FM-4.1.4-001": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.1-FM-4.1.4.1-001": "scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "HLA1516.1-FM-4.1.4.1-002": "scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "HLA1516.1-FM-4.2-001": "scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "HLA1516.1-FM-4.3-MOM-001": "scenario_resign.py::run_disconnect_mom_cleanup_scenario",
        "HLA1516.1-FM-4.10-EXC-001": "scenario_resign.py::run_resign_precondition_scenario",
        "HLA1516.1-FM-4.10-CB-001": "scenario_save_restore.py::run_resigned_federate_callback_silence_scenario",
        "HLA1516.1-FM-4.10-MOM-001": "scenario_resign.py::run_resign_mom_cleanup_scenario",
        "HLA1516.1-FM-4.10-PRE-001": "scenario_resign.py::run_resign_precondition_scenario",
        "HLA1516.1-FM-4.1.4-002": "scenario_federation_lifecycle.py::run_fom_module_visibility_scenario",
        "HLA1516.1-FM-4.17-MOM-001": "scenario_save_restore.py::run_save_restore_scenario",
        "HLA1516.1-FM-4.17-EXC-001": "scenario_save_restore.py::run_save_restore_scenario",
        "HLA1516.1-FM-4.22-EXC-001": "scenario_save_restore.py::run_save_status_exception_scenario",
        "HLA1516.1-FM-4.22-MOM-001": "scenario_save_restore.py::run_save_restore_scenario",
        "HLA1516.1-FM-4.27-EXC-001": "scenario_save_restore.py::run_save_restore_scenario",
        "HLA1516.1-FM-4.27-MOM-001": "scenario_save_restore.py::run_save_restore_scenario",
        "HLA1516.1-FM-4.30-MOM-001": "scenario_save_restore.py::run_restore_abort_scenario",
        "HLA1516.1-FM-4.1.4.2-001": "scenario_federation_lifecycle.py::run_fom_module_visibility_scenario",
        "HLA1516.1-FM-4.12-MOM-001": "scenario_sync.py::run_synchronization_scenario",
        "HLA1516.1-FM-4.2-MOM-001": "scenario_resign.py::run_resign_mom_cleanup_scenario",
        "HLA1516.1-FM-4.5-MOM-001": "scenario_federation_lifecycle.py::run_fom_module_visibility_scenario",
        "HLA1516.1-FM-4.6-MOM-001": "scenario_federation_lifecycle.py::run_federation_listing_scenario",
        "HLA1516.1-FM-4.9-MOM-001": "scenario_resign.py::run_resign_mom_cleanup_scenario",
        "HLA1516.1-FM-4.9-PRE-001": "scenario_join.py::run_join_precondition_scenario",
        "HLA1516.1-FM-4.6-CB-001": "scenario_federation_lifecycle.py::run_federation_listing_scenario",
        "HLA1516.1-FM-4.12-EXC-001": "scenario_sync.py::run_synchronization_registration_failure_scenario",
        "HLA1516.1-FM-4.17-CB-001": "scenario_save_restore.py::run_save_restore_scenario",
        "HLA1516.1-FM-4.30-CB-001": "scenario_save_restore.py::run_restore_abort_scenario",
    }
    for requirement_id, harness_ref in extracted_clause_rows.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert any(harness_ref in ref for ref in row["evidence_refs"])

    restore_status_exception = by_requirement_id["HLA1516.1-FM-4.31-EXC-001"]
    assert restore_status_exception["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_status_exception_scenario"
        in restore_status_exception["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_status_exception_matrix"
        in restore_status_exception["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_status_exception_matrix"
        in restore_status_exception["evidence_refs"]
    )

    save_request_exception = by_requirement_id["HLA1516.1-FM-4.16-EXC-001"]
    assert save_request_exception["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_request_precondition_scenario"
        in save_request_exception["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_request_precondition_matrix"
        in save_request_exception["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_request_precondition_matrix"
        in save_request_exception["evidence_refs"]
    )

    restore_request_exception = by_requirement_id["HLA1516.1-FM-4.24-EXC-001"]
    assert restore_request_exception["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_request_precondition_scenario"
        in restore_request_exception["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_request_precondition_matrix"
        in restore_request_exception["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_request_precondition_matrix"
        in restore_request_exception["evidence_refs"]
    )

    save_participant_exception = by_requirement_id["HLA1516.1-FM-4.18-EXC-001"]
    assert save_participant_exception["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_participant_exception_scenario"
        in save_participant_exception["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_participant_exception_matrix"
        in save_participant_exception["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_participant_exception_matrix"
        in save_participant_exception["evidence_refs"]
    )

    abort_save_exception = by_requirement_id["HLA1516.1-FM-4.21-EXC-001"]
    assert abort_save_exception["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_abort_save_exception_scenario"
        in abort_save_exception["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_abort_save_exception_matrix"
        in abort_save_exception["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_abort_save_exception_matrix"
        in abort_save_exception["evidence_refs"]
    )

    restore_participant_exception = by_requirement_id["HLA1516.1-FM-4.28-EXC-001"]
    assert restore_participant_exception["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_participant_exception_scenario"
        in restore_participant_exception["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_participant_exception_matrix"
        in restore_participant_exception["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_participant_exception_matrix"
        in restore_participant_exception["evidence_refs"]
    )

    for requirement_id in {
        "HLA1516.1-FM-4.16-MOM-001",
        "HLA1516.1-FM-4.18-EXC-001",
        "HLA1516.1-FM-4.18-MOM-001",
        "HLA1516.1-FM-4.23-EXC-001",
        "HLA1516.1-FM-4.23-MOM-001",
        "HLA1516.1-FM-4.24-MOM-001",
        "HLA1516.1-FM-4.19-EXC-001",
        "HLA1516.1-FM-4.19-MOM-001",
        "HLA1516.1-FM-4.20-EXC-001",
        "HLA1516.1-FM-4.20-MOM-001",
        "HLA1516.1-FM-4.21-EXC-001",
        "HLA1516.1-FM-4.21-MOM-001",
        "HLA1516.1-FM-4.25-EXC-001",
        "HLA1516.1-FM-4.25-MOM-001",
        "HLA1516.1-FM-4.26-EXC-001",
        "HLA1516.1-FM-4.26-MOM-001",
        "HLA1516.1-FM-4.29-EXC-001",
        "HLA1516.1-FM-4.29-MOM-001",
        "HLA1516.1-FM-4.28-EXC-001",
        "HLA1516.1-FM-4.28-MOM-001",
        "HLA1516.1-FM-4.31-MOM-001",
        "HLA1516.1-FM-4.32-EXC-001",
        "HLA1516.1-FM-4.32-MOM-001",
    }:
        assert rows[requirement_id]["pitch_disposition"] == "verified"

    clause4_not_yet_tested = [
        row
        for row in rows.values()
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)" and row["clause_root"] == "4" and row["pitch_disposition"] == "not-yet-tested"
    ]
    assert len(clause4_not_yet_tested) == 0


def test_pitch_clause6_mapped_rows_prefer_shared_harness_evidence_only():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "6"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}
    runtime_rows = [
        row
        for row in raw_rows
        if row["pitch_disposition"] in {"verified", "vendor-divergent"}
    ]
    strict_clause6_evidence_prefixes = (
        "packages/hla-verification/src/hla.verification/",
        "tests/scenarios/test_object_management_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )
    vendor_divergent_clause6_evidence_prefixes = strict_clause6_evidence_prefixes + (
        "packages/hla-vendor-pitch/docs/evidence/",
    )

    for row in runtime_rows:
        refs = row["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs), row["requirement_id"]
        assert not any(ref.startswith("tests/verification/") for ref in refs), row["requirement_id"]
        if row["pitch_disposition"] == "verified":
            assert row["pitch_jpype_disposition"] == "verified", row["requirement_id"]
            assert row["pitch_py4j_disposition"] == "verified", row["requirement_id"]
            assert all(ref.startswith(strict_clause6_evidence_prefixes) for ref in refs), (
                row["requirement_id"],
                refs,
            )
        else:
            assert all(ref.startswith(vendor_divergent_clause6_evidence_prefixes) for ref in refs), (
                row["requirement_id"],
                refs,
            )

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-RTI-OM-6_10-updateAttributeValues"][field]
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-RTI-OM-6_12-sendInteraction"][field]
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs


def test_pitch_clause7_mapped_rows_prefer_shared_harness_evidence_only():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "7"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}
    runtime_rows = [
        row
        for row in raw_rows
        if row["pitch_disposition"] in {"verified", "vendor-divergent"}
    ]
    strict_clause7_evidence_prefixes = (
        "packages/hla-verification/src/hla.verification/",
        "tests/scenarios/test_ownership_management_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )
    vendor_divergent_clause7_evidence_prefixes = strict_clause7_evidence_prefixes + (
        "packages/hla-vendor-pitch/docs/evidence/",
    )

    for row in runtime_rows:
        refs = row["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs), row["requirement_id"]
        assert not any(ref.startswith("tests/verification/") for ref in refs), row["requirement_id"]
        if row["pitch_disposition"] == "verified":
            assert row["pitch_jpype_disposition"] == "verified", row["requirement_id"]
            assert row["pitch_py4j_disposition"] == "verified", row["requirement_id"]
            assert all(ref.startswith(strict_clause7_evidence_prefixes) for ref in refs), (
                row["requirement_id"],
                refs,
            )
        else:
            assert all(ref.startswith(vendor_divergent_clause7_evidence_prefixes) for ref in refs), (
                row["requirement_id"],
                refs,
            )

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-FED-OWN-7_10-attributeOwnershipUnavailable"][field]
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_certi_backend_callbacks.py" not in refs
        assert "tests/backends/test_certi_java_profile_callbacks.py" not in refs

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-FED-OWN-7_11-requestAttributeOwnershipRelease"][field]
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs
        assert "tests/backends/test_certi_backend_callbacks.py" not in refs
        assert "tests/backends/test_certi_java_profile_callbacks.py" not in refs


def test_pitch_clause8_mapped_rows_prefer_shared_harness_evidence_only():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "8"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}
    runtime_rows = [
        row
        for row in raw_rows
        if row["pitch_disposition"] in {"verified", "vendor-divergent"}
    ]
    strict_clause8_evidence_prefixes = (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::",
        "tests/time/test_section8_backend_matrix.py::",
        "tests/time/test_lookahead_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
        "packages/hla-vendor-pitch/docs/evidence/",
    )

    for row in runtime_rows:
        refs = row["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs), row["requirement_id"]
        assert not any(ref.startswith("tests/verification/") for ref in refs), row["requirement_id"]
        if row["pitch_disposition"] == "verified":
            assert row["pitch_jpype_disposition"] == "verified", row["requirement_id"]
            assert row["pitch_py4j_disposition"] == "verified", row["requirement_id"]
        assert all(ref.startswith(strict_clause8_evidence_prefixes) for ref in refs), (
            row["requirement_id"],
            refs,
        )

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-RTI-TM-8_12-flushQueueRequest"][field]
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-RTI-TM-8_16-queryGALT"][field]
        assert "tests/verification/test_compliance_slice_v011.py" not in refs
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs


def test_pitch_clause9_mapped_rows_prefer_shared_harness_evidence_only():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "9"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}
    runtime_rows = [
        row
        for row in raw_rows
        if row["pitch_disposition"] == "verified"
    ]
    strict_clause9_evidence_prefixes = (
        "packages/hla-verification/src/hla.verification/",
        "tests/scenarios/test_ddm_backend_matrix.py::",
        "tests/vendors/test_pitch_real_backend_matrix.py::",
    )

    for row in runtime_rows:
        refs = row["evidence_refs"]
        assert not any(ref.startswith("tests/backends/") for ref in refs), row["requirement_id"]
        assert not any(ref.startswith("tests/verification/") for ref in refs), row["requirement_id"]
        assert row["pitch_jpype_disposition"] == "verified", row["requirement_id"]
        assert row["pitch_py4j_disposition"] == "verified", row["requirement_id"]
        assert all(ref.startswith(strict_clause9_evidence_prefixes) for ref in refs), (
            row["requirement_id"],
            refs,
        )

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions"][field]
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs
        assert "tests/verification/test_compliance_slice_v011.py" not in refs

    for field in ("evidence_refs", "pitch_jpype_evidence_refs", "pitch_py4j_evidence_refs"):
        refs = rows["REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions"][field]
        assert "tests/backends/test_python_backend_support_services.py" not in refs
        assert "tests/backends/test_python_backend_federation_extended.py" not in refs
        assert "tests/backends/test_python_backend_object_ownership_extended.py" not in refs
        assert "tests/backends/test_python_backend_time_ddm_extended.py" not in refs
        assert "tests/verification/test_spec_traceability_and_extended_python_rti.py" not in refs


def test_pitch_clause6_1516_1_dispositions_are_fully_classified_and_harness_backed():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "6"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    vendor_divergent_ids = {
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.24-001",
        "HLA1516.1-OM-6.25-001",
        "HLA1516.1-OM-6.26-001",
        "HLA1516.1-OM-6.27-001",
        "HLA1516.1-OM-6.28-001",
        "HLA1516.1-OM-6.29-001",
        "HLA1516.1-OM-6.30-001",
    }

    not_yet_tested_ids = {
        "HLA1516.1-OM-6.1.10-004",
        "HLA1516.1-OM-6.25-003",
        "HLA1516.1-OM-6.29-003",
    }

    assert len(raw_rows) == 119
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"} == not_yet_tested_ids
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"} == vendor_divergent_ids

    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    assert len(verified_rows) == 105

    for row in verified_rows:
        refs = row["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), row["requirement_id"]
        assert any(ref.startswith("tests/scenarios/test_object_management_backend_matrix.py::") for ref in refs), row["requirement_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"]

    for requirement_id in vendor_divergent_ids:
        refs = rows[requirement_id]["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), requirement_id
        assert any(ref.startswith("tests/scenarios/test_object_management_backend_matrix.py::") for ref in refs), requirement_id
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), requirement_id


def test_pitch_clause7_1516_1_dispositions_are_fully_classified_and_harness_backed():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "7"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    vendor_divergent_ids = {
        "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
    }

    assert len(raw_rows) == 39
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"} == vendor_divergent_ids
    assert {row["requirement_id"] or row["matrix_id"] for row in raw_rows if row["pitch_disposition"] == "not-applicable"} == {
        "AREA-1516.1-7",
        "HLA1516.1-OWN-001",
    }

    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    assert len(verified_rows) == 27

    for row in verified_rows:
        refs = row["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), row["requirement_id"]
        assert any(ref.startswith("tests/scenarios/test_ownership_management_backend_matrix.py::") for ref in refs), row["requirement_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"]

    for requirement_id in vendor_divergent_ids:
        refs = rows[requirement_id]["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), requirement_id
        assert any(ref.startswith("tests/scenarios/test_ownership_management_backend_matrix.py::") for ref in refs), requirement_id
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), requirement_id

    probe_rows = {
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
    }
    for requirement_id in probe_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::probe_negotiated_attribute_ownership_offer"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_negotiated_divesting_offer_probe_matrix"
            in row["evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_negotiated_divesting_offer_probe" in row["evidence_refs"]

    negotiated_rows = {
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
    }
    for requirement_id in negotiated_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_negotiated_attribute_ownership_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_negotiated_ownership_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_negotiated_ownership_matrix" in row["evidence_refs"]

    ownership_unavailable_row = rows["REQ-FED-OWN-7_10-attributeOwnershipUnavailable"]
    assert ownership_unavailable_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_unavailable_scenario"
        in ownership_unavailable_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix"
        in ownership_unavailable_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix" in ownership_unavailable_row["evidence_refs"]


def test_pitch_clause8_1516_1_dispositions_are_fully_classified_and_harness_backed():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "8"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    blocked_ids = set()
    vendor_divergent_ids = {
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
        "REQ-RTI-TM-8_21-retract",
        "REQ-FED-TM-8_22-requestRetraction",
        "HLA1516.1-TM-8.1-001",
        "HLA1516.1-TM-8.1-002",
        "HLA1516.1-TM-8.1.1-001",
        "HLA1516.1-TM-8.1.2-001",
        "HLA1516.1-TM-8.1.2-002",
        "HLA1516.1-TM-8.1.2-003",
        "HLA1516.1-TM-8.1.2-004",
        "HLA1516.1-TM-8.1.3-002",
        "HLA1516.1-TM-8.1.3-003",
        "HLA1516.1-TM-8.1.5-001",
        "HLA1516.1-TM-8.1.6-001",
        "HLA1516.1-TM-8.1.7-001",
        "HLA1516.1-TM-8.10-001",
        "HLA1516.1-TM-8.21-001",
    }

    assert len(raw_rows) == 61
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"} == blocked_ids
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"} == vendor_divergent_ids
    assert {row["requirement_id"] or row["matrix_id"] for row in raw_rows if row["pitch_disposition"] == "not-applicable"} == {
        "AREA-1516.1-8",
        "HLA1516.1-TM-001",
    }

    verified_rows = [row for row in raw_rows if row["pitch_disposition"] == "verified"]
    assert len(verified_rows) == 41

    for row in verified_rows:
        refs = row["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/section8_matrix.py::" in ref
            for ref in refs
        ), row["requirement_id"]
        assert any(
            ref.startswith("tests/time/test_section8_backend_matrix.py::")
            or ref.startswith("tests/time/test_lookahead_backend_matrix.py::")
            for ref in refs
        ), row["requirement_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"]

    for requirement_id in vendor_divergent_ids | blocked_ids:
        refs = rows[requirement_id]["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/section8_matrix.py::" in ref
            for ref in refs
        ), requirement_id
        assert any(ref.startswith("tests/time/test_section8_backend_matrix.py::") for ref in refs), requirement_id
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), requirement_id

    next_message_request_row = rows["REQ-RTI-TM-8_10-nextMessageRequest"]
    assert next_message_request_row["pitch_disposition"] == "vendor-divergent"
    assert (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_ordering_and_query_case"
        in next_message_request_row["evidence_refs"]
    )
    assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries" in next_message_request_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix" in next_message_request_row["evidence_refs"]

    query_galt_row = rows["REQ-RTI-TM-8_16-queryGALT"]
    assert query_galt_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_time_bound_query_case"
        in query_galt_row["evidence_refs"]
    )
    assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_time_bound_queries" in query_galt_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_time_bound_query_matrix" in query_galt_row["evidence_refs"]


def test_pitch_clause9_1516_1_dispositions_are_fully_classified_and_harness_backed():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "9"
    ]
    rows = {row["requirement_id"]: row for row in raw_rows if row.get("requirement_id")}

    blocked_ids = set()
    verified_ids = {
        "HLA1516.1-DDM-9.1-001",
        "HLA1516.1-DDM-9.1-002",
        "HLA1516.1-DDM-9.1-003",
        "REQ-RTI-DDM-9_2-createRegion",
        "REQ-RTI-DDM-9_3-commitRegionModifications",
        "REQ-RTI-DDM-9_4-deleteRegion",
        "REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions",
        "REQ-RTI-DDM-9_6-associateRegionsForUpdates",
        "REQ-RTI-DDM-9_7-unassociateRegionsForUpdates",
        "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions",
        "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions",
        "REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions",
        "REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions",
        "REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions",
        "REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions",
        "REQ-RTI-DDM-9_12-sendInteractionWithRegions",
        "REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions",
        "HLA1516.1-DDM-9.2-001",
        "HLA1516.1-DDM-9.3-001",
        "HLA1516.1-DDM-9.4-001",
        "HLA1516.1-DDM-9.5-001",
        "HLA1516.1-DDM-9.6-001",
        "HLA1516.1-DDM-9.7-001",
        "HLA1516.1-DDM-9.8-001",
        "HLA1516.1-DDM-9.9-001",
        "HLA1516.1-DDM-9.10-001",
        "HLA1516.1-DDM-9.11-001",
        "HLA1516.1-DDM-9.12-001",
        "HLA1516.1-DDM-9.13-001",
    }

    assert len(raw_rows) == 31
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "not-yet-tested"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"}
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"} == blocked_ids
    assert {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "verified"} == verified_ids
    assert {row["requirement_id"] or row["matrix_id"] for row in raw_rows if row["pitch_disposition"] == "not-applicable"} == {
        "AREA-1516.1-9",
        "HLA1516.1-DDM-001",
    }

    for requirement_id in verified_ids | blocked_ids:
        refs = rows[requirement_id]["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            and (
                "two_federate_suite_scenarios.py::run_suite_ddm_scenario" in ref
                or "scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario" in ref
                or "scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario" in ref
            )
            for ref in refs
        ), requirement_id
        assert any(ref.startswith("tests/scenarios/test_ddm_backend_matrix.py::") for ref in refs), requirement_id
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), requirement_id

    suite_ddm_row = rows["HLA1516.1-DDM-9.1-001"]
    assert suite_ddm_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/two_federate_suite_scenarios.py::run_suite_ddm_scenario"
        in suite_ddm_row["evidence_refs"]
    )
    assert "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix" in suite_ddm_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_matrix" in suite_ddm_row["evidence_refs"]

    passive_region_row = rows["REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions"]
    assert passive_region_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario"
        in passive_region_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_passive_region_subscription_matrix"
        in passive_region_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_passive_region_subscription_matrix" in passive_region_row["evidence_refs"]

    region_lifecycle_row = rows["REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions"]
    assert region_lifecycle_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario"
        in region_lifecycle_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix"
        in region_lifecycle_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_object_region_lifecycle_matrix" in region_lifecycle_row["evidence_refs"]


def test_pitch_clause10_1516_1_dispositions_are_explicitly_staged():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "10"
    ]
    rows = {row["requirement_id"] or row["matrix_id"]: row for row in raw_rows if row.get("requirement_id") or row.get("matrix_id")}

    assert len(raw_rows) == 86
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "verified"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "blocked"}
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "vendor-divergent"}

    not_applicable_ids = {
        row["requirement_id"] or row["matrix_id"]
        for row in raw_rows
        if row["pitch_disposition"] == "not-applicable"
    }
    assert not_applicable_ids == {
        "AREA-1516.1-10",
        "HLA1516.1-SUP-001",
    }

    not_yet_tested_ids = {
        row["requirement_id"] or row["matrix_id"]
        for row in raw_rows
        if row["pitch_disposition"] == "not-yet-tested"
    }
    assert len(not_yet_tested_ids) == 84
    assert "REQ-RTI-SS-10_4-getFederateHandle" in not_yet_tested_ids
    assert "REQ-RTI-SS-10_41-evokeCallback" in not_yet_tested_ids
    assert "HLA1516.1-SUP-10.17-001" in not_yet_tested_ids

    for requirement_id in {
        "REQ-RTI-SS-10_4-getFederateHandle",
        "REQ-RTI-SS-10_41-evokeCallback",
        "HLA1516.1-SUP-10.17-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "not-yet-tested"
        assert "analysis/compliance/section10_backend_matrix.json" in row["evidence_refs"]


def test_pitch_clause12_designator_rows_are_explicitly_not_yet_tested():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    raw_rows = [
        row
        for row in payload["rows"]
        if row.get("document") == "IEEE 1516.1-2010 (2010 edition)" and row.get("clause_root") == "12"
    ]
    rows = {row["requirement_id"] or row["matrix_id"]: row for row in raw_rows if row.get("requirement_id") or row.get("matrix_id")}

    assert len(raw_rows) == 10
    assert not {row["requirement_id"] for row in raw_rows if row["pitch_disposition"] == "classification-required"}

    clause12_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "12")
    assert clause12_summary == {
        "not-applicable": 1,
        "not-yet-tested": 9,
        "total": 10,
    }

    for requirement_id in {
        "REQ-RTI-PLM-12_2-decodeAttributeHandle",
        "REQ-RTI-PLM-12_2-decodeDimensionHandle",
        "REQ-RTI-PLM-12_2-decodeFederateHandle",
        "REQ-RTI-PLM-12_2-decodeInteractionClassHandle",
        "REQ-RTI-PLM-12_2-decodeMessageRetractionHandle",
        "REQ-RTI-PLM-12_2-decodeObjectClassHandle",
        "REQ-RTI-PLM-12_2-decodeObjectInstanceHandle",
        "REQ-RTI-PLM-12_2-decodeParameterHandle",
        "REQ-RTI-PLM-12_2-decodeRegionHandle",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "not-yet-tested"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_support_services.py::run_support_factory_and_decode_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_support_services_backend_matrix.py::test_python_backend_support_factory_and_decode_matrix"
            in row["evidence_refs"]
        )


def test_pitch_requirement_disposition_tracks_supporting_slices_and_non_omt_classification():
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))
    rows = {
        row["requirement_id"] or row["matrix_id"]: row
        for row in payload["rows"]
        if row.get("requirement_id") or row.get("matrix_id")
    }

    save_restore_slice = rows["REQ-SAVE-RESTORE-001"]
    assert save_restore_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_save_restore_scenario"
        in save_restore_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_save_restore_matrix" in save_restore_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_save_restore_matrix" in save_restore_slice["evidence_refs"]

    supporting_restore_slices = {
        "REQ-SAVE-RESTORE-OBJECT-STATE-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_object_state_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_object_state_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_object_state_matrix",
        ),
        "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_federate_local_state_scenario",
            "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_restore_federate_local_state_matrix",
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_restore_federate_local_state_matrix",
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_state_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_state",
            "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_restore_scenario",
            "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline_restore",
        ),
        "REQ-SAVE-RESTORE-CALLBACK-POLICY-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_callback_policy_scenario",
            "tests/verification/test_compliance_slice_v011.py::test_restore_treats_callback_enablement_as_runtime_policy_not_saved_state",
        ),
        "REQ-SAVE-RESTORE-TRANSIENT-STATE-001": (
            "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_transient_state_scenario",
            "tests/verification/test_compliance_slice_v011.py::test_restore_discards_pre_restore_callback_queue_and_retraction_bookkeeping",
        ),
    }
    for requirement_id, expected_refs in supporting_restore_slices.items():
        row = rows[requirement_id]
        expected_disposition = "not-yet-tested"
        if requirement_id in {
            "REQ-SAVE-RESTORE-OBJECT-STATE-001",
            "REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001",
        }:
            expected_disposition = "verified"
        elif requirement_id in {
            "REQ-SAVE-RESTORE-CALLBACK-POLICY-001",
            "REQ-SAVE-RESTORE-TRANSIENT-STATE-001",
        }:
            expected_disposition = "not-applicable"
        assert row["pitch_disposition"] == expected_disposition
        for ref in expected_refs:
            assert ref in row["evidence_refs"]

    omt_parse_slice = rows["REQ-OMT-PARSE-001"]
    assert omt_parse_slice["pitch_disposition"] == "not-applicable"
    assert "src/hla2010/fom.py::parse_fom_xml" in omt_parse_slice["evidence_refs"]
    assert "tests/factories/test_fom_omt_parsing.py" in omt_parse_slice["evidence_refs"]
    assert "analysis/compliance/verification_assets.json" in omt_parse_slice["evidence_refs"]

    target_radar_slice = rows["SCENARIO-TARGET-RADAR-001"]
    assert target_radar_slice["pitch_disposition"] == "not-applicable"
    assert "tests/scenarios/test_target_radar_scenario.py" in target_radar_slice["evidence_refs"]
    assert "analysis/compliance/verification_assets.json" in target_radar_slice["evidence_refs"]
    assert (
        "docs/evidence/hla2010_python_verification_evidence_v0_13/docs/mom_table_verification_v0_12.md"
        in target_radar_slice["evidence_refs"]
    )

    remaining_clause4_non_omt_classification_required = {
        requirement_id
        for requirement_id, row in rows.items()
        if row["clause_root"] == "4"
        and row["pitch_disposition"] == "classification-required"
        and row["document"] != "IEEE 1516.2-2010 (2010 edition)"
    }
    assert remaining_clause4_non_omt_classification_required == set()

    clause5_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "5")
    assert clause5_summary == {
        "blocked": 2,
        "not-applicable": 5,
        "total": 52,
        "verified": 45,
    }

    declaration_rows = {
        "REQ-RTI-DM-5_2-publishObjectClassAttributes",
        "REQ-RTI-DM-5_3-unpublishObjectClassAttributes",
        "REQ-RTI-DM-5_4-publishInteractionClass",
        "REQ-RTI-DM-5_5-unpublishInteractionClass",
        "REQ-RTI-DM-5_6-subscribeObjectClassAttributes",
        "REQ-RTI-DM-5_7-unsubscribeObjectClassAttributes",
        "REQ-RTI-DM-5_8-subscribeInteractionClass",
        "REQ-RTI-DM-5_9-unsubscribeInteractionClass",
        "REQ-FED-DM-5_10-startRegistrationForObjectClass",
        "REQ-FED-DM-5_11-stopRegistrationForObjectClass",
        "REQ-FED-DM-5_12-turnInteractionsOn",
        "REQ-FED-DM-5_13-turnInteractionsOff",
        "HLA1516.1-DM-5.1-001",
        "HLA1516.1-DM-5.1-002",
        "HLA1516.1-DM-5.1-003",
        "HLA1516.1-DM-5.1.2-001",
        "HLA1516.1-DM-5.1.2-002",
        "HLA1516.1-DM-5.1.3-001",
        "HLA1516.1-DM-5.1.3-002",
        "HLA1516.1-DM-5.10-001",
        "HLA1516.1-DM-5.11-001",
        "HLA1516.1-DM-5.12-001",
        "HLA1516.1-DM-5.13-001",
        "HLA1516.1-DM-5.2-001",
        "HLA1516.1-DM-5.2-002",
        "HLA1516.1-DM-5.3-001",
        "HLA1516.1-DM-5.4-001",
        "HLA1516.1-DM-5.4-002",
        "HLA1516.1-DM-5.5-001",
        "HLA1516.1-DM-5.6-001",
        "HLA1516.1-DM-5.6-002",
        "HLA1516.1-DM-5.6-003",
        "HLA1516.1-DM-5.7-001",
        "HLA1516.1-DM-5.7-002",
        "HLA1516.1-DM-5.8-001",
        "HLA1516.1-DM-5.8-002",
        "HLA1516.1-DM-5.9-001",
    }
    for requirement_id in declaration_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_management_matrix" in row["evidence_refs"]

    update_rate_declaration_row = rows["HLA1516.1-DM-5.1.6-001"]
    assert update_rate_declaration_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_update_rate.py::run_update_rate_scenario"
        in update_rate_declaration_row["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_update_rate_matrix" in update_rate_declaration_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_update_rate_matrix" in update_rate_declaration_row["evidence_refs"]

    declaration_overload_rows = {
        "REQ-RTI-DM-5_3-unpublishObjectClass",
        "REQ-RTI-DM-5_6-subscribeObjectClassAttributesPassively",
        "REQ-RTI-DM-5_7-unsubscribeObjectClass",
        "REQ-RTI-DM-5_8-subscribeInteractionClassPassively",
    }
    for requirement_id in declaration_overload_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_management_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_management_overload_matrix"
            in row["evidence_refs"]
        )
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_management_overload_matrix"
            in row["evidence_refs"]
        )

    invalid_attribute_publication_row = rows["HLA1516.1-DM-5.2-003"]
    assert invalid_attribute_publication_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_invalid_attribute_publication_scenario"
        in invalid_attribute_publication_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_invalid_attribute_publication_matrix"
        in invalid_attribute_publication_row["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_invalid_attribute_publication_matrix"
        in invalid_attribute_publication_row["evidence_refs"]
    )

    declaration_time_independence_row = rows["HLA1516.1-DM-5.1-004"]
    assert declaration_time_independence_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_time_managed_declaration_independence_scenario"
        in declaration_time_independence_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_time_managed_declaration_independence_matrix"
        in declaration_time_independence_row["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_time_managed_declaration_independence_matrix"
        in declaration_time_independence_row["evidence_refs"]
    )

    single_superclass_row = rows["HLA1516.1-DM-5.1.1-001"]
    assert single_superclass_row["pitch_disposition"] == "not-applicable"
    assert "src/hla2010/fom.py::parse_fom_xml" in single_superclass_row["evidence_refs"]
    assert "src/hla2010/fom.py::merge_fom_modules" in single_superclass_row["evidence_refs"]
    assert "tests/factories/test_fom_omt_parsing.py" in single_superclass_row["evidence_refs"]
    assert "analysis/compliance/verification_assets.json" in single_superclass_row["evidence_refs"]

    inherited_attribute_row = rows["HLA1516.1-DM-5.1.1-002"]
    assert inherited_attribute_row["pitch_disposition"] == "not-applicable"
    assert "src/hla2010/fom.py::parse_fom_xml" in inherited_attribute_row["evidence_refs"]
    assert "tests/factories/test_fom_omt_parsing.py" in inherited_attribute_row["evidence_refs"]
    assert "analysis/compliance/verification_assets.json" in inherited_attribute_row["evidence_refs"]

    inherited_parameter_row = rows["HLA1516.1-DM-5.1.1-003"]
    assert inherited_parameter_row["pitch_disposition"] == "not-applicable"
    assert "src/hla2010/fom.py::parse_fom_xml" in inherited_parameter_row["evidence_refs"]
    assert "tests/factories/test_fom_omt_parsing.py" in inherited_parameter_row["evidence_refs"]
    assert "analysis/compliance/verification_assets.json" in inherited_parameter_row["evidence_refs"]

    unpublish_object_row = rows["HLA1516.1-DM-5.3-002"]
    assert unpublish_object_row["pitch_disposition"] == "blocked"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_unpublish_rejection_scenario"
        in unpublish_object_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_unpublish_rejection_matrix"
        in unpublish_object_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_unpublish_rejection_matrix" in unpublish_object_row["evidence_refs"]

    unpublish_interaction_row = rows["HLA1516.1-DM-5.5-002"]
    assert unpublish_interaction_row["pitch_disposition"] == "blocked"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_declaration.py::run_declaration_unpublish_rejection_scenario"
        in unpublish_interaction_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_declaration_unpublish_rejection_matrix"
        in unpublish_interaction_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_declaration_unpublish_rejection_matrix" in unpublish_interaction_row["evidence_refs"]

    remaining_clause5_classification_required = {
        requirement_id
        for requirement_id, row in rows.items()
        if row["clause_root"] == "5"
        and row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["pitch_disposition"] == "classification-required"
    }
    assert remaining_clause5_classification_required == set()

    clause6_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "6")
    assert clause6_summary == {
        "not-applicable": 2,
        "not-yet-tested": 3,
        "total": 119,
        "vendor-divergent": 9,
        "verified": 105,
    }

    for requirement_id in {
        "REQ-RTI-OM-6_2-reserveObjectInstanceName",
        "REQ-FED-OM-6_3-objectInstanceNameReservationSucceeded",
        "REQ-FED-OM-6_3-objectInstanceNameReservationFailed",
        "REQ-RTI-OM-6_4-releaseObjectInstanceName",
        "REQ-RTI-OM-6_5-reserveMultipleObjectInstanceName",
        "REQ-FED-OM-6_6-multipleObjectInstanceNameReservationSucceeded",
        "REQ-FED-OM-6_6-multipleObjectInstanceNameReservationFailed",
        "REQ-RTI-OM-6_7-releaseMultipleObjectInstanceName",
        "REQ-RTI-OM-6_8-registerObjectInstance",
        "REQ-FED-OM-6_9-discoverObjectInstance",
        "REQ-FED-OM-6_9-hasProducingFederate",
        "REQ-FED-OM-6_9-getProducingFederate",
        "REQ-FED-OM-6_9-hasSentRegions",
        "REQ-FED-OM-6_9-getSentRegions",
        "REQ-FED-OM-6_11-reflectAttributeValues",
        "REQ-FED-OM-6_13-receiveInteraction",
        "REQ-RTI-OM-6_14-deleteObjectInstance",
        "REQ-FED-OM-6_15-removeObjectInstance",
        "REQ-RTI-OM-6_16-localDeleteObjectInstance",
        "REQ-FED-OM-6_17-attributesInScope",
        "REQ-FED-OM-6_18-attributesOutOfScope",
        "REQ-RTI-OM-6_19-requestAttributeValueUpdate",
        "REQ-FED-OM-6_20-provideAttributeValueUpdate",
        "REQ-FED-OM-6_21-turnUpdatesOnForObjectInstance",
        "REQ-FED-OM-6_22-turnUpdatesOffForObjectInstance",
        "REQ-RTI-OM-6_23-requestAttributeTransportationTypeChange",
        "REQ-FED-OM-6_24-confirmAttributeTransportationTypeChange",
        "REQ-RTI-OM-6_25-queryAttributeTransportationType",
        "REQ-FED-OM-6_26-reportAttributeTransportationType",
        "REQ-RTI-OM-6_27-requestInteractionTransportationTypeChange",
        "REQ-FED-OM-6_28-confirmInteractionTransportationTypeChange",
        "REQ-RTI-OM-6_29-queryInteractionTransportationType",
        "REQ-FED-OM-6_30-reportInteractionTransportationType",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        if requirement_id.startswith(("REQ-RTI-OM-6_23", "REQ-FED-OM-6_24", "REQ-RTI-OM-6_25", "REQ-FED-OM-6_26", "REQ-RTI-OM-6_27", "REQ-FED-OM-6_28", "REQ-RTI-OM-6_29", "REQ-FED-OM-6_30")):
            assert (
                "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix" in row["evidence_refs"]
            if requirement_id in {
                "REQ-RTI-OM-6_23-requestAttributeTransportationTypeChange",
                "REQ-RTI-OM-6_27-requestInteractionTransportationTypeChange",
            }:
                assert (
                    "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario"
                    in row["evidence_refs"]
                )
                assert (
                    "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix"
                    in row["evidence_refs"]
                )
                assert (
                    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix"
                    in row["evidence_refs"]
                )
        elif requirement_id == "REQ-RTI-OM-6_19-requestAttributeValueUpdate":
            assert (
                "packages/hla-verification/src/hla.verification/scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix" in row["evidence_refs"]
        elif requirement_id == "REQ-RTI-OM-6_16-localDeleteObjectInstance":
            assert (
                "packages/hla-verification/src/hla.verification/scenario_local_delete.py::run_local_delete_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_local_delete_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_local_delete_matrix" in row["evidence_refs"]
        elif requirement_id.startswith(("REQ-RTI-OM-6_2", "REQ-FED-OM-6_3", "REQ-RTI-OM-6_4", "REQ-RTI-OM-6_5", "REQ-FED-OM-6_6", "REQ-RTI-OM-6_7")):
            assert (
                "packages/hla-verification/src/hla.verification/scenario_name_reservation.py::run_name_reservation_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_name_reservation_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_name_reservation_matrix" in row["evidence_refs"]
        elif requirement_id.startswith(("REQ-FED-OM-6_17", "REQ-FED-OM-6_18", "REQ-FED-OM-6_20", "REQ-FED-OM-6_21", "REQ-FED-OM-6_22")):
            assert (
                "packages/hla-verification/src/hla.verification/scenario_update_advisory.py::run_update_advisory_callback_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_update_advisory_callback_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_update_advisory_callback_matrix" in row["evidence_refs"]
        elif requirement_id.startswith("REQ-FED-OM-6_9-") and requirement_id != "REQ-FED-OM-6_9-discoverObjectInstance":
            assert (
                "packages/hla-verification/src/hla.verification/scenario_discovery_metadata.py::run_discovery_metadata_callback_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_metadata_callback_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_metadata_callback_matrix" in row["evidence_refs"]
        else:
            assert (
                "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_exchange_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-OWN-7_2-unconditionalAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_10-attributeOwnershipUnavailable",
        "REQ-FED-OWN-7_7-attributeOwnershipAcquisitionNotification",
        "REQ-RTI-OWN-7_9-attributeOwnershipAcquisitionIfAvailable",
        "REQ-RTI-OWN-7_17-queryAttributeOwnership",
        "REQ-FED-OWN-7_18-attributeIsNotOwned",
        "REQ-RTI-OWN-7_19-isAttributeOwnedByFederate",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        if requirement_id == "REQ-FED-OWN-7_10-attributeOwnershipUnavailable":
            assert (
                "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_unavailable_scenario"
                in row["evidence_refs"]
            )
            assert (
                "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix"
                in row["evidence_refs"]
            )
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix" in row["evidence_refs"]
        else:
            assert (
                "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario"
                in row["evidence_refs"]
            )
            assert "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_matrix" in row["evidence_refs"]
            assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_matrix" in row["evidence_refs"]

    inform_row = rows["REQ-FED-OWN-7_18-informAttributeOwnership"]
    assert inform_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario"
        in inform_row["evidence_refs"]
    )
    assert "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_matrix" in inform_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_matrix" in inform_row["evidence_refs"]

    extracted_clause6_rows = {
        "HLA1516.1-OM-6.2-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.3-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.4-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.5-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.6-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.7-001": "scenario_name_reservation.py::run_name_reservation_scenario",
        "HLA1516.1-OM-6.1-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.1-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-003": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.10-005": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.1-002": "scenario_discovery_class.py::run_discovery_class_scenario",
        "HLA1516.1-OM-6.1.1-003": "scenario_discovery_class.py::run_discovery_class_scenario",
        "HLA1516.1-OM-6.1.1-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.2-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.3-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.4-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.5-001": "scenario_object_scope.py::run_object_scope_relevance_scenario",
        "HLA1516.1-OM-6.1.7-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.11-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.12-001": "scenario_update_rate.py::run_update_rate_scenario",
        "HLA1516.1-OM-6.12-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-003": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.12-005": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-003": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.8-004": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.9-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.11-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.11-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.13-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.14-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.14-002": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.15-001": "scenario_exchange.py::run_two_federate_exchange_scenario",
        "HLA1516.1-OM-6.1.6-001": "scenario_local_delete.py::run_local_delete_scenario",
        "HLA1516.1-OM-6.16-001": "scenario_local_delete.py::run_local_delete_scenario",
        "HLA1516.1-OM-6.16-002": "scenario_local_delete.py::run_local_delete_scenario",
        "HLA1516.1-OM-6.17-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.18-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.19-001": "scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
        "HLA1516.1-OM-6.19-002": "scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario",
        "HLA1516.1-OM-6.21-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.21-002": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.22-001": "scenario_update_advisory.py::run_update_advisory_callback_scenario",
        "HLA1516.1-OM-6.1.10-002": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.1.10-003": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.23-002": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.24-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.24-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "HLA1516.1-OM-6.25-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.26-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.26-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "HLA1516.1-OM-6.27-002": "scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
        "HLA1516.1-OM-6.28-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.28-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "HLA1516.1-OM-6.29-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.30-002": "scenario_transportation_type.py::run_transportation_type_scenario",
        "HLA1516.1-OM-6.30-003": "scenario_transportation_type.py::run_transportation_type_rejection_scenario",
    }
    for requirement_id, harness_ref in extracted_clause6_rows.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert any(harness_ref in ref for ref in row["evidence_refs"])

    for requirement_id in {
        "REQ-RTI-OM-6_10-updateAttributeValues",
        "REQ-RTI-OM-6_12-sendInteraction",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_exchange_matrix" in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-OM-6.10-005",
        "HLA1516.1-OM-6.12-005",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario"
            in row["evidence_refs"]
        )
        assert (
            "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_backend_exchange_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_exchange_matrix" in row["evidence_refs"]
        assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix" in row["evidence_refs"]

    vendor_divergent_clause6_rows = {
        "HLA1516.1-OM-6.1.10-001",
        "HLA1516.1-OM-6.23-001",
        "HLA1516.1-OM-6.24-001",
        "HLA1516.1-OM-6.25-001",
        "HLA1516.1-OM-6.26-001",
        "HLA1516.1-OM-6.27-001",
        "HLA1516.1-OM-6.28-001",
        "HLA1516.1-OM-6.29-001",
        "HLA1516.1-OM-6.30-001",
    }
    for requirement_id in vendor_divergent_clause6_rows:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert "packages/hla-vendor-pitch/docs/evidence/pitch_transport_subset_vendor_divergence_2026-06-11.md" in row["evidence_refs"]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario"
            in row["evidence_refs"]
        )
        if requirement_id in {
            "HLA1516.1-OM-6.1.10-001",
            "HLA1516.1-OM-6.23-001",
            "HLA1516.1-OM-6.27-001",
        }:
            assert (
                "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario"
                in row["evidence_refs"]
            )
            assert (
                "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix"
                in row["evidence_refs"]
            )
            assert (
                "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix"
                in row["evidence_refs"]
            )

    discovery_class_slice = rows["REQ-OM-DISCOVERY-CLASS-001"]
    assert discovery_class_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_discovery_class.py::run_discovery_class_scenario"
        in discovery_class_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_class_matrix" in discovery_class_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_class_matrix" in discovery_class_slice["evidence_refs"]

    reflect_known_class_slice = rows["REQ-OM-REFLECT-KNOWN-CLASS-001"]
    assert reflect_known_class_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_discovery_class.py::run_discovery_class_scenario"
        in reflect_known_class_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_discovery_class_matrix" in reflect_known_class_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_discovery_class_matrix" in reflect_known_class_slice["evidence_refs"]

    local_knowledge_slice = rows["REQ-OM-LOCAL-KNOWLEDGE-001"]
    assert local_knowledge_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_local_delete.py::run_local_delete_scenario"
        in local_knowledge_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_local_delete_matrix" in local_knowledge_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_local_delete_matrix" in local_knowledge_slice["evidence_refs"]

    for requirement_id in {
        "REQ-OM-ORPHAN-KNOWLEDGE-001",
        "REQ-OM-ORPHAN-LIFECYCLE-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_orphan_object.py::run_orphan_object_lifecycle_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_orphan_object_lifecycle_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_orphan_object_lifecycle_matrix" in row["evidence_refs"]

    timed_delete_slice = rows["REQ-OM-TIMED-DELETE-REMOVE-001"]
    assert timed_delete_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_timed_delete.py::run_timed_delete_scenario"
        in timed_delete_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_timed_delete_matrix" in timed_delete_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_timed_delete_matrix" in timed_delete_slice["evidence_refs"]

    attribute_relevance_slice = rows["REQ-OM-ATTRIBUTE-RELEVANCE-001"]
    assert attribute_relevance_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_object_scope.py::run_object_scope_relevance_scenario"
        in attribute_relevance_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_object_scope_relevance_matrix" in attribute_relevance_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_object_scope_relevance_matrix" in attribute_relevance_slice["evidence_refs"]

    scope_callbacks_slice = rows["REQ-OM-SCOPE-CALLBACKS-001"]
    assert scope_callbacks_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_object_scope.py::run_object_scope_relevance_scenario"
        in scope_callbacks_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_object_scope_relevance_matrix" in scope_callbacks_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_object_scope_relevance_matrix" in scope_callbacks_slice["evidence_refs"]

    request_value_update_slice = rows["REQ-OM-REQUEST-VALUE-UPDATE-001"]
    assert request_value_update_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_request_attribute_value_update.py::run_request_attribute_value_update_scenario"
        in request_value_update_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_matrix" in request_value_update_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_matrix" in request_value_update_slice["evidence_refs"]

    request_value_update_routing_slice = rows["REQ-OM-REQUEST-VALUE-UPDATE-ROUTING-001"]
    assert request_value_update_routing_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_request_attribute_value_update.py::run_request_attribute_value_update_routing_scenario"
        in request_value_update_routing_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_request_attribute_value_update_routing_matrix" in request_value_update_routing_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_request_attribute_value_update_routing_matrix" in request_value_update_routing_slice["evidence_refs"]

    transport_report_slice = rows["REQ-OM-TRANSPORT-REPORT-001"]
    assert transport_report_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario"
        in transport_report_slice["evidence_refs"]
    )
    assert (
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_rejection_scenario"
        in transport_report_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_matrix" in transport_report_slice["evidence_refs"]
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_rejection_matrix" in transport_report_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_matrix" in transport_report_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_rejection_matrix" in transport_report_slice["evidence_refs"]

    transport_best_effort_slice = rows["REQ-OM-TRANSPORT-BEST-EFFORT-001"]
    assert transport_best_effort_slice["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario"
        in transport_best_effort_slice["evidence_refs"]
    )
    assert "tests/scenarios/test_object_management_backend_matrix.py::test_python_transportation_type_restore_persistence_matrix" in transport_best_effort_slice["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_transportation_type_restore_persistence_matrix" in transport_best_effort_slice["evidence_refs"]

    discovery_lifecycle_slice = rows["REQ-OM-DISCOVERY-LIFECYCLE-001"]
    assert discovery_lifecycle_slice["pitch_disposition"] == "verified"
    for harness_ref in (
        "packages/hla-verification/src/hla.verification/scenario_exchange.py::run_two_federate_exchange_scenario",
        "packages/hla-verification/src/hla.verification/scenario_discovery_class.py::run_discovery_class_scenario",
        "packages/hla-verification/src/hla.verification/scenario_timed_delete.py::run_timed_delete_scenario",
    ):
        assert harness_ref in discovery_lifecycle_slice["evidence_refs"]

    omt_conformance_row = rows["HLA1516.2-OMT-6-001"]
    assert omt_conformance_row["pitch_disposition"] == "verified"
    assert "docs/verification/requirements_hierarchy.md" in omt_conformance_row["evidence_refs"]
    assert "tests/verification/test_requirement_traceability_1516_2_v013.py" in omt_conformance_row["evidence_refs"]

    omt_conformance_area = rows["REQ-OMT-6-conformance"]
    assert omt_conformance_area["pitch_disposition"] == "not-applicable"
    assert "HLA1516.2-OMT-6-001" not in omt_conformance_area["evidence_refs"]

    transport_scope_slice = rows["REQ-OM-TRANSPORT-SCOPE-001"]
    assert transport_scope_slice["pitch_disposition"] == "vendor-divergent"
    for harness_ref in (
        "packages/hla-verification/src/hla.verification/scenario_object_scope.py::run_object_scope_relevance_scenario",
        "packages/hla-verification/src/hla.verification/scenario_local_delete.py::run_local_delete_scenario",
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_scenario",
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_rejection_scenario",
        "packages/hla-verification/src/hla.verification/scenario_transportation_type.py::run_transportation_type_restore_persistence_scenario",
    ):
        assert harness_ref in transport_scope_slice["evidence_refs"]

    clause6_rows = {
        requirement_id: row
        for requirement_id, row in rows.items()
        if requirement_id.startswith("HLA1516.1-OM-6.")
    }
    clause6_disposition_counts: dict[str, int] = {}
    for row in clause6_rows.values():
        clause6_disposition_counts[row["pitch_disposition"]] = clause6_disposition_counts.get(row["pitch_disposition"], 0) + 1
    assert clause6_disposition_counts == {
        "not-yet-tested": 3,
        "vendor-divergent": 9,
        "verified": 70,
    }
    assert {
        requirement_id
        for requirement_id, row in clause6_rows.items()
        if row["pitch_disposition"] != "verified"
    } == vendor_divergent_clause6_rows | {
        "HLA1516.1-OM-6.1.10-004",
        "HLA1516.1-OM-6.25-003",
        "HLA1516.1-OM-6.29-003",
    }

    residual_clause6_rows = {
        row["requirement_id"] or row["matrix_id"]: row["pitch_disposition"]
        for row in payload["rows"]
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["clause_root"] == "6"
        and row["pitch_disposition"] != "verified"
    }
    assert residual_clause6_rows == {
        "AREA-1516.1-6": "not-applicable",
        "HLA1516.1-OM-001": "not-applicable",
        "HLA1516.1-OM-6.1.10-001": "vendor-divergent",
        "HLA1516.1-OM-6.1.10-004": "not-yet-tested",
        "HLA1516.1-OM-6.23-001": "vendor-divergent",
        "HLA1516.1-OM-6.24-001": "vendor-divergent",
        "HLA1516.1-OM-6.25-001": "vendor-divergent",
        "HLA1516.1-OM-6.25-003": "not-yet-tested",
        "HLA1516.1-OM-6.26-001": "vendor-divergent",
        "HLA1516.1-OM-6.27-001": "vendor-divergent",
        "HLA1516.1-OM-6.28-001": "vendor-divergent",
        "HLA1516.1-OM-6.29-001": "vendor-divergent",
        "HLA1516.1-OM-6.29-003": "not-yet-tested",
        "HLA1516.1-OM-6.30-001": "vendor-divergent",
    }

    remaining_clause6_classification_required = {
        requirement_id
        for requirement_id, row in rows.items()
        if row["clause_root"] == "6" and row["pitch_disposition"] == "classification-required"
    }
    assert remaining_clause6_classification_required == set()

    remaining_clause6_nonverified_counts = {
        disposition: sum(
            1
            for row in payload["rows"]
            if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
            and row["clause_root"] == "6"
            and row["pitch_disposition"] == disposition
        )
        for disposition in ("blocked", "classification-required", "not-yet-tested", "not-applicable", "vendor-divergent")
    }
    assert remaining_clause6_nonverified_counts == {
        "blocked": 0,
        "classification-required": 0,
        "not-yet-tested": 3,
        "not-applicable": 2,
        "vendor-divergent": 9,
    }

    clause7_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "7")
    assert clause7_summary == {
        "not-applicable": 2,
        "total": 39,
        "vendor-divergent": 10,
        "verified": 27,
    }

    verified_clause7_merge_rows = {
        "HLA1516.2-MERGE-7-001": "scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "HLA1516.2-OMT-7-001": "scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "HLA1516.2-OMT-7-002": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "REQ-OMT-7-merging_rules": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.2-MERGE-7.0-001": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.2-MERGE-7.0-002": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.2-MERGE-7.0-003": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.2-MERGE-7.0-004": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.2-MERGE-7.0-005": "scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "HLA1516.2-MERGE-7.0-006": "scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
        "HLA1516.2-MERGE-7.0-007": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
        "HLA1516.2-MERGE-7.0-008": "scenario_federation_lifecycle.py::run_fom_module_visibility_scenario",
        "REQ-OMT-MERGE-001": "scenario_federation_lifecycle.py::run_multi_module_fom_visibility_scenario",
    }
    for requirement_id, harness_ref in verified_clause7_merge_rows.items():
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert any(harness_ref in ref for ref in row["evidence_refs"])

    explicit_mim_merge_row = rows["HLA1516.2-MERGE-7-002"]
    assert explicit_mim_merge_row["pitch_disposition"] == "vendor-divergent"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_federation_lifecycle_scenario"
        in explicit_mim_merge_row["evidence_refs"]
    )
    assert "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_federation_lifecycle_with_mim_matrix" in explicit_mim_merge_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_federation_lifecycle_with_mim_matrix" in explicit_mim_merge_row["evidence_refs"]

    clause7_merge_requirement_ids = {
        "HLA1516.2-MERGE-7-001",
        "HLA1516.2-MERGE-7-002",
        "HLA1516.2-OMT-7-001",
        "HLA1516.2-OMT-7-002",
        "REQ-OMT-7-merging_rules",
        "HLA1516.2-MERGE-7.0-001",
        "HLA1516.2-MERGE-7.0-002",
        "HLA1516.2-MERGE-7.0-003",
        "HLA1516.2-MERGE-7.0-004",
        "HLA1516.2-MERGE-7.0-005",
        "HLA1516.2-MERGE-7.0-006",
        "HLA1516.2-MERGE-7.0-007",
        "HLA1516.2-MERGE-7.0-008",
        "REQ-OMT-MERGE-001",
    }
    remaining_clause7_classification_required = {
        requirement_id
        for requirement_id in clause7_merge_requirement_ids
        if rows[requirement_id]["pitch_disposition"] == "classification-required"
    }
    assert remaining_clause7_classification_required == set()

    rti_owned_row = rows["REQ-FED-OWN-7_18-attributeIsOwnedByRTI"]
    assert rti_owned_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_query_callback_scenario"
        in rti_owned_row["evidence_refs"]
    )
    assert "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix" in rti_owned_row["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_attribute_ownership_query_callback_matrix" in rti_owned_row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-OWN-7_8-attributeOwnershipAcquisition",
        "REQ-FED-OWN-7_11-requestAttributeOwnershipRelease",
        "REQ-RTI-OWN-7_13-attributeOwnershipDivestitureIfWanted",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_release_request_ownership_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_request_ownership_matrix"
            in row["evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_release_request_owned_attribute_probe" in row["evidence_refs"]

    release_denied = rows["REQ-RTI-OWN-7_12-attributeOwnershipReleaseDenied"]
    assert release_denied["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_release_request_ownership_scenario"
        in release_denied["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_denied_ownership_matrix"
        in release_denied["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_release_denied_ownership_matrix" in release_denied["evidence_refs"]

    non_owner_update = rows["HLA1516.1-OWN-7.1-003"]
    assert non_owner_update["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_non_owner_update_rejection_scenario"
        in non_owner_update["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_non_owner_update_rejection_matrix"
        in non_owner_update["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_non_owner_update_rejection_matrix" in non_owner_update["evidence_refs"]

    request_assumption = rows["REQ-FED-OWN-7_4-requestAttributeOwnershipAssumption"]
    assert request_assumption["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::probe_negotiated_attribute_ownership_offer"
        in request_assumption["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_negotiated_divesting_offer_probe_matrix"
        in request_assumption["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_negotiated_divesting_offer_probe" in request_assumption["evidence_refs"]

    negotiated_ownership_rows = {
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
        "HLA1516.1-OWN-7.10-001",
        "HLA1516.1-OWN-7.11-001",
    }
    for requirement_id in negotiated_ownership_rows:
        row = rows[requirement_id]
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_negotiated_attribute_ownership_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_negotiated_ownership_matrix"
            in row["evidence_refs"]
        )
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_negotiated_ownership_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation",
        "REQ-RTI-OWN-7_6-confirmDivestiture",
        "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture",
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert "packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md" in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-OWN-7.3-001",
        "HLA1516.1-OWN-7.4-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert "packages/hla-vendor-pitch/docs/evidence/pitch_negotiated_ownership_vendor_bug_2026-06-07.md" in row["evidence_refs"]

    residual_clause7_rows = {
        row["requirement_id"] or row["matrix_id"]: row["pitch_disposition"]
        for row in payload["rows"]
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["clause_root"] == "7"
        and row["pitch_disposition"] != "verified"
    }
    assert residual_clause7_rows == {
        "AREA-1516.1-7": "not-applicable",
        "HLA1516.1-OWN-001": "not-applicable",
        "REQ-RTI-OWN-7_3-negotiatedAttributeOwnershipDivestiture": "vendor-divergent",
        "REQ-FED-OWN-7_5-requestDivestitureConfirmation": "vendor-divergent",
        "REQ-RTI-OWN-7_6-confirmDivestiture": "vendor-divergent",
        "REQ-RTI-OWN-7_14-cancelNegotiatedAttributeOwnershipDivestiture": "vendor-divergent",
        "REQ-RTI-OWN-7_15-cancelAttributeOwnershipAcquisition": "vendor-divergent",
        "REQ-FED-OWN-7_16-confirmAttributeOwnershipAcquisitionCancellation": "vendor-divergent",
        "HLA1516.1-OWN-7.3-001": "vendor-divergent",
        "HLA1516.1-OWN-7.4-001": "vendor-divergent",
        "HLA1516.1-OWN-7.10-001": "vendor-divergent",
        "HLA1516.1-OWN-7.11-001": "vendor-divergent",
    }

    remaining_clause7_nonverified_counts = {
        disposition: sum(
            1
            for row in payload["rows"]
            if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
            and row["clause_root"] == "7"
            and row["pitch_disposition"] == disposition
        )
        for disposition in ("blocked", "classification-required", "not-yet-tested", "not-applicable", "vendor-divergent")
    }
    assert remaining_clause7_nonverified_counts == {
        "blocked": 0,
        "classification-required": 0,
        "not-yet-tested": 0,
        "not-applicable": 2,
        "vendor-divergent": 10,
    }

    for requirement_id in {
        "HLA1516.1-OWN-7.1-001",
        "HLA1516.1-OWN-7.1-002",
        "HLA1516.1-OWN-7.2-001",
        "HLA1516.1-OWN-7.6-001",
        "HLA1516.1-OWN-7.9-001",
        "HLA1516.1-OWN-7.7-001",
        "HLA1516.1-OWN-7.12-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_scenario"
            in row["evidence_refs"]
        )

    release_request_clause = rows["HLA1516.1-OWN-7.5-001"]
    assert release_request_clause["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_release_request_ownership_scenario"
        in release_request_clause["evidence_refs"]
    )

    no_notification_clause = rows["HLA1516.1-OWN-7.7-002"]
    assert no_notification_clause["pitch_disposition"] == "verified"
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_release_denied_ownership_matrix"
        in no_notification_clause["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_release_denied_ownership_matrix" in no_notification_clause["evidence_refs"]

    unavailable_clause = rows["HLA1516.1-OWN-7.8-001"]
    assert unavailable_clause["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_unavailable_scenario"
        in unavailable_clause["evidence_refs"]
    )

    unavailable_release_clause = rows["HLA1516.1-OWN-7.9-002"]
    assert unavailable_release_clause["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_unavailable_scenario"
        in unavailable_release_clause["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_backend_ownership_unavailable_matrix"
        in unavailable_release_clause["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ownership_unavailable_matrix" in unavailable_release_clause["evidence_refs"]

    ownership_notify_clause = rows["HLA1516.1-OWN-7.13-001"]
    assert ownership_notify_clause["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ownership.py::run_attribute_ownership_query_callback_scenario"
        in ownership_notify_clause["evidence_refs"]
    )
    assert "tests/scenarios/test_ownership_management_backend_matrix.py::test_python_attribute_ownership_query_callback_matrix" in ownership_notify_clause["evidence_refs"]
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_attribute_ownership_query_callback_matrix" in ownership_notify_clause["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-DDM-9.1-001",
        "HLA1516.1-DDM-9.1-002",
        "HLA1516.1-DDM-9.1-003",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/two_federate_suite_scenarios.py::run_suite_ddm_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_matrix" in row["evidence_refs"]

    clause9_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "9")
    assert clause9_summary == {
        "not-applicable": 2,
        "total": 31,
        "verified": 29,
    }

    clause9_rows = [
        row
        for row in payload["rows"]
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)" and row["clause_root"] == "9"
    ]
    for row in clause9_rows:
        if row["pitch_disposition"] == "not-applicable":
            continue
        refs = row["evidence_refs"]
        assert any(
            "packages/hla-verification/src/hla.verification/" in ref
            for ref in refs
        ), row["requirement_id"] or row["matrix_id"]
        assert any(ref.startswith("tests/scenarios/test_ddm_backend_matrix.py::") for ref in refs), row["requirement_id"] or row["matrix_id"]
        assert any(ref.startswith("tests/vendors/test_pitch_real_backend_matrix.py::") for ref in refs), row["requirement_id"] or row["matrix_id"]

    for requirement_id in {
        "REQ-RTI-DDM-9_2-createRegion",
        "REQ-RTI-DDM-9_3-commitRegionModifications",
        "REQ-RTI-DDM-9_10-subscribeInteractionClassWithRegions",
        "REQ-RTI-DDM-9_12-sendInteractionWithRegions",
        "HLA1516.1-DDM-9.2-001",
        "HLA1516.1-DDM-9.3-001",
        "HLA1516.1-DDM-9.10-001",
        "HLA1516.1-DDM-9.12-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/two_federate_suite_scenarios.py::run_suite_ddm_scenario"
            in row["evidence_refs"]
        )
        assert "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_matrix" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-DDM-9_4-deleteRegion",
        "REQ-RTI-DDM-9_5-registerObjectInstanceWithRegions",
        "REQ-RTI-DDM-9_6-associateRegionsForUpdates",
        "REQ-RTI-DDM-9_7-unassociateRegionsForUpdates",
        "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesWithRegions",
        "REQ-RTI-DDM-9_9-unsubscribeObjectClassAttributesWithRegions",
        "REQ-RTI-DDM-9_11-unsubscribeInteractionClassWithRegions",
        "REQ-RTI-DDM-9_13-requestAttributeValueUpdateWithRegions",
        "HLA1516.1-DDM-9.4-001",
        "HLA1516.1-DDM-9.5-001",
        "HLA1516.1-DDM-9.6-001",
        "HLA1516.1-DDM-9.7-001",
        "HLA1516.1-DDM-9.8-001",
        "HLA1516.1-DDM-9.9-001",
        "HLA1516.1-DDM-9.11-001",
        "HLA1516.1-DDM-9.13-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_object_region_lifecycle_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_object_region_lifecycle_matrix"
            in row["evidence_refs"]
        )
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_object_region_lifecycle_matrix"
            in row["evidence_refs"]
        )

    for requirement_id in {
        "REQ-RTI-DDM-9_8-subscribeObjectClassAttributesPassivelyWithRegions",
        "REQ-RTI-DDM-9_10-subscribeInteractionClassPassivelyWithRegions",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/scenario_ddm_passive_regions.py::run_ddm_passive_region_subscription_scenario"
            in row["evidence_refs"]
        )
        assert (
            "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_passive_region_subscription_matrix"
            in row["evidence_refs"]
        )
        assert (
            "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_passive_region_subscription_matrix"
            in row["evidence_refs"]
        )

    declaration_ddm_row = rows["HLA1516.1-DM-5.1.5-001"]
    assert declaration_ddm_row["pitch_disposition"] == "verified"
    assert (
        "packages/hla-verification/src/hla.verification/scenario_ddm_object_regions.py::run_ddm_declaration_gating_scenario"
        in declaration_ddm_row["evidence_refs"]
    )
    assert (
        "tests/scenarios/test_ddm_backend_matrix.py::test_python_backend_ddm_declaration_gating_matrix"
        in declaration_ddm_row["evidence_refs"]
    )
    assert (
        "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_ddm_declaration_gating_matrix"
        in declaration_ddm_row["evidence_refs"]
    )

    for requirement_id in {
        "REQ-RTI-TM-8_2-enableTimeRegulation",
        "REQ-FED-TM-8_3-timeRegulationEnabled",
        "REQ-RTI-TM-8_5-enableTimeConstrained",
        "REQ-FED-TM-8_6-timeConstrainedEnabled",
        "HLA1516.1-TM-8.2-001",
        "HLA1516.1-TM-8.2-002",
        "HLA1516.1-TM-8.2-003",
        "HLA1516.1-TM-8.5-001",
        "HLA1516.1-TM-8.5-002",
        "HLA1516.1-TM-8.5-003",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_services" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_services_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_17-queryLogicalTime",
        "HLA1516.1-TM-8.17-001",
        "HLA1516.1-TM-8.1.3-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_logical_time_query" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_logical_time_query_matrix" in row["evidence_refs"]

    clause8_summary = clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "8")
    assert clause8_summary == {
        "not-applicable": 2,
        "total": 61,
        "verified": 41,
        "vendor-divergent": 18,
    }

    for requirement_id in {
        "REQ-RTI-TM-8_4-disableTimeRegulation",
        "REQ-RTI-TM-8_7-disableTimeConstrained",
        "REQ-RTI-TM-8_14-enableAsynchronousDelivery",
        "REQ-RTI-TM-8_15-disableAsynchronousDelivery",
        "HLA1516.1-TM-8.4-001",
        "HLA1516.1-TM-8.7-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_toggle_services" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_toggle_services_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_8-timeAdvanceRequest",
        "REQ-FED-TM-8_13-timeAdvanceGrant",
        "HLA1516.1-TM-8.8-001",
        "HLA1516.1-TM-8.8-002",
        "HLA1516.1-TM-8.8-003",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_ordering_and_query_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_16-queryGALT",
        "REQ-RTI-TM-8_18-queryLITS",
        "HLA1516.1-TM-8.16-001",
        "HLA1516.1-TM-8.18-001",
        "HLA1516.1-TM-8.1.5-002",
        "HLA1516.1-TM-8.1.5-003",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_time_bound_queries" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_time_bound_query_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_9-timeAdvanceRequestAvailable",
        "REQ-RTI-TM-8_12-flushQueueRequest",
        "HLA1516.1-TM-8.12-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_flush_services" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_flush_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_23-changeAttributeOrderType",
        "REQ-RTI-TM-8_24-changeInteractionOrderType",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_order_override_services_matrix" in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-TM-8.1.4-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_early_timestamp_send_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_early_timestamp_send_rejection" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_early_timestamp_send_rejection_matrix" in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-TM-8.1-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_state_services_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_state_services" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_state_services_matrix" in row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-TM-8.1-002",
        "HLA1516.1-TM-8.1.1-001",
        "HLA1516.1-TM-8.1.2-004",
        "HLA1516.1-TM-8.1.3-002",
        "HLA1516.1-TM-8.1.3-003",
        "HLA1516.1-TM-8.1.5-001",
        "HLA1516.1-TM-8.1.6-001",
        "HLA1516.1-TM-8.1.7-001",
        "REQ-TIME-ORDER-001",
        "REQ-RTI-TM-8_10-nextMessageRequest",
        "HLA1516.1-TM-8.10-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_ordering_and_query_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_ordering_and_queries" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_ordering_and_queries_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable",
        "REQ-RTI-TM-8_21-retract",
        "HLA1516.1-TM-8.21-001",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_available_and_retraction_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_available_and_retraction" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_available_and_retraction_matrix" in row["evidence_refs"]

    request_retraction_row = rows["REQ-FED-TM-8_22-requestRetraction"]
    assert request_retraction_row["pitch_disposition"] == "vendor-divergent"
    assert (
        "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_request_retraction_case"
        in request_retraction_row["evidence_refs"]
    )
    assert (
        "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_request_retraction_callback"
        in request_retraction_row["evidence_refs"]
    )
    assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_request_retraction_callback_matrix" in request_retraction_row["evidence_refs"]

    for requirement_id in {
        "HLA1516.1-TM-8.1.2-001",
        "HLA1516.1-TM-8.1.2-002",
        "HLA1516.1-TM-8.1.2-003",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "vendor-divergent"
        assert (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case"
            in row["evidence_refs"]
        )
        assert "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_section8_order_override_services_matrix" in row["evidence_refs"]

    for requirement_id in {
        "REQ-RTI-TM-8_19-modifyLookahead",
        "REQ-RTI-TM-8_20-queryLookahead",
        "HLA1516.1-TM-8.19-001",
        "HLA1516.1-TM-8.1.4-002",
        "HLA1516.1-TM-8.1.4-003",
    }:
        row = rows[requirement_id]
        assert row["pitch_disposition"] == "verified"
        assert "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_state_services" in row["evidence_refs"]
        assert "tests/time/test_lookahead_backend_matrix.py::test_lookahead_backend_matrix_blocks_early_timestamped_send" in row["evidence_refs"]
        assert "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lookahead_matrix" in row["evidence_refs"]

    residual_clause8_rows = {
        row["requirement_id"] or row["matrix_id"]: row["pitch_disposition"]
        for row in payload["rows"]
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["clause_root"] == "8"
        and row["pitch_disposition"] != "verified"
    }
    assert residual_clause8_rows == {
        "REQ-RTI-TM-8_10-nextMessageRequest": "vendor-divergent",
        "REQ-RTI-TM-8_11-nextMessageRequestAvailable": "vendor-divergent",
        "REQ-RTI-TM-8_21-retract": "vendor-divergent",
        "REQ-FED-TM-8_22-requestRetraction": "vendor-divergent",
        "AREA-1516.1-8": "not-applicable",
        "HLA1516.1-TM-001": "not-applicable",
        "HLA1516.1-TM-8.1-001": "vendor-divergent",
        "HLA1516.1-TM-8.1-002": "vendor-divergent",
        "HLA1516.1-TM-8.1.1-001": "vendor-divergent",
        "HLA1516.1-TM-8.1.2-001": "vendor-divergent",
        "HLA1516.1-TM-8.1.2-002": "vendor-divergent",
        "HLA1516.1-TM-8.1.2-003": "vendor-divergent",
        "HLA1516.1-TM-8.1.2-004": "vendor-divergent",
        "HLA1516.1-TM-8.1.3-002": "vendor-divergent",
        "HLA1516.1-TM-8.1.3-003": "vendor-divergent",
        "HLA1516.1-TM-8.1.5-001": "vendor-divergent",
        "HLA1516.1-TM-8.1.6-001": "vendor-divergent",
        "HLA1516.1-TM-8.1.7-001": "vendor-divergent",
        "HLA1516.1-TM-8.10-001": "vendor-divergent",
        "HLA1516.1-TM-8.21-001": "vendor-divergent",
    }

    remaining_clause8_nonverified_counts = {
        disposition: sum(
            1
            for row in payload["rows"]
            if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
            and row["clause_root"] == "8"
            and row["pitch_disposition"] == disposition
        )
        for disposition in ("blocked", "classification-required", "not-yet-tested", "not-applicable", "vendor-divergent")
    }
    assert remaining_clause8_nonverified_counts == {
        "blocked": 0,
        "classification-required": 0,
        "not-yet-tested": 0,
        "not-applicable": 2,
        "vendor-divergent": 18,
    }

    residual_clause9_rows = {
        row["requirement_id"] or row["matrix_id"]: row["pitch_disposition"]
        for row in payload["rows"]
        if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
        and row["clause_root"] == "9"
        and row["pitch_disposition"] != "verified"
    }
    assert residual_clause9_rows == {
        "AREA-1516.1-9": "not-applicable",
        "HLA1516.1-DDM-001": "not-applicable",
    }

    remaining_clause9_nonverified_counts = {
        disposition: sum(
            1
            for row in payload["rows"]
            if row["document"] == "IEEE 1516.1-2010 (2010 edition)"
            and row["clause_root"] == "9"
            and row["pitch_disposition"] == disposition
        )
        for disposition in ("blocked", "classification-required", "not-yet-tested", "not-applicable", "vendor-divergent")
    }
    assert remaining_clause9_nonverified_counts == {
        "blocked": 0,
        "classification-required": 0,
        "not-yet-tested": 0,
        "not-applicable": 2,
        "vendor-divergent": 0,
    }


def test_discovery_payload_and_text_support_backlog_filters():
    project_root = Path(__file__).resolve().parents[2]
    payload = build_discovery_payload(project_root, backend_filter="certi-native", priority_filter="P1")

    assert payload["catalog"]["summary"]["backend_count"] == 1
    assert all(row["backend_id"] == "certi-native" for row in payload["backlog"]["rows"])
    assert all(row["priority"] == "P1" for row in payload["backlog"]["rows"])

    rendered = render_backend_compliance_catalog_text(
        payload["catalog"],
        backend_filter="certi-native",
        backlog=payload["backlog"],
        priority_filter="P1",
    )
    assert "Vendor discovery backlog:" in rendered
    assert "P1 certi-native" in rendered
    assert "priority=P1" in rendered


def test_vendor_discovery_backlog_writers_emit_generated_artifacts(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    json_path, md_path = write_vendor_discovery_backlog_artifacts(
        project_root,
        json_path=tmp_path / "vendor_discovery_backlog.json",
        markdown_path=tmp_path / "vendor_discovery_backlog.md",
    )

    assert json_path.read_text(encoding="utf-8").startswith("{\n")
    md_text = md_path.read_text(encoding="utf-8")
    assert "Vendor Discovery Backlog" in md_text
    assert "certi-native" in md_text
    assert "pitch-jpype" in md_text


def test_requirements_matrix_projects_pitch_dispositions_into_canonical_artifact() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "requirements_matrix_2010.json").read_text(encoding="utf-8"))

    summary = payload["summary"]
    assert summary["pitch_runtime_disposition_counts"]["verified"] > 0
    assert summary["pitch_runtime_disposition_counts"]["blocked"] >= 2
    assert summary["pitch_jpype_runtime_disposition_counts"]["blocked"] >= 2
    assert summary["pitch_py4j_runtime_disposition_counts"]["verified"] > 0

    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    blocked_row = rows["HLA1516.1-FM-4.1.5-001"]
    assert blocked_row["pitch_runtime_disposition"] == "blocked"
    assert blocked_row["pitch_jpype_runtime_disposition"] == "blocked"
    assert blocked_row["pitch_py4j_runtime_disposition"] == "blocked"

    verified_row = rows["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]
    assert verified_row["pitch_runtime_disposition"] == "verified"
    assert verified_row["pitch_jpype_runtime_disposition"] == "verified"
    assert verified_row["pitch_py4j_runtime_disposition"] == "verified"
    assert verified_row["python_runtime_disposition"] == "verified"
    assert verified_row["certi_runtime_disposition"] == "verified"

    certi_gap_row = rows["REQ-RTI-FM-4_16-requestFederationSave"]
    assert certi_gap_row["certi_runtime_disposition"] == "verified"

    planning_row = rows["AREA-1516.1-4"]
    assert planning_row["python_runtime_disposition"] == "not-applicable"
    assert planning_row["certi_runtime_disposition"] == "not-applicable"
    assert planning_row["pitch_runtime_disposition"] == "not-applicable"

    assert rows["HLA1516.1-FM-4.3-MOM-001"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.5-001"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.5-002"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.2-002"]["python_runtime_disposition"] == "verified"
    assert rows["HLA1516.1-FM-4.1.5-001"]["status"] == "partial"
    assert rows["HLA1516.1-FM-4.1.5-002"]["status"] == "partial"
    assert rows["HLA1516.1-TM-8.1.2-003"]["status"] == "partial"
    assert "requirements/2010/hla1516_1_priority_backend_resolution.csv" in rows["HLA1516.1-FM-4.1.5-001"]["artifact_refs"]
    assert "requirements/2010/traceability_matrix.csv" in rows["HLA1516.1-TM-8.1.2-003"]["artifact_refs"]
    assert not rows["HLA1516.1-FM-4.1.5-001"]["artifact_refs"].startswith("[")


def test_python_and_certi_requirement_disposition_artifacts_are_generated() -> None:
    project_root = Path(__file__).resolve().parents[2]
    python_payload = json.loads((project_root / "analysis" / "compliance" / "python_requirement_disposition.json").read_text(encoding="utf-8"))
    certi_payload = json.loads((project_root / "analysis" / "compliance" / "certi_requirement_disposition.json").read_text(encoding="utf-8"))

    assert python_payload["summary"]["backend"] == "python"
    assert python_payload["summary"]["disposition_counts"]["verified"] > 0
    assert certi_payload["summary"]["backend"] == "certi"
    assert certi_payload["summary"]["disposition_counts"]["verified"] > 0
    assert certi_payload["summary"]["disposition_counts"]["classification-required"] > 0

    python_rows = {row["requirement_id"] or row["matrix_id"]: row for row in python_payload["rows"]}
    certi_rows = {row["requirement_id"] or row["matrix_id"]: row for row in certi_payload["rows"]}
    assert python_rows["REQ-RTI-FM-4_11-registerFederationSynchronizationPoint"]["runtime_disposition"] == "verified"
    assert python_rows["HLA1516.1-FM-4.3-MOM-001"]["runtime_disposition"] == "verified"
    assert python_rows["HLA1516.1-FM-4.1.5-001"]["runtime_disposition"] == "verified"
    assert certi_rows["REQ-RTI-FM-4_16-requestFederationSave"]["runtime_disposition"] == "verified"


def test_backend_requirement_disposition_artifacts_keep_corrected_ddm_9_12_and_9_13_titles() -> None:
    project_root = Path(__file__).resolve().parents[2]
    expected_titles = {
        "HLA1516.1-DDM-9.12-001": "RTI shall route interactions based on region overlap where dimensions apply",
        "HLA1516.1-DDM-9.13-001": "RTI shall route attribute-value update requests based on region overlap",
    }
    artifact_paths = {
        "python": project_root / "analysis" / "compliance" / "python_requirement_disposition.json",
        "certi": project_root / "analysis" / "compliance" / "certi_requirement_disposition.json",
        "pitch": project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json",
        "portico": project_root / "analysis" / "compliance" / "portico_requirement_disposition.json",
    }

    for backend, path in artifact_paths.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = {row["requirement_id"]: row for row in payload["rows"]}
        for requirement_id, expected_title in expected_titles.items():
            assert rows[requirement_id]["title"] == expected_title, (backend, requirement_id)


def test_python_tranche_clauses_4_6_7_8_9_use_shared_harness_evidence_only() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "python_requirement_disposition.json").read_text(encoding="utf-8"))

    allowed_prefixes_by_clause = {
        "4": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
            "tests/scenarios/test_federation_management_backend_matrix.py::",
        ),
        "6": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_object_management_backend_matrix.py::",
        ),
        "7": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_ownership_management_backend_matrix.py::",
        ),
        "8": (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::",
            "tests/time/test_section8_backend_matrix.py::",
            "tests/time/test_lookahead_backend_matrix.py::",
        ),
        "9": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_ddm_backend_matrix.py::",
        ),
    }
    clause6_supported_subset_direct_evidence_rows = {
        "HLA1516.1-OM-6.1.10-004",
        "HLA1516.1-OM-6.1.12-001",
        "HLA1516.1-OM-6.23-003",
        "HLA1516.1-OM-6.24-004",
        "HLA1516.1-OM-6.25-003",
        "HLA1516.1-OM-6.26-004",
        "HLA1516.1-OM-6.27-003",
        "HLA1516.1-OM-6.28-004",
        "HLA1516.1-OM-6.29-003",
        "HLA1516.1-OM-6.30-004",
    }
    supported_subset_direct_evidence_prefixes = (
        "tests/backends/test_python_backend_object_ownership_extended.py::",
        "tests/backends/test_python_backend_support_services.py::",
        "tests/verification/test_compliance_slice_v011.py::",
    )

    for clause_root, allowed_prefixes in allowed_prefixes_by_clause.items():
        runtime_rows = [
            row
            for row in payload["rows"]
            if row.get("document") == "IEEE 1516.1-2010 (2010 edition)"
            and row.get("clause_root") == clause_root
            and row.get("runtime_disposition") in {"verified", "vendor-divergent"}
        ]
        assert runtime_rows
        for row in runtime_rows:
            refs = row["evidence_refs"]
            assert refs, row["requirement_id"] or row["matrix_id"]
            allowed_for_row = allowed_prefixes
            if clause_root == "6" and row["requirement_id"] in clause6_supported_subset_direct_evidence_rows:
                allowed_for_row = allowed_prefixes + supported_subset_direct_evidence_prefixes
            assert all(ref.startswith(allowed_for_row) for ref in refs), (
                row["requirement_id"] or row["matrix_id"],
                refs,
            )


def test_pitch_tranche_clauses_4_6_7_8_9_use_shared_harness_evidence_only() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "pitch_requirement_disposition.json").read_text(encoding="utf-8"))

    allowed_prefixes_by_clause = {
        "4": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::",
            "tests/scenarios/test_federation_management_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
        ),
        "6": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_object_management_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
            "packages/hla-vendor-pitch/docs/evidence/",
        ),
        "7": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_ownership_management_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
            "packages/hla-vendor-pitch/docs/evidence/",
        ),
        "8": (
            "packages/hla-verification/src/hla.verification/section8_matrix.py::",
            "tests/time/test_section8_backend_matrix.py::",
            "tests/time/test_lookahead_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
            "packages/hla-vendor-pitch/docs/evidence/",
        ),
        "9": (
            "packages/hla-verification/src/hla.verification/",
            "tests/scenarios/test_ddm_backend_matrix.py::",
            "tests/vendors/test_pitch_real_backend_matrix.py::",
        ),
    }

    for clause_root, allowed_prefixes in allowed_prefixes_by_clause.items():
        pitch_rows = [
            row
            for row in payload["rows"]
            if row.get("document") == "IEEE 1516.1-2010 (2010 edition)"
            and row.get("clause_root") == clause_root
            and row.get("pitch_disposition") in {"verified", "vendor-divergent"}
        ]
        assert pitch_rows
        for row in pitch_rows:
            refs = row["evidence_refs"]
            assert refs, row["requirement_id"] or row["matrix_id"]
            assert not any(ref.startswith("tests/backends/") for ref in refs), row["requirement_id"]
            assert not any(ref.startswith("tests/verification/") for ref in refs), row["requirement_id"]
            assert all(ref.startswith(allowed_prefixes) for ref in refs), (
                row["requirement_id"] or row["matrix_id"],
                refs,
            )


def test_python_tranche_clause_summaries_and_reclassified_rows_are_generated() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "python_requirement_disposition.json").read_text(encoding="utf-8"))

    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "4") == {
        "not-applicable": 2,
        "total": 281,
        "verified": 279,
    }
    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "6") == {
        "not-applicable": 2,
        "total": 119,
        "verified": 117,
    }
    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "7") == {
        "not-applicable": 2,
        "total": 39,
        "verified": 37,
    }
    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "8") == {
        "not-applicable": 2,
        "total": 61,
        "verified": 59,
    }
    assert clause_summary_counts(payload["summary"]["clause_summary"], IEEE_1516_1_2010, "9") == {
        "not-applicable": 2,
        "total": 31,
        "verified": 29,
    }

    rows = {row["requirement_id"] or row["matrix_id"]: row for row in payload["rows"]}
    for requirement_id, harness_ref, backend_ref in (
        (
            "HLA1516.1-FM-4.1-005",
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_multi_participation_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix",
        ),
        (
            "HLA1516.1-FM-4.1-006",
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_multi_participation_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_multi_participation_matrix",
        ),
        (
            "HLA1516.1-FM-4.1.4.1-002",
            "packages/hla-verification/src/hla.verification/scenario_federation_lifecycle.py::run_fom_integrity_negative_scenario",
            "tests/scenarios/test_federation_lifecycle_backend_matrix.py::test_python_backend_fom_integrity_negative_matrix",
        ),
        (
            "HLA1516.1-TM-8.1.2-003",
            "packages/hla-verification/src/hla.verification/section8_matrix.py::run_section8_order_override_case",
            "tests/time/test_section8_backend_matrix.py::test_section8_backend_matrix_order_override_services",
        ),
    ):
        row = rows[requirement_id]
        assert row["runtime_disposition"] == "verified"
        assert harness_ref in row["evidence_refs"]
        assert backend_ref in row["evidence_refs"]


def test_verification_asset_bundle_includes_future_exclusion_time_order_slice() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "verification_assets.json").read_text(encoding="utf-8"))
    rows = {row["asset_id"]: row for row in payload["assets"]}

    row = rows["REQ-TIME-ORDER-001"]
    assert row["status"] == "implemented-slice"
    assert "hla2010/time_management.py" in row["evidence"]
    assert "tests/verification/test_compliance_slice_v011.py::test_ddm_region_filtering_applies_before_timestamp_order_delivery" in row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_future_exclusion_scenario" in row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_output_delivery_scenario" in row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_consumer_order_scenario" in row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_scenario" in row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_receive_order_poison_scenario" in row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_future_exclusion" in row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_output_delivery" in row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_consumer_order" in row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline" in row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_receive_order_poison" in row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_future_exclusion_oracle_rejects_mismatched_lits_boundary" in row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_output_delivery_oracle_rejects_output_before_window_close" in row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_consumer_order_oracle_rejects_reversed_delivery_order" in row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_pipeline_oracle_rejects_cross_window_payload_contamination" in row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_receive_order_poison_oracle_rejects_closed_window_mutation" in row["evidence"]


def test_verification_asset_bundle_includes_time_window_save_restore_ladder() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "verification_assets.json").read_text(encoding="utf-8"))
    rows = {row["asset_id"]: row for row in payload["assets"]}

    local_state_row = rows["REQ-SAVE-RESTORE-FEDERATE-LOCAL-STATE-001"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_state_scenario" in local_state_row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_output_scenario" in local_state_row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_restore_scenario" in local_state_row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_state" in local_state_row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_output" in local_state_row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline_restore" in local_state_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_restore_window_state_oracle_rejects_dirty_post_close_callback_leak" in local_state_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore" in local_state_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay" in local_state_row["evidence"]

    transient_row = rows["REQ-SAVE-RESTORE-TRANSIENT-STATE-001"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_restore_output_scenario" in transient_row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_target_radar_time.py::run_target_radar_time_window_pipeline_restore_scenario" in transient_row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_restore_output" in transient_row["evidence"]
    assert "tests/scenarios/test_python_route_parity.py::test_python_route_parity_target_radar_time_window_pipeline_restore" in transient_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore" in transient_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay" in transient_row["evidence"]


def test_verification_asset_bundle_includes_save_restore_routing_state_rollback() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "analysis" / "compliance" / "verification_assets.json").read_text(encoding="utf-8"))
    rows = {row["asset_id"]: row for row in payload["assets"]}

    routing_row = rows["REQ-SAVE-RESTORE-ROUTING-STATE-001"]
    assert "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_plain_object_subscriber_routing_scenario" in routing_row["evidence"]
    assert "packages/hla-verification/src/hla.verification/scenario_save_restore.py::run_restore_plain_interaction_subscriber_routing_scenario" in routing_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_restore_recovers_plain_object_subscriber_routing" in routing_row["evidence"]
    assert "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_restore_recovers_plain_interaction_subscriber_routing" in routing_row["evidence"]
    assert "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_object_subscriber_routing_over_fedpro_schema" in routing_row["evidence"]
    assert "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_restore_recovers_plain_interaction_subscriber_routing_over_fedpro_schema" in routing_row["evidence"]
