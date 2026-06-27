#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

VERIFY_FAST_ARGS = [
    "-m",
    "pytest",
    "-q",
    "tests/test_operator_surface_policy.py",
    "tests/scenarios/test_test_surface_wrapper.py",
    "tests/scenarios/test_ci_green_wrappers.py",
    "tests/requirements/test_2025_route_parity_matrix.py",
    "tests/requirements/test_ieee_1516_2025_requirements_registry.py",
]

VERIFY_SMOKE_ARGS = [
    "-m",
    "pytest",
    "-q",
    "tests/test_operator_surface_policy.py",
    "tests/test_package_import_isolation.py",
    "tests/test_package_dependency_metadata.py",
    "tests/architecture/test_path_portability_policy.py",
    "tests/scenarios/test_ci_green_wrappers.py",
    "tests/scenarios/test_test_surface_wrapper.py",
    "tests/test_tools_python_wrapper.py",
    "tests/test_tools_test_focus.py",
    "tests/scenarios/test_top_level_vendor_wrappers.py",
    "tests/scenarios/test_pitch_tool_router.py",
]

VERIFY_MAIN_2025_COMMANDS = [
    ["-m", "pytest", "-q", "tests/test_python1516_2025_split_package.py", "tests/test_package_import_isolation.py", "tests/test_package_dependency_metadata.py", "tests/test_root_facade_policy.py"],
    ["-m", "pytest", "-q", "tests/scenarios/test_target_radar_scenario.py::test_target_radar_example_supports_2025_backends", "tests/test_fom_target_radar_split_package.py::test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter", "tests/test_fom_target_radar_split_package.py::test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface"],
    ["-m", "pytest", "-q", "tests/requirements/test_2025_python_rti_backend_audit.py"],
    ["-m", "pytest", "-q", "tests/requirements/test_ieee_1516_2025_requirements_registry.py"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "primary_python_rti_runs_support_factory_and_decode_scenario_without_wrapper_adapter or primary_python_rti_accepts_snake_case_aliases_for_direct_runtime_surface or primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "test_2025_provider_runs_federation_lifecycle_scenario_end_to_end or test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end or test_2025_provider_runs_federation_listing_scenario_end_to_end or test_2025_provider_runs_update_rate_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_update_rate_scenario_without_wrapper_adapter or test_2025_provider_runs_two_federate_object_and_interaction_exchange or test_2025_primary_python_rti_runs_two_federate_exchange_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_name_reservation_scenario_without_wrapper_adapter or test_2025_provider_runs_passive_full_declaration_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_passive_full_declaration_scenario_without_wrapper_adapter or test_2025_provider_runs_ddm_object_region_lifecycle_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_ddm_object_region_lifecycle_scenario_without_wrapper_adapter or test_2025_provider_runs_ddm_declaration_gating_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_ddm_declaration_gating_scenario_without_wrapper_adapter or test_2025_provider_runs_ddm_passive_region_subscription_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_ddm_passive_region_subscription_scenario_without_wrapper_adapter or test_2025_provider_runs_object_scope_relevance_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_object_scope_relevance_scenario_without_wrapper_adapter or test_2025_provider_runs_orphan_object_lifecycle_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_orphan_object_lifecycle_scenario_without_wrapper_adapter or test_2025_provider_runs_timed_delete_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_timed_delete_scenario_without_wrapper_adapter or test_2025_provider_routes_directed_interactions_only_to_subscribers or test_2025_provider_routes_directed_ddm_interactions_only_to_overlapping_subscribers or test_2025_primary_python_rti_runs_two_federate_suite_ddm_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_resigned_federate_callback_silence_scenario_without_wrapper_adapter"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "test_2025_provider_round_trips_automatic_resign_directive_support_service or test_2025_provider_runs_callback_control_route_with_object_reflection_end_to_end or test_2025_primary_python_rti_runs_callback_control_scenario_without_wrapper_adapter or test_2025_provider_runs_attribute_ownership_scenario_end_to_end or test_2025_primary_python_rti_runs_negotiated_ownership_flow_without_wrapper_adapter or test_2025_provider_runs_attribute_ownership_query_callback_scenario_via_compat_adapter or test_2025_primary_python_rti_runs_transportation_type_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_transportation_type_restore_persistence_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_transportation_type_rejection_scenario_without_wrapper_adapter or test_2025_primary_python_rti_restores_transportation_type_state_without_wrapper_adapter or test_2025_provider_serializes_mom_service_reports_without_overclaiming_conformance or test_2025_provider_routes_mom_mim_and_fom_module_reports_through_interactions or test_2025_provider_routes_mom_adjust_interactions_for_reporting_switches or test_2025_provider_routes_mom_time_management_service_interactions or test_2025_provider_routes_mom_object_and_ownership_service_interactions"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "test_2025_provider_runs_integrated_time_window_gauntlet_end_to_end or test_2025_provider_runs_time_window_core_scenario_end_to_end or test_2025_provider_runs_time_window_future_exclusion_scenario_end_to_end or test_2025_provider_runs_time_window_output_delivery_scenario_end_to_end or test_2025_provider_runs_time_window_consumer_order_scenario_end_to_end or test_2025_provider_runs_time_window_pipeline_scenario_end_to_end or test_2025_provider_runs_time_window_receive_order_poison_scenario_end_to_end or test_2025_provider_runs_time_window_restore_state_scenario_end_to_end or test_2025_provider_runs_time_window_restore_output_scenario_end_to_end or test_2025_provider_runs_time_window_pipeline_restore_scenario_end_to_end or test_2025_future_exclusion_oracle_rejects_mismatched_lits_boundary or test_2025_output_delivery_oracle_rejects_output_before_window_close or test_2025_consumer_order_oracle_rejects_reversed_delivery_order or test_2025_pipeline_oracle_rejects_cross_window_payload_contamination or test_2025_restore_window_state_oracle_rejects_dirty_post_close_callback_leak or test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore or test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay or test_2025_receive_order_poison_oracle_rejects_closed_window_mutation"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "test_2025_primary_python_rti_runs_backend_neutral_save_restore_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_two_federate_suite_save_restore_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_save_restore_queued_callback_scenario_without_wrapper_adapter or test_2025_primary_python_rti_runs_scheduled_save_restore_time_state_scenario_without_wrapper_adapter or test_2025_provider_runs_backend_neutral_save_restore_scenario_via_compat_adapter or test_2025_provider_runs_save_restore_queued_callback_scenario_via_compat_adapter or test_2025_provider_runs_scheduled_save_restore_time_state_scenario_via_compat_adapter or test_2025_provider_runs_federation_save_restore_lifecycle or test_2025_provider_runs_example_fom_save_restore_gauntlet or test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet or test_2025_provider_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso or test_2025_provider_restores_closed_window_output_resume_without_dirty_replay or test_2025_provider_restores_pipeline_resume_without_cross_window_replay"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "time_window and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "save_restore and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "ownership and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "callback and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "support_service and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "mom and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_validation.py", "tests/factories/test_fom_omt_parsing.py"],
    ["examples/target_radar_simulation.py", "--backend", "python1516_2025", "--steps", "5"],
]

