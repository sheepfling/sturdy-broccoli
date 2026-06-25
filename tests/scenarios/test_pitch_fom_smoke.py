from __future__ import annotations

from pathlib import Path

from hla.verification.repo_internal.verification import pitch_fom_smoke as module


def test_build_default_pitch_fom_smoke_specs_covers_rpr_and_repo_baselines() -> None:
    specs = {spec.id: spec for spec in module.build_default_pitch_fom_smoke_specs()}

    assert "repo-2010-demo" in specs
    assert "repo-cross-target-radar" in specs
    assert "link16-rpr2-integrated" in specs
    assert "rpr3-merged-informative-1516-2010" in specs
    assert "space-fom-core" in specs
    assert specs["rpr3-merged-informative-1516-2010"].scenario_family == "siso-rpr-3.0"
    assert "Datatype-heavy RPR 3.0" in specs["rpr3-merged-informative-1516-2010"].notes


def test_probe_pitch_fom_support_reports_lookup_green_and_failures(monkeypatch) -> None:
    class FakeRuntime:
        def close(self) -> None:
            return None

    class FakeRTI:
        def __init__(self, *, fail_interaction: str | None = None) -> None:
            self.fail_interaction = fail_interaction

        def connect(self, ambassador, callback_model) -> None:
            return None

        def create_federation_execution(self, federation_name, fom_modules, logical_time_implementation_name) -> None:
            return None

        def join_federation_execution(self, federate_name, federate_type, federation_name):
            return "joined"

        def get_object_class_handle(self, name: str) -> str:
            return f"obj:{name}"

        def get_interaction_class_handle(self, name: str) -> str:
            if self.fail_interaction == name:
                raise RuntimeError("simulated lookup failure")
            return f"int:{name}"

        def resign_federation_execution(self, action) -> None:
            return None

        def destroy_federation_execution(self, federation_name: str) -> None:
            return None

        def disconnect(self) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr(module, "launch_pitch_runtime", lambda: FakeRuntime())

    factory_calls = {"count": 0}

    def fake_factory(kind: str) -> FakeRTI:
        factory_calls["count"] += 1
        if factory_calls["count"] == 2:
            return FakeRTI(fail_interaction="HLAinteractionRoot.Broken")
        return FakeRTI()

    monkeypatch.setattr(module, "create_rti_ambassador", fake_factory)
    monkeypatch.setattr(module, "create_rti_ambassador_2025", lambda *, backend: FakeRTI())
    specs = (
        module.PitchFomSmokeSpec(
            id="demo-ok",
            scenario_family="demo",
            load_mode="standalone",
            notes="demo",
            fom_modules=("Demo.xml",),
            object_class_name="HLAobjectRoot.DemoObject",
            interaction_class_name="HLAinteractionRoot.Ping",
        ),
        module.PitchFomSmokeSpec(
            id="broken-rpr",
            scenario_family="siso-rpr-3.0",
            load_mode="ordered-family",
            notes="broken",
            fom_modules=("RPR.xml",),
            object_class_name="HLAobjectRoot.BridgeObject",
            interaction_class_name="HLAinteractionRoot.Broken",
        ),
    )

    summary = module.probe_pitch_fom_support(runtime_kinds=("pitch-jpype",), specs=specs)

    assert summary["suite_name"] == "pitch-fom-smoke"
    assert summary["lookup_green_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["by_runtime"]["pitch-jpype"]["lookup_green"] == 1
    assert summary["by_runtime"]["pitch-jpype"]["failed"] == 1
    assert summary["rows"][1]["error_type"] == "RuntimeError"
    assert summary["rows"][0]["evidence_mode"] == "vendor-runtime"
    assert summary["rows"][0]["counts_as_vendor_runtime"] is True


def test_probe_pitch_fom_support_marks_pitch_202x_routes_as_adapter_backed(monkeypatch) -> None:
    class FakeRTI:
        def connect(self, ambassador, callback_model) -> None:
            return None

        def create_federation_execution(self, federation_name, fom_modules, logical_time_implementation_name) -> None:
            return None

        def join_federation_execution(self, federate_name, federate_type, federation_name):
            return "joined"

        def get_object_class_handle(self, name: str) -> str:
            return f"obj:{name}"

        def get_interaction_class_handle(self, name: str) -> str:
            return f"int:{name}"

        def resign_federation_execution(self, action) -> None:
            return None

        def destroy_federation_execution(self, federation_name: str) -> None:
            return None

        def disconnect(self) -> None:
            return None

    monkeypatch.setattr(module, "launch_pitch_runtime", lambda: (_ for _ in ()).throw(AssertionError("should not launch runtime")))
    monkeypatch.setattr(module, "create_rti_ambassador_2025", lambda *, backend: FakeRTI())

    specs = (
        module.PitchFomSmokeSpec(
            id="demo-ok",
            scenario_family="demo",
            load_mode="standalone",
            notes="demo",
            fom_modules=("Demo.xml",),
            object_class_name="HLAobjectRoot.DemoObject",
            interaction_class_name="HLAinteractionRoot.Ping",
        ),
    )

    summary = module.probe_pitch_fom_support(runtime_kinds=("pitch-202x-jpype",), specs=specs)

    assert summary["lookup_green_count"] == 1
    assert summary["runtime_profiles"] == [
        {
            "kind": "pitch-202x-jpype",
            "spec_name": "rti1516_2025",
            "evidence_mode": "adapter-backed",
            "counts_as_vendor_runtime": False,
        }
    ]
    assert summary["rows"][0]["runtime_kind"] == "pitch-202x-jpype"
    assert summary["rows"][0]["evidence_mode"] == "adapter-backed"
    assert summary["rows"][0]["counts_as_vendor_runtime"] is False
    assert summary["rows"][0]["spec_name"] == "rti1516_2025"


def test_write_pitch_fom_smoke_emits_summary_and_markdown(tmp_path: Path) -> None:
    summary = {
        "suite_name": "pitch-fom-smoke",
        "packet_count": 1,
        "runtime_count": 1,
        "row_count": 1,
        "runtime_profiles": [
            {
                "kind": "pitch-jpype",
                "spec_name": "rti1516e",
                "evidence_mode": "vendor-runtime",
                "counts_as_vendor_runtime": True,
            }
        ],
        "lookup_green_count": 1,
        "failed_count": 0,
        "by_runtime": {"pitch-jpype": {"lookup_green": 1, "failed": 0}},
        "rows": [
            {
                "runtime_kind": "pitch-jpype",
                "spec_name": "rti1516e",
                "evidence_mode": "vendor-runtime",
                "counts_as_vendor_runtime": True,
                "packet_id": "repo-2010-demo",
                "scenario_family": "demo",
                "load_mode": "standalone",
                "status": "lookup-green",
                "notes": "demo",
            }
        ],
    }

    paths = module.write_pitch_fom_smoke(tmp_path, summary)

    assert paths.summary_json.exists()
    assert paths.report_markdown.exists()
    text = paths.report_markdown.read_text(encoding="utf-8")
    assert "Pitch FOM Smoke" in text
    assert "Runtime Profiles" in text
    assert "adapter-backed" in text
    assert "lookup-green" in text
    assert "repo-2010-demo" in text
