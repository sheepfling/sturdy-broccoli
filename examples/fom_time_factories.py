"""Small Python RTI smoke example for FOM URLs, time factories, and handle factories.

Run from the project root:

    PYTHONPATH=. python examples/fom_time_factories.py
"""
from __future__ import annotations

from hla2010.enums import CallbackModel, ResignAction
from hla2010.spec import FederateAmbassadorSpec
from hla2010_fom_target_radar.scenarios import target_radar_fom_path
from hla2010_rti_runtime_common import create_rti_ambassador


class PrinterFederate(FederateAmbassadorSpec):
    def time_advance_grant(self, logical_time):
        print(f"time advance grant: {logical_time}")


FOM = target_radar_fom_path()


def main() -> None:
    rti = create_rti_ambassador("python")
    fed = PrinterFederate()

    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("FactoryDemoFederation", FOM, "HLAfloat64Time")
    rti.join_federation_execution("factory-demo", "demo", "FactoryDemoFederation")

    time_factory = rti.get_time_factory()
    print("time factory:", time_factory.get_name())

    target_class = rti.get_object_class_handle("HLAobjectRoot.Target")
    rcs = rti.get_attribute_handle(target_class, "RCS")

    attrs = rti.get_attribute_handle_set_factory().create()
    attrs.add(rcs)
    rti.publish_object_class_attributes(target_class, attrs)

    obj = rti.register_object_instance(target_class, "Target-From-Factory-Demo")
    values = rti.get_attribute_handle_value_map_factory().create(1)
    values[rcs] = b"12.5"
    rti.update_attribute_values(obj, values, b"demo")

    rti.enable_time_regulation(time_factory.make_interval(0.5))
    rti.evoke_multiple_callbacks(0.0, 0.0)
    print("lookahead:", rti.query_lookahead())

    rti.time_advance_request(time_factory.make_time(1.25))
    rti.evoke_multiple_callbacks(0.0, 0.0)
    print("current time:", rti.query_logical_time())

    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution("FactoryDemoFederation")
    rti.disconnect()


if __name__ == "__main__":
    main()
