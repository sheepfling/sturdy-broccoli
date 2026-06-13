from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY_PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs/README.md",
    ROOT / "docs/onboarding.md",
    ROOT / "docs/first_run.md",
    ROOT / "docs/spec_reading_map.md",
    ROOT / "docs/fom_reading_map.md",
    ROOT / "docs/python_rti_reading_map.md",
    ROOT / "docs/python_rti_edit_one_service.md",
    ROOT / "docs/requirements_trace_one_method.md",
    ROOT / "docs/requirements_authoring_map.md",
    ROOT / "docs/python_environment.md",
    ROOT / "docs/two_federate_quickstart.md",
    ROOT / "packages/README.md",
    ROOT / "tests/README.md",
)
BANNED_PRIMARY_REFS = (
    "docs/evidence/",
    "docs/reference/archive_index.md",
)
EXPECTED_HEADINGS = {
    ROOT / "README.md": ("## Start Here", "## Read Next"),
    ROOT / "docs/README.md": ("## Start Here", "## Historical / Provenance", "## Read Next"),
    ROOT / "docs/onboarding.md": ("## What This Path Assumes", "## What This Path Avoids", "## Read Next"),
    ROOT / "docs/first_run.md": ("## Read Next",),
    ROOT / "docs/spec_reading_map.md": ("## Why These Files", "## What To Ignore First", "## Read Next"),
    ROOT / "docs/fom_reading_map.md": ("## Why These Files", "## Edit Here For", "## Read Next"),
    ROOT / "docs/python_rti_reading_map.md": ("## Why These Files", "## Edit Loop", "## Read Next"),
    ROOT / "docs/python_rti_edit_one_service.md": ("## Recommended First Example", "## Edit Loop", "## Read Next"),
    ROOT / "docs/requirements_trace_one_method.md": ("## Recommended First Example", "## Trace Loop", "## Read Next"),
    ROOT / "docs/requirements_authoring_map.md": ("## Why These Files", "## Authoring Loop", "## Read Next"),
    ROOT / "docs/requirements_edit_one_row.md": ("## Active Vs Generated Vs Reference", "## One-Row Edit Loop", "## Read Next"),
    ROOT / "docs/python_environment.md": ("## Read Next",),
    ROOT / "docs/two_federate_quickstart.md": ("## Read Next",),
    ROOT / "packages/README.md": ("## Start Here", "## Read Next"),
    ROOT / "tests/README.md": ("## Start Here", "## Read Next"),
}
EXPECTED_PATHS = {
    ROOT / "README.md": (
        ROOT / "tools/bootstrap",
        ROOT / "examples/target_radar_simulation.py",
        ROOT / "examples/backend_recording.py",
        ROOT / "tools/test",
    ),
    ROOT / "docs/onboarding.md": (
        ROOT / "docs/first_run.md",
        ROOT / "docs/python_rti_edit_one_service.md",
        ROOT / "docs/create_federate_and_fom.md",
        ROOT / "docs/requirements_trace_one_method.md",
        ROOT / "packages/README.md",
        ROOT / "docs/java_backends_quickstart.md",
        ROOT / "docs/verification/run_sequence.md",
        ROOT / "docs/spec_reading_map.md",
        ROOT / "docs/python_rti_reading_map.md",
        ROOT / "docs/requirements_edit_one_row.md",
        ROOT / "docs/requirements_traceability.md",
    ),
    ROOT / "docs/spec_reading_map.md": (
        ROOT / "packages/hla2010-spec/src/hla2010/spec/__init__.py",
        ROOT / "packages/hla2010-spec/src/hla2010/runtime_api.py",
        ROOT / "packages/hla2010-spec/src/hla2010/ambassadors.py",
        ROOT / "specs/hla2010_api.json",
    ),
    ROOT / "docs/fom_reading_map.md": (
        ROOT / "packages/hla2010-spec/src/hla2010/fom.py",
        ROOT / "packages/hla2010-spec/src/hla2010/_fom_parsing.py",
        ROOT / "packages/hla2010-spec/src/hla2010/_fom_merge.py",
        ROOT / "packages/hla2010-spec/src/hla2010/_fom_datatypes.py",
        ROOT / "packages/hla2010-spec/src/hla2010/_fom_serialization.py",
        ROOT / "packages/hla2010-spec/src/hla2010/_fom_models.py",
        ROOT / "tests/factories/test_fom_omt_parsing.py",
    ),
    ROOT / "docs/python_rti_reading_map.md": (
        ROOT / "docs/python_rti_backend.md",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/backend.py",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py",
        ROOT / "analysis/traceability/python_rti_service_map.md",
    ),
    ROOT / "docs/python_rti_edit_one_service.md": (
        ROOT / "tools/human-editability",
        ROOT / "docs/python_rti_backend.md",
        ROOT / "packages/hla2010-spec/src/hla2010/runtime_api.py",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py",
        ROOT / "tests/backends/test_python_rti_service_registry.py",
    ),
    ROOT / "docs/requirements_trace_one_method.md": (
        ROOT / "tools/human-editability",
        ROOT / "docs/requirements_traceability.md",
        ROOT / "requirements/traceability_matrix.csv",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/time_public_services.py",
        ROOT / "tests/scenarios/test_support_services_backend_matrix.py",
        ROOT / "tests/time/test_mom_mim_time_v10.py",
    ),
    ROOT / "docs/requirements_authoring_map.md": (
        ROOT / "docs/requirements_edit_one_row.md",
        ROOT / "requirements/README.md",
        ROOT / "requirements/surface_manifest.json",
        ROOT / "docs/requirements_traceability.md",
        ROOT / "requirements/traceability_matrix.csv",
        ROOT / "analysis/compliance/requirements_ledger.csv",
        ROOT / "scripts/validate_traceability_paths.py",
    ),
    ROOT / "docs/requirements_edit_one_row.md": (
        ROOT / "requirements/README.md",
        ROOT / "requirements/surface_manifest.json",
        ROOT / "requirements/traceability_matrix.csv",
        ROOT / "analysis/compliance/requirements_ledger.csv",
        ROOT / "analysis/traceability/service_trace_index.md",
        ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/support_lookup.py",
        ROOT / "tests/scenarios/test_support_services_backend_matrix.py",
    ),
    ROOT / "docs/first_run.md": (
        ROOT / "tools/bootstrap",
        ROOT / "tools/examples",
        ROOT / "tools/rti-factories",
        ROOT / "examples/backend_recording.py",
        ROOT / "examples/rti_factory_selection.py",
        ROOT / "examples/target_radar_simulation.py",
    ),
    ROOT / "docs/python_environment.md": (
        ROOT / "tools/bootstrap",
        ROOT / "examples/target_radar_simulation.py",
        ROOT / "tools/two-federate",
        ROOT / "tools/test",
        ROOT / "tools/python",
        ROOT / "tools/certi-easy",
        ROOT / "tools/pitch",
    ),
    ROOT / "docs/two_federate_quickstart.md": (
        ROOT / "tools/rti-factories",
        ROOT / "tools/two-federate",
        ROOT / "scripts/run_two_federate_suite.py",
        ROOT / "src/hla2010_repo_internal/verification/two_federate_suite_runner.py",
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_markdown_links_are_valid() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/ci/check_doc_links.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout or result.stderr


def test_markdown_links_checker_bootstraps_from_outside_repo(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "check_doc_links.py")],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout or result.stderr


def test_key_public_docs_keep_required_navigation_headings() -> None:
    for path, headings in EXPECTED_HEADINGS.items():
        text = _read(path)
        for heading in headings:
            assert heading in text, f"{path.relative_to(ROOT)} missing {heading}"


def test_key_public_docs_do_not_link_to_historical_material_in_primary_sections() -> None:
    for path in KEY_PUBLIC_DOCS:
        text = _read(path)
        historical_index = text.find("## Historical / Provenance")
        primary_text = text if historical_index == -1 else text[:historical_index]
        for banned in BANNED_PRIMARY_REFS:
            assert banned not in primary_text, f"{path.relative_to(ROOT)} promotes {banned} before the historical section"


def test_key_newcomer_docs_reference_existing_paths() -> None:
    for path, expected_paths in EXPECTED_PATHS.items():
        text = _read(path)
        for expected_path in expected_paths:
            repo_rel = expected_path.relative_to(ROOT).as_posix()
            doc_rel = expected_path.relative_to(ROOT).as_posix()
            if path.parent != ROOT:
                doc_rel = expected_path.relative_to(ROOT).as_posix()
                doc_rel = Path(
                    os.path.relpath(expected_path, start=path.parent)
                ).as_posix()
            assert repo_rel in text or doc_rel in text, (
                f"{path.relative_to(ROOT)} no longer references {repo_rel} "
                f"or {doc_rel}"
            )
            assert expected_path.exists(), repo_rel


def test_onboarding_doc_is_the_canonical_opinionated_map() -> None:
    text = _read(ROOT / "docs" / "onboarding.md")
    assert "1. [First Run](first_run.md)" in text
    assert "2. [Edit One Python RTI Service](python_rti_edit_one_service.md)" in text
    assert "3. [Create A Federate And FOM](create_federate_and_fom.md)" in text
    assert "4. [Trace One Method](requirements_trace_one_method.md)" in text
    assert "5. [Package Ownership Map](../packages/README.md)" in text
    assert "6. [Java Backends Later](java_backends_quickstart.md)" in text
    assert "7. [Full Verification](verification/run_sequence.md)" in text
    assert "8. [Spec Reading Map](spec_reading_map.md)" in text
    assert "9. [Python RTI Reading Map](python_rti_reading_map.md)" in text
    assert "10. [Requirements Details Later](requirements_traceability.md)" in text
    assert "[requirements_edit_one_row.md](requirements_edit_one_row.md)" in text
    assert "authoring map is secondary reading" in text
    assert "requirements_authoring_map.md" not in text
    assert "docs/evidence/" not in text
    assert "reference/archive_index.md" not in text


def test_reading_maps_define_small_human_front_doors() -> None:
    spec_text = _read(ROOT / "docs" / "spec_reading_map.md")
    assert "packages/hla2010-spec/src/hla2010/raw_api.py" in spec_text
    assert "packages/hla2010-spec/src/hla2010/_spec_impl.py" in spec_text
    assert "packages/hla2010-spec/src/hla2010/fom.py" in spec_text

    fom_text = _read(ROOT / "docs" / "fom_reading_map.md")
    assert "_fom_parsing.py" in fom_text
    assert "_fom_merge.py" in fom_text
    assert "_fom_datatypes.py" in fom_text
    assert "_fom_serialization.py" in fom_text
    assert "_fom_models.py" in fom_text
    assert "human-editability front-doors fom" in fom_text

    python_rti_text = _read(ROOT / "docs" / "python_rti_reading_map.md")
    assert "service_registry.py" in python_rti_text
    assert "human-editability trace <MethodName>" in python_rti_text
    assert "rti_factory_reading_map.md" in python_rti_text
    assert "./tools/rti-factories show in-memory --probe" in python_rti_text
    assert "./tools/human-editability front-doors python-rti-service" in python_rti_text

    python_rti_service_text = _read(ROOT / "docs" / "python_rti_edit_one_service.md")
    assert "./tools/human-editability trace getHLAversion" in python_rti_service_text
    assert "timeAdvanceRequest" in python_rti_service_text
    assert "support_lookup.py" in python_rti_service_text
    assert "service_registry.py" in python_rti_service_text

    requirements_trace_text = _read(ROOT / "docs" / "requirements_trace_one_method.md")
    assert "./tools/human-editability trace getHLAversion" in requirements_trace_text
    assert "./tools/human-editability trace timeAdvanceRequest" in requirements_trace_text
    assert "support_lookup.py" in requirements_trace_text
    assert "test_support_services_backend_matrix.py" in requirements_trace_text

    requirements_edit_text = _read(ROOT / "docs" / "requirements_edit_one_row.md")
    assert "requirements/traceability_matrix.csv" in requirements_edit_text
    assert "requirements/surface_manifest.json" in requirements_edit_text
    assert "./tools/human-editability requirements-surfaces" in requirements_edit_text
    assert "analysis/compliance/requirements_ledger.csv" in requirements_edit_text
    assert "Active Vs Generated Vs Reference" in requirements_edit_text
    assert "./tools/human-editability requirement REQ-RTI-TM-8_8-timeAdvanceRequest" in requirements_edit_text
    assert "./tools/human-editability check" in requirements_edit_text
    assert "./tools/human-editability generate-trace-index" in requirements_edit_text

    rti_factory_text = _read(ROOT / "docs" / "rti_factory_reading_map.md")
    assert "./tools/rti-factories list" in rti_factory_text
    assert "./tools/rti-factories instantiate in-memory --probe" in rti_factory_text
    assert "examples/rti_factory_selection.py" in rti_factory_text
    assert "./tools/examples rti-factory-selection --name in-memory --probe" in rti_factory_text
    assert "iter_rti_factories()" in rti_factory_text
    assert "get_rti_factory(name)" in rti_factory_text
    assert "human-editability front-doors rti-factories" in rti_factory_text
    assert "python_rti_reading_map.md" in rti_factory_text

    python_rti_backend_text = _read(ROOT / "docs" / "python_rti_backend.md")
    assert "rti_factory_reading_map.md" in python_rti_backend_text
    assert "python_rti_edit_one_service.md" in python_rti_backend_text
    assert "./tools/rti-factories list" in python_rti_backend_text
    assert "./tools/rti-factories show in-memory --probe" in python_rti_backend_text
    assert "./tools/rti-factories instantiate in-memory --probe" in python_rti_backend_text
    assert "./tools/examples target-radar --backend in-memory --steps 5" in python_rti_backend_text
    assert "./tools/examples rti-factory-selection --name in-memory --probe" in python_rti_backend_text
    assert "source .venv/bin/activate" in python_rti_backend_text

    requirements_text = _read(ROOT / "docs" / "requirements_authoring_map.md")
    assert "requirements_edit_one_row.md" in requirements_text
    assert "requirements/README.md" in requirements_text
    assert "active authored requirement input" in requirements_text
    assert "requirements_trace_one_method.md" in requirements_text
    assert "./tools/human-editability requirement <RequirementId>" in requirements_text
    assert "Do not start by editing generated files under `analysis/compliance/`" in requirements_text
    assert "./tools/human-editability check" in requirements_text

    create_fom_text = _read(ROOT / "docs" / "create_federate_and_fom.md")
    assert "./tools/examples minimal-fom-demo --backend in-memory" in create_fom_text
    assert "python examples/minimal_fom_demo.py --backend python" in create_fom_text


def test_requirements_docs_keep_distinct_roles() -> None:
    traceability_text = _read(ROOT / "docs" / "requirements_traceability.md")
    authoring_text = _read(ROOT / "docs" / "requirements_authoring_map.md")
    edit_text = _read(ROOT / "docs" / "requirements_edit_one_row.md")
    requirements_readme = _read(ROOT / "requirements" / "README.md")

    assert "Use this page for:\n\n- the broader traceability model" in traceability_text
    assert "Use this page for the ordered reading path." in authoring_text
    assert '"We missed one requirement row, or one mapping is wrong. What do I edit?"' in edit_text
    assert "Use this page for requirement-surface classification." in requirements_readme

    assert "generated service trace index" in traceability_text
    assert "Read these files in order:" in authoring_text
    assert "## One-Row Edit Loop" in edit_text
    assert "## Surface Types" in requirements_readme

    assert "Use this page for requirement-surface classification." not in traceability_text
    assert "Use this page for the ordered reading path." not in edit_text
    assert "Read these files in order:" not in requirements_readme


def test_python_rti_backend_doc_matches_registry_backed_dispatch_reality() -> None:
    text = _read(ROOT / "docs" / "python_rti_backend.md")
    assert "generated service registry" in text
    assert "PYTHON_RTI_SERVICE_REGISTRY" in text
    assert "`getattr(...)`" in text


def test_repo_does_not_keep_duplicate_markdown_copies() -> None:
    duplicates = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("**/* 2.md")
        if path.is_file()
    )
    assert duplicates == [], f"duplicate markdown copies remain: {duplicates}"


