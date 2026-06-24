"""JPype Java RTI skeleton.

Replace the classpath with the jars/classes for your RTI vendor. JPype runs the
JVM in-process, so this path is often best for low-latency callbacks and when
only one JVM is needed in the Python process.
"""
from hla.bridges.java.jpype import JPypeConfig, rti_ambassador
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel


class MyFederate(NullFederateAmbassador):
    def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag):
        print("sync point", synchronizationPointLabel, bytes(userSuppliedTag))


config = JPypeConfig(
    classpath=["/path/to/vendor-rti.jar", "/path/to/vendor-1516e.jar"],
    rti_factory_name=None,  # or a vendor factory name if more than one is installed
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
