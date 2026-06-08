"""Py4J Java RTI skeleton.

Use this when a vendor RTI is already running in a separate JVM, or when you want
process isolation between Python and Java.  The Java side must start a Py4J
GatewayServer with the RTI jars on its classpath.
"""
from hla2010.runtime_api import FederateAmbassador
from hla2010.backends.py4j import Py4JConfig, rti_ambassador
from hla2010.enums import CallbackModel


class MyFederate(FederateAmbassador):
    def time_advance_grant(self, logical_time):
        print("granted", logical_time)


config = Py4JConfig(
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
    callback_server_parameters={"port": 25334},
    rti_factory_name=None,
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
