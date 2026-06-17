from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _primary_text(path: Path) -> str:
    text = _read(path)
    historical_index = text.find("## Historical / Provenance")
    return text if historical_index == -1 else text[:historical_index]


def _documented_tool_inventory() -> set[str]:
    text = _read(ROOT / "tools" / "README.md")
    return {
        line.strip().split("./tools/", 1)[1][:-1]
        for line in text.splitlines()
        if line.strip().startswith("- `./tools/") and line.strip().endswith("`")
    }


def _scripts_readme_supported_tool_inventory() -> set[str]:
    lines = _read(ROOT / "scripts" / "README.md").splitlines()
    start = next(
        index
        for index, line in enumerate(lines)
        if "Supported human-facing entrypoints live under `tools/`" in line
    )
    inventory: set[str] = set()
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "Repo setup entrypoints that still live under `scripts/`:":
            break
        if stripped.startswith("- `./tools/"):
            inventory.add(stripped.split("./tools/", 1)[1].split("`", 1)[0])
    return inventory


def _actual_top_level_tool_wrappers() -> set[str]:
    return {
        path.name
        for path in (ROOT / "tools").iterdir()
        if path.is_file() and path.name != "README.md" and "." not in path.name
    }


def _actual_repo_root_files() -> set[str]:
    return {path.name for path in ROOT.iterdir() if path.is_file()}


def test_tools_readme_declares_canonical_operator_surface() -> None:
    text = _read(ROOT / "tools" / "README.md")
    assert "canonical home for human-facing operator entrypoints" in text
    assert "./tools/bootstrap" in text
    assert "./tools/python" in text
    assert "./tools/certi-easy" in text
    assert "./tools/pitch" in text
    assert "./tools/vendor-green" in text
    assert "./tools/vendor-state" in text
    assert "./tools/vendor-parity" in text
    assert "./tools/vendor-probe-review" in text
    assert "./tools/vendor-edge" in text
    assert "./tools/rti-options" in text
    assert "./tools/compliance" in text
    assert "./tools/fom-overview" in text
    assert "./tools/package-deps" in text
    assert "./tools/section8-gate" in text
    assert "./tools/target-radar" in text
    assert "./tools/lint" in text
    assert "./tools/two-federate" in text
    assert "./tools/test" in text
    assert "./tools/java" in text


def test_tools_readme_inventory_matches_actual_top_level_tool_wrappers() -> None:
    assert _documented_tool_inventory() == _actual_top_level_tool_wrappers()


def test_scripts_readme_supported_tool_inventory_matches_canonical_tools_surface() -> None:
    assert _scripts_readme_supported_tool_inventory() == _documented_tool_inventory()


def test_repo_root_does_not_duplicate_documented_tool_entrypoints() -> None:
    duplicated = _documented_tool_inventory() & _actual_repo_root_files()
    assert not duplicated, sorted(duplicated)


def test_scripts_readme_declares_implementation_boundary() -> None:
    text = _read(ROOT / "scripts" / "README.md")
    assert "implementation and CI plumbing, not the primary" in text
    assert "human-facing operator surface" in text
    assert "Compatibility aliases that remain for implementation and migration support" in text
    assert "./tools/lint" in text
    assert "./tools/compliance" in text
    assert "./tools/vendor-state classify" in text
    assert "./tools/vendor-state ci-state" in text
    assert "./tools/vendor-green [profile]" in text
    assert "./tools/vendor-probe-review" in text
    assert "./tools/vendor-edge" in text
    assert "./tools/section8-gate" in text
    assert "./tools/target-radar" in text
    assert "./scripts/certi_easy.sh" in text
    assert "./scripts/pitch_docker_easy.sh" in text
    assert "python3 scripts/ci/check_doc_links.py" not in text
    assert "python3 scripts/classify_vendor_runtime.py" not in text
    assert "python3 scripts/ci/check_vendor_runtime_ci_state.py" not in text
    assert "./scripts/ci/vendor_green.sh" not in text
    assert "./scripts/ci/vendor_runtime_smoke.sh" not in text
    assert "analysis/compliance/python_requirement_disposition.md" in text
    assert "analysis/compliance/certi_requirement_disposition.md" in text
    assert "analysis/compliance/certi-native_requirement_disposition.md" in text
    assert "analysis/compliance/pitch_requirement_disposition.md" in text
    assert "analysis/compliance/pitch-jpype_requirement_disposition.md" in text
    assert "analysis/compliance/pitch-py4j_requirement_disposition.md" in text
    assert "analysis/compliance/portico_requirement_disposition.md" in text
    assert "analysis/compliance/portico-jpype_requirement_disposition.md" in text
    assert "analysis/compliance/portico-py4j_requirement_disposition.md" in text


