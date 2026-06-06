# Architecture notes

The Python-facing federate code talks to a single HLA-style ambassador surface. Backend selection is separated from application code:

- `hla2010.backends.python_rti` provides the in-memory pure-Python RTI.
- `hla2010.backends.jpype_backend` adapts an in-process Java RTI through JPype.
- `hla2010.backends.py4j_backend` adapts an out-of-process Java RTI through Py4J.
- `hla2010.backends.transport` provides the lower transport abstraction and its typed `TransportRequest` / `TransportResponse` envelopes, so a transport can be backed by subprocess pipes, sockets, gRPC, REST, or generated protobuf/OpenAPI models without changing the service adapter.
- `hla2010.backends.grpc_transport` is a concrete gRPC transport using the checked-in `rti_transport.proto` schema and Python protobuf stubs.
- `hla2010.backends.rest_transport` is the first concrete typed transport built on that seam; it speaks JSON over HTTP and is registered under the `rest` and `http-json` transport kinds.
- `docs/openapi/rti_transport.yaml` formalizes the REST transport envelope so generated REST clients can target the same request/response shape.
- `hla2010.backends.certi.transport` and `hla2010.backends.certi.service_adapter` make the CERTI transport/service split explicit while keeping `hla2010.backends.certi_backend` as a compatibility shim over the vendored `CERTI/` tree and the local `CERTI-build/` / `CERTI-install/` outputs.
- `hla2010.backends.java_common` contains shared Java dispatch, callback, handle, collection, and exception conversion behavior.
- `hla2010.real_rti` discovers concrete local vendor runtime assets and builds
  bridge-ready runtime profiles for Pitch and process-launch profiles for CERTI.
- `hla2010.fom`, `hla2010.mom_catalog`, and bundled XML resources provide FOM/MIM parsing and MOM exposure support.
- `hla2010.time_management` keeps reusable logical-time ordering calculations out of the RTI backend.
- `scripts/bootstrap_python.sh`, `scripts/rebuild_certi.sh`, and `scripts/bootstrap_all.sh` are the primary workspace setup entrypoints.

The development goal is that a federate written against `hla2010` can run over either the pure-Python RTI or a Java RTI adapter with the same application-level code.