VERIFY_ROUTES_COMMANDS = [
    ["-m", "pytest", "-q", "tests/scenarios/test_python_route_parity.py"],
    ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_python_server.py"],
    ["scripts/run_python_route_parity_matrix.py"],
    ["examples/target_radar_simulation.py", "--backend", "python1516e", "--steps", "5"],
    ["examples/target_radar_simulation.py", "--backend", "python1516e-grpc", "--steps", "5"],
]

VERIFY_ROUTES_2025_COMMANDS = [
    ["-m", "pytest", "-q", "tests/requirements/test_2025_python_rti_backend_audit.py"],
    ["-m", "pytest", "-q", "tests/requirements/test_ieee_1516_2025_requirements_registry.py"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "primary_python_rti_runs_support_factory_and_decode_scenario_without_wrapper_adapter or primary_python_rti_accepts_snake_case_aliases_for_direct_runtime_surface or primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter"],
    ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_2025.py", "-k", "test_2025_transport_server_runs_shared_federation_lifecycle_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_federation_listing_scenario_over_fedpro_route or test_2025_transport_server_runs_object_and_interaction_exchange_over_fedpro_schema or test_2025_transport_server_runs_object_instance_name_reservation_flow_over_fedpro_schema or test_2025_transport_server_runs_ddm_object_region_lifecycle_scenario_over_fedpro_route or test_2025_transport_server_runs_ddm_declaration_gating_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_object_scope_relevance_scenario_over_fedpro_route or test_2025_transport_server_routes_directed_interactions_only_to_subscribers_over_fedpro_schema or test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema or test_2025_transport_server_runs_two_federate_suite_ddm_scenario_over_fedpro_route"],
    ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_2025.py", "-k", "test_2025_transport_server_round_trips_support_services_over_fedpro_schema or test_2025_transport_server_round_trips_2025_switch_services_over_fedpro_schema or test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route or test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema or test_2025_transport_server_routes_mom_adjust_controls_to_observable_switch_state_over_fedpro_schema or test_2025_transport_server_reports_failed_mom_service_actions_as_mom_exception_interactions"],
    ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_2025.py", "-k", "test_2025_factory_hosted_python2025_route_runs_package_owned_target_radar_shared_scenario or test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario or test_2025_factory_hosted_python2025_route_runs_package_owned_output_delivery_scenario or test_2025_factory_hosted_python2025_route_runs_package_owned_consumer_order_scenario or test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet or test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario or test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario or test_2025_factory_hosted_python2025_route_runs_package_owned_pipeline_restore_scenario or test_2025_transport_server_runs_shared_time_window_gauntlet_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_future_exclusion_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_output_delivery_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_consumer_order_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_pipeline_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_receive_order_poison_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_restore_state_scenario_over_fedpro_route or test_2025_transport_server_runs_shared_pipeline_restore_scenario_over_fedpro_route"],
    ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_2025.py", "-k", "test_2025_transport_server_runs_shared_save_restore_scenario_over_fedpro_route or test_2025_transport_server_runs_two_federate_suite_save_restore_scenario_over_fedpro_route or test_2025_transport_server_runs_backend_neutral_save_restore_scenario_over_fedpro_route or test_2025_transport_server_runs_save_restore_queued_callback_scenario_over_fedpro_route or test_2025_transport_server_runs_scheduled_save_restore_time_state_scenario_over_fedpro_route or test_2025_transport_server_runs_save_restore_lifecycle_over_fedpro_schema or test_2025_transport_server_tracks_multi_federate_save_restore_per_peer_over_fedpro_schema or test_2025_transport_server_runs_example_fom_save_restore_gauntlet_over_fedpro_schema or test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema or test_2025_transport_server_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso_over_fedpro_schema or test_2025_transport_server_restores_closed_window_output_resume_without_dirty_replay_over_fedpro_schema"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "time_window and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "save_restore and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "ownership and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "callback and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "support_service and python1516_2025"],
    ["-m", "pytest", "-q", "tests/test_rti1516_2025_python1516_2025_runtime.py", "-k", "mom and python1516_2025"],
    ["-m", "pytest", "-q", "tests/transport/test_grpc_transport_2025.py"],
    ["-m", "pytest", "-q", "tests/requirements/test_2025_route_parity_matrix.py"],
    ["-m", "pytest", "-q", "tests/requirements/test_2025_finish_line_snapshot.py", "-k", "checked_in_finish_line_artifacts_preserve_python2025_route_identity"],
    ["scripts/run_spec2025_finish_line.py"],
    ["examples/target_radar_simulation.py", "--backend", "python1516_2025", "--steps", "5"],
]


