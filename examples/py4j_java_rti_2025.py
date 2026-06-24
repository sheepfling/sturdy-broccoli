"""Py4J Java RTI skeleton for IEEE 1516.1-2025.

Use this when a vendor RTI is already running in a separate JVM, or when you want
process isolation between Python and Java. The Java side must start a Py4J
GatewayServer with the 2025 RTI jars on its classpath.
"""
from hla.bridges.java.py4j import Py4JConfig, rti_ambassador
from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador


class MyFederate(NullFederateAmbassador):
    def timeAdvanceGrant(self, logicalTime):
        print("granted", logicalTime)


config = Py4JConfig(
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
    callback_server_parameters={"port": 25334},
    java_api_profile="2025",
    rti_factory_name=None,
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
