#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from hla2010.backends.base import BackendUnavailableError
from hla2010.real_rti import discover_certi_smoke_fom
from hla2010.real_rti_certi import discover_certi_runtime
from hla2010.real_rti_process import reserve_tcp_port


ROOT_DIR = Path(__file__).resolve().parents[1]
LOCAL_STATE_ROOT = Path(os.environ.get("HLA2010_LOCAL_STATE_ROOT", str(ROOT_DIR / ".local")))


def _local_state_path(*parts: str) -> Path:
    return LOCAL_STATE_ROOT.joinpath(*parts)


def _check(name: str, func):
    try:
        value = func()
        return {"name": name, "ok": True, "message": f"{name}: ok: {value}"}
    except BackendUnavailableError as exc:
        return {"name": name, "ok": False, "message": f"{name}: blocked: {exc}"}
    except Exception as exc:
        return {
            "name": name,
            "ok": False,
            "message": f"{name}: error: {exc.__class__.__name__}: {exc}",
        }


def _path_record(path: Path, *, marker: str | None = None) -> dict[str, object]:
    resolved = path.expanduser().resolve()
    record: dict[str, object] = {
        "path": str(resolved),
        "exists": resolved.exists(),
    }
    if marker is not None:
        marker_path = resolved / marker
        record["marker"] = str(marker_path)
        record["marker_exists"] = marker_path.exists()
    return record


def _runtime_profiles() -> dict[str, dict[str, object]]:
    patched_source = Path(
        os.environ.get("HLA2010_CERTI_SOURCE", str(ROOT_DIR / "CERTI"))
    )
    patched_build = Path(
        os.environ.get(
            "HLA2010_CERTI_BUILD_ROOT",
            str(_local_state_path("certi", "patched", "build")),
        )
    )
    patched_prefix = Path(
        os.environ.get(
            "HLA2010_CERTI_PATCHED_PREFIX",
            os.environ.get(
                "HLA2010_CERTI_PREFIX",
                str(_local_state_path("certi", "patched", "install")),
            ),
        )
    )
    upstream_source = Path(
        os.environ.get(
            "HLA2010_CERTI_UPSTREAM_SOURCE",
            str(_local_state_path("certi", "upstream", "source")),
        )
    )
    upstream_build = Path(
        os.environ.get(
            "HLA2010_CERTI_UPSTREAM_BUILD_ROOT",
            str(_local_state_path("certi", "upstream", "build")),
        )
    )
    upstream_prefix = Path(
        os.environ.get(
            "HLA2010_CERTI_UPSTREAM_PREFIX",
            str(_local_state_path("certi", "upstream", "install")),
        )
    )
    active_prefix = Path(
        os.environ.get(
            "HLA2010_CERTI_PREFIX",
            str(_local_state_path("certi", "patched", "install")),
        )
    )
    active_build = Path(
        os.environ.get(
            "HLA2010_CERTI_BUILD_ROOT",
            str(_local_state_path("certi", "patched", "build")),
        )
    )
    return {
        "active": {
            "profile": "certi",
            "prefix": _path_record(active_prefix, marker="bin/rtig"),
            "build_root": _path_record(active_build, marker="libRTI/ieee1516-2010"),
        },
        "patched": {
            "profile": "certi-patched",
            "source": _path_record(patched_source, marker="test/InteractiveFederate/1516-2010/Certi-Test-02.xml"),
            "build_root": _path_record(patched_build, marker="libRTI/ieee1516-2010"),
            "prefix": _path_record(patched_prefix, marker="bin/rtig"),
        },
        "upstream": {
            "profile": "certi-upstream",
            "source": _path_record(upstream_source),
            "build_root": _path_record(upstream_build, marker="libRTI/ieee1516-2010"),
            "prefix": _path_record(upstream_prefix, marker="bin/rtig"),
        },
    }


