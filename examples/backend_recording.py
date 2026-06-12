"""Backend abstraction smoke example.

Run with:
    PYTHONPATH=. python examples/backend_recording.py
"""
from hla2010_rti_backend_common import RecordingBackend, make_rti_ambassador
from hla2010.enums import CallbackModel
from hla2010.spec import FederateAmbassadorSpec


class MyFederate(FederateAmbassadorSpec):
    def time_advance_grant(self, time):
        print("time advance grant", time)


backend = RecordingBackend(results={"getHLAversion": "HLA 1516.1-2010"})
rti = make_rti_ambassador(backend)

print(rti.get_hla_version())
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)

last_call = backend.calls[-1]
print(last_call.method_name, last_call.args[1])
