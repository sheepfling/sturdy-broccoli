#!/usr/bin/env python3
"""Run one Docker-backed Pitch exchange and dump callback evidence."""
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
from hla.rti1516e.factory import create_rti_ambassador
from hla.verification import TwoFederateExchangeConfig, run_two_federate_exchange_scenario
from hla.rti1516e.time import HLAinteger64Interval, HLAinteger64Time
from hla.vendors.pitch.real_rti_pitch import launch_pitch_runtime


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "backend",
        nargs="?",
        default="pitch-jpype",
        help="Backend identifier to exercise during the diagnostic run",
    )
    return parser.parse_args(argv)


def _format_arg(value: object) -> str:
    type_name = f"{type(value).__module__}.{type(value).__qualname__}"
    return f"{value!r} [{type_name}]"


def _dump_records(label: str, federate: RecordingFederateAmbassador) -> None:
    print(f"\n## {label}", flush=True)
    for idx, record in enumerate(federate.records):
        if record.method_name not in {
            "discoverObjectInstance",
            "reflectAttributeValues",
            "receiveInteraction",
            "timeRegulationEnabled",
            "timeConstrainedEnabled",
            "timeAdvanceGrant",
        }:
            continue
        print(f"{idx}: {record.method_name}", flush=True)
        for arg_idx, arg in enumerate(record.args):
            print(f"  arg{arg_idx}: {_format_arg(arg)}", flush=True)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    kind = args.backend
    os.environ.setdefault("HLA2010_PITCH_CRC_MODE", "docker")
    os.environ.setdefault("HLA2010_PITCH_DOCKER_BUILD", "0")

    try:
        runtime = launch_pitch_runtime()
    except BackendUnavailableError as exc:
        print(f"Pitch unavailable: {exc}", file=sys.stderr)
        return 2

    federation_name = f"pitch-diag-{uuid.uuid4().hex[:8]}"
    publisher_fed = RecordingFederateAmbassador()
    subscriber_fed = RecordingFederateAmbassador()
    publisher = None
    subscriber = None
    try:
        publisher = create_rti_ambassador(kind)
        subscriber = create_rti_ambassador(kind)
        try:
            run_two_federate_exchange_scenario(
                publisher,
                subscriber,
                config=TwoFederateExchangeConfig(
                    federation_name=federation_name,
                    fom_modules=("resource:VendorSmokeFOM.xml",),
                    logical_time_implementation_name="HLAinteger64Time",
                    object_class_name="HLAobjectRoot.SmokeObject",
                    attribute_name="Payload",
                    interaction_class_name="HLAinteractionRoot.SmokeInteraction",
                    parameter_name="Message",
                    object_instance_name=f"{kind}-PitchDiagObject-1",
                    enable_time_management=True,
                    lookahead=HLAinteger64Interval(1),
                    advance_time=HLAinteger64Time(8),
                    timestamped_attribute_time=HLAinteger64Time(5),
                    timestamped_interaction_time=HLAinteger64Time(6),
                ),
                publisher_federate=publisher_fed,
                subscriber_federate=subscriber_fed,
            )
            print("SCENARIO OK", flush=True)
        except BaseException:
            traceback.print_exc()
            print("SCENARIO FAILED", flush=True)
        finally:
            _dump_records("publisher callbacks", publisher_fed)
            _dump_records("subscriber callbacks", subscriber_fed)
            try:
                subscriber.resign_federation_execution(ResignAction.NO_ACTION)
            except BaseException:
                pass
            try:
                publisher.resign_federation_execution(ResignAction.DELETE_OBJECTS)
            except BaseException:
                pass
            try:
                publisher.destroy_federation_execution(federation_name)
            except BaseException:
                pass
            for rti in (subscriber, publisher):
                try:
                    rti.disconnect()
                except BaseException:
                    pass
    finally:
        if subscriber is not None:
            subscriber.close()
        if publisher is not None:
            publisher.close()
        runtime.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