def test_python_api_spec_matches_split_package_reality() -> None:
    path = ROOT / "docs/python_api_spec.md"
    text = _read(path)
    assert "installable root: `hla2010-spec`" in text
    assert "spec source root: `packages/hla2010-spec/src/hla2010/`" in text
    assert "package-owned implementations: `packages/*/src/...`" in text
    assert "temporary compatibility routing" in text
    assert "temporary backend-discovery and ambassador-factory compatibility facade" in text
    assert "../packages/hla2010-spec/src/hla2010/spec/__init__.py" in text
    assert "../packages/hla2010-spec/README.md" in text
    assert "../hla2010/spec/" not in text
    assert "hla2010.testing" not in text


def test_repo_overview_docs_describe_root_namespace_as_core_plus_temporary_facades() -> None:
    readme = _read(ROOT / "README.md")
    packages_readme = _read(ROOT / "packages" / "README.md")

    assert "`packages/hla2010-spec/src/hla2010/` is the package-owned root Python package for the abstract/core API plus the documented temporary compatibility facade `hla2010.rti`" in readme
    assert "`hla2010/` is a narrow top-level shim area for plugin-facing glue" not in readme
    assert "`packages/hla2010-spec/src/hla2010/` tree is the package-owned spec source root used for stable imports, abstract\ncore API ownership, and only documented temporary compatibility routing." in packages_readme
