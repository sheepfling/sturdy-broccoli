from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_tools_federate_cli_help_describes_scripted_and_interactive_usage() -> None:
    result = subprocess.run(
        ["bash", "tools/federate-cli", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "./tools/federate-cli --edition 2010 --command 'connect'" in result.stdout
    assert "./tools/federate-cli --edition 2025 --backend python1516_2025" in result.stdout
    assert "list-classes [all|object|interaction] [contains-text]" in result.stdout
    assert "inspect-class FULL_NAME" in result.stdout
    assert "inspect-adapter NAME" in result.stdout
    assert "publish-object CLASS ATTR1,ATTR2" in result.stdout
    assert "send-interaction CLASS param=value [param=value...]" in result.stdout
    assert "walkthrough NAME" in result.stdout
    assert "next-step" in result.stdout
    assert "walkthrough route-variation-tour" in result.stdout
    assert "./tools/federate-cli --edition 2025 --backend python1516_2025 --command 'walkthrough route-variation-tour'" in result.stdout
    assert "tui" in result.stdout
    assert "create [federation]" in result.stdout
    assert "evoke [minimum-seconds] [maximum-seconds]" in result.stdout


def test_federate_cli_change_map_doc_is_present_and_linked_from_front_doors() -> None:
    doc = (ROOT / "docs" / "federate_cli_change_map.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    tools_readme = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")

    assert "## FOM Shape Changes" in doc
    assert "## Transport Changes" in doc
    assert "## Adapter Dialect Changes" in doc
    assert "adapter-boundary-tour" in doc
    assert "[`federate_cli_change_map.md`](federate_cli_change_map.md)" in docs_index
    assert "docs/federate_cli_change_map.md" in tools_readme


def test_tools_federate_cli_runs_scripted_2010_lifecycle_and_reports_json() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2010",
            "--federation",
            "interactive-test-2010",
            "--command",
            "connect",
            "--command",
            "create interactive-test-2010",
            "--command",
            "join alice operator interactive-test-2010",
            "--command",
            "status",
            "--command",
            "resign",
            "--command",
            "destroy interactive-test-2010",
            "--command",
            "disconnect",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["tool"] == "federate-cli"
    assert payload["edition"] == "2010"
    assert payload["backend"] == "python1516e"
    commands = [entry["command"] for entry in payload["results"]]
    assert commands == [
        "connect",
        "create interactive-test-2010",
        "join alice operator interactive-test-2010",
        "status",
        "resign",
        "destroy interactive-test-2010",
        "disconnect",
    ]
    assert payload["final_status"]["session"]["connected"] is False
    assert payload["final_status"]["session"]["callback_count"] >= 0


def test_tools_federate_cli_runs_scripted_2025_lifecycle_and_reports_validation() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--backend",
            "python1516_2025",
            "--federation",
            "interactive-test-2025",
            "--command",
            "connect",
            "--command",
            "create interactive-test-2025 --fom-scenario message-test",
            "--command",
            "join observer analysis interactive-test-2025",
            "--command",
            "evoke 0 0",
            "--command",
            "callbacks 5",
            "--command",
            "resign",
            "--command",
            "destroy interactive-test-2025",
            "--command",
            "disconnect",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    assert payload["edition"] == "2025"
    assert payload["backend"] == "python1516_2025"
    create_result = next(entry for entry in payload["results"] if entry["command"].startswith("create "))
    assert create_result["validation_status"] == "validated"
    callbacks_result = next(entry for entry in payload["results"] if entry["command"] == "callbacks 5")
    assert "records" in callbacks_result
    assert payload["final_status"]["session"]["validation_status"] == "validated"


def test_tools_federate_cli_lists_fom_inventory_and_runs_publication_flow() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--backend",
            "python1516_2025",
            "--federation",
            "interactive-flow-2025",
            "--command",
            "create interactive-flow-2025 --fom-scenario message-test",
            "--command",
            "list-classes object MessageTest",
            "--command",
            "list-interactions MessageTest",
            "--command",
            "list-datatypes Proto2025",
            "--command",
            "join owner analysis interactive-flow-2025",
            "--command",
            "publish-object HLAobjectRoot.Proto2025.MessageTest.VerificationStatus TestCaseId,StepId,Verdict,Reason,ExpectedValueJson,ActualValueJson,CheckedLogicalTime",
            "--command",
            "register-object HLAobjectRoot.Proto2025.MessageTest.VerificationStatus verdict-1",
            "--command",
            "update-object verdict-1 TestCaseId=case-1 StepId=step-1 Verdict=PASS Reason=ready ExpectedValueJson=expected ActualValueJson=actual CheckedLogicalTime=1",
            "--command",
            "publish-interaction HLAinteractionRoot.Proto2025.MessageTest.VerificationResult",
            "--command",
            "send-interaction HLAinteractionRoot.Proto2025.MessageTest.VerificationResult TestCaseId=case-1 StepId=step-1 Verdict=PASS Reason=ready EvidenceArtifactId=evidence-1",
            "--command",
            "status",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    classes_result = next(entry for entry in payload["results"] if entry["command"] == "list-classes object MessageTest")
    interactions_result = next(entry for entry in payload["results"] if entry["command"] == "list-interactions MessageTest")
    datatypes_result = next(entry for entry in payload["results"] if entry["command"] == "list-datatypes Proto2025")
    status_result = next(entry for entry in payload["results"] if entry["command"] == "status")

    assert any(row["full_name"] == "HLAobjectRoot.Proto2025.MessageTest.VerificationStatus" for row in classes_result["object_classes"])
    assert any(row["full_name"] == "HLAinteractionRoot.Proto2025.MessageTest.VerificationResult" for row in interactions_result["interaction_classes"])
    assert any(row["name"] == "Proto2025Verdict" for row in datatypes_result["datatypes"])
    assert "verdict-1" in status_result["session"]["object_instances"]
    assert "HLAinteractionRoot.Proto2025.MessageTest.VerificationResult" in status_result["session"]["published_interaction_classes"]


def test_tools_federate_cli_tui_snapshot_renders_in_non_tty_json_mode() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "create dashboard-2025 --fom-scenario message-test",
            "--command",
            "tui",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    tui_result = next(entry for entry in payload["results"] if entry["command"] == "tui")
    assert "Federate CLI Dashboard" in tui_result["dashboard"]
    assert "fom counts:" in tui_result["dashboard"]


def test_tools_federate_cli_walkthrough_steps_through_learning_flow() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--backend",
            "python1516_2025",
            "--federation",
            "walkthrough-2025",
            "--command",
            "walkthrough message-test-tour",
            "--command",
            "walkthrough-status",
            "--command",
            "next-step",
            "--command",
            "next-step",
            "--command",
            "next-step",
            "--command",
            "next-step",
            "--command",
            "walkthrough-status",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    load_result = next(entry for entry in payload["results"] if entry["command"] == "walkthrough message-test-tour")
    initial_status = payload["results"][1]
    step_results = [entry for entry in payload["results"] if entry["command"] == "next-step"]
    final_walkthrough = next(entry for entry in payload["results"] if entry["command"] == "walkthrough-status" and entry is not initial_status)

    assert load_result["walkthrough"]["name"] == "message-test-tour"
    assert initial_status["walkthrough"]["next_step"]["title"] == "Connect"
    assert step_results[0]["step_result"]["message"] == "connected"
    assert step_results[2]["step_result"]["message"] == "object class detail"
    assert step_results[3]["step_result"]["message"] == "interaction class detail"
    assert final_walkthrough["walkthrough"]["step_index"] == 4
    assert final_walkthrough["walkthrough"]["next_step"]["title"] == "Inspect Datatype"


def test_tools_federate_cli_pause_and_inspect_datatype_are_script_friendly() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "create inspect-2025 --fom-scenario message-test",
            "--command",
            "inspect-datatype Proto2025Verdict",
            "--command",
            "pause 0 ready for next step",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    datatype_result = next(entry for entry in payload["results"] if entry["command"] == "inspect-datatype Proto2025Verdict")
    pause_result = next(entry for entry in payload["results"] if entry["command"] == "pause 0 ready for next step")

    assert datatype_result["datatype"]["name"] == "Proto2025Verdict"
    assert pause_result["note"] == "ready for next step"


def test_tools_federate_cli_two_federate_walkthrough_shows_receiver_callbacks() -> None:
    commands = [
        "walkthrough two-federate-callback-tour",
        *["next-step"] * 15,
        "walkthrough-status",
        "status",
    ]
    argv = [
        "bash",
        "tools/federate-cli",
        "--edition",
        "2025",
        "--backend",
        "python1516_2025",
        "--federation",
        "walkthrough-2fed-2025",
    ]
    for command in commands:
        argv.extend(["--command", command])
    argv.append("--json")

    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    peer_callbacks_result = next(
        entry
        for entry in payload["results"]
        if entry.get("step_result", {}).get("message") == "peer callbacks snapshot"
    )
    receiver_records = peer_callbacks_result["step_result"]["peer"]["records"]
    receiver_methods = {record["method_name"] for record in receiver_records}
    final_status = next(entry for entry in payload["results"] if entry["command"] == "status")

    assert {"discoverObjectInstance", "reflectAttributeValues", "receiveInteraction"} <= receiver_methods
    assert final_status["session"]["peers"]["sink"]["callback_count"] >= 3
    assert final_status["session"]["walkthrough"]["completed"] is True


def test_tools_federate_cli_tui_accepts_scripted_keys_for_walkthrough_and_inspection() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "create dashboard-keys-2025 --fom-scenario message-test",
            "--command",
            "walkthrough message-test-tour",
            "--command",
            "tui",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "FEDERATE_CLI_TUI_KEYS": "noidsq"},
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    tui_result = next(entry for entry in payload["results"] if entry["command"] == "tui")

    assert tui_result["tui_keys"] == list("noidsq")
    assert "walkthrough: message-test-tour | step 1/15" in tui_result["dashboard"]
    assert "Focus: Status" in tui_result["dashboard"]


def test_tools_federate_cli_tui_help_overlay_can_be_toggled_from_keys() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "create dashboard-help-2025 --fom-scenario message-test",
            "--command",
            "tui",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "FEDERATE_CLI_TUI_KEYS": "hq"},
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    tui_result = next(entry for entry in payload["results"] if entry["command"] == "tui")

    assert "Help Overlay" in tui_result["dashboard"]
    assert "n -> next walkthrough step" in tui_result["dashboard"]
    assert "menu=off | help=on" in tui_result["dashboard"]