def test_public_readme_uses_tools_surface_for_compliance_operator_flow() -> None:
    text = _primary_text(ROOT / "README.md")
    assert "./tools/compliance generate" in text
    assert "./tools/compliance discover --show-backlog" in text
    assert "python3 scripts/generate_compliance_artifacts.py" not in text
    assert "python3 scripts/discover_backend_compliance.py --show-backlog" not in text


def test_backend_compliance_doc_uses_tools_surface() -> None:
    text = _primary_text(ROOT / "docs" / "backend_compliance_discovery.md")
    assert "./tools/compliance generate" in text
    assert "./tools/compliance discover --show-backlog" in text
    assert "analysis/compliance/certi_requirement_disposition.md" in text
    assert "analysis/compliance/certi-native_requirement_disposition.md" in text
    assert "analysis/compliance/portico_requirement_disposition.md" in text
    assert "analysis/compliance/pitch_requirement_disposition.md" in text
    assert "python3 scripts/generate_compliance_artifacts.py" not in text
    assert "python3 scripts/discover_backend_compliance.py" not in text


def test_two_federate_quickstart_uses_tools_surface() -> None:
    text = _primary_text(ROOT / "docs" / "two_federate_quickstart.md")
    assert "./tools/two-federate" in text
    assert "python3 scripts/run_two_federate_suite.py" not in text
    assert "../scripts/run_two_federate_suite.py" not in text


def test_vendor_parity_doc_uses_tools_surface() -> None:
    text = _primary_text(ROOT / "docs" / "vendor_parity_artifacts.md")
    assert "./tools/vendor-parity" in text
    assert "./tools/vendor-edge all" in text
    assert "python3 scripts/run_vendor_parity_artifacts.py" not in text
    assert "./scripts/ci/vendor_edge_matrix.sh all" not in text


def test_package_dependency_tree_doc_uses_tools_surface() -> None:
    text = _primary_text(ROOT / "docs" / "package_dependency_tree.md")
    assert "./tools/package-deps generate" in text
    assert "python3 scripts/generate_package_dependency_tree.py" not in text


def test_rti_options_doc_uses_tools_surface() -> None:
    text = _primary_text(ROOT / "docs" / "rti_options_and_test_matrix.md")
    assert "./tools/rti-options generate" in text
    assert "python3 scripts/update_rti_options_matrix.py" not in text


