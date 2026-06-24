"""JPype Java RTI skeleton for IEEE 1516.1-2025.

Replace the classpath with the jars/classes for a Java RTI that exposes the
standard ``hla.rti1516_2025`` API. JPype runs the JVM in-process, so this route
is best when Python should own the process and only one JVM is needed.
"""
from hla.bridges.java.jpype import JPypeConfig, rti_ambassador
from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador


class MyFederate(NullFederateAmbassador):
    def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag):
        print("sync point", synchronizationPointLabel, bytes(userSuppliedTag))


config = JPypeConfig(
    classpath=["/path/to/vendor-rti-2025.jar", "/path/to/vendor-1516_2025.jar"],
    java_api_profile="2025",
    rti_factory_name=None,  # or a vendor factory name if more than one is installed
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
