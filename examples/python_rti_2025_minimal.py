"""Direct Python RTI skeleton for IEEE 1516.1-2025.

Use this when you want the smallest possible example for the native Python 2025
route without Java bridge details.
"""
from hla.runtime.rti1516_2025_factory import create_rti_ambassador
from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador


class MyFederate(NullFederateAmbassador):
    def connectionLost(self, faultDescription):
        print("connection lost:", faultDescription)

    def timeAdvanceGrant(self, theTime):
        print("time advance granted:", theTime)


rti = create_rti_ambassador(backend="python1516_2025")
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
