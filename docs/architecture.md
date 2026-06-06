# Architecture notes

The Python-facing federate code talks to a single HLA-style ambassador surface. Backend selection is separated from application code:

- `hla2010.backends.python_rti` provides the in-memory pure-Python RTI.
- `hla2010.backends.jpype_backend` adapts an in-process Java RTI through JPype.
- `hla2010.backends.py4j_backend` adapts an out-of-process Java RTI through Py4J.
- `hla2010.backends.transport` provides the lower transport abstraction that can be implemented with subprocess pipes, sockets, gRPC, REST, or other request/response protocols.
- `hla2010.backends.certi.transport` and `hla2010.backends.certi.service_adapter` make the CERTI transport/service split explicit while keeping `hla2010.backends.certi_backend` as a compatibility shim.
- `hla2010.backends.java_common` contains shared Java dispatch, callback, handle, collection, and exception conversion behavior.
- `hla2010.real_rti` discovers concrete local vendor runtime assets and builds
  bridge-ready runtime profiles for Pitch and process-launch profiles for CERTI.
- `hla2010.fom`, `hla2010.mom_catalog`, and bundled XML resources provide FOM/MIM parsing and MOM exposure support.
- `hla2010.time_management` keeps reusable logical-time ordering calculations out of the RTI backend.

The development goal is that a federate written against `hla2010` can run over either the pure-Python RTI or a Java RTI adapter with the same application-level code.
