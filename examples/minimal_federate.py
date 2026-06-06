from hla2010 import FederateAmbassador, CallbackModel

class MinimalFederate(FederateAmbassador):
    def connection_lost(self, fault_description: str):
        print("connection lost:", fault_description)

    def time_advance_grant(self, the_time):
        print("time advance granted:", the_time)

# A real federate will obtain a vendor-backed or local RTIAmbassador adapter.
# rti.connect(MinimalFederate(), CallbackModel.HLA_EVOKED)
