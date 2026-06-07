#!/usr/bin/env python3
"""Run one Docker-backed Pitch exchange and dump callback evidence."""
from __future__ import annotations

import os
import sys
import traceback
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.enums import ResignAction
from hla2010.backends.base import BackendUnavailableError
from hla2010.real_rti import launch_pitch_runtime
from hla2010.rti import create_rti_ambassador
from hla2010.testing.scenario_exchange import TwoFederateExchangeConfig, run_two_federate_exchange_scenario
from hla2010.time import HLAinteger64Interval, HLAinteger64Time


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


def main() -> int:
    kind = sys.argv[1] if len(sys.argv) > 1 else "pitch-jpype"
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
                    fom_modules=("hla2010:VendorSmokeFOM.xml",),
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