def test_tools_federate_cli_tui_walkthrough_menu_can_select_a_walkthrough() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "tui",
            "--command",
            "walkthrough-status",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "FEDERATE_CLI_TUI_KEYS": "m3q"},
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    status_result = next(entry for entry in payload["results"] if entry["command"] == "walkthrough-status")
    tui_result = next(entry for entry in payload["results"] if entry["command"] == "tui")

    assert status_result["walkthrough"]["name"] == "route-variation-tour"
    assert status_result["walkthrough"]["next_step"]["title"] == "Connect Direct Route"
    assert "menu=off | help=off" in tui_result["dashboard"]


def test_tools_federate_cli_tui_walkthrough_menu_accepts_letter_shortcuts() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "tui",
            "--command",
            "walkthrough-status",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "FEDERATE_CLI_TUI_KEYS": "marq"},
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    status_result = next(entry for entry in payload["results"] if entry["command"] == "walkthrough-status")
    tui_result = next(entry for entry in payload["results"] if entry["command"] == "tui")

    assert status_result["walkthrough"]["name"] == "adapter-boundary-tour"
    assert status_result["walkthrough"]["next_step"]["title"] == "Connect Direct Route"
    assert "menu=off | help=off" in tui_result["dashboard"]
    assert "walkthrough: adapter-boundary-tour | step 0/10" in tui_result["dashboard"]


