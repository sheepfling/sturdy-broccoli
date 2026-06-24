"""Py4J Java RTI skeleton.

Use this when a vendor RTI is already running in a separate JVM, or when you want
process isolation between Python and Java.  The Java side must start a Py4J
GatewayServer with the RTI jars on its classpath.
"""
from hla.bridges.java.py4j import Py4JConfig, rti_ambassador
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel


class MyFederate(NullFederateAmbassador):
    def timeAdvanceGrant(self, logicalTime):
        print("granted", logicalTime)


config = Py4JConfig(
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
    callback_server_parameters={"port": 25334},
    rti_factory_name=None,
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