def usage() -> str:
    return "\n".join(
        [
            "usage: ./tools/python [verify|verify-smoke|verify-fast|verify-gold|verify-main-2025|verify-routes|verify-routes-2025|verify-routes-preflight|smoke-examples|test-examples|help]",
            "",
            "Canonical Python / repo-green operator flow:",
            "  ./tools/python verify                  # run the repo-green verification lane",
            "  ./tools/python verify-smoke            # run the fast-fail repo smoke lane before expensive integration depth",
            "  ./tools/python verify-fast             # run the low-cost operator/docs/Python-matrix lane",
            "  ./tools/python verify-fast --with-gold # run verify-fast, then chain the higher-standard hygiene gate",
            "  ./tools/python verify-gold            # run the higher-standard package hygiene / typing smell gate",
            "  ./tools/python verify-main-2025        # run the primary 2025 Python RTI main-surface proof lane (python1516_2025)",
            "  ./tools/python verify-routes           # run 2010 Python direct-vs-gRPC route parity checks",
            "  ./tools/python verify-routes-2025      # run 2025 Python RTI / FedPro hosted-route checks",
            "  ./tools/python verify-routes-preflight # report whether python-grpc is runnable here",
            "  ./tools/python smoke-examples --edition 2010",
            "  ./tools/python smoke-examples --edition 2025",
            "  ./tools/python smoke-examples --all    # run both direct Python example routes",
            "  ./tools/python test-examples           # run focused Python example tests",
            "  ./tools/test-focus inventory           # list named focused targets by package/theme",
            "  ./tools/test-focus resume python-2025-runtime",
            "",
            "This is the human-facing wrapper over the Python-backed repo-green lane in",
            "`./scripts/ci/repo_green.py`, with `./scripts/ci/repo_green.sh` retained as a",
            "compatibility alias.",
            "Use ./tools/certi-easy and ./tools/pitch for vendor-runtime operator flows.",
        ]
    )


