from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

from hla.verification.repo_internal.verification import siso_runtime_showcase as showcase_module
from hla.verification.repo_internal.verification.siso_runtime_showcase import (
    build_siso_runtime_showcase_manifest,
    run_siso_runtime_showcase,
    run_siso_runtime_showcase_scenario,
    write_siso_runtime_showcase_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


class _FakeHandle:
    def __init__(self, owner: str, kind: str, name: str) -> None:
        self.owner = owner
        self.kind = kind
        self.name = name


class _FakeRTI:
    def __init__(self, name: str) -> None:
        self.name = name

    def getObjectClassHandle(self, class_name: str) -> _FakeHandle:
        return _FakeHandle(self.name, "object-class", class_name)

    def getAttributeHandle(self, class_handle: _FakeHandle, attribute_name: str) -> _FakeHandle:
        assert class_handle.owner == self.name
        return _FakeHandle(self.name, "attribute", attribute_name)

    def getInteractionClassHandle(self, class_name: str) -> _FakeHandle:
        return _FakeHandle(self.name, "interaction-class", class_name)

    def getParameterHandle(self, class_handle: _FakeHandle, parameter_name: str) -> _FakeHandle:
        assert class_handle.owner == self.name
        return _FakeHandle(self.name, "parameter", parameter_name)


def test_siso_runtime_showcase_completes_all_scenarios() -> None:
    summary = run_siso_runtime_showcase()

    assert summary["suite_name"] == "siso-fom-runtime-showcase"
    assert summary["status"] == "lifecycle-green"
    assert summary["scenario_count"] == 18
    assert summary["backend_matrix_count"] == 18
    assert summary["manifest_scenario_count"] == 18
    assert all(row["execution_complete"] for row in summary["scenarios"])

    by_scenario = {row["scenario"]: row for row in summary["scenarios"]}
    backend_by_scenario = {row["scenario"]: row for row in summary["backend_matrix"]}
    assert by_scenario["link16-rpr2-integrated-2010-micro-2"]["runtime_edition"] == "2010"
    assert by_scenario["link16-rpr2-integrated-2010-micro-2"]["interactions"] >= 2
    assert by_scenario["link16-rpr2-integrated-2025-constellation-10"]["federate_count"] == 10
    assert by_scenario["link16-rpr2-integrated-2025-constellation-10"]["interactions"] >= 6
    assert by_scenario["rpr-runtime-2010-micro-2"]["source_packet"] == "rpr3-merged-informative-1516-2010"
    assert by_scenario["rpr-runtime-2025-squad-5"]["source_packet"] == "rpr3-annex-a-normative"
    assert by_scenario["rpr-runtime-2025-squad-5"]["interactions"] >= 4
    assert by_scenario["space-fom-core-2010-micro-2"]["reflections"] >= 3
    assert by_scenario["space-fom-core-2025-constellation-10"]["federate_count"] == 10
    assert by_scenario["space-fom-core-2025-constellation-10"]["discoveries"] >= 4
    assert backend_by_scenario["link16-rpr2-integrated-2010-micro-2"]["python_backend"] == "python1516e"
    assert backend_by_scenario["link16-rpr2-integrated-2010-micro-2"]["pitch_2010_profiles"] == "pitch-jpype,pitch-py4j"
    assert backend_by_scenario["link16-rpr2-integrated-2010-micro-2"]["vendor_status"] == "eligible"
    assert backend_by_scenario["rpr-runtime-2025-micro-2"]["pitch_202x_profiles"] == "pitch-202x-jpype,pitch-202x-py4j"
    assert backend_by_scenario["rpr-runtime-2025-micro-2"]["vendor_status"] == "bounded-eligible"
    assert backend_by_scenario["space-fom-core-2025-constellation-10"]["pitch_202x_profiles"] == ""
    assert backend_by_scenario["space-fom-core-2025-constellation-10"]["vendor_status"] == "python-only-topology"


def test_siso_runtime_showcase_manifest_is_explicit() -> None:
    manifest = build_siso_runtime_showcase_manifest()

    assert manifest["schema_version"] == "siso-runtime-showcase-manifest-v0.1"
    assert manifest["scenario_count"] == 18
    by_scenario = {row["scenario"]: row for row in manifest["scenarios"]}
    assert by_scenario["link16-rpr2-integrated-2010-micro-2"]["participant_roles"] == [
        "originator-1",
        "observer-1",
    ]
    assert by_scenario["link16-rpr2-integrated-2010-micro-2"]["participant_profiles"][0]["federate"] == "Link16Federate1"
    assert by_scenario["rpr-runtime-2025-squad-5"]["participant_roles"] == [
        "bridge-owner",
        "shooter-1",
        "shooter-2",
        "observer-1",
        "observer-2",
    ]
    assert by_scenario["space-fom-core-2025-constellation-10"]["python_backend"] == "python1516_2025"
    assert by_scenario["space-fom-core-2025-constellation-10"]["vendor_status"] == "python-only-topology"


def test_siso_runtime_showcase_can_run_one_named_scenario() -> None:
    result = run_siso_runtime_showcase_scenario("space-fom-core-2010-micro-2")

    assert result["scenario"] == "space-fom-core-2010-micro-2"
    assert result["execution_complete"] is True
    assert result["status"] == "lifecycle-green"
    assert result["listener_event_count"] >= 1
    assert result["participant_profiles"][-1]["role"] == "observer"


def test_link16_integrated_packet_paths_include_rpr_parent_modules() -> None:
    paths = showcase_module._packet_paths("link16-rpr2-integrated")  # noqa: SLF001

    basenames = {Path(path).name for path in paths}
    assert "Link_16_v2.0.xml" in basenames
    assert "RPR-Communication_v2.0.xml" in basenames
    assert "RPR-Enumerations_v2.0.xml" in basenames
    assert "RPR-Base_v2.0.xml" in basenames
    assert "Link_11_11B_v1.0.xml" not in basenames


def test_siso_runtime_showcase_resolves_handles_per_rti() -> None:
    rtis = [_FakeRTI("sender"), _FakeRTI("observer")]

    object_classes, attrs_by_rti = showcase_module._resolve_attribute_handles(  # noqa: SLF001
        rtis,
        "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
        ("RadioIndex", "Frequency", "WorldLocation"),
    )
    interaction_classes, params_by_rti = showcase_module._resolve_parameter_handles(  # noqa: SLF001
        rtis,
        "HLAinteractionRoot.RadioSignal.RawBinaryRadioSignal.TDLBinaryRadioSignal.Link16RadioSignal.JTIDSMessageRadioSignal",
        ("NPGNumber", "NetNumber"),
    )

    assert object_classes[rtis[0]].owner == "sender"
    assert object_classes[rtis[1]].owner == "observer"
    assert attrs_by_rti[rtis[0]]["RadioIndex"].owner == "sender"
    assert attrs_by_rti[rtis[1]]["RadioIndex"].owner == "observer"
    assert interaction_classes[rtis[0]].owner == "sender"
    assert interaction_classes[rtis[1]].owner == "observer"
    assert params_by_rti[rtis[0]]["NPGNumber"].owner == "sender"
    assert params_by_rti[rtis[1]]["NPGNumber"].owner == "observer"


def test_siso_runtime_showcase_artifacts_are_generated(tmp_path: Path) -> None:
    paths = write_siso_runtime_showcase_artifacts(tmp_path)

    summary = json.loads(paths.summary_json.read_text(encoding="utf-8"))
    assert summary["status"] == "lifecycle-green"
    assert len(summary["scenarios"]) == 18
    assert len(summary["backend_matrix"]) == 18
    assert summary["scenario_manifest"]["scenario_count"] == 18

    with paths.scenario_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 18
    assert all(row["status"] == "lifecycle-green" for row in rows)

    with paths.backend_matrix_csv.open(encoding="utf-8") as handle:
        backend_rows = list(csv.DictReader(handle))
    assert len(backend_rows) == 18
    assert any(row["pitch_2010_profiles"] == "pitch-jpype,pitch-py4j" for row in backend_rows)
    assert any(row["pitch_202x_profiles"] == "pitch-202x-jpype,pitch-202x-py4j" for row in backend_rows)
    assert any(row["vendor_status"] == "python-only-topology" for row in backend_rows)

    manifest = json.loads(paths.scenario_manifest_json.read_text(encoding="utf-8"))
    assert manifest["scenario_count"] == 18
    assert "participant_roles" in manifest["scenarios"][0]
    assert paths.listener_index_json.exists()
    assert paths.listener_index_html.exists()
    listener_index = json.loads(paths.listener_index_json.read_text(encoding="utf-8"))
    assert listener_index["scenario_count"] == 18
    assert all(row["listener_event_count"] >= 1 for row in listener_index["listeners"])

    listener_root = tmp_path / "listener"
    listener_summary = listener_root / "link16-rpr2-integrated-2010-micro-2" / "listener_summary.json"
    listener_trace = listener_root / "link16-rpr2-integrated-2010-micro-2" / "listener_trace.ndjson"
    listener_report = listener_root / "link16-rpr2-integrated-2010-micro-2" / "listener_report.html"
    assert listener_summary.exists()
    assert listener_trace.exists()
    assert listener_report.exists()
    listener_payload = json.loads(listener_summary.read_text(encoding="utf-8"))
    assert listener_payload["participants"][0]["federate"] == "Link16Federate1"
    assert listener_payload["statistics"]["callbacks"]["receiveInteraction"] >= 2

    report = paths.report_markdown.read_text(encoding="utf-8")
    assert "SISO FOM Runtime Showcase" in report
    assert "Backend Eligibility Matrix" in report
    assert "bounded vendor-credence only" in report
    assert "scenario manifest json" in report
    assert "listener index html" in report
    assert "link16-rpr2-integrated-2010-micro-2" in report
    assert "rpr-runtime-2025-squad-5" in report
    assert "space-fom-core-2025-constellation-10" in report


def test_siso_runtime_showcase_top_level_wrapper_bootstraps_source_checkout(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
    output_dir = tmp_path / "siso-runtime-showcase"
    result = subprocess.run(
        [
            str(ROOT / "tools" / "fom-siso-runtime-showcase"),
            "--output-dir",
            str(output_dir),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summary_path = output_dir / "siso_runtime_showcase_summary.json"
    assert summary_path.exists()
    assert (output_dir / "siso_runtime_showcase_backend_matrix.csv").exists()
    assert (output_dir / "siso_runtime_showcase_manifest.json").exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["suite_name"] == "siso-fom-runtime-showcase"
    assert summary["status"] == "lifecycle-green"