def test_tools_federate_cli_can_inspect_adapter_boundary_profiles() -> None:
    result = subprocess.run(
        [
            "bash",
            "tools/federate-cli",
            "--edition",
            "2025",
            "--command",
            "inspect-adapter grpc-quirky-vendor",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    inspect_result = next(entry for entry in payload["results"] if entry["command"] == "inspect-adapter grpc-quirky-vendor")

    assert inspect_result["adapter"]["name"] == "grpc-quirky-vendor"
    assert "encode_request" in inspect_result["adapter"]["swap_points"]
    assert any(path.endswith("vendor_variant.py") for path in inspect_result["adapter"]["primary_files"])


def test_tools_federate_cli_route_variation_walkthrough_provisions_hosted_route() -> None:
    commands = [
        "walkthrough route-variation-tour",
        *["next-step"] * 9,
        "walkthrough-status",
        "status",
    ]
    argv = [
        "bash",
        "tools/federate-cli",
        "--edition",
        "2025",
        "--backend",
        "python1516_2025",
        "--federation",
        "walkthrough-route-2025",
    ]
    for command in commands:
        argv.extend(["--command", command])
    argv.append("--json")

    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    hosted_status = next(
        entry
        for entry in payload["results"]
        if entry.get("step_result", {}).get("message") == "route status"
    )
    final_status = next(entry for entry in payload["results"] if entry["command"] == "status")

    assert hosted_status["step_result"]["route"]["transport"]["kind"] == "grpc"
    assert hosted_status["step_result"]["route"]["joined"] is True
    assert final_status["session"]["peers"] == {}
    assert final_status["session"]["routes"]["hosted"]["transport"]["kind"] == "grpc"


def test_tools_federate_cli_transport_substitution_walkthrough_provisions_grpc_and_rest_routes() -> None:
    commands = [
        "walkthrough transport-substitution-tour",
        *["next-step"] * 13,
        "walkthrough-status",
        "status",
    ]
    argv = [
        "bash",
        "tools/federate-cli",
        "--edition",
        "2010",
        "--backend",
        "python1516e",
        "--federation",
        "walkthrough-transport-2010",
    ]
    for command in commands:
        argv.extend(["--command", command])
    argv.append("--json")

    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    rest_status = next(
        entry
        for entry in payload["results"]
        if entry.get("step_result", {}).get("route_alias") == "hosted-rest"
        and entry.get("step_result", {}).get("message") == "route status"
    )
    final_status = next(entry for entry in payload["results"] if entry["command"] == "status")

    assert rest_status["step_result"]["route"]["transport"]["kind"] == "rest"
    assert "base_url" in rest_status["step_result"]["route"]["transport"]
    assert final_status["session"]["routes"]["hosted-grpc"]["transport"]["kind"] == "grpc"
    assert "target" in final_status["session"]["routes"]["hosted-grpc"]["transport"]
    assert final_status["session"]["routes"]["hosted-rest"]["transport"]["kind"] == "rest"
    assert "base_url" in final_status["session"]["routes"]["hosted-rest"]["transport"]


def test_tools_federate_cli_2010_route_sessions_provision_grpc_and_rest_routes() -> None:
    commands = [
        "create route-matrix-2010",
        "join alpha analysis route-matrix-2010",
        "@route-ensure hosted-grpc grpc",
        "@route-connect hosted-grpc",
        "@route-create hosted-grpc route-matrix-2010-hosted-grpc",
        "@route-join hosted-grpc HostedGrpcFederate analysis route-matrix-2010-hosted-grpc",
        "@route-ensure hosted-rest rest",
        "@route-connect hosted-rest",
        "@route-create hosted-rest route-matrix-2010-hosted-rest",
        "@route-join hosted-rest HostedRestFederate analysis route-matrix-2010-hosted-rest",
        "@route-status hosted-grpc",
        "@route-status hosted-rest",
        "status",
    ]
    argv = [
        "bash",
        "tools/federate-cli",
        "--edition",
        "2010",
        "--backend",
        "python1516e",
        "--federation",
        "route-matrix-2010",
    ]
    for command in commands:
        argv.extend(["--command", command])
    argv.append("--json")

    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    grpc_status = next(entry for entry in payload["results"] if entry["command"] == "@route-status hosted-grpc")
    rest_status = next(entry for entry in payload["results"] if entry["command"] == "@route-status hosted-rest")
    final_status = next(entry for entry in payload["results"] if entry["command"] == "status")

    assert grpc_status["route"]["transport"]["kind"] == "grpc"
    assert "target" in grpc_status["route"]["transport"]
    assert rest_status["route"]["transport"]["kind"] == "rest"
    assert "base_url" in rest_status["route"]["transport"]
    assert final_status["session"]["routes"]["hosted-grpc"]["transport"]["kind"] == "grpc"
    assert "target" in final_status["session"]["routes"]["hosted-grpc"]["transport"]
    assert final_status["session"]["routes"]["hosted-rest"]["transport"]["kind"] == "rest"
    assert "base_url" in final_status["session"]["routes"]["hosted-rest"]["transport"]


def test_tools_federate_cli_adapter_boundary_walkthrough_surfaces_swap_points_and_hosted_route() -> None:
    commands = [
        "walkthrough adapter-boundary-tour",
        *["next-step"] * 8,
        "walkthrough-status",
        "status",
    ]
    argv = [
        "bash",
        "tools/federate-cli",
        "--edition",
        "2025",
        "--backend",
        "python1516_2025",
        "--federation",
        "walkthrough-adapter-2025",
    ]
    for command in commands:
        argv.extend(["--command", command])
    argv.append("--json")

    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout or result.stderr
    payload = json.loads(result.stdout)
    quirky_adapter_step = next(
        entry
        for entry in payload["results"]
        if entry.get("step_result", {}).get("message") == "adapter profile detail"
        and entry["step_result"]["adapter"]["name"] == "grpc-quirky-vendor"
    )
    hosted_status_step = next(
        entry
        for entry in payload["results"]
        if entry.get("step_result", {}).get("message") == "route status"
    )
    final_status = next(entry for entry in payload["results"] if entry["command"] == "status")

    assert "decode_callback_request" in quirky_adapter_step["step_result"]["adapter"]["swap_points"]
    assert hosted_status_step["step_result"]["route"]["transport"]["kind"] == "grpc"
    assert final_status["session"]["routes"]["hosted"]["transport"]["kind"] == "grpc"
