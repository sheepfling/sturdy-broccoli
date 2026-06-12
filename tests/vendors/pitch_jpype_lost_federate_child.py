from __future__ import annotations

import argparse
import json
import signal
import sys
import time
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_rti_backend_common import RecordingFederateAmbassador
from hla2010.enums import CallbackModel, ResignAction
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010_verification_harness import register_named_object_instance


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--federation-name", required=True)
    parser.add_argument("--federate-name", required=True)
    parser.add_argument("--federate-type", required=True)
    parser.add_argument("--logical-time-implementation-name", required=True)
    parser.add_argument("--object-class-name", required=True)
    parser.add_argument("--attribute-name", required=True)
    parser.add_argument("--object-instance-name", required=True)
    parser.add_argument("--automatic-resign-directive", default="DELETE_OBJECTS")
    parser.add_argument("--fom-module", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    victim = create_rti_ambassador("pitch-jpype")
    federate = RecordingFederateAmbassador()

    def _terminate(_signum, _frame):
        raise SystemExit(143)

    signal.signal(signal.SIGTERM, _terminate)

    victim.connect(federate, CallbackModel.HLA_EVOKED)
    victim.join_federation_execution(args.federate_name, args.federate_type, args.federation_name)
    victim.set_automatic_resign_directive(getattr(ResignAction, args.automatic_resign_directive))

    object_class = victim.get_object_class_handle(args.object_class_name)
    attribute = victim.get_attribute_handle(object_class, args.attribute_name)
    victim.publish_object_class_attributes(object_class, {attribute})
    register_named_object_instance(victim, federate, object_class, args.object_instance_name)

    payload = {
        "victim_handle_hex": victim.get_federate_handle(args.federate_name).encode().hex(),
        "victim_time_hex": victim.query_logical_time().encode().hex(),
        "victim_name": args.federate_name,
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()

    while True:
        time.sleep(1.0)


if __name__ == "__main__":
    raise SystemExit(main())