def _path_python_bin() -> str:
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("error: python3 or python not found")


def _workspace_python_bin() -> str:
    return os.environ.get("HLA2010_PYTHON_VERIFY_ROUTES_PYTHON", "python3")


def _workspace_pythonpath() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    return os.pathsep.join(str(ROOT / rel) for rel in source_roots)


def _workspace_env() -> dict[str, str]:
    env = os.environ.copy()
    workspace_pythonpath = _workspace_pythonpath()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{workspace_pythonpath}{os.pathsep}{existing}" if existing else workspace_pythonpath
    return env


def _run(argv: list[str], *, env: dict[str, str] | None = None) -> int:
    return subprocess.run(argv, cwd=ROOT, env=env, check=False).returncode


def _run_workspace_python(python_bin: str, argv: list[str]) -> int:
    return _run([python_bin, *argv], env=_workspace_env())


def _run_or_print_workspace_python(dry_run: bool, python_bin: str, argv: list[str]) -> int:
    if dry_run:
        print("+ hla2010_shell_run_workspace_python " + " ".join([python_bin, *argv]))
        return 0
    return _run_workspace_python(python_bin, argv)


def _run_delegate(env_name: str, args: list[str]) -> int | None:
    delegate = os.environ.get(env_name)
    if not delegate:
        return None
    return _run([delegate, *args])


def _run_command_sequence(commands: list[list[str]], trailing: list[str] | None = None) -> int:
    python_bin = _workspace_python_bin()
    trailing = trailing or []
    for index, command in enumerate(commands):
        argv = list(command)
        if index == len(commands) - 1 and trailing:
            argv.extend(trailing)
        status = _run_workspace_python(python_bin, argv)
        if status != 0:
            return status
    return 0


