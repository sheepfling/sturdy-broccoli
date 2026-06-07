"""JPype Java RTI skeleton.

Replace the classpath with the jars/classes for your RTI vendor.  JPype runs the
JVM in-process, so this path is often best for low-latency callbacks and when
only one JVM is needed in the Python process.
"""
from hla2010.api import FederateAmbassador
from hla2010.backends.jpype import JPypeConfig, rti_ambassador
from hla2010.enums import CallbackModel


class MyFederate(FederateAmbassador):
    def announce_synchronization_point(self, label, user_supplied_tag):
        print("sync point", label, bytes(user_supplied_tag))


config = JPypeConfig(
    classpath=["/path/to/vendor-rti.jar", "/path/to/vendor-1516e.jar"],
    rti_factory_name=None,  # or a vendor factory name if more than one is installed
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
