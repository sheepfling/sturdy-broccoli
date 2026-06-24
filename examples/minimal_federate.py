"""Legacy minimal federate skeleton for IEEE 1516.1-2010.

For explicit edition-by-edition examples, prefer:

- examples/python_rti_2010_minimal.py
- examples/python_rti_2025_minimal.py
"""
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel


class MinimalFederate(NullFederateAmbassador):
    def connectionLost(self, faultDescription):
        print("connection lost:", faultDescription)

    def timeAdvanceGrant(self, theTime):
        print("time advance granted:", theTime)


# A real federate will obtain a vendor-backed or local RTI ambassador adapter.
# rti.connect(MinimalFederate(), CallbackModel.HLA_EVOKED)