def verify_smoke(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_SMOKE_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    python_bin = _workspace_python_bin()
    status = _run_workspace_python(python_bin, ["scripts/detect_workspace_duplicates.py", "clean-same-content"])
    if status != 0:
        return status
    status = _run_workspace_python(python_bin, ["scripts/detect_workspace_duplicates.py"])
    if status != 0:
        return status
    status = _run_workspace_python(python_bin, ["scripts/validate_test_surface_manifest.py"])
    if status != 0:
        return status
    return _run_workspace_python(python_bin, [*VERIFY_SMOKE_ARGS, *args])


def verify_fast(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_FAST_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    with_gold = False
    passthrough: list[str] = []
    for arg in args:
        if arg == "--with-gold":
            with_gold = True
            continue
        passthrough.append(arg)

    status = _run_workspace_python(_workspace_python_bin(), [*VERIFY_FAST_ARGS, *passthrough])
    if status != 0 or not with_gold:
        return status
    return verify_gold([])


def verify_gold(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_GOLD_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    default_args = [
        "scripts/package_hygiene_score.py",
        "--top",
        "10",
        "--fail-under",
        "70",
        "--max-stringy",
        "0",
        "--max-init-side-effects",
        "0",
        "--max-path-sniffing",
        "0",
    ]
    return _run_workspace_python(_workspace_python_bin(), [*default_args, *args])


def verify_main_2025(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_MAIN_2025_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    return _run_command_sequence(VERIFY_MAIN_2025_COMMANDS, args)


def verify_routes(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_ROUTES_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    return _run_command_sequence(VERIFY_ROUTES_COMMANDS, args)


def verify_routes_2025(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_ROUTES_2025_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    return _run_command_sequence(VERIFY_ROUTES_2025_COMMANDS, args)


def verify_routes_preflight(args: list[str]) -> int:
    delegate_status = _run_delegate("HLA2010_PYTHON_VERIFY_ROUTES_PREFLIGHT_DELEGATE", args)
    if delegate_status is not None:
        return delegate_status
    return _run([_workspace_python_bin(), str(ROOT / "scripts" / "check_python_route_preflight.py"), *args], env=_workspace_env())


def smoke_examples(args: list[str]) -> int:
    edition = "2010"
    run_all = False
    dry_run = False
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--edition":
            if index + 1 >= len(args):
                raise SystemExit("--edition requires a value")
            edition = args[index + 1]
            index += 2
            continue
        if arg == "--all":
            run_all = True
            index += 1
            continue
        if arg == "--dry-run":
            dry_run = True
            index += 1
            continue
        raise SystemExit(f"unknown smoke-examples option: {arg}")
    if edition not in {"2010", "2025"}:
        raise SystemExit("--edition must be 2010 or 2025")

    python_bin = _workspace_python_bin()
    editions = ["2010", "2025"] if run_all else [edition]
    for selected in editions:
        status = _run_or_print_workspace_python(dry_run, python_bin, ["examples/python_route_federate.py", "--edition", selected])
        if status != 0:
            return status
    return 0


def test_examples(args: list[str]) -> int:
    dry_run = False
    for arg in args:
        if arg == "--dry-run":
            dry_run = True
            continue
        raise SystemExit(f"unknown test-examples option: {arg}")
    return _run_or_print_workspace_python(dry_run, _workspace_python_bin(), ["-m", "pytest", "-q", "tests/test_python_route_examples.py"])


def verify(args: list[str]) -> int:
    runner = _path_python_bin()
    return _run([runner, str(ROOT / "scripts" / "ci" / "repo_green.py"), *args])


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args:
        return verify([])

    command = args[0]
    tail = args[1:]
    if command in {"help", "-h", "--help"}:
        print(usage())
        return 0
    if command == "verify":
        return verify(tail)
    if command == "verify-smoke":
        return verify_smoke(tail)
    if command == "verify-fast":
        return verify_fast(tail)
    if command == "verify-gold":
        return verify_gold(tail)
    if command == "verify-main-2025":
        return verify_main_2025(tail)
    if command == "verify-routes":
        return verify_routes(tail)
    if command == "verify-routes-2025":
        return verify_routes_2025(tail)
    if command == "verify-routes-preflight":
        return verify_routes_preflight(tail)
    if command == "smoke-examples":
        return smoke_examples(tail)
    if command == "test-examples":
        return test_examples(tail)
    print(f"error: unknown subcommand: {command}", file=sys.stderr)
    print(usage(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
