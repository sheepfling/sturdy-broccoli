# Architecture notes

The Python-facing federate code talks to a single HLA-style ambassador surface. Backend selection is separated from application code:

- `hla2010.backends.python_rti` provides the in-memory pure-Python RTI.
- `hla2010.backends.jpype_backend` adapts an in-process Java RTI through JPype.
- `hla2010.backends.py4j_backend` adapts an out-of-process Java RTI through Py4J.
- `hla2010.backends.transport` provides the lower transport abstraction and its typed `TransportRequest` / `TransportResponse` envelopes. In practice this is currently a seam for the CERTI-backed adapters, not a separate backend family.
- `hla2010.backends.grpc_transport` is a concrete gRPC transport using the checked-in `rti_transport.proto` schema and Python protobuf stubs. It is currently exercised in two ways: as a CERTI transport surface and as a transport-hosted pure-Python RTI proving path.
- `hla2010.backends.rest_transport` is the matching JSON-over-HTTP transport. It is registered under the `rest` and `http-json` transport kinds and is likewise exercised as a CERTI transport surface.
- `docs/openapi/rti_transport.yaml` formalizes the REST transport envelope so generated REST clients can target the same request/response shape.
- `hla2010.backends.certi.transport` and `hla2010.backends.certi.service_adapter` make the CERTI transport/service split explicit while keeping `hla2010.backends.certi_backend` as a compatibility shim over the vendored `CERTI/` tree and the local `CERTI-build/` / `CERTI-install/` outputs.
- `hla2010.backends.java_common` contains shared Java dispatch, callback, handle, collection, and exception conversion behavior.
- `hla2010.real_rti` discovers concrete local vendor runtime assets and builds
  bridge-ready runtime profiles for Pitch and process-launch profiles for CERTI.
- `hla2010.fom`, `hla2010.mom_catalog`, and bundled XML resources provide FOM/MIM parsing and MOM exposure support.
- `hla2010.time_management` keeps reusable logical-time ordering calculations out of the RTI backend.
- `scripts/bootstrap_python.sh`, `scripts/rebuild_certi.sh`, and `scripts/bootstrap_all.sh` are the primary workspace setup entrypoints.

The development goal is that a federate written against `hla2010` can run over the pure-Python RTI, the CERTI-backed paths, or a Java RTI adapter with the same application-level code. REST and gRPC currently matter as transport choices under that backend-neutral surface, not as standalone backend targets.

## Current Remote Callback Contract

The current gRPC proving path uses unary request/response calls plus explicit callback polling through `evokeCallback` and `evokeMultipleCallbacks`.

- This is the current contract of record for remote callback delivery.
- The server is allowed to buffer multiple RTI callbacks and drain them across repeated polling requests.
- This keeps the remote path aligned with the existing HLA callback model and with the CERTI helper contract already used in the repo.

Server-streaming or bidi-streaming gRPC remains a plausible future transport contract, but it is not the current one. The immediate goal is clause-level parity over the existing polling model before widening the wire protocol again.