def test_public_docs_use_tools_surface_for_vendor_operator_flows() -> None:
    expected_paths = (
        ROOT / "README.md",
        ROOT / "docs/python_environment.md",
        ROOT / "docs/install_matrix.md",
        ROOT / "docs/top_to_bottom_green.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./tools/bootstrap" in text, path.relative_to(ROOT)
        assert "./tools/python" in text, path.relative_to(ROOT)
        assert "./tools/certi-easy" in text, path.relative_to(ROOT)
        assert "./tools/pitch" in text, path.relative_to(ROOT)
        assert "./tools/java" in text, path.relative_to(ROOT)
        assert "./tools/vendor-green" in text, path.relative_to(ROOT)


def test_vendor_runtime_docs_use_tools_vendor_green_surface() -> None:
    expected_paths = (
        ROOT / "README.md",
        ROOT / "docs/local_verification_commands.md",
        ROOT / "docs/top_to_bottom_green.md",
        ROOT / "docs/backend_route_inventory_commands.md",
        ROOT / "docs/vendor_runtime_runner_guide.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./tools/vendor-green" in text, path.relative_to(ROOT)


def test_vendor_runtime_runner_guide_uses_tools_probe_review_surface() -> None:
    text = _primary_text(ROOT / "docs" / "vendor_runtime_runner_guide.md")
    assert "./tools/vendor-probe-review <profile> 5" in text
    assert "./tools/vendor-probe-review promotion-review" in text
    assert "./scripts/ci/vendor_probe_review.sh <profile> 5" not in text
    assert "python3 scripts/ci/write_vendor_probe_promotion_review.py" not in text


def test_vendor_runtime_docs_use_tools_vendor_state_surface() -> None:
    expected_paths = (
        ROOT / "docs/preflight_artifacts.md",
        ROOT / "docs/vendor_runtime_runner_guide.md",
        ROOT / "docs/vendor_runner_provisioning.md",
        ROOT / "packages/hla-backend-certi/docs/certi_section8_runbook.md",
        ROOT / "packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./tools/vendor-state" in text, path.relative_to(ROOT)
        assert "python3 scripts/classify_vendor_runtime.py" not in text, path.relative_to(ROOT)
        assert "python3 scripts/ci/check_vendor_runtime_ci_state.py" not in text, path.relative_to(ROOT)


def test_public_pitch_docs_do_not_promote_script_operator_surfaces() -> None:
    expected_paths = (
        ROOT / "packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md",
        ROOT / "packages/hla-vendor-pitch/docs/pitch_crc_macos_vendor_bug.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./scripts/ci/vendor_green.sh" not in text, path.relative_to(ROOT)
        assert "./scripts/pitch_docker_easy.sh" not in text, path.relative_to(ROOT)
        assert "scripts/run_pitch_local.sh" not in text, path.relative_to(ROOT)


def test_pitch_lost_federate_docs_keep_tools_operator_surface_explicit() -> None:
    expected_paths = (
        ROOT / "packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md",
        ROOT / "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./tools/pitch lost-federate" in text, path.relative_to(ROOT)
        assert "./tools/pitch lost-federate-probe" in text, path.relative_to(ROOT)
        assert "./scripts/pitch_docker_easy.sh lost-federate" not in text, path.relative_to(ROOT)
        assert "./scripts/pitch_docker_easy.sh lost-federate-probe" not in text, path.relative_to(ROOT)
        assert "./scripts/ci/vendor_green.sh pitch" not in text, path.relative_to(ROOT)


def test_backend_capability_docs_use_tools_surface_for_operator_anchors() -> None:
    capability_text = _primary_text(ROOT / "docs" / "backend_capability_matrix.md")
    assert "./tools/vendor-parity" in capability_text
    assert "../scripts/run_vendor_parity_artifacts.py" not in capability_text

    options_text = _primary_text(ROOT / "docs" / "rti_options_and_test_matrix.md")
    assert "./tools/vendor-green" in options_text
    assert "../scripts/ci/vendor_runtime_smoke.sh" not in options_text


def test_backend_package_docs_use_tools_surface_for_specialized_vendor_flows() -> None:
    expected_paths = (
        ROOT / "packages/hla-vendor-pitch/docs/pitch_crc_macos_vendor_bug.md",
        ROOT / "packages/hla-backend-certi/docs/certi_runtime_limitations.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        if path.name == "pitch_crc_macos_vendor_bug.md":
            assert "./tools/pitch crc-macos-repro" in text, path.relative_to(ROOT)
            assert "./tools/pitch crc-docker-repro" in text, path.relative_to(ROOT)
            assert "python3 scripts/repro_pitch_crc_macos.py" not in text, path.relative_to(ROOT)
            assert "python3 scripts/repro_pitch_crc_docker.py" not in text, path.relative_to(ROOT)
        else:
            assert "./tools/certi-easy build patched" in text, path.relative_to(ROOT)
            assert "./tools/certi-easy build upstream" in text, path.relative_to(ROOT)
            assert "./scripts/rebuild_certi.sh" not in text, path.relative_to(ROOT)
            assert "./scripts/rebuild_certi_upstream.sh" not in text, path.relative_to(ROOT)


def test_certi_section8_runbook_uses_tools_gate_surface() -> None:
    text = _primary_text(ROOT / "packages/hla-backend-certi/docs/certi_section8_runbook.md")
    assert "./tools/section8-gate" in text
    assert "./scripts/ci/section8_backend_matrix_gate.sh" not in text


def test_public_docs_use_tools_test_for_local_pytest_flow() -> None:
    expected_paths = (
        ROOT / "README.md",
        ROOT / "docs/python_environment.md",
        ROOT / "tests/README.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./tools/test" in text, path.relative_to(ROOT)


def test_public_docs_use_tools_lint_for_local_lint_flow() -> None:
    text = _primary_text(ROOT / "docs" / "local_verification_commands.md")
    assert "./tools/lint" in text
    assert "./scripts/ci/lint.sh" not in text


def test_public_setup_docs_keep_root_install_policy_explicit() -> None:
    package_layout = _primary_text(ROOT / "docs" / "package_layout.md")
    first_run = _primary_text(ROOT / "docs" / "first_run.md")
    python_environment = _primary_text(ROOT / "docs" / "python_environment.md")
    scripts_readme = _primary_text(ROOT / "scripts" / "README.md")

    assert "repository root is tooling-only" in package_layout
    assert "Do not use `pip install -e .`" in package_layout
    assert "tooling-only and is not installed as a package" in first_run
    assert "without installing the repo root as a distribution" in python_environment
    assert "Do not use root `pip install -e .`" in scripts_readme


def test_public_docs_do_not_promote_legacy_script_vendor_aliases() -> None:
    expected_paths = (
        ROOT / "README.md",
        ROOT / "docs/README.md",
        ROOT / "docs/python_environment.md",
        ROOT / "docs/install_matrix.md",
        ROOT / "docs/agent_runbook.md",
        ROOT / "docs/top_to_bottom_green.md",
    )
    banned = ("./scripts/certi_easy.sh", "./scripts/pitch_docker_easy.sh")
    for path in expected_paths:
        text = _primary_text(path)
        for token in banned:
            assert token not in text, f"{path.relative_to(ROOT)} promotes {token}"


def test_public_docs_do_not_promote_legacy_vendor_green_surface() -> None:
    expected_paths = (
        ROOT / "README.md",
        ROOT / "docs/local_verification_commands.md",
        ROOT / "docs/top_to_bottom_green.md",
        ROOT / "docs/backend_route_inventory_commands.md",
        ROOT / "docs/vendor_runtime_runner_guide.md",
    )
    for path in expected_paths:
        text = _primary_text(path)
        assert "./scripts/ci/vendor_green.sh" not in text, (
            f"{path.relative_to(ROOT)} promotes legacy vendor-green surface"
        )


def test_public_docs_use_tools_bootstrap_and_repo_green_surface() -> None:
    bootstrap_paths = (
        ROOT / "packages/README.md",
        ROOT / "packages/hla-backend-inmemory/README.md",
        ROOT / "packages/hla-backend-certi/README.md",
        ROOT / "packages/hla-fom-target-radar/README.md",
        ROOT / "packages/hla-vendor-pitch/docs/pitch_decision_tree.md",
        ROOT / "docs/vendor_runtime_runner_guide.md",
    )
    for path in bootstrap_paths:
        text = _primary_text(path)
        assert "./tools/bootstrap" in text, path.relative_to(ROOT)
        assert "./scripts/bootstrap_profile.sh" not in text, path.relative_to(ROOT)

    repo_green_paths = (
        ROOT / "docs/backend_route_inventory_commands.md",
        ROOT / "docs/vendor_runtime_gap_map.md",
        ROOT / "docs/vendor_runtime_runner_guide.md",
    )
    for path in repo_green_paths:
        text = _primary_text(path)
        assert "./tools/python verify" in text, path.relative_to(ROOT)
        assert "./tools/vendor-green" in text, path.relative_to(ROOT)
        assert "./scripts/ci/repo_green.sh" not in text, path.relative_to(ROOT)