def _require_marker(record: dict[str, object], label: str) -> str:
    if not bool(record.get("marker_exists")):
        marker = record.get("marker") or record.get("path") or label
        raise BackendUnavailableError(f"{label} missing: {marker}")
    return str(record.get("marker") or record.get("path") or label)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether the local CERTI runtime is runnable.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--json-file", type=Path, help="write machine-readable JSON to this file")
    args = parser.parse_args()

    runtime_profiles = _runtime_profiles()
    checks: list[dict[str, object]] = [
        _check("certi_runtime", lambda: discover_certi_runtime().prefix),
        _check("active_prefix", lambda: _require_marker(runtime_profiles["active"]["prefix"], "active CERTI install prefix")),
        _check("active_build_root", lambda: _require_marker(runtime_profiles["active"]["build_root"], "active CERTI build root")),
        _check("certi_smoke_fom", discover_certi_smoke_fom),
        _check("loopback_bind", lambda: f"reserved tcp port {reserve_tcp_port('127.0.0.1')}"),
    ]

    environment = "loopback-ok" if all(bool(item["ok"]) for item in checks) else "partial"
    failed_names = {str(item["name"]) for item in checks if not bool(item["ok"])}
    if "loopback_bind" in failed_names:
        environment = "loopback-blocked"

    result = "real CERTI runnable" if all(bool(item["ok"]) for item in checks) else "real CERTI will skip"
    next_steps = (
        [
            "./scripts/certi_easy.sh smoke compare",
            (
                "HLA2010_ENABLE_REAL_RTI_SMOKE=1 python3 -m pytest -q "
                "tests/vendors/test_certi_real_backend_exchange_matrix.py "
                "tests/vendors/test_certi_real_backend_time_matrix.py "
                "tests/vendors/test_certi_real_backend_ownership_matrix.py"
            ),
        ]
        if result == "real CERTI runnable"
        else ["fix the blocked prerequisite above", "./scripts/certi_easy.sh preflight"]
    )

    if args.json:
        payload = {
            "tool": "certi-preflight",
            "environment": environment,
            "result": result,
            "checks": checks,
            "runtime_profiles": runtime_profiles,
            "required_markers": {
                "active_prefix": runtime_profiles["active"]["prefix"].get("marker"),
                "active_build_root": runtime_profiles["active"]["build_root"].get("marker"),
                "patched_prefix": runtime_profiles["patched"]["prefix"].get("marker"),
                "patched_build_root": runtime_profiles["patched"]["build_root"].get("marker"),
                "upstream_prefix": runtime_profiles["upstream"]["prefix"].get("marker"),
                "upstream_build_root": runtime_profiles["upstream"]["build_root"].get("marker"),
            },
            "next_steps": next_steps,
            "exit_code": 0 if result == "real CERTI runnable" else 1,
        }
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        if args.json_file is not None:
            args.json_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return 0 if result == "real CERTI runnable" else 1

    if args.json_file is not None:
        payload = {
            "tool": "certi-preflight",
            "environment": environment,
            "result": result,
            "checks": checks,
            "runtime_profiles": runtime_profiles,
            "required_markers": {
                "active_prefix": runtime_profiles["active"]["prefix"].get("marker"),
                "active_build_root": runtime_profiles["active"]["build_root"].get("marker"),
                "patched_prefix": runtime_profiles["patched"]["prefix"].get("marker"),
                "patched_build_root": runtime_profiles["patched"]["build_root"].get("marker"),
                "upstream_prefix": runtime_profiles["upstream"]["prefix"].get("marker"),
                "upstream_build_root": runtime_profiles["upstream"]["build_root"].get("marker"),
            },
            "next_steps": next_steps,
            "exit_code": 0 if result == "real CERTI runnable" else 1,
        }
        args.json_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    for item in checks:
        print(str(item["message"]))

    if result == "real CERTI runnable":
        print("environment: loopback-ok")
        print("result: real CERTI runnable")
        print("easy: ./scripts/certi_easy.sh preflight")
        print("next: ./scripts/certi_easy.sh smoke compare")
        print(
            "next: HLA2010_ENABLE_REAL_RTI_SMOKE=1 python3 -m pytest -q "
            "tests/vendors/test_certi_real_backend_exchange_matrix.py "
            "tests/vendors/test_certi_real_backend_time_matrix.py "
            "tests/vendors/test_certi_real_backend_ownership_matrix.py"
        )
        return 0

    if environment == "loopback-blocked":
        print("environment: loopback-blocked")
        print(
            "next: run this in an unrestricted local terminal or request approval "
            "for an unsandboxed command"
        )
    else:
        print("environment: partial")

    print("result: real CERTI will skip")
    print("easy: ./scripts/certi_easy.sh preflight")
    print("next: fix the blocked prerequisite above, then rerun ./scripts/certi_easy.sh preflight")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
