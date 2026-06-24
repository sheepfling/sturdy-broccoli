"""Direct Python RTI skeleton for IEEE 1516.1-2010.

Use this when you want the smallest possible example for the native Python 2010
route without Java bridge details.
"""
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel


class MyFederate(NullFederateAmbassador):
    def connectionLost(self, faultDescription):
        print("connection lost:", faultDescription)

    def timeAdvanceGrant(self, theTime):
        print("time advance granted:", theTime)


rti = create_rti_ambassador(backend="python1516e")
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
