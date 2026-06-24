#!/usr/bin/env python3
"""Run Docker-backed Pitch ownership probes and dump callback and server log evidence."""
from __future__ import annotations

import argparse
import os
import sys
import tomllib
import traceback
import uuid
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.backends.common import BackendUnavailableError, RecordingFederateAmbassador
from hla.rti1516e.enums import ResignAction
from hla.runtime.factory import create_rti_ambassador
from hla.verification import (
    NegotiatedOwnershipScenarioConfig,
    ReleaseRequestOwnershipScenarioConfig,
    probe_negotiated_attribute_ownership_offer,
    run_release_request_ownership_scenario,
)
from hla.vendors.pitch.real_rti_pitch import launch_pitch_runtime

CALLBACK_FILTER = {
    "discoverObjectInstance",
    "requestAttributeOwnershipAssumption",
    "requestDivestitureConfirmation",
    "requestAttributeOwnershipRelease",
    "attributeOwnershipAcquisitionNotification",
    "confirmAttributeOwnershipAcquisitionCancellation",
    "informAttributeOwnership",
    "attributeIsNotOwned",
}


def _format_arg(value: object) -> str:
    type_name = f"{type(value).__module__}.{type(value).__qualname__}"
    return f"{value!r} [{type_name}]"


def _dump_records(label: str, federate: RecordingFederateAmbassador) -> None:
    print(f"\n## {label}", flush=True)
    for idx, record in enumerate(federate.records):
        if record.method_name not in CALLBACK_FILTER:
            continue
        print(f"{idx}: {record.method_name}", flush=True)
        for arg_idx, arg in enumerate(record.args):
            print(f"  arg{arg_idx}: {_format_arg(arg)}", flush=True)


def _cleanup_federation(federation_name: str, owner, acquirer) -> None:
    try:
        acquirer.resign_federation_execution(ResignAction.UNCONDITIONALLY_DIVEST_ATTRIBUTES)
    except BaseException:
        pass
    try:
        owner.resign_federation_execution(ResignAction.DELETE_OBJECTS)
    except BaseException:
        pass
    try:
        owner.destroy_federation_execution(federation_name)
    except BaseException:
        pass
    for rti in (acquirer, owner):
        try:
            rti.disconnect()
        except BaseException:
            pass


def _dump_summary(summary: dict[str, object]) -> None:
    print("\n## Summary", flush=True)
    for key in sorted(summary):
        value = summary[key]
        if hasattr(value, "method_name") and hasattr(value, "args"):
            print(f"{key}: callback {value.method_name}", flush=True)
        else:
            print(f"{key}: {value!r}", flush=True)


def _dump_pitch_logs(runtime, *, tail_lines: int) -> None:
    print("\n## Runtime stdout", flush=True)
    try:
        stdout, stderr = runtime.process.communicate(timeout=2.0)
    except BaseException as exc:
        print(f"<unavailable: {exc}>", flush=True)
        stdout, stderr = "", ""
    print(stdout.rstrip() or "<empty>", flush=True)

    print("\n## Runtime stderr", flush=True)
    print(stderr.rstrip() or "<empty>", flush=True)

    user_home = Path(runtime.env.get("HLA2010_PITCH_USER_HOME", ""))
    log_dir = user_home / "logs" / "FedProServer"
    print(f"\n## FedPro log dir\n{log_dir}", flush=True)
    if not log_dir.exists():
        print("<missing>", flush=True)
        return

    log_files = sorted(log_dir.glob("*.log"), key=lambda path: path.stat().st_mtime)
    if not log_files:
        print("<no log files>", flush=True)
        return

    for path in log_files[-3:]:
        print(f"\n### {path.name}", flush=True)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        tail = lines[-tail_lines:] if lines else []
        if not tail:
            print("<empty>", flush=True)
            continue
        for line in tail:
            print(line, flush=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", nargs="?", default="pitch-jpype", choices=("pitch-jpype", "pitch-py4j"))
    parser.add_argument(
        "--mode",
        choices=("offer", "release-request"),
        default="offer",
        help="Probe the negotiated divesting-offer path or the owned-attribute release-request path.",
    )
    parser.add_argument("--tail-lines", type=int, default=120, help="Number of log lines to print from each FedPro log.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    os.environ.setdefault("HLA2010_PITCH_CRC_MODE", "docker")
    os.environ.setdefault("HLA2010_PITCH_DOCKER_BUILD", "0")

    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        print(f"Pitch unavailable: {exc}", file=sys.stderr)
        return 2

    federation_name = f"pitch-ownership-diag-{args.mode}-{uuid.uuid4().hex[:8]}"
    owner_fed = RecordingFederateAmbassador()
    acquirer_fed = RecordingFederateAmbassador()
    owner = None
    acquirer = None
    exit_code = 0
    try:
        owner = create_rti_ambassador(args.kind)
        acquirer = create_rti_ambassador(args.kind)
        try:
            if args.mode == "offer":
                summary = probe_negotiated_attribute_ownership_offer(
                    owner,
                    acquirer,
                    config=NegotiatedOwnershipScenarioConfig(
                        federation_name=federation_name,
                        fom_modules=("resource:VendorSmokeFOM.xml",),
                        logical_time_implementation_name="HLAinteger64Time",
                        owner_name="Owner",
                        acquirer_name="Acquirer",
                        federate_type="OwnershipFederate",
                        object_class_name="HLAobjectRoot.SmokeObject",
                        attribute_name="Payload",
                        object_instance_name=f"{args.kind}-NegotiatedOfferDiag-1",
                        assumption_tag=b"assume-offer",
                        request_tag=b"acquire-request",
                        cancel_tag=b"reacquire-request",
                    ),
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            else:
                summary = run_release_request_ownership_scenario(
                    owner,
                    acquirer,
                    config=ReleaseRequestOwnershipScenarioConfig(
                        federation_name=federation_name,
                        fom_modules=("resource:VendorSmokeFOM.xml",),
                        logical_time_implementation_name="HLAinteger64Time",
                        owner_name="Owner",
                        acquirer_name="Acquirer",
                        federate_type="OwnershipFederate",
                        object_class_name="HLAobjectRoot.SmokeObject",
                        attribute_name="Payload",
                        object_instance_name=f"{args.kind}-ReleaseRequestDiag-1",
                        request_tag=b"acquire-request",
                        owner_action="ifwanted",
                    ),
                    owner_federate=owner_fed,
                    acquirer_federate=acquirer_fed,
                )
            print("SCENARIO OK", flush=True)
        except BaseException:
            traceback.print_exc()
            print("SCENARIO FAILED", flush=True)
            exit_code = 1
            summary = {}
        finally:
            _dump_summary(summary)
            _dump_records("owner callbacks", owner_fed)
            _dump_records("acquirer callbacks", acquirer_fed)
            if owner is not None and acquirer is not None:
                _cleanup_federation(federation_name, owner, acquirer)
    finally:
        if acquirer is not None:
            acquirer.close()
        if owner is not None:
            owner.close()
        runtime.terminate()
        _dump_pitch_logs(runtime, tail_lines=args.tail_lines)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
